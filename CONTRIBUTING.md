# Contributing to Knowledge Base System

*Last updated: July 2025*

Thank you for your interest in contributing to our project! This document provides a high-level overview of how to contribute to the Knowledge Base System.

> **Note:** For detailed contributing guidelines, please see [docs/contributing.md](docs/contributing.md).

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/taiscoding/knowledge-base-system.git
   cd knowledge-base-system
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Run tests to verify setup**:
   ```bash
   python -m pytest
   ```

## Current Development Focus

We're currently focused on Milestone 2 (Enhanced Knowledge Organization):

1. **Hierarchical Organization** - Implementing folder/category structure
2. **Relationship Tracking** - Creating connections between content items
3. **Semantic Search** - Implementing vector-based search capabilities
4. **Content Recommendations** - Building a recommendation engine
5. **Knowledge Graph Visualization** - Visualizing content relationships

See our [roadmap](docs/roadmap.md) for more details.

## Core Development Principles

1. **Privacy by Design**: All features must preserve our privacy model
2. **Test-Driven Development**: Maintain our 91% test coverage standard
3. **Fault Tolerance**: Use the circuit breaker pattern for critical operations
4. **Documentation**: Update docs as you implement features

## Key Resources

- [Detailed Contributing Guide](docs/contributing.md)
- [API Documentation](docs/api.md)
- [Architecture Overview](docs/architecture.md)
- [Test Coverage Report](docs/test_coverage.md)
- [User Guide](docs/user_guide.md)
- [Milestone 1 Completion](development/records/MILESTONE_1_COMPLETION.md)
- [Roadmap](docs/roadmap.md)

## Getting Help

If you need help or have questions, you can:

1. Check existing documentation in the `docs/` directory
2. Open an issue on GitHub
3. Contact the development team

Thank you for contributing to the Knowledge Base System! 