#!/usr/bin/env python3
"""
Combined usage example for the Knowledge Base System showing integration
of privacy, intelligence, hierarchical organization, and semantic search.
"""

import json
import tempfile
from pathlib import Path

from knowledge_base import KnowledgeBaseManager
from knowledge_base.content_types import RelationshipType
from token_intelligence import TokenIntelligenceEngine

def demonstrate_combined_features():
    """Demonstrate multiple features working together."""
    
    # Create a temporary directory for this demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        
        # Initialize the Knowledge Base with all features
        kb = KnowledgeBaseManager(str(base_path))
        
        print("🚀 Knowledge Base System - Combined Features Demo")
        print("=" * 60)
        
        # ===========================================
        # 1. Create Privacy Session
        # ===========================================
        print("\n1. Creating privacy session...")
        session_id = kb.session_manager.create_session("balanced")
        print(f"   Session ID: {session_id}")
        
        # ===========================================
        # 2. Create Hierarchical Organization
        # ===========================================
        print("\n2. Setting up hierarchical organization...")
        
        # Create folder structure
        root_folder = kb.create_folder("My Knowledge Base")
        work_folder = kb.create_folder("Work Projects", parent_id=root_folder["id"])
        personal_folder = kb.create_folder("Personal", parent_id=root_folder["id"])
        archive_folder = kb.create_folder("Archive", parent_id=root_folder["id"])
        
        # Create subfolders
        current_projects = kb.create_folder("Current Projects", parent_id=work_folder["id"])
        brainstorming = kb.create_folder("Brainstorming", parent_id=work_folder["id"])
        
        print(f"   Created folder structure:")
        tree = kb.get_folder_tree(root_folder["id"])
        print(f"   {json.dumps(tree, indent=4)}")
    
        # ===========================================
        # 3. Create Content with Privacy
        # ===========================================
        print("\n3. Creating content with privacy protection...")
        
        # Process content with privacy - this will create todos and calendar events
        content_1 = "Meeting with John Smith tomorrow at 2pm about the Q4 budget review. Need to prepare financial reports and call Sarah Johnson to discuss the marketing campaign."
        
        result = kb.process_with_privacy(content_1, session_id=session_id)
        print(f"   Original content (anonymized): {result['original_content']}")
        print(f"   Extracted {len(result['extracted_info']['todos'])} todos")
        print(f"   Extracted {len(result['extracted_info']['calendar_events'])} events")
        
        # Create a project manually
        project_data = {
            "title": "Q4 Budget Review Project",
            "description": "Comprehensive review of Q4 financial performance and planning for next year",
            "category": "finance",
            "status": "active",
            "priority": "high",
            "tags": ["budget", "finance", "Q4", "planning"]
        }
        
        project = kb.create_content(
            project_data, 
            "project", 
            parent_id=current_projects["id"]
        )
        print(f"   Created project: {project['title']}")
        
        # Create a reference note
        reference_data = {
            "title": "Budget Review Guidelines",
            "content": "Standard procedures for quarterly budget reviews including stakeholder analysis and financial reporting requirements.",
            "category": "reference",
            "tags": ["guidelines", "budget", "process"]
        }
        
        reference = kb.create_content(
            reference_data,
            "reference",
            parent_id=work_folder["id"]
        )
        print(f"   Created reference: {reference['title']}")
        
        # ===========================================
        # 4. Create Relationships
        # ===========================================
        print("\n4. Creating relationships between content...")
        
        # Get the created todos and calendar events to link them
        todos = kb.get_content_by_type("todo", folder_id=root_folder["id"])
        events = kb.get_content_by_type("calendar_event", folder_id=root_folder["id"])
        
        if todos and events:
            # Link the project to related todos
            for todo in todos[:2]:  # Link first 2 todos
                relationship = kb.create_relationship(
                    project["id"],
                    todo["id"],
                    RelationshipType.DEPENDENCY,
                    "Project task dependency"
                )
                print(f"   Created dependency: {project['title']} -> {todo['title']}")
            
            # Link the meeting event to the project
            if events:
                meeting_relationship = kb.create_relationship(
                    events[0]["id"],
                    project["id"],
                    RelationshipType.REFERENCE,
                    "Meeting about project"
                )
                print(f"   Created reference: {events[0]['title']} -> {project['title']}")
    
        # Link the reference to the project
        ref_relationship = kb.create_relationship(
            project["id"],
            reference["id"],
            RelationshipType.REFERENCE,
            "Supporting documentation"
        )
        print(f"   Created reference: {project['title']} -> {reference['title']}")
        
        # ===========================================
        # 5. Semantic Search
        # ===========================================
        print("\n5. Demonstrating semantic search...")
        
        # Search for content semantically
        search_results = kb.search_semantic("budget planning and financial review", limit=5)
        print(f"   Found {len(search_results)} items related to 'budget planning and financial review':")
        for i, result in enumerate(search_results[:3], 1):
            print(f"     {i}. {result['content']['title']} (score: {result['score']:.3f})")
        
        # Search with different query
        search_results_2 = kb.search_semantic("meetings and discussions", limit=3)
        print(f"   Found {len(search_results_2)} items related to 'meetings and discussions':")
        for i, result in enumerate(search_results_2, 1):
            print(f"     {i}. {result['content']['title']} (score: {result['score']:.3f})")
        
        # ===========================================
        # 6. Smart Recommendations
        # ===========================================
        print("\n6. Getting smart recommendations...")
        
        # Get recommendations for the project
        recommendations = kb.get_recommendations(project["id"], limit=5)
        print(f"   Recommendations for '{project['title']}':")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"     {i}. {rec['content']['title']} (reason: {rec['reason']})")
        
        # Get recommendations for a todo if available
        if todos:
            todo_recs = kb.get_recommendations(todos[0]["id"], limit=3)
            print(f"   Recommendations for '{todos[0]['title']}':")
            for i, rec in enumerate(todo_recs, 1):
                print(f"     {i}. {rec['content']['title']} (reason: {rec['reason']})")
        
        # ===========================================
        # 7. Knowledge Graph
        # ===========================================
        print("\n7. Building knowledge graph...")
        
        # Build a knowledge graph starting from the project
        all_content = [project["id"]]
        if todos:
            all_content.extend([todo["id"] for todo in todos[:2]])
        if events:
            all_content.append(events[0]["id"])
        all_content.append(reference["id"])
        
        graph_data = kb.build_knowledge_graph(all_content)
        print(f"   Knowledge graph contains:")
        print(f"     - {len(graph_data['nodes'])} nodes")
        print(f"     - {len(graph_data['edges'])} connections")
    
        # Show some connections
        for edge in graph_data['edges'][:3]:
            source_title = next(n['title'] for n in graph_data['nodes'] if n['id'] == edge['source'])
            target_title = next(n['title'] for n in graph_data['nodes'] if n['id'] == edge['target'])
            print(f"     - {source_title} -> {target_title} ({edge['relationship_type']})")
        
        # ===========================================
        # 8. Token Intelligence Integration
        # ===========================================
        print("\n8. Generating token intelligence...")
        
        # Initialize Token Intelligence Engine
        token_engine = TokenIntelligenceEngine(str(base_path / "token_intelligence"))
        
        # Generate insights from privacy tokens
        insights = token_engine.generate_content_intelligence(
            list(kb.session_manager.get_session_tokens(session_id).values())
        )
        
        if insights:
            print(f"   Generated {len(insights)} insights:")
            for insight in insights[:3]:
                print(f"     - {insight['type']}: {insight['description'][:100]}...")
        
        # ===========================================
        # 9. Navigation and Discovery
        # ===========================================
        print("\n9. Navigation and content discovery...")
        
        # Navigate folder structure
        work_contents = kb.list_folder_contents(work_folder["id"])
        print(f"   Work folder contains {len(work_contents)} items:")
        for item in work_contents:
            item_type = "📁" if item.get("content_type") == "folder" else "📄"
            print(f"     {item_type} {item['title']}")
        
        # Get content by relationship
        related_to_project = kb.get_related_content(project["id"])
        print(f"   Content related to project:")
        for rel_type, items in related_to_project.items():
            if items:
                print(f"     {rel_type}: {len(items)} items")
        
        # ===========================================
        # 10. Privacy-Aware Response Generation
        # ===========================================
        print("\n10. Generating privacy-aware AI response...")
        
        query = "What's the status of my budget review project and what tasks do I need to complete?"
        response = kb.process_and_respond(query, session_id=session_id)
    
        print(f"   User query: {query}")
        print(f"   AI Response: {response['response']['message']}")
        
        if response['response'].get('suggestions'):
            print(f"   Suggestions:")
            for suggestion in response['response']['suggestions'][:3]:
                print(f"     - {suggestion['text']}")
        
        # ===========================================
        # Summary
        # ===========================================
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("\nThis demonstration showed:")
        print("• Privacy-first content processing with token anonymization")
        print("• Hierarchical organization with folders and content navigation")
        print("• Explicit relationship management between content items")
        print("• Semantic search using vector embeddings")
        print("• Smart recommendations based on relationships and similarity")
        print("• Knowledge graph construction and visualization")
        print("• Token intelligence generation from privacy-safe tokens")
        print("• Privacy-aware AI response generation")
        print("\nAll features work together seamlessly while maintaining privacy!")


if __name__ == "__main__":
    demonstrate_combined_features() 