#!/usr/bin/env python3
"""
Token Intelligence API Endpoints
Flask routes and API handlers for the Token Intelligence System.
"""

from flask import Flask, request, jsonify
from dataclasses import asdict
from datetime import datetime

from token_intelligence.api.validation import validate_token_request, validate_batch_request
from token_intelligence.core.engine import TokenIntelligenceEngine
from token_intelligence.core.data_models import (
    TokenIntelligenceRequest, 
    TokenIntelligenceResponse,
    BatchTokenRequest,
    BatchTokenResponse
)

# Initialize Flask application
app = Flask(__name__)
engine = TokenIntelligenceEngine()

@app.route('/analyze_privacy_tokens', methods=['POST'])
def analyze_privacy_tokens():
    """
    Main API endpoint for privacy layer integration.
    
    Expected format:
    {
        "privacy_text": "Meeting with [PERSON_001] about [PROJECT_002]",
        "session_id": "uuid",
        "preserved_context": ["meeting", "project"],
        "entity_relationships": {
            "[PERSON_001]": {"type": "person", "linked_entities": ["[PROJECT_002]"]},
            "[PROJECT_002]": {"type": "project", "belongs_to": "[PERSON_001]"}
        }
    }
    
    Returns:
        JSON response with intelligence data, confidence score, and metadata
    """
    try:
        data = request.json
        
        # Validate request data
        validation_result = validate_token_request(data)
        if validation_result:
            return jsonify({
                "intelligence": {},
                "confidence": 0.0,
                "intelligence_type": "error",
                "source": "knowledge_base_analysis",
                "processing_time_ms": 0,
                "error": validation_result
            }), 400
        
        # Create request object
        intelligence_request = TokenIntelligenceRequest(
            privacy_text=data['privacy_text'],
            session_id=data['session_id'],
            preserved_context=data['preserved_context'],
            entity_relationships=data['entity_relationships'],
            metadata=data.get('metadata')
        )
        
        # Generate intelligence
        response = engine.generate_intelligence(intelligence_request)
        
        return jsonify(asdict(response))
        
    except Exception as e:
        return jsonify({
            "intelligence": {},
            "confidence": 0.0,
            "intelligence_type": "error",
            "source": "knowledge_base_analysis",
            "processing_time_ms": 0,
            "error": str(e)
        }), 500

@app.route('/analyze_privacy_tokens_batch', methods=['POST'])
def analyze_privacy_tokens_batch():
    """
    Batch API endpoint for processing multiple token intelligence requests efficiently.
    
    Expected format:
    {
        "requests": [
            {
                "privacy_text": "Meeting with [PERSON_001] about [PROJECT_002]",
                "session_id": "uuid",
                "preserved_context": ["meeting", "project"],
                "entity_relationships": {...}
            },
            {
                "privacy_text": "Call [PHYSICIAN_001] about [CONDITION_001]",
                "session_id": "uuid",
                "preserved_context": ["call", "medical"],
                "entity_relationships": {...}
            }
        ],
        "batch_id": "batch_uuid",
        "session_id": "uuid",
        "metadata": {...}
    }
    
    Returns:
        JSON response with batch results, individual responses, and batch summary
    """
    try:
        data = request.json
        
        # Validate request data
        validation_result = validate_batch_request(data)
        if validation_result:
            return jsonify({
                "responses": [],
                "batch_id": data.get('batch_id', 'unknown'),
                "total_processing_time_ms": 0,
                "batch_size": 0,
                "success_count": 0,
                "error_count": 1,
                "batch_intelligence_summary": {},
                "error": validation_result
            }), 400
        
        # Create individual request objects
        intelligence_requests = []
        for req_data in data['requests']:
            req = TokenIntelligenceRequest(
                privacy_text=req_data['privacy_text'],
                session_id=req_data['session_id'],
                preserved_context=req_data['preserved_context'],
                entity_relationships=req_data['entity_relationships'],
                metadata=req_data.get('metadata')
            )
            intelligence_requests.append(req)
        
        # Create batch request
        batch_request = BatchTokenRequest(
            requests=intelligence_requests,
            batch_id=data['batch_id'],
            session_id=data['session_id'],
            metadata=data.get('metadata')
        )
        
        # Generate batch intelligence
        batch_response = engine.generate_batch_intelligence(batch_request)
        
        return jsonify(asdict(batch_response))
        
    except Exception as e:
        return jsonify({
            "responses": [],
            "batch_id": data.get('batch_id', 'unknown'),
            "total_processing_time_ms": 0,
            "batch_size": 0,
            "success_count": 0,
            "error_count": 1,
            "batch_intelligence_summary": {},
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring system status.
    
    Returns:
        Status information including service name, timestamp, and version
    """
    return jsonify({
        "status": "healthy",
        "service": "token_intelligence_api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

def start_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Start the Flask server with the specified configuration.
    
    Args:
        host: Host address to bind the server to
        port: Port number for the server
        debug: Whether to run in debug mode
    """
    print("🚀 Starting Token Intelligence API...")
    print("🔒 Privacy-preserving intelligence generation ready")
    print("🧠 Token-based analysis engine initialized")
    print("📦 Batch processing endpoint available")
    print("🌐 Endpoints:")
    print("   • POST /analyze_privacy_tokens - Single request processing")
    print("   • POST /analyze_privacy_tokens_batch - Batch processing")
    print("   • GET  /health - Health check")
    app.run(host=host, port=port, debug=debug) 