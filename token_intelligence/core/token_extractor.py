#!/usr/bin/env python3
"""
Token Extractor
Module for extracting and processing privacy tokens from text.
"""

import re
from typing import List, Dict, Any, Set, Tuple

from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


def extract_tokens(privacy_text: str) -> List[str]:
    """
    Extract privacy tokens from text.
    
    Args:
        privacy_text: Text containing privacy tokens in [TOKEN] format
        
    Returns:
        List of extracted token IDs (without brackets)
    """
    token_pattern = r'\[([A-Z_]+(?:_\d+)?)\]'
    return re.findall(token_pattern, privacy_text)


def extract_tokens_with_positions(privacy_text: str) -> List[Tuple[str, int, int]]:
    """
    Extract privacy tokens from text with their start and end positions.
    
    Args:
        privacy_text: Text containing privacy tokens in [TOKEN] format
        
    Returns:
        List of tuples with (token, start_pos, end_pos)
    """
    token_pattern = r'\[([A-Z_]+(?:_\d+)?)\]'
    tokens_with_pos = []
    
    for match in re.finditer(token_pattern, privacy_text):
        token = match.group(1)  # Extract token without brackets
        start_pos = match.start()
        end_pos = match.end()
        tokens_with_pos.append((token, start_pos, end_pos))
    
    return tokens_with_pos


def categorize_tokens(tokens: List[str]) -> Dict[str, List[str]]:
    """
    Categorize tokens by their prefix.
    
    Args:
        tokens: List of token IDs
        
    Returns:
        Dictionary mapping token categories to lists of tokens
    """
    categories = {}
    
    for token in tokens:
        # Get category from token prefix (e.g., PERSON, PHYSICIAN)
        if '_' in token:
            category = token.split('_')[0]
        else:
            category = token
            
        if category not in categories:
            categories[category] = []
            
        categories[category].append(token)
    
    return categories


def extract_token_relationships(privacy_text: str, entity_relationships: Dict[str, Any]) -> Dict[str, Set[str]]:
    """
    Extract relationships between tokens in the text.
    
    Args:
        privacy_text: Text containing privacy tokens
        entity_relationships: Dictionary of entity relationships from request
        
    Returns:
        Dictionary mapping tokens to sets of related tokens
    """
    tokens = extract_tokens(privacy_text)
    relationships = {}
    
    # Initialize from tokens in text
    for token in tokens:
        relationships[token] = set()
    
    # Add relationships from provided entity_relationships
    for entity, rel_data in entity_relationships.items():
        # Strip brackets if present
        entity_clean = entity.strip('[]') if entity.startswith('[') and entity.endswith(']') else entity
        
        if entity_clean not in relationships:
            relationships[entity_clean] = set()
            
        # Extract linked entities
        linked = rel_data.get('linked_entities', [])
        for linked_entity in linked:
            linked_clean = linked_entity.strip('[]') if linked_entity.startswith('[') and linked_entity.endswith(']') else linked_entity
            relationships[entity_clean].add(linked_clean)
            
            # Ensure the linked entity has an entry
            if linked_clean not in relationships:
                relationships[linked_clean] = set()
                
            # Add bidirectional relationship
            relationships[linked_clean].add(entity_clean)
    
    return relationships


def validate_token_format(token: str) -> bool:
    """
    Validate that a token follows the expected format.
    
    Args:
        token: Token ID to validate
        
    Returns:
        True if the token is valid, False otherwise
    """
    # Valid token format: UPPERCASE_LETTERS followed by optional _NUMBER
    token_pattern = r'^[A-Z_]+(?:_\d+)?$'
    return bool(re.match(token_pattern, token))


def normalize_token(token: str) -> str:
    """
    Normalize a token by removing brackets and ensuring proper format.
    
    Args:
        token: Token to normalize
        
    Returns:
        Normalized token
    """
    # Remove brackets if present
    token = token.strip('[]')
    
    # Ensure uppercase
    token = token.upper()
    
    return token 