"""
Hierarchy Manager
Manages hierarchical organization of content in the knowledge base.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union

from knowledge_base.content_types import Folder, BaseContent, RelationshipType
from knowledge_base.utils.helpers import (
    KnowledgeBaseError, NotFoundError, StorageError, ValidationError
)
from knowledge_base.core.relationship_manager import RelationshipManager

logger = logging.getLogger(__name__)


class HierarchyManager:
    """
    Manages hierarchical organization of content.
    
    This class handles:
    1. Creating and managing folders
    2. Building folder trees
    3. Moving content between folders
    4. Maintaining paths for content items
    5. Navigating through the content hierarchy
    """
    
    def __init__(self, base_path: str = ".", relationship_manager: Optional[RelationshipManager] = None):
        """
        Initialize the hierarchy manager.
        
        Args:
            base_path: Root path of the knowledge base
            relationship_manager: Optional relationship manager instance
        """
        self.base_path = Path(base_path)
        
        # Initialize or use provided relationship manager
        self.relationship_manager = relationship_manager or RelationshipManager(base_path)
        
        # Path to hierarchy index
        self.hierarchy_dir = self.base_path / "data/hierarchy"
        self.hierarchy_dir.mkdir(parents=True, exist_ok=True)
        self.hierarchy_index_path = self.hierarchy_dir / "hierarchy_index.json"
        
        # Ensure root folder exists
        self._ensure_root_folder()
    
    def _ensure_root_folder(self) -> str:
        """
        Ensure the root folder exists. Create if not.
        
        Returns:
            ID of the root folder
        """
        # Load hierarchy index
        hierarchy = self._load_hierarchy_index()
        
        # Check if root folder exists
        if "root" not in hierarchy:
            # Create root folder
            root_folder = Folder(
                title="Root",
                description="Root folder",
                path="/"
            )
            root_id = root_folder.id
            
            # Add to hierarchy
            hierarchy["root"] = root_id
            hierarchy[root_id] = {
                "id": root_id,
                "title": root_folder.title,
                "path": "/",
                "parent_id": None,
                "children": []
            }
            
            # Save hierarchy index
            self._save_hierarchy_index(hierarchy)
            
            # Root folder will be saved by calling code
            return root_id
        
        return hierarchy["root"]
    
    def _load_hierarchy_index(self) -> Dict[str, Any]:
        """Load the hierarchy index."""
        try:
            if not self.hierarchy_index_path.exists():
                return {}
                
            with open(self.hierarchy_index_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid hierarchy index JSON: {e}")
            # If corrupted, create a backup and start with empty index
            if self.hierarchy_index_path.exists():
                backup_path = self.hierarchy_index_path.with_suffix('.json.bak')
                self.hierarchy_index_path.rename(backup_path)
                logger.info(f"Corrupted index backed up to {backup_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading hierarchy index: {e}")
            raise StorageError(f"Failed to load hierarchy index: {e}")
    
    def _save_hierarchy_index(self, hierarchy: Dict[str, Any]) -> None:
        """Save the hierarchy index."""
        try:
            with open(self.hierarchy_index_path, 'w') as f:
                json.dump(hierarchy, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving hierarchy index: {e}")
            raise StorageError(f"Failed to save hierarchy index: {e}")
    
    def create_folder(
        self, 
        title: str, 
        parent_id: Optional[str] = None,
        description: str = "",
        icon: str = "folder"
    ) -> Folder:
        """
        Create a new folder.
        
        Args:
            title: Folder title
            parent_id: ID of the parent folder (None for root)
            description: Folder description
            icon: Folder icon
            
        Returns:
            The created Folder object
        """
        hierarchy = self._load_hierarchy_index()
        
        # If no parent specified, use root
        if parent_id is None:
            parent_id = hierarchy.get("root")
            if parent_id is None:
                parent_id = self._ensure_root_folder()
        
        # Validate parent exists
        if parent_id not in hierarchy:
            raise NotFoundError(f"Parent folder not found: {parent_id}")
        
        # Generate path
        parent_path = hierarchy[parent_id]["path"]
        path = f"{parent_path}/{title}" if parent_path != "/" else f"/{title}"
        
        # Create folder
        folder = Folder(
            title=title,
            description=description,
            icon=icon,
            parent_id=parent_id,
            path=path
        )
        
        # Update hierarchy index
        hierarchy[folder.id] = {
            "id": folder.id,
            "title": folder.title,
            "path": path,
            "parent_id": parent_id,
            "children": []
        }
        
        # Update parent's children
        hierarchy[parent_id]["children"].append(folder.id)
        
        # Create parent-child relationship
        self.relationship_manager.create_relationship(
            parent_id,
            folder.id,
            relationship_type=RelationshipType.PARENT_CHILD,
            description="Parent folder relationship"
        )
        
        # Save hierarchy index
        self._save_hierarchy_index(hierarchy)
        
        return folder
    
    def add_content_to_folder(self, content_id: str, folder_id: str) -> str:
        """
        Add content to a folder.
        
        Args:
            content_id: ID of the content to add
            folder_id: ID of the folder
            
        Returns:
            Path of the content in the hierarchy
        """
        hierarchy = self._load_hierarchy_index()
        
        # Validate folder exists
        if folder_id not in hierarchy:
            raise NotFoundError(f"Folder not found: {folder_id}")
        
        # Update folder's children
        if content_id not in hierarchy[folder_id]["children"]:
            hierarchy[folder_id]["children"].append(content_id)
        
        # Add content to hierarchy index if not already there
        if content_id not in hierarchy:
            folder_path = hierarchy[folder_id]["path"]
            # Note: We don't know the content title here, it will be updated later
            hierarchy[content_id] = {
                "id": content_id,
                "path": f"{folder_path}/<item>",
                "parent_id": folder_id,
                "children": []
            }
        
        # Create parent-child relationship
        self.relationship_manager.create_relationship(
            folder_id,
            content_id,
            relationship_type=RelationshipType.PARENT_CHILD,
            description="Folder membership"
        )
        
        # Save hierarchy index
        self._save_hierarchy_index(hierarchy)
        
        return hierarchy[content_id]["path"]
    
    def update_content_path(self, content_id: str, title: str) -> str:
        """
        Update content path in the hierarchy with the correct title.
        
        Args:
            content_id: ID of the content
            title: Title of the content
            
        Returns:
            Updated path
        """
        hierarchy = self._load_hierarchy_index()
        
        # If content not in hierarchy, do nothing
        if content_id not in hierarchy:
            return ""
        
        # Update path with actual title
        parent_id = hierarchy[content_id]["parent_id"]
        if parent_id:
            parent_path = hierarchy[parent_id]["path"]
            path = f"{parent_path}/{title}" if parent_path != "/" else f"/{title}"
            hierarchy[content_id]["path"] = path
            hierarchy[content_id]["title"] = title
            
            # Save hierarchy index
            self._save_hierarchy_index(hierarchy)
            return path
        
        return ""
    
    def move_content(self, content_id: str, new_parent_id: str) -> str:
        """
        Move content to a different folder.
        
        Args:
            content_id: ID of the content to move
            new_parent_id: ID of the new parent folder
            
        Returns:
            New path of the content
        """
        hierarchy = self._load_hierarchy_index()
        
        # Validate content and new parent exist
        if content_id not in hierarchy:
            raise NotFoundError(f"Content not found: {content_id}")
        if new_parent_id not in hierarchy:
            raise NotFoundError(f"Parent folder not found: {new_parent_id}")
        
        # Remove from current parent's children
        current_parent_id = hierarchy[content_id]["parent_id"]
        if current_parent_id and current_parent_id in hierarchy:
            if content_id in hierarchy[current_parent_id]["children"]:
                hierarchy[current_parent_id]["children"].remove(content_id)
        
        # Add to new parent's children
        if content_id not in hierarchy[new_parent_id]["children"]:
            hierarchy[new_parent_id]["children"].append(content_id)
        
        # Update content's parent and path
        hierarchy[content_id]["parent_id"] = new_parent_id
        parent_path = hierarchy[new_parent_id]["path"]
        title = hierarchy[content_id].get("title", "<item>")
        path = f"{parent_path}/{title}" if parent_path != "/" else f"/{title}"
        hierarchy[content_id]["path"] = path
        
        # Update relationships - replace old parent-child relationship
        if current_parent_id:
            self.relationship_manager.delete_relationship(current_parent_id, content_id)
        
        self.relationship_manager.create_relationship(
            new_parent_id,
            content_id,
            relationship_type=RelationshipType.PARENT_CHILD,
            description="Folder membership"
        )
        
        # Save hierarchy index
        self._save_hierarchy_index(hierarchy)
        
        return path
    
    def get_children(self, folder_id: str) -> List[str]:
        """
        Get children of a folder.
        
        Args:
            folder_id: ID of the folder
            
        Returns:
            List of child content IDs
        """
        hierarchy = self._load_hierarchy_index()
        
        # Validate folder exists
        if folder_id not in hierarchy:
            raise NotFoundError(f"Folder not found: {folder_id}")
        
        return hierarchy[folder_id].get("children", [])
    
    def get_path(self, content_id: str) -> str:
        """
        Get path of content in the hierarchy.
        
        Args:
            content_id: ID of the content
            
        Returns:
            Path of the content
        """
        hierarchy = self._load_hierarchy_index()
        
        # Validate content exists in hierarchy
        if content_id not in hierarchy:
            return ""
        
        return hierarchy[content_id].get("path", "")
    
    def get_parent_id(self, content_id: str) -> Optional[str]:
        """
        Get parent ID of content in the hierarchy.
        
        Args:
            content_id: ID of the content
            
        Returns:
            ID of the parent folder or None
        """
        hierarchy = self._load_hierarchy_index()
        
        # Validate content exists in hierarchy
        if content_id not in hierarchy:
            return None
        
        return hierarchy[content_id].get("parent_id")
    
    def get_folder_by_path(self, path: str) -> Optional[str]:
        """
        Get folder ID by path.
        
        Args:
            path: Path to look up
            
        Returns:
            ID of the folder or None if not found
        """
        hierarchy = self._load_hierarchy_index()
        
        # Handle root path
        if path == "/":
            return hierarchy.get("root")
        
        # Look for the path in the hierarchy
        for content_id, content_data in hierarchy.items():
            if content_id != "root" and content_data.get("path") == path:
                return content_id
        
        return None
    
    def get_content_by_path(self, path: str) -> Optional[str]:
        """
        Get content ID by path.
        
        Args:
            path: Path to look up
            
        Returns:
            ID of the content or None if not found
        """
        # Same implementation as get_folder_by_path but included for clarity
        return self.get_folder_by_path(path)
    
    def delete_folder(self, folder_id: str, recursive: bool = False) -> bool:
        """
        Delete a folder.
        
        Args:
            folder_id: ID of the folder to delete
            recursive: If True, delete all children recursively
            
        Returns:
            True if the folder was deleted, False otherwise
            
        Raises:
            ValidationError: If the folder has children and recursive is False
        """
        hierarchy = self._load_hierarchy_index()
        
        # Validate folder exists
        if folder_id not in hierarchy:
            return False
        
        # Check for root folder
        if hierarchy.get("root") == folder_id:
            raise ValidationError("Cannot delete root folder")
        
        # Check for children
        children = hierarchy[folder_id].get("children", [])
        if children and not recursive:
            raise ValidationError(f"Folder has {len(children)} children. Set recursive=True to delete.")
        
        # Recursively delete children if required
        if recursive:
            for child_id in list(children):  # Use list() to avoid modification during iteration
                if child_id in hierarchy and len(hierarchy[child_id].get("children", [])) > 0:
                    # It's a folder
                    self.delete_folder(child_id, recursive=True)
                else:
                    # It's a content item - just remove from hierarchy
                    if child_id in hierarchy:
                        del hierarchy[child_id]
                    
                    # Delete relationship with parent
                    self.relationship_manager.delete_relationship(folder_id, child_id)
        
        # Remove from parent's children
        parent_id = hierarchy[folder_id].get("parent_id")
        if parent_id and parent_id in hierarchy:
            if folder_id in hierarchy[parent_id]["children"]:
                hierarchy[parent_id]["children"].remove(folder_id)
        
        # Delete folder's relationships
        self.relationship_manager.delete_all_relationships(folder_id)
        
        # Delete folder from hierarchy
        del hierarchy[folder_id]
        
        # Save hierarchy index
        self._save_hierarchy_index(hierarchy)
        
        return True
    
    def get_breadcrumb(self, content_id: str) -> List[Dict[str, str]]:
        """
        Get breadcrumb path for content.
        
        Args:
            content_id: ID of the content
            
        Returns:
            List of dictionaries with id, title, path for each level in the hierarchy
        """
        hierarchy = self._load_hierarchy_index()
        
        # Validate content exists in hierarchy
        if content_id not in hierarchy:
            return []
        
        breadcrumb = []
        current_id = content_id
        
        # Prevent infinite loops
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            
            if current_id not in hierarchy:
                break
                
            current_item = hierarchy[current_id]
            breadcrumb.insert(0, {
                "id": current_id,
                "title": current_item.get("title", "<unknown>"),
                "path": current_item.get("path", "")
            })
            
            # Move up to parent
            current_id = current_item.get("parent_id")
            
            # Stop if we reach root or a cycle
            if current_id is None or current_id in visited:
                break
        
        return breadcrumb
    
    def build_folder_tree(self, folder_id: Optional[str] = None, max_depth: int = -1) -> Dict[str, Any]:
        """
        Build a tree representation of the folder structure.
        
        Args:
            folder_id: ID of the root folder (None for entire hierarchy)
            max_depth: Maximum depth of the tree (-1 for unlimited)
            
        Returns:
            Dictionary representing the folder tree
        """
        hierarchy = self._load_hierarchy_index()
        
        # Use root if folder_id is None
        if folder_id is None:
            folder_id = hierarchy.get("root")
            if folder_id is None:
                return {}
        
        # Validate folder exists
        if folder_id not in hierarchy:
            return {}
        
        # Build tree recursively
        return self._build_tree_node(folder_id, hierarchy, 0, max_depth)
    
    def _build_tree_node(
        self, 
        node_id: str, 
        hierarchy: Dict[str, Any],
        depth: int,
        max_depth: int
    ) -> Dict[str, Any]:
        """
        Build a tree node recursively.
        
        Args:
            node_id: ID of the current node
            hierarchy: Hierarchy index
            depth: Current depth in the tree
            max_depth: Maximum depth to traverse
            
        Returns:
            Dictionary representing the node and its children
        """
        # Check if we've reached max depth
        if max_depth >= 0 and depth > max_depth:
            return {}
            
        # Get node data
        if node_id not in hierarchy:
            return {}
            
        node_data = hierarchy[node_id]
        
        # Create result node
        result = {
            "id": node_id,
            "title": node_data.get("title", "<unknown>"),
            "path": node_data.get("path", ""),
            "type": "folder",  # Assuming nodes in hierarchy are folders
            "children": []
        }
        
        # Add children recursively if not at max depth
        if max_depth < 0 or depth < max_depth:
            for child_id in node_data.get("children", []):
                # Check if child exists in hierarchy
                if child_id in hierarchy:
                    # Recursive call
                    child_node = self._build_tree_node(
                        child_id, 
                        hierarchy, 
                        depth + 1, 
                        max_depth
                    )
                    if child_node:
                        result["children"].append(child_node)
                else:
                    # Child is likely a content item, not a folder
                    result["children"].append({
                        "id": child_id,
                        "type": "content",
                        "title": "<unknown>"  # Content title is not stored in hierarchy
                    })
        
        return result 