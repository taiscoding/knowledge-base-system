#!/usr/bin/env python3
"""
Token Pattern Storage
Storage and management of patterns detected among tokens.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Optional

from token_intelligence.core.data_models import TokenPattern
from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class TokenPatternManager:
    """Manager for token patterns and their persistent storage."""
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the token pattern manager.
        
        Args:
            base_path: Base path for data storage
        """
        self.base_path = Path(base_path)
        self.patterns_dir = self.base_path / "data" / "intelligence"
        self.patterns_file = self.patterns_dir / "token_patterns.json"
        
        # Ensure directory exists
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"TokenPatternManager initialized with patterns path: {self.patterns_file}")
    
    def load_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Load token patterns from storage.
        
        Returns:
            Dictionary of token patterns
        """
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} token patterns")
                    return data
            except Exception as e:
                logger.error(f"Error loading token patterns: {str(e)}")
                return {}
        else:
            logger.info("No existing token patterns found, starting with empty patterns")
            return {}
    
    def save_patterns(self, patterns: Dict[str, Dict[str, Any]]):
        """
        Save token patterns to storage.
        
        Args:
            patterns: Dictionary of token patterns to save
        """
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
                
            logger.info(f"Saved {len(patterns)} token patterns")
        except Exception as e:
            logger.error(f"Error saving token patterns: {str(e)}")
    
    def add_pattern(self, pattern_type: str, tokens_involved: List[str], 
                   confidence: float, description: str) -> str:
        """
        Add or update a token pattern.
        
        Args:
            pattern_type: Type of pattern
            tokens_involved: List of tokens involved in the pattern
            confidence: Confidence score (0-1)
            description: Human-readable description of the pattern
            
        Returns:
            ID of the pattern
        """
        patterns = self.load_patterns()
        
        # Check if similar pattern already exists
        existing_pattern_id = self._find_similar_pattern(patterns, pattern_type, tokens_involved)
        
        if existing_pattern_id:
            # Update existing pattern
            pattern = patterns[existing_pattern_id]
            pattern["confidence"] = max(pattern["confidence"], confidence)
            pattern["last_confirmed"] = datetime.now().isoformat()
            
            # Update tokens involved (might have detected new ones)
            all_tokens = set(pattern["tokens_involved"])
            all_tokens.update(tokens_involved)
            pattern["tokens_involved"] = list(all_tokens)
            
            logger.debug(f"Updated existing pattern: {existing_pattern_id}")
            pattern_id = existing_pattern_id
        else:
            # Create new pattern
            pattern_id = str(uuid.uuid4())
            patterns[pattern_id] = {
                "pattern_id": pattern_id,
                "pattern_type": pattern_type,
                "tokens_involved": tokens_involved,
                "confidence": confidence,
                "description": description,
                "first_detected": datetime.now().isoformat(),
                "last_confirmed": datetime.now().isoformat()
            }
            logger.debug(f"Created new pattern: {pattern_id}")
        
        self.save_patterns(patterns)
        return pattern_id
    
    def _find_similar_pattern(self, patterns: Dict[str, Dict[str, Any]], 
                             pattern_type: str, tokens_involved: List[str]) -> Optional[str]:
        """
        Find an existing pattern that matches the given criteria.
        
        Args:
            patterns: Dictionary of existing patterns
            pattern_type: Type of pattern to match
            tokens_involved: List of tokens involved
            
        Returns:
            Pattern ID if a match is found, None otherwise
        """
        tokens_set = set(tokens_involved)
        
        for pattern_id, pattern in patterns.items():
            # Must be same pattern type
            if pattern["pattern_type"] != pattern_type:
                continue
                
            # Check for significant overlap in tokens involved
            existing_tokens = set(pattern["tokens_involved"])
            if len(tokens_set.intersection(existing_tokens)) / max(len(tokens_set), len(existing_tokens)) >= 0.7:
                return pattern_id
        
        return None
    
    def get_patterns_for_token(self, token_id: str) -> List[Dict[str, Any]]:
        """
        Get all patterns involving a specific token.
        
        Args:
            token_id: Token ID to find patterns for
            
        Returns:
            List of patterns involving the token
        """
        patterns = self.load_patterns()
        token_patterns = []
        
        for pattern_id, pattern in patterns.items():
            if token_id in pattern["tokens_involved"]:
                token_patterns.append(pattern)
        
        return token_patterns
    
    def get_patterns_by_type(self, pattern_type: str) -> List[Dict[str, Any]]:
        """
        Get all patterns of a specific type.
        
        Args:
            pattern_type: Pattern type to filter by
            
        Returns:
            List of patterns of the specified type
        """
        patterns = self.load_patterns()
        matching_patterns = []
        
        for pattern_id, pattern in patterns.items():
            if pattern["pattern_type"] == pattern_type:
                matching_patterns.append(pattern)
        
        return matching_patterns
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """
        Delete a pattern by ID.
        
        Args:
            pattern_id: ID of the pattern to delete
            
        Returns:
            True if deleted, False if not found
        """
        patterns = self.load_patterns()
        
        if pattern_id in patterns:
            del patterns[pattern_id]
            self.save_patterns(patterns)
            logger.info(f"Deleted token pattern: {pattern_id}")
            return True
        else:
            logger.warning(f"Token pattern not found for deletion: {pattern_id}")
            return False
    
    def cleanup_old_patterns(self, max_age_days: int = 90) -> int:
        """
        Remove patterns that haven't been confirmed recently.
        
        Args:
            max_age_days: Maximum age in days for unconfirmed patterns
            
        Returns:
            Number of patterns deleted
        """
        patterns = self.load_patterns()
        cutoff_date = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        deleted_count = 0
        
        for pattern_id, pattern in list(patterns.items()):
            last_confirmed = datetime.fromisoformat(pattern["last_confirmed"]).timestamp()
            if last_confirmed < cutoff_date:
                del patterns[pattern_id]
                deleted_count += 1
                logger.debug(f"Deleted old pattern: {pattern_id}")
        
        if deleted_count > 0:
            self.save_patterns(patterns)
            logger.info(f"Cleaned up {deleted_count} old patterns")
        
        return deleted_count 