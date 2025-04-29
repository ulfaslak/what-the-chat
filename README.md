# What The Chat

A Python tool for fetching and summarizing Discord chat history from specific channels.

## Overview

This tool allows you to:
- Fetch all messages from a Discord channel since a specified date
- Include messages from threads within the channel
- Generate a structured summary of the chat history using OpenAI's GPT-4 Turbo
- Save both the full chat history and the summary to text files

## Features

- **Comprehensive Message Collection**: Fetches all messages from a specified Discord channel since a given date
- **Thread Support**: Automatically collects messages from all threads within the channel
- **User Reference Standardization**: Standardizes user references in the chat history
- **Intelligent Summarization**: Generates a structured summary based on the time span of messages:
  - Project Event Update (0-2 days)
  - Periodical Digest (3-6 days)
  - Full Project Status Summary (7+ days)
- **User-Friendly Output**: Replaces Discord user IDs with actual usernames in the summary for better readability
- **Accurate Filenames**: Uses the actual first message date in filenames for accurate time range representation

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/discord-history-fetcher.git
   cd discord-history-fetcher
   ```

2. Install the required dependencies (e.g. in a new environment):
   ```
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following variables (see **Discord Bot Setup** section below for more details on how to attain a Discord bot token):
   ```
   DISCORD_TOKEN=your_discord_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

### Basic Usage

To fetch chat history from a Discord channel since a specific date, and return a summary:

```
python fetch_discord_history.py --since 2024-04-01 --channel 123456789012345678 --summarize
```

This will save:
1. The summary to a file named `discord_history_summary_[channel_name]_[first_message_date]_[today's_date].md`
2. The full chat history to a file named `discord_history_[channel_name]_[first_message_date]_[today's_date].md`

### Without Summarization

To fetch chat history without generating a summary:

```
python fetch_discord_history.py --since 2024-04-01 --channel 123456789012345678
```

This will save the chat history to a file named `discord_history___[channel_name]___[first_message_date]__[today's_date].md`.

## Command Line Arguments

- `--since`: Start date in YYYY-MM-DD format (required)
- `--channel`: Discord channel ID (required)
- `--summarize`: Flag to generate a summary of the chat history (optional)

## Requirements

- Python 3.8+
- discord.py
- langchain
- langchain-openai
- python-dotenv

## Discord Bot Setup

1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a bot for your application
3. Enable the following intents for your bot:
   - Message Content Intent
4. Generate a token for your bot
5. Invite the bot to your server with the necessary permissions to read message history

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.