"""
Privacy Module for Knowledge Base System.

This module provides comprehensive privacy-preserving features for the knowledge base system,
ensuring sensitive information is protected during processing.

Milestone 3 Privacy Enhancements:
- End-to-End Encryption
- Granular Privacy Controls
- Privacy Audit Logging
- Differential Privacy
- Privacy Certification Framework
"""

# Legacy imports (existing functionality)
from knowledge_base.privacy.smart_anonymization import PrivacyEngine, DeidentificationResult
from knowledge_base.privacy.session_manager import PrivacySessionManager
from knowledge_base.privacy.token_intelligence_bridge import TokenIntelligenceBridge
from knowledge_base.privacy.adapter import PrivacyIntegrationAdapter, PrivacyValidatorAdapter, PrivacyBundle as AdapterPrivacyBundle
from knowledge_base.privacy.circuit_breaker import CircuitBreaker, CircuitBreakerError, CircuitOpenError

# Milestone 3 Privacy Enhancements
# End-to-End Encryption
from knowledge_base.privacy.encryption import (
    KeyManager, ContentEncryptionManager, EncryptedStorageAdapter,
    EncryptionResult, EncryptionKey, get_default_encryption_manager
)

# Granular Privacy Controls
from knowledge_base.privacy.privacy_controls import (
    PrivacyLevel, PrivacyRule, PrivacyProfile, PrivacySettings,
    PrivacyRuleEngine, PrivacyControlManager,
    create_default_content_profiles
)

# Privacy Audit Logging
from knowledge_base.privacy.audit_logging import (
    PrivacyOperation, PrivacyImpact, AuditLogEntry,
    PrivacyAuditLogger, ComplianceReporter
)

# Differential Privacy
from knowledge_base.privacy.differential_privacy import (
    NoiseDistribution, PrivacyBudget, BudgetExhaustedException,
    PrivacyBudgetManager, DifferentialPrivacyMechanism,
    PrivacyPreservingAnalytics
)

# Privacy Certification Framework
from knowledge_base.privacy.certification import (
    ComplianceStandard, ComplianceLevel, RiskLevel,
    ComplianceRequirement, ComplianceAssessment, PrivacyImpactAssessment,
    ComplianceChecker, PrivacyImpactAssessmentTool, CertificationReporter
)

# Import deprecated module (for backward compatibility)
import warnings

# Show deprecation warning for the legacy module
warnings.warn(
    "The knowledge_base.privacy.py module is deprecated and will be removed in a future version. "
    "Use knowledge_base.privacy.smart_anonymization.PrivacyEngine and related components instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    # Legacy Privacy Components
    'PrivacyEngine', 
    'DeidentificationResult',
    'PrivacySessionManager',
    'TokenIntelligenceBridge',
    'PrivacyIntegrationAdapter',
    'PrivacyValidatorAdapter',
    'AdapterPrivacyBundle',
    'CircuitBreaker',
    'CircuitBreakerError',
    'CircuitOpenError',
    
    # End-to-End Encryption
    'KeyManager',
    'ContentEncryptionManager',
    'EncryptedStorageAdapter',
    'EncryptionResult',
    'EncryptionKey',
    'get_default_encryption_manager',
    
    # Granular Privacy Controls
    'PrivacyLevel',
    'PrivacyRule',
    'PrivacyProfile',
    'PrivacySettings',
    'PrivacyRuleEngine',
    'PrivacyControlManager',
    'create_default_content_profiles',
    
    # Privacy Audit Logging
    'PrivacyOperation',
    'PrivacyImpact',
    'AuditLogEntry',
    'PrivacyAuditLogger',
    'ComplianceReporter',
    
    # Differential Privacy
    'NoiseDistribution',
    'PrivacyBudget',
    'BudgetExhaustedException',
    'PrivacyBudgetManager',
    'DifferentialPrivacyMechanism',
    'PrivacyPreservingAnalytics',
    
    # Privacy Certification Framework
    'ComplianceStandard',
    'ComplianceLevel',
    'RiskLevel',
    'ComplianceRequirement',
    'ComplianceAssessment',
    'PrivacyImpactAssessment',
    'ComplianceChecker',
    'PrivacyImpactAssessmentTool',
    'CertificationReporter',
] 