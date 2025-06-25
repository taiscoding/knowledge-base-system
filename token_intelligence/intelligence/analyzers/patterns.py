#!/usr/bin/env python3
"""
Pattern Detection Analyzer
Analysis of patterns across token occurrences.
"""

from typing import Dict, List, Any, Set, Tuple, Optional
from collections import Counter
from datetime import datetime

from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


def detect_token_patterns(token_data: Dict[str, Any], context_data: List[str]) -> List[Dict[str, Any]]:
    """
    Detect patterns in token usage and context.
    
    Args:
        token_data: Dictionary of token profiles or occurrences
        context_data: List of context keywords
        
    Returns:
        List of detected patterns
    """
    patterns = []
    
    # Frequency pattern detection
    frequency_patterns = _detect_frequency_patterns(token_data)
    patterns.extend(frequency_patterns)
    
    # Co-occurrence pattern detection
    cooccurrence_patterns = _detect_cooccurrence_patterns(token_data)
    patterns.extend(cooccurrence_patterns)
    
    # Context patterns
    context_patterns = _detect_context_patterns(token_data, context_data)
    patterns.extend(context_patterns)
    
    return patterns


def _detect_frequency_patterns(token_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect patterns in token frequency.
    
    Args:
        token_data: Dictionary of token profiles or occurrences
        
    Returns:
        List of frequency-based patterns
    """
    patterns = []
    
    # Get token categories
    token_categories = {}
    for token, data in token_data.items():
        category = token.split('_')[0] if '_' in token else token
        if category not in token_categories:
            token_categories[category] = []
        token_categories[category].append(token)
    
    # Detect dominant categories (if one category represents >70% of tokens)
    total_tokens = len(token_data)
    for category, tokens in token_categories.items():
        category_ratio = len(tokens) / total_tokens
        if category_ratio > 0.7 and len(tokens) >= 3:
            patterns.append({
                'pattern_type': 'frequency',
                'pattern_name': 'dominant_category',
                'description': f"High concentration of {category} tokens ({len(tokens)})",
                'tokens_involved': tokens,
                'confidence': 0.8,
                'detected_at': datetime.now().isoformat()
            })
    
    return patterns


def _detect_cooccurrence_patterns(token_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detect patterns in token co-occurrence.
    
    Args:
        token_data: Dictionary of token profiles or occurrences
        
    Returns:
        List of co-occurrence patterns
    """
    patterns = []
    
    # Find tokens that frequently appear together in the same context
    person_tokens = [t for t in token_data.keys() if t.startswith('PERSON')]
    project_tokens = [t for t in token_data.keys() if t.startswith('PROJECT')]
    
    # Check for project team pattern (multiple people associated with same project)
    if len(person_tokens) >= 2 and len(project_tokens) >= 1:
        for project_token in project_tokens:
            project_team = []
            
            for person_token in person_tokens:
                # Check for relationship between person and project
                # This is simplified - real implementation would check for actual relationship indicators
                if any(project_token in str(v) for v in token_data[person_token].values() if isinstance(v, str)):
                    project_team.append(person_token)
            
            if len(project_team) >= 2:
                patterns.append({
                    'pattern_type': 'cooccurrence',
                    'pattern_name': 'project_team',
                    'description': f"Project team detected: {len(project_team)} people working on {project_token}",
                    'tokens_involved': project_team + [project_token],
                    'confidence': 0.7,
                    'detected_at': datetime.now().isoformat()
                })
    
    return patterns


def _detect_context_patterns(token_data: Dict[str, Any], context_data: List[str]) -> List[Dict[str, Any]]:
    """
    Detect patterns in context keywords.
    
    Args:
        token_data: Dictionary of token profiles or occurrences
        context_data: List of context keywords
        
    Returns:
        List of context patterns
    """
    patterns = []
    
    # Group contexts into domains
    domain_keywords = {
        'professional': ['meeting', 'work', 'project', 'deadline', 'report', 'presentation'],
        'academic': ['research', 'paper', 'study', 'academic', 'journal', 'university'],
        'medical': ['doctor', 'health', 'medical', 'appointment', 'prescription', 'symptoms'],
        'social': ['dinner', 'lunch', 'social', 'friend', 'meetup', 'event']
    }
    
    # Count occurrences of each domain in context
    domain_counts = {domain: 0 for domain in domain_keywords}
    
    for keyword in context_data:
        for domain, domain_words in domain_keywords.items():
            if keyword in domain_words:
                domain_counts[domain] += 1
    
    # Check for dominant domain
    total_domain_matches = sum(domain_counts.values())
    if total_domain_matches > 0:
        dominant_domain = max(domain_counts.items(), key=lambda x: x[1])
        if dominant_domain[1] / total_domain_matches > 0.6:
            # Get tokens that match this domain
            domain_tokens = []
            for token in token_data:
                token_category = token.split('_')[0] if '_' in token else token
                
                # Map token categories to domains
                token_domain = None
                if token_category in ['PERSON', 'PHONE'] and dominant_domain[0] == 'social':
                    token_domain = 'social'
                elif token_category in ['PROJECT', 'DOCUMENT'] and dominant_domain[0] == 'professional':
                    token_domain = 'professional'
                elif token_category in ['DOCUMENT'] and dominant_domain[0] == 'academic':
                    token_domain = 'academic'
                elif token_category in ['PHYSICIAN', 'CONDITION', 'MEDICATION'] and dominant_domain[0] == 'medical':
                    token_domain = 'medical'
                
                if token_domain == dominant_domain[0]:
                    domain_tokens.append(token)
            
            if domain_tokens:
                patterns.append({
                    'pattern_type': 'context',
                    'pattern_name': f"{dominant_domain[0]}_domain",
                    'description': f"Strong {dominant_domain[0]} context with {len(domain_tokens)} relevant tokens",
                    'tokens_involved': domain_tokens,
                    'confidence': 0.75,
                    'detected_at': datetime.now().isoformat()
                })
    
    return patterns 