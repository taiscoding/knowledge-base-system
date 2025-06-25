#!/usr/bin/env python3
"""
Token Intelligence System - API Client Example
Demonstrates how to interact with the Token Intelligence API from a client application.
"""

import json
import requests
import sys
from typing import Dict, Any, List


class TokenIntelligenceClient:
    """Client for interacting with the Token Intelligence API."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the Token Intelligence API server
        """
        self.base_url = base_url
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check the health of the API server.
        
        Returns:
            Dictionary with health status information
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()  # Raise exception for error status codes
        return response.json()
    
    def analyze_tokens(self, 
                      privacy_text: str, 
                      preserved_context: List[str],
                      entity_relationships: Dict[str, Any],
                      session_id: str = "default-session",
                      metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a single token intelligence request.
        
        Args:
            privacy_text: Text containing privacy tokens
            preserved_context: List of context keywords
            entity_relationships: Dictionary mapping entities to their relationships
            session_id: Session identifier
            metadata: Optional additional metadata
            
        Returns:
            Dictionary containing the intelligence response
        """
        request_data = {
            "privacy_text": privacy_text,
            "session_id": session_id,
            "preserved_context": preserved_context,
            "entity_relationships": entity_relationships
        }
        
        if metadata:
            request_data["metadata"] = metadata
        
        response = requests.post(
            f"{self.base_url}/analyze_privacy_tokens",
            json=request_data
        )
        
        response.raise_for_status()
        return response.json()
    
    def analyze_batch(self, 
                     requests: List[Dict[str, Any]],
                     batch_id: str,
                     session_id: str,
                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a batch of token intelligence requests.
        
        Args:
            requests: List of request dictionaries
            batch_id: Unique identifier for the batch
            session_id: Session identifier
            metadata: Optional additional metadata
            
        Returns:
            Dictionary containing the batch response
        """
        batch_data = {
            "requests": requests,
            "batch_id": batch_id,
            "session_id": session_id
        }
        
        if metadata:
            batch_data["metadata"] = metadata
        
        response = requests.post(
            f"{self.base_url}/analyze_privacy_tokens_batch",
            json=batch_data
        )
        
        response.raise_for_status()
        return response.json()


def format_intelligence(intelligence: Dict[str, str]) -> str:
    """Format intelligence dictionary for display."""
    result = []
    for key, value in intelligence.items():
        result.append(f"  • {key}: {value}")
    return "\n".join(result)


def run_examples():
    """Run example API client interactions."""
    client = TokenIntelligenceClient()
    
    # Check server health
    try:
        health = client.check_health()
        print("\n=== API Server Health ===")
        print(f"Status: {health['status']}")
        print(f"Service: {health['service']}")
        print(f"Timestamp: {health['timestamp']}")
        if 'version' in health:
            print(f"Version: {health['version']}")
    except requests.RequestException as e:
        print(f"Error checking server health: {e}")
        print("Please make sure the Token Intelligence API server is running.")
        return
    
    # Single request example
    try:
        print("\n=== Single Request Example ===")
        response = client.analyze_tokens(
            privacy_text="Meeting with [PERSON_001] about [PROJECT_002] deadline",
            preserved_context=["meeting", "project", "deadline"],
            entity_relationships={
                "[PERSON_001]": {"type": "person", "linked_entities": ["[PROJECT_002]"]},
                "[PROJECT_002]": {"type": "project", "belongs_to": "[PERSON_001]"}
            },
            session_id="api-client-example"
        )
        
        print(f"Intelligence Type: {response['intelligence_type']}")
        print(f"Confidence: {response['confidence']:.2f}")
        print("Intelligence:")
        print(format_intelligence(response['intelligence']))
        print(f"Processing Time: {response['processing_time_ms']}ms")
    except requests.RequestException as e:
        print(f"Error processing single request: {e}")
    
    # Batch request example
    try:
        print("\n=== Batch Request Example ===")
        
        batch_requests = [
            {
                "privacy_text": "Meeting with [PERSON_001] about project updates",
                "session_id": "api-client-example",
                "preserved_context": ["meeting", "project", "updates"],
                "entity_relationships": {"[PERSON_001]": {"type": "person"}}
            },
            {
                "privacy_text": "Call [PHYSICIAN_001] about [CONDITION_001]",
                "session_id": "api-client-example",
                "preserved_context": ["call", "medical"],
                "entity_relationships": {
                    "[PHYSICIAN_001]": {"type": "physician"},
                    "[CONDITION_001]": {"type": "condition"}
                }
            }
        ]
        
        batch_response = client.analyze_batch(
            requests=batch_requests,
            batch_id="api-client-batch-example",
            session_id="api-client-example",
            metadata={"source": "api_client_example"}
        )
        
        print(f"Batch Size: {batch_response['batch_size']}")
        print(f"Success: {batch_response['success_count']}, Errors: {batch_response['error_count']}")
        print(f"Total Processing Time: {batch_response['total_processing_time_ms']}ms")
        
        print("\nIndividual Responses:")
        for i, response in enumerate(batch_response['responses']):
            print(f"\nResponse {i+1} - {response['intelligence_type']}:")
            print(f"  Confidence: {response['confidence']:.2f}")
            print("  Intelligence:")
            print(format_intelligence(response['intelligence']))
            
    except requests.RequestException as e:
        print(f"Error processing batch request: {e}")


if __name__ == "__main__":
    print("Token Intelligence System - API Client Example")
    print("---------------------------------------------")
    
    run_examples()
    
    print("\nExample completed!") 