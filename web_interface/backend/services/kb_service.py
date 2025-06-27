"""
Knowledge Base Service
Service layer that wraps the KnowledgeBaseManager for use in the web interface.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import os
from functools import lru_cache

from knowledge_base import KnowledgeBaseManager
from knowledge_base.privacy import PrivacyLevel, ComplianceStandard

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """Service layer for Knowledge Base operations."""
    
    def __init__(self, base_path: str = None, enable_encryption: bool = True, enable_audit_logging: bool = True):
        """
        Initialize the service with a KnowledgeBaseManager.
        
        Args:
            base_path: Path to the knowledge base directory
            enable_encryption: Whether to enable encryption
            enable_audit_logging: Whether to enable audit logging
        """
        # Determine base path
        if base_path is None:
            # Try to use environment variable
            base_path = os.environ.get("KB_BASE_PATH", ".")
        
        logger.info(f"Initializing KnowledgeBaseService with base_path: {base_path}")
        
        # Initialize the manager
        self.manager = KnowledgeBaseManager(
            base_path=base_path,
            enable_encryption=enable_encryption,
            enable_audit_logging=enable_audit_logging
        )
        
        logger.info("KnowledgeBaseService initialized successfully")
    
    # Content Management Methods
    
    def create_content(self, content_data: Dict[str, Any], content_type: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new content item.
        
        Args:
            content_data: Content data
            content_type: Type of content
            parent_id: Optional parent folder ID
            
        Returns:
            Created content
        """
        return self.manager.create_content(content_data, content_type, parent_id)
    
    def get_content(self, content_id: str, include_relationships: bool = False) -> Dict[str, Any]:
        """
        Get content by ID.
        
        Args:
            content_id: ID of the content
            include_relationships: Whether to include relationship information
            
        Returns:
            Content data
        """
        return self.manager.get_content(content_id, include_relationships)
    
    def update_content(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update content by ID.
        
        Args:
            content_id: ID of the content
            updates: Fields to update
            
        Returns:
            Updated content
        """
        return self.manager.update_content(content_id, updates)
    
    def delete_content(self, content_id: str) -> bool:
        """
        Delete content by ID.
        
        Args:
            content_id: ID of the content
            
        Returns:
            True if content was deleted
        """
        return self.manager.delete_content(content_id)
    
    # Folder Management Methods
    
    def create_folder(self, title: str, parent_id: Optional[str] = None, description: str = "", icon: str = "folder") -> Dict[str, Any]:
        """
        Create a new folder.
        
        Args:
            title: Folder title
            parent_id: ID of the parent folder
            description: Folder description
            icon: Folder icon
            
        Returns:
            Created folder
        """
        return self.manager.create_folder(title, parent_id, description, icon)
    
    def get_folder_tree(self, folder_id: Optional[str] = None, max_depth: int = -1) -> Dict[str, Any]:
        """
        Get a folder tree.
        
        Args:
            folder_id: ID of the root folder
            max_depth: Maximum depth of the tree
            
        Returns:
            Dictionary representing the folder tree
        """
        return self.manager.get_folder_tree(folder_id, max_depth)
    
    def list_folder_contents(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        List contents of a folder.
        
        Args:
            folder_id: ID of the folder
            
        Returns:
            List of content items in the folder
        """
        return self.manager.list_folder_contents(folder_id)
    
    def move_content_to_folder(self, content_id: str, folder_id: str) -> Dict[str, Any]:
        """
        Move content to a folder.
        
        Args:
            content_id: ID of the content
            folder_id: ID of the destination folder
            
        Returns:
            Updated content
        """
        return self.manager.move_content_to_folder(content_id, folder_id)
    
    # Search Methods
    
    def search_content(self, query: str, content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search content using text matching.
        
        Args:
            query: Search query
            content_type: Optional content type filter
            
        Returns:
            List of search results
        """
        return self.manager.search_content(query, content_type)
    
    def search_semantic(
        self,
        query: str,
        top_k: int = 10,
        content_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            content_types: Optional filter by content types
            categories: Optional filter by categories
            tags: Optional filter by tags
            min_similarity: Minimum similarity score
            
        Returns:
            List of search results with similarity scores
        """
        return self.manager.search_semantic(query, top_k, content_types, categories, tags, min_similarity)
    
    def similar_content(self, content_id: str, top_k: int = 5, min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find content similar to the specified content item.
        
        Args:
            content_id: ID of the content
            top_k: Number of results to return
            min_similarity: Minimum similarity score
            
        Returns:
            List of similar content items with similarity scores
        """
        return self.manager.similar_content(content_id, top_k, min_similarity)
    
    def get_search_suggestions(self, query: str, max_suggestions: int = 5) -> List[Dict[str, Any]]:
        """
        Get search suggestions based on partial query.
        
        Args:
            query: Partial search query
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of search suggestions
        """
        # This is a simplified implementation
        # In a real app, you might use more sophisticated logic
        suggestions = []
        
        # Try to find content with titles matching the query
        results = self.search_content(query)
        
        for result in results[:max_suggestions]:
            content_type = result.get("type", "")
            title = result.get("content_preview", "").split("\n")[0][:50]
            
            suggestions.append({
                "type": "content",
                "content_type": content_type,
                "title": title,
                "file": result.get("file", "")
            })
        
        return suggestions
    
    # Privacy Methods
    
    def encrypt_content(self, content: Union[str, Dict[str, Any]], searchable_fields: List[str] = None) -> Dict[str, Any]:
        """
        Encrypt content while preserving searchable fields.
        
        Args:
            content: Content to encrypt
            searchable_fields: Fields to keep searchable
            
        Returns:
            Encrypted content metadata
        """
        return self.manager.encrypt_content(content, searchable_fields)
    
    def decrypt_content(self, encrypted_data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        Decrypt encrypted content.
        
        Args:
            encrypted_data: Encrypted content data
            
        Returns:
            Decrypted content
        """
        return self.manager.decrypt_content(encrypted_data)
    
    def set_content_privacy(
        self, 
        content_id: str, 
        privacy_level: Union[PrivacyLevel, str],
        inherit_from: str = None, 
        override_parent: bool = False
    ) -> Dict[str, Any]:
        """
        Set privacy settings for content.
        
        Args:
            content_id: Content ID
            privacy_level: Privacy level to set
            inherit_from: Parent content ID for inheritance
            override_parent: Whether to override parent settings
            
        Returns:
            Privacy settings
        """
        # Convert string to enum if needed
        if isinstance(privacy_level, str):
            privacy_level = PrivacyLevel[privacy_level.upper()]
            
        return self.manager.set_content_privacy(content_id, privacy_level, inherit_from, override_parent)
    
    # Process Methods
    
    def process_stream_of_consciousness(self, content: str) -> Dict[str, Any]:
        """
        Process stream of consciousness input.
        
        Args:
            content: Raw text input from user
            
        Returns:
            Dictionary containing organized content and metadata
        """
        return self.manager.process_stream_of_consciousness(content)
    
    def process_with_privacy(self, content: str, session_id: str = None, privacy_level: str = "balanced") -> Dict[str, Any]:
        """
        Process content with privacy preservation.
        
        Args:
            content: Raw text input from user
            session_id: Privacy session ID (created if None)
            privacy_level: Privacy level for anonymization
            
        Returns:
            Dictionary containing organized content and privacy metadata
        """
        return self.manager.process_with_privacy(content, session_id, privacy_level)
    
    def process_and_respond(self, content: str, session_id: str = None) -> Dict[str, Any]:
        """
        Process content with privacy and generate intelligent response.
        
        Args:
            content: Raw text input from user
            session_id: Privacy session ID (created if None)
            
        Returns:
            Dictionary with processing results and response
        """
        return self.manager.process_and_respond(content, session_id)
    
    # Recommendation Methods
    
    def get_recommendations(self, content_id: str, max_items: int = 5) -> List[Dict[str, Any]]:
        """
        Get recommended content items related to the specified item.
        
        Args:
            content_id: ID of the content
            max_items: Maximum number of recommendations
            
        Returns:
            List of recommended content items
        """
        return self.manager.get_recommendations(content_id, max_items)
    
    # Knowledge Graph Methods
    
    def build_knowledge_graph(self, root_ids: Optional[List[str]] = None, max_depth: int = 2) -> Dict[str, Any]:
        """
        Build a graph representation of content relationships.
        
        Args:
            root_ids: List of root content IDs (None for all)
            max_depth: Maximum depth of graph
            
        Returns:
            Graph representation
        """
        return self.manager.build_knowledge_graph(root_ids, max_depth)


@lru_cache
def get_kb_service() -> KnowledgeBaseService:
    """
    Get or create a KnowledgeBaseService instance.
    
    Returns:
        Singleton KnowledgeBaseService instance
    """
    # Use environment variables for configuration
    base_path = os.environ.get("KB_BASE_PATH", ".")
    enable_encryption = os.environ.get("KB_ENABLE_ENCRYPTION", "true").lower() == "true"
    enable_audit_logging = os.environ.get("KB_ENABLE_AUDIT_LOGGING", "true").lower() == "true"
    
    return KnowledgeBaseService(
        base_path=base_path,
        enable_encryption=enable_encryption,
        enable_audit_logging=enable_audit_logging
    ) 