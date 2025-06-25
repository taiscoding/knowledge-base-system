#!/usr/bin/env python3
"""
Tests for the token_intelligence.api module.
"""

import unittest
import json
from flask import Flask
from flask.testing import FlaskClient

from token_intelligence.api import app
from token_intelligence.core import TokenIntelligenceRequest


class TestAPIEndpoints(unittest.TestCase):
    """Tests for the API endpoints."""
    
    def setUp(self):
        """Set up the test environment."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.app.get('/health')
        
        # Verify response code
        self.assertEqual(response.status_code, 200)
        
        # Verify response content
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('service', data)
        self.assertIn('timestamp', data)
    
    def test_analyze_tokens_endpoint(self):
        """Test the analyze_privacy_tokens endpoint."""
        # Create test request data
        request_data = {
            'privacy_text': 'Meeting with [PERSON_001] about [PROJECT_002]',
            'session_id': 'test-api-session',
            'preserved_context': ['meeting', 'project'],
            'entity_relationships': {
                '[PERSON_001]': {'type': 'person', 'linked_entities': ['[PROJECT_002]']},
                '[PROJECT_002]': {'type': 'project', 'belongs_to': '[PERSON_001]'}
            }
        }
        
        # Send the request
        response = self.app.post('/analyze_privacy_tokens', 
                                json=request_data,
                                content_type='application/json')
        
        # Verify response code
        self.assertEqual(response.status_code, 200)
        
        # Verify response structure
        data = json.loads(response.data)
        self.assertIn('intelligence', data)
        self.assertIn('confidence', data)
        self.assertIn('intelligence_type', data)
        self.assertIn('source', data)
        self.assertIn('processing_time_ms', data)
        
        # Verify the response contains some intelligence
        self.assertTrue(len(data['intelligence']) > 0)
    
    def test_batch_endpoint(self):
        """Test the analyze_privacy_tokens_batch endpoint."""
        # Create batch request data
        batch_request = {
            'requests': [
                {
                    'privacy_text': 'Meeting with [PERSON_001]',
                    'session_id': 'batch-test-1',
                    'preserved_context': ['meeting', 'work'],
                    'entity_relationships': {'[PERSON_001]': {'type': 'person'}}
                },
                {
                    'privacy_text': 'Call [PHYSICIAN_001] about [CONDITION_001]',
                    'session_id': 'batch-test-2',
                    'preserved_context': ['call', 'medical'],
                    'entity_relationships': {
                        '[PHYSICIAN_001]': {'type': 'physician'},
                        '[CONDITION_001]': {'type': 'condition'}
                    }
                }
            ],
            'batch_id': 'test-api-batch',
            'session_id': 'api-batch-parent'
        }
        
        # Send the request
        response = self.app.post('/analyze_privacy_tokens_batch', 
                                json=batch_request,
                                content_type='application/json')
        
        # Verify response code
        self.assertEqual(response.status_code, 200)
        
        # Verify batch response structure
        data = json.loads(response.data)
        self.assertIn('responses', data)
        self.assertEqual(len(data['responses']), 2)
        self.assertIn('batch_id', data)
        self.assertIn('total_processing_time_ms', data)
        self.assertIn('batch_size', data)
        self.assertIn('success_count', data)
        self.assertIn('error_count', data)
        self.assertIn('batch_intelligence_summary', data)
    
    def test_validation_error(self):
        """Test validation error handling."""
        # Create invalid request (missing required fields)
        invalid_request = {
            'privacy_text': 'Meeting with [PERSON_001]'
            # Missing session_id, preserved_context, entity_relationships
        }
        
        # Send the request
        response = self.app.post('/analyze_privacy_tokens', 
                                json=invalid_request,
                                content_type='application/json')
        
        # Verify response code (should be 400 Bad Request)
        self.assertEqual(response.status_code, 400)
        
        # Verify error message is present
        data = json.loads(response.data)
        self.assertIn('error', data)


if __name__ == "__main__":
    unittest.main() 