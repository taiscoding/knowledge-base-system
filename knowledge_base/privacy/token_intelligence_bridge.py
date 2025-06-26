#!/usr/bin/env python3
"""
Token Intelligence Bridge
Handles integration between the privacy layer and the token intelligence system.
"""

import logging
import importlib.util
from typing import Dict, List, Any, Optional, Tuple, Set
import re
import hashlib
import json
from functools import lru_cache
from datetime import datetime, timedelta
import os
import heapq
from pathlib import Path
import threading
import time

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


class CacheEntry:
    """Cache entry with metadata for multi-level caching."""
    def __init__(self, key: str, value: Any, priority: float = 0.0):
        self.key = key
        self.value = value
        self.priority = priority  # Higher values = higher priority
        self.last_access_time = datetime.now()
        self.access_count = 1
        self.created_at = datetime.now()
    
    def update_access(self):
        """Update access information when entry is used."""
        self.last_access_time = datetime.now()
        self.access_count += 1
        # Adjust priority based on recency and frequency
        time_factor = 1.0  # Recent accesses weight more
        count_factor = 0.1  # Frequently accessed items weight more
        self.priority = (
            time_factor * (datetime.now() - self.created_at).total_seconds() + 
            count_factor * self.access_count
        )
    
    def __lt__(self, other):
        """Compare entries based on priority for heap operations."""
        return self.priority < other.priority


class MultiLevelCache:
    """
    Multi-level cache implementation for token intelligence.
    
    Implements a priority-based caching system with in-memory and disk layers.
    """
    
    def __init__(self, max_memory_entries: int = 1000, cache_dir: str = None, ttl: int = 3600):
        """
        Initialize the multi-level cache.
        
        Args:
            max_memory_entries: Maximum number of entries in the memory cache
            cache_dir: Directory for disk cache (None to disable)
            ttl: Time-to-live for cache entries in seconds
        """
        self.max_memory_entries = max_memory_entries
        self.cache_dir = cache_dir
        self.ttl = ttl
        
        # In-memory cache as a dictionary
        self.memory_cache: Dict[str, CacheEntry] = {}
        
        # Priority queue for eviction policy
        self.priority_heap: List[Tuple[float, str]] = []
        
        # Lock for thread safety
        self.cache_lock = threading.RLock()
        
        # Create cache directory if specified
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Value if found and not expired, None otherwise
        """
        now = datetime.now()
        
        # Check memory cache first
        with self.cache_lock:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                
                # Check if expired
                if now - entry.last_access_time > timedelta(seconds=self.ttl):
                    # Remove expired entry
                    self._remove_entry(key)
                    return None
                
                # Update access information
                entry.update_access()
                return entry.value
        
        # Check disk cache if enabled
        if self.cache_dir:
            disk_value = self._get_from_disk(key)
            if disk_value is not None:
                # Add to memory cache for future access
                self.put(key, disk_value)
                return disk_value
        
        return None
    
    def put(self, key: str, value: Any) -> None:
        """
        Add item to cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self.cache_lock:
            # If already in cache, just update
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                entry.value = value
                entry.update_access()
                return
            
            # Create new cache entry
            entry = CacheEntry(key, value)
            self.memory_cache[key] = entry
            
            # Add to priority heap
            heapq.heappush(self.priority_heap, (entry.priority, key))
            
            # Check if we need to evict entries
            self._evict_if_needed()
            
            # Save to disk if enabled
            if self.cache_dir:
                self._save_to_disk(key, value)
    
    def _evict_if_needed(self) -> None:
        """Evict entries if cache is full."""
        while len(self.memory_cache) > self.max_memory_entries and self.priority_heap:
            # Get the lowest priority entry
            _, key = heapq.heappop(self.priority_heap)
            
            # Key might have been removed already
            if key not in self.memory_cache:
                continue
            
            # Remove from memory cache
            self._remove_entry(key)
    
    def _remove_entry(self, key: str) -> None:
        """Remove an entry from memory cache."""
        if key in self.memory_cache:
            del self.memory_cache[key]
    
    def _get_from_disk(self, key: str) -> Optional[Any]:
        """Get value from disk cache."""
        if not self.cache_dir:
            return None
        
        cache_file = Path(self.cache_dir) / f"{key}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if entry is expired
            timestamp = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
            if datetime.now() - timestamp > timedelta(seconds=self.ttl):
                # Remove expired cache file
                cache_file.unlink(missing_ok=True)
                return None
            
            return cache_data.get('value')
        except Exception as e:
            logger.warning(f"Error reading disk cache: {e}")
            return None
    
    def _save_to_disk(self, key: str, value: Any) -> None:
        """Save value to disk cache."""
        if not self.cache_dir:
            return
        
        cache_file = Path(self.cache_dir) / f"{key}.json"
        try:
            cache_data = {
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.warning(f"Error writing to disk cache: {e}")
    
    def clear(self, older_than: Optional[int] = None) -> None:
        """
        Clear cache entries.
        
        Args:
            older_than: Clear entries older than this many seconds (None for all)
        """
        now = datetime.now()
        
        with self.cache_lock:
            if older_than is None:
                # Clear all
                self.memory_cache = {}
                self.priority_heap = []
            else:
                # Clear only entries older than specified time
                cutoff = now - timedelta(seconds=older_than)
                
                # Remove old entries from memory cache
                keys_to_remove = [
                    key for key, entry in self.memory_cache.items()
                    if entry.last_access_time < cutoff
                ]
                
                for key in keys_to_remove:
                    self._remove_entry(key)
                
                # Rebuild priority heap
                self.priority_heap = [(entry.priority, key) for key, entry in self.memory_cache.items()]
                heapq.heapify(self.priority_heap)
        
        # Clear disk cache if enabled
        if self.cache_dir:
            try:
                cache_dir = Path(self.cache_dir)
                for cache_file in cache_dir.glob("*.json"):
                    try:
                        if older_than is None:
                            # Remove all files
                            cache_file.unlink()
                        else:
                            # Check file modification time
                            file_modified = datetime.fromtimestamp(cache_file.stat().st_mtime)
                            if file_modified < cutoff:
                                cache_file.unlink()
                    except Exception as e:
                        logger.warning(f"Error clearing cache file {cache_file}: {e}")
            except Exception as e:
                logger.warning(f"Error clearing disk cache: {e}")


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
        
        # Initialize cache system
        self.cache = MultiLevelCache(
            max_memory_entries=1000,
            cache_dir=cache_dir,
            ttl=cache_ttl
        )
        
        # Patterns for token extraction (precompiled for performance)
        self.token_pattern = re.compile(r'\[([A-Z_]+(?:_\d+)?)\]')
        
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
        cached_intelligence = self.cache.get(cache_key)
        if cached_intelligence:
            logger.debug("Using cached intelligence")
            return cached_intelligence
        
        # Extract token information for more targeted intelligence generation
        tokens = self.extract_tokens(privacy_text)
        
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
                    entity_relationships=entity_relationships,
                    tokens=tokens  # Pass extracted tokens for optimization
                )
                
                # Generate intelligence
                response = self.token_intelligence_engine.generate_intelligence(request)
                intelligence = response.intelligence
            except Exception as e:
                logger.error(f"Error generating token intelligence: {e}")
                intelligence = self._generate_fallback_intelligence(privacy_text, tokens)
        else:
            intelligence = self._generate_fallback_intelligence(privacy_text, tokens)
        
        # Cache the generated intelligence
        self.cache.put(cache_key, intelligence)
        
        return intelligence
    
    def _generate_fallback_intelligence(self, privacy_text: str, tokens: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate basic fallback intelligence when token intelligence isn't available.
        
        Args:
            privacy_text: Text with privacy tokens
            tokens: Pre-extracted tokens (optional)
            
        Returns:
            Basic token intelligence dictionary
        """
        intelligence = {}
        
        # Extract tokens from privacy text if not provided
        tokens = tokens or self.extract_tokens(privacy_text)
        
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
    
    @lru_cache(maxsize=100)
    def extract_tokens(self, text: str) -> List[str]:
        """
        Extract token identifiers from privacy text.
        
        Args:
            text: Text with privacy tokens
            
        Returns:
            List of token identifiers
        """
        if not text:
            return []
            
        # Extract tokens using precompiled pattern
        return list(set(self.token_pattern.findall(text)))
    
    def enhance_privacy_text(self, 
                            privacy_text: str, 
                            session_id: str = "enhancement_session",
                            preserved_context: List[str] = None,
                            entity_relationships: Dict[str, Any] = None) -> str:
        """
        Enhance privacy text with intelligence context.
        
        Args:
            privacy_text: Text with privacy tokens
            session_id: Session ID for intelligence generation
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
            
        # Extract tokens upfront
        tokens = self.extract_tokens(privacy_text)
        if not tokens:
            return privacy_text
            
        # Get intelligence for tokens
        intelligence = self.generate_intelligence(
            privacy_text, 
            session_id,
            preserved_context, 
            entity_relationships
        )
        
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
        self.cache.clear(older_than) 