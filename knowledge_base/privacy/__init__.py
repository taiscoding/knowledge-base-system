"""
Privacy Module for Knowledge Base System.

This module provides privacy-preserving features for the knowledge base system,
ensuring sensitive information is protected during processing.
"""

from knowledge_base.privacy.smart_anonymization import PrivacyEngine, DeidentificationResult
from knowledge_base.privacy.session_manager import PrivacySessionManager
from knowledge_base.privacy.token_intelligence_bridge import TokenIntelligenceBridge
from knowledge_base.privacy.adapter import PrivacyIntegrationAdapter, PrivacyValidatorAdapter, PrivacyBundle as AdapterPrivacyBundle

# Import deprecated module (removed circular import)
import warnings

# Show deprecation warning for the legacy module
warnings.warn(
    "The knowledge_base.privacy.py module is deprecated and will be removed in a future version. "
    "Use knowledge_base.privacy.smart_anonymization.PrivacyEngine and related components instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    'PrivacyEngine', 
    'DeidentificationResult',
    'PrivacySessionManager',
    'TokenIntelligenceBridge',
    'PrivacyIntegrationAdapter',
    'PrivacyValidatorAdapter',
    'AdapterPrivacyBundle',
    # Legacy items now removed from __all__ to prevent circular imports
] 