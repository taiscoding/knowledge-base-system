#!/usr/bin/env python3
"""
Privacy Session Manager
Manages privacy sessions for consistent tokenization across interactions.
"""

import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

class PrivacySessionManager:
    """
    Manages privacy sessions for consistent tokenization and context tracking.
    
    Sessions ensure that tokens remain consistent across multiple interactions,
    allowing for privacy-preserving context and intelligence across conversations.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the session manager.
        
        Args:
            storage_dir: Directory for storing session data
        """
        self.storage_dir = Path(storage_dir) if storage_dir else Path.home() / ".kb_privacy_sessions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.sessions = self._load_sessions()
        
    def _load_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Load saved sessions from storage."""
        sessions = {}
        
        if self.storage_dir.exists():
            session_files = list(self.storage_dir.glob("session_*.json"))
            for session_file in session_files:
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                        # Extract session ID from filename correctly
                        session_id = session_file.stem.split("session_", 1)[1]
                        sessions[session_id] = session_data
                except (Exception, IndexError) as e:
                    print(f"Error loading session {session_file}: {e}")
        
        return sessions
    
    def create_session(self, privacy_level: str = "balanced", 
                      metadata: Dict[str, Any] = None) -> str:
        """
        Create a new privacy session.
        
        Args:
            privacy_level: Privacy level for the session ("strict", "balanced", "minimal")
            metadata: Optional metadata for the session
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "privacy_level": privacy_level,
            "token_mappings": {},
            "entity_relationships": {},
            "preserved_context": [],
            "metadata": metadata or {}
        }
        
        self._save_session(session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            Session data or None if not found
        """
        if session_id in self.sessions:
            # Update last used timestamp
            self.sessions[session_id]["last_used"] = datetime.now().isoformat()
            self._save_session(session_id)
            return self.sessions[session_id]
        return None
    
    def update_session(self, session_id: str, 
                      updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a session with new data.
        
        Args:
            session_id: Session ID to update
            updates: Dictionary of updates to apply
            
        Returns:
            Updated session or None if not found
        """
        if session_id not in self.sessions:
            return None
        
        # Update session data
        for key, value in updates.items():
            if key in self.sessions[session_id]:
                # Handle dictionary merges
                if isinstance(value, dict) and isinstance(self.sessions[session_id][key], dict):
                    self.sessions[session_id][key].update(value)
                # Handle list appends
                elif isinstance(value, list) and isinstance(self.sessions[session_id][key], list):
                    self.sessions[session_id][key].extend(value)
                # Direct replacement
                else:
                    self.sessions[session_id][key] = value
        
        # Update last used timestamp
        self.sessions[session_id]["last_used"] = datetime.now().isoformat()
        
        # Save updated session
        self._save_session(session_id)
        
        return self.sessions[session_id]
    
    def add_context(self, session_id: str, context_items: List[str]) -> bool:
        """
        Add context items to a session.
        
        Args:
            session_id: Session ID
            context_items: List of context items to add
            
        Returns:
            True if successful, False otherwise
        """
        if session_id not in self.sessions:
            return False
        
        # Add unique context items
        existing_context = set(self.sessions[session_id].get("preserved_context", []))
        existing_context.update(context_items)
        
        self.sessions[session_id]["preserved_context"] = list(existing_context)
        self.sessions[session_id]["last_used"] = datetime.now().isoformat()
        
        self._save_session(session_id)
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        if session_id not in self.sessions:
            return False
        
        # Remove from memory
        del self.sessions[session_id]
        
        # Remove file
        session_file = self.storage_dir / f"session_{session_id}.json"
        if session_file.exists():
            session_file.unlink()
        
        return True
    
    def _save_session(self, session_id: str) -> None:
        """
        Save a session to storage.
        
        Args:
            session_id: Session ID to save
        """
        if session_id not in self.sessions:
            return
        
        session_file = self.storage_dir / f"session_{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(self.sessions[session_id], f, indent=2)
    
    def get_active_sessions(self, max_age_hours: int = 24) -> List[str]:
        """
        Get list of active session IDs.
        
        Args:
            max_age_hours: Maximum age in hours for a session to be considered active
            
        Returns:
            List of active session IDs
        """
        from datetime import datetime, timedelta
        
        now = datetime.now()
        max_age = timedelta(hours=max_age_hours)
        active_sessions = []
        
        for session_id, session_data in self.sessions.items():
            try:
                last_used = datetime.fromisoformat(session_data.get("last_used", session_data.get("created_at")))
                if now - last_used <= max_age:
                    active_sessions.append(session_id)
            except (ValueError, TypeError):
                # If datetime parsing fails, skip this session
                pass
        
        return active_sessions 