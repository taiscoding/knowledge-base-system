"""
Relationship Manager
Manages relationships between content items in the knowledge base.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
from datetime import datetime, timezone

from knowledge_base.content_types import Relationship, RelationshipType, BaseContent
from knowledge_base.utils.helpers import (
    KnowledgeBaseError, NotFoundError, StorageError, ValidationError
)

logger = logging.getLogger(__name__)


class RelationshipManager:
    """
    Manages relationships between content items.
    
    This class handles:
    1. Creating relationships between content items
    2. Retrieving relationships and related content
    3. Updating relationship metadata
    4. Deleting relationships
    5. Validating relationship integrity
    """
    
    def __init__(self, base_path: str = ".", storage_dir: str = "data/relationships"):
        """
        Initialize the relationship manager.
        
        Args:
            base_path: Root path of the knowledge base
            storage_dir: Directory for relationship storage
        """
        self.base_path = Path(base_path)
        self.relationships_dir = self.base_path / storage_dir
        self.relationships_dir.mkdir(parents=True, exist_ok=True)
        self.relationships_index_path = self.relationships_dir / "relationships_index.json"
        self._ensure_index_exists()
        
    def _ensure_index_exists(self) -> None:
        """Ensure the relationships index file exists."""
        if not self.relationships_index_path.exists():
            # Create empty index
            self._save_index({})
    
    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load the relationships index."""
        try:
            with open(self.relationships_index_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid relationships index JSON: {e}")
            # If corrupted, create a backup and start with empty index
            if self.relationships_index_path.exists():
                backup_path = self.relationships_index_path.with_suffix('.json.bak')
                self.relationships_index_path.rename(backup_path)
                logger.info(f"Corrupted index backed up to {backup_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading relationships index: {e}")
            raise StorageError(f"Failed to load relationships index: {e}")
    
    def _save_index(self, index: Dict[str, Dict[str, Any]]) -> None:
        """Save the relationships index."""
        try:
            with open(self.relationships_index_path, 'w') as f:
                json.dump(index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving relationships index: {e}")
            raise StorageError(f"Failed to save relationships index: {e}")
    
    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: Union[RelationshipType, str] = RelationshipType.RELATED,
        description: str = "",
        metadata: Dict[str, Any] = None
    ) -> Relationship:
        """
        Create a new relationship between two content items.
        
        Args:
            source_id: ID of the source content item
            target_id: ID of the target content item
            relationship_type: Type of relationship
            description: Optional description of the relationship
            metadata: Additional metadata for the relationship
            
        Returns:
            The created Relationship object
        """
        if metadata is None:
            metadata = {}

        # Convert string to enum if needed
        if isinstance(relationship_type, str):
            try:
                relationship_type = RelationshipType(relationship_type)
            except ValueError:
                logger.warning(f"Invalid relationship type: {relationship_type}. Using RELATED.")
                relationship_type = RelationshipType.RELATED

        # Create the relationship object
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            description=description,
            metadata=metadata
        )
        
        # Save the relationship
        self._save_relationship(relationship)
        
        return relationship
    
    def _save_relationship(self, relationship: Relationship) -> None:
        """
        Save a relationship to the index and update related content items.
        
        Args:
            relationship: Relationship object to save
        """
        index = self._load_index()
        relationship_dict = relationship.to_dict()
        index[relationship.source_id + "_" + relationship.target_id] = relationship_dict
        
        # Update the index
        self._save_index(index)
        
        # Note: Content items would be updated separately by the calling code
        # through the content manager or knowledge base manager
    
    def get_relationships(
        self, 
        content_id: str, 
        relationship_type: Optional[Union[RelationshipType, str]] = None,
        as_source: bool = True,
        as_target: bool = True
    ) -> List[Relationship]:
        """
        Get relationships for a content item.
        
        Args:
            content_id: ID of the content item
            relationship_type: Optional filter by relationship type
            as_source: Include relationships where the content is the source
            as_target: Include relationships where the content is the target
            
        Returns:
            List of relationships involving the content item
        """
        index = self._load_index()
        relationships = []
        
        # Convert string to enum if needed
        if isinstance(relationship_type, str):
            try:
                relationship_type = RelationshipType(relationship_type)
            except ValueError:
                logger.warning(f"Invalid relationship type filter: {relationship_type}")
                return []
        
        for rel_id, rel_data in index.items():
            rel_type = rel_data.get("relationship_type")
            
            # Check if type matches filter
            if relationship_type and rel_type != relationship_type.value:
                continue
                
            # Check if content is involved in this relationship
            source_matches = as_source and rel_data.get("source_id") == content_id
            target_matches = as_target and rel_data.get("target_id") == content_id
            
            if source_matches or target_matches:
                # Convert back to enum
                rel_enum_type = RelationshipType(rel_data.get("relationship_type"))
                relationship = Relationship(
                    source_id=rel_data.get("source_id"),
                    target_id=rel_data.get("target_id"),
                    relationship_type=rel_enum_type,
                    description=rel_data.get("description", ""),
                    created=rel_data.get("created"),
                    metadata=rel_data.get("metadata", {})
                )
                relationships.append(relationship)
        
        return relationships
    
    def get_related_content_ids(
        self, 
        content_id: str, 
        relationship_type: Optional[Union[RelationshipType, str]] = None,
        as_source: bool = True,
        as_target: bool = True
    ) -> Set[str]:
        """
        Get IDs of content items related to the given content item.
        
        Args:
            content_id: ID of the content item
            relationship_type: Optional filter by relationship type
            as_source: Include targets where the content is the source
            as_target: Include sources where the content is the target
            
        Returns:
            Set of related content IDs
        """
        relationships = self.get_relationships(
            content_id, 
            relationship_type=relationship_type,
            as_source=as_source,
            as_target=as_target
        )
        
        related_ids = set()
        for relationship in relationships:
            if relationship.source_id == content_id:
                related_ids.add(relationship.target_id)
            else:
                related_ids.add(relationship.source_id)
        
        return related_ids
    
    def update_relationship(
        self,
        source_id: str,
        target_id: str,
        description: Optional[str] = None,
        relationship_type: Optional[Union[RelationshipType, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Relationship:
        """
        Update an existing relationship.
        
        Args:
            source_id: ID of the source content item
            target_id: ID of the target content item
            description: New description (if updating)
            relationship_type: New relationship type (if updating)
            metadata: New or updated metadata (if updating)
            
        Returns:
            The updated Relationship object
            
        Raises:
            NotFoundError: If the relationship doesn't exist
        """
        index = self._load_index()
        rel_id = source_id + "_" + target_id
        
        if rel_id not in index:
            raise NotFoundError(f"Relationship not found: {rel_id}")
        
        rel_data = index[rel_id]
        
        # Update fields if provided
        if description is not None:
            rel_data["description"] = description
            
        if relationship_type is not None:
            if isinstance(relationship_type, str):
                try:
                    relationship_type = RelationshipType(relationship_type)
                except ValueError:
                    logger.warning(f"Invalid relationship type: {relationship_type}. Not updating.")
                else:
                    rel_data["relationship_type"] = relationship_type.value
            else:
                rel_data["relationship_type"] = relationship_type.value
        
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise ValidationError("Metadata must be a dictionary")
            rel_data["metadata"] = metadata
        
        # Save updated index
        self._save_index(index)
        
        # Convert data back to Relationship object
        rel_enum_type = RelationshipType(rel_data.get("relationship_type"))
        updated_relationship = Relationship(
            source_id=rel_data.get("source_id"),
            target_id=rel_data.get("target_id"),
            relationship_type=rel_enum_type,
            description=rel_data.get("description", ""),
            created=rel_data.get("created"),
            metadata=rel_data.get("metadata", {})
        )
        
        return updated_relationship
    
    def delete_relationship(self, source_id: str, target_id: str) -> bool:
        """
        Delete a relationship.
        
        Args:
            source_id: ID of the source content item
            target_id: ID of the target content item
            
        Returns:
            True if the relationship was deleted, False if it doesn't exist
        """
        index = self._load_index()
        rel_id = source_id + "_" + target_id
        
        if rel_id in index:
            del index[rel_id]
            self._save_index(index)
            return True
        
        return False
    
    def delete_all_relationships(self, content_id: str) -> int:
        """
        Delete all relationships involving a content item.
        
        Args:
            content_id: ID of the content item
            
        Returns:
            Number of relationships deleted
        """
        index = self._load_index()
        relationships_to_delete = []
        
        # Find all relationships involving the content item
        for rel_id, rel_data in index.items():
            if rel_data["source_id"] == content_id or rel_data["target_id"] == content_id:
                relationships_to_delete.append(rel_id)
        
        # Delete the relationships
        for rel_id in relationships_to_delete:
            del index[rel_id]
        
        # Save the updated index
        self._save_index(index)
        
        return len(relationships_to_delete)
    
    def get_relationship_count(self, content_id: str) -> int:
        """
        Get the number of relationships involving a content item.
        
        Args:
            content_id: ID of the content item
            
        Returns:
            Number of relationships
        """
        return len(self.get_relationships(content_id))
    
    def exists(self, source_id: str, target_id: str) -> bool:
        """
        Check if a relationship exists.
        
        Args:
            source_id: ID of the source content item
            target_id: ID of the target content item
            
        Returns:
            True if the relationship exists, False otherwise
        """
        index = self._load_index()
        rel_id = source_id + "_" + target_id
        return rel_id in index 