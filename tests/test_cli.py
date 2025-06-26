#!/usr/bin/env python3
"""
Tests for the Knowledge Base CLI.
"""

import pytest
import json
import sys
import re
from unittest.mock import patch, MagicMock
from io import StringIO

from knowledge_base.cli import main


class TestCLI:
    """Test suite for the Knowledge Base CLI."""
    
    @patch('sys.argv', ['knowledge_base.cli', '--help'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_cli_help(self, mock_stdout):
        """Test that CLI help is displayed."""
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0
        output = mock_stdout.getvalue()
        assert 'Knowledge Base with Integrated Privacy CLI' in output
    
    @patch('knowledge_base.KnowledgeBaseManager.process_stream_of_consciousness')
    @patch('sys.argv', ['knowledge_base.cli', 'process', 'Test content'])
    def test_process_command(self, mock_process, capsys):
        """Test the process command."""
        # Mock the process_stream_of_consciousness method
        mock_process.return_value = {
            "original_content": "Test content",
            "processed_items": [],
            "extracted_info": {
                "todos": [],
                "calendar_events": [],
                "notes": [{"title": "Test Note"}],
                "tags": [],
                "categories": ["general"],
                "cross_refs": []
            }
        }
        
        # Execute the CLI
        main()
        
        # Check that the method was called with correct args
        mock_process.assert_called_once_with("Test content")
        
        # Check stdout
        captured = capsys.readouterr()
        
        # Extract JSON from potentially log-contaminated output
        json_match = re.search(r'({.+})', captured.out, re.DOTALL)
        assert json_match, "No JSON found in output"
        
        # Parse the JSON
        result = json.loads(json_match.group(1))
        assert result["original_content"] == "Test content"
        assert "extracted_info" in result
    
    @patch('knowledge_base.KnowledgeBaseManager.process_with_privacy')
    @patch('sys.argv', ['knowledge_base.cli', 'process-private', 'Private content', 
                        '--privacy-level', 'strict'])
    def test_process_private_command(self, mock_process, capsys):
        """Test the process-private command."""
        # Mock the process_with_privacy method
        mock_process.return_value = {
            "original_content": "Private content",
            "processed_items": [],
            "extracted_info": {
                "todos": [],
                "calendar_events": [],
                "notes": [{"title": "Private Note"}],
                "tags": [],
                "categories": ["personal"],
                "cross_refs": []
            },
            "privacy": {
                "session_id": "test-session",
                "privacy_level": "strict",
                "is_anonymized": True
            }
        }
        
        # Execute the CLI
        main()
        
        # Check that the method was called with correct args
        mock_process.assert_called_once_with("Private content", session_id=None, privacy_level="strict")
        
        # Check stdout
        captured = capsys.readouterr()
        
        # Extract JSON from potentially log-contaminated output
        json_match = re.search(r'({.+})', captured.out, re.DOTALL)
        assert json_match, "No JSON found in output"
        
        # Parse the JSON
        result = json.loads(json_match.group(1))
        assert result["original_content"] == "Private content"
        assert result["privacy"]["privacy_level"] == "strict"
    
    @patch('knowledge_base.KnowledgeBaseManager.search_content')
    @patch('sys.argv', ['knowledge_base.cli', 'search', 'Phoenix', 
                        '--content-type', 'note'])
    def test_search_command(self, mock_search, capsys):
        """Test the search command."""
        # Mock the search_content method
        mock_search.return_value = [
            {
                "file": "/path/to/note.md",
                "type": "note",
                "content_preview": "Project Phoenix meeting notes"
            }
        ]
        
        # Execute the CLI
        main()
        
        # Check that the method was called with correct args
        mock_search.assert_called_once_with("Phoenix", content_type="note")
        
        # Check stdout
        captured = capsys.readouterr()
        
        # Extract JSON from potentially log-contaminated output
        json_match = re.search(r'(\[.+\])', captured.out, re.DOTALL)
        assert json_match, "No JSON found in output"
        
        # Parse the JSON
        result = json.loads(json_match.group(1))
        assert len(result) == 1
        assert result[0]["type"] == "note"
        assert "Phoenix" in result[0]["content_preview"]
    
    @patch('knowledge_base.PrivacySessionManager.create_session')
    @patch('sys.argv', ['knowledge_base.cli', 'create-session', 
                        '--privacy-level', 'minimal'])
    def test_create_session_command(self, mock_create_session, capsys):
        """Test the create-session command."""
        # Mock the create_session method
        mock_create_session.return_value = "test-session-id"
        
        # Execute the CLI
        main()
        
        # Check that the method was called with correct args
        mock_create_session.assert_called_once_with("minimal")
        
        # Check stdout
        captured = capsys.readouterr()
        
        # Extract JSON from potentially log-contaminated output
        json_match = re.search(r'({.+})', captured.out, re.DOTALL)
        assert json_match, "No JSON found in output"
        
        # Parse the JSON
        result = json.loads(json_match.group(1))
        assert result["session_id"] == "test-session-id"
        assert result["privacy_level"] == "minimal"
    
    @patch('knowledge_base.KnowledgeBaseManager.process_and_respond')
    @patch('knowledge_base.PrivacySessionManager.create_session')
    @patch('builtins.input', side_effect=['Test question', 'exit'])
    @patch('sys.argv', ['knowledge_base.cli', 'chat', 
                        '--privacy-level', 'balanced'])
    def test_chat_command(self, mock_input, mock_create_session, mock_process, capsys):
        """Test the chat command."""
        # Mock the create_session method
        mock_create_session.return_value = "test-session-id"
        
        # Mock the process_and_respond method
        mock_process.return_value = {
            "response": {
                "message": "I processed your input.",
                "suggestions": [
                    {"text": "Would you like to know more?", "action": "more"}
                ]
            }
        }
        
        # Execute the CLI
        main()
        
        # Check that the methods were called correctly
        mock_create_session.assert_called_once_with("balanced")
        mock_process.assert_called_once_with("Test question", "test-session-id")
        
        # Check output
        captured = capsys.readouterr()
        assert "Starting interactive chat mode" in captured.out
        assert "I processed your input." in captured.out
        assert "Would you like to know more?" in captured.out 