#!/usr/bin/env python3
"""
Tests for the token_intelligence.core module.
"""

import unittest
import time
from datetime import datetime

from token_intelligence.core import (
    TokenIntelligenceEngine,
    TokenIntelligenceRequest,
    TokenIntelligenceResponse,
    extract_tokens
)


class TestTokenExtractor(unittest.TestCase):
    """Tests for the token extractor functionality."""
    
    def test_extract_tokens(self):
        """Test token extraction from privacy text."""
        # Test basic token extraction
        text = "Meeting with [PERSON_001] about [PROJECT_002]"
        tokens = extract_tokens(text)
        self.assertEqual(tokens, ["PERSON_001", "PROJECT_002"])
        
        # Test with no tokens
        text = "Regular text without any tokens"
        tokens = extract_tokens(text)
        self.assertEqual(tokens, [])
        
        # Test with mixed tokens
        text = "[PERSON_001] has [CONDITION] and sees [PHYSICIAN]"
        tokens = extract_tokens(text)
        self.assertEqual(tokens, ["PERSON_001", "CONDITION", "PHYSICIAN"])


class TestTokenIntelligenceEngine(unittest.TestCase):
    """Tests for the TokenIntelligenceEngine class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.engine = TokenIntelligenceEngine()
    
    def test_generate_intelligence(self):
        """Test intelligence generation for privacy tokens."""
        # Create a test request
        request = TokenIntelligenceRequest(
            privacy_text="Meeting with [PERSON_001] about [PROJECT_002]",
            session_id="test-session",
            preserved_context=["meeting", "project", "work"],
            entity_relationships={
                "[PERSON_001]": {"type": "person", "linked_entities": ["[PROJECT_002]"]},
                "[PROJECT_002]": {"type": "project", "belongs_to": "[PERSON_001]"}
            }
        )
        
        # Generate intelligence
        response = self.engine.generate_intelligence(request)
        
        # Verify response structure
        self.assertIsInstance(response, TokenIntelligenceResponse)
        self.assertIsInstance(response.intelligence, dict)
        self.assertIsInstance(response.confidence, float)
        self.assertIsInstance(response.intelligence_type, str)
        self.assertIsInstance(response.processing_time_ms, int)
        
        # Verify intelligence content - should have some entries for PERSON_001 and/or PROJECT_002
        has_person_intelligence = any(key.startswith("PERSON_001") for key in response.intelligence.keys())
        has_project_intelligence = any(key.startswith("PROJECT_002") for key in response.intelligence.keys())
        
        self.assertTrue(has_person_intelligence or has_project_intelligence)
        
        # Verify performance requirement - should be fast
        self.assertLess(response.processing_time_ms, 100, "Intelligence generation took too long")
    
    def test_medical_intelligence(self):
        """Test medical intelligence generation."""
        # Create a test request with medical tokens
        request = TokenIntelligenceRequest(
            privacy_text="Call [PHYSICIAN_001] about [CONDITION_001]",
            session_id="test-medical",
            preserved_context=["call", "doctor", "medical", "blood pressure"],
            entity_relationships={
                "[PHYSICIAN_001]": {"type": "physician"},
                "[CONDITION_001]": {"type": "condition"}
            }
        )
        
        # Generate intelligence
        response = self.engine.generate_intelligence(request)
        
        # Verify medical intelligence type
        self.assertEqual(response.intelligence_type, "medical_healthcare")
        
        # Verify some medical intelligence was generated
        has_physician_intel = any(key.startswith("PHYSICIAN_001") for key in response.intelligence.keys())
        self.assertTrue(has_physician_intel)


class TestBatchProcessing(unittest.TestCase):
    """Tests for batch processing functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        self.engine = TokenIntelligenceEngine()
    
    def test_batch_intelligence(self):
        """Test batch processing of multiple requests."""
        from token_intelligence.core import BatchTokenRequest
        
        # Create individual requests
        request1 = TokenIntelligenceRequest(
            privacy_text="Meeting with [PERSON_001]",
            session_id="batch-test-1",
            preserved_context=["meeting", "work"],
            entity_relationships={"[PERSON_001]": {"type": "person"}}
        )
        
        request2 = TokenIntelligenceRequest(
            privacy_text="Call [PHYSICIAN_001] about [CONDITION_001]",
            session_id="batch-test-2",
            preserved_context=["call", "medical"],
            entity_relationships={
                "[PHYSICIAN_001]": {"type": "physician"},
                "[CONDITION_001]": {"type": "condition"}
            }
        )
        
        # Create batch request
        batch_request = BatchTokenRequest(
            requests=[request1, request2],
            batch_id="test-batch",
            session_id="batch-parent"
        )
        
        # Process batch
        batch_response = self.engine.generate_batch_intelligence(batch_request)
        
        # Verify batch response
        self.assertEqual(len(batch_response.responses), 2)
        self.assertEqual(batch_response.batch_size, 2)
        self.assertEqual(batch_response.success_count, 2)
        self.assertEqual(batch_response.error_count, 0)
        
        # Verify batch summary
        self.assertIn("unique_tokens_processed", batch_response.batch_intelligence_summary)
        self.assertIn("token_types_seen", batch_response.batch_intelligence_summary)
        self.assertIn("intelligence_types_generated", batch_response.batch_intelligence_summary)


if __name__ == "__main__":
    unittest.main() 