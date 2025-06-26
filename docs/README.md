# Knowledge Base System Documentation

*Last updated: July 2025*

## Documentation Contents

This directory contains comprehensive documentation for the Knowledge Base System with integrated Privacy.

### Core Documentation

- [API Documentation](api.md) - Detailed API endpoint reference
- [Architecture](architecture.md) - System architecture and design
- [Privacy Design](privacy_design.md) - Privacy protection approach and implementation
- [Test Coverage Report](test_coverage.md) - Current test coverage status (now at 91%)
- [Performance Optimization](performance_optimization.md) - Performance metrics and optimization techniques
- [User Guide](user_guide.md) - Getting started guide for users
- [Integration Guide](integration_guide.md) - How to integrate with other systems
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [FAQ](faq.md) - Frequently asked questions
- [Roadmap](roadmap.md) - Future development plans

### Technical Implementation

- [Privacy Implementation Details](examples/privacy_implementation.md) - Detailed explanation of pattern detection and entity relationships
- [Performance Benchmarks](../tests/benchmarks/test_privacy_benchmarks.py) - Performance benchmark tests
- [Circuit Breaker Pattern](architecture.md#circuit-breaker-pattern) - Fault tolerance implementation

### Usage Examples

The `examples` directory contains executable Python examples that demonstrate how to use the system:

- [Basic Usage](examples/basic_usage.py) - Using the system as a library
- [API Client](examples/api_client.py) - Interacting with the API server
- [Combined Usage](examples/combined_usage.py) - Using multiple features together
- [Error Handling](examples/error_handling.py) - Implementing proper error handling

### Additional Resources

- [Contributing Guide](contributing.md) - Guidelines for contributing to the project
- [Test Coverage Summary](../development/records/TEST_COVERAGE_SUMMARY.md) - Latest test coverage report
- [Milestone 1 Completion](../development/records/MILESTONE_1_COMPLETION.md) - Summary of Milestone 1 achievements
- [Privacy Migration Plan](../development/records/PRIVACY_MIGRATION_PLAN.md) - Migration status for privacy components

## Running Examples

You can run the example scripts directly:

```bash
# Make sure you have the Knowledge Base System installed
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
python -m scripts.api_server
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

# View circuit breaker status
curl http://localhost:8000/api/v1/system/circuit-breakers
```

## Current Version

The current version is **v1.1.0**, which includes the completion of Milestone 1:
- Comprehensive error handling framework
- Circuit breaker pattern for fault tolerance
- Test coverage improved to 91%
- Performance optimizations
- Legacy code migration completed

We are now working on Milestone 2: Enhanced Knowledge Organization.

## Documentation Updates

When updating the system, please also update the relevant documentation files. All documentation should follow these guidelines:

1. Include a "Last updated" date
2. Use Markdown format with proper headers
3. Include code examples where appropriate
4. Maintain compatibility between examples and actual code
5. Document API changes comprehensively 