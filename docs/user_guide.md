# User Guide: Getting Started with Your Knowledge System

Welcome to the Knowledge Base & Token Intelligence System! This guide will help you understand the basics of using the system to organize your information and gain insights while maintaining privacy.

## What Can This System Do For You?

This knowledge management system helps you:

1. **Organize your information** - automatically categorize notes, tasks, and events
2. **Find connections** - discover relationships between different pieces of information
3. **Get intelligent insights** - enhance your data with privacy-preserving intelligence
4. **Keep your sensitive data private** - work with a system designed for privacy

## Web Interface

For users of the web interface, here are some additional features:

### User Profile Management

The system includes comprehensive user profile management features:

- Personal information management
- Preference settings for UI and content
- Security settings for account protection
- Tag management for interests and expertise areas

To access your profile, click your avatar in the top-right corner of the interface and select "Profile", or use the keyboard shortcut `Ctrl+P`.

For detailed information, see the [User Profile Documentation](../web_interface/frontend/docs/user_profile.md).

### Keyboard Shortcuts

The web interface supports keyboard shortcuts for faster navigation and improved productivity:

- `Ctrl+K`: Open search
- `Ctrl+D`: Go to dashboard
- `Ctrl+Alt+N`: Create new note
- `Ctrl+Alt+T`: Create new todo
- `Ctrl+?`: Show all available shortcuts

To view all available shortcuts, press `Ctrl+?` or click the keyboard icon in the top toolbar.

For a complete list of shortcuts, see the [Keyboard Shortcuts Documentation](../web_interface/frontend/docs/keyboard_shortcuts.md).

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

## Introduction

The Knowledge Base System helps you organize and process unstructured content, extracting structured information while maintaining privacy. This guide covers both basic and advanced usage.

## Quick Start

### Installation

```bash
# Install the package
pip install knowledge-base-system

# Or install from source
git clone https://github.com/yourorg/knowledge-base-system.git
cd knowledge-base-system
pip install -e .
```

### Basic Usage

```python
from knowledge_base import KnowledgeBaseManager

# Initialize the manager
kb = KnowledgeBaseManager()

# Process stream-of-consciousness content
result = kb.process_stream_of_consciousness(
    "Need to call John about Project X tomorrow at 2pm. Also make notes about the Q2 budget review."
)

# Search content
search_results = kb.search_content("budget")
```

## Core Functionality

### Processing Content

The system can process raw textual content and extract structured information:

```python
# Process with default privacy settings
result = kb.process_stream_of_consciousness(
    "Reminder to email sarah@example.com about the client meeting next Monday."
)

# Process with enhanced privacy
result = kb.process_stream_of_consciousness(
    "Reminder to email sarah@example.com about the client meeting next Monday.",
    privacy_level="enhanced"
)

# Process with a session ID for token consistency
result = kb.process_stream_of_consciousness(
    "Reminder to email sarah@example.com about the client meeting next Monday.",
    session_id="user-123-session"
)
```

### Content Types

The system extracts and organizes content into different types:

1. **Notes**: General text content
2. **Todos**: Action items with optional due dates
3. **Calendar Events**: Events with dates, times, and attendees
4. **Projects**: Project-related information
5. **References**: Citations or reference material

### Privacy Features

The system provides privacy protection for sensitive information:

```python
# Process content with privacy protection
result = kb.process_stream_of_consciousness(
    "Schedule a call with John Smith (555-123-4567) to discuss Project X.",
    privacy_level="standard"
)

# The processed content will contain tokens instead of sensitive information
# "Schedule a call with [PERSON_001] ([PHONE_001]) to discuss [PROJECT_001]."
```

#### Privacy Levels

- **Minimal**: Basic entity detection (names, emails)
- **Standard**: Comprehensive entity detection (default)
- **Enhanced**: Maximum privacy with additional context analysis

## Advanced Usage

### Custom Configuration

```python
from knowledge_base import KnowledgeBaseManager

# Initialize with custom configuration paths
kb = KnowledgeBaseManager(
    config_path="/path/to/config/",
    base_path="/path/to/data/"
)

# Or set configuration via environment variables
# export KB_CONFIG_PATH="/path/to/config/"
# export KB_DATA_PATH="/path/to/data/"
```

### Working with Privacy Sessions

To ensure consistent tokenization across multiple operations, use session IDs:

```python
# First operation creates tokens
result1 = kb.process_stream_of_consciousness(
    "Meeting with John Smith about Project X.",
    session_id="user-123"
)

# Later operations use the same tokens for the same entities
result2 = kb.process_stream_of_consciousness(
    "Send report to John Smith regarding Project X progress.",
    session_id="user-123"
)
```

### Exporting and Importing Content

```python
# Export content to a portable format
exported_content = kb.export_content(content_types=["notes", "todos"])

# Save to a file
import json
with open("exported_kb.json", "w") as f:
    json.dump(exported_content, f)

# Import content from a file
with open("exported_kb.json", "r") as f:
    imported_content = json.load(f)
    
kb.import_content(imported_content)
```

## Command Line Interface

The system provides a command-line interface for common operations:

```bash
# Process a file
kb-cli process input.txt

# Search content
kb-cli search "budget meeting"

# Export content
kb-cli export --output exported_kb.json

# Import content
kb-cli import exported_kb.json
```

## Hierarchical Organization

The Knowledge Base System now supports hierarchical organization of content through folders, making it easier to navigate and find your information.

### Working with Folders

You can create folders and organize your content in a hierarchical structure:

```python
# Create folders
kb = KnowledgeBaseManager()
root_folder = kb.create_folder("Root Folder")
work_folder = kb.create_folder("Work", parent_id=root_folder["id"])
projects_folder = kb.create_folder("Projects", parent_id=work_folder["id"])

# Create content within a folder
project_note = kb.create_content({
    "title": "Project Phoenix",
    "content": "Notes about Project Phoenix implementation...",
    "category": "work",
    "tags": ["project", "phoenix"]
}, "note", parent_id=projects_folder["id"])

# Get folder contents
work_contents = kb.list_folder_contents(work_folder["id"])

# Get folder tree
folder_tree = kb.get_folder_tree(root_folder["id"])

# Move content to a different folder
kb.move_content_to_folder(project_note["id"], work_folder["id"])
```

### Navigating the Hierarchy

Each content item has a path that reflects its position in the hierarchy:

```python
# Get content by path
content = kb.content_manager.get_content_by_path("/Work/Projects/Project Phoenix")

# Get parent folder
parent_id = kb.hierarchy_manager.get_parent_id(content["id"])
parent = kb.content_manager.get_content(parent_id)

# Get breadcrumb path
breadcrumb = kb.hierarchy_manager.get_breadcrumb(content["id"])
for item in breadcrumb:
    print(f"{item['title']} > ", end="")
```

## Relationship Management

The system allows you to create explicit relationships between content items, helping you understand how different pieces of information are connected.

### Creating Relationships

You can define different types of relationships between content items:

```python
# Create content items
project = kb.create_content({
    "title": "Project Phoenix",
    "description": "A major project initiative.",
    "category": "work"
}, "project")

task = kb.create_content({
    "title": "Create project timeline",
    "description": "Develop a timeline for Project Phoenix.",
    "priority": "high",
    "status": "active"
}, "todo")

note = kb.create_content({
    "title": "Meeting Notes",
    "content": "Notes from the project kickoff meeting.",
    "category": "work"
}, "note")

# Create relationships between items
kb.create_relationship(project["id"], task["id"], RelationshipType.DEPENDENCY)
kb.create_relationship(project["id"], note["id"], RelationshipType.REFERENCE)
```

### Relationship Types

The system supports several types of relationships:

- **PARENT_CHILD**: Hierarchical relationship (folder containment)
- **REFERENCE**: One content references another
- **DEPENDENCY**: One content depends on another
- **CONTINUATION**: One content continues from another
- **RELATED**: General relationship between content items

### Working with Related Content

You can retrieve related content and filter by relationship type:

```python
# Get all related content
related_items = kb.get_related_content(project["id"], include_content=True)

# Filter by relationship type
dependencies = kb.get_related_content(
    project["id"], 
    relationship_type=RelationshipType.DEPENDENCY,
    include_content=True
)

# Delete a relationship
kb.delete_relationship(project["id"], note["id"])
```

## Semantic Search and Recommendations

The system now provides powerful semantic search capabilities and content recommendations based on meaning rather than just keywords.

### Semantic Search

You can search for content semantically using natural language queries:

```python
# Semantic search across all content
results = kb.search_semantic("artificial intelligence and machine learning")

# Filter by content types
filtered_results = kb.search_semantic(
    "web design principles", 
    content_types=["note", "project"],
    top_k=5
)

# Find similar content
similar_items = kb.similar_content(note["id"], top_k=3)
```

Unlike traditional keyword search, semantic search understands the meaning of your query and returns results that are conceptually related, even if they don't contain the exact same words.

### Content Recommendations

The system can recommend related content based on relationships, semantic similarity, and user interactions:

```python
# Get recommendations for a specific content item
recommendations = kb.get_recommendations(project["id"])

# Get contextual recommendations based on current activity
context = {
    "content_id": note["id"],
    "text": "I'm writing about knowledge management systems and methodologies."
}
suggestions = kb.get_contextual_suggestions(context)
```

Recommendations are scored and include a reason explaining why each item was recommended, helping you understand the relationships between content items.

### Knowledge Graph

You can build a knowledge graph to visualize relationships between content items:

```python
# Build a knowledge graph starting from a specific content item
graph = kb.build_knowledge_graph([project["id"]])

# Visualize the graph (requires additional visualization library)
# Visualization not included in this example

# Access graph components
nodes = graph["nodes"]
edges = graph["edges"]
```

The knowledge graph helps you discover connections between different pieces of information and navigate your knowledge base visually.

## API Server

An HTTP API server is available for integrating with other applications:

```bash
# Start the API server
kb-api-server

# Server runs on http://localhost:5000 by default
```

### API Usage Example

```python
import requests
import json

# Process content via API
response = requests.post(
    "http://localhost:5000/api/v1/content/process",
    headers={"Content-Type": "application/json"},
    data=json.dumps({
        "content": "Call John about the project tomorrow at 2pm.",
        "session_id": "user-123",
        "privacy_level": "standard"
    })
)

result = response.json()
```

## Error Handling and Troubleshooting

The Knowledge Base System implements a comprehensive error handling system that helps you diagnose and fix issues.

### Understanding Error Types

All errors in the system inherit from a base `KnowledgeBaseError` class and are categorized by type:

```
KnowledgeBaseError
├── ConfigurationError - Issues with configuration files or settings
├── StorageError - Problems reading/writing files or accessing storage
├── ContentProcessingError - Failures in extracting or processing content
├── PrivacyError - Privacy-related operations failures
├── ValidationError - Input validation failures
├── NotFoundError - Requested resources not found
└── RecoveryError - Failed recovery attempts
```

### Common Errors and Solutions

#### ConfigurationError

This occurs when configuration files can't be loaded or contain invalid settings.

**Solution:**
```python
# Verify config path
import os
print(os.path.exists("/path/to/config/ai_instructions.yaml"))

# Use valid configuration path
kb = KnowledgeBaseManager(config_path="/valid/path/to/config/")
```

#### StorageError

This happens when the system can't read from or write to the data directory.

**Solution:**
```python
# Ensure data directory exists and has correct permissions
import os
os.makedirs("/path/to/data", exist_ok=True)

# Use a different data directory
kb = KnowledgeBaseManager(base_path="/different/path/to/data/")
```

#### PrivacyError

This occurs when privacy operations fail, such as tokenization or token resolution.

**Solution:**
```python
# Try with a fresh session ID
result = kb.process_stream_of_consciousness(
    "Meeting with John about the project.",
    session_id="new-session-id"
)

# Or use a different privacy level
result = kb.process_stream_of_consciousness(
    "Meeting with John about the project.",
    privacy_level="minimal"  # Try less aggressive privacy settings
)
```

### Handling API Errors

When using the API, errors are returned with descriptive status codes and messages:

```python
import requests
import json

response = requests.post(
    "http://localhost:5000/api/v1/content/process",
    headers={"Content-Type": "application/json"},
    data=json.dumps({
        "content": "Call John tomorrow"
    })
)

if response.status_code != 200:
    error = response.json()
    print(f"Error type: {error['error']['type']}")
    print(f"Message: {error['error']['message']}")
    # Handle specific error types
    if error['error']['type'] == 'ValidationError':
        # Fix validation issue
        pass
```

### Circuit Breaker Pattern

The system implements the Circuit Breaker pattern to prevent cascading failures when components experience problems.

#### How Circuit Breakers Work

1. **CLOSED** state: Normal operation
2. **OPEN** state: When failures exceed threshold, requests are rejected to prevent further failures
3. **HALF_OPEN** state: After timeout period, allows some requests to test if the system has recovered

#### Circuit Breaker Status

You can check the status of circuit breakers via the API:

```bash
# Check circuit breaker status
curl http://localhost:5000/api/v1/system/circuit-breakers

# Response shows state of all circuit breakers
# {
#   "status": "success",
#   "circuit_breakers": {
#     "privacy_engine": {
#       "state": "CLOSED",
#       "failure_count": 0,
#       "failure_threshold": 5,
#       ...
#     },
#     ...
#   }
# }
```

#### Handling Circuit Breaker Open Errors

When a circuit breaker is OPEN, API requests will return a 429 status code:

```python
response = requests.post("http://localhost:5000/api/v1/privacy/tokenize", 
                         json={"text": "Meeting with John"})

if response.status_code == 429:
    error = response.json()
    if error['error']['type'] == 'CircuitBreakerOpenError':
        print("Service temporarily unavailable due to circuit breaker")
        # Implement retry with exponential backoff
        # Or use fallback mechanism
```

### Using Fallback Mechanisms

The system provides fallback mechanisms when components are unavailable:

```python
try:
    # Try normal processing
    result = kb.process_stream_of_consciousness(
        "Meeting with John about Project X tomorrow.",
        privacy_level="standard"
    )
except KnowledgeBaseError as e:
    # Fall back to minimal processing on error
    print(f"Using fallback due to error: {str(e)}")
    result = kb.process_stream_of_consciousness(
        "Meeting with John about Project X tomorrow.",
        privacy_level="minimal"
    )
```

### Logging for Troubleshooting

Enable detailed logging to troubleshoot issues:

```python
import logging

# Set logging level for the knowledge_base module
logging.getLogger('knowledge_base').setLevel(logging.DEBUG)

# Add a handler to see messages
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger('knowledge_base').addHandler(handler)

# Now operations will log detailed information
kb = KnowledgeBaseManager()
kb.process_stream_of_consciousness("Meeting with John tomorrow")
```

### Common Troubleshooting Steps

1. **Check logs**: Review log files for detailed error information
2. **Verify configurations**: Ensure configuration files exist and are valid
3. **Check permissions**: Verify filesystem permissions for data directories
4. **Test API connectivity**: Use health endpoints to verify services are running
5. **Check circuit breakers**: If operations are failing, check if circuit breakers are open

For more detailed troubleshooting information, refer to the [Troubleshooting Guide](./troubleshooting.md).

## Best Practices

### Sessions and Privacy

- Use consistent session IDs for related content to maintain token consistency
- Choose appropriate privacy levels for your needs
- Store session IDs securely as they can be used to reconstruct sensitive information

### Performance Optimization

- Process content in batches when possible
- Use appropriate privacy levels (higher levels require more processing)
- Consider caching for frequently accessed content

### Content Management

- Add context or tags to improve search results
- Use descriptive titles when manually creating content
- Regularly export your knowledge base for backup purposes

## Integration Examples

### Integration with Note-Taking Apps

```python
def sync_notes_with_knowledge_base(notes):
    kb = KnowledgeBaseManager()
    results = []
    
    for note in notes:
        try:
            result = kb.process_stream_of_consciousness(
                note['content'],
                title=note['title'],
                tags=note['tags']
            )
            results.append(result)
        except Exception as e:
            print(f"Error processing note '{note['title']}': {str(e)}")
    
    return results
```

### Integration with Calendar Applications

```python
def extract_events_from_knowledge_base():
    kb = KnowledgeBaseManager()
    events = kb.get_content_by_type("calendar")
    
    calendar_events = []
    for event in events:
        calendar_events.append({
            'title': event['title'],
            'start': event['datetime'],
            'attendees': event.get('attendees', []),
            'location': event.get('location', '')
        })
    
    return calendar_events
```

## Further Reading

- [API Reference](./api.md): Detailed API documentation
- [Architecture Guide](./architecture.md): System architecture and design
- [Configuration Guide](./configuration.md): Configuration options and settings
- [Privacy Design](./privacy_design.md): Privacy features and implementation
- [Troubleshooting Guide](./troubleshooting.md): Detailed troubleshooting steps 