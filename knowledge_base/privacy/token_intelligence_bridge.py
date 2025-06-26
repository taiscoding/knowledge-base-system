#!/usr/bin/env python3
"""
Token Intelligence Bridge
Handles integration between the privacy layer and the token intelligence system.
"""

import logging
import importlib.util
from typing import Dict, List, Any, Optional
import re
import hashlib
import json
from functools import lru_cache
from datetime import datetime, timedelta
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Dummy class for fallback when token intelligence isn't available
class DummyTokenIntelligenceResponse:
    """Dummy response when token intelligence is unavailable."""
    def __init__(self):
        self.intelligence = {}
        self.confidence = 0.0
        self.intelligence_type = "unavailable"
        self.source = "fallback"
        self.processing_time_ms = 0


class TokenIntelligenceBridge:
    """Bridge between privacy layer and token intelligence system."""
    
    def __init__(self, cache_dir: str = None, cache_ttl: int = 3600):
        """
        Initialize the bridge and try to import token intelligence.
        
        Args:
            cache_dir: Directory for caching intelligence results (None for in-memory only)
            cache_ttl: Time-to-live for cache entries in seconds (default: 1 hour)
        """
        self.token_intelligence_available = False
        self.token_intelligence_engine = None
        self.token_intelligence_request_class = None
        
        # Initialize cache settings
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        self.memory_cache = {}
        self.cache_timestamps = {}
        
        # Create cache directory if specified
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
        
        # Try to import token intelligence
        self._try_import_token_intelligence()
    
    def _try_import_token_intelligence(self):
        """Try to import token intelligence modules."""
        try:
            # Check if token intelligence is installed
            if importlib.util.find_spec("token_intelligence") is not None:
                # Import required classes
                from token_intelligence import TokenIntelligenceEngine
                from token_intelligence.core.data_models import TokenIntelligenceRequest
                
                # Initialize engine
                self.token_intelligence_engine = TokenIntelligenceEngine()
                self.token_intelligence_request_class = TokenIntelligenceRequest
                self.token_intelligence_available = True
                logger.info("Token intelligence system successfully initialized")
            else:
                logger.warning("Token intelligence module not available")
                self.token_intelligence_available = False
        except Exception as e:
            logger.warning(f"Error initializing token intelligence: {e}")
            self.token_intelligence_available = False
    
    def _generate_cache_key(self, text: str, context: List[str], relationships: Dict[str, Any]) -> str:
        """
        Generate a cache key for token intelligence request.
        
        Args:
            text: Privacy text
            context: Context keywords
            relationships: Entity relationships
            
        Returns:
            Cache key string
        """
        # Create a deterministic representation of the request
        request_data = {
            "text": text,
            "context": sorted(context) if context else [],
            "relationships": json.dumps(relationships, sort_keys=True)
        }
        
        # Generate a hash of the request data
        request_str = json.dumps(request_data, sort_keys=True)
        return hashlib.md5(request_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get intelligence from cache if available and not expired.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Intelligence dict if cached, None otherwise
        """
        # Check memory cache first
        if cache_key in self.memory_cache:
            # Check if cache entry is expired
            cache_time = self.cache_timestamps.get(cache_key)
            if cache_time and datetime.now() - cache_time < timedelta(seconds=self.cache_ttl):
                return self.memory_cache[cache_key]
            else:
                # Remove expired entry
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                if cache_key in self.cache_timestamps:
                    del self.cache_timestamps[cache_key]
        
        # Check disk cache if enabled
        if self.cache_dir:
            cache_file = Path(self.cache_dir) / f"{cache_key}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    
                    # Check if cache entry is expired
                    cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
                    if datetime.now() - cache_time < timedelta(seconds=self.cache_ttl):
                        # Store in memory cache for faster access next time
                        intelligence = cache_data.get('intelligence', {})
                        self.memory_cache[cache_key] = intelligence
                        self.cache_timestamps[cache_key] = cache_time
                        return intelligence
                    else:
                        # Remove expired cache file
                        cache_file.unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(f"Error reading cache file: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, intelligence: Dict[str, Any]):
        """
        Save intelligence to cache.
        
        Args:
            cache_key: Cache key
            intelligence: Intelligence dict to cache
        """
        # Save to memory cache
        self.memory_cache[cache_key] = intelligence
        self.cache_timestamps[cache_key] = datetime.now()
        
        # Save to disk cache if enabled
        if self.cache_dir:
            cache_file = Path(self.cache_dir) / f"{cache_key}.json"
            try:
                cache_data = {
                    'intelligence': intelligence,
                    'timestamp': datetime.now().isoformat()
                }
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f)
            except Exception as e:
                logger.warning(f"Error writing cache file: {e}")
    
    def generate_intelligence(self, 
                             privacy_text: str, 
                             session_id: str,
                             preserved_context: List[str],
                             entity_relationships: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate intelligence for privacy tokens.
        
        Args:
            privacy_text: Text with privacy tokens
            session_id: Session ID
            preserved_context: List of context keywords
            entity_relationships: Dictionary of entity relationships
            
        Returns:
            Dictionary of token intelligence
        """
        # Generate a cache key for this request
        cache_key = self._generate_cache_key(privacy_text, preserved_context, entity_relationships)
        
        # Check if we have cached intelligence
        cached_intelligence = self._get_from_cache(cache_key)
        if cached_intelligence:
            logger.debug("Using cached intelligence")
            return cached_intelligence
        
        # No cached data, generate intelligence
        intelligence = {}
        
        # Try to use token intelligence if available
        if self.token_intelligence_available and self.token_intelligence_engine:
            try:
                # Create request
                request = self.token_intelligence_request_class(
                    privacy_text=privacy_text,
                    session_id=session_id,
                    preserved_context=preserved_context,
                    entity_relationships=entity_relationships
                )
                
                # Generate intelligence
                response = self.token_intelligence_engine.generate_intelligence(request)
                intelligence = response.intelligence
            except Exception as e:
                logger.error(f"Error generating token intelligence: {e}")
                intelligence = self._generate_fallback_intelligence(privacy_text)
        else:
            intelligence = self._generate_fallback_intelligence(privacy_text)
        
        # Cache the generated intelligence
        self._save_to_cache(cache_key, intelligence)
        
        return intelligence
    
    def _generate_fallback_intelligence(self, privacy_text: str) -> Dict[str, Any]:
        """
        Generate basic fallback intelligence when token intelligence isn't available.
        
        Args:
            privacy_text: Text with privacy tokens
            
        Returns:
            Basic token intelligence dictionary
        """
        intelligence = {}
        
        # Extract tokens from privacy text
        tokens = re.findall(r'\[([A-Z_]+(?:_\d+)?)\]', privacy_text)
        
        # Generate basic intelligence for each token
        for token in tokens:
            token_type = token.split('_')[0]
            
            # Add generic intelligence based on token type
            if token_type == "PERSON":
                intelligence[f"{token}_type"] = "individual"
                intelligence[f"{token}_context"] = "mentioned_in_content"
            elif token_type == "PHONE":
                intelligence[f"{token}_type"] = "contact_method"
            elif token_type == "EMAIL":
                intelligence[f"{token}_type"] = "contact_method"
                intelligence[f"{token}_context"] = "electronic_communication"
            elif token_type == "LOCATION":
                intelligence[f"{token}_type"] = "physical_place"
            elif token_type == "PROJECT":
                intelligence[f"{token}_type"] = "work_activity"
                intelligence[f"{token}_context"] = "professional"
        
        return intelligence
    
    def enhance_privacy_text(self, 
                            privacy_text: str, 
                            preserved_context: List[str] = None,
                            entity_relationships: Dict[str, Any] = None) -> str:
        """
        Enhance privacy text with intelligence context.
        
        Args:
            privacy_text: Text with privacy tokens
            preserved_context: List of context keywords
            entity_relationships: Dictionary of entity relationships
            
        Returns:
            Enhanced text with context hints for AI
        """
        # Set default values
        if preserved_context is None:
            preserved_context = []
            
        if entity_relationships is None:
            entity_relationships = {}
            
        # Get intelligence for tokens
        intelligence = self.generate_intelligence(
            privacy_text, 
            "enhancement_session",  # Use fixed session ID for enhancement 
            preserved_context, 
            entity_relationships
        )
        
        # Extract tokens from text
        tokens = re.findall(r'\[([A-Z_]+(?:_\d+)?)\]', privacy_text)
        
        # Create enhanced prompt with context
        enhanced_text = privacy_text
        
        # Add intelligence context based on token type
        if intelligence:
            enhanced_text += "\n\nContext (Privacy-Preserved):\n"
            for token in tokens:
                token_context = {}
                for key, value in intelligence.items():
                    if key.startswith(token):
                        context_key = key.replace(f"{token}_", "")
                        token_context[context_key] = value
                
                if token_context:
                    enhanced_text += f"\n[{token}]: {token_context}\n"
        
        return enhanced_text
    
    def clear_cache(self, older_than: int = None):
        """
        Clear intelligence cache.
        
        Args:
            older_than: Clear entries older than this many seconds (None for all)
        """
        now = datetime.now()
        
        # Clear memory cache
        if older_than:
            # Remove entries older than specified time
            expired_keys = [
                key for key, timestamp in self.cache_timestamps.items()
                if now - timestamp > timedelta(seconds=older_than)
            ]
            for key in expired_keys:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
        else:
            # Clear all entries
            self.memory_cache = {}
            self.cache_timestamps = {}
        
        # Clear disk cache if enabled
        if self.cache_dir:
            cache_dir = Path(self.cache_dir)
            if older_than:
                # Remove files older than specified time
                for cache_file in cache_dir.glob("*.json"):
                    try:
                        file_modified = datetime.fromtimestamp(cache_file.stat().st_mtime)
                        if now - file_modified > timedelta(seconds=older_than):
                            cache_file.unlink()
                    except Exception as e:
                        logger.warning(f"Error clearing cache file {cache_file}: {e}")
            else:
                # Remove all cache files
                for cache_file in cache_dir.glob("*.json"):
                    try:
                        cache_file.unlink()
                    except Exception as e:
                        logger.warning(f"Error clearing cache file {cache_file}: {e}") 