#!/usr/bin/env python3
"""
Tests for helper utility functions.
"""

import pytest
import re
from datetime import datetime, timezone, timedelta
from knowledge_base.utils.helpers import (
    generate_id, get_timestamp, extract_hashtags, 
    extract_mentions, parse_date_string, detect_content_type,
    format_filename, sanitize_filename
)


class TestHelperFunctions:
    """Test suite for helper utility functions."""
    
    def test_generate_id(self):
        """Test that generate_id produces unique IDs."""
        id1 = generate_id()
        id2 = generate_id()
        
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2
        assert len(id1) == 36  # UUID4 standard length
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', id1)
    
    def test_get_timestamp(self):
        """Test that get_timestamp returns proper ISO format timestamp."""
        timestamp = get_timestamp()
        
        assert isinstance(timestamp, str)
        # Try parsing the timestamp, should not raise an exception
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        # Ensure the timestamp is close to current time
        now = datetime.now(timezone.utc)
        timestamp_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        delta = abs((now - timestamp_time).total_seconds())
        
        assert delta < 5  # Within 5 seconds
    
    def test_extract_hashtags(self):
        """Test that hashtags are correctly extracted from text."""
        text = "This is a test with #hashtag1 and #hashtag2 and #combined_hashtag."
        hashtags = extract_hashtags(text)
        
        assert isinstance(hashtags, list)
        assert len(hashtags) == 3
        assert "hashtag1" in hashtags
        assert "hashtag2" in hashtags
        assert "combined_hashtag" in hashtags
    
    def test_extract_hashtags_empty(self):
        """Test hashtag extraction with no hashtags."""
        text = "This text has no hashtags at all."
        hashtags = extract_hashtags(text)
        
        assert isinstance(hashtags, list)
        assert len(hashtags) == 0
    
    def test_extract_mentions(self):
        """Test that mentions are correctly extracted from text."""
        text = "Hey @user1 and @user2 and @admin_user, check this out!"
        mentions = extract_mentions(text)
        
        assert isinstance(mentions, list)
        assert len(mentions) == 3
        assert "user1" in mentions
        assert "user2" in mentions
        assert "admin_user" in mentions
    
    def test_extract_mentions_empty(self):
        """Test mention extraction with no mentions."""
        text = "This text has no mentions at all."
        mentions = extract_mentions(text)
        
        assert isinstance(mentions, list)
        assert len(mentions) == 0
    
    def test_parse_date_string_valid_formats(self):
        """Test parsing date strings in various formats."""
        formats = {
            "2023-01-15": datetime(2023, 1, 15),
            "01/15/2023": datetime(2023, 1, 15),
            "15/01/2023": datetime(2023, 1, 15),
            "January 15, 2023": datetime(2023, 1, 15),
            "Jan 15, 2023": datetime(2023, 1, 15),
            "2023-01-15T10:30:45": datetime(2023, 1, 15, 10, 30, 45),
            "2023-01-15T10:30:45.123Z": datetime(2023, 1, 15, 10, 30, 45, 123000)
        }
        
        for date_str, expected in formats.items():
            result = parse_date_string(date_str)
            assert result is not None
            assert result.year == expected.year
            assert result.month == expected.month
            assert result.day == expected.day
            
            if hasattr(expected, 'hour'):
                assert result.hour == expected.hour
                assert result.minute == expected.minute
                assert result.second == expected.second
    
    def test_parse_date_string_relative(self):
        """Test parsing relative date strings."""
        today = datetime.now()
        tomorrow = today.replace(day=today.day + 1)
        yesterday = today.replace(day=today.day - 1)
        
        assert parse_date_string("today").day == today.day
        assert parse_date_string("tomorrow").day == tomorrow.day
        assert parse_date_string("yesterday").day == yesterday.day
    
    def test_parse_date_string_invalid(self):
        """Test parsing invalid date strings."""
        assert parse_date_string("not a date") is None
        assert parse_date_string("") is None
        assert parse_date_string("2023-13-45") is None  # Invalid month and day
    
    def test_detect_content_type_todo(self):
        """Test detection of todo content type."""
        todo_texts = [
            "TODO: finish the report",
            "[ ] Buy groceries",
            "Remember to call John",
            "Don't forget to submit the form",
            "Action Item: Review PR",
            "Task: Complete documentation",
        ]
        
        for text in todo_texts:
            assert detect_content_type(text) == "todo"
    
    def test_detect_content_type_calendar(self):
        """Test detection of calendar content type."""
        calendar_texts = [
            "Meeting with Sarah at 2pm",
            "Doctor appointment next Tuesday",
            "Call with client scheduled for tomorrow",
            "Event: Company retreat",
            "Schedule review with manager",
        ]
        
        for text in calendar_texts:
            assert detect_content_type(text) == "calendar"
    
    def test_detect_content_type_project(self):
        """Test detection of project content type."""
        project_texts = [
            "Project Phoenix timeline",
            "New initiative for Q1",
            "Project plan for website redesign",
            "Workflow for content approval",
            "Key milestones for 2023",
        ]
        
        for text in project_texts:
            assert detect_content_type(text) == "project"
    
    def test_detect_content_type_default(self):
        """Test default content type detection (note)."""
        note_texts = [
            "Ideas for the weekend",
            "Thoughts on the presentation",
            "Book recommendations",
            "Random notes from the meeting",
        ]
        
        for text in note_texts:
            assert detect_content_type(text) == "note"
    
    def test_format_filename(self):
        """Test filename formatting with templates."""
        template = "note-{timestamp}-{category}.md"
        data = {
            "category": "work"
        }
        
        filename = format_filename(template, data)
        
        assert filename.startswith("note-")
        assert filename.endswith("-work.md")
        assert re.match(r"note-\d{4}-\d{2}-\d{2}-\d{6}-work\.md", filename)
        
        # Test with all provided data
        template = "{type}-{id}-{category}.{ext}"
        data = {
            "type": "note",
            "id": "12345",
            "category": "personal",
            "ext": "md",
            "timestamp": "2023-01-01-120000"
        }
        
        filename = format_filename(template, data)
        assert filename == "note-12345-personal.md"
    
    def test_sanitize_filename(self):
        """Test sanitization of filenames."""
        invalid_filenames = {
            "file<with>invalid:chars.txt": "file_with_invalid_chars.txt",
            "file/with\\more|invalid?chars*.txt": "file_with_more_invalid_chars_.txt",
            'file"with"quotes.txt': "file_with_quotes.txt",
            "normal_file.txt": "normal_file.txt"  # Should remain unchanged
        }
        
        for original, expected in invalid_filenames.items():
            assert sanitize_filename(original) == expected 