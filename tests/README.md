# Knowledge Base System Testing

This directory contains tests for the Knowledge Base System.

## Testing Framework

Tests are implemented using pytest with the following additional plugins:
- `pytest-cov`: For coverage reporting
- `pytest-mock`: For mocking dependencies
- `pytest-benchmark`: For performance benchmarking

## Test Structure

- `tests/privacy/`: Tests for privacy components
  - `test_privacy_engine.py`: Unit tests for the PrivacyEngine class
  - `test_session_manager.py`: Unit tests for the PrivacySessionManager class
  - `test_token_intelligence_bridge.py`: Unit tests for the TokenIntelligenceBridge class
  - `test_privacy_integration.py`: Integration tests for privacy components
- `tests/benchmarks/`: Performance benchmark tests
  - `test_privacy_benchmarks.py`: Benchmark tests for privacy components

## Current Test Coverage

Privacy components are currently at 96% test coverage:
- `knowledge_base/privacy/__init__.py`: 100%
- `knowledge_base/privacy/session_manager.py`: 98%
- `knowledge_base/privacy/smart_anonymization.py`: 96%
- `knowledge_base/privacy/token_intelligence_bridge.py`: 92%

## Performance Benchmarks

Current performance benchmarks for privacy components:

| Operation | Small Text | Medium Text | Large Text |
|-----------|------------|------------|------------|
| Deidentify | ~30μs | ~130μs | ~1200μs |
| Reconstruct | ~11μs | - | - |
| Session Create | ~120μs | - | - |
| Token Consistency | ~18μs | - | - |

## Running Tests

### Basic Test Run

```bash
python -m pytest
```

### Run with Coverage Report

```bash
python -m pytest --cov=knowledge_base
```

### Run with Detailed Coverage Report

```bash
python -m pytest --cov=knowledge_base --cov-report=html
```
This will generate an HTML coverage report in the `htmlcov` directory.

### Run Specific Tests

```bash
python -m pytest tests/privacy/test_privacy_engine.py  # Run a specific test file
python -m pytest tests/privacy/                       # Run all tests in a directory
python -m pytest tests/privacy/test_privacy_engine.py::TestPrivacyEngine::test_deidentify_with_emails  # Run a specific test
```

### Run Performance Benchmarks

```bash
python -m pytest tests/benchmarks/ --benchmark-only
```

## Test Fixtures

Test fixtures are defined in `conftest.py` files:
- `tests/privacy/conftest.py`: Fixtures for privacy component testing

## Coverage Goals

The goal is to achieve 90%+ code coverage across the codebase, with priority on:
1. Core privacy components (✅ 96% coverage achieved)
2. Knowledge base manager
3. API endpoints and CLI interface

## Known Issues

Several tests are currently failing due to:
1. Pattern recognition issues in PrivacyEngine
2. Entity relationship detection problems
3. Session loading inconsistencies
4. Token consistency issues across multiple calls

These issues are documented in `tests/privacy/IMPLEMENTATION_NOTES.md` and are scheduled to be fixed in the next phase of development.

## Mocking Strategy

- External services are mocked to isolate test scope
- The TokenIntelligenceBridge is tested with its fallback behavior when the token intelligence module is not available
- File system operations use temporary directories to avoid side effects

## Next Steps

1. Fix failing tests by addressing identified issues
2. Add tests for the KnowledgeBaseManager class
3. Add tests for CLI interface and API endpoints
4. Add more complex integration tests
5. Add parameterized tests for edge cases 