# What The Chat 💬

> A modular Python package for fetching and summarizing chat history from Discord or Slack channels using AI.

https://github.com/user-attachments/assets/efc9d54e-eff4-4528-b7dd-43994660e96d

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Beta](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/ulfaslak/what-the-chat)

</div>

> ⚠️ **Beta Notice**: This package is currently in beta. While core functionality works, some features may be unstable or incomplete. Use at your own discretion and expect potential breaking changes in future releases.

## 🌟 Overview

Transform your Discord and Slack conversations into actionable insights! This package provides:

📥 **Fetch** all messages from Discord/Slack channels since any date  
🧵 **Include** messages from threads within channels  
🤖 **Generate** intelligent summaries using local or remote LLMs  
💾 **Save** both full chat history and summaries to files  
💭 **Chat** interactively with your conversation history  
🔧 **Import** into your own projects and build cool things with it (bots, web apps, etc.)

## ✨ Features

### 🔗 Versatile
- **Discord** and **Slack** channel integration
- **Thread support** - automatically collects messages from all threads
- **User reference standardization** - clean, readable output

### 🧠 Intelligent Summarization
- **Smart summarization** based on timespan:
  - `📋 Project Event Update` (0-2 days)
  - `📊 Periodical Digest` (3-6 days)
  - `📈 Full Project Status Summary` (7+ days)
- **Model flexibility** - local models (Ollama) or remote (OpenAI)
- **User-friendly output** - replaces IDs with actual usernames

### 💬 Interactive Features
- **Chat with your history** - ask questions about conversations
- **Colorful terminal output** with clear visual cues
- **Graceful exit handling** - no more ugly tracebacks
- **Export formats** - markdown files with accurate timestamps

### 🛠️ Developer Friendly
- **Modular architecture** - clean separation of concerns
- **Python package** - easy integration into other projects
- **Explicit token handling** - no hidden environment dependencies
- **Extensible design** - perfect for building bots and web apps

## 🚀 Quick Start

Originally created for personal use as a CLI application, this package has been refactored to also work as an importable Python package for your own projects.

### 💻 Running the CLI Application

**1. Clone and Install**
```bash
git clone https://github.com/yourusername/what-the-chat.git
cd what-the-chat
```

**2. Choose Installation Method**

<details>
<summary><strong>🎯 Option A: Using pixi (recommended)</strong></summary>

```bash
pixi install
```
</details>

<details>
<summary><strong>🐍 Option B: Using pip</strong></summary>

```bash
pip install -e .
```
</details>

**3. Setup Environment**
Create a `.env` file with your tokens:
```bash
DISCORD_TOKEN=your_discord_bot_token
SLACK_TOKEN=your_slack_bot_token
OPENAI_API_KEY=your_openai_api_key  # Only needed for remote models
```

### 📦 Installing as a Package

Add to your own projects:
```bash
pip install git+https://github.com/ulfaslak/what-the-chat.git
```

## 💡 Usage Examples

### 🖥️ CLI Application

#### 🎯 Basic Usage

Get a 30-day summary with interactive chat:

```bash
# Using pixi
pixi run python scripts/launch_cli.py --since-days 30 --channel 123456789012345678 --chat

# Or direct script execution
python scripts/launch_cli.py --since-days 30 --channel 123456789012345678 --chat
```

**Slack channels:**
```bash
python scripts/launch_cli.py --since-days 30 --platform slack --channel general --chat
```

**✨ What happens:**
1. 📥 Fetches messages from the specified channel for the last 30 days
2. 🤖 Generates an intelligent summary of the chat history
3. 💬 Starts an interactive chat session for Q&A

#### 💾 Saving to Files

Save everything for later analysis:

```bash
python scripts/launch_cli.py --since-days 30 --channel 123456789012345678 \
  --dump-file ./output --dump-collected-chat-history
```

**📁 Creates:**
- `discord_history_summary_[channel]_[dates].md` - AI-generated summary
- `discord_history_[channel]_[dates].md` - Full conversation log

#### 🌐 Using Remote Models

Switch to powerful cloud models:

```bash
python scripts/launch_cli.py --since-days 30 --channel 123456789012345678 \
  --model-source remote --model gpt-4o
```

### 🐍 Python Package Integration

Build What The Chat into your own applications:

```python
import os
from datetime import datetime, timedelta
from what_the_chat import DiscordPlatform, SlackPlatform, SummarizationService, ChatService

# Get tokens and API keys explicitly
discord_token = os.getenv("DISCORD_TOKEN")  # or however you manage secrets
slack_token = os.getenv("SLACK_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Discord example with explicit token
discord = DiscordPlatform(discord_token)
since_date = datetime.now() - timedelta(days=7)

# Fetch Discord messages (in an async context)
chat_history, first_date = await discord.fetch_messages_with_token(channel_id, since_date)
user_mapping = discord.get_user_mapping()

# Or Slack example with explicit token
slack = SlackPlatform(slack_token)
chat_history, first_date = slack.fetch_messages_with_token("general", since_date)
user_mapping = slack.get_user_mapping()

# Generate summary with explicit API key
summarizer = SummarizationService(model_source="remote", model="gpt-4o", api_key=openai_api_key)
summary = summarizer.generate_summary(chat_history, user_mapping)

# Start interactive chat with explicit API key
chat_service = ChatService(model_source="remote", model="gpt-4o", api_key=openai_api_key)
chat_service.start_interactive_session(chat_history, user_mapping)

# For local models, no API key needed
local_summarizer = SummarizationService(model_source="local", model="deepseek-r1-distill-qwen-7b")
local_summary = local_summarizer.generate_summary(chat_history, user_mapping)
```

## ⚙️ Command Line Arguments

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| `--since-days` | 📅 Number of days to look back | ✅ | - |
| `--platform` | 🔗 Platform (discord/slack) | - | discord |
| `--channel` | 📺 Channel ID or name | ✅ | - |
| `--model-source` | 🧠 Model source (local/remote) | - | local |
| `--model` | 🤖 Specific model name | - | deepseek-r1-distill-qwen-7b |
| `--dump-file` | 💾 Save summary to file | - | - |
| `--dump-collected-chat-history` | 📄 Save full chat history | - | false |
| `--chat` | 💬 Start interactive chat | - | false |

## 💬 Interactive Chat Commands

Once you're in the chat session, use these commands:

| Command | Description |
|---------|-------------|
| `help` | 📖 Show available commands |
| `exit`, `quit`, `q` | 👋 End chat gracefully |
| `summary` | 📋 Generate new summary |
| `users` | 👥 List all users in chat |
| `Ctrl+C` | ⚡ Quick exit |

## 📁 Package Structure

```
what_the_chat/
├── __init__.py              # Main package exports
├── summarize.py             # High-level API & compatibility layer
├── platforms/               # Platform integrations
│   ├── discord.py          # Discord platform class
│   └── slack.py            # Slack platform class
├── llm/                    # LLM services
│   ├── summarization.py    # Summary generation service
│   └── chat.py             # Interactive chat service
├── utils/                  # Utilities
│   └── formatting.py       # Text processing utilities
└── models/                 # Data models
    └── message.py          # Message and ChatHistory classes
scripts/
└── launch_cli.py           # CLI application entry point
```

## 📋 Requirements

### Core Dependencies
- 🐍 **Python 3.10+**
- 🎮 **discord.py** - Discord integration
- 💼 **slack-sdk** - Slack integration  
- 🧠 **langchain-core** - LLM functionality
- 🌐 **langchain-openai** - OpenAI models
- 🏠 **langchain-community** - Ollama and local models
- 🎨 **colorama** - Colored terminal output

## 🔧 Setup Guides

<details>
<summary><strong>🎮 Discord Bot Setup</strong></summary>

1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a bot for your application
3. Enable the following intents:
   - ✅ **Message Content Intent**
4. Generate a token for your bot
5. Invite the bot with **Read Message History** permissions

</details>

<details>
<summary><strong>💼 Slack Bot Setup</strong></summary>

1. Create a Slack app at [Slack API](https://api.slack.com/apps)
2. Add these OAuth scopes:
   - ✅ `channels:history` - read public channels
   - ✅ `groups:history` - read private channels  
   - ✅ `im:history` - read direct messages
   - ✅ `mpim:history` - read group direct messages
   - ✅ `users:read` - get user information
3. Install the app to your workspace
4. Copy the **Bot User OAuth Token** to your `.env` file as `SLACK_TOKEN`

</details>

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<div align="center">

**⭐ If this project helped you, please consider giving it a star! ⭐**

</div>
