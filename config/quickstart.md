# Quick Start Guide

This guide will help you get started with the Knowledge Base & Token Intelligence System.

## Installation

### Option 1: Install from PyPI

```bash
pip install knowledge-base-system
```

### Option 2: Install from Source

```bash
git clone https://github.com/example/knowledge-base-system.git
cd knowledge-base-system
pip install -e .
```

## Basic Usage

### Initialize the System

```python
from knowledge_base import KnowledgeBaseManager
from token_intelligence import TokenIntelligenceEngine

# Create a knowledge base manager
kb = KnowledgeBaseManager()

# Create a token intelligence engine
engine = TokenIntelligenceEngine()
```

### Add Content

```python
# Process a stream of consciousness input
result = kb.process_stream_of_consciousness("""
Need to finish the quarterly report by Friday.
Meeting with the team tomorrow at 2pm to discuss progress.
Remember to check the budget numbers before the meeting.
""")

# See what was extracted
print(f"Todos found: {len(result['extracted_info']['todos'])}")
print(f"Events found: {len(result['extracted_info']['calendar_events'])}")
print(f"Tags: {result['extracted_info']['tags']}")
```

### Search for Content

```python
# Search across all content
results = kb.search_content("meeting")

# Search in specific content type
todo_results = kb.search_content("report", content_type="todos")

# Display results
for result in results:
    print(f"{result['type']}: {result['content_preview']}")
```

### Generate Token Intelligence

```python
from token_intelligence import TokenIntelligenceRequest

# Create a request with tokenized text
request = TokenIntelligenceRequest(
    privacy_text="Meeting with [PERSON_001] about [PROJECT_002]",
    preserved_context=["quarterly", "report", "budget"],
    session_id="quickstart-session"
)

# Generate intelligence
response = engine.generate_intelligence(request)

# Use the intelligence
print(f"Intelligence type: {response.intelligence_type}")
for key, value in response.intelligence.items():
    print(f"• {key}: {value}")
```

## Using the CLI

The system includes a command-line interface for common operations:

```bash
# Add content
kb-cli add "Need to finish the quarterly report by Friday"

# Search content
kb-cli search "report"

# Generate intelligence
kb-cli intel "Meeting with [PERSON_001]" --context "report,quarterly"

# Export data
kb-cli export --privacy
```

## Privacy Integration

To use the system with the Sankofa privacy layer:

```python
from knowledge_base.privacy import PrivacyIntegration

# Initialize privacy integration
privacy = PrivacyIntegration(kb)

# Import privacy bundle
result = privacy.import_privacy_bundle("path/to/bundle.json")

# Export privacy bundle
export_result = privacy.export_to_privacy_bundle()
```

## Configuration

The system can be configured through YAML files in the `config` directory:

- `config/ai_instructions.yaml`: Configure AI behavior
- `config/conventions.yaml`: Configure naming conventions
- `config/sankofa_integration.yaml`: Configure privacy integration

You can also override settings with environment variables:

```bash
# Set log level
export KB_LOG_LEVEL=DEBUG

# Set data path
export KB_DATA_PATH=/path/to/data
```

## Next Steps

- Read the [User Guide](../docs/user_guide.md) for detailed usage instructions
- Explore the [API Reference](../docs/api.md) for developer documentation
- Check the [Privacy Design](../docs/privacy_design.md) to understand the privacy features
- Join the community forum for help and discussions

## Examples

For more examples, see the `docs/examples` directory:

- [Basic Usage](../docs/examples/basic_usage.py)
- [Combined Usage](../docs/examples/combined_usage.py)
- [API Client](../docs/examples/api_client.py) 