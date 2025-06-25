#!/usr/bin/env python3
"""
Document Intelligence Generator
Generation of intelligence for document-related tokens.
"""

from typing import Dict, List, Any

from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


def generate_document_intelligence(token: str, context: List[str], profile: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate intelligence for document tokens.
    
    Args:
        token: Document token ID
        context: List of context keywords
        profile: Existing token profile data
        
    Returns:
        Dictionary of generated intelligence
    """
    logger.debug(f"Generating document intelligence for {token}")
    intelligence = {}
    
    # Academic context
    if any(word in context for word in ['paper', 'research', 'study', 'journal']):
        intelligence[f"{token}_type"] = "academic paper, research document"
        intelligence[f"{token}_relevance"] = "high relevance to current research interests"
        
        # Additional academic document context
        if any(word in context for word in ['cite', 'reference', 'bibliography']):
            intelligence[f"{token}_usage"] = "citation source, reference material"
        elif any(word in context for word in ['read', 'review']):
            intelligence[f"{token}_status"] = "pending review, in reading queue"
    
    # Business context
    elif any(word in context for word in ['report', 'analysis', 'business', 'financial']):
        intelligence[f"{token}_type"] = "business document, analytical content"
        intelligence[f"{token}_purpose"] = "information source for decision making"
        
        # Additional business document context
        if any(word in context for word in ['quarterly', 'annual']):
            intelligence[f"{token}_frequency"] = "periodic report, regular publication"
        elif any(word in context for word in ['presentation', 'slides']):
            intelligence[f"{token}_format"] = "presentation material, visual content"
    
    # Personal context
    elif any(word in context for word in ['personal', 'note', 'journal']):
        intelligence[f"{token}_type"] = "personal document, private notes"
        intelligence[f"{token}_privacy"] = "confidential content, personal reference"
    
    # Additional insights from profile
    if profile:
        # Frequency of interaction indicates importance
        if profile.get('interactions', 0) > 3:
            intelligence[f"{token}_importance"] = "frequently referenced document"
        
        # Recent vs older document
        if profile.get('last_seen'):
            intelligence[f"{token}_recency"] = "recently accessed document"
    
    return intelligence 