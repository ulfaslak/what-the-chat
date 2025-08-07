"""Tests for utility functions."""

import pytest
from what_the_chat.utils.formatting import standardize_user_references, replace_user_ids_with_names


class TestFormattingUtils:
    """Test cases for formatting utility functions."""
    
    def test_standardize_user_references_basic(self):
        """Test basic user reference standardization."""
        chat_history = "[2024-01-15 10:30:00] Alice: Hello everyone!\n[2024-01-15 10:31:00] Bob: Hi Alice!"
        user_mapping = {"Alice": "123456", "Bob": "789012"}
        
        result = standardize_user_references(chat_history, user_mapping)
        expected = "[2024-01-15 10:30:00] <@123456>: Hello everyone!\n[2024-01-15 10:31:00] <@789012>: Hi <@123456>!"
        
        assert result == expected
    
    def test_standardize_user_references_no_users(self):
        """Test standardization with no users to replace."""
        chat_history = "[2024-01-15 10:30:00] System: Channel created"
        user_mapping = {"Alice": "123456"}
        
        result = standardize_user_references(chat_history, user_mapping)
        assert result == chat_history  # Should remain unchanged
    
    def test_standardize_user_references_empty_mapping(self):
        """Test standardization with empty user mapping."""
        chat_history = "[2024-01-15 10:30:00] Alice: Hello!"
        user_mapping = {}
        
        result = standardize_user_references(chat_history, user_mapping)
        assert result == chat_history  # Should remain unchanged
    
    def test_standardize_user_references_partial_match(self):
        """Test standardization with partial username matches."""
        chat_history = "[2024-01-15 10:30:00] Alice: Hello!\n[2024-01-15 10:31:00] Bob: Hi there!"
        user_mapping = {"Alice": "123456"}  # Only Alice is mapped
        
        result = standardize_user_references(chat_history, user_mapping)
        expected = "[2024-01-15 10:30:00] <@123456>: Hello!\n[2024-01-15 10:31:00] Bob: Hi there!"
        
        assert result == expected
    
    def test_replace_user_ids_with_names_basic(self):
        """Test basic user ID replacement with names."""
        text = "Hey <@123456>, can you check this? <@789012> might be interested too."
        user_mapping = {"Alice": "123456", "Bob": "789012"}
        
        result = replace_user_ids_with_names(text, user_mapping)
        expected = "Hey @Alice, can you check this? @Bob might be interested too."
        
        assert result == expected
    
    def test_replace_user_ids_with_names_no_ids(self):
        """Test replacement with no user IDs in text."""
        text = "This is a regular message with no user mentions."
        user_mapping = {"Alice": "123456", "Bob": "789012"}
        
        result = replace_user_ids_with_names(text, user_mapping)
        assert result == text  # Should remain unchanged
    
    def test_replace_user_ids_with_names_empty_mapping(self):
        """Test replacement with empty user mapping."""
        text = "Hey <@123456>, how are you?"
        user_mapping = {}
        
        result = replace_user_ids_with_names(text, user_mapping)
        assert result == text  # Should remain unchanged
    
    def test_replace_user_ids_with_names_unknown_id(self):
        """Test replacement with unknown user ID."""
        text = "Hey <@123456>, and also <@999999> (unknown user)."
        user_mapping = {"Alice": "123456"}
        
        result = replace_user_ids_with_names(text, user_mapping)
        expected = "Hey @Alice, and also <@999999> (unknown user)."
        
        assert result == expected
    
    def test_replace_user_ids_with_names_multiple_same_user(self):
        """Test replacement with multiple mentions of same user."""
        text = "<@123456> and <@123456> again, plus <@789012>."
        user_mapping = {"Alice": "123456", "Bob": "789012"}
        
        result = replace_user_ids_with_names(text, user_mapping)
        expected = "@Alice and @Alice again, plus @Bob."
        
        assert result == expected
    
    def test_round_trip_conversion(self):
        """Test that standardization and replacement are inverse operations."""
        original_text = "[2024-01-15 10:30:00] Alice: Hello Bob!"
        user_mapping = {"Alice": "123456", "Bob": "789012"}
        
        # Standardize first
        standardized = standardize_user_references(original_text, user_mapping)
        # Then replace back
        restored = replace_user_ids_with_names(standardized, user_mapping)
        
        expected_restored = "[2024-01-15 10:30:00] @Alice: Hello @Bob!"
        assert restored == expected_restored
    
    def test_formatting_with_special_characters(self):
        """Test formatting with special characters in usernames."""
        chat_history = "[2024-01-15 10:30:00] User_123: Hello!"
        user_mapping = {"User_123": "abc456"}
        
        result = standardize_user_references(chat_history, user_mapping)
        expected = "[2024-01-15 10:30:00] <@abc456>: Hello!"
        
        assert result == expected
    
    def test_empty_inputs(self):
        """Test functions with empty inputs."""
        assert standardize_user_references("", {}) == ""
        assert replace_user_ids_with_names("", {}) == ""
        assert standardize_user_references("", {"Alice": "123"}) == ""
        assert replace_user_ids_with_names("", {"Alice": "123"}) == ""
