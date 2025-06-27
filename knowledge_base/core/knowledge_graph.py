"""
Knowledge Graph
Implements knowledge graph functionality for visualizing and exploring content relationships.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from datetime import datetime, timezone
from collections import defaultdict

from knowledge_base.content_types import RelationshipType
from knowledge_base.utils.helpers import (
    KnowledgeBaseError, NotFoundError, StorageError, ValidationError
)
from knowledge_base.core.relationship_manager import RelationshipManager
from knowledge_base.core.hierarchy_manager import HierarchyManager
from knowledge_base.core.content_manager import ContentManager

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """
    Represents the knowledge graph of content relationships.
    
    This class handles:
    1. Building graph representations of content relationships
    2. Finding paths between content items
    3. Identifying clusters and communities of content
    4. Generating graph visualizations
    5. Computing graph metrics
    """
    
    def __init__(
        self, 
        base_path: str = ".",
        content_manager: Optional[ContentManager] = None,
        relationship_manager: Optional[RelationshipManager] = None,
        hierarchy_manager: Optional[HierarchyManager] = None
    ):
        """
        Initialize the knowledge graph.
        
        Args:
            base_path: Root path of the knowledge base
            content_manager: Optional content manager instance
            relationship_manager: Optional relationship manager instance
            hierarchy_manager: Optional hierarchy manager instance
        """
        self.base_path = Path(base_path)
        
        # Initialize or use provided managers
        self.relationship_manager = relationship_manager or RelationshipManager(base_path)
        self.hierarchy_manager = hierarchy_manager or HierarchyManager(
            base_path, 
            relationship_manager=self.relationship_manager
        )
        self.content_manager = content_manager or ContentManager(
            base_path,
            relationship_manager=self.relationship_manager,
            hierarchy_manager=self.hierarchy_manager
        )
    
    def build_graph(
        self, 
        root_ids: Optional[List[str]] = None, 
        max_depth: int = 2,
        relationship_types: Optional[List[Union[RelationshipType, str]]] = None
    ) -> Dict[str, Any]:
        """
        Build a graph representation of the knowledge base content and relationships.
        
        Args:
            root_ids: Optional list of content IDs to use as root nodes (None for all)
            max_depth: Maximum depth to traverse from root nodes
            relationship_types: Optional filter by relationship types
            
        Returns:
            Dictionary representing the graph
        """
        # Convert string relationship types to enum
        if relationship_types:
            enum_types = []
            for rel_type in relationship_types:
                if isinstance(rel_type, str):
                    try:
                        enum_types.append(RelationshipType(rel_type))
                    except ValueError:
                        logger.warning(f"Invalid relationship type: {rel_type}")
                else:
                    enum_types.append(rel_type)
            relationship_types = enum_types
        
        # Build nodes and edges
        nodes = []
        edges = []
        visited = set()
        
        # If no root IDs specified, get all relationships
        if not root_ids:
            # Load all relationships
            index = self.relationship_manager._load_index()
            
            # Extract unique content IDs
            content_ids = set()
            for rel_id, rel_data in index.items():
                content_ids.add(rel_data.get("source_id"))
                content_ids.add(rel_data.get("target_id"))
            
            root_ids = list(content_ids)
        
        # Process each root node and its relationships
        for root_id in root_ids:
            self._build_graph_node(
                root_id, 
                nodes, 
                edges, 
                visited, 
                0, 
                max_depth, 
                relationship_types
            )
        
        # Combine nodes and edges into graph
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def _build_graph_node(
        self,
        content_id: str,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        visited: Set[str],
        depth: int,
        max_depth: int,
        relationship_types: Optional[List[RelationshipType]] = None
    ) -> None:
        """
        Recursively build graph nodes and edges.
        
        Args:
            content_id: ID of the current content
            nodes: List to append nodes to
            edges: List to append edges to
            visited: Set of already visited content IDs
            depth: Current depth in the graph
            max_depth: Maximum depth to traverse
            relationship_types: Optional filter by relationship types
        """
        # Skip if already visited or max depth reached
        if content_id in visited or depth > max_depth:
            return
        
        # Mark as visited
        visited.add(content_id)
        
        try:
            # Get content data
            content = self.content_manager.get_content(content_id)
            
            # Create node
            node = {
                "id": content_id,
                "label": content.get("title", "Untitled"),
                "type": content.get("_content_type", "unknown"),
                "data": {
                    "path": content.get("path", ""),
                    "category": content.get("category", ""),
                    "tags": content.get("tags", [])
                }
            }
            
            # Add node to list
            nodes.append(node)
            
            # Skip relationship traversal if at max depth
            if depth >= max_depth:
                return
            
            # Get relationships
            relationships = self.relationship_manager.get_relationships(content_id)
            
            # Filter by relationship types if specified
            if relationship_types:
                relationships = [
                    r for r in relationships 
                    if r.relationship_type in relationship_types
                ]
            
            # Process each relationship
            for relationship in relationships:
                # Determine the target
                target_id = relationship.target_id if relationship.source_id == content_id else relationship.source_id
                
                # Skip self-relationships
                if target_id == content_id:
                    continue
                
                # Create edge
                edge = {
                    "source": relationship.source_id,
                    "target": relationship.target_id,
                    "label": relationship.relationship_type.value,
                    "data": {
                        "description": relationship.description,
                        "type": relationship.relationship_type.value,
                        "created": relationship.created
                    }
                }
                
                # Add edge to list
                edges.append(edge)
                
                # Recursively process target
                self._build_graph_node(
                    target_id,
                    nodes,
                    edges,
                    visited,
                    depth + 1,
                    max_depth,
                    relationship_types
                )
                
        except NotFoundError:
            # Skip content that can't be found
            return
        except Exception as e:
            logger.error(f"Error building graph node for {content_id}: {e}")
            return
    
    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find a path between two content items.
        
        Args:
            source_id: ID of the source content
            target_id: ID of the target content
            max_depth: Maximum path length to consider
            
        Returns:
            List of nodes and edges in the path, or empty list if no path found
        """
        # Breadth-first search to find shortest path
        queue = [(source_id, [])]
        visited = {source_id}
        
        while queue:
            node_id, path = queue.pop(0)
            
            # Check if we reached target
            if node_id == target_id:
                return self._build_path_result(path + [node_id])
            
            # Check if we reached max depth
            if len(path) >= max_depth:
                continue
            
            # Get relationships
            relationships = self.relationship_manager.get_relationships(node_id)
            
            # Process each relationship
            for relationship in relationships:
                # Determine the next node
                next_id = relationship.target_id if relationship.source_id == node_id else relationship.source_id
                
                # Skip if already visited
                if next_id in visited:
                    continue
                
                # Mark as visited
                visited.add(next_id)
                
                # Add to queue
                queue.append((next_id, path + [node_id]))
        
        # No path found
        return []
    
    def _build_path_result(self, path: List[str]) -> List[Dict[str, Any]]:
        """
        Build path result from list of content IDs.
        
        Args:
            path: List of content IDs in the path
            
        Returns:
            List of nodes and edges in the path
        """
        result = []
        
        for i, content_id in enumerate(path):
            try:
                # Add node
                content = self.content_manager.get_content(content_id)
                result.append({
                    "type": "node",
                    "id": content_id,
                    "label": content.get("title", "Untitled"),
                    "content_type": content.get("_content_type", "unknown")
                })
                
                # Add edge if not last node
                if i < len(path) - 1:
                    next_id = path[i + 1]
                    
                    # Find relationship
                    relationships = self.relationship_manager.get_relationships(content_id)
                    for relationship in relationships:
                        if (relationship.source_id == content_id and relationship.target_id == next_id) or \
                           (relationship.source_id == next_id and relationship.target_id == content_id):
                            result.append({
                                "type": "edge",
                                "source": relationship.source_id,
                                "target": relationship.target_id,
                                "label": relationship.relationship_type.value,
                                "description": relationship.description
                            })
                            break
            except NotFoundError:
                # Skip content that can't be found
                continue
            except Exception as e:
                logger.error(f"Error building path result for {content_id}: {e}")
                continue
        
        return result
    
    def find_related_clusters(
        self,
        content_id: str,
        max_depth: int = 2,
        min_cluster_size: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find clusters of related content.
        
        Args:
            content_id: ID of the starting content
            max_depth: Maximum depth to traverse
            min_cluster_size: Minimum size for a cluster
            
        Returns:
            List of clusters (groups of related content)
        """
        # Build graph starting from content
        graph = self.build_graph([content_id], max_depth=max_depth)
        
        # Extract nodes and edges
        nodes = {node["id"]: node for node in graph["nodes"]}
        
        # Build adjacency list
        adjacency = defaultdict(set)
        for edge in graph["edges"]:
            adjacency[edge["source"]].add(edge["target"])
            adjacency[edge["target"]].add(edge["source"])
        
        # Find connected components (clusters)
        clusters = []
        visited = set()
        
        for node_id in nodes:
            if node_id in visited:
                continue
            
            # BFS to find connected component
            cluster = []
            queue = [node_id]
            component_visited = {node_id}
            
            while queue:
                current = queue.pop(0)
                cluster.append(nodes[current])
                visited.add(current)
                
                for neighbor in adjacency[current]:
                    if neighbor not in component_visited:
                        component_visited.add(neighbor)
                        queue.append(neighbor)
            
            # Add cluster if it meets minimum size
            if len(cluster) >= min_cluster_size:
                clusters.append({
                    "size": len(cluster),
                    "nodes": cluster
                })
        
        return clusters
    
    def get_content_graph_metrics(self, content_id: str) -> Dict[str, Any]:
        """
        Get graph metrics for a content item.
        
        Args:
            content_id: ID of the content
            
        Returns:
            Dictionary of graph metrics
        """
        try:
            # Get relationships
            relationships = self.relationship_manager.get_relationships(content_id)
            
            # Count relationships by type
            relationship_counts = defaultdict(int)
            for relationship in relationships:
                relationship_counts[relationship.relationship_type.value] += 1
            
            # Get related content IDs
            related_ids = self.relationship_manager.get_related_content_ids(content_id)
            
            # Get path to root
            path_to_root = self.hierarchy_manager.get_breadcrumb(content_id)
            
            # Calculate metrics
            metrics = {
                "degree": len(related_ids),
                "relationship_counts": dict(relationship_counts),
                "hierarchy_depth": len(path_to_root),
                "is_folder": False
            }
            
            # Check if it's a folder
            try:
                content = self.content_manager.get_content(content_id)
                if content.get("_content_type") == "folder":
                    metrics["is_folder"] = True
                    metrics["child_count"] = len(self.hierarchy_manager.get_children(content_id))
            except Exception:
                pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating graph metrics for {content_id}: {e}")
            return {
                "degree": 0,
                "relationship_counts": {},
                "hierarchy_depth": 0,
                "is_folder": False
            }
    
    def generate_visualization_data(
        self,
        root_ids: Optional[List[str]] = None,
        max_depth: int = 2,
        include_hierarchy: bool = True
    ) -> Dict[str, Any]:
        """
        Generate visualization data for the knowledge graph.
        
        Args:
            root_ids: Optional list of content IDs to use as root nodes
            max_depth: Maximum depth to traverse
            include_hierarchy: Include hierarchical relationships
            
        Returns:
            Visualization data suitable for rendering
        """
        # Types of relationships to include
        rel_types = None if include_hierarchy else [
            rt for rt in RelationshipType if rt != RelationshipType.PARENT_CHILD
        ]
        
        # Build graph
        graph = self.build_graph(root_ids, max_depth, rel_types)
        
        # Categorize nodes
        node_types = defaultdict(list)
        for node in graph["nodes"]:
            node_type = node["type"]
            node_types[node_type].append(node)
        
        # Categorize edges
        edge_types = defaultdict(list)
        for edge in graph["edges"]:
            edge_type = edge["label"]
            edge_types[edge_type].append(edge)
        
        # Add statistics
        stats = {
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"]),
            "node_type_counts": {k: len(v) for k, v in node_types.items()},
            "edge_type_counts": {k: len(v) for k, v in edge_types.items()}
        }
        
        # Add visualization metadata
        visualization = {
            "graph": graph,
            "statistics": stats,
            "config": {
                "directed": True,
                "hierarchical": include_hierarchy
            }
        }
        
        return visualization 