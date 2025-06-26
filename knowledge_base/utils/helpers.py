"""
Helper Functions
Utility functions for the Knowledge Base system.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import re

# Set up logging
logger = logging.getLogger(__name__)

class KnowledgeBaseError(Exception):
    """Base exception class for all Knowledge Base errors."""
    def __init__(self, message="An error occurred in the knowledge base system"):
        self.message = message
        super().__init__(self.message)


class ContentProcessingError(KnowledgeBaseError):
    """Raised when there is an error processing content."""
    def __init__(self, message="Error processing content"):
        super().__init__(message)


class StorageError(KnowledgeBaseError):
    """Raised when there is an error reading or writing data."""
    def __init__(self, message="Error accessing storage"):
        super().__init__(message)


class ConfigurationError(KnowledgeBaseError):
    """Raised when there is a configuration error."""
    def __init__(self, message="Invalid configuration"):
        super().__init__(message)


class PrivacyError(KnowledgeBaseError):
    """Raised when there is an error related to privacy components."""
    def __init__(self, message="Privacy component error"):
        super().__init__(message)


class ValidationError(KnowledgeBaseError):
    """Raised when data validation fails."""
    def __init__(self, message="Data validation failed"):
        super().__init__(message)


class NotFoundError(KnowledgeBaseError):
    """Raised when a requested resource is not found."""
    def __init__(self, message="Resource not found"):
        super().__init__(message)


class RecoveryError(KnowledgeBaseError):
    """Raised when recovery from a previous error fails."""
    def __init__(self, message="Recovery failed"):
        super().__init__(message)


def generate_id() -> str:
    """
    Generate a unique ID for content.
    
    Returns:
        Unique UUID string
    """
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        Current time in ISO format
    """
    return datetime.now(timezone.utc).isoformat()


def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from text.
    
    Args:
        text: The text to extract hashtags from
    
    Returns:
        List of hashtags without the # symbol
    """
    hashtag_pattern = r"#(\w+)"
    return re.findall(hashtag_pattern, text)


def extract_mentions(text: str) -> List[str]:
    """
    Extract @mentions from text.
    
    Args:
        text: The text to extract mentions from
    
    Returns:
        List of mentions without the @ symbol
    """
    mention_pattern = r"@(\w+)"
    return re.findall(mention_pattern, text)


def parse_date_string(date_string: str) -> Optional[datetime]:
    """
    Parse a date string into a datetime object.
    
    Args:
        date_string: String representing a date
        
    Returns:
        Datetime object or None if parsing failed
    """
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    # Handle relative dates (simple cases)
    today = datetime.now()
    
    if date_string.lower() == 'today':
        return today
    elif date_string.lower() == 'tomorrow':
        return today.replace(day=today.day + 1)
    elif date_string.lower() == 'yesterday':
        return today.replace(day=today.day - 1)
    
    return None


def detect_content_type(content: str) -> str:
    """
    Detect the most likely content type based on text.
    
    Args:
        content: Text content to analyze
        
    Returns:
        Content type string (note, todo, calendar, etc.)
    """
    content_lower = content.lower()
    
    # Look for todo indicators (highest priority)
    todo_indicators = ['todo', 'task', 'action item', '[ ]', '[x]', 'remember to', 'don\'t forget']
    if any(indicator in content_lower for indicator in todo_indicators):
        return "todo"
    
    # Look for calendar indicators
    # Specific patterns that strongly indicate a calendar event
    calendar_primary_indicators = [
        'meeting at', 'appointment at', 'event at', 'call at',
        'scheduled for', 'on the calendar'
    ]
    if any(indicator in content_lower for indicator in calendar_primary_indicators):
        return "calendar"
        
    # Look for project indicators
    project_indicators = ['project', 'initiative', 'plan', 'workflow', 'milestone']
    if any(indicator in content_lower for indicator in project_indicators):
        return "project"
    
    # Secondary calendar indicators (only if not part of "notes from" or similar phrases)
    calendar_secondary = ['meeting', 'appointment', 'event', 'call', 'schedule']
    notes_context = ['notes from', 'summary of', 'minutes from', 'about the', 'regarding the']
    
    # Check if any calendar word appears WITHOUT the context words before it
    if any(cal_word in content_lower for cal_word in calendar_secondary):
        # Make sure it's not just notes ABOUT a meeting 
        if not any(context in content_lower for context in notes_context):
            return "calendar"
    
    # Default to note
    return "note"


def format_filename(template: str, data: Dict[str, Any]) -> str:
    """
    Format a filename based on a template and data.
    
    Args:
        template: Filename template with placeholders
        data: Dictionary of values to substitute
        
    Returns:
        Formatted filename
    """
    # Add timestamp if not in data
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        
    return template.format(**data)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for file systems.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, '_', filename) 