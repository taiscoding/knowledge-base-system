"""
Token Intelligence System
Privacy-preserving token-based intelligence generation.

This package provides a modular and extensible system for generating intelligence
from privacy tokens, without using any original data. It includes core functionality
for token extraction, intelligence generation, pattern detection, and relationship analysis.

This system is designed to work seamlessly with the Knowledge Base system and the
Sankofa privacy layer to provide a complete privacy-preserving knowledge management solution.
"""

__version__ = "1.0.0"
__author__ = "Knowledge Base Team"

from token_intelligence.core import (
    TokenIntelligenceEngine,
    TokenIntelligenceRequest,
    TokenIntelligenceResponse,
    BatchTokenRequest,
    BatchTokenResponse,
    extract_tokens
)

from token_intelligence.api import (
    app, 
    start_server
)

# Expose main classes and functions at package level
__all__ = [
    '__version__',
    '__author__',
    
    # Core
    'TokenIntelligenceEngine',
    'TokenIntelligenceRequest',
    'TokenIntelligenceResponse',
    'BatchTokenRequest', 
    'BatchTokenResponse',
    'extract_tokens',
    
    # API
    'app',
    'start_server'
]

# Integration note
"""
Integration with Knowledge Base:

To use Token Intelligence with the Knowledge Base system:

1. Process content through the Knowledge Base
2. Use the Sankofa privacy layer to tokenize sensitive content
3. Pass tokenized content to the Token Intelligence Engine
4. Apply the resulting intelligence back to the Knowledge Base

See the 'docs/examples/combined_usage.py' for a complete example.
"""
