"""Tests for data models."""

import pytest
from datetime import datetime
from what_the_chat.models.message import ChatMessage, ChatHistory


class TestChatMessage:
    """Test cases for ChatMessage class."""
    
    def test_chat_message_creation(self):
        """Test basic ChatMessage creation."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        message = ChatMessage(
            timestamp=timestamp,
            author="test_user",
            content="Hello world!",
            user_id="123456",
            thread_name="general-discussion",
            is_thread_message=True
        )
        
        assert message.timestamp == timestamp
        assert message.author == "test_user"
        assert message.content == "Hello world!"
        assert message.user_id == "123456"
        assert message.thread_name == "general-discussion"
        assert message.is_thread_message is True
    
    def test_chat_message_defaults(self):
        """Test ChatMessage with default values."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        message = ChatMessage(
            timestamp=timestamp,
            author="test_user",
            content="Hello world!"
        )
        
        assert message.user_id is None
        assert message.thread_name is None
        assert message.is_thread_message is False
    
    def test_chat_message_format(self):
        """Test message formatting."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        message = ChatMessage(
            timestamp=timestamp,
            author="Alice",
            content="How's the project going?"
        )
        
        expected = "[2024-01-15 10:30:00] Alice: How's the project going?"
        assert message.format() == expected


class TestChatHistory:
    """Test cases for ChatHistory class."""
    
    def test_chat_history_creation(self):
        """Test basic ChatHistory creation."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        messages = [
            ChatMessage(timestamp, "Alice", "Hello!"),
            ChatMessage(timestamp, "Bob", "Hi there!")
        ]
        user_mapping = {"alice_id": "Alice", "bob_id": "Bob"}
        
        history = ChatHistory(
            messages=messages,
            user_mapping=user_mapping,
            first_message_date=timestamp,
            platform="discord",
            channel_name="general"
        )
        
        assert len(history.messages) == 2
        assert history.user_mapping == user_mapping
        assert history.first_message_date == timestamp
        assert history.platform == "discord"
        assert history.channel_name == "general"
    
    def test_get_message_count(self):
        """Test message count functionality."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        messages = [
            ChatMessage(timestamp, "Alice", "Hello!"),
            ChatMessage(timestamp, "Bob", "Hi there!"),
            ChatMessage(timestamp, "Charlie", "Good morning!")
        ]
        
        history = ChatHistory(
            messages=messages,
            user_mapping={},
            first_message_date=timestamp,
            platform="discord",
            channel_name="general"
        )
        
        assert history.get_message_count() == 3
    
    def test_get_user_count(self):
        """Test user count functionality."""
        user_mapping = {"alice_id": "Alice", "bob_id": "Bob", "charlie_id": "Charlie"}
        
        history = ChatHistory(
            messages=[],
            user_mapping=user_mapping,
            first_message_date=datetime.now(),
            platform="discord",
            channel_name="general"
        )
        
        assert history.get_user_count() == 3
    
    def test_get_thread_count(self):
        """Test thread count functionality."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        messages = [
            ChatMessage(timestamp, "Alice", "Hello!", thread_name="thread1", is_thread_message=True),
            ChatMessage(timestamp, "Bob", "Hi!", thread_name="thread1", is_thread_message=True),
            ChatMessage(timestamp, "Charlie", "Hey!", thread_name="thread2", is_thread_message=True),
            ChatMessage(timestamp, "Dave", "General message", is_thread_message=False)
        ]
        
        history = ChatHistory(
            messages=messages,
            user_mapping={},
            first_message_date=timestamp,
            platform="discord",
            channel_name="general"
        )
        
        assert history.get_thread_count() == 2
    
    def test_format_as_text_simple(self):
        """Test basic text formatting without threads."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        messages = [
            ChatMessage(timestamp, "Alice", "Hello!"),
            ChatMessage(timestamp, "Bob", "Hi there!")
        ]
        
        history = ChatHistory(
            messages=messages,
            user_mapping={},
            first_message_date=timestamp,
            platform="discord",
            channel_name="general"
        )
        
        expected = "[2024-01-15 10:30:00] Alice: Hello!\n[2024-01-15 10:30:00] Bob: Hi there!"
        assert history.format_as_text() == expected
    
    def test_format_as_text_with_threads(self):
        """Test text formatting with thread transitions."""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        messages = [
            ChatMessage(timestamp, "Alice", "Hello!", is_thread_message=False),
            ChatMessage(timestamp, "Bob", "In thread", thread_name="Project Discussion", is_thread_message=True),
            ChatMessage(timestamp, "Charlie", "Also in thread", thread_name="Project Discussion", is_thread_message=True),
            ChatMessage(timestamp, "Dave", "Back to main", is_thread_message=False)
        ]
        
        history = ChatHistory(
            messages=messages,
            user_mapping={},
            first_message_date=timestamp,
            platform="discord",
            channel_name="general"
        )
        
        formatted = history.format_as_text()
        
        # Check that thread markers are present
        assert "--- Thread: Project Discussion ---" in formatted
        assert "--- End of Thread ---" in formatted
        # Check that all messages are present
        assert "Alice: Hello!" in formatted
        assert "Bob: In thread" in formatted
        assert "Charlie: Also in thread" in formatted
        assert "Dave: Back to main" in formatted
    
    def test_empty_chat_history(self):
        """Test empty chat history."""
        history = ChatHistory(
            messages=[],
            user_mapping={},
            first_message_date=datetime.now(),
            platform="discord",
            channel_name="general"
        )
        
        assert history.get_message_count() == 0
        assert history.get_user_count() == 0
        assert history.get_thread_count() == 0
        assert history.format_as_text() == ""
