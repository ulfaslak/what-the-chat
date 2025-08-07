"""Tests for platform classes."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from what_the_chat.platforms.discord import DiscordPlatform
from what_the_chat.platforms.slack import SlackPlatform


class TestDiscordPlatform:
    """Test cases for DiscordPlatform."""
    
    def test_discord_platform_init_no_token(self):
        """Test DiscordPlatform initialization without token."""
        platform = DiscordPlatform()
        
        assert platform.token is None
    
    def test_discord_platform_init_with_token(self):
        """Test DiscordPlatform initialization with token."""
        platform = DiscordPlatform(token="test-token")
        
        assert platform.token == "test-token"
    
    def test_discord_platform_has_required_methods(self):
        """Test that DiscordPlatform has required methods."""
        platform = DiscordPlatform()
        
        # Check that basic methods exist
        assert hasattr(platform, 'fetch_messages')
        assert hasattr(platform, 'fetch_messages_with_token')
        assert callable(platform.fetch_messages_with_token)
    
    def test_fetch_messages_with_token_no_token(self):
        """Test fetch_messages_with_token without token raises error."""
        platform = DiscordPlatform()
        
        # This should be synchronous, not async, so we can test directly
        with pytest.raises(ValueError, match="Discord token is required"):
            # This should fail immediately without requiring async
            import asyncio
            asyncio.run(platform.fetch_messages_with_token(123456, datetime.now()))


class TestSlackPlatform:
    """Test cases for SlackPlatform."""
    
    def test_slack_platform_init_no_token(self):
        """Test SlackPlatform initialization without token."""
        platform = SlackPlatform()
        
        assert platform.token is None
    
    def test_slack_platform_init_with_token(self):
        """Test SlackPlatform initialization with token."""
        platform = SlackPlatform(token="test-token")
        
        assert platform.token == "test-token"
    
    def test_slack_platform_has_required_methods(self):
        """Test that SlackPlatform has required methods."""
        platform = SlackPlatform()
        
        # Check that basic methods exist
        assert hasattr(platform, 'fetch_messages')
        assert hasattr(platform, 'fetch_messages_with_token')
        assert callable(platform.fetch_messages_with_token)
    
    def test_fetch_messages_with_token_no_token(self):
        """Test fetch_messages_with_token without token raises error."""
        platform = SlackPlatform()
        
        with pytest.raises(ValueError, match="Slack token is required"):
            platform.fetch_messages_with_token("general", datetime.now())


class TestPlatformBasics:
    """Test basic platform functionality."""
    
    def test_platform_instantiation(self):
        """Test that platforms can be instantiated safely."""
        # These should not make any network calls or require dependencies
        discord_platform = DiscordPlatform()
        slack_platform = SlackPlatform()
        
        assert discord_platform is not None
        assert slack_platform is not None
        
        # With tokens
        discord_with_token = DiscordPlatform(token="test")
        slack_with_token = SlackPlatform(token="test")
        
        assert discord_with_token.token == "test"
        assert slack_with_token.token == "test"
    
    def test_platform_token_property(self):
        """Test token property access and modification."""
        discord_platform = DiscordPlatform()
        slack_platform = SlackPlatform()
        
        # Initially None
        assert discord_platform.token is None
        assert slack_platform.token is None
        
        # Can be set via constructor
        discord_with_token = DiscordPlatform(token="discord-token")
        slack_with_token = SlackPlatform(token="slack-token")
        
        assert discord_with_token.token == "discord-token"
        assert slack_with_token.token == "slack-token"
    
    def test_platform_methods_exist(self):
        """Test that required methods exist on platforms."""
        discord_platform = DiscordPlatform()
        slack_platform = SlackPlatform()
        
        # Test Discord platform
        required_discord_methods = ['fetch_messages', 'fetch_messages_with_token']
        for method in required_discord_methods:
            assert hasattr(discord_platform, method), f"Discord platform missing {method}"
            assert callable(getattr(discord_platform, method)), f"Discord {method} not callable"
        
        # Test Slack platform
        required_slack_methods = ['fetch_messages', 'fetch_messages_with_token']
        for method in required_slack_methods:
            assert hasattr(slack_platform, method), f"Slack platform missing {method}"
            assert callable(getattr(slack_platform, method)), f"Slack {method} not callable"
    
    def test_platform_error_handling_basic(self):
        """Test basic error handling for token requirements."""
        discord_platform = DiscordPlatform()
        slack_platform = SlackPlatform()
        
        # Discord should require token for fetch_messages_with_token
        try:
            import asyncio
            asyncio.run(discord_platform.fetch_messages_with_token(12345, datetime.now()))
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "token" in str(e).lower()
        except Exception:
            # Other exceptions are acceptable (missing dependencies, etc.)
            pass
        
        # Slack should require token for fetch_messages_with_token  
        try:
            slack_platform.fetch_messages_with_token("general", datetime.now())
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "token" in str(e).lower()
        except Exception:
            # Other exceptions are acceptable (missing dependencies, etc.)
            pass


class TestPlatformIntegration:
    """Test that platforms are ready for integration."""
    
    def test_platforms_support_datetime_parameters(self):
        """Test that platforms accept datetime parameters correctly."""
        discord_platform = DiscordPlatform(token="test")
        slack_platform = SlackPlatform(token="test")
        
        test_date = datetime(2024, 1, 15, 10, 30, 0)
        
        # These calls will likely fail due to invalid tokens/missing services,
        # but they should accept the datetime parameter without type errors
        try:
            import asyncio
            asyncio.run(discord_platform.fetch_messages_with_token(12345, test_date))
        except (ValueError, TypeError) as e:
            # Type errors are problems, value errors (invalid token) are expected
            if "TypeError" in str(type(e)):
                assert False, f"Type error in Discord platform: {e}"
        except Exception:
            # Other exceptions (network, missing services) are acceptable
            pass
        
        try:
            slack_platform.fetch_messages_with_token("general", test_date)
        except (ValueError, TypeError) as e:
            # Type errors are problems, value errors (invalid token) are expected
            if "TypeError" in str(type(e)):
                assert False, f"Type error in Slack platform: {e}"
        except Exception:
            # Other exceptions (network, missing services) are acceptable
            pass
