#!/usr/bin/env python3
"""
Shared test fixtures for privacy component tests.
"""

import os
import tempfile
import pytest
from typing import Dict, Any

from knowledge_base.privacy.smart_anonymization import PrivacyEngine
from knowledge_base.privacy.session_manager import PrivacySessionManager
from knowledge_base.privacy.token_intelligence_bridge import TokenIntelligenceBridge


@pytest.fixture
def privacy_engine():
    """Fixture providing a PrivacyEngine instance for testing."""
    config = {
        "privacy_level": "balanced",
        "token_prefix": "[",
        "token_suffix": "]"
    }
    engine = PrivacyEngine(config)
    return engine


@pytest.fixture
def session_manager():
    """Fixture providing a PrivacySessionManager instance with temp directory."""
    # Create a temporary directory for session storage
    with tempfile.TemporaryDirectory() as temp_dir:
        session_mgr = PrivacySessionManager(storage_dir=temp_dir)
        yield session_mgr
        # Cleanup happens automatically when the tempdir context exits


@pytest.fixture
def token_intelligence_bridge():
    """Fixture providing a TokenIntelligenceBridge instance."""
    return TokenIntelligenceBridge()


@pytest.fixture
def sample_text():
    """Fixture providing sample text with sensitive information."""
    return """
    Hi John Smith,
    
    I wanted to follow up on our meeting about Project Phoenix.
    Please call me at 555-123-4567 or email john.smith@example.com
    when you have time. We can meet at 123 Main Street.
    
    Best regards,
    Sarah Johnson
    """


@pytest.fixture
def mock_entity_relationships():
    """Fixture providing mock entity relationships."""
    return {
        "PERSON_001": {
            "type": "person",
            "linked_entities": ["PROJECT_001", "EMAIL_001", "PHONE_001"],
            "relationships": {
                "PROJECT_001": "works_on",
                "EMAIL_001": "has_email",
                "PHONE_001": "has_phone_number"
            }
        },
        "PROJECT_001": {
            "type": "project", 
            "linked_entities": ["PERSON_001"],
            "relationships": {
                "PERSON_001": "has_member"
            }
        }
    } 