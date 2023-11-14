import time
import json
from json.decoder import JSONDecodeError
 
import os
from pathlib import Path

from numpy_serializer import numpy_json_serializer

def chat(client, thread, assistant, functions):
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
          assistant_id=assistant.id,
        )

        # wait for run to complete
        wait_time = 0
        while True:
            run = client.beta.threads.runs.retrieve(
              thread_id=thread.id,
              run_id=run.id,
            )

            if run.status == "completed":
                break
            elif run.status == "in_progress":
                continue
            elif run.status == "queued":
                continue
            elif run.status == "requires_action":
                if run.required_action.type == 'submit_tool_outputs':
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls

                    tool_outputs = []
                    for tc in tool_calls:
                        function_to_call = functions.get(tc.function.name)
                        if not function_to_call:
                            raise ValueError(f"Function {tc.function.name} not found in execution environment")

                        # safely parse function arguments and call function
                        try:
                            function_args = json.loads(tc.function.arguments or {})
                            function_response = function_to_call(**function_args)
                        except Exception as e:
                            exception_message = f"Exception in function {tc.function.name}: {e}"
                            print(exception_message, flush=True)
                            function_response = exception_message

                        print(f"\nCalling function {tc.function.name} with args {function_args}", flush=True)
                        tool_outputs.append({
                            "tool_call_id": tc.id,
                            "output": json.dumps(function_response, default=numpy_json_serializer),
                        })

                    print(f"Submitting tool outputs\n {json.dumps(tool_outputs,indent=4)}\n\n", flush=True)
                    run = client.beta.threads.runs.submit_tool_outputs(
                      thread_id=thread.id,
                      run_id=run.id,
                      tool_outputs=tool_outputs
                    )
            else:
                input(f'Run status: {run.status}. press enter to continue, or ctrl+c to quit')

            if wait_time % 5 == 0:
                print(f"waiting for run to complete...", flush=True)
            wait_time += 1
            time.sleep(1)


        # get most recent message from thread
        thread_message = client.beta.threads.messages.list(thread.id, limit=1, order='desc').data[0]

        # get assistant response from message
        try:
            assistant_response = ''
            for content in thread_message.content:
                if content.type == 'text':
                    assistant_response += content.text.value
                elif content.type == 'image_file':
                    # get the file id
                    file_id = content.image_file.file_id
                    message_file = client.beta.threads.messages.files.retrieve(
                        thread_id=thread.id,
                        message_id=thread_message.id,
                        file_id=file_id,
                    )

                    # get the image data
                    image_data = client.files.retrieve_content(message_file.id)
                    image_data_bytes = image_data.data
                    
                    # # debug output
                    # print(f"File id: {file_id}", flush=True)
                    # print(f'Message file: {message_file}\n\n{dir(message_file)}', flush=True)
                    # print(f"Image data: {image_data}\n\n{dir(image_data)}", flush=True)
                    # print(f"Image data bytes: {image_data_bytes}", flush=True)

                    os.makedirs('images', exist_ok=True)
                    with open(f"images/{file_id}.png", "wb") as file:
                        file.write(image_data_bytes)
                    print(f"Saved image to images/{file_id}.png", flush=True)

                    assistant_response += f"\n![{file_id}.png](images/{file_id}.png)"
                assistant_response += '\n'

        except Exception as e:
            print(f"Exception getting assistant response: {e}", flush=True)


        print(f"\n\nBot: {assistant_response}\n\n", flush=True)

        # continue?
        try:
            input("Press enter to continue chatting, or ctrl+c to stop chat\n")
        except KeyboardInterrupt:
            print(f"Stopping chat\n" + 90*"-" + "\n\n", flush=True)
            break

    # Store information about the conversation
    thread_creation_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(thread.created_at))
    conversation = {
        'start_date': thread_creation_time,  
        'end_date': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        'assistant': assistant.name, 
        'bot_id': assistant.id,
        'thread_id': thread.id,
    }

    # Check that chat_history.json exists and append the conversation
    chat_history_path = Path('assistants/chat_history.json')
    chat_history = []

    if chat_history_path.exists():
        with chat_history_path.open('r+') as f:
            try:
                chat_history = json.load(f)
            except JSONDecodeError:
                pass  # File is empty or invalid, will overwrite with new content

    chat_history.append(conversation)

    with chat_history_path.open('w') as f:
        json.dump(chat_history, f, indent=4)