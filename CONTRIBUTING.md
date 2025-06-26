# Contributing to Knowledge Base & Token Intelligence System

*Last updated: June 23, 2025*

Thank you for your interest in contributing to our project! This document provides guidelines and instructions for contributing to the Knowledge Base & Token Intelligence System.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Privacy Guidelines](#privacy-guidelines)

## Project Structure

The project consists of two main packages:

- **knowledge_base**: Content organization and management
- **token_intelligence**: Privacy-preserving intelligence generation

Each package follows a similar structure:

```
package/
├── __init__.py      # Package initialization
├── core/            # Core functionality
├── utils/           # Utilities and helpers
├── tests/           # Tests for the package
└── README.md        # Package-specific documentation
```

## Getting Started

### Setup Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/taiscoding/knowledge-base-system.git
   cd knowledge-base-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the coding standards

3. Add tests for your changes

4. Ensure all tests pass:
   ```bash
   pytest
   ```

5. Update documentation as needed

6. Submit a pull request

## Coding Standards

We follow these standards for code quality:

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use meaningful variable and function names
- Keep lines under 100 characters
- Use docstrings for all modules, classes, and functions

### Imports

- Group imports in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library-specific imports
- Within each group, sort imports alphabetically

### Type Annotations

- Use type annotations for all function parameters and return values
- Use Optional[Type] for parameters that might be None

### Example

```python
"""
Module docstring with a brief description.
"""

import os
from typing import Dict, List, Optional

import yaml

from knowledge_base.utils import generate_id


def process_data(input_data: List[Dict[str, str]], flag: Optional[bool] = None) -> Dict[str, Any]:
    """
    Process the input data.
    
    Args:
        input_data: List of dictionaries to process
        flag: Optional flag to control processing
    
    Returns:
        Processed data dictionary
    """
    result = {}
    # Implementation
    return result
```

## Testing Guidelines

### Test Structure

- Place tests in the `tests` directory parallel to the code being tested
- Name test files with `test_` prefix (e.g., `test_manager.py`)
- Name test functions with `test_` prefix (e.g., `test_process_content`)

### Test Coverage

- Aim for at least 80% test coverage
- Include unit tests for all public functions
- Include integration tests for key workflows
- Test edge cases and error conditions

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=knowledge_base --cov=token_intelligence

# Run specific test file
pytest tests/test_manager.py
```

## Documentation

We value clear and comprehensive documentation:

### Code Documentation

- Every module should have a module-level docstring
- Every class and function should have a docstring explaining:
  - What it does
  - Parameters (with types)
  - Return values (with types)
  - Exceptions raised (if applicable)
  - Examples (for complex functions)

### User Documentation

When adding features, update the relevant documentation:
- User Guide for end-user features
- API Reference for developer-facing interfaces
- Integration Guide for integration points
- Privacy Design for privacy-related changes

## Pull Request Process

1. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Include screenshots for UI changes

2. **Code Review**
   - Address reviewer feedback
   - Make requested changes
   - Respond to comments

3. **Continuous Integration**
   - Ensure all CI checks pass
   - Fix any failing tests or linting issues

4. **Approval and Merge**
   - Once approved, maintainers will merge your PR
   - Squash commits if needed for a cleaner history

## Privacy Guidelines

Since this project handles privacy-sensitive operations, additional guidelines apply:

### Privacy Principles

- **Zero Data Exposure**: Never process or store original sensitive data
- **Token-Only Processing**: All operations should work exclusively with tokens
- **Session Isolation**: Maintain proper session boundaries
- **Transparency**: Document privacy decisions clearly

### Implementation Guidelines

- All token intelligence functions must validate they only process tokens
- Never store mappings between tokens and original data in the main system
- Privacy layer integration must maintain clear boundaries
- Add privacy validation tests for new features

### Privacy Testing

- Include explicit tests verifying privacy boundaries are maintained
- Test for potential re-identification risks
- Validate proper token isolation in all operations

---

Thank you for contributing to the Knowledge Base & Token Intelligence System! Your efforts help build a better privacy-preserving knowledge system for everyone. 