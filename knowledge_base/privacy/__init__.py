"""
Privacy Module
Core privacy components for knowledge base system.
"""

from knowledge_base.privacy.smart_anonymization import PrivacyEngine, DeidentificationResult
from knowledge_base.privacy.session_manager import PrivacySessionManager

__all__ = ['PrivacyEngine', 'PrivacySessionManager', 'DeidentificationResult'] 