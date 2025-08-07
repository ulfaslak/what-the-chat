"""Tests for package imports and exports."""

import pytest


class TestPackageImports:
    """Test cases for package-level imports."""
    
    def test_main_imports(self):
        """Test that main classes can be imported from package root."""
        from what_the_chat import DiscordPlatform, SlackPlatform
        from what_the_chat import SummarizationService, ChatService
        from what_the_chat import ChatMessage, ChatHistory
        
        # Check that classes are importable
        assert DiscordPlatform is not None
        assert SlackPlatform is not None
        assert SummarizationService is not None
        assert ChatService is not None
        assert ChatMessage is not None
        assert ChatHistory is not None
    
    def test_compatibility_function_imports(self):
        """Test that compatibility functions can be imported."""
        from what_the_chat import (
            fetch_discord_messages,
            fetch_slack_messages,
            generate_summary,
            create_chat_chain,
            interactive_chat_session
        )
        
        # Check that functions are importable
        assert fetch_discord_messages is not None
        assert fetch_slack_messages is not None
        assert generate_summary is not None
        assert create_chat_chain is not None
        assert interactive_chat_session is not None
    
    def test_utility_function_imports(self):
        """Test that utility functions can be imported."""
        from what_the_chat import standardize_user_references, replace_user_ids_with_names
        
        assert standardize_user_references is not None
        assert replace_user_ids_with_names is not None
    
    def test_factory_function_imports(self):
        """Test that factory functions can be imported."""
        from what_the_chat import (
            get_discord_platform,
            get_slack_platform,
            get_summarization_service,
            get_chat_service
        )
        
        assert get_discord_platform is not None
        assert get_slack_platform is not None
        assert get_summarization_service is not None
        assert get_chat_service is not None
    
    def test_package_metadata(self):
        """Test that package metadata is available."""
        import what_the_chat
        
        assert hasattr(what_the_chat, '__version__')
        assert hasattr(what_the_chat, '__author__')
        assert what_the_chat.__version__ is not None
        assert what_the_chat.__author__ is not None
    
    def test_all_exports(self):
        """Test that __all__ exports work correctly."""
        import what_the_chat
        
        # Check that __all__ is defined
        assert hasattr(what_the_chat, '__all__')
        assert isinstance(what_the_chat.__all__, list)
        assert len(what_the_chat.__all__) > 0
        
        # Check that all items in __all__ are actually available
        for item in what_the_chat.__all__:
            assert hasattr(what_the_chat, item), f"Item '{item}' in __all__ but not available"
    
    def test_submodule_imports(self):
        """Test that submodules can be imported directly."""
        # Test platform imports
        from what_the_chat.platforms.discord import DiscordPlatform
        from what_the_chat.platforms.slack import SlackPlatform
        
        # Test LLM service imports
        from what_the_chat.llm.summarization import SummarizationService
        from what_the_chat.llm.chat import ChatService
        
        # Test model imports
        from what_the_chat.models.message import ChatMessage, ChatHistory
        
        # Test utility imports
        from what_the_chat.utils.formatting import standardize_user_references
        
        # All should be available
        assert DiscordPlatform is not None
        assert SlackPlatform is not None
        assert SummarizationService is not None
        assert ChatService is not None
        assert ChatMessage is not None
        assert ChatHistory is not None
        assert standardize_user_references is not None


class TestBasicFunctionality:
    """Test basic functionality without external dependencies."""
    
    def test_chat_message_instantiation(self):
        """Test that ChatMessage can be instantiated."""
        from what_the_chat import ChatMessage
        from datetime import datetime
        
        message = ChatMessage(
            timestamp=datetime.now(),
            author="test_user",
            content="test message"
        )
        
        assert message.author == "test_user"
        assert message.content == "test message"
    
    def test_platform_instantiation(self):
        """Test that platform classes can be instantiated."""
        from what_the_chat import DiscordPlatform, SlackPlatform
        
        # These should not raise errors when instantiated
        discord_platform = DiscordPlatform()
        slack_platform = SlackPlatform()
        
        assert discord_platform is not None
        assert slack_platform is not None
    
    def test_service_instantiation(self):
        """Test that service classes can be instantiated."""
        from what_the_chat import SummarizationService, ChatService
        
        # These should not raise errors when instantiated with basic params
        summarizer = SummarizationService(model_source="local", model="test-model")
        chat_service = ChatService(model_source="local", model="test-model")
        
        assert summarizer is not None
        assert chat_service is not None
    
    def test_utility_functions_callable(self):
        """Test that utility functions are callable."""
        from what_the_chat import standardize_user_references, replace_user_ids_with_names
        
        # Test with simple inputs
        result1 = standardize_user_references("test", {})
        result2 = replace_user_ids_with_names("test", {})
        
        assert result1 == "test"
        assert result2 == "test"
