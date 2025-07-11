# Knowledge Base API Documentation

*Last updated: June 27, 2025*

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

### Hierarchical Organization & Relationships

#### Create Folder

**POST /folders**

Create a new folder in the hierarchy.

**Request Body**
```json
{
  "title": "Work Projects",
  "parent_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "description": "Collection of work-related projects",
  "icon": "folder-work"
}
```

**Response**
```json
{
  "id": "7f8e9d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c",
  "title": "Work Projects",
  "description": "Collection of work-related projects",
  "icon": "folder-work",
  "parent_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "path": "/Root Folder/Work Projects",
  "created": "2025-06-26T14:30:45.123456+00:00",
  "last_modified": "2025-06-26T14:30:45.123456+00:00",
  "children": []
}
```

#### Get Folder Contents

**GET /folders/{folder_id}/contents**

Retrieve the contents of a folder.

**Response**
```json
{
  "folder": {
    "id": "7f8e9d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c",
    "title": "Work Projects",
    "description": "Collection of work-related projects",
    "path": "/Root Folder/Work Projects",
    "parent_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
  },
  "contents": [
    {
      "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "title": "Project Phoenix",
      "content_type": "project",
      "last_modified": "2025-06-26T14:35:22.123456+00:00"
    },
    {
      "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
      "title": "Website Redesign",
      "content_type": "project",
      "last_modified": "2025-06-26T14:36:10.123456+00:00"
    }
  ]
}
```

#### Get Folder Tree

**GET /folders/tree**

Retrieve the folder hierarchy tree.

**Query Parameters**
```
root_id: Optional ID of the root folder (default: system root)
max_depth: Maximum depth to retrieve (default: -1 for unlimited)
```

**Response**
```json
{
  "id": "root-folder-id",
  "title": "Root Folder",
  "path": "/",
  "type": "folder",
  "children": [
    {
      "id": "7f8e9d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c",
      "title": "Work Projects",
      "path": "/Work Projects",
      "type": "folder",
      "children": [
        {
          "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
          "title": "Project Phoenix",
          "path": "/Work Projects/Project Phoenix",
          "type": "content"
        },
        {
          "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
          "title": "Website Redesign",
          "path": "/Work Projects/Website Redesign",
          "type": "content"
        }
      ]
    },
    {
      "id": "personal-folder-id",
      "title": "Personal",
      "path": "/Personal",
      "type": "folder",
      "children": []
    }
  ]
}
```

#### Move Content

**POST /content/{content_id}/move**

Move content to a different folder.

**Request Body**
```json
{
  "destination_folder_id": "7f8e9d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c"
}
```

**Response**
```json
{
  "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "title": "Project Notes",
  "content_type": "note",
  "parent_id": "7f8e9d6c-5b4a-3f2e-1d0c-9b8a7f6e5d4c",
  "path": "/Work Projects/Project Notes",
  "message": "Content moved successfully"
}
```

#### Create Relationship

**POST /relationships**

Create a relationship between two content items.

**Request Body**
```json
{
  "source_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "target_id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
  "relationship_type": "REFERENCE",
  "description": "Meeting notes reference the project document"
}
```

**Response**
```json
{
  "source_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "target_id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
  "relationship_type": "REFERENCE",
  "description": "Meeting notes reference the project document",
  "created": "2025-06-26T14:42:15.123456+00:00"
}
```

#### Get Related Content

**GET /content/{content_id}/related**

Get content related to a specific item.

**Query Parameters**
```
relationship_type: Optional filter by relationship type
include_content: Whether to include full content data (default: false)
```

**Response**
```json
{
  "content_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "title": "Project Phoenix",
  "related_items": [
    {
      "content_id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
      "relationship": {
        "source_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        "target_id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        "relationship_type": "DEPENDENCY",
        "description": "Project task"
      },
      "content": {
        "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        "title": "Create project timeline",
        "content_type": "todo",
        "status": "active"
      }
    },
    {
      "content_id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
      "relationship": {
        "source_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        "target_id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
        "relationship_type": "REFERENCE",
        "description": "Project documentation"
      },
      "content": {
        "id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
        "title": "Meeting Notes",
        "content_type": "note"
      }
    }
  ]
}
```

#### Delete Relationship

**DELETE /relationships/{source_id}/{target_id}**

Delete a relationship between two content items.

**Response**
```json
{
  "status": "success",
  "message": "Relationship deleted successfully"
}
```

### Semantic Search & Recommendations

#### Semantic Search

**POST /semantic-search**

Search content semantically using natural language.

**Request Body**
```json
{
  "query": "artificial intelligence and machine learning",
  "top_k": 5,
  "content_types": ["note", "project"],
  "min_similarity": 0.7
}
```

**Response**
```json
{
  "query": "artificial intelligence and machine learning",
  "results": [
    {
      "content_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "similarity": 0.92,
      "content": {
        "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        "title": "AI Research Notes",
        "content": "Notes on recent advancements in artificial intelligence and machine learning techniques.",
        "content_type": "note",
        "category": "research",
        "tags": ["AI", "research", "deep learning"]
      }
    },
    {
      "content_id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
      "similarity": 0.85,
      "content": {
        "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        "title": "Machine Learning Project",
        "description": "A project focused on neural networks and deep learning algorithms.",
        "content_type": "project",
        "category": "tech",
        "tags": ["AI", "machine learning", "neural networks"]
      }
    }
  ]
}
```

#### Similar Content

**GET /content/{content_id}/similar**

Find content similar to a specific item.

**Query Parameters**
```
top_k: Maximum number of results to return (default: 5)
min_similarity: Minimum similarity threshold (default: 0.7)
```

**Response**
```json
{
  "content_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "similar_items": [
    {
      "content_id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
      "similarity": 0.88,
      "content": {
        "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        "title": "Machine Learning Project",
        "content_type": "project"
      }
    },
    {
      "content_id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
      "similarity": 0.76,
      "content": {
        "id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
        "title": "Deep Learning Techniques",
        "content_type": "note"
      }
    }
  ]
}
```

#### Get Recommendations

**GET /content/{content_id}/recommendations**

Get recommendations for a specific content item.

**Query Parameters**
```
max_items: Maximum number of recommendations to return (default: 5)
```

**Response**
```json
{
  "content_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "recommendations": [
    {
      "content_id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
      "score": 0.92,
      "reason": "Referenced content",
      "content": {
        "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        "title": "Meeting Notes",
        "content_type": "note"
      }
    },
    {
      "content_id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
      "score": 0.85,
      "reason": "Semantically similar (0.85)",
      "content": {
        "id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
        "title": "Project Timeline",
        "content_type": "todo"
      }
    }
  ]
}
```

#### Get Contextual Suggestions

**POST /contextual-suggestions**

Get contextual suggestions based on user activity.

**Request Body**
```json
{
  "content_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "text": "I'm writing about knowledge management systems and methodologies.",
  "max_items": 3
}
```

**Response**
```json
{
  "suggestions": [
    {
      "content_id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
      "score": 0.88,
      "reason": "Relevant to current context (0.88)",
      "content": {
        "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        "title": "Knowledge Graph Systems",
        "content_type": "note"
      }
    },
    {
      "content_id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
      "score": 0.82,
      "reason": "Referenced in current document",
      "content": {
        "id": "c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f",
        "title": "Methodology Comparison",
        "content_type": "note"
      }
    }
  ]
}
```

#### Knowledge Graph

**GET /knowledge-graph**

Generate a knowledge graph for visualization.

**Query Parameters**
```
root_ids: Comma-separated list of content IDs to use as roots
max_depth: Maximum depth to traverse (default: 2)
include_hierarchy: Whether to include hierarchical relationships (default: true)
```

**Response**
```json
{
  "graph": {
    "nodes": [
      {
        "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        "label": "Project Phoenix",
        "type": "project",
        "data": {
          "path": "/Work/Projects/Project Phoenix",
          "category": "work",
          "tags": ["project", "important"]
        }
      },
      {
        "id": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        "label": "Create project timeline",
        "type": "todo",
        "data": {
          "path": "/Work/Tasks/Create project timeline",
          "category": "task",
          "tags": ["project", "planning"]
        }
      }
    ],
    "edges": [
      {
        "source": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        "target": "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
        "label": "DEPENDENCY",
        "data": {
          "description": "Project task",
          "type": "DEPENDENCY",
          "created": "2025-06-26T14:30:15.123456+00:00"
        }
      }
    ]
  },
  "statistics": {
    "node_count": 2,
    "edge_count": 1,
    "node_type_counts": {
      "project": 1,
      "todo": 1
    },
    "edge_type_counts": {
      "DEPENDENCY": 1
    }
  },
  "config": {
    "directed": true,
    "hierarchical": true
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

# Knowledge Base System: API Reference

This document serves as a reference for the Knowledge Base System API, covering endpoints, request/response formats, and error handling.

## Core API Endpoints

### Content Management

#### Process Content
```http
POST /api/v1/content/process
```

Processes raw content streams and identifies content types.

**Request Body:**
```json
{
  "content": "Meeting with John about Project X tomorrow at 2pm",
  "session_id": "user-session-123",  
  "privacy_level": "standard"
}
```

**Response:**
```json
{
  "status": "success",
  "processed_items": [
    {
      "content_type": "calendar",
      "extracted_data": {
        "title": "Meeting with [PERSON_001] about [PROJECT_001]",
        "datetime": "2023-05-15T14:00:00",
        "attendees": ["[PERSON_001]"],
        "tags": ["meeting", "[PROJECT_001]"]
      },
      "file_path": "data/calendar/event-20230515-1400.json",
      "privacy": {
        "tokens": {
          "[PERSON_001]": {"type": "person", "confidence": 0.95},
          "[PROJECT_001]": {"type": "project", "confidence": 0.92}
        }
      }
    }
  ],
  "privacy_session_id": "session-123abc"
}
```

**Error Responses:**

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | `ValidationError` | Invalid request format or missing required fields |
| 422 | `ContentProcessingError` | Content could not be processed due to format issues |
| 500 | `PrivacyError` | Privacy operations failed during content processing |
| 500 | `StorageError` | Content processed but could not be saved |

#### Retrieve Content
```http
GET /api/v1/content/{content_type}/{id}
```

Retrieves a specific content item by ID.

**Parameters:**
- `content_type` - Type of content (notes, todos, calendar, journal)
- `id` - Content identifier

**Response:**
```json
{
  "status": "success",
  "content": {
    "id": "todo-20230515-123456",
    "title": "Prepare presentation for [PROJECT_001]",
    "due_date": "2023-05-20",
    "priority": "high",
    "tags": ["presentation", "[PROJECT_001]"],
    "content_type": "todos",
    "created_at": "2023-05-15T12:34:56",
    "updated_at": "2023-05-15T12:34:56"
  }
}
```

**Error Responses:**

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 404 | `NotFoundError` | Content with specified ID not found |
| 400 | `ValidationError` | Invalid content type or ID format |
| 500 | `StorageError` | Storage system could not retrieve content |

#### Search Content
```http
GET /api/v1/search?q={query}&type={content_type}&limit={limit}&offset={offset}
```

Searches for content matching the query.

**Parameters:**
- `q` - Search query 
- `type` (optional) - Filter by content type
- `limit` (optional) - Maximum number of results (default: 10)
- `offset` (optional) - Result offset for pagination (default: 0)

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "id": "note-20230514-123456",
      "title": "Notes from meeting with [PERSON_001]",
      "content_type": "notes",
      "snippet": "...discussed the timelines for [PROJECT_001] and agreed on...",
      "score": 0.92,
      "created_at": "2023-05-14T12:34:56",
      "updated_at": "2023-05-14T12:34:56"
    },
    {
      "id": "todo-20230515-123456",
      "title": "Prepare presentation for [PROJECT_001]",
      "content_type": "todos",
      "snippet": "...need to include latest metrics and forecast...",
      "score": 0.85,
      "created_at": "2023-05-15T12:34:56",
      "updated_at": "2023-05-15T12:34:56"
    }
  ],
  "total": 24,
  "limit": 10,
  "offset": 0
}
```

**Error Responses:**

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | `ValidationError` | Invalid search parameters |
| 500 | `SearchError` | Search index error or other search failure |

### Privacy Management

#### Generate Privacy Tokens
```http
POST /api/v1/privacy/tokenize
```

Tokenizes sensitive information in content.

**Request Body:**
```json
{
  "text": "Meeting with John about Project X", 
  "session_id": "user-session-123",
  "entity_types": ["person", "project", "location"],
  "privacy_level": "standard"
}
```

**Response:**
```json
{
  "status": "success",
  "tokenized_text": "Meeting with [PERSON_001] about [PROJECT_001]",
  "tokens": {
    "[PERSON_001]": {
      "type": "person",
      "confidence": 0.95
    },
    "[PROJECT_001]": {
      "type": "project",
      "confidence": 0.92
    }
  },
  "session_id": "session-123abc"
}
```

**Error Responses:**

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | `ValidationError` | Invalid request format or text |
| 429 | `CircuitBreakerOpenError` | Privacy service circuit breaker is open due to failures |
| 500 | `PrivacyError` | Privacy tokenization failed |

#### Resolve Privacy Tokens
```http
POST /api/v1/privacy/detokenize
```

Resolves privacy tokens back to their original values in the session.

**Request Body:**
```json
{
  "text": "Meeting with [PERSON_001] about [PROJECT_001]",
  "session_id": "session-123abc"
}
```

**Response:**
```json
{
  "status": "success",
  "resolved_text": "Meeting with John about Project X",
  "resolved_tokens": {
    "[PERSON_001]": {
      "value": "John",
      "type": "person"
    },
    "[PROJECT_001]": {
      "value": "Project X",
      "type": "project"
    }
  }
}
```

**Error Responses:**

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | `ValidationError` | Invalid request format or text |
| 404 | `NotFoundError` | Session not found or expired |
| 429 | `CircuitBreakerOpenError` | Privacy service circuit breaker is open due to failures |
| 500 | `PrivacyError` | Privacy resolution failed |

### System Status

#### Check System Health
```http
GET /api/v1/system/health
```

Checks the health of system components.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "storage": {
      "status": "healthy",
      "latency_ms": 12
    },
    "privacy_engine": {
      "status": "healthy",
      "latency_ms": 45
    },
    "search_index": {
      "status": "healthy",
      "latency_ms": 28,
      "document_count": 1250
    },
    "token_intelligence": {
      "status": "degraded",
      "message": "High latency detected",
      "latency_ms": 350
    }
  },
  "version": "1.5.2"
}
```

#### Circuit Breaker Status
```http
GET /api/v1/system/circuit-breakers
```

Returns the status of all circuit breakers in the system.

**Response:**
```json
{
  "status": "success",
  "circuit_breakers": {
    "privacy_engine": {
      "state": "CLOSED", 
      "failure_count": 0,
      "failure_threshold": 5,
      "reset_timeout": 30000,
      "last_failure": null,
      "last_success": "2023-05-15T14:32:12"
    },
    "token_intelligence": {
      "state": "HALF_OPEN",
      "failure_count": 3,
      "failure_threshold": 5,
      "reset_timeout": 30000,
      "last_failure": "2023-05-15T14:28:45",
      "last_success": "2023-05-15T14:31:22"
    }
  }
}
```

#### Reset Circuit Breaker
```http
POST /api/v1/system/circuit-breakers/reset
```

Force resets all circuit breakers or a specific one.

**Request Body:**
```json
{
  "target": "token_intelligence"  // Optional - resets all if omitted
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Circuit breaker reset successful",
  "reset_targets": ["token_intelligence"]
}
```

**Error Responses:**

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | `ValidationError` | Invalid target circuit breaker |
| 500 | `RecoveryError` | Failed to reset circuit breaker |

## Error Handling

All API endpoints follow consistent error response formats:

```json
{
  "status": "error",
  "error": {
    "type": "ContentProcessingError",
    "message": "Failed to parse event time from content",
    "code": "E1003",
    "details": {
      "content_id": "raw-20230515-123456",
      "field": "datetime",
      "reason": "Invalid datetime format"
    }
  }
}
```

### Standard Error Types

| Error Type | Code | Description |
|------------|------|-------------|
| `ValidationError` | E1001 | Request validation failed |
| `NotFoundError` | E1002 | Requested resource not found |
| `ContentProcessingError` | E1003 | Error during content extraction or processing |
| `StorageError` | E1004 | File I/O or storage operations failed |
| `PrivacyError` | E1005 | Privacy-preserving operations failed |
| `SearchError` | E1006 | Search operation failed |
| `ConfigurationError` | E1007 | System configuration issue |
| `RecoveryError` | E1008 | Failed recovery attempt |
| `CircuitBreakerOpenError` | E1009 | Operation rejected due to open circuit breaker |

### HTTP Status Codes

| Status Code | Meaning | Common Error Types |
|-------------|---------|-------------------|
| 400 | Bad Request | ValidationError |
| 404 | Not Found | NotFoundError |
| 422 | Unprocessable Entity | ContentProcessingError |
| 429 | Too Many Requests | CircuitBreakerOpenError |
| 500 | Internal Server Error | StorageError, PrivacyError, ConfigurationError |

## Authentication

API requests require authentication using an API key provided in the `Authorization` header:

```http
Authorization: Bearer YOUR_API_KEY
```

### Key Management

API keys can be generated and managed through:

```http
POST /api/v1/auth/keys
DELETE /api/v1/auth/keys/{key_id}
```

## Rate Limiting

API endpoints are rate limited based on the tier:

| Tier | Rate Limit | Burst Limit |
|------|------------|-------------|
| Free | 100 requests/hour | 15 requests/minute |
| Standard | 1,000 requests/hour | 60 requests/minute |
| Premium | 10,000 requests/hour | 600 requests/minute |

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1684162800
```

## Pagination

List endpoints support pagination using `limit` and `offset` parameters:

```http
GET /api/v1/content/notes?limit=10&offset=20
```

Pagination metadata is included in responses:

```json
{
  "status": "success",
  "items": [...],
  "pagination": {
    "total": 135,
    "limit": 10,
    "offset": 20,
    "next_offset": 30,
    "prev_offset": 10
  }
}
```

## Versioning

The API is versioned in the URL path. The current version is v1:

```http
/api/v1/...
```

## Content-Type

All requests must use `Content-Type: application/json` and responses will be in JSON format. 