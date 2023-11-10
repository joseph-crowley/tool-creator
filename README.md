# Tool Creator and Tool User

The `Tool Creator Assistant` is an automation for the creation of tools for other assistants. This repository houses the core `tool_creator` script that serves as a meta-assistant, capable of crafting additional tools to enhance the capabilities of your chat-based systems. Additionally, we include a `tool_user` script that seamlessly integrates these tools into a chat assistant, allowing for an interactive experience where the assistant utilizes the newly created tools in real-time.

## Features

- **Tool Creation**: Generate new tools tailored for assistant-based applications using the OpenAI API.
- **Tool Integration**: A ready-to-use `tool_user` script that incorporates tools into a chat interface.
- **Demo Video**: Visual demonstration of the tool creation and usage process.

## Video Demo

A video demonstration is available to showcase the capabilities and usage of the `Tool Creator Assistant`. You can view the video [here](https://youtu.be/18Dl2Y46ej4).


## Getting Started

### Prerequisites

- OpenAI API key

### Installation

1. Clone the repository:
   ```shell
   git clone https://github.com/joseph-crowley/tool-creator.git
   ```
2. Navigate to the cloned directory:
   ```shell
   cd tool-creator
   ```
3. Install the required packages:
   ```shell
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory of the repository and **add your OpenAI API key**:
   ```shell
   cp .env.example .env
   # Add your OpenAI API key to the .env file
   ```

### Usage

#### Environment Setup

- Source the `.env` file:
  ```shell
  source .env
  ```

#### Tool Creation

- Run the `tool_creator` script:
  ```shell
  python tool_creator.py
  ```
- chat with the bot about what you want the tool to do, and it will create the tool for you.
- The tool will be saved in the `tools` directory with both the `.json` and `.py` files
- The assistant will be saved in the `assistants` directory as `tool_creator.json`.

#### Tool Usage

- Execute the `tool_user` script to start the assistant:
  ```shell
  python tool_user.py
  ```
- The assistant will use all the tools in the `tools` directory.
- Interact with the assistant in the chat to use the integrated tools.
- The assistant will be saved in the `assistants` directory as `tool_user.json`.

## Contributing

We welcome contributions from the community. If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are welcome.