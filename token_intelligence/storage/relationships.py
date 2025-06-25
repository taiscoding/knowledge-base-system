#!/usr/bin/env python3
"""
Token Relationship Storage
Storage and management of relationships between tokens.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Optional, Tuple

from token_intelligence.core.data_models import TokenRelationship
from token_intelligence.utils.logging import get_logger

logger = get_logger(__name__)


class TokenRelationshipManager:
    """Manager for token relationships and their persistent storage."""
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the token relationship manager.
        
        Args:
            base_path: Base path for data storage
        """
        self.base_path = Path(base_path)
        self.relationships_dir = self.base_path / "data" / "intelligence"
        self.relationships_file = self.relationships_dir / "token_relationships.json"
        
        # Ensure directory exists
        self.relationships_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"TokenRelationshipManager initialized with relationships path: {self.relationships_file}")
    
    def load_relationships(self) -> Dict[str, Dict[str, Any]]:
        """
        Load token relationships from storage.
        
        Returns:
            Dictionary of token relationships
        """
        if self.relationships_file.exists():
            try:
                with open(self.relationships_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} token relationships")
                    return data
            except Exception as e:
                logger.error(f"Error loading token relationships: {str(e)}")
                return {}
        else:
            logger.info("No existing token relationships found, starting with empty relationships")
            return {}
    
    def save_relationships(self, relationships: Dict[str, Dict[str, Any]]):
        """
        Save token relationships to storage.
        
        Args:
            relationships: Dictionary of token relationships to save
        """
        try:
            with open(self.relationships_file, 'w') as f:
                json.dump(relationships, f, indent=2)
                
            logger.info(f"Saved {len(relationships)} token relationships")
        except Exception as e:
            logger.error(f"Error saving token relationships: {str(e)}")
    
    def add_relationship(self, source_token: str, target_token: str, relationship_type: str, 
                        confidence: float, context: List[str] = None) -> str:
        """
        Add or update a token relationship.
        
        Args:
            source_token: Source token ID
            target_token: Target token ID
            relationship_type: Type of relationship
            confidence: Confidence score (0-1)
            context: Optional list of context keywords
            
        Returns:
            ID of the relationship
        """
        relationships = self.load_relationships()
        
        # Create relationship ID
        relationship_id = f"{source_token}:{target_token}"
        
        if context is None:
            context = []
        
        # Check if relationship already exists
        if relationship_id in relationships:
            # Update existing relationship
            rel_data = relationships[relationship_id]
            rel_data["confidence"] = max(rel_data["confidence"], confidence)
            
            # Update contexts
            existing_contexts = set(rel_data.get("contexts", []))
            existing_contexts.update(context)
            rel_data["contexts"] = list(existing_contexts)
            
            rel_data["last_updated"] = datetime.now().isoformat()
        else:
            # Create new relationship
            relationships[relationship_id] = {
                "source_token": source_token,
                "target_token": target_token,
                "relationship_type": relationship_type,
                "confidence": confidence,
                "contexts": context,
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        
        self.save_relationships(relationships)
        return relationship_id
    
    def get_relationships_for_token(self, token_id: str) -> List[Dict[str, Any]]:
        """
        Get all relationships for a specific token.
        
        Args:
            token_id: Token ID to find relationships for
            
        Returns:
            List of relationships where token is source or target
        """
        relationships = self.load_relationships()
        token_relationships = []
        
        for rel_id, rel_data in relationships.items():
            if rel_data["source_token"] == token_id or rel_data["target_token"] == token_id:
                token_relationships.append(rel_data)
        
        return token_relationships
    
    def get_related_tokens(self, token_id: str, relationship_type: Optional[str] = None) -> List[str]:
        """
        Get all tokens related to the specified token.
        
        Args:
            token_id: Token ID to find related tokens for
            relationship_type: Optional filter by relationship type
            
        Returns:
            List of related token IDs
        """
        token_relationships = self.get_relationships_for_token(token_id)
        related_tokens = set()
        
        for rel in token_relationships:
            if relationship_type and rel["relationship_type"] != relationship_type:
                continue
                
            if rel["source_token"] == token_id:
                related_tokens.add(rel["target_token"])
            else:
                related_tokens.add(rel["source_token"])
        
        return list(related_tokens)
    
    def delete_relationship(self, source_token: str, target_token: str) -> bool:
        """
        Delete a relationship between two tokens.
        
        Args:
            source_token: Source token ID
            target_token: Target token ID
            
        Returns:
            True if deleted, False if not found
        """
        relationships = self.load_relationships()
        relationship_id = f"{source_token}:{target_token}"
        
        if relationship_id in relationships:
            del relationships[relationship_id]
            self.save_relationships(relationships)
            logger.info(f"Deleted token relationship: {relationship_id}")
            return True
        else:
            logger.warning(f"Token relationship not found for deletion: {relationship_id}")
            return False
    
    def find_relationship_chains(self, start_token: str, max_depth: int = 3) -> List[List[str]]:
        """
        Find chains of related tokens starting from a token.
        
        Args:
            start_token: Starting token ID
            max_depth: Maximum depth of relationship chain
            
        Returns:
            List of token chains (lists of token IDs)
        """
        relationships = self.load_relationships()
        chains = []
        visited = set()
        
        def dfs(current_token, depth, current_chain):
            if depth > max_depth or current_token in visited:
                return
                
            visited.add(current_token)
            current_chain.append(current_token)
            
            if depth > 1:
                chains.append(current_chain.copy())
            
            # Find all tokens related to current token
            for rel_id, rel_data in relationships.items():
                if rel_data["source_token"] == current_token:
                    dfs(rel_data["target_token"], depth + 1, current_chain)
                elif rel_data["target_token"] == current_token:
                    dfs(rel_data["source_token"], depth + 1, current_chain)
            
            current_chain.pop()
            visited.remove(current_token)
        
        dfs(start_token, 1, [])
        return chains 