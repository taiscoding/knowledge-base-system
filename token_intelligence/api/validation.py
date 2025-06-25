#!/usr/bin/env python3
"""
Token Intelligence API Request/Response Validation
Validation functions for ensuring API requests meet expected format and requirements.
"""

from typing import Dict, Any, Optional, List


def validate_token_request(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate a single token intelligence request.
    
    Args:
        data: Request data to validate
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    # Required fields check
    required_fields = ['privacy_text', 'session_id', 'preserved_context', 'entity_relationships']
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"
    
    # Type validation
    if not isinstance(data['privacy_text'], str):
        return "privacy_text must be a string"
    
    if not isinstance(data['session_id'], str):
        return "session_id must be a string"
    
    if not isinstance(data['preserved_context'], list):
        return "preserved_context must be a list"
    
    if not isinstance(data['entity_relationships'], dict):
        return "entity_relationships must be a dictionary"
    
    # Privacy text validation - must contain at least one token
    if not _contains_privacy_token(data['privacy_text']):
        return "privacy_text must contain at least one privacy token [TOKEN]"
    
    return None


def validate_batch_request(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate a batch token intelligence request.
    
    Args:
        data: Batch request data to validate
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    # Required fields check
    required_fields = ['requests', 'batch_id', 'session_id']
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"
    
    # Type validation
    if not isinstance(data['requests'], list):
        return "requests must be a list"
    
    if not isinstance(data['batch_id'], str):
        return "batch_id must be a string"
    
    if not isinstance(data['session_id'], str):
        return "session_id must be a string"
    
    # Validate individual requests in batch
    if len(data['requests']) == 0:
        return "batch requests list cannot be empty"
    
    for idx, request in enumerate(data['requests']):
        validation_result = validate_token_request(request)
        if validation_result:
            return f"Request at index {idx} is invalid: {validation_result}"
    
    return None


def _contains_privacy_token(text: str) -> bool:
    """
    Check if text contains at least one privacy token in [TOKEN] format.
    
    Args:
        text: Text to check for tokens
        
    Returns:
        True if at least one token is found, False otherwise
    """
    import re
    token_pattern = r'\[([A-Z_]+(?:_\d+)?)\]'
    tokens = re.findall(token_pattern, text)
    return len(tokens) > 0


def validate_token_response(response_data: Dict[str, Any]) -> Optional[str]:
    """
    Validate a token intelligence response.
    
    Args:
        response_data: Response data to validate
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    required_fields = ['intelligence', 'confidence', 'intelligence_type', 'source', 'processing_time_ms']
    for field in required_fields:
        if field not in response_data:
            return f"Missing required field: {field}"
    
    # Type validation
    if not isinstance(response_data['intelligence'], dict):
        return "intelligence must be a dictionary"
    
    if not isinstance(response_data['confidence'], (int, float)) or not (0 <= response_data['confidence'] <= 1):
        return "confidence must be a number between 0 and 1"
    
    if not isinstance(response_data['intelligence_type'], str):
        return "intelligence_type must be a string"
    
    if not isinstance(response_data['source'], str):
        return "source must be a string"
    
    if not isinstance(response_data['processing_time_ms'], int):
        return "processing_time_ms must be an integer"
    
    return None 