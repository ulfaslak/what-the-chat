"""Data models for chat messages and history."""

from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Represents a single chat message."""
    
    timestamp: datetime
    author: str
    content: str
    user_id: Optional[str] = None
    thread_name: Optional[str] = None
    is_thread_message: bool = False
    
    def format(self) -> str:
        """Format the message as a string."""
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp_str}] {self.author}: {self.content}"


@dataclass
class ChatHistory:
    """Represents a collection of chat messages with metadata."""
    
    messages: List[ChatMessage]
    user_mapping: Dict[str, str]
    first_message_date: datetime
    platform: str
    channel_name: str
    
    def format_as_text(self) -> str:
        """Format the entire chat history as a text string."""
        formatted_messages = []
        current_thread = None
        
        for message in self.messages:
            # Handle thread transitions
            if message.is_thread_message and message.thread_name != current_thread:
                if current_thread is not None:
                    formatted_messages.append("--- End of Thread ---\n")
                formatted_messages.append(f"\n--- Thread: {message.thread_name} ---")
                current_thread = message.thread_name
            elif not message.is_thread_message and current_thread is not None:
                formatted_messages.append("--- End of Thread ---\n")
                current_thread = None
            
            formatted_messages.append(message.format())
        
        # Close final thread if needed
        if current_thread is not None:
            formatted_messages.append("--- End of Thread ---\n")
        
        return "\n".join(formatted_messages)
    
    def get_message_count(self) -> int:
        """Get the total number of messages."""
        return len(self.messages)
    
    def get_user_count(self) -> int:
        """Get the number of unique users."""
        return len(self.user_mapping)
    
    def get_thread_count(self) -> int:
        """Get the number of unique threads."""
        threads = set()
        for message in self.messages:
            if message.is_thread_message and message.thread_name:
                threads.add(message.thread_name)
        return len(threads)
