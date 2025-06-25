# Token Intelligence API Documentation

*Last updated: June 23, 2025*

## Overview

The Token Intelligence System provides a REST API for privacy-preserving token-based intelligence generation. This document outlines the available endpoints, request/response formats, and usage examples.

## Base URL

```
http://localhost:5000
```

For production deployments, replace with your actual server URL.

## Authentication

Authentication is not implemented in the core API but should be added in production deployments.

## Endpoints

### Health Check

**GET /health**

Returns the current status of the API service.

**Response**
```json
{
  "status": "healthy",
  "service": "token_intelligence_api",
  "timestamp": "2025-06-23T14:32:45.123456",
  "version": "1.0.0"
}
```

### Single Request Processing

**POST /analyze_privacy_tokens**

Process a single token intelligence request.

**Request Body**
```json
{
  "privacy_text": "Meeting with [PERSON_001] about [PROJECT_002]",
  "session_id": "uuid-12345",
  "preserved_context": ["meeting", "project", "discussion"],
  "entity_relationships": {
    "[PERSON_001]": {
      "type": "person",
      "linked_entities": ["[PROJECT_002]"]
    },
    "[PROJECT_002]": {
      "type": "project",
      "belongs_to": "[PERSON_001]"
    }
  },
  "metadata": {
    "application": "knowledge_base",
    "user_context": "work"
  }
}
```

**Response**
```json
{
  "intelligence": {
    "PERSON_001_context": "professional colleague, frequent collaborator",
    "PERSON_001_interaction_pattern": "regular work meetings, project discussions",
    "PROJECT_002_status": "active project, requires attention"
  },
  "confidence": 0.85,
  "intelligence_type": "professional_collaboration",
  "source": "knowledge_base_analysis",
  "processing_time_ms": 2
}
```

### Batch Request Processing

**POST /analyze_privacy_tokens_batch**

Process multiple token intelligence requests efficiently in a single call.

**Request Body**
```json
{
  "requests": [
    {
      "privacy_text": "Meeting with [PERSON_001] about [PROJECT_002]",
      "session_id": "uuid-12345",
      "preserved_context": ["meeting", "project"],
      "entity_relationships": {
        "[PERSON_001]": {"type": "person", "linked_entities": ["[PROJECT_002]"]},
        "[PROJECT_002]": {"type": "project", "belongs_to": "[PERSON_001]"}
      }
    },
    {
      "privacy_text": "Call [PHYSICIAN_001] about [CONDITION_001]",
      "session_id": "uuid-12345",
      "preserved_context": ["call", "medical"],
      "entity_relationships": {
        "[PHYSICIAN_001]": {"type": "physician"},
        "[CONDITION_001]": {"type": "condition"}
      }
    }
  ],
  "batch_id": "batch-12345",
  "session_id": "uuid-12345",
  "metadata": {
    "priority": "high",
    "source": "mobile_app"
  }
}
```

**Response**
```json
{
  "responses": [
    {
      "intelligence": {
        "PERSON_001_context": "professional colleague, frequent collaborator",
        "PROJECT_002_status": "active project, requires attention"
      },
      "confidence": 0.85,
      "intelligence_type": "professional_collaboration",
      "source": "knowledge_base_analysis",
      "processing_time_ms": 1
    },
    {
      "intelligence": {
        "PHYSICIAN_001_specialization": "specializes in condition management",
        "PHYSICIAN_001_visit_frequency": "3 visits in past month"
      },
      "confidence": 0.78,
      "intelligence_type": "medical_healthcare",
      "source": "knowledge_base_analysis",
      "processing_time_ms": 2
    }
  ],
  "batch_id": "batch-12345",
  "total_processing_time_ms": 5,
  "batch_size": 2,
  "success_count": 2,
  "error_count": 0,
  "batch_intelligence_summary": {
    "unique_tokens_processed": 4,
    "token_types_seen": ["PERSON", "PROJECT", "PHYSICIAN", "CONDITION"],
    "intelligence_types_generated": ["professional_collaboration", "medical_healthcare"],
    "batch_patterns": {
      "context_diversity": 2
    }
  }
}
```

## Error Responses

**Validation Error**
```json
{
  "intelligence": {},
  "confidence": 0.0,
  "intelligence_type": "error",
  "source": "knowledge_base_analysis",
  "processing_time_ms": 0,
  "error": "Missing required field: preserved_context"
}
```

**Server Error**
```json
{
  "intelligence": {},
  "confidence": 0.0,
  "intelligence_type": "error",
  "source": "knowledge_base_analysis",
  "processing_time_ms": 0,
  "error": "Internal server error"
}
```

## Using the API with Python

```python
import requests
import json

# API endpoint
API_URL = "http://localhost:5000"

# Single request example
def process_single_request():
    request_data = {
        "privacy_text": "Meeting with [PERSON_001] about [PROJECT_002]",
        "session_id": "test-session",
        "preserved_context": ["meeting", "project"],
        "entity_relationships": {
            "[PERSON_001]": {"type": "person", "linked_entities": ["[PROJECT_002]"]},
            "[PROJECT_002]": {"type": "project", "belongs_to": "[PERSON_001]"}
        }
    }
    
    response = requests.post(
        f"{API_URL}/analyze_privacy_tokens", 
        json=request_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("Intelligence:", json.dumps(result["intelligence"], indent=2))
        print(f"Confidence: {result['confidence']}")
        print(f"Type: {result['intelligence_type']}")
        print(f"Processing time: {result['processing_time_ms']}ms")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Batch request example
def process_batch_request():
    batch_data = {
        "requests": [
            {
                "privacy_text": "Meeting with [PERSON_001]",
                "session_id": "batch-test",
                "preserved_context": ["meeting"],
                "entity_relationships": {"[PERSON_001]": {"type": "person"}}
            },
            {
                "privacy_text": "Call [PHYSICIAN_001] about [CONDITION_001]",
                "session_id": "batch-test",
                "preserved_context": ["call", "medical"],
                "entity_relationships": {
                    "[PHYSICIAN_001]": {"type": "physician"},
                    "[CONDITION_001]": {"type": "condition"}
                }
            }
        ],
        "batch_id": "test-batch",
        "session_id": "batch-parent"
    }
    
    response = requests.post(
        f"{API_URL}/analyze_privacy_tokens_batch", 
        json=batch_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Processed {result['batch_size']} requests")
        print(f"Success: {result['success_count']}, Errors: {result['error_count']}")
        print(f"Total processing time: {result['total_processing_time_ms']}ms")
        
        # Print individual responses
        for i, resp in enumerate(result["responses"]):
            print(f"\nResponse {i+1}:")
            print(f"Type: {resp['intelligence_type']}")
            print("Intelligence:", json.dumps(resp["intelligence"], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
```

## Recommended Practices

1. **Maintain Session Consistency**: Use the same session ID for related requests to build intelligence over time.
2. **Preserve Context**: Include relevant keywords in the `preserved_context` field to guide intelligence generation.
3. **Specify Relationships**: Clearly define entity relationships to improve intelligence quality.
4. **Batch Processing**: Use batch processing for multiple related requests to improve efficiency.
5. **Error Handling**: Implement proper error handling in client applications.

## Rate Limiting

The API currently does not implement rate limiting, but production deployments should add appropriate limits. 