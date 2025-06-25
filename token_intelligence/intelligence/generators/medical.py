#!/usr/bin/env python3
"""
Medical Intelligence Generator
Generation of intelligence for medical-related tokens.
"""

from typing import Dict, List, Any

from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


def generate_medical_intelligence(token: str, context: List[str], profile: Dict[str, Any], tracker=None) -> Dict[str, str]:
    """
    Generate intelligence for medical provider tokens.
    
    Args:
        token: Medical provider token ID
        context: List of context keywords
        profile: Existing token profile data
        tracker: Optional PersonalDataIntelligenceTracker instance
        
    Returns:
        Dictionary of generated intelligence
    """
    logger.debug(f"Generating medical intelligence for {token}")
    intelligence = {}
    
    # Get visit patterns from tracker if available
    if tracker:
        visit_pattern = tracker._get_provider_visit_pattern(f"[{token}]", days=30)
        if visit_pattern:
            intelligence[f"{token}_visit_frequency"] = f"{visit_pattern['count']} visits in past month"
            intelligence[f"{token}_relationship"] = "established healthcare provider, ongoing care"
    
    # Medical context intelligence
    if any(word in context for word in ['blood pressure', 'hypertension', 'bp']):
        intelligence[f"{token}_specialization"] = "hypertension management, cardiovascular care"
        intelligence[f"{token}_monitoring_style"] = "prefers regular monitoring, data-driven approach"
        
    if any(word in context for word in ['diabetes', 'glucose', 'blood sugar']):
        intelligence[f"{token}_specialization"] = "diabetes management, endocrine care"
    
    # Add more specialized insights from historical data
    if profile and profile.get('interactions', 0) > 3:
        intelligence[f"{token}_visit_pattern"] = "regular follow-up appointments"
        
        # Check historical contexts for care patterns
        contexts_seen = profile.get('contexts_seen', set())
        if 'prescription' in contexts_seen or 'medication' in contexts_seen:
            intelligence[f"{token}_prescription_management"] = "manages ongoing prescriptions"
    
    return intelligence


def generate_health_intelligence(token: str, context: List[str], profile: Dict[str, Any], tracker=None) -> Dict[str, str]:
    """
    Generate intelligence for health condition/medication tokens.
    
    Args:
        token: Health condition/medication token ID
        context: List of context keywords
        profile: Existing token profile data
        tracker: Optional PersonalDataIntelligenceTracker instance
        
    Returns:
        Dictionary of generated intelligence
    """
    logger.debug(f"Generating health intelligence for {token}")
    intelligence = {}
    
    # Get recent measurements for conditions if tracker available
    if tracker and token.startswith('CONDITION'):
        measurements = _get_condition_measurements(context, tracker)
        if measurements:
            intelligence[f"{token}_recent_data"] = "recent readings show improvement trend"
            intelligence[f"{token}_monitoring_available"] = "home monitoring equipment available"
    
    # Condition monitoring patterns
    if any(word in context for word in ['monitor', 'track', 'record', 'log']):
        intelligence[f"{token}_management"] = "actively monitored condition"
    
    # Medication context
    if token.startswith('MEDICATION'):
        if any(word in context for word in ['daily', 'morning', 'evening']):
            intelligence[f"{token}_schedule"] = "regular scheduled medication"
        elif any(word in context for word in ['as needed', 'prn', 'when necessary']):
            intelligence[f"{token}_schedule"] = "as-needed medication"
    
    # Additional insights from profile
    if profile and profile.get('interactions', 0) > 2:
        intelligence[f"{token}_attention_level"] = "frequently discussed health topic"
    
    return intelligence


def _get_condition_measurements(context: List[str], tracker) -> List[Dict]:
    """
    Get recent measurements related to health context.
    
    Args:
        context: List of context keywords
        tracker: PersonalDataIntelligenceTracker instance
        
    Returns:
        List of measurements
    """
    if any(word in context for word in ['blood pressure', 'bp']):
        return tracker._get_recent_measurements("blood_pressure", days=30)
    elif any(word in context for word in ['temperature', 'fever']):
        return tracker._get_recent_measurements("temperature", days=7)
    elif any(word in context for word in ['weight']):
        return tracker._get_recent_measurements("weight", days=30)
    
    return [] 