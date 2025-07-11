# Knowledge Base System with Integrated Privacy

A unified system that combines intelligent knowledge management with built-in privacy protection and advanced content organization.

## 👋 Welcome!

This system provides a secure way to manage your knowledge while protecting privacy through intelligent tokenization. The project integrates:

1. **Knowledge Base Manager**: Organizes and processes your notes, todos, events, and other content with hierarchical organization
2. **Privacy Layer**: Ensures your data remains private through smart anonymization
3. **Token Intelligence**: Generates insights from privacy tokens without accessing original data
4. **Hierarchical Organization**: Organize content in folders with parent-child relationships
5. **Relationship Management**: Create explicit connections between content items
6. **Semantic Search**: Find content based on meaning, not just keywords
7. **Smart Recommendations**: Get contextual suggestions based on relationships and content similarity
8. **Web Interface**: Modern, responsive UI for interacting with the knowledge base

## ✨ Key Features

### Advanced Content Organization
- **Hierarchical Folder Structure**: Organize content in folders with unlimited nesting
- **Explicit Relationships**: Define connections between content items (references, dependencies, continuations)
- **Semantic Search**: Find content based on meaning using vector embeddings
- **Smart Recommendations**: Get suggestions based on relationships, similarity, and user behavior
- **Knowledge Graph**: Visualize connections between your content items

### Privacy-First Design
- **Smart Anonymization**: Preserves essential information while protecting personal identifiers
- **Automatic De-anonymization**: System responses are automatically de-anonymized for users
- **Entity Relationships**: Links related information (person ↔ phone, email, etc.) using privacy tokens
- **Perfect Session Isolation**: Complete privacy boundaries between usage contexts

### Smart Organization
- **Intelligent Processing**: Automatically categorizes and organizes your content
- **Context Awareness**: Recognizes relationships between different pieces of information
- **Personalized Intelligence**: Learns from usage patterns while maintaining privacy

### Web Interface
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Keyboard Shortcuts**: Improve productivity with customizable shortcuts
- **Profile Management**: Comprehensive user profile and preferences
- **Animated Transitions**: Smooth page transitions and interface animations
- **Material Design**: Modern UI with consistent Material Design components

### Rich Capabilities  
- **Multiple Content Types**: Notes, tasks, calendar events, projects, references, and folders
- **Search & Discovery**: Find connections across your knowledge base
- **API Integration**: Connect with other tools through a comprehensive REST API
- **Conversational Interface**: Chat naturally with your knowledge base

### Quality & Reliability
- **Comprehensive Test Coverage**: 94% test coverage for privacy components, 91% overall
- **Fault Tolerance**: Circuit breaker pattern for resilient operation
- **Robust Error Handling**: Consistent exception framework with graceful degradation
- **Performance Optimization**: Batch processing and caching for maximum efficiency

## 🚀 Getting Started

### Installation

```bash
# Install from PyPI
pip install knowledge-base-system

# Or install from source
git clone https://github.com/taiscoding/knowledge-base-system.git
cd knowledge-base-system
pip install -e .
```

### Quick Example

```python
from knowledge_base import KnowledgeBaseManager
from knowledge_base.content_types import RelationshipType

# Initialize the integrated knowledge base
kb = KnowledgeBaseManager()

# Create a folder structure
work_folder = kb.create_folder("Work Projects")
project_folder = kb.create_folder("Project Phoenix", parent_id=work_folder["id"])

# Create content in folders
project = kb.create_content({
    "title": "Project Phoenix",
    "description": "Main project initiative",
    "category": "work"
}, "project", parent_id=project_folder["id"])

task = kb.create_content({
    "title": "Create timeline",
    "description": "Develop project timeline",
    "priority": "high"
}, "todo", parent_id=project_folder["id"])

# Create relationships between content
kb.create_relationship(
    project["id"], 
    task["id"], 
    RelationshipType.DEPENDENCY,
    "Project task"
)

# Semantic search
results = kb.search_semantic("project planning and timelines")

# Get recommendations
recommendations = kb.get_recommendations(project["id"])

# Build knowledge graph
graph = kb.build_knowledge_graph([project["id"]])
```

### Privacy Example

```python
# Create a privacy session
session_id = kb.session_manager.create_session("balanced")

# Process content with privacy
result = kb.process_with_privacy(
    "Need to meet with John about the marketing project tomorrow at 2pm.",
    session_id=session_id
)

# Process and get AI response
response = kb.process_and_respond(
    "Call John tomorrow about the project status.",
    session_id=session_id
)

print(f"AI Response: {response['response']['message']}")
```

### Web Interface

To use the web interface:

```bash
# Navigate to the web interface directory
cd web_interface

# Start the backend API server
cd backend
pip install -r requirements.txt
python main.py

# In a separate terminal, start the frontend
cd frontend
npm install
npm start
```

Access the web interface at `http://localhost:3000`

## 🔄 System Architecture

The system is designed with privacy built into every component and enhanced with hierarchical organization:

```mermaid
graph TD
    A[User Content] -->|Tokenization| B[Privacy Engine]
    B -->|Tokenized Content| C[Knowledge Base Manager]
    
    C -->|Organization & Storage| D[Knowledge Base]
    C -->|Privacy-Safe Tokens| E[Token Intelligence Engine]
    
    E -->|Token Intelligence| C
    C -->|Enhanced Content| F[AI Response Generator]
    F -->|Anonymized Response| B
    B -->|De-anonymized Response| A

    %% Components and flows
    C -->|Content Management| G[Content Manager]
    C -->|Hierarchical Organization| H[Hierarchy Manager]
    C -->|Relationship Management| I[Relationship Manager]
    C -->|Semantic Search| J[Semantic Search Engine]
    C -->|Recommendations| K[Recommendation Engine]
    C -->|Graph Visualization| L[Knowledge Graph]
    
    G -->|Content Items| D
    H -->|Folder Structure| D
    I -->|Content Relationships| D
    J -->|Search Results| C
    K -->|Content Suggestions| C
    L -->|Graph Data| C
    
    %% Web interface
    A <-->|API Calls| M[Web Interface]
    M -->|User Interactions| N[React Frontend]
    N -->|API Requests| O[FastAPI Backend]
    O -->|Data Access| C
    
    subgraph "Knowledge System"
    C
    D
    E
    F
    G
    H
    I
    J
    K
    L
    end
    
    subgraph "Privacy Layer"
    B
    end
    
    subgraph "Web Interface"
    M
    N
    O
    end
```

This enhanced flow ensures that:
1. User input is properly anonymized
2. Processing happens with privacy tokens (never the original data)
3. Content is organized hierarchically with explicit relationships
4. Semantic search and recommendations enhance discoverability
5. Responses are automatically de-anonymized before being shown to users
6. Web interface provides an intuitive, responsive user experience

**Core Components:**
- **Privacy Engine**: Smart anonymization of sensitive information
- **Knowledge Base**: Manages content organization and processing
- **Hierarchy Manager**: Folder structures and content navigation
- **Relationship Manager**: Explicit connections between content items
- **Semantic Search**: Vector-based content similarity and search
- **Recommendation Engine**: Context-aware content suggestions
- **Knowledge Graph**: Visualization of content relationships
- **Token Intelligence**: Provides privacy-safe insights from tokens
- **Web Interface**: Modern React/TypeScript interface with Material-UI

## 📚 Documentation

For detailed information, see:

- [User Guide](docs/user_guide.md) - Start here if you're new!
- [API Reference](docs/api.md) - Technical API details
- [Architecture](docs/architecture.md) - System design overview
- [Privacy Design](docs/privacy_design.md) - How the system protects your data
- [Integration Guide](docs/integration_guide.md) - Connect with other systems
- [Test Coverage](docs/test_coverage.md) - Current test coverage report
- [Performance Optimization](docs/performance_optimization.md) - Optimization techniques
- [Contributing Guide](docs/contributing.md) - How to contribute to the project
- [Troubleshooting Guide](docs/troubleshooting.md) - Solutions to common issues
- [Troubleshooting Fixes](development/records/TROUBLESHOOTING_FIXES_SUMMARY.md) - Recent fixes for common issues
- [Web Interface Documentation](web_interface/frontend/docs/README.md) - Web UI features and usage

## 🔒 Privacy & Security

This system was built with privacy as the core principle:

1. **Built-in Privacy**: Privacy engine integrated into every operation
2. **Smart Anonymization**: Only sensitive data is tokenized, preserving essential context
3. **Zero Re-identification Risk**: Design prevents any possibility of reconstructing original data
4. **Session Isolation**: Usage contexts are kept completely separate
5. **Entity Relationships**: Understand connections between entities without exposing identities

For a complete privacy overview, see our [Privacy Design](docs/privacy_design.md) documentation.

## 🧪 Testing & Quality

We maintain high code quality through:

1. **Comprehensive Testing**: 91% overall test coverage, 94% for privacy components
2. **Performance Monitoring**: Regular benchmarking of key operations
3. **Integration Tests**: End-to-end workflow testing
4. **Continuous Improvement**: Ongoing enhancement of tests and code quality

For more details, check out our [Test Coverage Report](docs/test_coverage.md).

## 📝 Usage Examples

### CLI Interface

```bash
# Process text with privacy
knowledge-base process-private "Call Jane tomorrow about the project deadline"

# Interactive chat mode with privacy
knowledge-base chat

# Create a new privacy session
knowledge-base create-session --privacy-level balanced

# Search across content
knowledge-base search "project"
```

### API Usage

```bash
# Start the API server
python -m scripts.api_server

# Create a session and process with privacy
curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{"privacy_level": "balanced"}'

# Process with privacy
curl -X POST "http://localhost:8000/process-private" \
  -H "Content-Type: application/json" \
  -d '{"content": "Call John at 555-0123", "session_id": "SESSION_ID_HERE"}'

# Check circuit breaker status
curl -X GET "http://localhost:8000/api/v1/system/circuit-breakers"
```

### Error Handling

```python
from knowledge_base import KnowledgeBaseManager
from knowledge_base.utils.helpers import KnowledgeBaseError, StorageError

kb = KnowledgeBaseManager()

try:
    result = kb.process_stream_of_consciousness("Meeting with John tomorrow")
except StorageError as e:
    print(f"Storage error: {e}")
    # Implement fallback behavior
except KnowledgeBaseError as e:
    print(f"General error: {e}")
```

### Development & Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest

# Run tests with coverage report
python -m pytest --cov=knowledge_base

# Run performance benchmarks
python -m pytest tests/benchmarks/ --benchmark-only
```

## 👥 Contributing

We welcome contributions to the Knowledge Base System! See the [Contributing Guide](docs/contributing.md) for details on:

- Setting up your development environment
- Testing standards and requirements
- Code style and documentation
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Structure

- `knowledge_base/` - Core module containing the main functionality
- `tests/` - Comprehensive test suite for the project
- `docs/` - User and developer documentation
- `scripts/` - Helper scripts and utilities
- `development/` - Development resources, planning documents, and historical records
- `web_interface/` - Web UI with React/TypeScript frontend and FastAPI backend

## Latest Improvements

### Web Interface Stability Update (v1.3.1) - June 2025

We've made several important fixes to improve the stability and reliability of the web interface:

- **Runtime Error Fixes**: Resolved animation issues and routing conflicts
- **TypeScript Error Corrections**: Fixed undefined property checks and null handling
- **ESLint Compliance**: Removed unused imports and variables, fixed hook dependencies
- **Backend Connection Improvements**: Added sample data and fixed API connection issues
- **Documentation**: Created comprehensive troubleshooting guide for common issues

For detailed information about these fixes, see our [Troubleshooting Fixes Summary](development/records/TROUBLESHOOTING_FIXES_SUMMARY.md).

### Milestone 4 Completion (v1.3.0) - June 2025

We're excited to announce the completion of Milestone 4, which delivers a comprehensive web interface:

#### Web Interface Features
- **Modern UI**: React/TypeScript implementation with Material-UI components
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **User Profile**: Comprehensive profile management and preferences
- **Keyboard Shortcuts**: Productivity enhancements with keyboard navigation
- **Interactive Visualizations**: Dynamic knowledge graph visualization
- **Page Transitions**: Smooth animations between routes and content changes

#### User Experience Improvements
- **Intuitive Navigation**: Sidebar and breadcrumb navigation
- **Content Management**: Create, edit, and organize all content types
- **Search Integration**: Both text-based and semantic search capabilities
- **Privacy Controls**: User-friendly privacy settings management
- **Dynamic Dashboard**: Actionable insights and content organization

### Milestone 3 Completion (v1.2.0) - May 2025

Major enhancements to content organization:

#### Hierarchical Organization
- **Folder Structure**: Create unlimited nested folders to organize your content
- **Path Navigation**: Each content item has a clear path in the hierarchy
- **Content Movement**: Easily move content between folders
- **Tree Views**: Get comprehensive folder tree representations

#### Relationship Management
- **Explicit Relationships**: Define connections between content items
- **Relationship Types**: Support for references, dependencies, continuations, and more
- **Bidirectional Tracking**: Relationships are maintained in both directions
- **Relationship Metadata**: Add descriptions and context to relationships

#### Semantic Search & Recommendations
- **Vector Embeddings**: Content represented as semantic vectors for similarity matching
- **Natural Language Search**: Find content based on meaning, not just keywords
- **Smart Recommendations**: Get suggestions based on relationships and semantic similarity
- **Contextual Suggestions**: Recommendations adapt to your current activity

#### Knowledge Graph
- **Graph Visualization**: See your content as an interconnected network
- **Path Discovery**: Find connections between seemingly unrelated content
- **Cluster Detection**: Identify groups of related content
- **Interactive Exploration**: Navigate through your knowledge visually