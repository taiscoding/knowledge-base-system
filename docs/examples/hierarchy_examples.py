#!/usr/bin/env python3
"""
Hierarchical Organization Examples for the Knowledge Base System.

This script demonstrates how to use folders, organize content hierarchically,
navigate the structure, and manage relationships between content items.
"""

import json
import tempfile
from pathlib import Path

from knowledge_base import KnowledgeBaseManager
from knowledge_base.content_types import RelationshipType


def demonstrate_folder_organization():
    """Demonstrate folder creation and organization."""
    print("\n🗂️  Folder Organization Example")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        kb = KnowledgeBaseManager(str(temp_dir))
        
        # Create a nested folder structure
        print("1. Creating nested folder structure...")
        
        # Root level folders
        work = kb.create_folder("Work")
        personal = kb.create_folder("Personal")
        archive = kb.create_folder("Archive")
        
        # Work subfolders
        projects = kb.create_folder("Projects", parent_id=work["id"])
        meetings = kb.create_folder("Meetings", parent_id=work["id"])
        resources = kb.create_folder("Resources", parent_id=work["id"])
        
        # Project subfolders
        project_a = kb.create_folder("Project Alpha", parent_id=projects["id"])
        project_b = kb.create_folder("Project Beta", parent_id=projects["id"])
        
        # Personal subfolders
        hobbies = kb.create_folder("Hobbies", parent_id=personal["id"])
        finance = kb.create_folder("Finance", parent_id=personal["id"])
        
        # Display the folder tree
        print("\n2. Complete folder structure:")
        work_tree = kb.get_folder_tree(work["id"])
        personal_tree = kb.get_folder_tree(personal["id"])
        
        print("Work:")
        print(json.dumps(work_tree, indent=2))
        print("\nPersonal:")
        print(json.dumps(personal_tree, indent=2))
        
        # Add content to folders
        print("\n3. Adding content to folders...")
        
        # Add project content
        project_alpha_plan = kb.create_content({
            "title": "Project Alpha Plan",
            "description": "Detailed project plan and timeline",
            "category": "project",
            "status": "active"
        }, "project", parent_id=project_a["id"])
        
        # Add meeting notes
        meeting_notes = kb.create_content({
            "title": "Weekly Team Meeting Notes",
            "content": "Discussion about project status and upcoming deadlines",
            "category": "meeting"
        }, "note", parent_id=meetings["id"])
        
        # Add resource document
        resource_doc = kb.create_content({
            "title": "Development Guidelines",
            "content": "Coding standards and best practices for the team",
            "category": "reference"
        }, "reference", parent_id=resources["id"])
        
        print(f"   ✓ Created project plan in: {project_alpha_plan['folder_path']}")
        print(f"   ✓ Created meeting notes in: {meeting_notes['folder_path']}")
        print(f"   ✓ Created resource doc in: {resource_doc['folder_path']}")
        
        # Navigate folder contents
        print("\n4. Navigating folder contents...")
        
        work_contents = kb.list_folder_contents(work["id"])
        print(f"\nWork folder contains {len(work_contents)} items:")
        for item in work_contents:
            item_type = "📁" if item.get("content_type") == "folder" else "📄"
            print(f"   {item_type} {item['title']}")
        
        # Show deep navigation
        project_a_contents = kb.list_folder_contents(project_a["id"])
        print(f"\nProject Alpha folder contains {len(project_a_contents)} items:")
        for item in project_a_contents:
            item_type = "📁" if item.get("content_type") == "folder" else "📄"
            print(f"   {item_type} {item['title']}")
        
        # Move content between folders
        print("\n5. Moving content between folders...")
        
        # Move the project plan to archive
        updated_plan = kb.move_content(project_alpha_plan["id"], archive["id"])
        print(f"   ✓ Moved '{updated_plan['title']}' to archive")
        print(f"   New path: {updated_plan['folder_path']}")
        
        return {
            "folders": {
                "work": work["id"],
                "projects": projects["id"], 
                "project_a": project_a["id"]
            },
            "content": {
                "project": project_alpha_plan["id"],
                "meeting": meeting_notes["id"],
                "resource": resource_doc["id"]
            }
        }


def demonstrate_relationship_management(folder_data):
    """Demonstrate relationship creation and management."""
    print("\n🔗 Relationship Management Example")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        kb = KnowledgeBaseManager(str(temp_dir))
        
        # Recreate some content for relationships
        work_folder = kb.create_folder("Work")
        
        # Create interconnected content
        project = kb.create_content({
            "title": "Website Redesign Project",
            "description": "Complete redesign of company website",
            "category": "project",
            "status": "active"
        }, "project", parent_id=work_folder["id"])
        
        task1 = kb.create_content({
            "title": "Design wireframes",
            "description": "Create low-fidelity wireframes for all pages",
            "priority": "high",
            "status": "active"
        }, "todo", parent_id=work_folder["id"])
        
        task2 = kb.create_content({
            "title": "Content audit",
            "description": "Review existing content and identify gaps",
            "priority": "medium",
            "status": "active"
        }, "todo", parent_id=work_folder["id"])
        
        reference = kb.create_content({
            "title": "Design System Guidelines",
            "content": "Color schemes, typography, and component guidelines",
            "category": "reference"
        }, "reference", parent_id=work_folder["id"])
        
        meeting = kb.create_content({
            "title": "Kickoff Meeting",
            "description": "Project kickoff with stakeholders",
            "date": "2025-12-20",
            "time": "14:00"
        }, "calendar_event", parent_id=work_folder["id"])
        
        print("1. Created interconnected content:")
        print(f"   📋 Project: {project['title']}")
        print(f"   ✅ Task 1: {task1['title']}")
        print(f"   ✅ Task 2: {task2['title']}")
        print(f"   📖 Reference: {reference['title']}")
        print(f"   📅 Meeting: {meeting['title']}")
        
        # Create relationships
        print("\n2. Creating relationships...")
        
        # Project dependencies
        dep1 = kb.create_relationship(
            project["id"], task1["id"], 
            RelationshipType.DEPENDENCY,
            "Required task for project completion"
        )
        
        dep2 = kb.create_relationship(
            project["id"], task2["id"],
            RelationshipType.DEPENDENCY, 
            "Essential preparation work"
        )
        
        # Reference relationships
        ref1 = kb.create_relationship(
            task1["id"], reference["id"],
            RelationshipType.REFERENCE,
            "Guidelines for wireframe design"
        )
        
        # Continuation relationship (tasks sequence)
        cont = kb.create_relationship(
            task2["id"], task1["id"],
            RelationshipType.CONTINUATION,
            "Content audit should complete before wireframing"
        )
        
        # Meeting relationship
        meeting_ref = kb.create_relationship(
            meeting["id"], project["id"],
            RelationshipType.REFERENCE,
            "Project kickoff meeting"
        )
        
        print(f"   ✓ Created {RelationshipType.DEPENDENCY}: Project → Tasks")
        print(f"   ✓ Created {RelationshipType.REFERENCE}: Task → Reference")
        print(f"   ✓ Created {RelationshipType.CONTINUATION}: Task sequence")
        print(f"   ✓ Created {RelationshipType.REFERENCE}: Meeting → Project")
        
        # Explore relationships
        print("\n3. Exploring relationships...")
        
        # Get all relationships for the project
        project_relationships = kb.get_content_relationships(project["id"])
        print(f"\nProject relationships:")
        for rel_type, relationships in project_relationships.items():
            if relationships:
                print(f"   {rel_type}: {len(relationships)} relationships")
                for rel in relationships:
                    print(f"     → {rel['target_content']['title']}")
        
        # Get related content
        related_to_project = kb.get_related_content(project["id"])
        print(f"\nContent related to project:")
        for rel_type, items in related_to_project.items():
            if items:
                print(f"   {rel_type}: {len(items)} items")
                for item in items:
                    print(f"     • {item['title']}")
        
        # Find relationships for a specific task
        task1_relationships = kb.get_content_relationships(task1["id"])
        print(f"\nTask 1 ('{task1['title']}') relationships:")
        for rel_type, relationships in task1_relationships.items():
            if relationships:
                print(f"   {rel_type}:")
                for rel in relationships:
                    direction = "→" if rel['source_id'] == task1["id"] else "←"
                    other_title = rel['target_content']['title'] if rel['source_id'] == task1["id"] else rel['source_content']['title']
                    print(f"     {direction} {other_title}")
        
        return {
            "project_id": project["id"],
            "relationships_created": 5
        }


def demonstrate_navigation_patterns():
    """Demonstrate different navigation patterns through the hierarchy."""
    print("\n🧭 Navigation Patterns Example")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        kb = KnowledgeBaseManager(str(temp_dir))
        
        # Create a complex folder structure with content
        print("1. Setting up complex folder structure...")
        
        # Create education folder structure
        education = kb.create_folder("Education")
        courses = kb.create_folder("Courses", parent_id=education["id"])
        research = kb.create_folder("Research", parent_id=education["id"])
        
        # Course subfolders
        cs101 = kb.create_folder("CS 101 - Intro to Programming", parent_id=courses["id"])
        math201 = kb.create_folder("MATH 201 - Statistics", parent_id=courses["id"])
        
        # Research subfolders
        ml_research = kb.create_folder("Machine Learning Research", parent_id=research["id"])
        papers = kb.create_folder("Papers", parent_id=ml_research["id"])
        
        # Add content across the structure
        lecture_notes = kb.create_content({
            "title": "Introduction to Variables",
            "content": "Basic concepts of variables in programming",
            "category": "education"
        }, "note", parent_id=cs101["id"])
        
        assignment = kb.create_content({
            "title": "Statistics Assignment 1",
            "description": "Calculate mean, median, mode for given dataset",
            "due_date": "2025-12-25",
            "priority": "high"
        }, "todo", parent_id=math201["id"])
        
        paper = kb.create_content({
            "title": "Deep Learning Survey Paper",
            "content": "Comprehensive survey of deep learning techniques",
            "category": "research"
        }, "reference", parent_id=papers["id"])
        
        print("   ✓ Created education folder structure with content")
        
        # Navigation Pattern 1: Breadth-first exploration
        print("\n2. Breadth-first navigation from root:")
        education_contents = kb.list_folder_contents(education["id"])
        for item in education_contents:
            print(f"   📁 {item['title']}")
            if item.get("content_type") == "folder":
                sub_contents = kb.list_folder_contents(item["id"])
                for sub_item in sub_contents:
                    folder_icon = "📁" if sub_item.get("content_type") == "folder" else "📄"
                    print(f"      {folder_icon} {sub_item['title']}")
        
        # Navigation Pattern 2: Path-based navigation
        print("\n3. Path-based navigation:")
        all_content = []
        
        # Get all content with paths
        for content_type in ["note", "todo", "reference"]:
            content_items = kb.get_content_by_type(content_type, folder_id=education["id"])
            all_content.extend(content_items)
        
        print("   Content paths:")
        for item in all_content:
            print(f"   📄 {item['title']}")
            print(f"      Path: {item.get('folder_path', 'No path')}")
        
        # Navigation Pattern 3: Search within folders
        print("\n4. Search within specific folders:")
        
        # Search within courses folder
        course_content = kb.search_content_in_folder("assignment", courses["id"])
        print(f"   Search 'assignment' in Courses folder:")
        for result in course_content:
            print(f"      📄 {result['title']} (in {result.get('folder_path', 'unknown')})")
        
        # Navigation Pattern 4: Cross-folder content discovery
        print("\n5. Cross-folder content discovery:")
        
        # Find all education-related content
        education_content = kb.get_content_by_category("education", folder_id=education["id"])
        print(f"   Education category content ({len(education_content)} items):")
        for item in education_content:
            print(f"      📄 {item['title']} → {item.get('folder_path', 'No path')}")
        
        # Get content by tags across the hierarchy
        tagged_content = kb.get_content_by_tags(["high"], folder_id=education["id"])
        print(f"   High priority content ({len(tagged_content)} items):")
        for item in tagged_content:
            print(f"      📄 {item['title']} → {item.get('folder_path', 'No path')}")
        
        return {"total_folders": 6, "total_content": 3}


def main():
    """Run all hierarchy and organization examples."""
    print("🗂️  Knowledge Base System - Hierarchical Organization Examples")
    print("=" * 70)
    
    # Run folder organization example
    folder_data = demonstrate_folder_organization()
    
    # Run relationship management example  
    relationship_data = demonstrate_relationship_management(folder_data)
    
    # Run navigation patterns example
    navigation_data = demonstrate_navigation_patterns()
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ All hierarchical organization examples completed!")
    print("\nKey features demonstrated:")
    print("• 📁 Nested folder structures with unlimited depth")
    print("• 📄 Content organization within folders")
    print("• 🔗 Explicit relationships between content items")
    print("• 🧭 Multiple navigation patterns and search strategies")
    print("• 📍 Path-based content identification")
    print("• 🏷️  Category and tag-based content discovery")
    print("\nThe hierarchical organization system provides:")
    print("- Clear content structure and navigation")
    print("- Flexible relationship modeling")
    print("- Powerful search and discovery capabilities")
    print("- Scalable organization for growing knowledge bases")


if __name__ == "__main__":
    main() 