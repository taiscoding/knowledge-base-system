# Knowledge Base API Documentation

*Last updated: June 26, 2025*

## Overview

The Knowledge Base System provides a REST API for content management with built-in privacy features. This document outlines the available endpoints, request/response formats, and usage examples.

## Base URL

```
http://localhost:8000
```

For production deployments, replace with your actual server URL.

## Authentication

Authentication is not implemented in the core API but should be added in production deployments.

## Endpoints

### Health Check

**GET /**

Returns the current status of the API service.

**Response**
```json
{
  "name": "Knowledge Base with Integrated Privacy API",
  "version": "1.0.0",
  "docs_url": "/docs"
}
```

### Process Content (Without Privacy)

**POST /process**

Process a text input without privacy features.

**Request Body**
```json
{
  "content": "Call John Smith tomorrow about the project status."
}
```

**Response**
```json
{
  "original_content": "Call John Smith tomorrow about the project status.",
  "processed_items": [],
  "extracted_info": {
    "todos": [
      {
        "title": "Call John Smith tomorrow about the project status",
        "description": "",
        "priority": "medium",
        "status": "active",
        "category": "task",
        "tags": ["@work"],
        "due_date": "2025-06-27",
        "context": "@work",
        "id": "c58f9a2e-19af-4f5c-802b-d0a3739a32d0",
        "created": "2025-06-26T13:45:32.123456+00:00",
        "last_modified": "2025-06-26T13:45:32.123456+00:00"
      }
    ],
    "calendar_events": [],
    "notes": [],
    "tags": ["@work"],
    "categories": ["work"],
    "cross_refs": []
  }
}
```

### Process with Privacy

**POST /process-private**

Process text with privacy preservation.

**Request Body**
```json
{
  "content": "Call John Smith tomorrow about the project status.",
  "session_id": "c2ba9bef-1feb-4c6e-b5dc-f715b8cff37f",
  "privacy_level": "balanced"
}
```

**Response**
```json
{
  "original_content": "[PERSON_001] tomorrow about the project status.",
  "processed_items": [],
  "extracted_info": {
    "todos": [
      {
        "title": "[PERSON_001] tomorrow about the project status",
        "description": "",
        "priority": "medium",
        "status": "active",
        "category": "task",
        "tags": ["@work"],
        "due_date": "2025-06-27",
        "context": "@work",
        "id": "a7b4c8d9-2e3f-4a5b-8c9d-1e2f3a4b5c6d",
        "created": "2025-06-26T13:45:32.123456+00:00",
        "last_modified": "2025-06-26T13:45:32.123456+00:00",
        "privacy_safe": true
      }
    ],
    "calendar_events": [],
    "notes": [],
    "tags": ["@work"],
    "categories": ["work"],
    "cross_refs": []
  },
  "privacy": {
    "session_id": "c2ba9bef-1feb-4c6e-b5dc-f715b8cff37f",
    "privacy_level": "balanced",
    "tokens": {
      "PERSON_001": "Call John Smith"
    },
    "is_anonymized": true
  }
}
```

### Search Content

**POST /search**

Search across knowledge base content.

**Request Body**
```json
{
  "query": "project",
  "content_type": "todo"
}
```

**Response**
```json
{
  "results": [
    {
      "file": "data/todos/todo-2025-06-26-134532.json",
      "type": "todo",
      "content_preview": "{\"title\": \"Call John Smith tomorrow about the project status\", \"description\": \"\", \"priority\": \"medium\", \"status\": \"active\", \"category\": \"task\", \"..."
    }
  ]
}
```

### Create Session

**POST /sessions**

Create a new privacy session.

**Request Body**
```json
{
  "privacy_level": "balanced",
  "metadata": {
    "application": "mobile_app",
    "user_context": "work"
  }
}
```

**Response**
```json
{
  "session_id": "c2ba9bef-1feb-4c6e-b5dc-f715b8cff37f",
  "privacy_level": "balanced",
  "message": "Created new privacy session: c2ba9bef-1feb-4c6e-b5dc-f715b8cff37f"
}
```

### Get Session

**GET /sessions/{session_id}**

Get details about a specific session.

**Response**
```json
{
  "created_at": "2025-06-26T13:42:15.123456",
  "last_used": "2025-06-26T13:45:32.123456",
  "privacy_level": "balanced",
  "token_mappings": {
    "PERSON_001": "Call John Smith"
  },
  "entity_relationships": {
    "PERSON_001": {
      "type": "PERSON",
      "linked_entities": []
    }
  },
  "preserved_context": ["call", "project", "status"],
  "metadata": {
    "application": "mobile_app",
    "user_context": "work"
  }
}
```

### Conversation

**POST /conversation**

Process content with privacy and generate intelligent response.

**Request Body**
```json
{
  "message": "Call John Smith tomorrow about the project status.",
  "session_id": "c2ba9bef-1feb-4c6e-b5dc-f715b8cff37f"
}
```

**Response**
```json
{
  "original_content": "[PERSON_001] tomorrow about the project status.",
  "processed_items": [],
  "extracted_info": {
    "todos": [
      {
        "title": "[PERSON_001] tomorrow about the project status",
        "description": "",
        "priority": "medium",
        "status": "active",
        "category": "task",
        "tags": ["@work"],
        "due_date": "2025-06-27",
        "context": "@work",
        "id": "a7b4c8d9-2e3f-4a5b-8c9d-1e2f3a4b5c6d",
        "created": "2025-06-26T13:45:32.123456+00:00",
        "last_modified": "2025-06-26T13:45:32.123456+00:00",
        "privacy_safe": true
      }
    ],
    "calendar_events": [],
    "notes": [],
    "tags": ["@work"],
    "categories": ["work"],
    "cross_refs": []
  },
  "privacy": {
    "session_id": "c2ba9bef-1feb-4c6e-b5dc-f715b8cff37f",
    "privacy_level": "balanced",
    "tokens": {
      "PERSON_001": "Call John Smith"
    },
    "is_anonymized": true
  },
  "response": {
    "message": "I've added 1 task(s) to your to-do list. Is there anything else you need help with regarding this?",
    "suggestions": [
      {
        "type": "todo_followup",
        "text": "Would you like to set a reminder for this task?",
        "action": "set_reminder"
      }
    ]
  }
}
```

## Error Responses

**Validation Error**
```json
{
  "detail": "Missing required field: content"
}
```

**Not Found Error**
```json
{
  "detail": "Session c2ba9bef-1feb-4c6e-b5dc-f715b8cff37f not found"
}
```

**Server Error**
```json
{
  "detail": "Processing failed: Internal server error"
}
```

## Using the API with Python

```python
import requests
import json

# API endpoint
API_URL = "http://localhost:8000"

# Process with privacy example
def process_with_privacy():
    # First create a session
    session_response = requests.post(
        f"{API_URL}/sessions",
        json={"privacy_level": "balanced"}
    )
    
    if session_response.status_code == 200:
        session_data = session_response.json()
        session_id = session_data["session_id"]
        
        # Now process with privacy
        content_data = {
            "content": "Call John Smith tomorrow about the project status.",
            "session_id": session_id
        }
        
        response = requests.post(
            f"{API_URL}/process-private",
            json=content_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Privacy Session: {session_id}")
            print(f"Original content: {content_data['content']}")
            print(f"Privacy-safe content: {result['original_content']}")
            print("Extracted todos:")
            for todo in result["extracted_info"]["todos"]:
                print(f"- {todo['title']}")
            print(f"Tokens: {json.dumps(result['privacy']['tokens'], indent=2)}")
        else:
            print(f"Error processing: {response.status_code}")
            print(response.text)
    else:
        print(f"Error creating session: {session_response.status_code}")
        print(session_response.text)

# Conversation example
def have_conversation():
    # First create a session
    session_response = requests.post(
        f"{API_URL}/sessions",
        json={"privacy_level": "balanced"}
    )
    
    if session_response.status_code == 200:
        session_id = session_response.json()["session_id"]
        
        # Have a conversation
        conversation_data = {
            "message": "Schedule a meeting with Susan Jones next Wednesday at 2pm",
            "session_id": session_id
        }
        
        response = requests.post(
            f"{API_URL}/conversation",
            json=conversation_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Assistant: {result['response']['message']}")
            print("\nSuggestions:")
            for suggestion in result["response"]["suggestions"]:
                print(f"- {suggestion['text']}")
        else:
            print(f"Error in conversation: {response.status_code}")
            print(response.text)
    else:
        print(f"Error creating session: {session_response.status_code}")
        print(session_response.text)
```

## CLI Usage

The Knowledge Base System also provides a command-line interface:

```bash
# Process text with privacy
python -m knowledge_base.cli process-private "Call John Smith tomorrow about the project status."

# Create a new privacy session
python -m knowledge_base.cli create-session --privacy-level balanced

# Interactive chat with privacy
python -m knowledge_base.cli chat

# Search across content
python -m knowledge_base.cli search "project"
```

## Recommended Practices

1. **Session Management**: Create and reuse sessions for related content to maintain consistency
2. **Privacy Level Selection**:
   - "strict": Maximum privacy with more tokenization (recommended for sensitive data)
   - "balanced": Standard level that balances privacy and context (default)
   - "minimal": Lower privacy with only essential tokenization
3. **Error Handling**: Implement proper error handling in client applications
4. **Interactive Mode**: Use the conversation endpoint for interactive experiences 