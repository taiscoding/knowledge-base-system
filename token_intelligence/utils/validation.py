#!/usr/bin/env python3
"""
Validation Utilities
General validation helpers for the token intelligence system.
"""

import re
from typing import Any, Dict, List, Optional, Union, Callable


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Optional[str]:
    """
    Validate that all required fields are present in a dictionary.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"
    return None


def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> Optional[str]:
    """
    Validate that fields have the expected types.
    
    Args:
        data: Dictionary to validate
        field_types: Dictionary mapping field names to expected types
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    for field, expected_type in field_types.items():
        if field in data and not isinstance(data[field], expected_type):
            return f"Field '{field}' must be of type {expected_type.__name__}"
    return None


def validate_string_pattern(value: str, pattern: str, field_name: str = "value") -> Optional[str]:
    """
    Validate that a string matches a regular expression pattern.
    
    Args:
        value: String to validate
        pattern: Regular expression pattern
        field_name: Name of the field for error message
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    if not re.match(pattern, value):
        return f"{field_name} must match pattern: {pattern}"
    return None


def validate_numeric_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                        max_value: Optional[Union[int, float]] = None, 
                        field_name: str = "value") -> Optional[str]:
    """
    Validate that a numeric value is within a specified range.
    
    Args:
        value: Numeric value to validate
        min_value: Optional minimum value (inclusive)
        max_value: Optional maximum value (inclusive)
        field_name: Name of the field for error message
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    if min_value is not None and value < min_value:
        return f"{field_name} must be greater than or equal to {min_value}"
    if max_value is not None and value > max_value:
        return f"{field_name} must be less than or equal to {max_value}"
    return None


def validate_list_contents(items: List[Any], validator: Callable[[Any], Optional[str]]) -> Optional[str]:
    """
    Validate each item in a list using a validator function.
    
    Args:
        items: List of items to validate
        validator: Function that takes an item and returns an error message or None
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    for i, item in enumerate(items):
        error = validator(item)
        if error:
            return f"Item at index {i} is invalid: {error}"
    return None


def validate_token_format(token: str) -> Optional[str]:
    """
    Validate that a token follows the expected format.
    
    Args:
        token: Token to validate
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    # Valid token format: UPPERCASE_LETTERS followed by optional _NUMBER
    token_pattern = r'^[A-Z_]+(?:_\d+)?$'
    if not re.match(token_pattern, token):
        return f"Token '{token}' does not follow the expected format"
    return None


def validate_privacy_text(text: str) -> Optional[str]:
    """
    Validate that privacy text contains at least one token in the correct format.
    
    Args:
        text: Privacy text to validate
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    token_pattern = r'\[([A-Z_]+(?:_\d+)?)\]'
    matches = re.findall(token_pattern, text)
    
    if not matches:
        return "Privacy text must contain at least one token in [TOKEN] format"
    return None


def validate_dict_structure(data: Dict[str, Any], structure: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """
    Validate that a dictionary follows a specific structure.
    
    Args:
        data: Dictionary to validate
        structure: Dictionary describing the expected structure
        
    Returns:
        Error message if validation fails, None if validation passes
    """
    for field_name, field_spec in structure.items():
        # Check if field is required
        required = field_spec.get('required', False)
        if required and field_name not in data:
            return f"Missing required field: {field_name}"
        
        # Skip further validation if field is not present
        if field_name not in data:
            continue
        
        # Check field type
        expected_type = field_spec.get('type')
        if expected_type and not isinstance(data[field_name], expected_type):
            return f"Field '{field_name}' must be of type {expected_type.__name__}"
        
        # Check nested structure for dict types
        if isinstance(data[field_name], dict) and 'structure' in field_spec:
            nested_error = validate_dict_structure(data[field_name], field_spec['structure'])
            if nested_error:
                return f"In field '{field_name}': {nested_error}"
    
    return None 