#!/usr/bin/env python3
"""
Person Intelligence Generator
Generation of intelligence for person-related tokens.
"""

from typing import Dict, List, Any

from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


def generate_person_intelligence(token: str, context: List[str], profile: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate intelligence for person tokens.
    
    Args:
        token: Person token ID
        context: List of context keywords
        profile: Existing token profile data
        
    Returns:
        Dictionary of generated intelligence
    """
    logger.debug(f"Generating person intelligence for {token}")
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
    if profile and profile.get('communication_frequency') == 'high':
        intelligence[f"{token}_patterns"] = "frequent communication, prefers quick responses"
        
    # Additional insights from historical data
    if profile and profile.get('interactions', 0) > 5:
        intelligence[f"{token}_familiarity"] = "frequently mentioned contact"
        
        # Add context-specific insights based on historical contexts
        contexts_seen = profile.get('contexts_seen', set())
        if 'meeting' in contexts_seen and 'project' in contexts_seen:
            intelligence[f"{token}_project_role"] = "regular project participant"
    
    return intelligence 