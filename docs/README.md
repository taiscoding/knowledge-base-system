# Token Intelligence System Documentation

*Last updated: June 26, 2025*

## Documentation Contents

This directory contains comprehensive documentation for the Token Intelligence System.

### Core Documentation

- [API Documentation](api.md) - Detailed API endpoint reference
- [Architecture](architecture.md) - System architecture and design
- [Privacy Design](privacy_design.md) - Privacy protection approach and implementation
- [Test Coverage Report](test_coverage.md) - Current test coverage status and goals
- [Performance Optimization](performance_optimization.md) - Performance metrics and optimization techniques
- [Configuration Modes](../CONFIG_MODES.md) - Configuration options and modes

### Technical Implementation

- [Privacy Implementation Details](examples/privacy_implementation.md) - Detailed explanation of pattern detection and entity relationships
- [Performance Benchmarks](../tests/benchmarks/test_privacy_benchmarks.py) - Performance benchmark tests

### Usage Examples

The `examples` directory contains executable Python examples that demonstrate how to use the system:

- [Basic Usage](examples/basic_usage.py) - Using the system as a library
- [API Client](examples/api_client.py) - Interacting with the API server

### Additional Resources

- [Refactoring Summary](../REFACTORING_SUMMARY.md) - Overview of the recent refactoring
- [Reorganization Summary](../REORGANIZATION_SUMMARY.md) - Latest system reorganization updates
- [Token Intelligence Roadmap](../TOKEN_INTELLIGENCE_ROADMAP.md) - Future development plans
- [Contributing Guide](../CONTRIBUTING.md) - Guidelines for contributing to the project

## Running Examples

You can run the example scripts directly:

```bash
# Make sure you have the Token Intelligence System installed
pip install -e ..

# Run basic usage example
python examples/basic_usage.py

# Make sure the API server is running for this example
python examples/api_client.py
```

## Starting the API Server

To start the API server for testing:

```bash
# From the project root
token-intelligence-server --host 127.0.0.1 --port 5000 --debug
```

## Running Tests

To run the test suite:

```bash
# Run all tests
python -m pytest

# Run privacy tests with coverage report
python -m pytest tests/privacy/ --cov=knowledge_base.privacy

# Run benchmarks
python -m pytest tests/benchmarks/
```

## Documentation Updates

When updating the system, please also update the relevant documentation files. All documentation should follow these guidelines:

1. Include a "Last updated" date
2. Use Markdown format with proper headers
3. Include code examples where appropriate
4. Maintain compatibility between examples and actual code
5. Document API changes comprehensively 