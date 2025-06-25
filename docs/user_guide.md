# User Guide: Getting Started with Your Knowledge System

Welcome to the Knowledge Base & Token Intelligence System! This guide will help you understand the basics of using the system to organize your information and gain insights while maintaining privacy.

## What Can This System Do For You?

This knowledge management system helps you:

1. **Organize your information** - automatically categorize notes, tasks, and events
2. **Find connections** - discover relationships between different pieces of information
3. **Get intelligent insights** - enhance your data with privacy-preserving intelligence
4. **Keep your sensitive data private** - work with a system designed for privacy

## Basic Concepts

Before diving into usage, let's understand some key concepts:

- **Knowledge Base**: This is where all your information lives - notes, tasks, events, and more
- **Token Intelligence**: This analyzes patterns in your data without accessing sensitive information
- **Privacy Layer**: This protects your private data by replacing it with anonymous tokens

## Quick Start Guide

### Adding Content

The simplest way to add content is through the stream of consciousness interface:

```python
from knowledge_base import KnowledgeBaseManager

# Initialize the system
kb = KnowledgeBaseManager()

# Add some content through stream of consciousness
result = kb.process_stream_of_consciousness(
    "Need to call Mary about the quarterly report tomorrow at 3pm. 
     Also remember to check the budget numbers before the meeting."
)

# See what was extracted
print(f"Tasks found: {len(result['extracted_info']['todos'])}")
print(f"Events found: {len(result['extracted_info']['calendar_events'])}")
```

The system will automatically:
- Identify a task about checking budget numbers
- Create a calendar event for the call with Mary
- Extract relevant tags (#work, #report)
- Categorize the content appropriately

### Finding Information

To find information in your knowledge base:

```python
# Search across all content types
results = kb.search_content("budget")

# Or search in specific categories
todo_results = kb.search_content("budget", content_type="todos")
```

### Using Intelligent Features

The token intelligence system enhances your experience while protecting privacy:

```python
from token_intelligence import TokenIntelligenceEngine

# Initialize the engine
engine = TokenIntelligenceEngine()

# Get intelligence about tokenized content
response = engine.generate_intelligence(
    privacy_text="Meeting with [PERSON_001] about [PROJECT_002]",
    preserved_context=["quarterly", "report", "budget"],
    session_id="my-session-123"
)

# Use the intelligence
print(f"Intelligence type: {response.intelligence_type}")
print(f"Insights: {response.intelligence}")
```

## Content Types

The system supports various content types:

### Notes
Free-form text for capturing ideas, information, or thoughts.

### Tasks (Todos)
Actionable items with properties like priority, due date, and status.

### Calendar Events
Time-based events with properties like datetime, duration, and category.

### Projects
Collections of related notes, tasks, and events.

### References
Links to external resources or uploaded documents.

## Working with Privacy

This system is designed with privacy as a fundamental principle. When you add sensitive information, the system:

1. Identifies sensitive information
2. Tokenizes it for privacy (through the Sankofa integration)
3. Works only with these anonymous tokens
4. Returns insights without exposing the original data

For example:

```
You write: "Meeting with Dr. Smith about diabetes management"

System processes: "Meeting with [PHYSICIAN_001] about [CONDITION_001] management"

Intelligence returned: "[PHYSICIAN_001] specializes in [CONDITION_001] management 
                       with a data-driven approach"
```

## Practical Examples

### Example 1: Managing a Project

```python
# Add project information
kb.process_stream_of_consciousness("""
Working on the Marketing Campaign project with John and Sarah.
Need to complete the budget by Friday.
Schedule team meeting for Wednesday at 10am.
""")

# Later, get project intelligence
engine = TokenIntelligenceEngine()
response = engine.generate_intelligence(
    privacy_text="Status update on [PROJECT_001] with [PERSON_001] and [PERSON_002]",
    preserved_context=["marketing", "campaign", "budget", "meeting"],
    session_id="project-session"
)
```

### Example 2: Health Management

```python
# Add health information
kb.process_stream_of_consciousness("""
Appointment with Dr. Johnson about blood pressure medication next Tuesday at 2pm.
Remember to bring latest test results and medication list.
""")

# Later, get relevant intelligence
response = engine.generate_intelligence(
    privacy_text="Follow-up with [PHYSICIAN_001] about [CONDITION_001] and [MEDICATION_001]",
    preserved_context=["appointment", "test results"],
    session_id="health-session"
)
```

## Tips for Getting the Most Out of the System

1. **Be consistent with tagging** - Use consistent tags to help the system make connections
2. **Include context** - The more context you provide, the better the intelligence
3. **Use the stream interface** - Let the system automatically organize your thoughts
4. **Review categorized items** - Check and refine how the system organizes your content
5. **Maintain session consistency** - Use consistent session IDs for related activities

## Next Steps

Now that you understand the basics, you might want to explore:

- [API Reference](api.md) - For technical integration
- [Privacy Design](privacy_design.md) - To understand the privacy features
- [Integration Guide](integration_guide.md) - To connect with other systems

## Need Help?

If you have questions or need assistance:

- Check the [FAQ](faq.md)
- Review [Common Issues](troubleshooting.md)
- Join our [Community Forum](https://forum.knowledge-base-system.com)

Happy organizing! 