"""Main API module for what_the_chat package.

This module provides a high-level interface to all chat summarization and interaction functionality.
It serves as the main entry point for other applications (CLI, web, bots) to use the core features.
"""

from datetime import datetime
from typing import Dict, Tuple

# Import platform integrations
from .platforms.discord import DiscordPlatform
from .platforms.slack import SlackPlatform

# Import LLM services
from .llm.summarization import SummarizationService
from .llm.chat import ChatService

# Import utilities
from .utils.formatting import standardize_user_references as _standardize_user_references
from .utils.formatting import replace_user_ids_with_names as _replace_user_ids_with_names

# Import models
from .models.message import ChatMessage, ChatHistory


# High-level API functions for backward compatibility

async def fetch_discord_messages(bot, channel_id: int, since_date: datetime) -> Tuple[str, datetime]:
    """Fetch messages from a Discord channel.
    
    Args:
        bot: Discord bot instance
        channel_id: Discord channel ID  
        since_date: Date to start fetching messages from

    Returns:
        tuple: (formatted_history, first_message_date)
    """
    platform = DiscordPlatform()
    return await platform.fetch_messages(bot, channel_id, since_date)


def fetch_slack_messages(slack_token: str, channel_name: str, since_date: datetime) -> Tuple[str, datetime]:
    """Fetch messages from a Slack channel.
    
    Args:
        slack_token: Slack API token
        channel_name: Slack channel name
        since_date: Date to start fetching messages from

    Returns:
        tuple: (formatted_history, first_message_date)
    """
    platform = SlackPlatform()
    return platform.fetch_messages(slack_token, channel_name, since_date)


def standardize_user_references(chat_history: str, user_mapping: Dict[str, str] = None) -> str:
    """Standardize user references in the chat history.
    
    Args:
        chat_history: Raw chat history string
        user_mapping: Optional user mapping dictionary
        
    Returns:
        Chat history with standardized user references
    """
    return _standardize_user_references(chat_history, user_mapping or {})


def replace_user_ids_with_names(text: str, user_mapping: Dict[str, str] = None) -> str:
    """Replace user IDs with usernames in text.
    
    Args:
        text: Text containing user IDs
        user_mapping: Optional user mapping dictionary
        
    Returns:
        Text with user IDs replaced by usernames
    """
    return _replace_user_ids_with_names(text, user_mapping or {})


def generate_summary(chat_history: str, model_source: str, model: str, user_mapping: Dict[str, str] = None) -> str:
    """Generate a summary of the chat history.
    
    Args:
        chat_history: Formatted chat history to summarize
        model_source: "local" or "remote"
        model: Model name to use
        user_mapping: Optional user mapping for ID replacement
        
    Returns:
        Generated summary text
    """
    service = SummarizationService(model_source, model)
    return service.generate_summary(chat_history, user_mapping)


def create_chat_chain(chat_history: str, model_source: str, model: str):
    """Create a chat chain for interactive chat.
    
    Args:
        chat_history: Formatted chat history for context
        model_source: "local" or "remote"
        model: Model name to use
        
    Returns:
        Configured chat chain
    """
    service = ChatService(model_source, model)
    return service.create_chat_chain(chat_history)


def interactive_chat_session(chat_history: str, model_source: str, model: str, user_mapping: Dict[str, str] = None):
    """Start an interactive chat session.
    
    Args:
        chat_history: Formatted chat history for context
        model_source: "local" or "remote"
        model: Model name to use
        user_mapping: Optional user mapping for ID replacement
    """
    service = ChatService(model_source, model)
    service.start_interactive_session(chat_history, user_mapping)


def create_discord_bot():
    """Create a Discord bot instance.
    
    Returns:
        Configured Discord bot
    """
    platform = DiscordPlatform()
    return platform.create_bot()


# Factory functions for platform instances

def get_discord_platform() -> DiscordPlatform:
    """Get a Discord platform instance."""
    return DiscordPlatform()


def get_slack_platform() -> SlackPlatform:
    """Get a Slack platform instance."""
    return SlackPlatform()


def get_summarization_service(model_source: str = "local", model: str = "deepseek-r1-distill-qwen-7b") -> SummarizationService:
    """Get a summarization service instance.
    
    Args:
        model_source: "local" or "remote"
        model: Model name to use
        
    Returns:
        Configured summarization service
    """
    return SummarizationService(model_source, model)


def get_chat_service(model_source: str = "local", model: str = "deepseek-r1-distill-qwen-7b") -> ChatService:
    """Get a chat service instance.
    
    Args:
        model_source: "local" or "remote" 
        model: Model name to use
        
    Returns:
        Configured chat service
    """
    return ChatService(model_source, model)


# Export all the main classes for direct usage
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