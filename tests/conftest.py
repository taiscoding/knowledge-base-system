#!/usr/bin/env python3
"""
Shared test fixtures for all components.
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from knowledge_base.privacy.smart_anonymization import PrivacyEngine
from knowledge_base.privacy.session_manager import PrivacySessionManager
from knowledge_base.privacy.token_intelligence_bridge import TokenIntelligenceBridge
from knowledge_base.manager import KnowledgeBaseManager


@pytest.fixture
def sample_base_path():
    """Create a temporary directory with basic structure for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up directory structure
        data_dir = Path(temp_dir) / "data"
        (data_dir / "notes").mkdir(parents=True, exist_ok=True)
        (data_dir / "todos").mkdir(parents=True, exist_ok=True)
        (data_dir / "calendar").mkdir(parents=True, exist_ok=True)
        (data_dir / "journal").mkdir(parents=True, exist_ok=True)
        (data_dir / "projects").mkdir(parents=True, exist_ok=True)
        (data_dir / "references").mkdir(parents=True, exist_ok=True)
        
        # Create mock config
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_dir / "conventions.yaml", "w") as f:
            f.write("""
auto_categorization:
  work:
    - office
    - meeting
    - client
  learning:
    - study
    - learn
    - research
priority_detection:
  urgent_keywords:
    - urgent
    - asap
    - immediately
    - critical
            """)
        
        yield temp_dir


@pytest.fixture
def mock_config():
    """Fixture providing mock configuration."""
    return {
        "privacy": {"privacy_level": "balanced"},
        "organization": {
            "auto_categorization": {
                "work": ["office", "meeting", "client"],
                "learning": ["study", "learn", "research"]
            },
            "priority_detection": {
                "urgent_keywords": ["urgent", "asap", "immediately", "critical"]
            }
        }
    }


@pytest.fixture
def sample_content():
    """Fixture providing sample content for testing."""
    return """
    Need to finish the quarterly report by tomorrow. It's urgent!
    
    Meeting with Sarah next Monday at 2pm to discuss Project Phoenix.
    
    Remember to call John at 555-123-4567 about the budget approval.
    
    #work #finance #report
    """


@pytest.fixture
def kb_manager(sample_base_path):
    """Fixture providing a KnowledgeBaseManager instance with temp directory."""
    manager = KnowledgeBaseManager(base_path=sample_base_path, privacy_storage_dir=sample_base_path)
    
    # Mock the config loading
    manager.config = {
        "privacy": {"privacy_level": "balanced"},
        "organization": {
            "auto_categorization": {
                "work": ["office", "meeting", "client"],
                "learning": ["study", "learn", "research"]
            },
            "priority_detection": {
                "urgent_keywords": ["urgent", "asap", "immediately", "critical"]
            }
        }
    }
    manager.conventions = {}
    
    return manager 