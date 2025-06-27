"""
Content Manager
Manages content items with hierarchical organization and relationships.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from datetime import datetime, timezone

from knowledge_base.content_types import (
    BaseContent, Note, Todo, CalendarEvent, Project, Reference, Folder,
    Relationship, RelationshipType
)
from knowledge_base.utils.helpers import (
    KnowledgeBaseError, NotFoundError, StorageError, ValidationError, 
    generate_id, get_timestamp
)
from knowledge_base.core.relationship_manager import RelationshipManager
from knowledge_base.core.hierarchy_manager import HierarchyManager

logger = logging.getLogger(__name__)


class ContentManager:
    """
    Manages content with hierarchical organization and relationships.
    
    This class handles:
    1. CRUD operations for content items
    2. Content organization in folders
    3. Relationship management between content items
    4. Content retrieval with hierarchy and relationship information
    """
    
    def __init__(
        self, 
        base_path: str = ".",
        relationship_manager: Optional[RelationshipManager] = None,
        hierarchy_manager: Optional[HierarchyManager] = None
    ):
        """
        Initialize the content manager.
        
        Args:
            base_path: Root path of the knowledge base
            relationship_manager: Optional relationship manager instance
            hierarchy_manager: Optional hierarchy manager instance
        """
        self.base_path = Path(base_path)
        self.data_dir = self.base_path / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize managers
        self.relationship_manager = relationship_manager or RelationshipManager(base_path)
        self.hierarchy_manager = hierarchy_manager or HierarchyManager(
            base_path, 
            relationship_manager=self.relationship_manager
        )
        
        # Content type directories
        self.content_dirs = {
            "note": self.data_dir / "notes",
            "todo": self.data_dir / "todos",
            "calendar": self.data_dir / "calendar",
            "project": self.data_dir / "projects",
            "reference": self.data_dir / "references",
            "folder": self.data_dir / "hierarchy"
        }
        
        # Create content directories
        for content_dir in self.content_dirs.values():
            content_dir.mkdir(parents=True, exist_ok=True)
    
    def create_content(
        self, 
        content_data: Dict[str, Any],
        content_type: str,
        parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new content item.
        
        Args:
            content_data: Content data
            content_type: Type of content
            parent_id: Optional parent folder ID
            
        Returns:
            Created content with id and path
        """
        # Create appropriate content object based on type
        if content_type == "note":
            content = Note(**content_data)
        elif content_type == "todo":
            content = Todo(**content_data)
        elif content_type == "calendar":
            content = CalendarEvent(**content_data)
        elif content_type == "project":
            content = Project(**content_data)
        elif content_type == "reference":
            content = Reference(**content_data)
        elif content_type == "folder":
            # Use hierarchy manager to create folder
            folder = self.hierarchy_manager.create_folder(
                title=content_data["title"],
                parent_id=parent_id,
                description=content_data.get("description", ""),
                icon=content_data.get("icon", "folder")
            )
            # Save folder content
            return self._save_content(folder, "folder")
        else:
            raise ValidationError(f"Invalid content type: {content_type}")
        
        # Set parent_id if provided
        if parent_id:
            content.parent_id = parent_id
        
        # Add to hierarchy if parent is specified
        if parent_id:
            # Add content to folder
            path = self.hierarchy_manager.add_content_to_folder(content.id, parent_id)
            content.path = path
            
            # Update path with actual title
            if path:
                content.path = self.hierarchy_manager.update_content_path(content.id, content.title)
        
        # Save content
        return self._save_content(content, content_type)
    
    def _save_content(self, content: BaseContent, content_type: str) -> Dict[str, Any]:
        """
        Save content to the appropriate location.
        
        Args:
            content: Content object
            content_type: Type of content
            
        Returns:
            Saved content as dictionary
        """
        content_dict = content.to_dict()
        
        # Get the appropriate directory
        content_dir = self.content_dirs.get(content_type)
        if not content_dir:
            raise ValidationError(f"Invalid content type: {content_type}")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        if content_type == "folder":
            filename = f"folder-{content.id}.json"
        else:
            filename = f"{content_type}-{timestamp}-{content.id}.json"
        
        filepath = content_dir / filename
        
        try:
            # Write content to file
            with open(filepath, 'w') as f:
                json.dump(content_dict, f, indent=2)
            
            logger.info(f"Content saved: {filepath}")
            
            # Add filepath to the returned dictionary
            content_dict["_filepath"] = str(filepath)
            
            return content_dict
        except Exception as e:
            logger.error(f"Error saving content: {e}")
            raise StorageError(f"Failed to save content: {e}")
    
    def get_content(self, content_id: str, include_relationships: bool = False) -> Dict[str, Any]:
        """
        Get content by ID.
        
        Args:
            content_id: ID of the content
            include_relationships: Include relationship information
            
        Returns:
            Content data
            
        Raises:
            NotFoundError: If the content doesn't exist
        """
        # Check all content directories
        for content_type, content_dir in self.content_dirs.items():
            for filepath in content_dir.glob(f"*-{content_id}.json"):
                try:
                    # Read content from file
                    with open(filepath, 'r') as f:
                        content = json.load(f)
                    
                    # Add filepath to the returned dictionary
                    content["_filepath"] = str(filepath)
                    content["_content_type"] = content_type
                    
                    # Include relationships if requested
                    if include_relationships:
                        relationships = self.relationship_manager.get_relationships(content_id)
                        content["_relationships"] = [rel.to_dict() for rel in relationships]
                    
                    # Include hierarchy information
                    path = self.hierarchy_manager.get_path(content_id)
                    if path:
                        content["path"] = path
                    
                    parent_id = self.hierarchy_manager.get_parent_id(content_id)
                    if parent_id:
                        content["parent_id"] = parent_id
                    
                    # Add breadcrumb if in hierarchy
                    if path:
                        content["_breadcrumb"] = self.hierarchy_manager.get_breadcrumb(content_id)
                    
                    return content
                except Exception as e:
                    logger.error(f"Error reading content {content_id}: {e}")
                    continue
        
        # Content not found
        raise NotFoundError(f"Content not found: {content_id}")
    
    def update_content(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update content by ID.
        
        Args:
            content_id: ID of the content
            updates: Fields to update
            
        Returns:
            Updated content
            
        Raises:
            NotFoundError: If the content doesn't exist
        """
        try:
            # Get current content
            content = self.get_content(content_id)
            
            # Apply updates
            for key, value in updates.items():
                # Skip special fields
                if key.startswith("_"):
                    continue
                content[key] = value
            
            # Update last_modified timestamp
            content["last_modified"] = get_timestamp()
            
            # Write back to file
            filepath = content.get("_filepath")
            if not filepath:
                raise StorageError("Missing filepath in content data")
            
            with open(filepath, 'w') as f:
                # Remove special fields before saving
                clean_content = {k: v for k, v in content.items() if not k.startswith("_")}
                json.dump(clean_content, f, indent=2)
            
            # Update path in hierarchy if title changed
            if "title" in updates and content.get("path"):
                self.hierarchy_manager.update_content_path(content_id, updates["title"])
                # Refresh path
                path = self.hierarchy_manager.get_path(content_id)
                if path:
                    content["path"] = path
            
            # Add filepath back to the returned dictionary
            content["_filepath"] = filepath
            
            return content
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating content {content_id}: {e}")
            raise StorageError(f"Failed to update content: {e}")
    
    def delete_content(self, content_id: str) -> bool:
        """
        Delete content by ID.
        
        Args:
            content_id: ID of the content
            
        Returns:
            True if content was deleted, False otherwise
        """
        try:
            # Get content first to check if it exists and get the filepath
            content = self.get_content(content_id)
            filepath = content.get("_filepath")
            
            if filepath and Path(filepath).exists():
                # Delete the file
                Path(filepath).unlink()
                
                # Clean up relationships
                self.relationship_manager.delete_all_relationships(content_id)
                
                # Remove from hierarchy
                parent_id = self.hierarchy_manager.get_parent_id(content_id)
                if parent_id:
                    # If it's a folder, delete from hierarchy
                    if content.get("_content_type") == "folder":
                        self.hierarchy_manager.delete_folder(content_id)
                    else:
                        # For regular content, just remove from parent's children
                        hierarchy = self.hierarchy_manager._load_hierarchy_index()
                        if parent_id in hierarchy and hierarchy[parent_id].get("children"):
                            if content_id in hierarchy[parent_id]["children"]:
                                hierarchy[parent_id]["children"].remove(content_id)
                                self.hierarchy_manager._save_hierarchy_index(hierarchy)
                
                return True
            
            return False
        except NotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error deleting content {content_id}: {e}")
            raise StorageError(f"Failed to delete content: {e}")
    
    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: Union[RelationshipType, str] = RelationshipType.RELATED,
        description: str = "",
        metadata: Dict[str, Any] = None
    ) -> Relationship:
        """
        Create a relationship between content items.
        
        Args:
            source_id: ID of the source content
            target_id: ID of the target content
            relationship_type: Type of relationship
            description: Relationship description
            metadata: Additional metadata
            
        Returns:
            Created relationship
            
        Raises:
            NotFoundError: If either content doesn't exist
        """
        # Verify both content items exist
        self.get_content(source_id)
        self.get_content(target_id)
        
        # Create relationship
        relationship = self.relationship_manager.create_relationship(
            source_id, target_id, relationship_type, description, metadata
        )
        
        # Update content items to include relationship reference
        try:
            source = self.get_content(source_id)
            if "relationships" not in source:
                source["relationships"] = []
            relationship_id = f"{source_id}_{target_id}"
            if relationship_id not in source["relationships"]:
                source["relationships"].append(relationship_id)
                self.update_content(source_id, {"relationships": source["relationships"]})
            
            target = self.get_content(target_id)
            if "relationships" not in target:
                target["relationships"] = []
            if relationship_id not in target["relationships"]:
                target["relationships"].append(relationship_id)
                self.update_content(target_id, {"relationships": target["relationships"]})
        except Exception as e:
            logger.error(f"Error updating content relationships: {e}")
        
        return relationship
    
    def get_related_content(
        self, 
        content_id: str,
        relationship_type: Optional[Union[RelationshipType, str]] = None,
        include_content: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get content related to the given content item.
        
        Args:
            content_id: ID of the content
            relationship_type: Optional filter by relationship type
            include_content: Include full content data (not just IDs)
            
        Returns:
            List of related content items
        """
        # Get related IDs
        related_ids = self.relationship_manager.get_related_content_ids(content_id, relationship_type)
        
        if not include_content:
            # Return just the relationship info
            result = []
            for related_id in related_ids:
                # Get the relationship
                relationships = self.relationship_manager.get_relationships(
                    content_id, 
                    as_source=(related_id != content_id),
                    as_target=(related_id == content_id)
                )
                
                for rel in relationships:
                    if (rel.source_id == content_id and rel.target_id == related_id) or \
                       (rel.source_id == related_id and rel.target_id == content_id):
                        result.append({
                            "content_id": related_id,
                            "relationship": rel.to_dict()
                        })
                        break
            
            return result
        
        # Include full content
        result = []
        for related_id in related_ids:
            try:
                related_content = self.get_content(related_id)
                
                # Get the relationship
                relationships = self.relationship_manager.get_relationships(
                    content_id,
                    as_source=(related_id != content_id),
                    as_target=(related_id == content_id)
                )
                
                for rel in relationships:
                    if (rel.source_id == content_id and rel.target_id == related_id) or \
                       (rel.source_id == related_id and rel.target_id == content_id):
                        related_content["_relationship"] = rel.to_dict()
                        break
                
                result.append(related_content)
            except NotFoundError:
                # Skip content that can't be found
                continue
            except Exception as e:
                logger.error(f"Error getting related content {related_id}: {e}")
                continue
        
        return result
    
    def move_content_to_folder(self, content_id: str, folder_id: str) -> Dict[str, Any]:
        """
        Move content to a folder.
        
        Args:
            content_id: ID of the content
            folder_id: ID of the destination folder
            
        Returns:
            Updated content
            
        Raises:
            NotFoundError: If content or folder doesn't exist
        """
        # Verify content and folder exist
        content = self.get_content(content_id)
        folder = self.get_content(folder_id)
        
        if folder.get("_content_type") != "folder":
            raise ValidationError(f"Destination is not a folder: {folder_id}")
        
        # Move content in hierarchy
        new_path = self.hierarchy_manager.move_content(content_id, folder_id)
        
        # Update content path
        content["path"] = new_path
        content["parent_id"] = folder_id
        
        # Save changes
        self.update_content(content_id, {
            "path": new_path,
            "parent_id": folder_id
        })
        
        return content
    
    def get_content_by_path(self, path: str) -> Dict[str, Any]:
        """
        Get content by path.
        
        Args:
            path: Path in hierarchy
            
        Returns:
            Content data
            
        Raises:
            NotFoundError: If content doesn't exist at path
        """
        content_id = self.hierarchy_manager.get_content_by_path(path)
        if not content_id:
            raise NotFoundError(f"Content not found at path: {path}")
        
        return self.get_content(content_id)
    
    def list_folder_contents(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        List contents of a folder.
        
        Args:
            folder_id: ID of the folder
            
        Returns:
            List of content items in the folder
            
        Raises:
            NotFoundError: If folder doesn't exist
        """
        # Verify folder exists
        folder = self.get_content(folder_id)
        
        if folder.get("_content_type") != "folder":
            raise ValidationError(f"Not a folder: {folder_id}")
        
        # Get children from hierarchy
        child_ids = self.hierarchy_manager.get_children(folder_id)
        
        # Get content for each child
        contents = []
        for child_id in child_ids:
            try:
                child_content = self.get_content(child_id)
                contents.append(child_content)
            except NotFoundError:
                # Skip content that can't be found
                continue
            except Exception as e:
                logger.error(f"Error getting child content {child_id}: {e}")
                continue
        
        return contents
    
    def get_folder_tree(self, folder_id: Optional[str] = None, max_depth: int = -1) -> Dict[str, Any]:
        """
        Get folder tree.
        
        Args:
            folder_id: ID of the root folder (None for entire hierarchy)
            max_depth: Maximum depth of the tree (-1 for unlimited)
            
        Returns:
            Dictionary representing the folder tree
        """
        return self.hierarchy_manager.build_folder_tree(folder_id, max_depth)
    
    def create_folder(
        self, 
        title: str, 
        parent_id: Optional[str] = None,
        description: str = "",
        icon: str = "folder"
    ) -> Dict[str, Any]:
        """
        Create a new folder.
        
        Args:
            title: Folder title
            parent_id: ID of the parent folder (None for root)
            description: Folder description
            icon: Folder icon
            
        Returns:
            Created folder
        """
        return self.create_content({
            "title": title,
            "description": description,
            "icon": icon
        }, "folder", parent_id=parent_id)
    
    def get_or_create_folder(
        self, 
        path: str, 
        create_intermediate: bool = True
    ) -> Dict[str, Any]:
        """
        Get a folder by path or create it if it doesn't exist.
        
        Args:
            path: Folder path (e.g., /work/projects)
            create_intermediate: Create intermediate folders if needed
            
        Returns:
            Folder content
        """
        # Check if folder already exists
        folder_id = self.hierarchy_manager.get_folder_by_path(path)
        if folder_id:
            return self.get_content(folder_id)
        
        if not create_intermediate:
            raise NotFoundError(f"Folder not found at path: {path}")
        
        # Split path into components
        components = [p for p in path.split("/") if p]
        if not components:
            # Root folder
            folder_id = self.hierarchy_manager._ensure_root_folder()
            return self.get_content(folder_id)
        
        # Start at root
        current_path = "/"
        current_folder_id = self.hierarchy_manager._ensure_root_folder()
        
        # Create folders along the path
        for component in components:
            current_path = f"{current_path}{component}/" if current_path == "/" else f"{current_path}/{component}"
            current_path = current_path.rstrip("/")
            
            folder_id = self.hierarchy_manager.get_folder_by_path(current_path)
            if folder_id:
                current_folder_id = folder_id
            else:
                # Create folder
                folder = self.create_folder(component, parent_id=current_folder_id)
                current_folder_id = folder["id"]
        
        return self.get_content(current_folder_id) 