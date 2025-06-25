# Token Intelligence System Documentation

*Last updated: June 23, 2025*

## Documentation Contents

This directory contains comprehensive documentation for the Token Intelligence System.

### Core Documentation

- [API Documentation](api.md) - Detailed API endpoint reference
- [Architecture](architecture.md) - System architecture and design
- [Configuration Modes](../CONFIG_MODES.md) - Configuration options and modes

### Usage Examples

The `examples` directory contains executable Python examples that demonstrate how to use the system:

- [Basic Usage](examples/basic_usage.py) - Using the system as a library
- [API Client](examples/api_client.py) - Interacting with the API server

### Additional Resources

- [Refactoring Summary](../REFACTORING_SUMMARY.md) - Overview of the recent refactoring
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

## Documentation Updates

When updating the system, please also update the relevant documentation files. All documentation should follow these guidelines:

1. Include a "Last updated" date
2. Use Markdown format with proper headers
3. Include code examples where appropriate
4. Maintain compatibility between examples and actual code
5. Document API changes comprehensively 