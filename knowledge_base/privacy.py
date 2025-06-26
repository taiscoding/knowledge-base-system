"""
Privacy Integration Module (Legacy)

DEPRECATED: This module is maintained for backwards compatibility only.
Please use the privacy.smart_anonymization and related modules instead.

This forwards all calls to the new adapter class that uses the modern privacy components.
"""

import warnings
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

# Issue deprecation warning
warnings.warn(
    "The privacy.py module is deprecated and will be removed in a future version. "
    "Use privacy.smart_anonymization module and related components instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import adapter classes
from knowledge_base.privacy.adapter import (
    PrivacyIntegrationAdapter,
    PrivacyBundle as AdapterPrivacyBundle,
    PrivacyValidatorAdapter
)

# Re-export from modern components for compatibility
from knowledge_base.privacy.smart_anonymization import PrivacyEngine, DeidentificationResult
from knowledge_base.privacy.session_manager import PrivacySessionManager

# Legacy class definitions that forward to modern implementations

@dataclass
class PrivacyBundle:
    """
    Legacy PrivacyBundle class that forwards to the new adapter implementation.
    
    This is maintained for backwards compatibility only.
    """
    bundle_id: str
    version: str
    privacy_level: str
    content_items: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    privacy_tokens: Dict[str, str]  # Privacy-safe reference tokens
    
    def to_adapter_bundle(self):
        """Convert to adapter bundle for use with new components."""
        return AdapterPrivacyBundle(
            bundle_id=self.bundle_id,
            version=self.version,
            privacy_level=self.privacy_level,
            content_items=self.content_items,
            metadata=self.metadata,
            privacy_tokens=self.privacy_tokens
        )
    
    @classmethod
    def from_adapter_bundle(cls, adapter_bundle):
        """Create from adapter bundle."""
        return cls(
            bundle_id=adapter_bundle.bundle_id,
            version=adapter_bundle.version,
            privacy_level=adapter_bundle.privacy_level,
            content_items=adapter_bundle.content_items,
            metadata=adapter_bundle.metadata,
            privacy_tokens=adapter_bundle.privacy_tokens
        )


class PrivacyIntegration:
    """
    Legacy PrivacyIntegration class that forwards to the new adapter implementation.
    
    This is maintained for backwards compatibility only.
    """
    
    def __init__(self, kb_manager=None, config_path: Optional[str] = None):
        """
        Initialize the privacy integration.
        
        Args:
            kb_manager: Knowledge base manager instance
            config_path: Path to privacy configuration file
        """
        # Forward to adapter
        self.adapter = PrivacyIntegrationAdapter(kb_manager, config_path)
        self.kb = self.adapter.kb
        self.config = self.adapter.config
        self.validator = PrivacyValidator(self.config)
    
    def import_privacy_bundle(self, bundle_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Import a privacy data bundle into the knowledge base.
        
        Args:
            bundle_path: Path to privacy bundle file
            
        Returns:
            Import result summary
        """
        # Forward to adapter
        return self.adapter.import_privacy_bundle(bundle_path)
    
    def export_to_privacy_bundle(self, export_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export knowledge base content to a privacy-preserving bundle.
        
        Args:
            export_config: Optional export configuration
            
        Returns:
            Export result with bundle path
        """
        # Forward to adapter
        return self.adapter.export_to_privacy_bundle(export_config)
    
    def process_privacy_stream(self, privacy_stream_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process streaming data with privacy preservation.
        
        Args:
            privacy_stream_data: Privacy-preserving data stream
            
        Returns:
            Processing result
        """
        # Forward to adapter
        return self.adapter.process_privacy_stream(privacy_stream_data)


class PrivacyValidator:
    """
    Legacy PrivacyValidator class that forwards to the new adapter implementation.
    
    This is maintained for backwards compatibility only.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the privacy validator.
        
        Args:
            config: Configuration dictionary
        """
        # Forward to adapter
        self.adapter = PrivacyValidatorAdapter(config)
        self.config = config
    
    def validate_bundle(self, bundle: PrivacyBundle) -> Dict[str, Any]:
        """
        Validate that a privacy bundle maintains privacy compliance.
        
        Args:
            bundle: Privacy bundle to validate
            
        Returns:
            Validation result
        """
        # Convert to adapter bundle and forward
        adapter_bundle = bundle.to_adapter_bundle()
        return self.adapter.validate_bundle(adapter_bundle)
    
    def validate_export(self, content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate content before export to ensure privacy compliance.
        
        Args:
            content: Content to export
            
        Returns:
            Validation result
        """
        # Forward to adapter
        return self.adapter.validate_export(content)
    
    def validate_stream_item(self, item: Dict[str, Any]) -> bool:
        """
        Validate a streaming item for privacy compliance.
        
        Args:
            item: Stream item to validate
            
        Returns:
            True if privacy-compliant, False otherwise
        """
        # Forward to adapter
        return self.adapter.validate_stream_item(item)
    
    def _validate_item_privacy(self, item: Dict[str, Any]) -> List[str]:
        """
        Validate individual item for privacy compliance.
        
        Args:
            item: Item to validate
            
        Returns:
            List of error messages, empty if valid
        """
        # Forward to adapter
        return self.adapter._validate_item_privacy(item)
    
    def _contains_identifying_info(self, item: Dict[str, Any]) -> bool:
        """
        Check if item contains potentially identifying information.
        
        Args:
            item: Item to check
            
        Returns:
            True if identifying info found, False otherwise
        """
        # Forward to adapter
        return self.adapter._contains_identifying_info(item) 