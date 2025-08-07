"""What The Chat - A tool for summarizing and chatting with chat history.

This package provides functionality to:
- Fetch messages from Discord and Slack channels
- Generate intelligent summaries using LLMs
- Interactive chat with chat history
- Support for both local (Ollama) and remote (OpenAI) models

Main modules:
- platforms: Discord and Slack integrations
- llm: LLM services for summarization and chat
- utils: Utility functions for text processing
- models: Data models for messages and chat history
"""

from .summarize import (
    # Platform classes
    DiscordPlatform,
    SlackPlatform,
    # Service classes  
    SummarizationService,
    ChatService,
    # Model classes
    ChatMessage,
    ChatHistory,
    # Compatibility functions
    fetch_discord_messages,
    fetch_slack_messages,
    standardize_user_references,
    replace_user_ids_with_names,
    generate_summary,
    create_chat_chain,
    interactive_chat_session,
    create_discord_bot,
    # Factory functions
    get_discord_platform,
    get_slack_platform,
    get_summarization_service,
    get_chat_service,
)

__version__ = "0.2.0"
__author__ = "pymc-labs"

__all__ = [
    # Platform classes
    "DiscordPlatform", "SlackPlatform",
    # Service classes
    "SummarizationService", "ChatService", 
    # Model classes
    "ChatMessage", "ChatHistory",
    # Compatibility functions
    "fetch_discord_messages", "fetch_slack_messages",
    "standardize_user_references", "replace_user_ids_with_names",
    "generate_summary", "create_chat_chain", "interactive_chat_session",
    "create_discord_bot",
    # Factory functions
    "get_discord_platform", "get_slack_platform", 
    "get_summarization_service", "get_chat_service"
]
