"""
Privacy Integration Module
Handles integration with the Sankofa privacy layer.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PrivacyBundle:
    """Represents a privacy-preserving data bundle."""
    bundle_id: str
    version: str
    privacy_level: str
    content_items: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    privacy_tokens: Dict[str, str]  # Privacy-safe reference tokens


class PrivacyIntegration:
    """
    Integration with the Sankofa privacy layer.
    
    This class handles the privacy-preserving aspects of the knowledge base,
    ensuring that sensitive information is properly tokenized and protected.
    """
    
    def __init__(self, kb_manager=None, config_path: Optional[str] = None):
        """
        Initialize the privacy integration.
        
        Args:
            kb_manager: Knowledge base manager instance
            config_path: Path to privacy configuration file
        """
        from knowledge_base import KnowledgeBaseManager
        
        self.kb = kb_manager or KnowledgeBaseManager()
        self.config = self._load_privacy_config(config_path)
        self.validator = PrivacyValidator(self.config)
    
    def _load_privacy_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load privacy integration configuration.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        if config_path:
            path = Path(config_path)
        else:
            path = Path("config/sankofa_integration.yaml")
        
        if path.exists():
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def import_privacy_bundle(self, bundle_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Import a privacy data bundle into the knowledge base.
        
        Args:
            bundle_path: Path to privacy bundle file
            
        Returns:
            Import result summary
        """
        try:
            logger.info(f"Importing privacy bundle from {bundle_path}")
            
            # Load and validate bundle
            bundle = self._load_bundle(bundle_path)
            validation_result = self.validator.validate_bundle(bundle)
            
            if not validation_result['valid']:
                return {
                    "success": False,
                    "error": "Privacy validation failed",
                    "details": validation_result['errors']
                }
            
            # Process each content item
            imported_items = []
            saved_files = []
            
            for item in bundle.content_items:
                processed_item = self._process_privacy_item(item, bundle)
                if processed_item:
                    filepath = self.kb.save_content(processed_item['content'], processed_item['type'])
                    saved_files.append(filepath)
                    imported_items.append(processed_item)
            
            # Create organizational metadata while preserving privacy
            enriched_items = self._enrich_with_organization(imported_items, bundle)
            
            # Save to knowledge base
            for item in enriched_items:
                try:
                    filepath = self.kb.save_content(item['content'], item['type'])
                    saved_files.append(filepath)
                    logger.info(f"Saved {item['type']}: {filepath}")
                except Exception as e:
                    logger.error(f"Error saving item: {e}")
            
            return {
                "success": True,
                "bundle_id": bundle.bundle_id,
                "items_imported": len(imported_items),
                "files_created": len(saved_files),
                "privacy_level": bundle.privacy_level,
                "message": f"Successfully imported {len(imported_items)} items from privacy bundle"
            }
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to import privacy bundle: {e}"
            }
    
    def export_to_privacy_bundle(self, export_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export knowledge base content to a privacy-preserving bundle.
        
        Args:
            export_config: Optional export configuration
            
        Returns:
            Export result with bundle path
        """
        try:
            config = export_config or self.config.get('export', {})
            
            # Collect all knowledge base content
            kb_content = self._collect_kb_content()
            
            # Validate privacy compliance before export
            privacy_check = self.validator.validate_export(kb_content)
            if not privacy_check['valid']:
                return {
                    "success": False,
                    "error": "Privacy validation failed for export",
                    "details": privacy_check['errors']
                }
            
            # Create privacy bundle
            bundle = self._create_privacy_bundle(kb_content, config)
            
            # Save bundle
            bundle_path = self._save_bundle(bundle, config)
            
            return {
                "success": True,
                "bundle_path": str(bundle_path),
                "bundle_id": bundle.bundle_id,
                "items_exported": len(bundle.content_items),
                "message": f"Successfully exported {len(bundle.content_items)} items to privacy bundle"
            }
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to export to privacy bundle: {e}"
            }
    
    def process_privacy_stream(self, privacy_stream_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process streaming data with privacy preservation.
        
        Args:
            privacy_stream_data: Privacy-preserving data stream
            
        Returns:
            Processing result
        """
        try:
            # Validate streaming data
            if not self.validator.validate_stream_item(privacy_stream_data):
                return {
                    "success": False,
                    "error": "Stream data failed privacy validation"
                }
            
            # Process the stream item
            processed_item = self._process_stream_item(privacy_stream_data)
            
            # Intelligent categorization and organization
            organized_item = self._organize_stream_item(processed_item)
            
            # Save to knowledge base
            filepath = self.kb.save_content(organized_item['content'], organized_item['type'])
            
            return {
                "success": True,
                "item_type": organized_item['type'],
                "file_saved": filepath,
                "privacy_preserved": True,
                "message": "Stream item processed and organized successfully"
            }
            
        except Exception as e:
            logger.error(f"Stream processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to process stream item: {e}"
            }
    
    def _load_bundle(self, bundle_path: Union[str, Path]) -> PrivacyBundle:
        """Load and parse a privacy bundle."""
        with open(bundle_path, 'r') as f:
            raw_data = json.load(f)
        
        return PrivacyBundle(
            bundle_id=raw_data['bundle_id'],
            version=raw_data['version'],
            privacy_level=raw_data['privacy_level'],
            content_items=raw_data['content_items'],
            metadata=raw_data.get('metadata', {}),
            privacy_tokens=raw_data.get('privacy_tokens', {})
        )
    
    def _process_privacy_item(self, item: Dict[str, Any], bundle: PrivacyBundle) -> Dict[str, Any]:
        """Process a single privacy item while preserving privacy."""
        # Map privacy types to knowledge base types
        type_mapping = self.config.get('integration', {}).get('import', {}).get('data_mapping', {})
        
        privacy_type = item.get('privacy_type', 'unknown')
        kb_type = type_mapping.get(privacy_type, 'note')
        
        # Preserve privacy tokens and de-identification
        privacy_metadata = {
            'privacy_id': item.get('privacy_id'),
            'privacy_level': bundle.privacy_level,
            'privacy_tokens': item.get('privacy_tokens', {}),
            'deidentified': True
        }
        
        # Extract content while maintaining privacy
        content = {
            'id': self.kb.generate_id(),
            'created': item.get('created', self.kb.get_timestamp()),
            'type': kb_type,
            'title': item.get('title', 'Imported from privacy layer'),
            'content': item.get('content', ''),
            'privacy_metadata': privacy_metadata,
            'tags': item.get('tags', []),
            'category': item.get('category', 'imported')
        }
        
        return {
            'type': kb_type,
            'content': content,
            'original_item': item
        }
    
    def _process_stream_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a streaming item with privacy preservation."""
        # This is a simplified implementation
        content_type = item.get('type', 'note')
        
        return {
            'content': item,
            'type': content_type
        }
    
    def _organize_stream_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Add organizational intelligence to a stream item."""
        # This is a simplified implementation
        return item
    
    def _collect_kb_content(self) -> List[Dict[str, Any]]:
        """Collect content from the knowledge base for export."""
        # This is a simplified implementation - real implementation would query all KB content
        return []
    
    def _create_privacy_bundle(self, content: List[Dict[str, Any]], config: Dict[str, Any]) -> PrivacyBundle:
        """Create a privacy bundle from knowledge base content."""
        from knowledge_base.utils.helpers import generate_id, get_timestamp
        
        bundle_id = f"kb-export-{generate_id()}"
        
        return PrivacyBundle(
            bundle_id=bundle_id,
            version="1.0.0",
            privacy_level=config.get('privacy_level', 'standard'),
            content_items=content,
            metadata={
                "exported_at": get_timestamp(),
                "source": "knowledge_base",
                "item_count": len(content)
            },
            privacy_tokens={}
        )
    
    def _save_bundle(self, bundle: PrivacyBundle, config: Dict[str, Any]) -> Path:
        """Save a privacy bundle to disk."""
        from datetime import datetime
        
        # Determine export path
        export_dir = Path(config.get('export_dir', 'exports'))
        export_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"portable_kb_bundle_{timestamp}.json"
        filepath = export_dir / filename
        
        # Convert bundle to dict
        bundle_dict = {
            "bundle_id": bundle.bundle_id,
            "version": bundle.version,
            "privacy_level": bundle.privacy_level,
            "content_items": bundle.content_items,
            "metadata": bundle.metadata,
            "privacy_tokens": bundle.privacy_tokens
        }
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(bundle_dict, f, indent=2)
        
        return filepath
    
    def _enrich_with_organization(self, items: List[Dict[str, Any]], bundle: PrivacyBundle) -> List[Dict[str, Any]]:
        """Add organizational intelligence while preserving privacy."""
        # This is a simplified implementation
        return items


class PrivacyValidator:
    """Validates that privacy is maintained throughout processing."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the privacy validator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    def validate_bundle(self, bundle: PrivacyBundle) -> Dict[str, Any]:
        """
        Validate that a privacy bundle maintains privacy compliance.
        
        Args:
            bundle: Privacy bundle to validate
            
        Returns:
            Validation result
        """
        errors = []
        
        # Check bundle structure
        if not bundle.bundle_id:
            errors.append("Missing bundle ID")
        
        if not bundle.privacy_level:
            errors.append("Missing privacy level")
        
        # Validate each content item
        for i, item in enumerate(bundle.content_items):
            item_errors = self._validate_item_privacy(item)
            if item_errors:
                errors.extend([f"Item {i}: {error}" for error in item_errors])
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'privacy_level': bundle.privacy_level
        }
    
    def validate_export(self, content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate content before export to ensure privacy compliance.
        
        Args:
            content: Content to export
            
        Returns:
            Validation result
        """
        errors = []
        
        for item in content:
            # Check for potential re-identification risks
            if self._contains_identifying_info(item):
                errors.append(f"Item {item.get('id', 'unknown')} may contain identifying information")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def validate_stream_item(self, item: Dict[str, Any]) -> bool:
        """
        Validate a streaming item for privacy compliance.
        
        Args:
            item: Stream item to validate
            
        Returns:
            True if privacy-compliant, False otherwise
        """
        return not self._contains_identifying_info(item)
    
    def _validate_item_privacy(self, item: Dict[str, Any]) -> List[str]:
        """
        Validate individual item for privacy compliance.
        
        Args:
            item: Item to validate
            
        Returns:
            List of error messages, empty if valid
        """
        errors = []
        
        if not item.get('privacy_tokens'):
            errors.append("Missing privacy tokens")
        
        if self._contains_identifying_info(item):
            errors.append("Item may contain identifying information")
        
        return errors
    
    def _contains_identifying_info(self, item: Dict[str, Any]) -> bool:
        """
        Check if item contains potentially identifying information.
        
        Args:
            item: Item to check
            
        Returns:
            True if identifying info found, False otherwise
        """
        content = str(item.get('content', '')).lower()
        
        # Simple patterns that might indicate identifying info
        identifying_patterns = [
            '@',  # Email addresses
            'phone:', 'tel:', 'mobile:',  # Phone numbers
            'ssn:', 'social security',  # SSN
            'address:', 'street:', 'home:'  # Addresses
        ]
        
        return any(pattern in content for pattern in identifying_patterns) 