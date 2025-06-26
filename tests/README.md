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

Privacy components are currently at 93% test coverage:
- `knowledge_base/privacy/__init__.py`: 100%
- `knowledge_base/privacy/session_manager.py`: 100%
- `knowledge_base/privacy/smart_anonymization.py`: 88%
- `knowledge_base/privacy/token_intelligence_bridge.py`: 96%

## Performance Benchmarks

Current performance benchmarks for privacy components:

| Operation | Performance | Per-operation Time |
|-----------|------------|--------|
| Deidentify (Small Text) | ~14,492 ops/sec | ~69μs |
| Deidentify (Medium Text) | ~3,469 ops/sec | ~288μs |
| Deidentify (Large Text) | ~364 ops/sec | ~2.75ms |
| Reconstruct | ~49,858 ops/sec | ~20μs |
| Token Consistency | ~30,316 ops/sec | ~33μs |
| Session Create | ~8,997 ops/sec | ~111μs |
| Session Update | ~13,444 ops/sec | ~74μs |

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
1. Core privacy components (✅ 93% coverage achieved)
2. Knowledge base manager
3. API endpoints and CLI interface

## Implementation Details

For detailed information about the implementation and testing of privacy components, see:

- [Privacy Implementation Details](../docs/examples/privacy_implementation.md)
- [Performance Optimization Guide](../docs/performance_optimization.md)
- [Test Coverage Report](../docs/test_coverage.md)

## Mocking Strategy

- External services are mocked to isolate test scope
- The TokenIntelligenceBridge is tested with its fallback behavior when the token intelligence module is not available
- File system operations use temporary directories to avoid side effects

## Next Steps

1. Add tests for the KnowledgeBaseManager class
2. Add tests for CLI interface and API endpoints
3. Add more complex integration tests
4. Add parameterized tests for edge cases 