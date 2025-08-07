# 💬 What The Chat

> 🚀 **A powerful, modular Python package for fetching and summarizing chat history from Discord or Slack channels with AI-powered insights!**

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Discord](https://img.shields.io/badge/Discord-7289DA?logo=discord&logoColor=white)](https://discord.com/)
[![Slack](https://img.shields.io/badge/Slack-4A154B?logo=slack&logoColor=white)](https://slack.com/)

</div>

---

## 🌟 **Overview**

Transform your Discord or Slack conversations into **actionable insights** with AI-powered summarization and interactive chat capabilities!

### ✨ **What it does:**
- 📥 **Fetch** all messages from Discord/Slack channels since any date
- 🧵 **Include** messages from threads within channels  
- 🤖 **Generate** intelligent summaries using local or remote LLMs
- 💾 **Save** both full chat history and summaries to files
- 💭 **Chat** interactively with your conversation history
- 🔧 **Extend** easily with modular architecture for web apps, bots, and more

---

## 🎯 **Features**

<table>
<tr>
<td width="50%">

### 🌐 **Multi-Platform**
- 🎮 **Discord** channel support
- 💼 **Slack** workspace integration  
- 🧵 **Thread** message collection
- 👥 **User reference** standardization

</td>
<td width="50%">

### 🧠 **AI-Powered Insights**
- 📊 **Smart summarization** based on timespan:
  - ⚡ Project Event Update (0-2 days)
  - 📝 Periodical Digest (3-6 days) 
  - 📋 Full Project Status (7+ days)
- 🤖 **Local models** (via Ollama)
- ☁️ **Remote models** (via OpenAI)

</td>
</tr>
<tr>
<td width="50%">

### 💬 **Interactive Features**
- 🗣️ **Chat** with your history
- ❓ **Ask questions** about conversations
- 🎨 **Colorful terminal** output
- ⌨️ **Graceful exit** handling

</td>
<td width="50%">

### 🔧 **Developer Friendly**
- 📦 **Modular architecture**
- 🐍 **Clean Python package**
- 🔌 **Easy extension** for bots/web apps
- 📚 **Comprehensive documentation**

</td>
</tr>
</table>

---

## 🚀 **Quick Start**

### 📦 **Installation**

<details>
<summary>🔥 <strong>Option A: Using pixi (recommended)</strong></summary>

```bash
git clone https://github.com/ulfaslak/what-the-chat.git
cd what-the-chat
pixi install
```

</details>

<details>
<summary>🐍 <strong>Option B: Using pip</strong></summary>

```bash
# From source
git clone https://github.com/ulfaslak/what-the-chat.git
cd what-the-chat
pip install -e .

# Or directly from GitHub
pip install git+https://github.com/ulfaslak/what-the-chat.git
```

</details>

### ⚙️ **Configuration**

Create a `.env` file with your tokens:

```bash
# 🎮 Discord (required for Discord channels)
DISCORD_TOKEN=your_discord_bot_token

# 💼 Slack (required for Slack channels)  
SLACK_TOKEN=your_slack_bot_token

# 🤖 OpenAI (only needed for remote models)
OPENAI_API_KEY=your_openai_api_key
```

---

## 💻 **Usage Examples**

### 🎮 **Discord Channel Summarization**

```bash
# 📊 Get a 7-day summary with interactive chat
python scripts/launch_cli.py --since-days 7 --channel 123456789012345678 --chat

# 💾 Save everything to files
python scripts/launch_cli.py --since-days 30 --channel 123456789012345678 \
  --dump-file ./output --dump-collected-chat-history

# 🤖 Use GPT-4 for summarization
python scripts/launch_cli.py --since-days 7 --channel 123456789012345678 \
  --model-source remote --model gpt-4o --chat
```

### 💼 **Slack Channel Analysis**

```bash
# 📈 Analyze your #general channel
python scripts/launch_cli.py --since-days 14 --platform slack \
  --channel general --chat
```

### 🐍 **Python Package Integration**

<details>
<summary>🔥 <strong>Click to see code example</strong></summary>

```python
import os
from datetime import datetime, timedelta
from what_the_chat import DiscordPlatform, SlackPlatform, SummarizationService, ChatService

# 🔐 Get your tokens (manage however you prefer!)
discord_token = os.getenv("DISCORD_TOKEN")
slack_token = os.getenv("SLACK_TOKEN") 
openai_api_key = os.getenv("OPENAI_API_KEY")

# 🎮 Discord example
discord = DiscordPlatform(discord_token)
since_date = datetime.now() - timedelta(days=7)

# 📥 Fetch messages
chat_history, first_date = await discord.fetch_messages_with_token(channel_id, since_date)
user_mapping = discord.get_user_mapping()

# 💼 Or use Slack
slack = SlackPlatform(slack_token)
chat_history, first_date = slack.fetch_messages_with_token("general", since_date)

# 🤖 Generate AI summary
summarizer = SummarizationService("remote", "gpt-4o", api_key=openai_api_key)
summary = summarizer.generate_summary(chat_history, user_mapping)

# 💬 Interactive chat with your history
chat_service = ChatService("remote", "gpt-4o", api_key=openai_api_key)
chat_service.start_interactive_session(chat_history, user_mapping)

# 🏠 For local models (no API key needed!)
local_summarizer = SummarizationService("local", "deepseek-r1-distill-qwen-7b")
summary = local_summarizer.generate_summary(chat_history, user_mapping)
```

</details>

---

## 🛠️ **Extensibility**

Build amazing things with the modular architecture! 

<details>
<summary>🌐 <strong>Web Application Example</strong></summary>

```python
from what_the_chat import DiscordPlatform, SummarizationService
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/summarize', methods=['POST'])
def summarize_endpoint():
    discord_token = request.json['discord_token']
    channel_id = request.json['channel_id']
    
    # 🚀 Use the same core components!
    platform = DiscordPlatform(discord_token)
    summarizer = SummarizationService("remote", "gpt-4o", api_key=openai_key)
    
    # ✨ Your web logic here
    return jsonify({"summary": "..."})
```

</details>

<details>
<summary>🤖 <strong>Discord Bot Example</strong></summary>

```python
from what_the_chat import DiscordPlatform, ChatService
import discord
from discord.ext import commands

class SummaryBot(commands.Cog):
    def __init__(self, bot):
        self.platform = DiscordPlatform()
        self.chat_service = ChatService("remote", "gpt-4o", api_key=api_key)
    
    @commands.command()
    async def summarize(self, ctx, days: int):
        # 🔄 Reuse the platform logic!
        history, _ = await self.platform.fetch_messages(ctx.bot, ctx.channel.id, since_date)
        # ✨ Your bot logic here
```

</details>

<details>
<summary>💼 <strong>Slack Bot Example</strong></summary>

```python
from what_the_chat import SlackPlatform, SummarizationService
from slack_bolt import App

app = App(token=slack_token)
platform = SlackPlatform(slack_token)
summarizer = SummarizationService("local", "deepseek-r1-distill-qwen-7b")

@app.command("/summarize")
def summarize_command(ack, say, command):
    # 🔄 Reuse the platform and summarization logic
    # ✨ Your Slack bot logic here
    pass
```

</details>

---

## 💬 **Interactive Chat Commands**

When chatting with your history, use these commands:

| Command | Description | Example |
|---------|-------------|---------|
| `help` | 📋 Show available commands | `help` |
| `exit`, `quit`, `q` | 👋 End chat gracefully | `quit` |
| `summary` | 📊 Generate new summary | `summary` |
| `users` | 👥 List all users in chat | `users` |
| `Ctrl+C` | ⚡ Quick exit | *keyboard shortcut* |

---

## 📁 **Package Structure**

```
📦 what_the_chat/
├── 📄 __init__.py              # Main package exports
├── 🔧 summarize.py             # High-level API & compatibility  
├── 🌐 platforms/               # Platform integrations
│   ├── 🎮 discord.py          # Discord platform class
│   └── 💼 slack.py            # Slack platform class
├── 🤖 llm/                    # LLM services
│   ├── 📊 summarization.py    # Summary generation
│   └── 💬 chat.py             # Interactive chat
├── 🛠️ utils/                  # Utilities
│   └── ✨ formatting.py       # Text processing
└── 📋 models/                 # Data models
    └── 💌 message.py          # Message & ChatHistory classes
📁 scripts/
└── 🚀 launch_cli.py           # CLI application entry point
```

---

## 🔧 **Setup Guides**

<details>
<summary>🎮 <strong>Discord Bot Setup</strong></summary>

### Discord Bot Configuration

1. 🌐 Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. ➕ **Create New Application** → Name it (e.g., "Chat Summarizer")
3. 🤖 Go to **Bot** section → **Add Bot**
4. ⚙️ **Enable these Bot Permissions:**
   - ✅ Read Message History
   - ✅ View Channels  
   - ✅ Read Messages/View Channels
5. 🔐 **Enable Privileged Gateway Intents:**
   - ✅ **Message Content Intent** (important!)
6. 🔑 Copy the **Bot Token** → Add to your `.env` as `DISCORD_TOKEN`
7. 🎯 **Invite Bot to Server:**
   - Go to **OAuth2** → **URL Generator**
   - Select **bot** scope
   - Select **Read Message History** permission
   - Use generated URL to invite bot

</details>

<details>
<summary>💼 <strong>Slack App Setup</strong></summary>

### Slack App Configuration  

1. 🌐 Go to [Slack API](https://api.slack.com/apps)
2. ➕ **Create New App** → **From scratch**
3. 🔐 **Add OAuth Scopes** (in OAuth & Permissions):
   - `channels:history` - 📖 Read public channel messages
   - `groups:history` - 📖 Read private channel messages  
   - `im:history` - 📖 Read direct messages
   - `mpim:history` - 📖 Read group DMs
   - `users:read` - 👥 Get user information
4. 🏢 **Install App to Workspace**
5. 🔑 Copy **Bot User OAuth Token** → Add to `.env` as `SLACK_TOKEN`

</details>

---

## 🎨 **Command Line Arguments**

| Argument | Description | Example | Required |
|----------|-------------|---------|----------|
| `--since-days` | 📅 Days to look back | `--since-days 7` | ✅ |
| `--platform` | 🌐 Discord or Slack | `--platform slack` | ❌ (default: discord) |
| `--channel` | 📺 Channel ID/name | `--channel general` | ✅ |
| `--model-source` | 🤖 Local or remote AI | `--model-source remote` | ❌ (default: local) |
| `--model` | 🧠 Specific model name | `--model gpt-4o` | ❌ |
| `--dump-file` | 💾 Save summary to file | `--dump-file ./output` | ❌ |
| `--dump-collected-chat-history` | 📁 Save full chat history | *(flag)* | ❌ |
| `--chat` | 💬 Start interactive chat | *(flag)* | ❌ |

---

## ⚡ **Requirements**

### 🐍 **Core Dependencies**
- **Python 3.10+** 
- **discord.py** (🎮 Discord integration)
- **slack-sdk** (💼 Slack integration)  
- **langchain-core** (🤖 LLM functionality)
- **langchain-openai** (☁️ OpenAI models)
- **langchain-community** (🏠 Local models via Ollama)
- **colorama** (🎨 Colored terminal output)

---

## 📄 **License**

**MIT License** - feel free to use this in your own projects! 🎉

---

## 🤝 **Contributing**

Contributions are **super welcome**! 🙌

- 🐛 **Found a bug?** Open an issue
- 💡 **Have an idea?** Start a discussion  
- 🔧 **Want to contribute?** Submit a PR

---

<div align="center">

### 🌟 **Made with ❤️ for better team communication** 

**Star this repo if you find it useful!** ⭐

</div>