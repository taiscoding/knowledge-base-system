#!/usr/bin/env python3
"""
Knowledge Base & Token Intelligence System - Combined Usage Example
Shows how to use both the knowledge base and token intelligence system with privacy integration.
"""

from knowledge_base import KnowledgeBaseManager
from knowledge_base.privacy import PrivacyIntegration
from token_intelligence import TokenIntelligenceEngine, TokenIntelligenceRequest


def privacy_enhanced_workflow():
    """Example of a privacy-enhanced workflow using both systems."""
    print("=========================================")
    print("Privacy-Enhanced Knowledge Base Workflow")
    print("=========================================")

    # Initialize components
    kb = KnowledgeBaseManager()
    privacy_integration = PrivacyIntegration(kb)
    engine = TokenIntelligenceEngine()

    print("\n1. Adding content through stream of consciousness...")
    # Normally we would want to use Sankofa to tokenize this first
    # But for this example, we'll manually create the tokenized version
    original_content = """
    Need to meet with Dr. Smith about my diabetes management plan tomorrow at 2pm.
    Also need to finish the quarterly report for John in Marketing.
    """
    
    print("Original content (would be tokenized by Sankofa):")
    print(original_content)
    
    # This would be done by Sankofa in a real implementation
    tokenized_content = """
    Need to meet with [PHYSICIAN_001] about my [CONDITION_001] management plan tomorrow at 2pm.
    Also need to finish the quarterly report for [PERSON_001] in Marketing.
    """
    
    print("\nTokenized content (after Sankofa processing):")
    print(tokenized_content)
    
    # Process the tokenized content
    result = kb.process_stream_of_consciousness(tokenized_content)
    
    print("\n2. Extracted items from tokenized content:")
    print(f"  • {len(result['extracted_info']['todos'])} todos")
    print(f"  • {len(result['extracted_info']['calendar_events'])} calendar events")
    print(f"  • Tags: {result['extracted_info']['tags']}")
    
    print("\n3. Generating token intelligence...")
    # Create a token intelligence request
    request = TokenIntelligenceRequest(
        privacy_text="Meeting with [PHYSICIAN_001] about [CONDITION_001]",
        session_id="example-session-001",
        preserved_context=["management", "plan", "quarterly"],
        entity_relationships={
            "[PHYSICIAN_001]": {"type": "physician", "specialty": "endocrinology"},
            "[CONDITION_001]": {"type": "condition", "category": "chronic"}
        }
    )
    
    # Generate intelligence
    response = engine.generate_intelligence(request)
    
    print("\n4. Token Intelligence Results:")
    print(f"  • Intelligence Type: {response.intelligence_type}")
    print(f"  • Confidence: {response.confidence:.2f}")
    print("  • Intelligence:")
    for key, value in response.intelligence.items():
        print(f"    - {key}: {value}")
    
    print("\n5. Cross-domain intelligence request...")
    # Create a second request that combines both contexts
    cross_request = TokenIntelligenceRequest(
        privacy_text="Need [PERSON_001] to review report on [CONDITION_001] stats",
        session_id="example-session-001",  # Same session for continuity
        preserved_context=["report", "quarterly", "review", "management"],
        entity_relationships={
            "[PERSON_001]": {"type": "person", "department": "marketing"},
            "[CONDITION_001]": {"type": "condition", "category": "chronic"}
        }
    )
    
    # Generate cross-domain intelligence
    cross_response = engine.generate_intelligence(cross_request)
    
    print("\n6. Cross-Domain Results:")
    print(f"  • Intelligence Type: {cross_response.intelligence_type}")
    print(f"  • Confidence: {cross_response.confidence:.2f}")
    print("  • Intelligence:")
    for key, value in cross_response.intelligence.items():
        print(f"    - {key}: {value}")
    
    print("\n7. Searching for content...")
    search_results = kb.search_content("quarterly")
    
    print(f"\n8. Found {len(search_results)} items matching 'quarterly':")
    for i, result in enumerate(search_results):
        print(f"  • Result {i+1}: {result['type']} - {result['file']}")
        print(f"    {result['content_preview'][:50]}...")
    
    print("\n9. Exporting to privacy bundle...")
    # In a real implementation, this would properly anonymize all content
    export_result = privacy_integration.export_to_privacy_bundle()
    
    print("\n10. Privacy export results:")
    if export_result.get("success"):
        print(f"  ✓ Successfully exported to {export_result.get('bundle_path')}")
        print(f"  ✓ Exported {export_result.get('items_exported')} items")
    else:
        print(f"  ✗ Export failed: {export_result.get('error')}")
    
    print("\nWorkflow completed successfully!")


if __name__ == "__main__":
    print("Knowledge Base & Token Intelligence - Combined Example")
    print("----------------------------------------------------")
    privacy_enhanced_workflow() 