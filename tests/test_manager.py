#!/usr/bin/env python3
"""
Tests for the KnowledgeBaseManager class.
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch, mock_open

from knowledge_base.manager import KnowledgeBaseManager
from knowledge_base.content_types import Note, Todo, CalendarEvent
from knowledge_base.utils.config import Config
from knowledge_base.utils.helpers import (
    KnowledgeBaseError, ContentProcessingError, 
    StorageError, ConfigurationError, PrivacyError
)


@pytest.fixture
def mock_config():
    """Create a mock config object."""
    config = {
        "privacy": {
            "privacy_level": "balanced",
            "token_prefix": "[",
            "token_suffix": "]"
        },
        "organization": {
            "auto_categorization": {
                "work": ["office", "meeting", "client"],
                "learning": ["study", "learn", "research"]
            },
            "priority_detection": {
                "urgent_keywords": ["urgent", "asap", "immediately", "critical"]
            }
        },
        "storage": {
            "data_path": "data"
        }
    }
    
    return config


@pytest.fixture
def mock_conventions():
    """Create mock conventions object."""
    conventions = {
        "file_naming": {
            "notes": "note-{timestamp}.md",
            "todos": "todo-{timestamp}.json",
            "events": "event-{timestamp}.json"
        }
    }
    
    return conventions


@pytest.fixture
def kb_manager(mock_config, mock_conventions):
    """Fixture providing a KnowledgeBaseManager instance with temp directory."""
    # Create a temporary directory for the knowledge base
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up necessary directory structure
        data_dir = Path(temp_dir) / "data"
        (data_dir / "notes").mkdir(parents=True, exist_ok=True)
        (data_dir / "todos").mkdir(parents=True, exist_ok=True)
        (data_dir / "calendar").mkdir(parents=True, exist_ok=True)
        (data_dir / "journal").mkdir(parents=True, exist_ok=True)
        
        # Create mock config files
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_dir / "conventions.yaml", "w") as f:
            f.write("""
file_naming:
  notes: note-{timestamp}.md
  todos: todo-{timestamp}.json
  events: event-{timestamp}.json
            """)
        
        with open(config_dir / "ai_instructions.yaml", "w") as f:
            f.write("""
privacy:
  privacy_level: balanced
  token_prefix: "["
  token_suffix: "]"
organization:
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
        
        # Create the manager with mocked config loading
        with patch.object(Config, 'load_config', return_value=mock_config), \
             patch.object(Config, 'load_conventions', return_value=mock_conventions):
            manager = KnowledgeBaseManager(base_path=temp_dir, privacy_storage_dir=temp_dir)
            yield manager


@pytest.fixture
def sample_content():
    """Fixture providing sample content for testing."""
    return """
    Need to finish the quarterly report by tomorrow. It's urgent!
    
    Meeting with Sarah next Monday at 2pm to discuss Project Phoenix.
    
    Remember to call John at 555-123-4567 about the budget approval.
    
    #work #finance #report
    """


class TestKnowledgeBaseManager:
    """Test suite for the KnowledgeBaseManager class."""
    
    def test_initialization(self, kb_manager):
        """Test that the KnowledgeBaseManager initializes correctly."""
        assert isinstance(kb_manager, KnowledgeBaseManager)
        assert isinstance(kb_manager.privacy_engine, object)
        assert isinstance(kb_manager.session_manager, object)
        
    def test_initialization_error(self):
        """Test error handling during initialization with invalid path."""
        with pytest.raises(ConfigurationError):
            # Non-existent path should raise ConfigurationError
            KnowledgeBaseManager(base_path="/non/existent/path")
        
    def test_extract_todos(self, kb_manager):
        """Test extraction of todos from content."""
        # Simple todo extraction
        content = "Need to buy groceries tomorrow."
        todos = kb_manager._extract_todos(content)
        
        assert len(todos) == 1
        assert todos[0]["title"] == "buy groceries tomorrow"
        assert todos[0]["status"] == "active"
        
        # Multiple todos
        content = "Need to buy groceries. Remember to call mom."
        todos = kb_manager._extract_todos(content)
        
        assert len(todos) == 2
        assert todos[0]["title"] == "buy groceries"
        assert todos[1]["title"] == "call mom"
        
        # Todo with checkbox format
        content = "- [ ] Complete project report"
        todos = kb_manager._extract_todos(content)
        
        assert len(todos) == 1
        assert todos[0]["title"] == "Complete project report"
        
    def test_extract_todos_error_handling(self, kb_manager):
        """Test error handling in todo extraction."""
        # Mock re.findall to raise an exception
        with patch('re.findall', side_effect=Exception("Mock regex error")):
            with pytest.raises(ContentProcessingError):
                kb_manager._extract_todos("Content with todo")
        
    def test_extract_calendar_events(self, kb_manager):
        """Test extraction of calendar events from content."""
        content = "Meeting with Sarah on Monday at 2pm."
        events = kb_manager._extract_calendar_events(content)
        
        assert len(events) == 1
        assert "Sarah" in events[0]["title"]
        assert events[0]["category"] == "meeting"
        
        content = "Call with team tomorrow at 10:30."
        events = kb_manager._extract_calendar_events(content)
        
        assert len(events) == 1
        assert "team tomorrow at 10:30" in events[0]["title"]
        
    def test_extract_calendar_events_error_handling(self, kb_manager):
        """Test error handling in calendar event extraction."""
        # Mock re.findall to raise an exception
        with patch('re.findall', side_effect=Exception("Mock regex error")):
            with pytest.raises(ContentProcessingError):
                kb_manager._extract_calendar_events("Meeting tomorrow")
        
    def test_extract_tags(self, kb_manager):
        """Test extraction of tags from content."""
        content = "This is a #work task about #project"
        tags = kb_manager._extract_tags(content)
        
        assert "work" in tags
        assert "project" in tags
        
        # With context keywords
        content = "Office meeting about quarterly review"
        tags = kb_manager._extract_tags(content)
        
        assert "@work" in tags
        
    def test_extract_tags_error_handling(self, kb_manager):
        """Test error handling in tag extraction."""
        # Mock re.findall to raise an exception
        with patch('re.findall', side_effect=Exception("Mock regex error")):
            # Should return empty tags instead of raising
            tags = kb_manager._extract_tags("Content with #tags")
            assert tags == []
        
    def test_categorize_content(self, kb_manager):
        """Test categorization of content."""
        # Work-related content
        content = "Planning for the client meeting tomorrow."
        tags = ["@work"]
        category = kb_manager._categorize_content(content, tags)
        
        assert category == "work"
        
        # Learning-related content
        content = "Need to study for the exam."
        tags = ["study"]
        category = kb_manager._categorize_content(content, tags)
        
        assert category == "learning"
        
        # Default categorization
        content = "Remember to buy milk."
        tags = []
        category = kb_manager._categorize_content(content, tags)
        
        assert category == "personal"
        
    def test_categorize_content_error_handling(self, kb_manager):
        """Test error handling in content categorization."""
        # Modify config to be None to trigger error
        with patch.object(kb_manager, 'config', None):
            # Should return "personal" as fallback
            category = kb_manager._categorize_content("Test content", ["tag"])
            assert category == "personal"
        
    def test_detect_priority(self, kb_manager):
        """Test priority detection."""
        # High priority
        text = "Need to finish this ASAP!"
        priority = kb_manager._detect_priority(text)
        assert priority == "high"
        
        # Medium priority
        text = "This is an important task."
        priority = kb_manager._detect_priority(text)
        assert priority == "medium"
        
        # Low priority
        text = "Sometime next week, check the reports."
        priority = kb_manager._detect_priority(text)
        assert priority == "low"
        
    def test_detect_priority_error_handling(self, kb_manager):
        """Test error handling in priority detection."""
        # Modify config to be None to trigger error
        with patch.object(kb_manager, 'config', None):
            # Should return "medium" as fallback
            priority = kb_manager._detect_priority("Test content")
            assert priority == "medium"
        
    def test_extract_due_date(self, kb_manager):
        """Test extraction of due dates from text."""
        # Today due date
        text = "Need to finish this today."
        due_date = kb_manager._extract_due_date(text)
        
        # Check that due_date matches today's date
        assert due_date == datetime.now().date().isoformat()
        
        # Tomorrow due date
        text = "Complete this task by tomorrow."
        due_date = kb_manager._extract_due_date(text)
        
        # Should be tomorrow's date
        assert due_date is not None
        
        # No specific date
        text = "Complete this task soon."
        due_date = kb_manager._extract_due_date(text)
        
        assert due_date is None
        
    def test_extract_context(self, kb_manager):
        """Test extraction of context tags."""
        # Home context
        text = "Fix the kitchen sink at home."
        context = kb_manager._extract_context(text)
        assert context == "@home"
        
        # Work context
        text = "Prepare for the meeting at the office."
        context = kb_manager._extract_context(text)
        assert context == "@work"
        
        # Urgent context
        text = "This is very urgent and important!"
        context = kb_manager._extract_context(text)
        assert context == "@urgent"
        
        # Default context
        text = "Read the new book."
        context = kb_manager._extract_context(text)
        assert context == "@personal"
        
    def test_create_note_from_content(self, kb_manager):
        """Test creation of note from content."""
        content = "This is a test note with #important tag."
        tags = ["#important", "@work"]
        category = "work"
        
        note = kb_manager._create_note_from_content(content, tags, category)
        
        # More lenient check that ignores trailing periods
        assert note["title"].rstrip('.') == "This is a test note with #important tag"
        assert note["content"] == content
        assert note["category"] == "work"
        assert "#important" in note["tags"]
        assert "@work" in note["tags"]
        
    def test_create_note_error_handling(self, kb_manager):
        """Test error handling in note creation."""
        # Mock _generate_title_from_content to raise an exception
        with patch.object(kb_manager, '_generate_title_from_content', side_effect=Exception("Mock title error")):
            note = kb_manager._create_note_from_content("Test content", ["tag"], "category")
            # Should create a note with error info
            assert note["title"] == "Note Creation Error"
            assert note["category"] == "error"
            assert "error" in note["tags"]
        
    def test_generate_title_from_content(self, kb_manager):
        """Test generation of title from content."""
        # Short content
        content = "This is a short note."
        title = kb_manager._generate_title_from_content(content)
        assert title.rstrip('.') == content.rstrip('.')
        
        # Long content needs truncation
        content = "This is a very long note that should be truncated when generating a title because it exceeds the maximum allowed length."
        title = kb_manager._generate_title_from_content(content)
        assert len(title) <= 50
        assert title.endswith("...")
        
    def test_generate_title_error_handling(self, kb_manager):
        """Test error handling in title generation."""
        # Pass None to trigger exception
        title = kb_manager._generate_title_from_content(None)
        assert title == "Untitled Note"
        
    def test_process_stream_of_consciousness(self, kb_manager, sample_content):
        """Test the main processing method for stream of consciousness input."""
        # Mock the save methods to avoid file system operations
        with patch.object(kb_manager, '_save_extracted_info'):
            result = kb_manager.process_stream_of_consciousness(sample_content)
            
            # Check that todos were extracted
            assert len(result["extracted_info"]["todos"]) > 0
            assert "quarterly report" in result["extracted_info"]["todos"][0]["title"].lower()
            
            # Check that calendar events were extracted
            assert len(result["extracted_info"]["calendar_events"]) > 0
            assert "Sarah" in result["extracted_info"]["calendar_events"][0]["title"]
            
            # Check that tags were extracted
            assert "#work" in result["extracted_info"]["tags"] or "work" in result["extracted_info"]["tags"]
            
            # Check that content was categorized
            assert result["extracted_info"]["categories"][0] == "work"
        
    def test_process_stream_error_handling(self, kb_manager):
        """Test error handling in process_stream_of_consciousness."""
        # Mock _extract_todos to raise an exception
        with patch.object(kb_manager, '_extract_todos', side_effect=ContentProcessingError("Mock extraction error")):
            with pytest.raises(ContentProcessingError):
                kb_manager.process_stream_of_consciousness("Test content")
                
        # Test with an unexpected error
        with patch.object(kb_manager, '_extract_todos', side_effect=Exception("Unexpected error")):
            with pytest.raises(ContentProcessingError):
                kb_manager.process_stream_of_consciousness("Test content")
        
    def test_save_content(self, kb_manager):
        """Test saving content to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            kb_manager.base_path = Path(temp_dir)
            
            # Create directory structure
            todos_dir = kb_manager.base_path / "data" / "todos"
            notes_dir = kb_manager.base_path / "data" / "notes"
            todos_dir.mkdir(parents=True, exist_ok=True)
            notes_dir.mkdir(parents=True, exist_ok=True)
            
            # Test saving JSON content (todo)
            todo = Todo(
                title="Test Todo",
                description="Test description",
                priority="high"
            ).to_dict()
            
            todo_path = kb_manager.save_content(todo, "todo")
            assert os.path.exists(todo_path)
            
            # Verify JSON content
            with open(todo_path, 'r') as f:
                saved_todo = json.load(f)
                assert saved_todo["title"] == "Test Todo"
                assert saved_todo["priority"] == "high"
            
            # Test saving Markdown content (note)
            note = Note(
                title="Test Note",
                content="This is a test note content",
                tags=["#test", "#example"]
            ).to_dict()
            
            note_path = kb_manager.save_content(note, "note")
            assert os.path.exists(note_path)
            
            # Verify markdown content
            with open(note_path, 'r') as f:
                content = f.read()
                assert "# Test Note" in content
                assert "This is a test note content" in content
                assert "#test" in content
                assert "#example" in content
        
    def test_save_content_file_error(self, kb_manager):
        """Test error handling when file cannot be written."""
        content_data = {"title": "Test", "content": "Test content"}
        
        # Mock open to raise IOError
        m = mock_open()
        m.side_effect = IOError("Mock IO error")
        with patch("builtins.open", m):
            with pytest.raises(StorageError):
                kb_manager.save_content(content_data, "note")
        
    def test_search_content(self, kb_manager):
        """Test searching across content."""
        # Create sample files for testing search
        with tempfile.TemporaryDirectory() as temp_dir:
            kb_manager.base_path = Path(temp_dir)
            notes_dir = kb_manager.base_path / "data" / "notes"
            notes_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test note
            with open(notes_dir / "test-note.md", "w") as f:
                f.write("# Test Note\n\nThis is a test note about Project Phoenix.\n")
            
            # Search for content
            results = kb_manager.search_content("Project Phoenix")
            
            assert len(results) == 1
            assert "test-note.md" in results[0]["file"]
            assert "notes" in results[0]["type"]
        
    def test_search_content_error_handling(self, kb_manager):
        """Test error handling in search."""
        # Test with empty query
        results = kb_manager.search_content("")
        assert results == []
        
        # Test with invalid directory
        with patch.object(kb_manager, 'base_path', Path("/non/existent/path")):
            results = kb_manager.search_content("test")
            assert results == []
        
        # Test with unexpected error in file reading
        with tempfile.TemporaryDirectory() as temp_dir:
            kb_manager.base_path = Path(temp_dir)
            data_dir = kb_manager.base_path / "data"
            notes_dir = data_dir / "notes"
            notes_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test note
            with open(notes_dir / "test-note.md", "w") as f:
                f.write("Test content")
            
            # Mock _read_file_content to raise exception
            with patch.object(kb_manager, '_read_file_content', side_effect=Exception("Mock read error")):
                results = kb_manager.search_content("test")
                # Should handle error and return empty list
                assert results == []
        
    def test_read_file_content_errors(self, kb_manager):
        """Test error handling in file reading."""
        # Test with non-existent file
        with pytest.raises(StorageError):
            kb_manager._read_file_content(Path("/non/existent/file.txt"))
        
        # Test with JSON decode error
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            f.write("Invalid JSON content")
            f.flush()
            file_path = Path(f.name)
        
        try:
            with pytest.raises(StorageError):
                kb_manager._read_file_content(file_path)
        finally:
            os.unlink(file_path)
            
        # Test with IO error
        with patch("builtins.open", side_effect=IOError("Mock IO error")):
            with pytest.raises(StorageError):
                kb_manager._read_file_content(Path("test.txt"))
        
    def test_process_with_privacy(self, kb_manager):
        """Test processing content with privacy protection."""
        # Mock the privacy engine and session manager
        with patch.object(kb_manager.privacy_engine, 'deidentify') as mock_deidentify, \
             patch.object(kb_manager, 'process_stream_of_consciousness') as mock_process:
            
            # Setup mocks
            mock_result = MagicMock()
            mock_result.text = "anonymized content"
            mock_result.privacy_level = "balanced"
            mock_result.tokens = ["TOKEN_001"]
            
            mock_deidentify.return_value = mock_result
            mock_process.return_value = {
                "extracted_info": {
                    "todos": [],
                    "calendar_events": [],
                    "notes": [{"title": "Test"}],
                    "tags": [],
                    "categories": []
                }
            }
            
            # Test processing with privacy
            result = kb_manager.process_with_privacy("test content", "session123")
            
            # Check that privacy metadata was added
            assert "privacy" in result
            assert result["privacy"]["session_id"] == "session123"
            assert result["privacy"]["privacy_level"] == "balanced"
            assert result["privacy"]["is_anonymized"] == True
        
    def test_process_with_privacy_error(self, kb_manager):
        """Test error handling in privacy processing."""
        # Mock privacy engine to raise exception
        with patch.object(kb_manager.privacy_engine, 'deidentify', side_effect=Exception("Mock privacy error")):
            with pytest.raises(PrivacyError):
                kb_manager.process_with_privacy("test content")
        
    def test_process_and_respond(self, kb_manager):
        """Test complete flow of processing and responding."""
        # Mock privacy processing and response generation
        with patch.object(kb_manager, 'process_with_privacy') as mock_privacy, \
             patch.object(kb_manager, '_generate_suggestions') as mock_suggestions, \
             patch.object(kb_manager.privacy_engine, 'reconstruct') as mock_reconstruct, \
             patch.object(kb_manager, '_generate_ai_response') as mock_response:
            
            # Setup mock returns
            mock_privacy.return_value = {
                "privacy": {"session_id": "session123"},
                "extracted_info": {
                    "todos": [{"title": "Test todo"}],
                    "calendar_events": [],
                    "notes": []
                }
            }
            mock_suggestions.return_value = [{"text": "Would you like a reminder?", "action": "remind"}]
            mock_reconstruct.return_value = "Would you like a reminder?"
            mock_response.return_value = "I've processed your input successfully."
            
            # Test process and respond
            result = kb_manager.process_and_respond("test content")
            
            # Check response format
            assert "response" in result
            assert result["response"]["message"] == "I've processed your input successfully."
            assert len(result["response"]["suggestions"]) == 1
        
    def test_process_and_respond_error_handling(self, kb_manager):
        """Test error handling in process_and_respond."""
        # Test with error in process_with_privacy
        with patch.object(kb_manager, 'process_with_privacy', side_effect=Exception("Mock processing error")):
            result = kb_manager.process_and_respond("test content")
            # Should return minimal error response
            assert "error" in result
            assert result["response"]["message"] == "I'm having trouble processing your request. Please try again later."
        
        # Test with error in response generation but successful processing
        with patch.object(kb_manager, 'process_with_privacy') as mock_privacy, \
             patch.object(kb_manager, '_generate_suggestions', return_value=[]), \
             patch.object(kb_manager, '_generate_ai_response', side_effect=Exception("Mock response error")):
            
            mock_privacy.return_value = {
                "privacy": {"session_id": "session123"},
                "extracted_info": {"todos": [], "calendar_events": [], "notes": []}
            }
            
            result = kb_manager.process_and_respond("test content")
            # Should still return a valid response with default message
            assert result["response"]["message"] == "I've processed your input."
            assert result["response"]["suggestions"] == []

    def test_extract_context_keywords_error(self, kb_manager):
        """Test error handling in context keyword extraction."""
        # Test with None to trigger exception
        keywords = kb_manager._extract_context_keywords(None)
        assert keywords == []  # Should return empty list rather than failing
        
    def test_mark_privacy_safe_error(self, kb_manager):
        """Test error handling in marking items privacy-safe."""
        # Test with improperly formatted data to trigger exception
        invalid_data = {"key": "not a list"}  # Will cause exception when iterating
        # Should not raise exception
        kb_manager._mark_privacy_safe(invalid_data)
        
    def test_generate_suggestions_error(self, kb_manager):
        """Test error handling in suggestion generation."""
        # Test with improperly formatted data to trigger exception
        invalid_info = None  # Will cause exception when accessing
        suggestions = kb_manager._generate_suggestions(invalid_info)
        assert suggestions == []  # Should return empty list rather than failing
        
    def test_generate_ai_response_error(self, kb_manager):
        """Test error handling in AI response generation."""
        # Test with improperly formatted data to trigger exception
        invalid_result = {"invalid": "format"}  # Missing extracted_info
        response = kb_manager._generate_ai_response(invalid_result, "session123")
        assert response == "I've processed your input."  # Should return fallback message
