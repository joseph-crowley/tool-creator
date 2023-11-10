"""
Create an assistant using the tools from tool_creator
"""

import os
import time
import json

from openai import OpenAI
client = OpenAI() # be sure to set your OPENAI_API_KEY environment variable

def create_tool_user(tools_to_use):
    print(f"Creating assistant to use tools: {tools_to_use}", flush=True)
    # create the assistant details 
    instructions_for_assistant = 'use the tools to accomplish the task'
    files_for_assistant = [] # local file paths 
    
    assistant_details = {
        'build_params' : {
            'model': "gpt-4-1106-preview", 
            'name': "Tool User",
            'description': "Assistant to use tools made by the tool creator.",
            'instructions': instructions_for_assistant, 
            'tools': [], # added later
            'file_ids': [],
            'metadata': {},
        },
        'file_paths': files_for_assistant,
        'functions': {}, # added later
    }
    
    # get the tools from the tools/ directory
    # json and py files by the tool name 
    os.makedirs('tools', exist_ok=True)
    for tool in tools_to_use:
        with open('tools/' + tool + '.json') as f:
            tool_details = json.load(f)
    
        with open('tools/' + tool + '.py') as f:
            tool_code = f.read()
    
        # add the tool to the assistant details
        assistant_details['build_params']['tools'].append({
            "type": "function", 
            "function": {
                "name": tool_details['name'],
                "description": tool_details['description'],
                "parameters": eval(tool_details['parameters']),
            },
        })
    
        # note: tool_code is a string of the code for the tool, should be evaluated to bring into the execution environment before use by the assistant
        assistant_details['functions'].update({
            tool_details['name']: tool_code,
        })

    # create the assistant
    tool_user = client.beta.assistants.create(**assistant_details["build_params"])

    print(f"Created assistant {tool_user.id}")

    # save the assistant info to a json file
    info_to_export = {
        "assistant_id": tool_user.id,
        "assistant_details": assistant_details,
    }
    os.makedirs('assistants', exist_ok=True)
    with open('assistants/tool_user.json', 'w') as f:
        json.dump(info_to_export, f, indent=4)

    return tool_user

def talk_to_tool_user():
    """
    talk to the assistant to use the tools
    """

    # check if json file exists
    try:
        os.makedirs('assistants', exist_ok=True)
        with open('assistants/tool_user.json') as f:
            assistant_details = json.load(f)
            tool_user = client.beta.assistants.retrieve(assistant_details['assistant_id'])
            print(f"Loaded assistant details from tool_user.json\n\n" + 90*"-" + "\n\n", flush=True)

        tools_to_use = [func for func in assistant_details['assistant_details']['functions']]
    except:
        # create the assistant first 

        # specify the tools for the assistant (currently everything in the tools/ directory)
        tools_to_use = [tool.split('.')[0] for tool in os.listdir('tools') if tool.endswith('.json')]
        tool_user = create_tool_user(tools_to_use)

    # exec the functions from the py files
    os.makedirs('tools', exist_ok=True)
    for func in tools_to_use:
        print(f"Loading function {func} into execution environment", flush=True)
        with open('tools/' + func + '.py') as f:
            exec(f.read(), globals())

    # Create thread
    thread = client.beta.threads.create()

    while True:
        user_message = input("You: ")

        # add user message to thread
        thread_message = client.beta.threads.messages.create(
          thread.id,
          role="user",
          content=user_message,
        ) 

        # get assistant response in thread
        run = client.beta.threads.runs.create(
          thread_id=thread.id,
          assistant_id=tool_user.id,
        )

        # wait for run to complete
        wait_time = 0
        while True:
            if wait_time % 5 == 0:
                print(f"waiting for run to complete...", flush=True)
            wait_time += 1
            time.sleep(1)

            run = client.beta.threads.runs.retrieve(
              thread_id=thread.id,
              run_id=run.id,
            )

            if run.status == "completed":
                break
            elif run.status == "in_progress":
                continue
            elif run.status == "requires_action":
                if run.required_action.type == 'submit_tool_outputs':
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls

                    tool_outputs = []
                    for tc in tool_calls:
                        function_to_call = eval(tc.function.name)
                        function_args = json.loads(tc.function.arguments)
                        function_response = function_to_call(**function_args)

                        tool_outputs.append({
                            "tool_call_id": tc.id,
                            "output": function_response,
                        })

                    print(f"Submitting tool outputs...", flush=True)
                    run = client.beta.threads.runs.submit_tool_outputs(
                      thread_id=thread.id,
                      run_id=run.id,
                      tool_outputs=tool_outputs
                    )
            else:
                input(f'Run status: {run.status}. press enter to continue, or ctrl+c to quit')

        # get most recent message from thread
        thread_messages = client.beta.threads.messages.list(thread.id, limit=10, order='desc')

        # get assistant response from message
        assistant_response = thread_messages.data[0].content[0].text.value

        print(f"\n\nBot: {assistant_response}\n\n", flush=True)

        # continue?
        try:
            input("Press enter to continue chatting, or ctrl+c to quit")
        except KeyboardInterrupt:
            exit()

if __name__ == "__main__":
    talk_to_tool_user()