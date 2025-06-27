"""
Semantic Search
Implements semantic search functionality using vector embeddings.
"""

import json
import logging
import os
import math
import re
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from datetime import datetime, timezone
import heapq

try:
    import sklearn.metrics.pairwise as pw
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from knowledge_base.utils.helpers import (
    KnowledgeBaseError, NotFoundError, StorageError, ValidationError
)
from knowledge_base.core.content_manager import ContentManager

logger = logging.getLogger(__name__)


class SemanticSearch:
    """
    Semantic search engine using vector embeddings.
    
    This class handles:
    1. Creating and managing vector embeddings for content
    2. Performing similarity-based search
    3. Ranking and filtering search results
    4. Integrating with external embedding services
    """
    
    def __init__(
        self, 
        base_path: str = ".", 
        content_manager: Optional[ContentManager] = None,
        embedding_dimension: int = 768,
        use_mock_embeddings: bool = False
    ):
        """
        Initialize the semantic search engine.
        
        Args:
            base_path: Root path of the knowledge base
            content_manager: Optional content manager instance
            embedding_dimension: Dimension of the embedding vectors
            use_mock_embeddings: Use mock embeddings for testing (no external dependencies)
        """
        self.base_path = Path(base_path)
        self.content_manager = content_manager or ContentManager(base_path)
        self.embedding_dimension = embedding_dimension
        self.use_mock_embeddings = use_mock_embeddings
        
        # Directory for storing embeddings
        self.embeddings_dir = self.base_path / "data" / "embeddings"
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        # Embeddings index file
        self.embeddings_index_path = self.embeddings_dir / "embeddings_index.json"
        
        # Check if sklearn is available for cosine similarity
        if not SKLEARN_AVAILABLE and not use_mock_embeddings:
            logger.warning("scikit-learn not available. Falling back to mock embeddings.")
            self.use_mock_embeddings = True
        
        # Initialize or load embeddings index
        self._ensure_index_exists()
        
    def _ensure_index_exists(self) -> None:
        """Ensure the embeddings index file exists."""
        if not self.embeddings_index_path.exists():
            # Create empty index
            self._save_index({
                "metadata": {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "embedding_dimension": self.embedding_dimension,
                    "count": 0
                },
                "embeddings": {}
            })
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the embeddings index."""
        try:
            with open(self.embeddings_index_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "metadata": {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "embedding_dimension": self.embedding_dimension,
                    "count": 0
                },
                "embeddings": {}
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid embeddings index JSON: {e}")
            # If corrupted, create a backup and start with empty index
            if self.embeddings_index_path.exists():
                backup_path = self.embeddings_index_path.with_suffix('.json.bak')
                self.embeddings_index_path.rename(backup_path)
                logger.info(f"Corrupted index backed up to {backup_path}")
            return {
                "metadata": {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "embedding_dimension": self.embedding_dimension,
                    "count": 0
                },
                "embeddings": {}
            }
        except Exception as e:
            logger.error(f"Error loading embeddings index: {e}")
            raise StorageError(f"Failed to load embeddings index: {e}")
    
    def _save_index(self, index: Dict[str, Any]) -> None:
        """Save the embeddings index."""
        try:
            with open(self.embeddings_index_path, 'w') as f:
                json.dump(index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving embeddings index: {e}")
            raise StorageError(f"Failed to save embeddings index: {e}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding vector for the given text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector as a list of floats
        """
        if self.use_mock_embeddings:
            # For testing, generate a deterministic mock embedding
            # based on the text content (hash-based)
            import hashlib
            
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            
            # Use hash to seed a random generator for deterministic output
            import random
            random.seed(hash_bytes)
            
            # Generate a mock embedding vector
            mock_embedding = [
                random.uniform(-1, 1) for _ in range(self.embedding_dimension)
            ]
            
            # Normalize the vector to unit length
            norm = math.sqrt(sum(x*x for x in mock_embedding))
            if norm > 0:
                mock_embedding = [x/norm for x in mock_embedding]
                
            return mock_embedding
        else:
            # In a real implementation, this would call an embedding service or library
            # For example, using sentence-transformers or an OpenAI API
            
            # Placeholder - should be replaced with actual embedding generation
            logger.warning("External embedding service not configured. Using mock embedding.")
            return self._generate_embedding(text)
    
    def create_content_embedding(self, content_id: str) -> bool:
        """
        Create an embedding for a content item.
        
        Args:
            content_id: ID of the content item
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get content data
            content = self.content_manager.get_content(content_id)
            
            # Extract text for embedding
            text = self._extract_text_for_embedding(content)
            
            # Generate embedding
            embedding = self._generate_embedding(text)
            
            # Store embedding
            self._store_embedding(content_id, embedding, content)
            
            return True
        except NotFoundError:
            logger.warning(f"Content not found for embedding: {content_id}")
            return False
        except Exception as e:
            logger.error(f"Error creating embedding for {content_id}: {e}")
            return False
    
    def _extract_text_for_embedding(self, content: Dict[str, Any]) -> str:
        """
        Extract text from content for embedding generation.
        
        Args:
            content: Content data dictionary
            
        Returns:
            Text for embedding generation
        """
        text_parts = []
        
        # Add title
        if "title" in content:
            text_parts.append(content["title"])
        
        # Add content based on type
        content_type = content.get("_content_type", "")
        
        if content_type == "note":
            # For notes, include the content
            if "content" in content:
                text_parts.append(content["content"])
        
        elif content_type == "todo":
            # For todos, include the description
            if "description" in content:
                text_parts.append(content["description"])
        
        elif content_type == "calendar":
            # For calendar events, include the description
            if "description" in content:
                text_parts.append(content["description"])
        
        elif content_type == "project":
            # For projects, include the description and goals
            if "description" in content:
                text_parts.append(content["description"])
            
            if "goals" in content and isinstance(content["goals"], list):
                text_parts.extend(content["goals"])
        
        elif content_type == "reference":
            # For references, include the description and notes
            if "description" in content:
                text_parts.append(content["description"])
            
            if "notes" in content:
                text_parts.append(content["notes"])
        
        # Add tags
        if "tags" in content and isinstance(content["tags"], list):
            text_parts.append(" ".join(content["tags"]))
        
        # Add category
        if "category" in content:
            text_parts.append(content["category"])
        
        # Combine all text
        return " ".join(text_parts)
    
    def _store_embedding(self, content_id: str, embedding: List[float], content: Dict[str, Any]) -> None:
        """
        Store an embedding for a content item.
        
        Args:
            content_id: ID of the content item
            embedding: Embedding vector
            content: Content data for metadata
        """
        # Load current index
        index = self._load_index()
        
        # Add or update embedding
        index["embeddings"][content_id] = {
            "vector": embedding,
            "metadata": {
                "title": content.get("title", ""),
                "content_type": content.get("_content_type", ""),
                "category": content.get("category", ""),
                "tags": content.get("tags", []),
                "path": content.get("path", ""),
                "created": content.get("created", ""),
                "last_modified": content.get("last_modified", "")
            }
        }
        
        # Update metadata
        index["metadata"]["count"] = len(index["embeddings"])
        index["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Save index
        self._save_index(index)
    
    def batch_create_embeddings(self, content_ids: List[str]) -> Dict[str, bool]:
        """
        Create embeddings for multiple content items.
        
        Args:
            content_ids: List of content IDs
            
        Returns:
            Dictionary mapping content IDs to success status
        """
        results = {}
        
        for content_id in content_ids:
            results[content_id] = self.create_content_embedding(content_id)
        
        return results
    
    def search(
        self, 
        query: str, 
        top_k: int = 10,
        content_types: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Perform a semantic search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            content_types: Optional filter by content types
            categories: Optional filter by categories
            tags: Optional filter by tags
            min_similarity: Minimum similarity score (0.0 - 1.0)
            
        Returns:
            List of search results with content and similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Load embeddings
            index = self._load_index()
            embeddings = index["embeddings"]
            
            if not embeddings:
                logger.warning("No embeddings available for search")
                return []
            
            # Calculate similarities and filter by criteria
            results = []
            
            for content_id, embedding_data in embeddings.items():
                # Get embedding vector and metadata
                vector = embedding_data["vector"]
                metadata = embedding_data["metadata"]
                
                # Filter by content type if specified
                if content_types and metadata["content_type"] not in content_types:
                    continue
                
                # Filter by category if specified
                if categories and metadata["category"] not in categories:
                    continue
                
                # Filter by tags if specified
                if tags:
                    # Check if any specified tag is in the content tags
                    content_tags = metadata["tags"]
                    if not any(tag in content_tags for tag in tags):
                        continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(query_embedding, vector)
                
                # Filter by minimum similarity
                if similarity < min_similarity:
                    continue
                
                # Add to results
                results.append({
                    "content_id": content_id,
                    "similarity": similarity,
                    "metadata": metadata
                })
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Take top k
            results = results[:top_k]
            
            # Fetch full content for results
            for result in results:
                try:
                    result["content"] = self.content_manager.get_content(result["content_id"])
                except NotFoundError:
                    # Content not found, use metadata only
                    result["content"] = {
                        "id": result["content_id"],
                        "title": result["metadata"]["title"],
                        "content_type": result["metadata"]["content_type"],
                        "_not_found": True
                    }
                except Exception as e:
                    logger.error(f"Error fetching content for {result['content_id']}: {e}")
                    result["content"] = {
                        "id": result["content_id"],
                        "title": result["metadata"]["title"],
                        "content_type": result["metadata"]["content_type"],
                        "_error": str(e)
                    }
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            raise KnowledgeBaseError(f"Semantic search failed: {e}")
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0.0 - 1.0)
        """
        if SKLEARN_AVAILABLE:
            # Use sklearn's cosine similarity
            similarity = float(pw.cosine_similarity([vec1], [vec2])[0][0])
            
            # Ensure the result is in [0, 1]
            similarity = max(0.0, min(1.0, similarity))
            
            return similarity
        else:
            # Manual cosine similarity calculation
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            
            norm_a = math.sqrt(sum(a * a for a in vec1))
            norm_b = math.sqrt(sum(b * b for b in vec2))
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
                
            similarity = dot_product / (norm_a * norm_b)
            
            # Ensure the result is in [0, 1]
            similarity = max(0.0, min(1.0, similarity))
            
            return similarity
    
    def similar_content(
        self, 
        content_id: str, 
        top_k: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find content similar to the given content item.
        
        Args:
            content_id: ID of the content item
            top_k: Number of results to return
            min_similarity: Minimum similarity score (0.0 - 1.0)
            
        Returns:
            List of similar content items with similarity scores
        """
        try:
            # Load embeddings
            index = self._load_index()
            embeddings = index["embeddings"]
            
            if content_id not in embeddings:
                # Content not in embedding index, create embedding
                if not self.create_content_embedding(content_id):
                    logger.warning(f"Could not create embedding for {content_id}")
                    return []
                
                # Reload embeddings
                index = self._load_index()
                embeddings = index["embeddings"]
            
            # Get content embedding
            content_embedding = embeddings[content_id]["vector"]
            
            # Calculate similarities
            similarities = []
            
            for other_id, embedding_data in embeddings.items():
                # Skip self
                if other_id == content_id:
                    continue
                
                # Calculate similarity
                similarity = self._calculate_similarity(content_embedding, embedding_data["vector"])
                
                # Filter by minimum similarity
                if similarity >= min_similarity:
                    similarities.append((other_id, similarity, embedding_data["metadata"]))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Take top k
            similarities = similarities[:top_k]
            
            # Build results
            results = []
            
            for other_id, similarity, metadata in similarities:
                try:
                    content = self.content_manager.get_content(other_id)
                    results.append({
                        "content_id": other_id,
                        "similarity": similarity,
                        "content": content,
                        "metadata": metadata
                    })
                except NotFoundError:
                    # Content not found, use metadata only
                    results.append({
                        "content_id": other_id,
                        "similarity": similarity,
                        "content": {
                            "id": other_id,
                            "title": metadata["title"],
                            "content_type": metadata["content_type"],
                            "_not_found": True
                        },
                        "metadata": metadata
                    })
                except Exception as e:
                    logger.error(f"Error fetching content for {other_id}: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar content: {e}")
            raise KnowledgeBaseError(f"Similar content search failed: {e}")
    
    def refresh_embeddings(
        self, 
        content_ids: Optional[List[str]] = None,
        force: bool = False
    ) -> Dict[str, bool]:
        """
        Refresh embeddings for content items.
        
        Args:
            content_ids: List of content IDs (None for all)
            force: Force refresh even if embedding exists
            
        Returns:
            Dictionary mapping content IDs to success status
        """
        try:
            # Load current index
            index = self._load_index()
            embeddings = index["embeddings"]
            
            # Get all content IDs if not specified
            if content_ids is None:
                # Load all content IDs from content manager
                # This is a simplified approximation - real implementation would need
                # a method to get all content IDs from the content manager
                content_ids = []
                
                # Extract existing content IDs from embeddings
                existing_ids = set(embeddings.keys())
                content_ids = list(existing_ids)
            
            # Track results
            results = {}
            
            for content_id in content_ids:
                # Skip if embedding exists and not forcing refresh
                if not force and content_id in embeddings:
                    results[content_id] = True
                    continue
                
                # Create or refresh embedding
                results[content_id] = self.create_content_embedding(content_id)
            
            return results
            
        except Exception as e:
            logger.error(f"Error refreshing embeddings: {e}")
            raise KnowledgeBaseError(f"Embedding refresh failed: {e}")
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the embeddings.
        
        Returns:
            Dictionary of statistics
        """
        try:
            # Load current index
            index = self._load_index()
            embeddings = index["embeddings"]
            
            # Calculate stats
            content_type_counts = {}
            category_counts = {}
            newest_embedding = None
            oldest_embedding = None
            
            for content_id, embedding_data in embeddings.items():
                metadata = embedding_data["metadata"]
                
                # Count by content type
                content_type = metadata["content_type"]
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
                
                # Count by category
                category = metadata["category"]
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # Track newest and oldest
                last_modified = metadata["last_modified"]
                
                if not newest_embedding or last_modified > newest_embedding["last_modified"]:
                    newest_embedding = {
                        "content_id": content_id,
                        "title": metadata["title"],
                        "content_type": content_type,
                        "last_modified": last_modified
                    }
                
                if not oldest_embedding or last_modified < oldest_embedding["last_modified"]:
                    oldest_embedding = {
                        "content_id": content_id,
                        "title": metadata["title"],
                        "content_type": content_type,
                        "last_modified": last_modified
                    }
            
            # Build stats
            stats = {
                "total_embeddings": len(embeddings),
                "by_content_type": content_type_counts,
                "by_category": category_counts,
                "newest_embedding": newest_embedding,
                "oldest_embedding": oldest_embedding,
                "metadata": index["metadata"]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting embedding stats: {e}")
            raise KnowledgeBaseError(f"Failed to get embedding stats: {e}")
            
    def delete_embedding(self, content_id: str) -> bool:
        """
        Delete an embedding for a content item.
        
        Args:
            content_id: ID of the content item
            
        Returns:
            True if deleted, False if not found or error
        """
        try:
            # Load current index
            index = self._load_index()
            embeddings = index["embeddings"]
            
            # Check if embedding exists
            if content_id not in embeddings:
                return False
            
            # Remove embedding
            del embeddings[content_id]
            
            # Update metadata
            index["metadata"]["count"] = len(embeddings)
            index["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # Save index
            self._save_index(index)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting embedding for {content_id}: {e}")
            return False 