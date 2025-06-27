#!/usr/bin/env python3
"""
Semantic Search and Recommendation Examples for the Knowledge Base System.

This script demonstrates how to use semantic search with vector embeddings
and the intelligent recommendation engine to discover related content.
"""

import tempfile
from pathlib import Path

from knowledge_base import KnowledgeBaseManager
from knowledge_base.content_types import RelationshipType


def create_sample_knowledge_base(kb):
    """Create a sample knowledge base with diverse content for testing."""
    
    # Create folder structure
    root = kb.create_folder("Knowledge Base")
    tech = kb.create_folder("Technology", parent_id=root["id"])
    health = kb.create_folder("Health & Wellness", parent_id=root["id"])
    projects = kb.create_folder("Projects", parent_id=root["id"])
    learning = kb.create_folder("Learning", parent_id=root["id"])
    
    # Technology content
    tech_content = [
        {
            "data": {
                "title": "Machine Learning Fundamentals",
                "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. It involves algorithms that can identify patterns, make predictions, and improve performance over time.",
                "category": "technology",
                "tags": ["AI", "machine learning", "algorithms", "data science"]
            },
            "type": "note",
            "folder": tech["id"]
        },
        {
            "data": {
                "title": "Deep Learning with Neural Networks",
                "content": "Deep learning uses artificial neural networks with multiple layers to model and understand complex patterns in data. It's particularly effective for tasks like image recognition, natural language processing, and speech recognition.",
                "category": "technology", 
                "tags": ["deep learning", "neural networks", "AI", "pattern recognition"]
            },
            "type": "note",
            "folder": tech["id"]
        },
        {
            "data": {
                "title": "Build AI Chatbot Project",
                "description": "Create an intelligent chatbot using natural language processing and machine learning techniques",
                "priority": "high",
                "status": "active",
                "category": "project",
                "tags": ["AI", "chatbot", "NLP", "project"]
            },
            "type": "todo",
            "folder": projects["id"]
        }
    ]
    
    # Health content
    health_content = [
        {
            "data": {
                "title": "Benefits of Regular Exercise",
                "content": "Regular physical exercise improves cardiovascular health, strengthens muscles and bones, enhances mental well-being, and reduces the risk of chronic diseases. It's recommended to engage in at least 150 minutes of moderate-intensity exercise per week.",
                "category": "health",
                "tags": ["exercise", "fitness", "health", "wellness"]
            },
            "type": "note",
            "folder": health["id"]
        },
        {
            "data": {
                "title": "Nutrition and Mental Health",
                "content": "The connection between nutrition and mental health is significant. A balanced diet rich in omega-3 fatty acids, vitamins, and minerals can improve mood, cognitive function, and overall mental well-being.",
                "category": "health",
                "tags": ["nutrition", "mental health", "diet", "wellness"]
            },
            "type": "note",
            "folder": health["id"]
        },
        {
            "data": {
                "title": "Start Daily Meditation Practice",
                "description": "Begin a daily meditation routine to improve mental clarity and reduce stress",
                "priority": "medium",
                "status": "active",
                "category": "wellness",
                "tags": ["meditation", "mindfulness", "mental health"]
            },
            "type": "todo",
            "folder": health["id"]
        }
    ]
    
    # Learning content
    learning_content = [
        {
            "data": {
                "title": "Effective Study Techniques",
                "content": "Research shows that active learning techniques like spaced repetition, retrieval practice, and elaborative interrogation are more effective than passive reading. These methods help improve long-term retention and understanding.",
                "category": "education",
                "tags": ["study", "learning", "memory", "education"]
            },
            "type": "note",
            "folder": learning["id"]
        },
        {
            "data": {
                "title": "Python Programming Course",
                "content": "Comprehensive course covering Python fundamentals, data structures, object-oriented programming, and web development. Includes hands-on projects and real-world applications.",
                "category": "education",
                "tags": ["python", "programming", "course", "development"]
            },
            "type": "reference",
            "folder": learning["id"]
        },
        {
            "data": {
                "title": "Complete Python Course",
                "description": "Finish the online Python programming course with all exercises and projects",
                "priority": "high",
                "status": "active",
                "category": "education",
                "tags": ["python", "programming", "learning", "course"]
            },
            "type": "todo",
            "folder": learning["id"]
        }
    ]
    
    # Create all content
    created_content = []
    for content_group in [tech_content, health_content, learning_content]:
        for item in content_group:
            content = kb.create_content(
                item["data"], 
                item["type"], 
                parent_id=item["folder"]
            )
            created_content.append(content)
    
    # Create some relationships to enhance recommendations
    # Find related content
    ml_note = next(c for c in created_content if c["title"] == "Machine Learning Fundamentals")
    dl_note = next(c for c in created_content if c["title"] == "Deep Learning with Neural Networks")
    ai_project = next(c for c in created_content if c["title"] == "Build AI Chatbot Project")
    python_course = next(c for c in created_content if c["title"] == "Python Programming Course")
    python_todo = next(c for c in created_content if c["title"] == "Complete Python Course")
    
    # Create relationships
    kb.create_relationship(
        ml_note["id"], dl_note["id"], 
        RelationshipType.RELATED,
        "Deep learning builds on machine learning concepts"
    )
    
    kb.create_relationship(
        ai_project["id"], ml_note["id"],
        RelationshipType.REFERENCE,
        "Project requires ML knowledge"
    )
    
    kb.create_relationship(
        python_todo["id"], python_course["id"],
        RelationshipType.REFERENCE,
        "Todo refers to this course"
    )
    
    return {
        "folders": {"tech": tech["id"], "health": health["id"], "projects": projects["id"], "learning": learning["id"]},
        "content": created_content
    }


def demonstrate_semantic_search():
    """Demonstrate semantic search capabilities."""
    print("\n🔍 Semantic Search Example")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        kb = KnowledgeBaseManager(str(temp_dir))
        
        # Create sample content
        data = create_sample_knowledge_base(kb)
        print("✓ Created sample knowledge base with diverse content")
        
        # Example 1: Search for AI/ML related content
        print("\n1. Searching for AI and machine learning content:")
        ml_results = kb.search_semantic("artificial intelligence and machine learning algorithms", limit=5)
        
        print(f"   Found {len(ml_results)} results for 'artificial intelligence and machine learning algorithms':")
        for i, result in enumerate(ml_results, 1):
            print(f"   {i}. {result['content']['title']} (score: {result['score']:.3f})")
            print(f"      Type: {result['content']['content_type']} | Category: {result['content'].get('category', 'N/A')}")
            print(f"      Preview: {result['content'].get('content', result['content'].get('description', ''))[:100]}...")
            print()
        
        # Example 2: Search for health and wellness
        print("\n2. Searching for health and wellness content:")
        health_results = kb.search_semantic("physical wellness mental health exercise nutrition", limit=5)
        
        print(f"   Found {len(health_results)} results for 'physical wellness mental health exercise nutrition':")
        for i, result in enumerate(health_results, 1):
            print(f"   {i}. {result['content']['title']} (score: {result['score']:.3f})")
            print(f"      Tags: {', '.join(result['content'].get('tags', []))}")
            print()
        
        # Example 3: Search for learning and education
        print("\n3. Searching for learning and education content:")
        learning_results = kb.search_semantic("study methods educational techniques programming courses", limit=5)
        
        print(f"   Found {len(learning_results)} results for 'study methods educational techniques programming courses':")
        for i, result in enumerate(learning_results, 1):
            print(f"   {i}. {result['content']['title']} (score: {result['score']:.3f})")
            print(f"      Type: {result['content']['content_type']}")
            print()
        
        # Example 4: Search for project-related content
        print("\n4. Searching for project-related content:")
        project_results = kb.search_semantic("building projects development tasks programming", limit=5)
        
        print(f"   Found {len(project_results)} results for 'building projects development tasks programming':")
        for i, result in enumerate(project_results, 1):
            print(f"   {i}. {result['content']['title']} (score: {result['score']:.3f})")
            print(f"      Priority: {result['content'].get('priority', 'N/A')} | Status: {result['content'].get('status', 'N/A')}")
            print()
        
        # Example 5: Cross-domain search
        print("\n5. Cross-domain search:")
        cross_results = kb.search_semantic("improving performance and optimization", limit=5)
        
        print(f"   Found {len(cross_results)} results for 'improving performance and optimization':")
        for i, result in enumerate(cross_results, 1):
            print(f"   {i}. {result['content']['title']} (score: {result['score']:.3f})")
            print(f"      Domain: {result['content'].get('category', 'N/A')}")
            print()
        
        return data


def demonstrate_recommendation_engine(data):
    """Demonstrate the recommendation engine capabilities."""
    print("\n💡 Recommendation Engine Example")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        kb = KnowledgeBaseManager(str(temp_dir))
        
        # Recreate the knowledge base
        recreated_data = create_sample_knowledge_base(kb)
        
        # Get some content items for testing recommendations
        all_content = recreated_data["content"]
        
        # Example 1: Recommendations for Machine Learning note
        ml_note = next(c for c in all_content if c["title"] == "Machine Learning Fundamentals")
        print(f"1. Getting recommendations for: '{ml_note['title']}'")
        
        ml_recommendations = kb.get_recommendations(ml_note["id"], limit=5)
        print(f"   Found {len(ml_recommendations)} recommendations:")
        for i, rec in enumerate(ml_recommendations, 1):
            print(f"   {i}. {rec['content']['title']} (score: {rec['score']:.3f})")
            print(f"      Reason: {rec['reason']}")
            print(f"      Type: {rec['content']['content_type']} | Category: {rec['content'].get('category', 'N/A')}")
            print()
        
        # Example 2: Recommendations for a project task
        ai_project = next(c for c in all_content if c["title"] == "Build AI Chatbot Project")
        print(f"\n2. Getting recommendations for: '{ai_project['title']}'")
        
        project_recommendations = kb.get_recommendations(ai_project["id"], limit=5)
        print(f"   Found {len(project_recommendations)} recommendations:")
        for i, rec in enumerate(project_recommendations, 1):
            print(f"   {i}. {rec['content']['title']} (score: {rec['score']:.3f})")
            print(f"      Reason: {rec['reason']}")
            print(f"      Tags overlap: {set(ai_project.get('tags', [])) & set(rec['content'].get('tags', []))}")
            print()
        
        # Example 3: Recommendations for learning content
        python_course = next(c for c in all_content if c["title"] == "Python Programming Course")
        print(f"\n3. Getting recommendations for: '{python_course['title']}'")
        
        course_recommendations = kb.get_recommendations(python_course["id"], limit=5)
        print(f"   Found {len(course_recommendations)} recommendations:")
        for i, rec in enumerate(course_recommendations, 1):
            print(f"   {i}. {rec['content']['title']} (score: {rec['score']:.3f})")
            print(f"      Reason: {rec['reason']}")
            print()
        
        # Example 4: Recommendations for health content
        exercise_note = next(c for c in all_content if c["title"] == "Benefits of Regular Exercise")
        print(f"\n4. Getting recommendations for: '{exercise_note['title']}'")
        
        health_recommendations = kb.get_recommendations(exercise_note["id"], limit=5)
        print(f"   Found {len(health_recommendations)} recommendations:")
        for i, rec in enumerate(health_recommendations, 1):
            print(f"   {i}. {rec['content']['title']} (score: {rec['score']:.3f})")
            print(f"      Reason: {rec['reason']}")
            print()
        
        return recreated_data


def demonstrate_advanced_search_features():
    """Demonstrate advanced search features like filtering and ranking."""
    print("\n🔬 Advanced Search Features")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        kb = KnowledgeBaseManager(str(temp_dir))
        
        # Create sample content
        data = create_sample_knowledge_base(kb)
        
        # Example 1: Search with content type filtering
        print("1. Semantic search filtered by content type:")
        
        # Search only for notes
        note_results = kb.search_semantic("learning and education", content_types=["note"], limit=3)
        print(f"   Notes about learning and education ({len(note_results)} results):")
        for result in note_results:
            print(f"   • {result['content']['title']} (score: {result['score']:.3f})")
        
        # Search only for todos
        todo_results = kb.search_semantic("programming and development", content_types=["todo"], limit=3)
        print(f"\n   Todos about programming and development ({len(todo_results)} results):")
        for result in todo_results:
            print(f"   • {result['content']['title']} (score: {result['score']:.3f})")
        
        # Example 2: Search within specific folders
        print("\n2. Search within specific folders:")
        
        tech_folder = data["folders"]["tech"]
        tech_results = kb.search_semantic("algorithms and data", folder_id=tech_folder, limit=3)
        print(f"   Technology folder search results ({len(tech_results)} results):")
        for result in tech_results:
            print(f"   • {result['content']['title']} (score: {result['score']:.3f})")
        
        # Example 3: Search by category and tags
        print("\n3. Search by category and tags:")
        
        # Find high-priority items
        high_priority_content = kb.get_content_by_tags(["python", "programming"])
        print(f"   Content tagged with 'python' and 'programming' ({len(high_priority_content)} items):")
        for item in high_priority_content:
            print(f"   • {item['title']} (Type: {item['content_type']})")
        
        # Find health-related content
        health_content = kb.get_content_by_category("health")
        print(f"\n   Health category content ({len(health_content)} items):")
        for item in health_content:
            print(f"   • {item['title']}")
        
        # Example 4: Similarity threshold filtering
        print("\n4. Similarity threshold filtering:")
        
        # High similarity threshold (more strict)
        strict_results = kb.search_semantic("machine learning algorithms", similarity_threshold=0.7, limit=5)
        print(f"   High similarity results (≥0.7) ({len(strict_results)} results):")
        for result in strict_results:
            print(f"   • {result['content']['title']} (score: {result['score']:.3f})")
        
        # Lower similarity threshold (more inclusive)
        inclusive_results = kb.search_semantic("machine learning algorithms", similarity_threshold=0.3, limit=5)
        print(f"\n   Inclusive results (≥0.3) ({len(inclusive_results)} results):")
        for result in inclusive_results:
            print(f"   • {result['content']['title']} (score: {result['score']:.3f})")


def demonstrate_discovery_workflows():
    """Demonstrate content discovery workflows combining search and recommendations."""
    print("\n🔍 Content Discovery Workflows")
    print("-" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        kb = KnowledgeBaseManager(str(temp_dir))
        
        # Create sample content
        data = create_sample_knowledge_base(kb)
        
        # Workflow 1: Find related learning content
        print("1. Learning Path Discovery Workflow:")
        print("   Goal: Find a learning path from basic concepts to advanced projects")
        
        # Start with a search for fundamentals
        fundamental_results = kb.search_semantic("fundamentals basics introduction", limit=3)
        print(f"\n   Step 1 - Found fundamental concepts ({len(fundamental_results)} results):")
        for result in fundamental_results:
            print(f"   • {result['content']['title']}")
        
        # Get recommendations for the first fundamental topic
        if fundamental_results:
            first_topic = fundamental_results[0]["content"]
            recommendations = kb.get_recommendations(first_topic["id"], limit=3)
            print(f"\n   Step 2 - Recommendations from '{first_topic['title']}':")
            for rec in recommendations:
                print(f"   • {rec['content']['title']} (reason: {rec['reason']})")
            
            # Find related projects
            project_search = kb.search_semantic("project build create develop", content_types=["todo"], limit=3)
            print(f"\n   Step 3 - Related projects ({len(project_search)} results):")
            for result in project_search:
                print(f"   • {result['content']['title']} (priority: {result['content'].get('priority', 'N/A')})")
        
        # Workflow 2: Health and wellness connection discovery
        print("\n\n2. Wellness Connection Discovery Workflow:")
        print("   Goal: Find connections between physical and mental health")
        
        # Search for physical health content
        physical_results = kb.search_semantic("physical exercise fitness", limit=2)
        mental_results = kb.search_semantic("mental health mindfulness", limit=2)
        
        print(f"\n   Physical health content ({len(physical_results)} results):")
        for result in physical_results:
            print(f"   • {result['content']['title']}")
            
            # Get recommendations to find connections
            recs = kb.get_recommendations(result["content"]["id"], limit=2)
            if recs:
                print(f"     → Connected to: {recs[0]['content']['title']}")
        
        print(f"\n   Mental health content ({len(mental_results)} results):")
        for result in mental_results:
            print(f"   • {result['content']['title']}")
        
        # Workflow 3: Technology stack discovery
        print("\n\n3. Technology Stack Discovery Workflow:")
        print("   Goal: Discover technology learning path and related projects")
        
        # Find technology concepts
        tech_concepts = kb.search_semantic("programming artificial intelligence", folder_id=data["folders"]["tech"], limit=2)
        print(f"\n   Technology concepts ({len(tech_concepts)} results):")
        for result in tech_concepts:
            print(f"   • {result['content']['title']}")
            
            # Find related learning resources
            related_learning = kb.search_semantic(
                f"{result['content']['title']} course tutorial learning",
                content_types=["reference", "todo"],
                limit=2
            )
            if related_learning:
                print(f"     Learning resources:")
                for learning in related_learning:
                    print(f"     → {learning['content']['title']} ({learning['content']['content_type']})")


def main():
    """Run all semantic search and recommendation examples."""
    print("🔍 Knowledge Base System - Semantic Search and Recommendations")
    print("=" * 70)
    
    # Run semantic search examples
    data = demonstrate_semantic_search()
    
    # Run recommendation engine examples
    recommendation_data = demonstrate_recommendation_engine(data)
    
    # Run advanced search features
    demonstrate_advanced_search_features()
    
    # Run discovery workflows
    demonstrate_discovery_workflows()
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ All semantic search and recommendation examples completed!")
    print("\nKey features demonstrated:")
    print("• 🔍 Vector-based semantic search with similarity scoring")
    print("• 💡 Intelligent content recommendations")
    print("• 🎯 Content type and folder filtering")
    print("• 🏷️  Category and tag-based discovery")
    print("• 📊 Similarity threshold controls")
    print("• 🔗 Relationship-aware recommendations")
    print("• 🧭 Multi-step discovery workflows")
    print("\nThe semantic search and recommendation system provides:")
    print("- Content discovery based on meaning, not just keywords")
    print("- Contextual suggestions that adapt to user interests")
    print("- Cross-domain knowledge connections")
    print("- Intelligent learning path suggestions")
    print("- Scalable similarity matching with performance optimization")


if __name__ == "__main__":
    main() 