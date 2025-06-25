#!/usr/bin/env python3
"""
Relationship Analysis
Detection and analysis of relationships between tokens.
"""

from typing import Dict, List, Any, Set, Tuple, Optional
from datetime import datetime

from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


def analyze_token_relationships(token_data: Dict[str, Any], 
                              entity_relationships: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyze relationships between tokens based on data.
    
    Args:
        token_data: Dictionary of token profiles or occurrences
        entity_relationships: Dictionary of entity relationships from the request
        
    Returns:
        List of detected relationships with type and confidence
    """
    relationships = []
    
    # Extract explicit relationships from entity_relationships
    explicit_relationships = _extract_explicit_relationships(entity_relationships)
    relationships.extend(explicit_relationships)
    
    # Infer relationships from token intelligence
    inferred_relationships = _infer_relationships_from_intelligence(token_data)
    relationships.extend(inferred_relationships)
    
    # Remove duplicates (keeping the higher confidence one)
    deduplicated = _deduplicate_relationships(relationships)
    
    return deduplicated


def _extract_explicit_relationships(entity_relationships: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract explicit relationships from entity relationships data.
    
    Args:
        entity_relationships: Dictionary of entity relationships from request
        
    Returns:
        List of relationship dictionaries
    """
    relationships = []
    
    for entity, rel_data in entity_relationships.items():
        # Clean token ID (remove brackets)
        source_token = entity.strip('[]') if entity.startswith('[') and entity.endswith(']') else entity
        
        # Extract relationship type
        entity_type = rel_data.get('type', 'unknown')
        
        # Process linked entities
        linked_entities = rel_data.get('linked_entities', [])
        for linked_entity in linked_entities:
            target_token = linked_entity.strip('[]') if linked_entity.startswith('[') and linked_entity.endswith(']') else linked_entity
            
            # Determine relationship type based on entity types
            relationship_type = _determine_relationship_type(source_token, entity_type, target_token)
            
            relationships.append({
                'source_token': source_token,
                'target_token': target_token,
                'relationship_type': relationship_type,
                'confidence': 0.9,  # High confidence for explicit relationships
                'contexts': [],
                'detected_at': datetime.now().isoformat(),
                'source': 'explicit'
            })
        
        # Process belongs_to relationship
        if 'belongs_to' in rel_data:
            belongs_to = rel_data['belongs_to']
            target_token = belongs_to.strip('[]') if belongs_to.startswith('[') and belongs_to.endswith(']') else belongs_to
            
            relationships.append({
                'source_token': source_token,
                'target_token': target_token,
                'relationship_type': 'belongs_to',
                'confidence': 0.9,
                'contexts': [],
                'detected_at': datetime.now().isoformat(),
                'source': 'explicit'
            })
    
    return relationships


def _infer_relationships_from_intelligence(token_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Infer relationships from token intelligence data.
    
    Args:
        token_data: Dictionary of token profiles
        
    Returns:
        List of inferred relationships
    """
    relationships = []
    
    # Get all tokens by category
    tokens_by_category = {}
    for token in token_data:
        category = token.split('_')[0] if '_' in token else token
        if category not in tokens_by_category:
            tokens_by_category[category] = []
        tokens_by_category[category].append(token)
    
    # Analyze intelligence for mentions of other tokens
    for token, profile in token_data.items():
        token_category = token.split('_')[0] if '_' in token else token
        
        # Look for references to other tokens in intelligence
        if isinstance(profile, dict):
            for intel_key, intel_value in profile.items():
                if isinstance(intel_value, str):
                    # Check if intelligence mentions other tokens
                    for other_category, other_tokens in tokens_by_category.items():
                        if token_category == other_category:
                            continue  # Skip same category
                            
                        for other_token in other_tokens:
                            if other_token in intel_value:
                                relationship_type = _determine_relationship_type(token, token_category, other_token)
                                
                                relationships.append({
                                    'source_token': token,
                                    'target_token': other_token,
                                    'relationship_type': relationship_type,
                                    'confidence': 0.7,  # Lower confidence for inferred relationships
                                    'contexts': [],
                                    'detected_at': datetime.now().isoformat(),
                                    'source': 'inferred',
                                    'intelligence_key': intel_key
                                })
    
    return relationships


def _determine_relationship_type(source_token: str, source_type: str, target_token: str) -> str:
    """
    Determine the type of relationship between two tokens.
    
    Args:
        source_token: Source token ID
        source_type: Type of source entity
        target_token: Target token ID
        
    Returns:
        Relationship type
    """
    # Get token categories
    source_category = source_token.split('_')[0] if '_' in source_token else source_token
    target_category = target_token.split('_')[0] if '_' in target_token else target_token
    
    # Person to Person
    if source_category == 'PERSON' and target_category == 'PERSON':
        return 'colleague'
        
    # Person to Project
    if source_category == 'PERSON' and target_category == 'PROJECT':
        return 'works_on'
    if source_category == 'PROJECT' and target_category == 'PERSON':
        return 'has_member'
    
    # Person to Document
    if source_category == 'PERSON' and target_category == 'DOCUMENT':
        return 'authored'
    if source_category == 'DOCUMENT' and target_category == 'PERSON':
        return 'authored_by'
    
    # Medical relationships
    if source_category == 'PERSON' and target_category == 'PHYSICIAN':
        return 'patient_of'
    if source_category == 'PHYSICIAN' and target_category == 'PERSON':
        return 'doctor_for'
    
    if source_category == 'PERSON' and target_category == 'CONDITION':
        return 'has_condition'
    if source_category == 'CONDITION' and target_category == 'PERSON':
        return 'affects'
    
    # Generic relationship for unknown combinations
    return 'related_to'


def _deduplicate_relationships(relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate relationships, keeping those with higher confidence.
    
    Args:
        relationships: List of relationship dictionaries
        
    Returns:
        Deduplicated list of relationships
    """
    relationship_map = {}
    
    for rel in relationships:
        # Create a unique key for each relationship pair
        rel_key = f"{rel['source_token']}:{rel['target_token']}:{rel['relationship_type']}"
        
        if rel_key in relationship_map:
            # Keep the one with higher confidence
            if rel['confidence'] > relationship_map[rel_key]['confidence']:
                relationship_map[rel_key] = rel
        else:
            relationship_map[rel_key] = rel
    
    return list(relationship_map.values()) 