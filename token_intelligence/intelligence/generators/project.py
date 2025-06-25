#!/usr/bin/env python3
"""
Project Intelligence Generator
Generation of intelligence for project-related tokens.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


def generate_project_intelligence(token: str, context: List[str], profile: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate intelligence for project tokens.
    
    Args:
        token: Project token ID
        context: List of context keywords
        profile: Existing token profile data
        
    Returns:
        Dictionary of generated intelligence
    """
    logger.debug(f"Generating project intelligence for {token}")
    intelligence = {}
    
    # Project urgency/priority
    if any(word in context for word in ['deadline', 'urgent', 'priority']):
        intelligence[f"{token}_status"] = "time-sensitive project, requires immediate attention"
        intelligence[f"{token}_priority"] = "high priority, critical timeline"
    
    # Project type/collaboration style
    if any(word in context for word in ['collaborative', 'team', 'group']):
        intelligence[f"{token}_type"] = "team project, multiple stakeholders involved"
        intelligence[f"{token}_collaboration"] = "requires coordination with multiple team members"
    elif any(word in context for word in ['personal', 'individual', 'solo']):
        intelligence[f"{token}_type"] = "individual project, self-managed"
        intelligence[f"{token}_ownership"] = "personally owned and directed"
    
    # Project phase/status
    if any(word in context for word in ['planning', 'early', 'initial']):
        intelligence[f"{token}_phase"] = "early planning stage, defining requirements"
    elif any(word in context for word in ['implementation', 'development', 'building']):
        intelligence[f"{token}_phase"] = "active development, implementation phase"
    elif any(word in context for word in ['testing', 'review', 'finalizing']):
        intelligence[f"{token}_phase"] = "final stages, review and refinement"
    elif any(word in context for word in ['complete', 'finished', 'done']):
        intelligence[f"{token}_phase"] = "completed project, maintenance phase"
    
    # Additional insights from profile
    if profile:
        # Project duration/activity
        if profile.get('created') and profile.get('last_seen'):
            created = datetime.fromisoformat(profile['created'])
            last_seen = datetime.fromisoformat(profile['last_seen'])
            duration_days = (last_seen - created).days
            
            if duration_days > 90:
                intelligence[f"{token}_duration"] = "long-term project, extended timeline"
            elif duration_days > 30:
                intelligence[f"{token}_duration"] = "medium-term project, several weeks scope"
            else:
                intelligence[f"{token}_duration"] = "short-term project, quick turnaround"
        
        # Project activity level
        if profile.get('interactions', 0) > 10:
            intelligence[f"{token}_activity"] = "highly active project, frequent updates"
        elif profile.get('interactions', 0) > 5:
            intelligence[f"{token}_activity"] = "moderately active project, regular progress"
    
    return intelligence 