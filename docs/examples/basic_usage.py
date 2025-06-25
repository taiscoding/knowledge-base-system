#!/usr/bin/env python3
"""
Token Intelligence System - Basic Usage Example
Demonstrates how to use the Token Intelligence System as a library.
"""

from token_intelligence import (
    TokenIntelligenceEngine,
    TokenIntelligenceRequest,
    TokenIntelligenceResponse
)


def basic_example():
    """Basic example of token intelligence processing."""
    # Initialize the engine
    engine = TokenIntelligenceEngine()
    
    # Create a request for professional context
    request = TokenIntelligenceRequest(
        privacy_text="Meeting with [PERSON_001] about [PROJECT_002] deadlines",
        session_id="example-session-001",
        preserved_context=["meeting", "project", "deadlines"],
        entity_relationships={
            "[PERSON_001]": {"type": "person", "linked_entities": ["[PROJECT_002]"]},
            "[PROJECT_002]": {"type": "project", "belongs_to": "[PERSON_001]"}
        }
    )
    
    # Generate intelligence
    response = engine.generate_intelligence(request)
    
    # Display results
    print("\n=== Professional Context Example ===")
    print(f"Intelligence Type: {response.intelligence_type}")
    print(f"Confidence: {response.confidence:.2f}")
    print("Intelligence:")
    for key, value in response.intelligence.items():
        print(f"  • {key}: {value}")
    print(f"Processing Time: {response.processing_time_ms}ms\n")
    
    # Create a request for medical context
    medical_request = TokenIntelligenceRequest(
        privacy_text="Call [PHYSICIAN_001] about [CONDITION_001] monitoring",
        session_id="example-session-001",
        preserved_context=["call", "medical", "monitoring", "blood pressure"],
        entity_relationships={
            "[PHYSICIAN_001]": {"type": "physician"},
            "[CONDITION_001]": {"type": "condition"}
        }
    )
    
    # Generate intelligence
    medical_response = engine.generate_intelligence(medical_request)
    
    # Display results
    print("=== Medical Context Example ===")
    print(f"Intelligence Type: {medical_response.intelligence_type}")
    print(f"Confidence: {medical_response.confidence:.2f}")
    print("Intelligence:")
    for key, value in medical_response.intelligence.items():
        print(f"  • {key}: {value}")
    print(f"Processing Time: {medical_response.processing_time_ms}ms")


def batch_example():
    """Example of batch processing."""
    from token_intelligence import BatchTokenRequest
    
    # Initialize the engine
    engine = TokenIntelligenceEngine()
    
    # Create individual requests
    request1 = TokenIntelligenceRequest(
        privacy_text="Meeting with [PERSON_001] about project updates",
        session_id="batch-example-session",
        preserved_context=["meeting", "project", "updates"],
        entity_relationships={"[PERSON_001]": {"type": "person"}}
    )
    
    request2 = TokenIntelligenceRequest(
        privacy_text="Call [PHYSICIAN_001] about [CONDITION_001]",
        session_id="batch-example-session",
        preserved_context=["call", "medical"],
        entity_relationships={
            "[PHYSICIAN_001]": {"type": "physician"},
            "[CONDITION_001]": {"type": "condition"}
        }
    )
    
    request3 = TokenIntelligenceRequest(
        privacy_text="Review [DOCUMENT_001] from [PERSON_002]",
        session_id="batch-example-session",
        preserved_context=["review", "document"],
        entity_relationships={
            "[DOCUMENT_001]": {"type": "document", "belongs_to": "[PERSON_002]"},
            "[PERSON_002]": {"type": "person"}
        }
    )
    
    # Create batch request
    batch_request = BatchTokenRequest(
        requests=[request1, request2, request3],
        batch_id="example-batch-001",
        session_id="batch-example-session"
    )
    
    # Process batch
    batch_response = engine.generate_batch_intelligence(batch_request)
    
    # Display results
    print("\n=== Batch Processing Example ===")
    print(f"Batch Size: {batch_response.batch_size}")
    print(f"Success: {batch_response.success_count}, Errors: {batch_response.error_count}")
    print(f"Total Processing Time: {batch_response.total_processing_time_ms}ms")
    print("\nBatch Intelligence Summary:")
    for key, value in batch_response.batch_intelligence_summary.items():
        if isinstance(value, dict):
            print(f"  • {key}:")
            for subkey, subvalue in value.items():
                print(f"    - {subkey}: {subvalue}")
        else:
            print(f"  • {key}: {value}")
    
    print("\nIndividual Responses:")
    for i, response in enumerate(batch_response.responses):
        print(f"\nResponse {i+1} - {response.intelligence_type}:")
        print(f"  Confidence: {response.confidence:.2f}")
        print("  Intelligence:")
        for key, value in response.intelligence.items():
            print(f"    • {key}: {value}")


if __name__ == "__main__":
    print("Token Intelligence System - Basic Usage Example")
    print("----------------------------------------------")
    basic_example()
    batch_example()
    print("\nExample completed successfully!") 