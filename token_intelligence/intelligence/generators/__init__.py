"""
Token Intelligence Generators
Collection of intelligence generators for different token types.
"""

from token_intelligence.intelligence.generators.person import generate_person_intelligence
from token_intelligence.intelligence.generators.medical import (
    generate_medical_intelligence,
    generate_health_intelligence
)
from token_intelligence.intelligence.generators.document import generate_document_intelligence
from token_intelligence.intelligence.generators.project import generate_project_intelligence


def generate_contact_intelligence(token: str, context: list, profile: dict) -> dict:
    """
    Generate intelligence for contact tokens.
    
    Args:
        token: Contact token ID
        context: List of context keywords
        profile: Existing token profile data
        
    Returns:
        Dictionary of generated intelligence
    """
    intelligence = {}
    
    # Phone number context
    if any(word in context for word in ['call', 'urgent', 'emergency']):
        intelligence[f"{token}_usage"] = "emergency contact, urgent communications"
    elif any(word in context for word in ['work', 'office']):
        intelligence[f"{token}_usage"] = "professional contact, business hours"
    else:
        intelligence[f"{token}_usage"] = "personal contact, flexible timing"
            
    return intelligence


__all__ = [
    'generate_person_intelligence',
    'generate_medical_intelligence',
    'generate_health_intelligence',
    'generate_contact_intelligence',
    'generate_document_intelligence',
    'generate_project_intelligence'
]
