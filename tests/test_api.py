#!/usr/bin/env python3
"""
Tests for the Knowledge Base API Server.
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Import the app from the API server
from scripts.api_server import app, get_kb_manager


@pytest.fixture
def mock_kb_manager():
    """Create a mock KnowledgeBaseManager for testing."""
    manager = MagicMock()
    
    # Set up mock return values
    manager.process_stream_of_consciousness.return_value = {
        "original_content": "Test content",
        "processed_items": [],
        "extracted_info": {
            "todos": [],
            "calendar_events": [],
            "notes": [{"title": "Test Note"}],
            "tags": [],
            "categories": ["general"]
        }
    }
    
    manager.process_with_privacy.return_value = {
        "original_content": "Private content",
        "processed_items": [],
        "extracted_info": {
            "todos": [],
            "calendar_events": [],
            "notes": [{"title": "Private Note"}]
        },
        "privacy": {
            "session_id": "test-session",
            "privacy_level": "balanced",
            "is_anonymized": True
        }
    }
    
    manager.search_content.return_value = [
        {
            "file": "/path/to/note.md",
            "type": "note",
            "content_preview": "Test content preview"
        }
    ]
    
    manager.process_and_respond.return_value = {
        "response": {
            "message": "I processed your input.",
            "suggestions": []
        }
    }
    
    # Set up session manager mock
    session_manager = MagicMock()
    session_manager.create_session.return_value = "test-session-id"
    session_manager.get_session.return_value = {
        "id": "test-session-id",
        "privacy_level": "balanced",
        "created": "2023-01-01T00:00:00Z"
    }
    
    manager.session_manager = session_manager
    
    return manager


@pytest.fixture
def client(mock_kb_manager):
    """Create a test client with the mock KB manager."""
    # Override the dependency to use our mock
    app.dependency_overrides[get_kb_manager] = lambda: mock_kb_manager
    return TestClient(app)


class TestAPI:
    """Test suite for the Knowledge Base API."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Knowledge Base with Integrated Privacy API"
        assert "version" in data
        
    def test_process_endpoint(self, client, mock_kb_manager):
        """Test the /process endpoint."""
        response = client.post(
            "/process",
            json={"content": "Test content to process"}
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["original_content"] == "Test content"
        
        # Verify the mock was called correctly
        mock_kb_manager.process_stream_of_consciousness.assert_called_once_with("Test content to process")
        
    def test_process_private_endpoint(self, client, mock_kb_manager):
        """Test the /process-private endpoint."""
        response = client.post(
            "/process-private",
            json={
                "content": "Private content to process",
                "privacy_level": "strict"
            }
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert "privacy" in data
        assert data["privacy"]["privacy_level"] == "balanced"  # From the mock return value
        
        # Verify the mock was called correctly
        mock_kb_manager.process_with_privacy.assert_called_once_with(
            "Private content to process",
            session_id=None,
            privacy_level="strict"
        )
        
    def test_search_endpoint(self, client, mock_kb_manager):
        """Test the /search endpoint."""
        response = client.post(
            "/search",
            json={
                "query": "test query",
                "content_type": "note"
            }
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["type"] == "note"
        
        # Verify the mock was called correctly
        mock_kb_manager.search_content.assert_called_once_with("test query", "note")
        
    def test_create_session_endpoint(self, client, mock_kb_manager):
        """Test the /sessions endpoint."""
        response = client.post(
            "/sessions",
            json={
                "privacy_level": "minimal",
                "metadata": {"source": "test"}
            }
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-id"
        assert data["privacy_level"] == "minimal"
        
        # Verify the mock was called correctly
        mock_kb_manager.session_manager.create_session.assert_called_once_with(
            "minimal", 
            {"source": "test"}
        )
        
    def test_get_session_endpoint(self, client, mock_kb_manager):
        """Test the /sessions/{session_id} endpoint."""
        response = client.get("/sessions/test-session-id")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-session-id"
        assert data["privacy_level"] == "balanced"
        
        # Verify the mock was called correctly
        mock_kb_manager.session_manager.get_session.assert_called_once_with("test-session-id")
        
    def test_get_session_not_found(self, client, mock_kb_manager):
        """Test the /sessions/{session_id} endpoint with a non-existent session."""
        # Configure the mock to return None for this specific session ID
        mock_kb_manager.session_manager.get_session.return_value = None
        
        response = client.get("/sessions/non-existent-id")
        
        # Check response
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
        
    def test_conversation_endpoint(self, client, mock_kb_manager):
        """Test the /conversation endpoint."""
        response = client.post(
            "/conversation",
            json={
                "message": "Test message",
                "session_id": "test-session-id"
            }
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["response"]["message"] == "I processed your input."
        
        # Verify the mock was called correctly
        mock_kb_manager.process_and_respond.assert_called_once_with(
            "Test message", 
            "test-session-id"
        )
        
    def test_error_handling(self, client, mock_kb_manager):
        """Test API error handling."""
        # Configure the mock to raise an exception
        mock_kb_manager.process_stream_of_consciousness.side_effect = Exception("Test error")
        
        response = client.post(
            "/process",
            json={"content": "Error content"}
        )
        
        # Check response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Test error" in data["detail"] 