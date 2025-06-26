#!/usr/bin/env python3
"""
Tests for the PrivacyEngine class.
"""

import pytest
import re
from knowledge_base.privacy.smart_anonymization import PrivacyEngine, DeidentificationResult


class TestPrivacyEngine:
    """Test suite for the PrivacyEngine class."""

    def test_initialization(self, privacy_engine):
        """Test that the PrivacyEngine initializes correctly."""
        assert isinstance(privacy_engine, PrivacyEngine)
        assert isinstance(privacy_engine.token_intelligence_bridge, object)
        assert hasattr(privacy_engine, 'name_patterns')
        assert hasattr(privacy_engine, 'phone_patterns')
        assert hasattr(privacy_engine, 'email_patterns')
        assert hasattr(privacy_engine, 'location_patterns')
        assert hasattr(privacy_engine, 'project_patterns')

    def test_create_session(self, privacy_engine):
        """Test session creation with different privacy levels."""
        # Test default privacy level
        session_id = privacy_engine.create_session()
        assert session_id in privacy_engine.sessions
        assert privacy_engine.sessions[session_id]["privacy_level"] == "balanced"
        
        # Test strict privacy level
        strict_session_id = privacy_engine.create_session("strict")
        assert strict_session_id in privacy_engine.sessions
        assert privacy_engine.sessions[strict_session_id]["privacy_level"] == "strict"
        
        # Test minimal privacy level
        minimal_session_id = privacy_engine.create_session("minimal")
        assert minimal_session_id in privacy_engine.sessions
        assert privacy_engine.sessions[minimal_session_id]["privacy_level"] == "minimal"
        
        # Verify session IDs are unique
        assert session_id != strict_session_id
        assert session_id != minimal_session_id
        assert strict_session_id != minimal_session_id

    def test_deidentify_with_names(self, privacy_engine, sample_text):
        """Test that names are correctly identified and tokenized."""
        session_id = privacy_engine.create_session()
        result = privacy_engine.deidentify(sample_text, session_id)
        
        assert isinstance(result, DeidentificationResult)
        
        # Check for name tokenization
        assert "John Smith" not in result.text
        assert "Sarah Johnson" not in result.text
        
        # Check that tokens were generated for names
        assert any(original == "John Smith" for original in result.token_map.values())
        assert any(original == "Sarah Johnson" for original in result.token_map.values())

    def test_deidentify_with_phone_numbers(self, privacy_engine, sample_text):
        """Test that phone numbers are correctly identified and tokenized."""
        session_id = privacy_engine.create_session()
        result = privacy_engine.deidentify(sample_text, session_id)
        
        # Check that phone number is tokenized
        assert "555-123-4567" not in result.text
        
        # Check that token was generated for phone number
        assert any(original == "555-123-4567" for original in result.token_map.values())
        
        # Check token format
        phone_tokens = [token for token, value in result.token_map.items() 
                        if value == "555-123-4567" and token.startswith("PHONE")]
        assert len(phone_tokens) == 1

    def test_deidentify_with_emails(self, privacy_engine, sample_text):
        """Test that emails are correctly identified and tokenized."""
        session_id = privacy_engine.create_session()
        result = privacy_engine.deidentify(sample_text, session_id)
        
        # Check that email is tokenized
        assert "john.smith@example.com" not in result.text
        
        # Check that token was generated for email
        assert any(original == "john.smith@example.com" for original in result.token_map.values())
        
        # Check token format
        email_tokens = [token for token, value in result.token_map.items() 
                       if value == "john.smith@example.com" and token.startswith("EMAIL")]
        assert len(email_tokens) == 1

    def test_deidentify_with_locations(self, privacy_engine, sample_text):
        """Test that locations are correctly identified and tokenized."""
        session_id = privacy_engine.create_session("balanced")
        result = privacy_engine.deidentify(sample_text, session_id)
        
        # Check that location is tokenized (in balanced or strict mode)
        assert "123 Main Street" not in result.text
        
        # Check that token was generated for location
        assert any(original == "123 Main Street" for original in result.token_map.values())
        
        # Check token format
        location_tokens = [token for token, value in result.token_map.items() 
                          if value == "123 Main Street" and token.startswith("LOCATION")]
        assert len(location_tokens) == 1

    def test_deidentify_with_projects(self, privacy_engine, sample_text):
        """Test that project names are correctly identified and tokenized."""
        session_id = privacy_engine.create_session()
        result = privacy_engine.deidentify(sample_text, session_id)
        
        # Check that project name is tokenized
        assert "Project Phoenix" not in result.text
        
        # Check that token was generated for project
        assert any(original == "Project Phoenix" for original in result.token_map.values())
        
        # Check token format
        project_tokens = [token for token, value in result.token_map.items() 
                         if value == "Project Phoenix" and token.startswith("PROJECT")]
        assert len(project_tokens) == 1

    def test_deidentify_token_consistency(self, privacy_engine):
        """Test that tokens remain consistent across multiple calls."""
        session_id = privacy_engine.create_session()
        
        # First deidentification
        text1 = "John Smith works on Project Phoenix with Sarah Johnson."
        result1 = privacy_engine.deidentify(text1, session_id)
        
        # Second deidentification with some of the same entities
        text2 = "John Smith sent an email about Project Phoenix progress."
        result2 = privacy_engine.deidentify(text2, session_id)
        
        # Find tokens for John Smith in both results
        john_token1 = None
        john_token2 = None
        
        for token, value in result1.token_map.items():
            if value == "John Smith":
                john_token1 = token
        
        for token, value in result2.token_map.items():
            if value == "John Smith":
                john_token2 = token
        
        # Tokens for the same entity should be consistent
        assert john_token1 is not None
        assert john_token2 is not None
        assert john_token1 == john_token2
        
        # Same for Project Phoenix
        project_token1 = None
        project_token2 = None
        
        for token, value in result1.token_map.items():
            if value == "Project Phoenix":
                project_token1 = token
        
        for token, value in result2.token_map.items():
            if value == "Project Phoenix":
                project_token2 = token
        
        assert project_token1 is not None
        assert project_token2 is not None
        assert project_token1 == project_token2

    def test_deidentify_privacy_levels(self, privacy_engine):
        """Test different privacy levels affect what gets tokenized."""
        text = "John Smith lives at 123 Main Street in Anytown."
        
        # Test with strict privacy
        strict_session = privacy_engine.create_session("strict")
        strict_result = privacy_engine.deidentify(text, strict_session)
        
        # Test with minimal privacy
        minimal_session = privacy_engine.create_session("minimal")
        minimal_result = privacy_engine.deidentify(text, minimal_session)
        
        # Strict should tokenize locations, minimal might not
        has_location_token_strict = any(token.startswith("LOCATION") 
                                        for token in strict_result.token_map)
        
        # Names should be tokenized in both levels
        assert "John Smith" not in strict_result.text
        assert "John Smith" not in minimal_result.text
        
        # Check if strict session tokenized location
        assert has_location_token_strict
        assert "123 Main Street" not in strict_result.text

    def test_reconstruct(self, privacy_engine, sample_text):
        """Test reconstruction of original text from tokenized version."""
        session_id = privacy_engine.create_session()
        result = privacy_engine.deidentify(sample_text, session_id)
        
        # Reconstruct the original text
        reconstructed = privacy_engine.reconstruct(result.text, session_id)
        
        # Clean up whitespace to make comparison easier
        original_cleaned = re.sub(r'\s+', ' ', sample_text).strip()
        reconstructed_cleaned = re.sub(r'\s+', ' ', reconstructed).strip()
        
        assert original_cleaned == reconstructed_cleaned
        
        # Verify all sensitive information is present in reconstructed text
        assert "John Smith" in reconstructed
        assert "555-123-4567" in reconstructed
        assert "john.smith@example.com" in reconstructed
        assert "123 Main Street" in reconstructed
        assert "Project Phoenix" in reconstructed
        assert "Sarah Johnson" in reconstructed

    def test_reconstruct_with_invalid_session(self, privacy_engine):
        """Test reconstruct behavior with an invalid session ID."""
        text = "This contains a token [PERSON_001]."
        result = privacy_engine.reconstruct(text, "invalid_session_id")
        
        # Should return original text when session is invalid
        assert result == text

    def test_enhance_for_ai(self, privacy_engine, mocker):
        """Test enhancement of deidentified text for AI processing."""
        # Create a mock for token_intelligence_bridge.enhance_privacy_text
        mock_enhance = mocker.patch.object(
            privacy_engine.token_intelligence_bridge, 
            'enhance_privacy_text', 
            return_value="Enhanced text with context hints"
        )
        
        session_id = privacy_engine.create_session()
        privacy_engine.sessions[session_id]["preserved_context"] = ["meeting", "project"]
        result = privacy_engine.enhance_for_ai("Deidentified text with [PERSON_001]", session_id)
        
        # Check that enhancement was called with correct parameters
        mock_enhance.assert_called_once()
        assert result == "Enhanced text with context hints"

    def test_entity_relationships(self, privacy_engine):
        """Test that entity relationships are correctly detected and tracked."""
        session_id = privacy_engine.create_session()
        
        # Text with related entities
        text = "John Smith is working on Project Phoenix. His email is john.smith@example.com."
        result = privacy_engine.deidentify(text, session_id)
        
        # Get tokens for entities
        john_token = None
        project_token = None
        email_token = None
        
        for token, value in result.token_map.items():
            if value == "John Smith":
                john_token = token
            elif value == "Project Phoenix":
                project_token = token
            elif value == "john.smith@example.com":
                email_token = token
        
        # Check that relationships were created
        relationships = result.entity_relationships
        
        # John should be linked to the project and email
        assert john_token in relationships
        assert project_token in relationships[john_token].get("linked_entities", [])
        assert email_token in relationships[john_token].get("linked_entities", [])

        # Project should be linked to John
        assert project_token in relationships
        assert john_token in relationships[project_token].get("linked_entities", [])

    def test_process_patterns(self, privacy_engine):
        """Test internal _process_patterns method."""
        text = "John Smith and Jane Doe"
        patterns = [r'\b(?:[A-Z][a-z]+\s+[A-Z][a-z]+)\b']  # Simple name pattern
        existing_mappings = {}
        
        processed_text, new_mappings = privacy_engine._process_patterns(
            text, patterns, "PERSON", existing_mappings)
        
        # Should tokenize both names
        assert "[PERSON_001]" in processed_text
        assert "[PERSON_002]" in processed_text
        assert "John Smith" not in processed_text
        assert "Jane Doe" not in processed_text
        
        # Check mappings
        assert len(new_mappings) == 2
        assert "PERSON_001" in new_mappings
        assert "PERSON_002" in new_mappings
        
        # Check existing mappings preservation
        existing = {"PERSON_003": "Alice Johnson"}
        processed_text2, new_mappings2 = privacy_engine._process_patterns(
            text, patterns, "PERSON", existing)
        
        # Should use new token numbers
        assert "PERSON_003" not in new_mappings2  # Not overwriting existing
        assert "PERSON_004" in new_mappings2  # Continuing from last token number 