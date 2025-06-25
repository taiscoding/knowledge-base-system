#!/usr/bin/env python3
"""
Token Profile Management
Storage and retrieval of token profiles and related information.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Optional

from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class TokenProfileManager:
    """Manager for token profiles and their persistent storage."""
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the token profile manager.
        
        Args:
            base_path: Base path for data storage
        """
        self.base_path = Path(base_path)
        self.profiles_dir = self.base_path / "data" / "intelligence"
        self.profiles_file = self.profiles_dir / "token_profiles.json"
        
        # Ensure directory exists
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"TokenProfileManager initialized with profiles path: {self.profiles_file}")
    
    def load_profiles(self) -> Dict[str, Any]:
        """
        Load token profiles from storage.
        
        Returns:
            Dictionary of token profiles
        """
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    
                    # Convert sets back from lists
                    for profile in data.values():
                        if 'contexts_seen' in profile and isinstance(profile['contexts_seen'], list):
                            profile['contexts_seen'] = set(profile['contexts_seen'])
                    
                    logger.info(f"Loaded {len(data)} token profiles")
                    return data
            except Exception as e:
                logger.error(f"Error loading token profiles: {str(e)}")
                return {}
        else:
            logger.info("No existing token profiles found, starting with empty profiles")
            return {}
    
    def save_profiles(self, profiles: Dict[str, Any]):
        """
        Save token profiles to storage.
        
        Args:
            profiles: Dictionary of token profiles to save
        """
        try:
            # Convert sets to lists for JSON serialization
            serializable_profiles = {}
            for token, profile in profiles.items():
                serializable_profile = profile.copy()
                if 'contexts_seen' in serializable_profile:
                    serializable_profile['contexts_seen'] = list(serializable_profile['contexts_seen'])
                serializable_profiles[token] = serializable_profile
            
            with open(self.profiles_file, 'w') as f:
                json.dump(serializable_profiles, f, indent=2)
                
            logger.info(f"Saved {len(profiles)} token profiles")
        except Exception as e:
            logger.error(f"Error saving token profiles: {str(e)}")
    
    def get_profile(self, token_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single token profile by ID.
        
        Args:
            token_id: ID of the token
            
        Returns:
            Token profile or None if not found
        """
        profiles = self.load_profiles()
        return profiles.get(token_id)
    
    def update_profile(self, token_id: str, updates: Dict[str, Any]):
        """
        Update a token profile with new data.
        
        Args:
            token_id: ID of the token to update
            updates: Dictionary of updates to apply
        """
        profiles = self.load_profiles()
        
        if token_id not in profiles:
            # Create new profile
            profiles[token_id] = {
                'created': datetime.now().isoformat(),
                'interactions': 0,
                'contexts_seen': set()
            }
        
        # Apply updates
        for key, value in updates.items():
            if key == 'contexts_seen' and isinstance(value, (list, set)):
                # Special handling for contexts_seen set
                if 'contexts_seen' not in profiles[token_id]:
                    profiles[token_id]['contexts_seen'] = set()
                profiles[token_id]['contexts_seen'].update(value)
            else:
                profiles[token_id][key] = value
        
        # Update last modified timestamp
        profiles[token_id]['last_modified'] = datetime.now().isoformat()
        
        # Save updated profiles
        self.save_profiles(profiles)
    
    def get_profiles_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get all profiles for a specific token category.
        
        Args:
            category: Token category (e.g., 'PERSON', 'PHYSICIAN')
            
        Returns:
            Dictionary of token profiles for the category
        """
        profiles = self.load_profiles()
        category_profiles = {}
        
        for token_id, profile in profiles.items():
            if token_id.startswith(category):
                category_profiles[token_id] = profile
        
        return category_profiles
    
    def delete_profile(self, token_id: str) -> bool:
        """
        Delete a token profile.
        
        Args:
            token_id: ID of the token profile to delete
            
        Returns:
            True if deleted, False if not found
        """
        profiles = self.load_profiles()
        
        if token_id in profiles:
            del profiles[token_id]
            self.save_profiles(profiles)
            logger.info(f"Deleted token profile: {token_id}")
            return True
        else:
            logger.warning(f"Token profile not found for deletion: {token_id}")
            return False
    
    def backup_profiles(self, backup_suffix: Optional[str] = None) -> str:
        """
        Create a backup of the current token profiles.
        
        Args:
            backup_suffix: Optional suffix for the backup file
            
        Returns:
            Path to the backup file
        """
        if not backup_suffix:
            backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        backup_file = self.profiles_dir / f"token_profiles_backup_{backup_suffix}.json"
        
        # Load the current profiles and save as backup
        profiles = self.load_profiles()
        
        # Convert sets to lists for JSON serialization
        serializable_profiles = {}
        for token, profile in profiles.items():
            serializable_profile = profile.copy()
            if 'contexts_seen' in serializable_profile:
                serializable_profile['contexts_seen'] = list(serializable_profile['contexts_seen'])
            serializable_profiles[token] = serializable_profile
        
        with open(backup_file, 'w') as f:
            json.dump(serializable_profiles, f, indent=2)
        
        logger.info(f"Created profile backup: {backup_file}")
        return str(backup_file) 