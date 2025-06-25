#!/usr/bin/env python3
"""
Token Intelligence Engine
Core engine for generating token-based intelligence.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from token_intelligence.core.data_models import (
    TokenIntelligenceRequest,
    TokenIntelligenceResponse,
    BatchTokenRequest,
    BatchTokenResponse
)
from token_intelligence.core.token_extractor import extract_tokens
from token_intelligence.intelligence.generators import (
    generate_person_intelligence,
    generate_medical_intelligence,
    generate_health_intelligence,
    generate_contact_intelligence,
    generate_document_intelligence,
    generate_project_intelligence
)
from token_intelligence.storage.profiles import TokenProfileManager
from token_intelligence.utils.logging import get_logger
# Removed circular import: from token_intelligence.api.batch_handler import BatchProcessor

# Mock these dependencies for testing purposes
class PersonalDataIntelligenceTracker:
    def __init__(self, base_path):
        self.base_path = base_path
        
    def _get_provider_visit_pattern(self, provider_token, days=30):
        return {
            "count": 2,
            "visit_frequency": "monthly",
            "last_visit_days_ago": 30,
            "visit_regularity": "consistent"
        }
    
    def _get_recent_measurements(self, measurement_type, days=30):
        return [
            {"date": "2025-06-01", "value": "120/80"},
            {"date": "2025-06-15", "value": "118/78"}
        ]
    
    def get_condition_context(self, condition_token):
        return {
            "duration": "chronic",
            "severity": "moderate",
            "management": "medication"
        }

class KnowledgeBaseManager:
    def __init__(self, base_path):
        self.base_path = base_path
        
    def get_related_entries(self, token, limit=5):
        return [{"type": "note", "date": "2025-01-01"}]

logger = get_logger(__name__)


class TokenIntelligenceEngine:
    """Core engine for generating token-based intelligence."""
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the token intelligence engine.
        
        Args:
            base_path: Base path for loading configuration and data
        """
        self.base_path = Path(base_path)
        logger.info(f"Initializing TokenIntelligenceEngine with base path: {self.base_path}")
        
        # Initialize dependencies
        self.tracker = PersonalDataIntelligenceTracker(base_path)
        self.kb_manager = KnowledgeBaseManager(base_path)
        
        # Initialize token storage components
        self.profile_manager = TokenProfileManager(self.base_path)
        self.token_profiles = self.profile_manager.load_profiles()
        
        # Initialize batch processor - deferred to avoid circular import
        self.batch_processor = None
    
    def generate_intelligence(self, request: TokenIntelligenceRequest) -> TokenIntelligenceResponse:
        """
        Generate intelligence from privacy tokens - NEVER uses original data.
        
        Args:
            request: Token intelligence request from privacy layer
            
        Returns:
            Token-based intelligence response
        """
        start_time = time.time()
        logger.debug(f"Processing request {request.session_id}")
        
        try:
            # Extract tokens from privacy text
            tokens = extract_tokens(request.privacy_text)
            
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
            logger.debug(f"Request {request.session_id} processed in {processing_time}ms")
            
            return TokenIntelligenceResponse(
                intelligence=intelligence,
                confidence=confidence,
                intelligence_type=intelligence_type,
                source="knowledge_base_analysis",
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error in generate_intelligence: {str(e)}")
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
        # Import here to avoid circular imports
        from token_intelligence.api.batch_handler import BatchProcessor
        
        if self.batch_processor is None:
            self.batch_processor = BatchProcessor(self)
            
        return self.batch_processor.process_batch(batch_request)
    
    def _generate_token_intelligence(self, token: str, context: List[str], relationships: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate specific intelligence for a token.
        
        Args:
            token: Token ID
            context: List of context keywords
            relationships: Dictionary of entity relationships
            
        Returns:
            Dictionary with intelligence and confidence
        """
        # Check existing token profile
        token_profile = self.token_profiles.get(token, {})
        
        intelligence = {}
        
        # Route to appropriate intelligence generator based on token type
        if token.startswith('PERSON'):
            intelligence = generate_person_intelligence(token, context, token_profile)
        elif token.startswith('PHONE'):
            intelligence = generate_contact_intelligence(token, context, token_profile)
        elif token.startswith('DOCUMENT'):
            intelligence = generate_document_intelligence(token, context, token_profile)
        elif token.startswith('PROJECT'):
            intelligence = generate_project_intelligence(token, context, token_profile)
        elif token.startswith('PHYSICIAN') or token.startswith('DOCTOR'):
            intelligence = generate_medical_intelligence(token, context, token_profile, self.tracker)
        elif token.startswith('CONDITION') or token.startswith('MEDICATION'):
            intelligence = generate_health_intelligence(token, context, token_profile, self.tracker)
        
        if intelligence:
            return {
                'intelligence': intelligence,
                'confidence': self._calculate_confidence(intelligence, token_profile)
            }
        
        return None
    
    def _classify_intelligence_type(self, privacy_text: str, intelligence: Dict[str, str]) -> str:
        """
        Classify the type of intelligence generated.
        
        Args:
            privacy_text: Original privacy text
            intelligence: Generated intelligence dictionary
            
        Returns:
            Classification of intelligence type
        """
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
        """
        Calculate confidence score for intelligence.
        
        Args:
            intelligence: Generated intelligence dictionary
            profile: Token profile data
            
        Returns:
            Confidence score (0-1)
        """
        base_confidence = 0.7
        
        # Increase confidence if we have historical data
        if profile:
            base_confidence += 0.2
            
        # Increase confidence based on intelligence richness
        if len(intelligence) > 2:
            base_confidence += 0.1
            
        return min(base_confidence, 1.0)
    
    def _store_token_intelligence(self, tokens: List[str], intelligence: Dict[str, str], request: TokenIntelligenceRequest):
        """
        Store generated intelligence for future use.
        
        Args:
            tokens: List of tokens
            intelligence: Generated intelligence dictionary
            request: Original request
        """
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
        
        # Save updated profiles
        self.profile_manager.save_profiles(self.token_profiles) 