"""
Recommendation Engine
Provides content recommendations based on relationships and semantic similarity.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter

from knowledge_base.utils.helpers import (
    KnowledgeBaseError, NotFoundError, StorageError, ValidationError
)
from knowledge_base.core.content_manager import ContentManager
from knowledge_base.core.semantic_search import SemanticSearch
from knowledge_base.core.relationship_manager import RelationshipManager
from knowledge_base.content_types import RelationshipType

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Recommendation engine for knowledge base content.
    
    This class handles:
    1. Generating content recommendations based on relationships
    2. Finding related items based on semantic similarity
    3. Providing contextual suggestions based on current content
    4. Tracking user interactions to improve recommendations
    """
    
    def __init__(
        self, 
        base_path: str = ".",
        content_manager: Optional[ContentManager] = None,
        semantic_search: Optional[SemanticSearch] = None,
        relationship_manager: Optional[RelationshipManager] = None
    ):
        """
        Initialize the recommendation engine.
        
        Args:
            base_path: Root path of the knowledge base
            content_manager: Optional content manager instance
            semantic_search: Optional semantic search instance
            relationship_manager: Optional relationship manager instance
        """
        self.base_path = Path(base_path)
        
        # Initialize or use provided components
        self.content_manager = content_manager or ContentManager(base_path)
        self.relationship_manager = relationship_manager or RelationshipManager(base_path)
        self.semantic_search = semantic_search or SemanticSearch(base_path, content_manager=self.content_manager)
        
        # Directory for storing recommendation data
        self.recommendations_dir = self.base_path / "data" / "recommendations"
        self.recommendations_dir.mkdir(parents=True, exist_ok=True)
        
        # User interactions file
        self.interactions_path = self.recommendations_dir / "interactions.json"
        
        # Initialize user interactions file if needed
        self._ensure_interactions_file()
    
    def _ensure_interactions_file(self) -> None:
        """Ensure the user interactions file exists."""
        if not self.interactions_path.exists():
            # Create empty interactions file
            self._save_interactions({
                "metadata": {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "count": 0
                },
                "interactions": []
            })
    
    def _load_interactions(self) -> Dict[str, Any]:
        """Load user interactions."""
        try:
            if not self.interactions_path.exists():
                return {
                    "metadata": {
                        "created": datetime.now(timezone.utc).isoformat(),
                        "count": 0
                    },
                    "interactions": []
                }
                
            with open(self.interactions_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid interactions JSON: {e}")
            # If corrupted, create a backup and start with empty interactions
            if self.interactions_path.exists():
                backup_path = self.interactions_path.with_suffix('.json.bak')
                self.interactions_path.rename(backup_path)
                logger.info(f"Corrupted interactions backed up to {backup_path}")
            return {
                "metadata": {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "count": 0
                },
                "interactions": []
            }
        except Exception as e:
            logger.error(f"Error loading interactions: {e}")
            raise StorageError(f"Failed to load interactions: {e}")
    
    def _save_interactions(self, interactions: Dict[str, Any]) -> None:
        """Save user interactions."""
        try:
            with open(self.interactions_path, 'w') as f:
                json.dump(interactions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving interactions: {e}")
            raise StorageError(f"Failed to save interactions: {e}")
    
    def record_interaction(
        self, 
        content_id: str, 
        interaction_type: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a user interaction with content.
        
        Args:
            content_id: ID of the content item
            interaction_type: Type of interaction (view, edit, create, etc.)
            context: Additional context for the interaction
        """
        try:
            # Load current interactions
            interactions_data = self._load_interactions()
            
            # Add new interaction
            interaction = {
                "content_id": content_id,
                "type": interaction_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if context:
                interaction["context"] = context
            
            interactions_data["interactions"].append(interaction)
            
            # Update metadata
            interactions_data["metadata"]["count"] = len(interactions_data["interactions"])
            interactions_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # Limit the size of the interactions list (keep most recent 1000)
            if len(interactions_data["interactions"]) > 1000:
                interactions_data["interactions"] = interactions_data["interactions"][-1000:]
                interactions_data["metadata"]["count"] = len(interactions_data["interactions"])
            
            # Save interactions
            self._save_interactions(interactions_data)
            
        except Exception as e:
            logger.error(f"Error recording interaction for {content_id}: {e}")
    
    def get_related_items(
        self,
        content_id: str,
        max_items: int = 5,
        use_semantic: bool = True,
        use_relationships: bool = True,
        use_interactions: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get items related to the given content item.
        
        Args:
            content_id: ID of the content item
            max_items: Maximum number of items to return
            use_semantic: Include semantically similar items
            use_relationships: Include items with explicit relationships
            use_interactions: Use interaction history for recommendations
            
        Returns:
            List of related content items with scores and reasons
        """
        try:
            # Get content
            try:
                content = self.content_manager.get_content(content_id)
            except NotFoundError:
                logger.warning(f"Content not found for recommendations: {content_id}")
                return []
            
            # Results dictionary to deduplicate and merge scores
            # Key is content ID, value is score and reason
            results = {}
            
            # Get related items from relationships
            if use_relationships:
                relationship_items = self._get_related_from_relationships(content_id)
                for item in relationship_items:
                    item_id = item["content_id"]
                    if item_id not in results:
                        results[item_id] = {
                            "content_id": item_id,
                            "score": item["score"],
                            "reason": item["reason"],
                            "source": "relationship"
                        }
                    else:
                        # Update score and reason
                        results[item_id]["score"] = max(results[item_id]["score"], item["score"])
                        results[item_id]["reason"] += f", {item['reason']}"
            
            # Get semantically similar items
            if use_semantic:
                semantic_items = self._get_related_from_semantics(content_id)
                for item in semantic_items:
                    item_id = item["content_id"]
                    if item_id not in results:
                        results[item_id] = {
                            "content_id": item_id,
                            "score": item["score"],
                            "reason": item["reason"],
                            "source": "semantic"
                        }
                    else:
                        # Update score and reason
                        results[item_id]["score"] = max(results[item_id]["score"], item["score"])
                        results[item_id]["reason"] += f", {item['reason']}"
            
            # Get items from interaction history
            if use_interactions:
                interaction_items = self._get_related_from_interactions(content_id)
                for item in interaction_items:
                    item_id = item["content_id"]
                    if item_id not in results:
                        results[item_id] = {
                            "content_id": item_id,
                            "score": item["score"],
                            "reason": item["reason"],
                            "source": "interaction"
                        }
                    else:
                        # Update score and reason
                        results[item_id]["score"] = max(results[item_id]["score"], item["score"])
                        results[item_id]["reason"] += f", {item['reason']}"
            
            # Convert results to list and sort by score
            result_list = list(results.values())
            result_list.sort(key=lambda x: x["score"], reverse=True)
            
            # Take top items
            result_list = result_list[:max_items]
            
            # Fetch content for each result
            for result in result_list:
                try:
                    result["content"] = self.content_manager.get_content(result["content_id"])
                except NotFoundError:
                    result["content"] = {
                        "id": result["content_id"],
                        "title": "Content not found",
                        "_not_found": True
                    }
                except Exception as e:
                    logger.error(f"Error fetching content for {result['content_id']}: {e}")
                    result["content"] = {
                        "id": result["content_id"],
                        "title": "Error fetching content",
                        "_error": str(e)
                    }
            
            return result_list
            
        except Exception as e:
            logger.error(f"Error getting related items for {content_id}: {e}")
            raise KnowledgeBaseError(f"Failed to get related items: {e}")
    
    def _get_related_from_relationships(self, content_id: str) -> List[Dict[str, Any]]:
        """
        Get related items based on explicit relationships.
        
        Args:
            content_id: ID of the content item
            
        Returns:
            List of related content items with scores and reasons
        """
        # Get relationships
        relationships = self.relationship_manager.get_relationships(content_id)
        
        # Results
        results = []
        
        # Process each relationship
        for relationship in relationships:
            # Get the related content ID
            related_id = relationship.target_id if relationship.source_id == content_id else relationship.source_id
            
            # Skip self-relationships
            if related_id == content_id:
                continue
            
            # Determine score based on relationship type
            score = 0.0
            reason = ""
            
            if relationship.relationship_type == RelationshipType.PARENT_CHILD:
                score = 0.9
                reason = "Parent-child relationship"
            elif relationship.relationship_type == RelationshipType.REFERENCE:
                score = 0.8
                reason = "Referenced content"
            elif relationship.relationship_type == RelationshipType.DEPENDENCY:
                score = 0.85
                reason = "Dependency relationship"
            elif relationship.relationship_type == RelationshipType.CONTINUATION:
                score = 0.95
                reason = "Continues from/to"
            else:  # RELATED
                score = 0.75
                reason = "Related content"
            
            # Add description if available
            if relationship.description:
                reason += f" ({relationship.description})"
            
            results.append({
                "content_id": related_id,
                "score": score,
                "reason": reason,
                "relationship_type": relationship.relationship_type.value
            })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def _get_related_from_semantics(self, content_id: str) -> List[Dict[str, Any]]:
        """
        Get related items based on semantic similarity.
        
        Args:
            content_id: ID of the content item
            
        Returns:
            List of related content items with scores and reasons
        """
        try:
            # Use semantic search to find similar content
            similar_items = self.semantic_search.similar_content(content_id, top_k=10, min_similarity=0.5)
            
            # Convert to standard format
            results = []
            
            for item in similar_items:
                results.append({
                    "content_id": item["content_id"],
                    "score": item["similarity"],
                    "reason": f"Semantically similar ({item['similarity']:.2f})"
                })
            
            return results
        except Exception as e:
            logger.error(f"Error getting semantic recommendations: {e}")
            return []
    
    def _get_related_from_interactions(self, content_id: str) -> List[Dict[str, Any]]:
        """
        Get related items based on interaction history.
        
        Args:
            content_id: ID of the content item
            
        Returns:
            List of related content items with scores and reasons
        """
        try:
            # Load interactions
            interactions_data = self._load_interactions()
            interactions = interactions_data["interactions"]
            
            # Find interactions with the given content
            content_interactions = [i for i in interactions if i["content_id"] == content_id]
            
            if not content_interactions:
                return []
            
            # Find interactions that occurred close in time to content interactions
            time_window = timedelta(hours=1)  # Items accessed within 1 hour
            co_accessed_items = Counter()
            
            for interaction in content_interactions:
                interaction_time = datetime.fromisoformat(interaction["timestamp"])
                
                # Find other interactions within the time window
                for other in interactions:
                    if other["content_id"] == content_id:
                        continue
                        
                    other_time = datetime.fromisoformat(other["timestamp"])
                    time_diff = abs(other_time - interaction_time)
                    
                    if time_diff <= time_window:
                        co_accessed_items[other["content_id"]] += 1
            
            # Convert to standard format
            results = []
            
            # Get the top co-accessed items
            for item_id, count in co_accessed_items.most_common(10):
                # Normalize score between 0.5 and 0.9 based on count
                score = min(0.5 + (count / 10) * 0.4, 0.9)
                
                results.append({
                    "content_id": item_id,
                    "score": score,
                    "reason": f"Frequently accessed together ({count} times)"
                })
            
            return results
        except Exception as e:
            logger.error(f"Error getting interaction-based recommendations: {e}")
            return []
    
    def get_contextual_suggestions(
        self, 
        current_context: Dict[str, Any],
        max_items: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get contextual suggestions based on current activity.
        
        Args:
            current_context: Context information (content, activity, etc.)
            max_items: Maximum number of suggestions to return
            
        Returns:
            List of suggested content items with scores and reasons
        """
        try:
            results = []
            
            # Check for content ID in context
            content_id = current_context.get("content_id")
            if content_id:
                # Get related items
                related = self.get_related_items(
                    content_id, 
                    max_items=max_items, 
                    use_semantic=True,
                    use_relationships=True,
                    use_interactions=True
                )
                results.extend(related)
            
            # Check for text in context that can be used for search
            search_text = current_context.get("text", "")
            if search_text and len(search_text) > 10:
                try:
                    # Use semantic search to find relevant content
                    search_results = self.semantic_search.search(
                        search_text, 
                        top_k=max_items,
                        min_similarity=0.4
                    )
                    
                    # Convert to standard format and add to results
                    for item in search_results:
                        # Skip items already in results
                        if any(r["content_id"] == item["content_id"] for r in results):
                            continue
                            
                        results.append({
                            "content_id": item["content_id"],
                            "score": item["similarity"],
                            "reason": f"Relevant to current context ({item['similarity']:.2f})",
                            "content": item["content"],
                            "source": "contextual_search"
                        })
                except Exception as e:
                    logger.error(f"Error in contextual semantic search: {e}")
            
            # Sort by score and limit results
            results.sort(key=lambda x: x["score"], reverse=True)
            results = results[:max_items]
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting contextual suggestions: {e}")
            raise KnowledgeBaseError(f"Failed to get contextual suggestions: {e}")
    
    def get_popular_items(
        self, 
        time_period: str = "week", 
        content_type: Optional[str] = None,
        max_items: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get popular items based on interaction frequency.
        
        Args:
            time_period: Time period to consider (day, week, month, year, all)
            content_type: Optional filter by content type
            max_items: Maximum number of items to return
            
        Returns:
            List of popular content items
        """
        try:
            # Load interactions
            interactions_data = self._load_interactions()
            interactions = interactions_data["interactions"]
            
            # Determine cutoff date
            now = datetime.now(timezone.utc)
            cutoff_date = None
            
            if time_period == "day":
                cutoff_date = now - timedelta(days=1)
            elif time_period == "week":
                cutoff_date = now - timedelta(weeks=1)
            elif time_period == "month":
                cutoff_date = now - timedelta(days=30)
            elif time_period == "year":
                cutoff_date = now - timedelta(days=365)
                
            # Filter interactions by time period and content type
            filtered_interactions = interactions
            
            if cutoff_date:
                filtered_interactions = [
                    i for i in filtered_interactions
                    if datetime.fromisoformat(i["timestamp"]) >= cutoff_date
                ]
            
            # Count interactions by content ID
            content_counts = Counter()
            
            for interaction in filtered_interactions:
                content_counts[interaction["content_id"]] += 1
            
            # Get the top items
            popular_items = content_counts.most_common(max_items * 2)  # Get more than needed to account for filtering
            
            # Build results
            results = []
            
            for item_id, count in popular_items:
                try:
                    content = self.content_manager.get_content(item_id)
                    
                    # Filter by content type if specified
                    if content_type and content.get("_content_type") != content_type:
                        continue
                    
                    # Add to results
                    results.append({
                        "content_id": item_id,
                        "count": count,
                        "content": content
                    })
                    
                    # Stop if we have enough items
                    if len(results) >= max_items:
                        break
                        
                except NotFoundError:
                    # Skip items that can't be found
                    continue
                except Exception as e:
                    logger.error(f"Error fetching content for {item_id}: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting popular items: {e}")
            raise KnowledgeBaseError(f"Failed to get popular items: {e}")
    
    def get_recently_viewed(
        self, 
        max_items: int = 5,
        content_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recently viewed items.
        
        Args:
            max_items: Maximum number of items to return
            content_type: Optional filter by content type
            
        Returns:
            List of recently viewed content items
        """
        try:
            # Load interactions
            interactions_data = self._load_interactions()
            interactions = interactions_data["interactions"]
            
            # Filter view interactions
            view_interactions = [i for i in interactions if i["type"] == "view"]
            
            # Sort by timestamp (descending)
            view_interactions.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Track seen content IDs to avoid duplicates
            seen_ids = set()
            results = []
            
            for interaction in view_interactions:
                content_id = interaction["content_id"]
                
                # Skip if already seen
                if content_id in seen_ids:
                    continue
                
                seen_ids.add(content_id)
                
                try:
                    content = self.content_manager.get_content(content_id)
                    
                    # Filter by content type if specified
                    if content_type and content.get("_content_type") != content_type:
                        continue
                    
                    # Add to results
                    results.append({
                        "content_id": content_id,
                        "timestamp": interaction["timestamp"],
                        "content": content
                    })
                    
                    # Stop if we have enough items
                    if len(results) >= max_items:
                        break
                        
                except NotFoundError:
                    # Skip items that can't be found
                    continue
                except Exception as e:
                    logger.error(f"Error fetching content for {content_id}: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting recently viewed items: {e}")
            raise KnowledgeBaseError(f"Failed to get recently viewed items: {e}")
    
    def get_recommendations_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about recommendations.
        
        Returns:
            Dictionary of statistics
        """
        try:
            # Load interactions
            interactions_data = self._load_interactions()
            interactions = interactions_data["interactions"]
            
            # Count interactions by type
            interaction_types = Counter()
            for interaction in interactions:
                interaction_types[interaction["type"]] += 1
            
            # Count interactions by content type
            content_types = Counter()
            for interaction in interactions:
                content_id = interaction["content_id"]
                try:
                    content = self.content_manager.get_content(content_id)
                    content_type = content.get("_content_type", "unknown")
                    content_types[content_type] += 1
                except Exception:
                    pass
            
            # Calculate time-based statistics
            now = datetime.now(timezone.utc)
            timestamps = [datetime.fromisoformat(i["timestamp"]) for i in interactions]
            
            earliest = min(timestamps) if timestamps else now
            latest = max(timestamps) if timestamps else now
            
            # Build summary
            summary = {
                "total_interactions": len(interactions),
                "by_interaction_type": dict(interaction_types),
                "by_content_type": dict(content_types),
                "date_range": {
                    "earliest": earliest.isoformat(),
                    "latest": latest.isoformat(),
                    "days_span": (latest - earliest).days
                },
                "metadata": interactions_data["metadata"]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting recommendations summary: {e}")
            raise KnowledgeBaseError(f"Failed to get recommendations summary: {e}")
    
    def clear_interactions(self, older_than_days: Optional[int] = None) -> int:
        """
        Clear interaction history.
        
        Args:
            older_than_days: Only clear interactions older than this many days (None for all)
            
        Returns:
            Number of interactions cleared
        """
        try:
            # Load interactions
            interactions_data = self._load_interactions()
            interactions = interactions_data["interactions"]
            
            if older_than_days is None:
                # Clear all
                cleared_count = len(interactions)
                interactions_data["interactions"] = []
            else:
                # Clear older than specified days
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
                
                # Keep only recent interactions
                new_interactions = [
                    i for i in interactions
                    if datetime.fromisoformat(i["timestamp"]) >= cutoff_date
                ]
                
                cleared_count = len(interactions) - len(new_interactions)
                interactions_data["interactions"] = new_interactions
            
            # Update metadata
            interactions_data["metadata"]["count"] = len(interactions_data["interactions"])
            interactions_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            # Save interactions
            self._save_interactions(interactions_data)
            
            return cleared_count
            
        except Exception as e:
            logger.error(f"Error clearing interactions: {e}")
            raise KnowledgeBaseError(f"Failed to clear interactions: {e}") 