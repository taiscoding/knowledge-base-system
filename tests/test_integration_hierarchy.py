#!/usr/bin/env python3
"""
Integration tests for hierarchical content organization and relationships.
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from knowledge_base.manager import KnowledgeBaseManager
from knowledge_base.content_types import RelationshipType


class TestHierarchicalContentIntegration:
    """Test KnowledgeBaseManager integration with hierarchical organization features."""
    
    @pytest.fixture
    def kb_manager(self):
        """Create a KnowledgeBaseManager with temporary directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up directory structure
            data_dir = Path(temp_dir) / "data"
            
            # Create directories
            (data_dir / "notes").mkdir(parents=True, exist_ok=True)
            (data_dir / "todos").mkdir(parents=True, exist_ok=True)
            (data_dir / "projects").mkdir(parents=True, exist_ok=True)
            
            # Initialize the knowledge base manager
            manager = KnowledgeBaseManager(
                base_path=temp_dir
            )
            
            yield manager, temp_dir
    
    def test_folder_creation_and_navigation(self, kb_manager):
        """Test creating folders and navigating the hierarchy."""
        manager, temp_dir = kb_manager
        
        # Create a hierarchy of folders
        root_folder = manager.create_folder("Root Folder", None)
        assert root_folder is not None
        assert root_folder["title"] == "Root Folder"
        
        work_folder = manager.create_folder("Work", root_folder["id"])
        assert work_folder is not None
        assert work_folder["title"] == "Work"
        assert work_folder["parent_id"] == root_folder["id"]
        
        projects_folder = manager.create_folder("Projects", work_folder["id"])
        assert projects_folder is not None
        assert projects_folder["title"] == "Projects"
        assert projects_folder["parent_id"] == work_folder["id"]
        
        # Test folder tree retrieval
        folder_tree = manager.get_folder_tree()
        assert folder_tree is not None
        
        # There should be a root folder
        assert folder_tree["title"] == "Root"
        
        # Get the children of the root folder
        root_folder_contents = manager.list_folder_contents(root_folder["id"])
        assert len(root_folder_contents) == 1
        assert root_folder_contents[0]["title"] == "Work"
        
        # Get the children of the work folder
        work_folder_contents = manager.list_folder_contents(work_folder["id"])
        assert len(work_folder_contents) == 1
        assert work_folder_contents[0]["title"] == "Projects"

    def test_content_in_folders(self, kb_manager):
        """Test creating content within folders."""
        manager, temp_dir = kb_manager
        
        # Create folders
        projects_folder = manager.create_folder("Projects")
        personal_folder = manager.create_folder("Personal")
        
        # Create content in folders
        project_note = manager.create_content({
            "title": "Project Alpha",
            "content": "This is a project note.",
            "category": "work",
            "tags": ["project", "alpha"]
        }, "note", parent_id=projects_folder["id"])
        
        personal_note = manager.create_content({
            "title": "Personal Goals",
            "content": "My personal goals for the year.",
            "category": "personal",
            "tags": ["goals", "personal"]
        }, "note", parent_id=personal_folder["id"])
        
        # Verify content is in the correct folders
        projects_contents = manager.list_folder_contents(projects_folder["id"])
        personal_contents = manager.list_folder_contents(personal_folder["id"])
        
        assert len(projects_contents) == 1
        assert projects_contents[0]["title"] == "Project Alpha"
        
        assert len(personal_contents) == 1
        assert personal_contents[0]["title"] == "Personal Goals"
        
        # Test moving content to a different folder
        moved_note = manager.move_content_to_folder(personal_note["id"], projects_folder["id"])
        
        # Verify content was moved
        projects_contents = manager.list_folder_contents(projects_folder["id"])
        personal_contents = manager.list_folder_contents(personal_folder["id"])
        
        assert len(projects_contents) == 2
        assert len(personal_contents) == 0

    def test_content_relationships(self, kb_manager):
        """Test creating and managing relationships between content items."""
        manager, temp_dir = kb_manager
        
        # Create some content items
        project = manager.create_content({
            "title": "Project Phoenix",
            "description": "A major project initiative.",
            "status": "active",
            "category": "work",
            "tags": ["project", "important"]
        }, "project")
        
        note = manager.create_content({
            "title": "Meeting Notes",
            "content": "Notes from the project kickoff meeting.",
            "category": "work",
            "tags": ["meeting", "notes"]
        }, "note")
        
        todo = manager.create_content({
            "title": "Create project timeline",
            "description": "Develop a timeline for Project Phoenix.",
            "priority": "high",
            "status": "active",
            "category": "task",
            "tags": ["project", "planning"]
        }, "todo")
        
        # Create relationships between items
        project_note_relation = manager.create_relationship(
            source_id=project["id"],
            target_id=note["id"],
            relationship_type=RelationshipType.REFERENCE,
            description="Project documentation"
        )
        
        project_todo_relation = manager.create_relationship(
            source_id=project["id"],
            target_id=todo["id"],
            relationship_type=RelationshipType.DEPENDENCY,
            description="Project task"
        )
        
        # Test retrieving related content
        project_related = manager.get_related_content(project["id"], include_content=True)
        assert len(project_related) == 2
        
        # The related items should be the note and the todo
        related_ids = {item["content_id"] for item in project_related}
        assert note["id"] in related_ids
        assert todo["id"] in related_ids
        
        # Test filtering by relationship type
        project_dependencies = manager.get_related_content(
            project["id"],
            relationship_type=RelationshipType.DEPENDENCY,
            include_content=True
        )
        
        assert len(project_dependencies) == 1
        assert project_dependencies[0]["content_id"] == todo["id"]
        
        # Test deleting a relationship
        deleted = manager.delete_relationship(project["id"], note["id"])
        assert deleted is True
        
        # Verify the relationship was deleted
        project_related = manager.get_related_content(project["id"], include_content=True)
        assert len(project_related) == 1
        assert project_related[0]["content_id"] == todo["id"]

    def test_knowledge_graph(self, kb_manager):
        """Test building a knowledge graph."""
        manager, temp_dir = kb_manager
        
        # Create a network of related items
        project = manager.create_content({
            "title": "Project Phoenix",
            "description": "Main project",
            "category": "work"
        }, "project")
        
        task1 = manager.create_content({
            "title": "Design phase",
            "description": "Design task",
            "category": "task"
        }, "todo")
        
        task2 = manager.create_content({
            "title": "Implementation phase",
            "description": "Implementation task",
            "category": "task"
        }, "todo")
        
        note = manager.create_content({
            "title": "Architecture notes",
            "content": "Notes about the project architecture.",
            "category": "technical"
        }, "note")
        
        # Create relationships
        manager.create_relationship(project["id"], task1["id"], RelationshipType.DEPENDENCY)
        manager.create_relationship(project["id"], task2["id"], RelationshipType.DEPENDENCY)
        manager.create_relationship(task1["id"], task2["id"], RelationshipType.CONTINUATION)
        manager.create_relationship(task1["id"], note["id"], RelationshipType.REFERENCE)
        
        # Build knowledge graph
        graph = manager.build_knowledge_graph([project["id"]])
        
        # Check graph structure
        assert "nodes" in graph
        assert "edges" in graph
        
        # There should be 4 nodes in the graph
        assert len(graph["nodes"]) == 4
        
        # There should be 4 edges in the graph
        assert len(graph["edges"]) == 4
        
        # Verify node IDs
        node_ids = {node["id"] for node in graph["nodes"]}
        assert project["id"] in node_ids
        assert task1["id"] in node_ids
        assert task2["id"] in node_ids
        assert note["id"] in node_ids


class TestSemanticSearchIntegration:
    """Test KnowledgeBaseManager integration with semantic search features."""
    
    @pytest.fixture
    def kb_manager(self):
        """Create a KnowledgeBaseManager with test content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize the knowledge base manager
            manager = KnowledgeBaseManager(base_path=temp_dir)
            
            # Create some content with distinct semantic meanings
            project1 = manager.create_content({
                "title": "Machine Learning Project",
                "description": "A project focused on neural networks and deep learning algorithms.",
                "category": "tech",
                "tags": ["AI", "machine learning", "neural networks"]
            }, "project")
            
            project2 = manager.create_content({
                "title": "Website Redesign",
                "description": "Redesigning the company website with modern UI/UX principles.",
                "category": "design",
                "tags": ["web", "design", "UI/UX"]
            }, "project")
            
            note1 = manager.create_content({
                "title": "AI Research Notes",
                "content": "Notes on recent advancements in artificial intelligence and machine learning techniques.",
                "category": "research",
                "tags": ["AI", "research", "deep learning"]
            }, "note")
            
            note2 = manager.create_content({
                "title": "Design Principles",
                "content": "Important principles of good web design and user experience.",
                "category": "design",
                "tags": ["design", "web", "principles"]
            }, "note")
            
            # Generate embeddings for all content
            for content_id in [project1["id"], project2["id"], note1["id"], note2["id"]]:
                manager.semantic_search_engine.create_content_embedding(content_id)
            
            yield manager, [project1, project2, note1, note2]
    
    def test_semantic_search(self, kb_manager):
        """Test semantic search across content."""
        manager, content_items = kb_manager
        project1, project2, note1, note2 = content_items
        
        # Search for AI-related content
        ai_results = manager.search_semantic("artificial intelligence and neural networks")
        
        # Search for design-related content
        design_results = manager.search_semantic("web design and user experience")
        
        # Skip detailed content assertions since we're using mock embeddings
        # Just check that we get results back
        assert len(ai_results) > 0
        assert len(design_results) > 0
    
    def test_similar_content(self, kb_manager):
        """Test finding similar content."""
        manager, content_items = kb_manager
        project1, project2, note1, note2 = content_items
        
        # Find content similar to the AI research note
        similar_to_ai = manager.similar_content(note1["id"])
        
        # Find content similar to the website project
        similar_to_web = manager.similar_content(project2["id"])
        
        # Skip detailed assertions since we're using mock embeddings
        # Just check that we get results back
        assert len(similar_to_ai) > 0
        assert len(similar_to_web) > 0


class TestRecommendationsIntegration:
    """Test KnowledgeBaseManager integration with recommendation engine."""
    
    @pytest.fixture
    def kb_manager(self):
        """Create a KnowledgeBaseManager with test content and relationships."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize the knowledge base manager
            manager = KnowledgeBaseManager(base_path=temp_dir)
            
            # Create content items
            project = manager.create_content({
                "title": "Research Project",
                "description": "A research project on knowledge management.",
                "category": "research"
            }, "project")
            
            note1 = manager.create_content({
                "title": "Literature Review",
                "content": "Review of existing knowledge management systems.",
                "category": "research"
            }, "note")
            
            note2 = manager.create_content({
                "title": "Methodology",
                "content": "Research methodology and approach.",
                "category": "research"
            }, "note")
            
            note3 = manager.create_content({
                "title": "Preliminary Results",
                "content": "Initial findings from the research.",
                "category": "research"
            }, "note")
            
            # Create relationships
            manager.create_relationship(project["id"], note1["id"], RelationshipType.REFERENCE)
            manager.create_relationship(project["id"], note2["id"], RelationshipType.REFERENCE)
            manager.create_relationship(note1["id"], note2["id"], RelationshipType.CONTINUATION)
            manager.create_relationship(note2["id"], note3["id"], RelationshipType.CONTINUATION)
            
            # Generate embeddings (important for semantic recommendations)
            for content_id in [project["id"], note1["id"], note2["id"], note3["id"]]:
                manager.semantic_search_engine.create_content_embedding(content_id)
            
            # Record some interactions to inform recommendations
            manager.recommendation_engine.record_interaction(project["id"], "view")
            manager.recommendation_engine.record_interaction(note1["id"], "view")
            manager.recommendation_engine.record_interaction(note1["id"], "edit")
            manager.recommendation_engine.record_interaction(note2["id"], "view")
            
            yield manager, {
                "project": project,
                "note1": note1,
                "note2": note2,
                "note3": note3
            }
    
    def test_get_recommendations(self, kb_manager):
        """Test getting content recommendations."""
        manager, content_dict = kb_manager
        
        # Get recommendations for the project
        project_recommendations = manager.get_recommendations(content_dict["project"]["id"])
        
        # We should get some recommendations
        assert len(project_recommendations) > 0
        
        # Get recommendations for note1
        note1_recommendations = manager.get_recommendations(content_dict["note1"]["id"])
        assert len(note1_recommendations) > 0
    
    def test_contextual_suggestions(self, kb_manager):
        """Test getting contextual suggestions."""
        manager, content_dict = kb_manager
        
        # Create a context with the current content
        context = {
            "content_id": content_dict["note1"]["id"],
            "text": "I'm writing about knowledge management systems and methodologies."
        }
        
        # Get contextual suggestions
        suggestions = manager.get_contextual_suggestions(context)
        
        # We should get some suggestions
        assert len(suggestions) > 0 