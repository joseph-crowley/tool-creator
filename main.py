# tool_creator assistant
from tool_creator import main as talk_to_creator

# tool_user assistant
from tool_user import main as talk_to_user

if __name__ == '__main__':
    # create the tool creator assistant and chat to create your tools
    talk_to_creator()

    # create the tool user assistant and chat to test your tools
    talk_to_user()
