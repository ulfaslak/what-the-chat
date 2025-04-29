# What The Chat

A Python tool for fetching and summarizing chat history from Discord or Slack channels.

https://github.com/user-attachments/assets/efc9d54e-eff4-4528-b7dd-43994660e96d

## Overview

This tool allows you to:
- Fetch all messages from a Discord or Slack channel since a specified date
- Include messages from threads within the channel
- Generate a structured summary of the chat history using either local or remote LLMs
- Save both the full chat history and the summary to text files
- Interact with the chat history through an interactive chat session

## Features

- **Multi-Platform Support**: Works with both Discord and Slack channels
- **Comprehensive Message Collection**: Fetches all messages from a specified channel since a given date
- **Thread Support**: Automatically collects messages from all threads within the channel
- **User Reference Standardization**: Standardizes user references in the chat history
- **Intelligent Summarization**: Generates a structured summary based on the time span of messages:
  - Project Event Update (0-2 days)
  - Periodical Digest (3-6 days)
  - Full Project Status Summary (7+ days)
- **User-Friendly Output**: Replaces user IDs with actual usernames in the summary for better readability
- **Accurate Filenames**: Uses the actual first message date in filenames for accurate time range representation
- **Model Flexibility**: Supports both local models (via Ollama) and remote models (via OpenAI)
- **Interactive Chat**: Allows users to ask questions about the chat history in an interactive session
- **Colorful Terminal Output**: Provides clear visual cues with color-coded output and action indicators

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/what-the-chat.git
   cd what-the-chat
   ```

2. Install the required dependencies (e.g. in a new environment):
   ```
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following variables:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   SLACK_TOKEN=your_slack_bot_token
   OPENAI_API_KEY=your_openai_api_key  # Only needed if using remote models
   ```

## Usage

### Basic Usage

To fetch chat history from a Discord channel for the last 30 days, generate a summary, and start an interactive chat session:

```
python summarize.py --since-days 30 --channel 123456789012345678 --chat
```

To fetch chat history from a Slack channel:

```
python summarize.py --since-days 30 --platform slack --channel general --chat
```

This will:
1. Fetch messages from the specified channel for the last 30 days
2. Generate a summary of the chat history
3. Start an interactive chat session where you can ask questions about the chat history

### Saving to Files

To save the summary and/or full chat history to files:

```
python summarize.py --since-days 30 --channel 123456789012345678 --dump-file ./output --dump-collected-chat-history
```

This will save:
1. The summary to a file named `discord_history_summary_[channel_name]_[first_message_date]_[today's_date].md` in the `./output` directory
2. The full chat history to a file named `discord_history_[channel_name]_[first_message_date]_[today's_date].md` in the `./output` directory

For Slack:
```
python summarize.py --since-days 30 --platform slack --channel general --dump-file ./output --dump-collected-chat-history
```

This will save:
1. The summary to a file named `slack_history_summary_[channel_name]_[first_message_date]_[today's_date].md` in the `./output` directory
2. The full chat history to a file named `slack_history_[channel_name]_[first_message_date]_[today's_date].md` in the `./output` directory

### Using Remote Models

To use a remote model (e.g., GPT-4 Turbo) instead of the default local model:

```
python summarize.py --since-days 30 --channel 123456789012345678 --model-source remote --model gpt-4-turbo
```

## Command Line Arguments

- `--since-days`: Number of days to look back from today (required)
- `--platform`: Platform to fetch messages from (choices: "discord", "slack", default: "discord")
- `--channel`: Channel ID (Discord) or Channel name (Slack) (required)
- `--model-source`: Source of the model to use for summarization (choices: "local", "remote", default: "local")
- `--model`: Name of the model to use (default: "deepseek-r1-distill-qwen-7b" for local, "gpt-4-turbo" for remote)
- `--dump-file`: Optional: Save summary to a markdown file. If no path is provided, saves to current directory.
- `--dump-collected-chat-history`: Optional: Save the collected chat history to a file alongside the summary
- `--chat`: Optional: Start an interactive chat session with the collected conversation history

## Interactive Chat Commands

When in the interactive chat session, the following commands are available:

- `help`: Show available commands
- `exit`, `quit`, or `q`: End the chat session
- `summary`: Generate a summary of the chat history
- `users`: List all users mentioned in the chat history

## Requirements

- Python 3.8+
- discord.py
- slack-sdk
- langchain
- langchain-openai
- langchain-community
- python-dotenv
- colorama

## Discord Bot Setup

1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a bot for your application
3. Enable the following intents for your bot:
   - Message Content Intent
4. Generate a token for your bot
5. Invite the bot to your server with the necessary permissions to read message history

## Slack Bot Setup

1. Create a Slack app at [Slack API](https://api.slack.com/apps)
2. Add the following OAuth scopes to your bot:
   - `channels:history` - To read messages from public channels
   - `groups:history` - To read messages from private channels
   - `im:history` - To read direct messages
   - `mpim:history` - To read group direct messages
   - `users:read` - To get user information
3. Install the app to your workspace
4. Copy the Bot User OAuth Token to your `.env` file as `SLACK_TOKEN`

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
