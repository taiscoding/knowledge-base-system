# Contributing to Knowledge Base System

*Last updated: July 2025*

Thank you for your interest in contributing to the Knowledge Base System! This document provides guidelines for contributing code, documentation, and tests.

## Development Environment

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/taiscoding/knowledge-base-system.git
   cd knowledge-base-system
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Code Style

We follow PEP 8 style guidelines for Python code. The codebase uses:

- Black for code formatting
- isort for import sorting
- flake8 for linting

## Testing Standards

### Test Coverage Requirements

- **New Features**: Must include tests with 90%+ coverage
- **Bug Fixes**: Must include regression tests
- **Refactoring**: Must maintain or improve existing test coverage

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=knowledge_base

# Generate detailed HTML coverage report
python -m pytest --cov=knowledge_base --cov-report=html

# Run specific test files/directories
python -m pytest tests/privacy/

# Run performance benchmarks
python -m pytest tests/benchmarks/ --benchmark-only
```

### Writing Tests

1. **Test Structure**:
   - Place tests in the `tests/` directory
   - Follow the same structure as the module being tested
   - Use descriptive test names that explain what's being tested

2. **Test Types**:
   - **Unit Tests**: Test individual components in isolation
   - **Integration Tests**: Test interactions between components
   - **Benchmark Tests**: Test performance characteristics

3. **Test Fixtures**:
   - Use fixtures for reusable setup/teardown
   - Place shared fixtures in `conftest.py`
   - Use temporary directories for file operations

4. **Mocking**:
   - Use pytest-mock for mocking
   - Mock external services and dependencies
   - Don't mock the system under test

### Example Test

```python
def test_deidentify_with_emails(self, privacy_engine, sample_text):
    """Test that emails are correctly identified and tokenized."""
    session_id = privacy_engine.create_session()
    result = privacy_engine.deidentify(sample_text, session_id)
    
    # Check that email is tokenized
    assert "john.smith@example.com" not in result.text
    
    # Check that token was generated for email
    assert any(original == "john.smith@example.com" for original in result.token_map.values())
    
    # Check token format
    email_tokens = [token for token, value in result.token_map.items() 
                   if value == "john.smith@example.com" and token.startswith("EMAIL")]
    assert len(email_tokens) == 1
```

## Error Handling

All new code should use the established error handling framework:

1. **Exception Hierarchy**:
   - Use appropriate exception types from `knowledge_base.utils.helpers`
   - Create specialized exceptions when needed (inheriting from base types)

2. **Circuit Breaker Pattern**:
   - Use circuit breakers for fault-prone operations
   - See `knowledge_base.privacy.circuit_breaker` for implementation details
   - Include fallback mechanisms for when the circuit is open

3. **Graceful Degradation**:
   - Implement fallback behaviors for non-critical failures
   - Use try/except blocks to handle expected error cases
   - Log all errors with appropriate context

## Performance Testing

### Benchmark Requirements

- New features should include performance benchmarks
- Changes should not degrade performance of existing operations
- Performance-critical paths should have detailed benchmarks

### Creating Benchmarks

```python
def test_deidentify_medium_text(self, benchmark, privacy_engine):
    """Benchmark deidentification of medium text."""
    session_id = privacy_engine.create_session()
    benchmark(privacy_engine.deidentify, MEDIUM_TEXT, session_id)
```

## Documentation

### Documentation Requirements

- New features should include documentation
- API changes must update relevant API docs
- Complex logic should have detailed inline comments
- Examples should be provided for new functionality

### Documentation Standards

- Use descriptive docstrings (Google style)
- Include type hints
- Document parameters, return values, and exceptions
- Add examples when appropriate

## Pull Request Process

1. Create a branch for your feature/fix
2. Add tests for your changes
3. Ensure all tests pass
4. Update documentation as needed
5. Submit a pull request
6. Address review feedback

## Current Development Focus

We're currently focused on Milestone 2 (Enhanced Knowledge Organization):

1. **Hierarchical Organization**:
   - Implementing folder/category structure for knowledge items
   - Adding parent-child relationships between content items
   - Creating navigation capabilities across hierarchies

2. **Relationship Tracking**:
   - Implementing explicit connections between content items
   - Adding relationship types (references, dependencies, continuations)
   - Creating bidirectional relationship maintenance

3. **Semantic Search**:
   - Integrating vector embeddings for content
   - Implementing similarity-based search
   - Adding relevance ranking and filters

4. **Content Recommendations**:
   - Creating recommendation engine based on content relationships
   - Implementing "related items" functionality
   - Adding contextual suggestions based on current content

5. **Knowledge Graph Visualization**:
   - Creating graph data structure for knowledge relationships
   - Implementing basic visualization endpoints
   - Adding interactive exploration capabilities

For more details, see the [roadmap.md](./roadmap.md) and [development/records/MILESTONE_1_COMPLETION.md](../development/records/MILESTONE_1_COMPLETION.md) files. 