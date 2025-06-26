# Migration Guide: Legacy Privacy Module to Modern Components

This guide outlines how to transition your code from the legacy `privacy.py` module to the modern privacy components.

## Background

The original `privacy.py` module has been replaced by a more modular, better-tested set of privacy components:

- **PrivacyEngine**: Core privacy functionality for tokenization/de-tokenization
- **SessionManager**: Manages privacy sessions for consistent tokenization
- **TokenIntelligenceBridge**: Connects to the token intelligence system with fallback

The legacy module is now implemented as an adapter that forwards calls to these new components. While this provides backward compatibility, we recommend migrating to the modern components directly.

## Migration Benefits

- **Better Performance**: Modern components have optimized implementations
- **More Features**: Access to newer features not available in legacy interface
- **Better Testing**: Modern components have ~90-100% test coverage
- **Better Documentation**: More comprehensive documentation
- **More Flexibility**: Modular components give better control

## Migration Path

### Step 1: Replace Imports

**Before**:
```python
from knowledge_base.privacy import PrivacyIntegration, PrivacyValidator
```

**After**:
```python
from knowledge_base.privacy.smart_anonymization import PrivacyEngine
from knowledge_base.privacy.session_manager import PrivacySessionManager
from knowledge_base.privacy.token_intelligence_bridge import TokenIntelligenceBridge
```

### Step 2: Replace PrivacyIntegration Initialization

**Before**:
```python
privacy_integration = PrivacyIntegration(kb_manager)
```

**After**:
```python
# These components are already available in the knowledge base manager
privacy_engine = kb_manager.privacy_engine
session_manager = kb_manager.session_manager
```

### Step 3: Replace Privacy Bundle Operations

**Before**:
```python
result = privacy_integration.import_privacy_bundle("path/to/bundle.json")
export_result = privacy_integration.export_to_privacy_bundle(export_config)
```

**After**:
```python
# Import bundle
session_id = session_manager.create_session()
with open("path/to/bundle.json", "r") as f:
    bundle_data = json.load(f)

# Process bundle content with privacy engine
for item in bundle_data["content_items"]:
    content = item.get("content", "")
    result = privacy_engine.deidentify(content, session_id)
    # Process the tokenized content

# Export content with privacy
tokenized_content = []
for content in kb_content:
    result = privacy_engine.deidentify(content, session_id)
    tokenized_content.append(result.text)

export_data = {
    "content_items": tokenized_content,
    "privacy_level": session_manager.get_session(session_id)["privacy_level"],
    "token_mappings": session_manager.get_session(session_id)["token_mappings"]
}
```

### Step 4: Replace Privacy Stream Processing

**Before**:
```python
result = privacy_integration.process_privacy_stream(stream_data)
```

**After**:
```python
# Use knowledge base's built-in privacy processing
result = kb_manager.process_with_privacy(
    content=stream_data["content"],
    session_id=session_id,
    privacy_level="balanced"  # Or as appropriate
)
```

### Step 5: Replace Privacy Validation

**Before**:
```python
validator = PrivacyValidator(config)
is_valid = validator.validate_stream_item(item)
```

**After**:
```python
# Validate by checking if any sensitive information remains after tokenization
test_result = privacy_engine.deidentify(item["content"], session_id)
is_sensitive_info_present = any_sensitive_patterns_in(test_result.text)
is_valid = not is_sensitive_info_present
```

## Advanced Migration

### Using Enhanced Features

The modern components offer features not available in the legacy module:

#### Batch Processing

```python
# Process multiple texts efficiently
texts = ["Text 1 with sensitive data", "Text 2 with sensitive data"]
results = privacy_engine.deidentify_batch(texts, session_id)
```

#### Enhanced Privacy Text

```python
# Add context hints to tokens for better AI processing
enhanced_text = token_intelligence_bridge.enhance_privacy_text(
    privacy_text=tokenized_text,
    session_id=session_id,
    preserved_context=context_keywords
)
```

#### Token Intelligence

```python
# Get intelligence directly related to tokens
intelligence = token_intelligence_bridge.generate_intelligence(
    privacy_text=tokenized_text,
    session_id=session_id,
    preserved_context=context_keywords,
    entity_relationships=relationships
)
```

## Compatibility Layer

If you need to maintain compatibility with both legacy and modern components, you can use this wrapper:

```python
def get_privacy_handler(kb_manager):
    """Get appropriate privacy handler based on what's available."""
    try:
        # Try modern components first
        return {
            "engine": kb_manager.privacy_engine,
            "session_manager": kb_manager.session_manager,
            "is_modern": True
        }
    except AttributeError:
        # Fall back to legacy
        from knowledge_base.privacy import PrivacyIntegration
        privacy = PrivacyIntegration(kb_manager)
        return {
            "integration": privacy,
            "is_modern": False
        }
```

## Timeline

The legacy `privacy.py` module is now deprecated but will remain available with full functionality through the adapter layer until the next major version release. We recommend migrating to the modern components as soon as practical.

## Need Help?

If you need assistance migrating your code:

- Check the full API documentation for modern components
- See example code in the `tests/` directory
- Review the architecture documentation for component interactions 