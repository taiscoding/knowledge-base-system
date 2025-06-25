#!/usr/bin/env python3
"""
Token Intelligence API
Core API service for processing privacy tokens and generating cross-context intelligence.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from flask import Flask, request, jsonify
from data_intelligence_tracker import PersonalDataIntelligenceTracker
from kb_manager import KnowledgeBaseManager
import re

@dataclass
class TokenIntelligenceRequest:
    """Request format from privacy layer."""
    privacy_text: str
    session_id: str
    preserved_context: List[str]
    entity_relationships: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TokenIntelligenceResponse:
    """Response format to privacy layer."""
    intelligence: Dict[str, str]  # Token-based intelligence only
    confidence: float
    intelligence_type: str
    source: str
    processing_time_ms: int

@dataclass
class BatchTokenRequest:
    """Batch request format for multiple token analyses."""
    requests: List[TokenIntelligenceRequest]
    batch_id: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BatchTokenResponse:
    """Batch response format for multiple token analyses."""
    responses: List[TokenIntelligenceResponse]
    batch_id: str
    total_processing_time_ms: int
    batch_size: int
    success_count: int
    error_count: int
    batch_intelligence_summary: Dict[str, Any]

class TokenIntelligenceEngine:
    """Core engine for generating token-based intelligence."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.tracker = PersonalDataIntelligenceTracker(base_path)
        self.kb_manager = KnowledgeBaseManager(base_path)
        
        # Token intelligence storage
        self.token_profiles = self._load_token_profiles()
        self.token_relationships = self._load_token_relationships()
        self.token_patterns = self._load_token_patterns()
        
    def generate_intelligence(self, request: TokenIntelligenceRequest) -> TokenIntelligenceResponse:
        """
        Generate intelligence from privacy tokens - NEVER uses original data.
        
        Args:
            request: Token intelligence request from privacy layer
            
        Returns:
            Token-based intelligence response
        """
        start_time = time.time()
        
        try:
            # Extract tokens from privacy text
            tokens = self._extract_tokens(request.privacy_text)
            
            # Generate intelligence for each token
            intelligence = {}
            confidence_scores = []
            
            for token in tokens:
                token_intel = self._generate_token_intelligence(
                    token, 
                    request.preserved_context,
                    request.entity_relationships
                )
                
                if token_intel:
                    intelligence.update(token_intel['intelligence'])
                    confidence_scores.append(token_intel['confidence'])
            
            # Determine intelligence type
            intelligence_type = self._classify_intelligence_type(request.privacy_text, intelligence)
            
            # Calculate overall confidence
            confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # Store this intelligence for future use
            self._store_token_intelligence(tokens, intelligence, request)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return TokenIntelligenceResponse(
                intelligence=intelligence,
                confidence=confidence,
                intelligence_type=intelligence_type,
                source="knowledge_base_analysis",
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return TokenIntelligenceResponse(
                intelligence={},
                confidence=0.0,
                intelligence_type="error",
                source="knowledge_base_analysis",
                processing_time_ms=processing_time
            )
    
    def generate_batch_intelligence(self, batch_request: BatchTokenRequest) -> BatchTokenResponse:
        """
        Generate intelligence for multiple requests in batch for improved efficiency.
        
        Args:
            batch_request: Batch of token intelligence requests
            
        Returns:
            Batch response with individual results and summary
        """
        start_time = time.time()
        
        responses = []
        success_count = 0
        error_count = 0
        all_tokens = set()
        all_intelligence_types = []
        
        # Pre-load all unique tokens for batch optimization
        for request in batch_request.requests:
            tokens = self._extract_tokens(request.privacy_text)
            all_tokens.update(tokens)
        
        # Process each request
        for request in batch_request.requests:
            try:
                response = self.generate_intelligence(request)
                responses.append(response)
                
                if response.intelligence_type != "error":
                    success_count += 1
                    all_intelligence_types.append(response.intelligence_type)
                else:
                    error_count += 1
                    
            except Exception as e:
                error_response = TokenIntelligenceResponse(
                    intelligence={},
                    confidence=0.0,
                    intelligence_type="error",
                    source="knowledge_base_analysis",
                    processing_time_ms=0
                )
                responses.append(error_response)
                error_count += 1
        
        # Generate batch summary intelligence
        batch_summary = self._generate_batch_summary(
            all_tokens, all_intelligence_types, batch_request
        )
        
        total_processing_time = int((time.time() - start_time) * 1000)
        
        return BatchTokenResponse(
            responses=responses,
            batch_id=batch_request.batch_id,
            total_processing_time_ms=total_processing_time,
            batch_size=len(batch_request.requests),
            success_count=success_count,
            error_count=error_count,
            batch_intelligence_summary=batch_summary
        )
    
    def _generate_batch_summary(self, all_tokens: set, intelligence_types: List[str], batch_request: BatchTokenRequest) -> Dict[str, Any]:
        """Generate summary intelligence across the batch."""
        summary = {
            "unique_tokens_processed": len(all_tokens),
            "token_types_seen": list(set(token.split('_')[0] for token in all_tokens)),
            "intelligence_types_generated": list(set(intelligence_types)),
            "batch_patterns": {}
        }
        
        # Detect cross-request patterns
        if len(intelligence_types) > 1:
            type_counts = {}
            for intel_type in intelligence_types:
                type_counts[intel_type] = type_counts.get(intel_type, 0) + 1
            
            summary["batch_patterns"]["dominant_context"] = max(type_counts, key=type_counts.get)
            summary["batch_patterns"]["context_diversity"] = len(type_counts)
        
        # Token relationship analysis across batch
        person_tokens = [t for t in all_tokens if t.startswith('PERSON')]
        medical_tokens = [t for t in all_tokens if t.startswith('PHYSICIAN') or t.startswith('CONDITION')]
        
        if person_tokens and medical_tokens:
            summary["batch_patterns"]["cross_domain_relationships"] = "healthcare_personal_mixed"
        elif len(person_tokens) > 1:
            summary["batch_patterns"]["social_network_detected"] = f"{len(person_tokens)} people involved"
            
        return summary
    
    def _extract_tokens(self, privacy_text: str) -> List[str]:
        """Extract privacy tokens from text."""
        token_pattern = r'\[([A-Z_]+(?:_\d+)?)\]'
        return re.findall(token_pattern, privacy_text)
    
    def _generate_token_intelligence(self, token: str, context: List[str], relationships: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate specific intelligence for a token."""
        
        # Check existing token profile
        token_profile = self.token_profiles.get(token, {})
        
        intelligence = {}
        
        # Personal Knowledge Management Intelligence
        if token.startswith('PERSON'):
            intelligence = self._generate_person_intelligence(token, context, token_profile)
        elif token.startswith('PHONE'):
            intelligence = self._generate_contact_intelligence(token, context, token_profile)
        elif token.startswith('DOCUMENT'):
            intelligence = self._generate_document_intelligence(token, context, token_profile)
        elif token.startswith('PROJECT'):
            intelligence = self._generate_project_intelligence(token, context, token_profile)
        elif token.startswith('PHYSICIAN') or token.startswith('DOCTOR'):
            intelligence = self._generate_medical_intelligence(token, context, token_profile)
        elif token.startswith('CONDITION') or token.startswith('MEDICATION'):
            intelligence = self._generate_health_intelligence(token, context, token_profile)
        
        if intelligence:
            return {
                'intelligence': intelligence,
                'confidence': self._calculate_confidence(intelligence, token_profile)
            }
        
        return None
    
    def _generate_person_intelligence(self, token: str, context: List[str], profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate intelligence for person tokens."""
        intelligence = {}
        
        # Professional context
        if any(word in context for word in ['meeting', 'work', 'project', 'colleague']):
            intelligence[f"{token}_context"] = "professional colleague, frequent collaborator"
            intelligence[f"{token}_interaction_pattern"] = "regular work meetings, project discussions"
            
        # Academic context  
        if any(word in context for word in ['paper', 'research', 'study', 'academic']):
            intelligence[f"{token}_context"] = "academic collaborator, research colleague"
            intelligence[f"{token}_expertise"] = "machine learning research, paper recommendations"
            
        # Social context
        if any(word in context for word in ['lunch', 'dinner', 'social', 'friend']):
            intelligence[f"{token}_context"] = "close friend, regular social contact"
            intelligence[f"{token}_preferences"] = "prefers quiet restaurants, reliable for social plans"
            
        # Communication patterns from profile
        if profile.get('communication_frequency') == 'high':
            intelligence[f"{token}_patterns"] = "frequent communication, prefers quick responses"
            
        return intelligence
    
    def _generate_medical_intelligence(self, token: str, context: List[str], profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate intelligence for medical provider tokens."""
        intelligence = {}
        
        # Get visit patterns from tracker
        visit_pattern = self.tracker._get_provider_visit_pattern(f"[{token}]", days=30)
        if visit_pattern:
            intelligence[f"{token}_visit_frequency"] = f"{visit_pattern['count']} visits in past month"
            intelligence[f"{token}_relationship"] = "established healthcare provider, ongoing care"
            
        # Medical context intelligence
        if any(word in context for word in ['blood pressure', 'hypertension', 'bp']):
            intelligence[f"{token}_specialization"] = "hypertension management, cardiovascular care"
            intelligence[f"{token}_monitoring_style"] = "prefers regular monitoring, data-driven approach"
            
        if any(word in context for word in ['diabetes', 'glucose', 'blood sugar']):
            intelligence[f"{token}_specialization"] = "diabetes management, endocrine care"
            
        return intelligence
    
    def _generate_health_intelligence(self, token: str, context: List[str], profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate intelligence for health condition/medication tokens."""
        intelligence = {}
        
        # Get recent measurements for conditions
        if token.startswith('CONDITION'):
            measurements = self._get_condition_measurements(context)
            if measurements:
                intelligence[f"{token}_recent_data"] = f"recent readings show improvement trend"
                intelligence[f"{token}_monitoring_available"] = "home monitoring equipment available"
                
        return intelligence
    
    def _get_condition_measurements(self, context: List[str]) -> List[Dict]:
        """Get recent measurements related to health context."""
        if any(word in context for word in ['blood pressure', 'bp']):
            return self.tracker._get_recent_measurements("blood_pressure", days=30)
        elif any(word in context for word in ['temperature', 'fever']):
            return self.tracker._get_recent_measurements("temperature", days=7)
        elif any(word in context for word in ['weight']):
            return self.tracker._get_recent_measurements("weight", days=30)
        return []
    
    def _generate_contact_intelligence(self, token: str, context: List[str], profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate intelligence for contact tokens."""
        intelligence = {}
        
        # Phone number context
        if any(word in context for word in ['call', 'urgent', 'emergency']):
            intelligence[f"{token}_usage"] = "emergency contact, urgent communications"
        elif any(word in context for word in ['work', 'office']):
            intelligence[f"{token}_usage"] = "professional contact, business hours"
        else:
            intelligence[f"{token}_usage"] = "personal contact, flexible timing"
            
        return intelligence
    
    def _generate_document_intelligence(self, token: str, context: List[str], profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate intelligence for document tokens."""
        intelligence = {}
        
        if any(word in context for word in ['paper', 'research']):
            intelligence[f"{token}_type"] = "academic paper, research document"
            intelligence[f"{token}_relevance"] = "high relevance to current research interests"
        elif any(word in context for word in ['report', 'analysis']):
            intelligence[f"{token}_type"] = "business document, analytical content"
            
        return intelligence
    
    def _generate_project_intelligence(self, token: str, context: List[str], profile: Dict[str, Any]) -> Dict[str, str]:
        """Generate intelligence for project tokens."""
        intelligence = {}
        
        if any(word in context for word in ['deadline', 'urgent']):
            intelligence[f"{token}_status"] = "time-sensitive project, requires immediate attention"
        elif any(word in context for word in ['collaborative', 'team']):
            intelligence[f"{token}_type"] = "team project, multiple stakeholders involved"
            
        return intelligence
    
    def _classify_intelligence_type(self, privacy_text: str, intelligence: Dict[str, str]) -> str:
        """Classify the type of intelligence generated."""
        if any('visit_frequency' in key for key in intelligence.keys()):
            return "medical_healthcare"
        elif any('_context' in key and 'colleague' in value for key, value in intelligence.items()):
            return "professional_collaboration"
        elif any('paper' in privacy_text.lower() or 'research' in privacy_text.lower()):
            return "academic_research"
        elif any('lunch' in privacy_text.lower() or 'dinner' in privacy_text.lower()):
            return "social_dining"
        else:
            return "general_personal_knowledge"
    
    def _calculate_confidence(self, intelligence: Dict[str, str], profile: Dict[str, Any]) -> float:
        """Calculate confidence score for intelligence."""
        base_confidence = 0.7
        
        # Increase confidence if we have historical data
        if profile:
            base_confidence += 0.2
            
        # Increase confidence based on intelligence richness
        if len(intelligence) > 2:
            base_confidence += 0.1
            
        return min(base_confidence, 1.0)
    
    def _store_token_intelligence(self, tokens: List[str], intelligence: Dict[str, str], request: TokenIntelligenceRequest):
        """Store generated intelligence for future use."""
        for token in tokens:
            if token not in self.token_profiles:
                self.token_profiles[token] = {
                    'created': datetime.now().isoformat(),
                    'interactions': 0,
                    'contexts_seen': set()
                }
            
            # Update interaction count and contexts
            profile = self.token_profiles[token]
            profile['interactions'] += 1
            profile['contexts_seen'].update(request.preserved_context)
            profile['last_seen'] = datetime.now().isoformat()
            
            # Store intelligence permanently
            token_key = f"{token}_intelligence"
            if token_key not in profile:
                profile[token_key] = {}
            
            # Update with new intelligence
            for key, value in intelligence.items():
                if key.startswith(token):
                    profile[token_key][key] = value
        
        self._save_token_profiles()
    
    def _load_token_profiles(self) -> Dict[str, Any]:
        """Load token profiles from storage."""
        profiles_file = self.base_path / "data" / "intelligence" / "token_profiles.json"
        if profiles_file.exists():
            with open(profiles_file, 'r') as f:
                data = json.load(f)
                # Convert sets back from lists
                for profile in data.values():
                    if 'contexts_seen' in profile and isinstance(profile['contexts_seen'], list):
                        profile['contexts_seen'] = set(profile['contexts_seen'])
                return data
        return {}
    
    def _save_token_profiles(self):
        """Save token profiles to storage."""
        profiles_file = self.base_path / "data" / "intelligence" / "token_profiles.json"
        profiles_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert sets to lists for JSON serialization
        serializable_profiles = {}
        for token, profile in self.token_profiles.items():
            serializable_profile = profile.copy()
            if 'contexts_seen' in serializable_profile:
                serializable_profile['contexts_seen'] = list(serializable_profile['contexts_seen'])
            serializable_profiles[token] = serializable_profile
        
        with open(profiles_file, 'w') as f:
            json.dump(serializable_profiles, f, indent=2)
    
    def _load_token_relationships(self) -> Dict[str, Any]:
        """Load token relationships from storage."""
        relationships_file = self.base_path / "data" / "intelligence" / "token_relationships.json"
        if relationships_file.exists():
            with open(relationships_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_token_patterns(self) -> Dict[str, Any]:
        """Load token patterns from storage."""
        patterns_file = self.base_path / "data" / "intelligence" / "token_patterns.json"
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                return json.load(f)
        return {}

# Flask API Setup
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
    """
    try:
        data = request.json
        
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
    """
    try:
        data = request.json
        
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
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "token_intelligence_api",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("🚀 Starting Token Intelligence API...")
    print("🔒 Privacy-preserving intelligence generation ready")
    print("🧠 Token-based analysis engine initialized")
    print("📦 Batch processing endpoint available")
    print("🌐 Endpoints:")
    print("   • POST /analyze_privacy_tokens - Single request processing")
    print("   • POST /analyze_privacy_tokens_batch - Batch processing")
    print("   • GET  /health - Health check")
    app.run(host='0.0.0.0', port=5000, debug=False) 