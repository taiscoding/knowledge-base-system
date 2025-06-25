#!/usr/bin/env python3
"""
Token Intelligence Data Models
Core dataclasses and type definitions for the token intelligence system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class TokenIntelligenceRequest:
    """
    Request format for token intelligence generation.
    
    Attributes:
        privacy_text: Text with privacy tokens in format [TOKEN]
        session_id: Unique identifier for the session
        preserved_context: List of context keywords preserved from original content
        entity_relationships: Dictionary mapping entities to their relationships
        metadata: Optional additional metadata
    """
    privacy_text: str
    session_id: str
    preserved_context: List[str]
    entity_relationships: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TokenIntelligenceResponse:
    """
    Response format for token intelligence generation.
    
    Attributes:
        intelligence: Dictionary mapping tokens to their generated intelligence
        confidence: Confidence score for the generated intelligence (0-1)
        intelligence_type: Category of intelligence generated
        source: Source of the intelligence
        processing_time_ms: Processing time in milliseconds
    """
    intelligence: Dict[str, str]  # Token-based intelligence only
    confidence: float
    intelligence_type: str
    source: str
    processing_time_ms: int


@dataclass
class BatchTokenRequest:
    """
    Batch request format for processing multiple token intelligence requests.
    
    Attributes:
        requests: List of individual token intelligence requests
        batch_id: Unique identifier for the batch
        session_id: Session identifier
        metadata: Optional additional metadata
    """
    requests: List[TokenIntelligenceRequest]
    batch_id: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BatchTokenResponse:
    """
    Batch response format for multiple token intelligence requests.
    
    Attributes:
        responses: List of individual token intelligence responses
        batch_id: Unique identifier for the batch
        total_processing_time_ms: Total processing time in milliseconds
        batch_size: Number of requests in the batch
        success_count: Number of successfully processed requests
        error_count: Number of requests that resulted in errors
        batch_intelligence_summary: Summary intelligence for the entire batch
    """
    responses: List[TokenIntelligenceResponse]
    batch_id: str
    total_processing_time_ms: int
    batch_size: int
    success_count: int
    error_count: int
    batch_intelligence_summary: Dict[str, Any]


@dataclass
class TokenProfile:
    """
    Profile for a specific token with historical intelligence.
    
    Attributes:
        token_id: Unique identifier for the token
        created: Timestamp when the profile was created
        interactions: Number of times this token has been processed
        contexts_seen: Set of contexts in which this token has appeared
        last_seen: Timestamp when the token was last processed
        intelligence: Dictionary of generated intelligence for this token
    """
    token_id: str
    created: str
    interactions: int = 0
    contexts_seen: set = field(default_factory=set)
    last_seen: Optional[str] = None
    intelligence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TokenRelationship:
    """
    Relationship between two tokens.
    
    Attributes:
        source_token: Source token ID
        target_token: Target token ID
        relationship_type: Type of relationship
        confidence: Confidence score for the relationship (0-1)
        contexts: List of contexts in which this relationship was observed
    """
    source_token: str
    target_token: str
    relationship_type: str
    confidence: float
    contexts: List[str] = field(default_factory=list)


@dataclass
class TokenPattern:
    """
    Pattern detected across multiple token occurrences.
    
    Attributes:
        pattern_id: Unique identifier for the pattern
        pattern_type: Type of pattern detected
        tokens_involved: List of tokens involved in the pattern
        confidence: Confidence score for the pattern (0-1)
        description: Human-readable description of the pattern
        first_detected: Timestamp when the pattern was first detected
        last_confirmed: Timestamp when the pattern was last confirmed
    """
    pattern_id: str
    pattern_type: str
    tokens_involved: List[str]
    confidence: float
    description: str
    first_detected: str
    last_confirmed: Optional[str] = None 