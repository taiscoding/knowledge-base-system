#!/usr/bin/env python3
"""
Token Intelligence Batch Processing
Specialized handler for efficient batch processing of token intelligence requests.
"""

import time
from typing import Dict, List, Set, Any
from datetime import datetime

from token_intelligence.core.data_models import (
    TokenIntelligenceRequest,
    TokenIntelligenceResponse,
    BatchTokenRequest,
    BatchTokenResponse
)
from token_intelligence.core.token_extractor import extract_tokens
from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class BatchProcessor:
    """Handler for efficient batch processing of token intelligence requests."""
    
    def __init__(self, engine):
        """
        Initialize the batch processor with a token intelligence engine.
        
        Args:
            engine: TokenIntelligenceEngine instance to use for processing
        """
        self.engine = engine
    
    def process_batch(self, batch_request: BatchTokenRequest) -> BatchTokenResponse:
        """
        Process a batch of token intelligence requests efficiently.
        
        Args:
            batch_request: Batch request containing multiple token intelligence requests
            
        Returns:
            Batch response with individual results and summary intelligence
        """
        start_time = time.time()
        logger.info(f"Processing batch {batch_request.batch_id} with {len(batch_request.requests)} requests")
        
        responses = []
        success_count = 0
        error_count = 0
        all_tokens = set()
        all_intelligence_types = []
        
        # Pre-load all unique tokens for batch optimization
        for request in batch_request.requests:
            tokens = extract_tokens(request.privacy_text)
            all_tokens.update(tokens)
        
        # Process each request
        for request in batch_request.requests:
            try:
                response = self.engine.generate_intelligence(request)
                responses.append(response)
                
                if response.intelligence_type != "error":
                    success_count += 1
                    all_intelligence_types.append(response.intelligence_type)
                else:
                    error_count += 1
                    logger.warning(f"Error processing request in batch {batch_request.batch_id}")
                    
            except Exception as e:
                logger.error(f"Exception in batch processing: {str(e)}")
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
        
        logger.info(f"Completed batch {batch_request.batch_id} in {total_processing_time}ms " 
                   f"({success_count} success, {error_count} errors)")
        
        return BatchTokenResponse(
            responses=responses,
            batch_id=batch_request.batch_id,
            total_processing_time_ms=total_processing_time,
            batch_size=len(batch_request.requests),
            success_count=success_count,
            error_count=error_count,
            batch_intelligence_summary=batch_summary
        )
    
    def _generate_batch_summary(self, 
                               all_tokens: Set[str], 
                               intelligence_types: List[str], 
                               batch_request: BatchTokenRequest) -> Dict[str, Any]:
        """
        Generate summary intelligence across the batch.
        
        Args:
            all_tokens: Set of all tokens processed in the batch
            intelligence_types: List of intelligence types generated
            batch_request: Original batch request
            
        Returns:
            Dictionary containing batch-level intelligence and patterns
        """
        summary = {
            "unique_tokens_processed": len(all_tokens),
            "token_types_seen": list(set(token.split('_')[0] for token in all_tokens)),
            "intelligence_types_generated": list(set(intelligence_types)),
            "batch_patterns": {},
            "timestamp": datetime.now().isoformat()
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