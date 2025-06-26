#!/usr/bin/env python3
"""
Tests for the PrivacySessionManager class.
"""

import os
import pytest
import json
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from knowledge_base.privacy.session_manager import PrivacySessionManager


class TestPrivacySessionManager:
    """Test suite for the PrivacySessionManager class."""

    def test_initialization(self, session_manager):
        """Test that the PrivacySessionManager initializes correctly."""
        assert isinstance(session_manager, PrivacySessionManager)
        assert hasattr(session_manager, 'storage_dir')
        assert hasattr(session_manager, 'sessions')
        assert isinstance(session_manager.sessions, dict)

    def test_create_session(self, session_manager):
        """Test session creation with different privacy levels."""
        # Test default privacy level
        session_id = session_manager.create_session()
        assert session_id in session_manager.sessions
        assert session_manager.sessions[session_id]["privacy_level"] == "balanced"
        
        # Test strict privacy level
        strict_session_id = session_manager.create_session("strict")
        assert strict_session_id in session_manager.sessions
        assert session_manager.sessions[strict_session_id]["privacy_level"] == "strict"
        
        # Test with metadata
        metadata = {"user": "test_user", "source": "unit_test"}
        meta_session_id = session_manager.create_session(metadata=metadata)
        assert meta_session_id in session_manager.sessions
        assert session_manager.sessions[meta_session_id]["metadata"] == metadata
        
        # Verify session IDs are unique
        assert session_id != strict_session_id
        assert session_id != meta_session_id
        assert strict_session_id != meta_session_id
        
        # Verify session file was created
        session_file = Path(session_manager.storage_dir) / f"session_{session_id}.json"
        assert session_file.exists()

    def test_get_session(self, session_manager):
        """Test retrieving a session by ID."""
        session_id = session_manager.create_session()
        
        # Get valid session
        session = session_manager.get_session(session_id)
        assert session is not None
        assert session["privacy_level"] == "balanced"
        
        # Get invalid session
        invalid_session = session_manager.get_session("invalid_session_id")
        assert invalid_session is None
        
        # Verify last_used timestamp was updated
        first_used = session_manager.sessions[session_id]["last_used"]
        
        # Wait a tiny bit to ensure timestamp would be different
        import time
        time.sleep(0.01)
        
        session_manager.get_session(session_id)
        second_used = session_manager.sessions[session_id]["last_used"]
        
        assert first_used != second_used

    def test_update_session(self, session_manager):
        """Test updating a session with new data."""
        session_id = session_manager.create_session()
        
        # Update session with new privacy level
        updates = {"privacy_level": "strict"}
        updated = session_manager.update_session(session_id, updates)
        
        assert updated is not None
        assert updated["privacy_level"] == "strict"
        
        # Update with dictionary merge
        token_mappings = {"PERSON_001": "John Smith"}
        updates = {"token_mappings": token_mappings}
        updated = session_manager.update_session(session_id, updates)
        
        assert "token_mappings" in updated
        assert updated["token_mappings"] == token_mappings
        
        # Update with additional dictionary entries
        more_tokens = {"PERSON_002": "Jane Doe"}
        updates = {"token_mappings": more_tokens}
        updated = session_manager.update_session(session_id, updates)
        
        # Should merge dictionaries not replace
        assert "PERSON_001" in updated["token_mappings"]
        assert "PERSON_002" in updated["token_mappings"]
        
        # Update with list append
        context = ["meeting", "project"]
        updates = {"preserved_context": context}
        updated = session_manager.update_session(session_id, updates)
        
        assert updated["preserved_context"] == context
        
        # Update with additional list items
        more_context = ["email", "report"]
        updates = {"preserved_context": more_context}
        updated = session_manager.update_session(session_id, updates)
        
        # Should append lists
        for item in context + more_context:
            assert item in updated["preserved_context"]
        
        # Update non-existent session
        result = session_manager.update_session("invalid_session_id", updates)
        assert result is None

    def test_add_context(self, session_manager):
        """Test adding context items to a session."""
        session_id = session_manager.create_session()
        
        # Add context items
        context_items = ["meeting", "project", "email"]
        result = session_manager.add_context(session_id, context_items)
        
        assert result is True
        assert "preserved_context" in session_manager.sessions[session_id]
        for item in context_items:
            assert item in session_manager.sessions[session_id]["preserved_context"]
        
        # Add duplicate context items (should not duplicate)
        result = session_manager.add_context(session_id, ["meeting", "report"])
        assert result is True
        
        # Check uniqueness
        context_count = session_manager.sessions[session_id]["preserved_context"].count("meeting")
        assert context_count == 1
        
        # Add to non-existent session
        result = session_manager.add_context("invalid_session_id", ["test"])
        assert result is False

    def test_delete_session(self, session_manager):
        """Test deleting a session."""
        session_id = session_manager.create_session()
        
        # Verify file exists before deletion
        session_file = Path(session_manager.storage_dir) / f"session_{session_id}.json"
        assert session_file.exists()
        
        # Delete session
        result = session_manager.delete_session(session_id)
        
        assert result is True
        assert session_id not in session_manager.sessions
        assert not session_file.exists()
        
        # Delete non-existent session
        result = session_manager.delete_session("invalid_session_id")
        assert result is False

    def test_save_session(self, session_manager):
        """Test saving a session to storage."""
        session_id = session_manager.create_session()
        
        # Modify session and save
        session_manager.sessions[session_id]["test_field"] = "test_value"
        session_manager._save_session(session_id)
        
        # Load the session file directly to verify
        session_file = Path(session_manager.storage_dir) / f"session_{session_id}.json"
        with open(session_file, 'r') as f:
            saved_data = json.load(f)
        
        assert "test_field" in saved_data
        assert saved_data["test_field"] == "test_value"
        
        # Test with non-existent session
        session_manager._save_session("invalid_session_id")  # Should not raise exception

    def test_load_sessions(self, tmp_path):
        """Test loading saved sessions from storage."""
        # Create a temporary session file
        storage_dir = tmp_path / "test_sessions"
        storage_dir.mkdir()
        
        session_data = {
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "privacy_level": "balanced",
            "token_mappings": {"PERSON_001": "John Smith"},
            "entity_relationships": {},
            "preserved_context": ["meeting"],
            "metadata": {"source": "test"}
        }
        
        # Write a test session file
        test_session_id = "test_session_123"
        session_file = storage_dir / f"session_{test_session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        # Create a session manager with this directory
        manager = PrivacySessionManager(storage_dir=str(storage_dir))
        
        # Verify session was loaded
        assert test_session_id in manager.sessions
        assert manager.sessions[test_session_id]["privacy_level"] == "balanced"
        assert manager.sessions[test_session_id]["token_mappings"] == {"PERSON_001": "John Smith"}
        
        # Test with invalid session file
        invalid_file = storage_dir / "session_invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("This is not valid JSON")
        
        # Should not raise exception for invalid files
        manager = PrivacySessionManager(storage_dir=str(storage_dir))
        assert test_session_id in manager.sessions  # Good session still loaded

    def test_get_active_sessions(self, session_manager):
        """Test retrieving active sessions based on age."""
        # Create sessions with different timestamps
        current_session_id = session_manager.create_session()
        
        # Create an "old" session by manipulating its timestamp
        old_session_id = session_manager.create_session()
        old_timestamp = (datetime.now() - timedelta(hours=48)).isoformat()
        session_manager.sessions[old_session_id]["last_used"] = old_timestamp
        session_manager._save_session(old_session_id)
        
        # Test with default 24-hour window
        active_sessions = session_manager.get_active_sessions()
        assert current_session_id in active_sessions
        assert old_session_id not in active_sessions
        
        # Test with larger window
        active_sessions = session_manager.get_active_sessions(max_age_hours=72)
        assert current_session_id in active_sessions
        assert old_session_id in active_sessions
        
        # Test with invalid timestamp
        session_manager.sessions[current_session_id]["last_used"] = "not_a_timestamp"
        active_sessions = session_manager.get_active_sessions()
        assert current_session_id not in active_sessions  # Should be skipped due to invalid timestamp 