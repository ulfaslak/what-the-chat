"""Text formatting utilities for user references and chat history."""

from typing import Dict


def standardize_user_references(chat_history: str, user_mapping: Dict[str, str]) -> str:
    """Standardize user references in the chat history by replacing usernames with consistent IDs.
    
    Args:
        chat_history: The raw chat history string
        user_mapping: Dictionary mapping usernames to user IDs
        
    Returns:
        Chat history with standardized user references
    """
    # Create a mapping of usernames to their IDs
    username_to_id = {
        username: f"<@{user_id}>" for username, user_id in user_mapping.items()
    }

    # Replace usernames with their ID mentions
    standardized_history = chat_history
    for username, id_mention in username_to_id.items():
        # Replace username in the format [timestamp] username: message
        standardized_history = standardized_history.replace(
            f"{username}", f"{id_mention}"
        )

    return standardized_history


def replace_user_ids_with_names(text: str, user_mapping: Dict[str, str]) -> str:
    """Replace Discord user IDs with actual usernames in the text.
    
    Args:
        text: Text containing user IDs in <@user_id> format
        user_mapping: Dictionary mapping usernames to user IDs
        
    Returns:
        Text with user IDs replaced by @username format
    """
    # Create a mapping of user IDs to usernames
    id_to_username = {
        f"<@{user_id}>": f"@{username}" for username, user_id in user_mapping.items()
    }

    # Replace user IDs with usernames
    processed_text = text
    for id_mention, username in id_to_username.items():
        processed_text = processed_text.replace(id_mention, username)

    return processed_text
