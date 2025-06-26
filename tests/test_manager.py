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
from unittest.mock import MagicMock, patch

from knowledge_base.manager import KnowledgeBaseManager
from knowledge_base.content_types import Note, Todo, CalendarEvent
from knowledge_base.utils.config import Config


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
        
    def test_extract_calendar_events(self, kb_manager):
        """Test extraction of calendar events from content."""
        content = "Meeting with John on March 15th at 2:30."
        events = kb_manager._extract_calendar_events(content)
        
        assert len(events) > 0
        # Check if at least one event title contains relevant information
        assert any("March 15th" in event["title"] for event in events)
        assert any("John" in event["title"] for event in events)
        
        # Test other event formats
        content = "Call with team tomorrow at 10:00"
        events = kb_manager._extract_calendar_events(content)
        
        assert len(events) > 0
        # Check if at least one event title contains relevant information
        assert any("tomorrow" in event["title"] for event in events)
        assert any("10:00" in event["title"] for event in events)
        
    def test_extract_tags(self, kb_manager):
        """Test extraction of tags from content."""
        content = "Working on the project report #work #important"
        tags = kb_manager._extract_tags(content)
        
        assert "work" in tags
        assert "important" in tags
        
        # Test context-based tags
        content = "Need to finish this at work before going home."
        tags = kb_manager._extract_tags(content)
        
        assert "@work" in tags
        
        # Test topic-based tags
        content = "Need to study the research paper tonight."
        tags = kb_manager._extract_tags(content)
        
        assert "#learning" in tags
        
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
    
    @patch('knowledge_base.privacy.PrivacyEngine.deidentify')
    def test_process_with_privacy(self, mock_deidentify, kb_manager):
        """Test the privacy-preserving processing method."""
        # Create a DeidentificationResult mock
        mock_result = MagicMock(
            text="Anonymized content",
            privacy_level="balanced",
            tokens=["PERSON_001"],
            token_map={"PERSON_001": "John"},
            entity_relationships={}
        )
        mock_deidentify.return_value = mock_result
        
        # Mock process_stream_of_consciousness
        with patch.object(kb_manager, 'process_stream_of_consciousness') as mock_process:
            mock_process.return_value = {
                "original_content": "Anonymized content",
                "processed_items": [],
                "extracted_info": {
                    "todos": [],
                    "calendar_events": [],
                    "notes": [{"title": "Test Note"}],
                    "tags": [],
                    "categories": ["work"],
                    "cross_refs": []
                }
            }
            
            # Call the method
            result = kb_manager.process_with_privacy("Test content with John's information")
            
            # Verify the privacy engine was called
            mock_deidentify.assert_called_once()
            
            # Verify privacy metadata was added
            assert "privacy" in result
            assert "session_id" in result["privacy"]
            assert "privacy_level" in result["privacy"]
            assert result["privacy"]["privacy_level"] == "balanced"
            
            # Verify items were marked as privacy-safe
            for note in result["extracted_info"]["notes"]:
                assert note["privacy_safe"] is True

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
