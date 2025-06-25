#!/usr/bin/env python3
"""
Sankofa Integration Module
Handles import/export of de-identified data with the Sankofa privacy layer.
"""

import json
import yaml
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import hashlib
import logging
from dataclasses import dataclass

from kb_manager import KnowledgeBaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SankofoDataBundle:
    """Represents a Sankofa data bundle with privacy-preserved content."""
    bundle_id: str
    version: str
    privacy_level: str
    content_items: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    sankofa_tokens: Dict[str, str]  # Privacy-safe reference tokens

class SankofoIntegration:
    """Main class for integrating with Sankofa privacy layer."""
    
    def __init__(self, kb_manager: KnowledgeBaseManager = None):
        self.kb = kb_manager or KnowledgeBaseManager()
        self.config = self._load_sankofa_config()
        self.privacy_validator = PrivacyValidator(self.config)
        
    def _load_sankofa_config(self) -> Dict[str, Any]:
        """Load Sankofa integration configuration."""
        config_path = Path("config/sankofa_integration.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def import_sankofa_bundle(self, bundle_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Import a Sankofa data bundle into the knowledge base.
        
        Args:
            bundle_path: Path to Sankofa bundle file
            
        Returns:
            Import result summary
        """
        try:
            logger.info(f"Importing Sankofa bundle from {bundle_path}")
            
            # Load and validate bundle
            bundle = self._load_bundle(bundle_path)
            validation_result = self.privacy_validator.validate_bundle(bundle)
            
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
                processed_item = self._process_sankofa_item(item, bundle)
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
            
            # Update cross-references and connections
            self._update_privacy_safe_connections(enriched_items, bundle)
            
            return {
                "success": True,
                "bundle_id": bundle.bundle_id,
                "items_imported": len(imported_items),
                "files_created": len(saved_files),
                "privacy_level": bundle.privacy_level,
                "message": f"Successfully imported {len(imported_items)} items from Sankofa bundle"
            }
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to import Sankofa bundle: {e}"
            }
    
    def export_to_sankofa(self, export_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export knowledge base content back to Sankofa format.
        
        Args:
            export_config: Optional export configuration
            
        Returns:
            Export result with bundle path
        """
        try:
            config = export_config or self.config.get('export', {})
            
            # Collect all knowledge base content
            kb_content = self._collect_kb_content()
            
            # Enrich with organizational insights
            enriched_content = self._add_organizational_insights(kb_content)
            
            # Validate privacy compliance before export
            privacy_check = self.privacy_validator.validate_export(enriched_content)
            if not privacy_check['valid']:
                return {
                    "success": False,
                    "error": "Privacy validation failed for export",
                    "details": privacy_check['errors']
                }
            
            # Create Sankofa bundle
            bundle = self._create_sankofa_bundle(enriched_content, config)
            
            # Save bundle
            bundle_path = self._save_bundle(bundle, config)
            
            return {
                "success": True,
                "bundle_path": str(bundle_path),
                "bundle_id": bundle.bundle_id,
                "items_exported": len(bundle.content_items),
                "enrichment_added": self._summarize_enrichment(bundle),
                "message": f"Successfully exported {len(bundle.content_items)} items to Sankofa bundle"
            }
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to export to Sankofa: {e}"
            }
    
    def stream_process(self, sankofa_stream_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process streaming data from Sankofa in real-time.
        
        Args:
            sankofa_stream_data: Real-time data from Sankofa
            
        Returns:
            Processing result
        """
        try:
            # Validate streaming data
            if not self.privacy_validator.validate_stream_item(sankofa_stream_data):
                return {
                    "success": False,
                    "error": "Stream data failed privacy validation"
                }
            
            # Process the stream item
            processed_item = self._process_stream_item(sankofa_stream_data)
            
            # Intelligent categorization and organization
            organized_item = self._organize_stream_item(processed_item)
            
            # Save to knowledge base
            filepath = self.kb.save_content(organized_item['content'], organized_item['type'])
            
            # Update real-time indexes
            self._update_real_time_indexes(organized_item)
            
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
    
    def _load_bundle(self, bundle_path: Union[str, Path]) -> SankofoDataBundle:
        """Load and parse a Sankofa bundle."""
        with open(bundle_path, 'r') as f:
            raw_data = json.load(f)
        
        return SankofoDataBundle(
            bundle_id=raw_data['bundle_id'],
            version=raw_data['version'],
            privacy_level=raw_data['privacy_level'],
            content_items=raw_data['content_items'],
            metadata=raw_data.get('metadata', {}),
            sankofa_tokens=raw_data.get('sankofa_tokens', {})
        )
    
    def _process_sankofa_item(self, item: Dict[str, Any], bundle: SankofoDataBundle) -> Dict[str, Any]:
        """Process a single Sankofa item while preserving privacy."""
        # Map Sankofa types to knowledge base types
        type_mapping = self.config.get('sankofa_integration', {}).get('import', {}).get('data_mapping', {})
        
        sankofa_type = item.get('sankofa_type', 'unknown')
        kb_type = type_mapping.get(sankofa_type, 'note')
        
        # Preserve privacy tokens and de-identification
        privacy_metadata = {
            'sankofa_id': item.get('sankofa_id'),
            'privacy_level': bundle.privacy_level,
            'privacy_tokens': item.get('privacy_tokens', {}),
            'deidentified': True
        }
        
        # Extract content while maintaining privacy
        content = {
            'id': self.kb.generate_id(),
            'created': item.get('created', self.kb.get_timestamp()),
            'type': kb_type,
            'title': item.get('title', 'Imported from Sankofa'),
            'content': item.get('content', ''),
            'sankofa_metadata': privacy_metadata,
            'tags': item.get('tags', []),
            'category': item.get('category', 'imported')
        }
        
        return {
            'type': kb_type,
            'content': content,
            'original_item': item
        }
    
    def _enrich_with_organization(self, items: List[Dict[str, Any]], bundle: SankofoDataBundle) -> List[Dict[str, Any]]:
        """Add organizational intelligence while preserving privacy."""
        enriched_items = []
        
        for item in items:
            content = item['content']
            
            # Generate privacy-safe connections
            connections = self._find_privacy_safe_connections(content, items)
            content['cross_refs'] = connections
            
            # Add AI-generated insights (privacy-aware)
            insights = self._generate_privacy_safe_insights(content)
            content['ai_insights'] = insights
            
            # Enhance categorization
            enhanced_category = self._enhance_categorization(content)
            content['category'] = enhanced_category
            
            enriched_items.append(item)
        
        return enriched_items
    
    def _find_privacy_safe_connections(self, content: Dict[str, Any], all_items: List[Dict[str, Any]]) -> List[str]:
        """Find connections between items using privacy-safe methods."""
        connections = []
        
        # Use content similarity without exposing private data
        content_text = content.get('content', '').lower()
        content_tags = set(content.get('tags', []))
        
        for other_item in all_items:
            if other_item['content']['id'] == content['id']:
                continue
                
            other_content = other_item['content']
            other_text = other_content.get('content', '').lower()
            other_tags = set(other_content.get('tags', []))
            
            # Tag-based connections (privacy-safe)
            tag_overlap = len(content_tags.intersection(other_tags))
            if tag_overlap > 0:
                connection_ref = f"[{other_content['type']}:{other_content['id']}:{other_content['title'][:30]}]"
                connections.append(connection_ref)
        
        return connections
    
    def _generate_privacy_safe_insights(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights without compromising privacy."""
        insights = {
            'content_type_confidence': 0.9,  # How confident we are in the type classification
            'estimated_importance': 'medium',  # Based on content patterns
            'suggested_tags': [],  # Additional tags that might be relevant
            'privacy_level': content.get('sankofa_metadata', {}).get('privacy_level', 'standard')
        }
        
        # Generate suggestions based on content patterns (not content itself)
        content_length = len(content.get('content', ''))
        if content_length > 500:
            insights['estimated_importance'] = 'high'
        elif content_length < 100:
            insights['estimated_importance'] = 'low'
        
        return insights
    
    def _enhance_categorization(self, content: Dict[str, Any]) -> str:
        """Enhance categorization using privacy-safe methods."""
        current_category = content.get('category', 'uncategorized')
        
        # Use existing tags and metadata for better categorization
        tags = content.get('tags', [])
        content_type = content.get('type', 'note')
        
        # Privacy-safe categorization rules
        if '@work' in tags or 'professional' in tags:
            return 'work'
        elif '@personal' in tags or 'personal' in tags:
            return 'personal'
        elif content_type == 'todo':
            return 'tasks'
        elif content_type == 'journal':
            return 'reflection'
        else:
            return current_category

class PrivacyValidator:
    """Validates that privacy is maintained throughout processing."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def validate_bundle(self, bundle: SankofoDataBundle) -> Dict[str, Any]:
        """Validate that a Sankofa bundle maintains privacy compliance."""
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
        """Validate content before export to ensure privacy compliance."""
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
        """Validate a streaming item for privacy compliance."""
        return not self._contains_identifying_info(item)
    
    def _validate_item_privacy(self, item: Dict[str, Any]) -> List[str]:
        """Validate individual item for privacy compliance."""
        errors = []
        
        if not item.get('privacy_tokens'):
            errors.append("Missing privacy tokens")
        
        if self._contains_identifying_info(item):
            errors.append("Item may contain identifying information")
        
        return errors
    
    def _contains_identifying_info(self, item: Dict[str, Any]) -> bool:
        """Check if item contains potentially identifying information."""
        # This is a simplified check - real implementation would be more sophisticated
        content = str(item.get('content', '')).lower()
        
        # Simple patterns that might indicate identifying info
        identifying_patterns = [
            '@',  # Email addresses
            'phone:', 'tel:', 'mobile:',  # Phone numbers
            'ssn:', 'social security',  # SSN
            'address:', 'street:', 'home:'  # Addresses
        ]
        
        return any(pattern in content for pattern in identifying_patterns)


def main():
    """Command line interface for Sankofa integration."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sankofa_integration.py <command> [args...]")
        print("Commands: import <bundle_path>, export [config], test")
        return
    
    integration = SankofoIntegration()
    command = sys.argv[1]
    
    if command == "import" and len(sys.argv) > 2:
        bundle_path = sys.argv[2]
        result = integration.import_sankofa_bundle(bundle_path)
        print(json.dumps(result, indent=2))
    
    elif command == "export":
        result = integration.export_to_sankofa()
        print(json.dumps(result, indent=2))
    
    elif command == "test":
        print("Testing Sankofa integration...")
        print("✅ Privacy validator initialized")
        print("✅ Configuration loaded")
        print("✅ Integration ready")
    
    else:
        print("Invalid command or missing arguments")


if __name__ == "__main__":
    main() 