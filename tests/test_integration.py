#!/usr/bin/env python3
"""
Integration tests between KnowledgeBaseManager and privacy components.
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from knowledge_base.manager import KnowledgeBaseManager


class TestKnowledgeBaseManagerPrivacyIntegration:
    """Test KnowledgeBaseManager integration with privacy components."""
    
    @pytest.fixture
    def kb_manager_with_privacy(self):
        """Create a KnowledgeBaseManager with privacy components enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up directory structure
            data_dir = Path(temp_dir) / "data"
            (data_dir / "notes").mkdir(parents=True, exist_ok=True)
            (data_dir / "todos").mkdir(parents=True, exist_ok=True)
            (data_dir / "calendar").mkdir(parents=True, exist_ok=True)
            (data_dir / "journal").mkdir(parents=True, exist_ok=True)
            
            # Create a manager with privacy enabled
            manager = KnowledgeBaseManager(
                base_path=temp_dir,
                privacy_enabled=True,
                privacy_level="balanced",
                privacy_storage_dir=temp_dir
            )
            
            # Make some data files to test with
            note_content = {
                "id": "test-note",
                "title": "Test Note with Sensitive Information",
                "content": "Meeting with John Smith about Project Phoenix. His phone is 555-123-4567.",
                "created": "2023-01-15T10:30:00Z",
                "updated": "2023-01-15T10:35:00Z",
                "type": "note",
                "tags": ["meeting", "project"]
            }
            
            note_path = data_dir / "notes" / "note-20230115-103000.md"
            with open(note_path, 'w') as f:
                f.write(f"# {note_content['title']}\n\n{note_content['content']}")
            
            yield manager, temp_dir, note_content
    
    def test_privacy_session_creation(self, kb_manager_with_privacy):
        """Test that privacy session is created when privacy is enabled."""
        manager, _, _ = kb_manager_with_privacy
        
        # Verify privacy components are initialized
        assert manager.privacy_enabled is True
        assert manager.privacy_engine is not None
        assert manager.privacy_session_manager is not None
        
        # Manager should already have a session ID
        assert manager.privacy_session_id is not None
        assert manager.privacy_session_id in manager.privacy_engine.sessions
    
    def test_content_processing_with_privacy(self, kb_manager_with_privacy):
        """Test that content is processed with privacy protection."""
        manager, temp_dir, note_content = kb_manager_with_privacy
        
        # Process text that contains sensitive information
        text = "Meeting notes with John Smith about Project Phoenix. Call him at 555-123-4567."
        processed_text = manager.process_content_with_privacy(text)
        
        # Check that sensitive information is tokenized
        assert "John Smith" not in processed_text
        assert "Project Phoenix" not in processed_text
        assert "555-123-4567" not in processed_text
        
        # Tokens should be present instead
        assert "[PERSON_" in processed_text
        assert "[PROJECT_" in processed_text
        assert "[PHONE_" in processed_text
    
    def test_content_retrieval_with_privacy(self, kb_manager_with_privacy):
        """Test that content is retrieved with privacy reconstruction."""
        manager, temp_dir, note_content = kb_manager_with_privacy
        
        # Process text with sensitive information
        text = "Meeting with John Smith about Project Phoenix"
        processed_text = manager.process_content_with_privacy(text)
        
        # Store processed text
        test_path = Path(temp_dir) / "test_file.txt"
        with open(test_path, 'w') as f:
            f.write(processed_text)
        
        # Retrieve and reconstruct content
        retrieved_text = manager.retrieve_content_with_privacy(test_path)
        
        # Original sensitive information should be restored
        assert "John Smith" in retrieved_text
        assert "Project Phoenix" in retrieved_text
    
    def test_save_content_with_privacy(self, kb_manager_with_privacy):
        """Test saving content with privacy protection."""
        manager, temp_dir, _ = kb_manager_with_privacy
        
        # Content to save
        content = {
            "title": "Sensitive Note",
            "content": "Call John Smith at 555-123-4567 about Project Phoenix.",
            "type": "note",
            "tags": ["meeting", "confidential"]
        }
        
        # Save content
        filepath = manager.save_content(content, "note")
        
        # Read file to check content was saved with privacy protection
        with open(filepath, 'r') as f:
            saved_content = f.read()
        
        # Sensitive information should be tokenized
        assert "John Smith" not in saved_content
        assert "555-123-4567" not in saved_content
        assert "Project Phoenix" not in saved_content
        
        # Read back with privacy reconstruction
        retrieved_content = manager.get_content("note", filepath)
        
        # Sensitive information should be reconstructed
        assert "John Smith" in retrieved_content["content"]
        assert "555-123-4567" in retrieved_content["content"]
        assert "Project Phoenix" in retrieved_content["content"]
    
    def test_search_with_privacy(self, kb_manager_with_privacy):
        """Test searching with privacy awareness."""
        manager, temp_dir, note_content = kb_manager_with_privacy
        
        # Create some test content with sensitive information
        content1 = {
            "title": "Project Update",
            "content": "John Smith presented the Project Phoenix update.",
            "type": "note",
            "tags": ["meeting"]
        }
        
        content2 = {
            "title": "Contact List",
            "content": "Sarah Johnson - 555-987-6543\nJohn Smith - 555-123-4567",
            "type": "note",
            "tags": ["contacts"]
        }
        
        # Save content with privacy protection
        path1 = manager.save_content(content1, "note")
        path2 = manager.save_content(content2, "note")
        
        # Search for content with sensitive terms
        # The search should match against the tokenized values
        results = manager.search("John Smith")
        
        # Should find both notes (after reconstruction)
        assert len(results) == 2
        
        # Check results have original content reconstructed
        for result in results:
            assert "John Smith" in result["content"]
    
    def test_export_with_privacy(self, kb_manager_with_privacy):
        """Test exporting content with privacy protection."""
        manager, temp_dir, _ = kb_manager_with_privacy
        
        # Create content with sensitive information
        content = {
            "title": "Confidential Report",
            "content": "John Smith's review of Project Phoenix. Contact: 555-123-4567",
            "type": "note",
            "tags": ["confidential"]
        }
        
        # Save content
        manager.save_content(content, "note")
        
        # Export content
        export_path = Path(temp_dir) / "export.json"
        manager.export_data(str(export_path))
        
        # Read exported file to verify privacy was maintained
        import json
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        # Sensitive information should be tokenized in export
        exported_content = exported_data["content"][0]["content"]
        assert "John Smith" not in exported_content
        assert "Project Phoenix" not in exported_content
        assert "555-123-4567" not in exported_content
    
    def test_privacy_session_persistence(self, kb_manager_with_privacy):
        """Test that privacy session information persists between manager instances."""
        manager, temp_dir, _ = kb_manager_with_privacy
        
        # Process text to populate session with tokens
        text = "Meeting with John Smith and Sarah Johnson about Project Phoenix."
        processed = manager.process_content_with_privacy(text)
        
        # Store original session ID
        original_session_id = manager.privacy_session_id
        
        # Create a new manager instance with the same settings
        new_manager = KnowledgeBaseManager(
            base_path=temp_dir,
            privacy_enabled=True,
            privacy_level="balanced",
            privacy_storage_dir=temp_dir
        )
        
        # The new manager should load the existing session
        assert new_manager.privacy_session_id is not None
        assert original_session_id == new_manager.privacy_session_id
        
        # Process the same text - should use consistent tokens
        new_processed = new_manager.process_content_with_privacy(text)
        
        # Token assignments should be the same across instances
        assert processed == new_processed 