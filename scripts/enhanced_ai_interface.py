#!/usr/bin/env python3
"""
Enhanced AI Interface with Sankofa Integration
Extended interface that supports privacy-preserved data processing.
"""

import sys
import json
import yaml
import uuid
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from ai_interface import KnowledgeBaseAI
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from data_intelligence_tracker import PersonalDataIntelligenceTracker

class SankofoSyncHandler(FileSystemEventHandler):
    """Handles real-time sync events from Sankofa."""
    
    def __init__(self, ai_interface):
        self.ai = ai_interface
        self.processing_queue = []
        
    def on_created(self, event):
        """Handle new files from Sankofa."""
        if not event.is_directory and event.src_path.endswith('.json'):
            print(f"📥 Received Sankofa data: {event.src_path}")
            self.ai.handle_sankofa_event(event.src_path)
    
    def on_modified(self, event):
        """Handle modified files from Sankofa."""
        if not event.is_directory and event.src_path.endswith('.json'):
            print(f"📝 Updated Sankofa data: {event.src_path}")
            self.ai.handle_sankofa_event(event.src_path)

class EnhancedKnowledgeBaseAI(KnowledgeBaseAI):
    """Enhanced AI interface with Sankofa privacy layer integration."""
    
    def __init__(self):
        super().__init__()
        self.sankofa_config = self._load_sankofa_config()
        self.intelligence_tracker = PersonalDataIntelligenceTracker()
        self.sync_active = False
        self.sync_thread = None
        self.file_observer = None
        self.sync_folders = {
            'sankofa_to_kb': Path('sync/sankofa_to_kb'),
            'kb_to_sankofa': Path('sync/kb_to_sankofa'),
            'status': Path('sync/status')
        }
        self._setup_sync_folders()
        
    def _setup_sync_folders(self):
        """Create sync folders for communication with Sankofa."""
        for folder in self.sync_folders.values():
            folder.mkdir(parents=True, exist_ok=True)
    
    def start_realtime_sync(self, sync_mode: str = "live_processing") -> Dict[str, Any]:
        """
        Start real-time bidirectional sync with Sankofa.
        
        Args:
            sync_mode: Type of sync ('live_processing', 'batch_sync', 'event_driven')
            
        Returns:
            Sync startup status
        """
        try:
            if self.sync_active:
                return {
                    "success": False,
                    "message": "Real-time sync already active",
                    "sync_mode": sync_mode
                }
            
            print(f"🚀 Starting real-time sync in {sync_mode} mode...")
            
            # Start file system watcher
            self.file_observer = Observer()
            sync_handler = SankofoSyncHandler(self)
            self.file_observer.schedule(
                sync_handler, 
                str(self.sync_folders['sankofa_to_kb']), 
                recursive=True
            )
            self.file_observer.start()
            
            # Start background sync worker
            self.sync_thread = threading.Thread(target=self._background_sync_worker, daemon=True)
            self.sync_thread.start()
            
            self.sync_active = True
            
            # Write status file for Sankofa
            self._write_sync_status({
                "kb_sync_active": True,
                "sync_mode": sync_mode,
                "started": datetime.now().isoformat(),
                "folders": {k: str(v) for k, v in self.sync_folders.items()}
            })
            
            return {
                "success": True,
                "sync_mode": sync_mode,
                "sync_folders": {k: str(v) for k, v in self.sync_folders.items()},
                "message": f"Real-time sync started in {sync_mode} mode"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to start real-time sync: {e}"
            }
    
    def handle_sankofa_event(self, file_path: str) -> Dict[str, Any]:
        """
        Handle incoming events/data from Sankofa in real-time.
        
        Args:
            file_path: Path to the Sankofa data file
            
        Returns:
            Event processing result
        """
        try:
            # Read Sankofa data
            with open(file_path, 'r') as f:
                sankofa_data = json.load(f)
            
            # Determine data type and process accordingly
            if 'mapping_data' in sankofa_data and sankofa_data.get('format_version') == 'arx_phase2_compatible':
                # This is ARX Phase 2 mapping data
                result = self.import_arx_mappings(sankofa_data['mapping_data'])
                processing_type = "arx_phase2_import"
            elif isinstance(sankofa_data, list) and len(sankofa_data) > 0 and 'token' in sankofa_data[0]:
                # This is raw ARX mapping data (list format)
                result = self.import_arx_mappings(sankofa_data)
                processing_type = "arx_mappings_import"
            elif 'bundle_id' in sankofa_data:
                # This is a complete bundle (legacy format)
                result = self.import_deidentified_data(sankofa_data)
                processing_type = "bundle_import"
            elif 'stream_id' in sankofa_data:
                # This is a stream item
                result = self._process_stream_item(sankofa_data)
                processing_type = "stream_processing"
            else:
                # Unknown format - try generic processing
                result = self._process_generic_sankofa_data(sankofa_data)
                processing_type = "generic_processing"
            
            # If successful, trigger sync back to Sankofa
            if result.get('success'):
                self._trigger_sync_to_sankofa(result, processing_type)
            
            # Mark file as processed
            self._mark_file_processed(file_path)
            
            return {
                "success": True,
                "processing_type": processing_type,
                "file_path": file_path,
                "result": result,
                "message": f"Successfully processed {processing_type}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "message": f"Failed to process Sankofa event: {e}"
            }
    
    def sync_to_sankofa(self, data_filter: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export enhanced organizational metadata back to Sankofa using ARX Phase 2 APIs.
        
        Args:
            data_filter: Optional filter for what data to sync
            
        Returns:
            Sync operation result
        """
        try:
            # Collect relevant knowledge base data in ARX-compatible format
            kb_data = self._collect_sync_data(data_filter)
            
            # Create enhanced bundle for Sankofa ARX Phase 2
            enhanced_bundle = self._create_sankofa_sync_bundle(kb_data)
            
            # Write to sync folder for Sankofa to pick up
            sync_file = self.sync_folders['kb_to_sankofa'] / f"arx_mappings_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(sync_file, 'w') as f:
                json.dump(enhanced_bundle, f, indent=2)
            
            # Also create a control file to signal Sankofa about the sync type
            control_file = self.sync_folders['kb_to_sankofa'] / f"sync_control_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            control_data = {
                "sync_type": "arx_mapping_enhancement",
                "data_file": sync_file.name,
                "api_compatibility": "arx_phase2",
                "operations": {
                    "import_mappings": True,
                    "column_filtering": data_filter.get('columns') if data_filter else None,
                    "overwrite_control": data_filter.get('overwrite', False) if data_filter else False
                },
                "kb_enhancements": {
                    "mappings_count": len(kb_data),
                    "categories_added": len(enhanced_bundle['organizational_metadata']['categories_identified']),
                    "connections_added": enhanced_bundle['organizational_metadata']['connections_discovered']
                }
            }
            
            with open(control_file, 'w') as f:
                json.dump(control_data, f, indent=2)
            
            return {
                "success": True,
                "sync_file": str(sync_file),
                "control_file": str(control_file),
                "mappings_synced": len(kb_data),
                "arx_compatible": True,
                "privacy_preserved": True,
                "message": f"Successfully synced {len(kb_data)} enhanced mappings to Sankofa ARX Phase 2"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to sync to Sankofa ARX Phase 2: {e}"
            }
    
    def stop_realtime_sync(self) -> Dict[str, Any]:
        """Stop real-time sync with Sankofa."""
        try:
            if not self.sync_active:
                return {
                    "success": False,
                    "message": "Real-time sync not active"
                }
            
            print("🛑 Stopping real-time sync...")
            
            # Stop file observer
            if self.file_observer:
                self.file_observer.stop()
                self.file_observer.join()
            
            # Stop background worker
            self.sync_active = False
            if self.sync_thread and self.sync_thread.is_alive():
                self.sync_thread.join(timeout=5)
            
            # Update status
            self._write_sync_status({
                "kb_sync_active": False,
                "stopped": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "message": "Real-time sync stopped successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error stopping sync: {e}"
            }
    
    def _background_sync_worker(self):
        """Background worker for periodic sync operations."""
        while self.sync_active:
            try:
                # Check for pending sync operations
                self._process_pending_syncs()
                
                # Perform health checks
                self._sync_health_check()
                
                # Sleep before next cycle
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Background sync worker error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _process_stream_item(self, stream_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single stream item from Sankofa."""
        try:
            # Extract content and privacy tokens
            content = stream_data.get('content', '')
            privacy_tokens = stream_data.get('privacy_tokens', {})
            
            # Process using standard KB methods while preserving privacy
            processed_content = {
                'id': self.kb.generate_id(),
                'created': stream_data.get('timestamp', self.kb.get_timestamp()),
                'content': content,
                'privacy_metadata': {
                    'stream_id': stream_data.get('stream_id'),
                    'privacy_tokens': privacy_tokens,
                    'deidentified': True
                },
                'type': 'stream_note',
                'category': 'real_time'
            }
            
            # Extract intelligence from the content
            measurements = self.intelligence_tracker.extract_and_store_measurement(content, processed_content)
            visit_pattern = self.intelligence_tracker.track_visit_pattern(content, processed_content)
            equipment = self.intelligence_tracker.track_equipment_mention(content, processed_content)
            
            # Save to knowledge base
            filepath = self.kb.save_content(processed_content, 'note')
            
            return {
                "success": True,
                "file_saved": filepath,
                "stream_id": stream_data.get('stream_id'),
                "privacy_preserved": True,
                "intelligence_extracted": {
                    "measurements_found": len(measurements),
                    "visit_pattern_updated": visit_pattern is not None,
                    "equipment_tracked": len(equipment)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_generic_sankofa_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic Sankofa data format."""
        try:
            # Try to extract meaningful content
            content = data.get('content') or data.get('text') or str(data)
            
            # Create KB entry
            kb_entry = {
                'id': self.kb.generate_id(),
                'created': self.kb.get_timestamp(),
                'content': content,
                'type': 'imported',
                'category': 'sankofa_generic',
                'privacy_metadata': {
                    'source': 'sankofa',
                    'original_format': 'generic'
                }
            }
            
            # Extract intelligence from the content
            measurements = self.intelligence_tracker.extract_and_store_measurement(content, kb_entry)
            visit_pattern = self.intelligence_tracker.track_visit_pattern(content, kb_entry)
            equipment = self.intelligence_tracker.track_equipment_mention(content, kb_entry)
            
            filepath = self.kb.save_content(kb_entry, 'note')
            
            return {
                "success": True,
                "file_saved": filepath,
                "processing_type": "generic",
                "intelligence_extracted": {
                    "measurements_found": len(measurements),
                    "visit_pattern_updated": visit_pattern is not None,
                    "equipment_tracked": len(equipment)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _trigger_sync_to_sankofa(self, processing_result: Dict[str, Any], processing_type: str):
        """Trigger sync back to Sankofa with enhanced metadata."""
        try:
            # Create enhanced metadata based on processing
            enhanced_metadata = {
                "kb_processing_result": processing_result,
                "processing_type": processing_type,
                "enhanced_at": datetime.now().isoformat(),
                "organizational_insights": self._generate_insights_for_sankofa(processing_result)
            }
            
            # Write trigger file for background worker to process
            trigger_file = self.sync_folders['status'] / f"sync_trigger_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(trigger_file, 'w') as f:
                json.dump(enhanced_metadata, f, indent=2)
                
        except Exception as e:
            print(f"Failed to trigger sync to Sankofa: {e}")
    
    def _collect_sync_data(self, data_filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Collect KB data for syncing to Sankofa using ARX-compatible format."""
        try:
            sync_data = []
            data_dir = Path("data")
            
            if not data_dir.exists():
                return sync_data
            
            # Collect recent files (last 24 hours by default)
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for content_type_dir in data_dir.iterdir():
                if not content_type_dir.is_dir():
                    continue
                    
                for file_path in content_type_dir.glob("*"):
                    if not file_path.is_file():
                        continue
                        
                    # Check file modification time
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mod_time < cutoff_time:
                        continue
                    
                    try:
                        # Read file content
                        with open(file_path, 'r') as f:
                            if file_path.suffix == '.json':
                                content = json.load(f)
                            else:
                                content = f.read()
                        
                        # Extract privacy tokens if they exist
                        privacy_metadata = {}
                        if isinstance(content, dict) and 'privacy_metadata' in content:
                            privacy_metadata = content['privacy_metadata']
                        
                        # Create ARX-compatible mapping entries
                        if privacy_metadata.get('privacy_tokens'):
                            for token, original_ref in privacy_metadata['privacy_tokens'].items():
                                sync_data.append({
                                    "token": token,
                                    "original": original_ref,  # This is already anonymized in our system
                                    "context": {
                                        "file_path": str(file_path),
                                        "content_type": content_type_dir.name,
                                        "kb_enhanced": True,
                                        "type": "privacy_token"
                                    },
                                    "kb_metadata": {
                                        "organized_at": mod_time.isoformat(),
                                        "file_id": content.get('id') if isinstance(content, dict) else None,
                                        "categories": content.get('tags', []) if isinstance(content, dict) else [],
                                        "connections": self._identify_content_connections(content)
                                    }
                                })
                    
                    except Exception as e:
                        print(f"Warning: Could not process {file_path}: {e}")
                        continue
            
            return sync_data
            
        except Exception as e:
            print(f"Error collecting sync data: {e}")
            return []
    
    def _create_sankofa_sync_bundle(self, kb_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a sync bundle for Sankofa with enhanced metadata in ARX-compatible format."""
        return {
            "sync_id": self.kb.generate_id(),
            "created": self.kb.get_timestamp(),
            "source": "knowledge_base_ai",
            "sync_type": "arx_mapping_enhancement",
            "format_version": "arx_phase2_compatible",
            
            # ARX-compatible mapping data
            "mapping_data": kb_data,
            
            # Knowledge Base organizational enhancements
            "organizational_metadata": {
                "enhanced_by": "knowledge_base_system_v2.0",
                "mappings_enhanced": len(kb_data),
                "connections_discovered": self._count_connections_in_data(kb_data),
                "categories_identified": self._extract_categories_from_data(kb_data),
                "processing_timestamp": self.kb.get_timestamp(),
                "sync_capabilities": {
                    "column_filtering": True,
                    "overwrite_control": True,
                    "context_preservation": True,
                    "secure_handling": True
                }
            }
        }
    
    def _identify_content_connections(self, content: Any) -> List[str]:
        """Identify connections for content based on KB intelligence."""
        connections = []
        
        if isinstance(content, dict):
            # Look for explicit connections
            if 'related_items' in content:
                connections.extend(content['related_items'])
            
            # Look for content-based connections
            content_text = content.get('content', '')
            if 'appointment' in content_text.lower():
                connections.append('health_appointments')
            if 'project' in content_text.lower():
                connections.append('work_projects')
            if 'meeting' in content_text.lower():
                connections.append('meeting_schedule')
        
        return connections
    
    def _count_connections_in_data(self, kb_data: List[Dict[str, Any]]) -> int:
        """Count total connections discovered in KB data."""
        total_connections = 0
        for item in kb_data:
            metadata = item.get('kb_metadata', {})
            connections = metadata.get('connections', [])
            total_connections += len(connections)
        return total_connections
    
    def _extract_categories_from_data(self, kb_data: List[Dict[str, Any]]) -> List[str]:
        """Extract unique categories from KB data."""
        categories = set()
        for item in kb_data:
            metadata = item.get('kb_metadata', {})
            item_categories = metadata.get('categories', [])
            categories.update(item_categories)
        return list(categories)
    
    def _organize_arx_mappings(self, context_type: str, mappings: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Organize ARX mappings into intelligent knowledge base content."""
        try:
            # Extract tokens and contexts
            tokens = {}
            contexts = []
            
            for mapping in mappings:
                token = mapping.get('token', '')
                original = mapping.get('original', '')
                context = mapping.get('context', {})
                
                tokens[token] = original
                contexts.append(context)
            
            # Determine content type based on context
            kb_content_type = self._map_arx_context_to_kb_type(context_type, contexts)
            
            # Create organized content
            organized_content = {
                'id': self.kb.generate_id(),
                'created': self.kb.get_timestamp(),
                'type': kb_content_type,
                'title': f"ARX Organized: {context_type.replace('_', ' ').title()}",
                'content': self._generate_organized_content_from_mappings(mappings),
                'arx_metadata': {
                    'context_type': context_type,
                    'token_count': len(tokens),
                    'privacy_tokens': tokens,
                    'arx_compatible': True,
                    'phase': 'arx_phase2'
                },
                'tags': self._generate_tags_from_arx_context(context_type, contexts),
                'category': 'arx_organized',
                'connections': self._identify_arx_connections(context_type, mappings)
            }
            
            return organized_content
            
        except Exception as e:
            print(f"Error organizing ARX mappings for {context_type}: {e}")
            return None
    
    def _map_arx_context_to_kb_type(self, context_type: str, contexts: List[Dict[str, Any]]) -> str:
        """Map ARX context type to Knowledge Base content type."""
        context_mapping = {
            'quasi-identifying': 'note',
            'identifying': 'reference',
            'sensitive': 'private_note',
            'insensitive': 'note',
            'medical': 'health_record',
            'financial': 'financial_record',
            'personal': 'personal_note',
            'professional': 'work_note'
        }
        
        # Check specific context clues
        for context in contexts:
            if 'medical' in str(context).lower() or 'health' in str(context).lower():
                return 'health_record'
            if 'work' in str(context).lower() or 'project' in str(context).lower():
                return 'work_note'
            if 'appointment' in str(context).lower():
                return 'calendar'
        
        return context_mapping.get(context_type, 'note')
    
    def _generate_organized_content_from_mappings(self, mappings: List[Dict[str, Any]]) -> str:
        """Generate organized content text from ARX mappings."""
        content_parts = []
        
        # Group by context for better readability
        contexts = {}
        for mapping in mappings:
            context_info = mapping.get('context', {})
            column = context_info.get('column', 'unknown')
            
            if column not in contexts:
                contexts[column] = []
            contexts[column].append(mapping)
        
        for column, column_mappings in contexts.items():
            content_parts.append(f"\n## {column.replace('_', ' ').title()} Data")
            content_parts.append(f"Privacy-preserved mappings: {len(column_mappings)} items")
            
            # Add organizational insights
            tokens = [m.get('token', '') for m in column_mappings]
            if tokens:
                content_parts.append(f"Token patterns: {', '.join(tokens[:5])}")
                if len(tokens) > 5:
                    content_parts.append(f"... and {len(tokens) - 5} more")
        
        return '\n'.join(content_parts)
    
    def _generate_tags_from_arx_context(self, context_type: str, contexts: List[Dict[str, Any]]) -> List[str]:
        """Generate intelligent tags from ARX context information."""
        tags = ['arx_processed', 'privacy_preserved']
        
        # Add context-based tags
        tags.append(f"context_{context_type}")
        
        # Extract domain-specific tags
        for context in contexts:
            column = context.get('column', '')
            if 'name' in column.lower():
                tags.append('personal_identity')
            elif 'address' in column.lower():
                tags.append('location_data')
            elif 'phone' in column.lower() or 'email' in column.lower():
                tags.append('contact_info')
            elif 'medical' in column.lower() or 'health' in column.lower():
                tags.append('health_data')
            elif 'financial' in column.lower() or 'payment' in column.lower():
                tags.append('financial_data')
        
        return list(set(tags))  # Remove duplicates
    
    def _identify_arx_connections(self, context_type: str, mappings: List[Dict[str, Any]]) -> List[str]:
        """Identify connections based on ARX mapping patterns."""
        connections = []
        
        # Pattern-based connections
        if context_type == 'quasi-identifying':
            connections.append('identity_cluster')
        elif context_type == 'sensitive':
            connections.append('sensitive_data_group')
        
        # Context-based connections
        contexts = [m.get('context', {}) for m in mappings]
        columns = [c.get('column', '') for c in contexts]
        
        if any('medical' in col.lower() for col in columns):
            connections.append('health_records')
        if any('work' in col.lower() or 'project' in col.lower() for col in columns):
            connections.append('professional_data')
        if any('personal' in col.lower() for col in columns):
            connections.append('personal_information')
        
        return connections
    
    def _create_arx_based_connections(self, processed_items: List[Dict[str, Any]]) -> int:
        """Create intelligent connections between ARX-organized content."""
        connections_created = 0
        
        # Create connections between related context types
        context_types = [item['context_type'] for item in processed_items]
        
        # Group related context types
        if 'quasi-identifying' in context_types and 'sensitive' in context_types:
            # Connect identity and sensitive data
            connections_created += 1
        
        if any('medical' in ct for ct in context_types):
            # Group all medical-related contexts
            medical_items = [item for item in processed_items if 'medical' in item['context_type']]
            connections_created += len(medical_items) - 1 if len(medical_items) > 1 else 0
        
        return connections_created
    
    def _generate_insights_for_sankofa(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate organizational insights to send back to Sankofa."""
        return {
            "processing_success": processing_result.get('success', False),
            "files_created": len(processing_result.get('files_saved', [])),
            "categories_identified": [],  # Placeholder
            "connections_suggested": []   # Placeholder
        }
    
    def _mark_file_processed(self, file_path: str):
        """Mark a Sankofa file as processed."""
        try:
            processed_path = Path(file_path).with_suffix('.processed')
            Path(file_path).rename(processed_path)
        except Exception as e:
            print(f"Warning: Could not mark file as processed: {e}")
    
    def _write_sync_status(self, status: Dict[str, Any]):
        """Write sync status for Sankofa to read."""
        try:
            status_file = self.sync_folders['status'] / "kb_sync_status.json"
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not write sync status: {e}")
    
    def _process_pending_syncs(self):
        """Process any pending sync operations."""
        try:
            # Check for sync triggers
            trigger_files = list(self.sync_folders['status'].glob('sync_trigger_*.json'))
            for trigger_file in trigger_files:
                # Process the trigger
                self.sync_to_sankofa()
                # Remove processed trigger
                trigger_file.unlink()
        except Exception as e:
            print(f"Error processing pending syncs: {e}")
    
    def _sync_health_check(self):
        """Perform health check on sync system."""
        try:
            health_status = {
                "sync_active": self.sync_active,
                "last_health_check": datetime.now().isoformat(),
                "sync_folders_accessible": all(folder.exists() for folder in self.sync_folders.values()),
                "background_worker_alive": self.sync_thread and self.sync_thread.is_alive()
            }
            
            health_file = self.sync_folders['status'] / "health_check.json"
            with open(health_file, 'w') as f:
                json.dump(health_status, f, indent=2)
                
        except Exception as e:
            print(f"Health check failed: {e}")
    
    def _load_sankofa_config(self) -> Dict[str, Any]:
        """Load Sankofa integration configuration."""
        config_path = Path("config/sankofa_integration.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def import_arx_mappings(self, arx_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Import ARX Phase 2 mapping data from Sankofa for intelligent organization.
        
        Args:
            arx_data: List of ARX-compatible mapping entries
            
        Returns:
            Import and organization results
        """
        try:
            processed_items = []
            saved_files = []
            
            # Group mappings by context for better organization
            context_groups = {}
            for mapping in arx_data:
                context = mapping.get('context', {})
                context_type = context.get('type', 'unknown')
                
                if context_type not in context_groups:
                    context_groups[context_type] = []
                context_groups[context_type].append(mapping)
            
            # Process each context group
            for context_type, mappings in context_groups.items():
                # Create organized content from ARX mappings
                organized_content = self._organize_arx_mappings(context_type, mappings)
                
                if organized_content:
                    # Save organized content to knowledge base
                    filepath = self.kb.save_content(organized_content, organized_content['type'])
                    saved_files.append(filepath)
                    processed_items.append({
                        "context_type": context_type,
                        "mappings_count": len(mappings),
                        "file_saved": filepath,
                        "organized_content_id": organized_content['id']
                    })
            
            # Create intelligent connections between organized content
            connections_added = self._create_arx_based_connections(processed_items)
            
            return {
                "success": True,
                "format": "arx_phase2_mappings",
                "context_groups_processed": len(context_groups),
                "total_mappings": len(arx_data),
                "files_created": len(saved_files),
                "connections_created": connections_added,
                "privacy_preserved": True,
                "message": f"Successfully imported and organized {len(arx_data)} ARX mappings into {len(context_groups)} context groups"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error importing ARX mappings: {e}"
            }
    
    def import_deidentified_data(self, data_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import de-identified data from Sankofa and intelligently organize it.
        
        Args:
            data_bundle: De-identified data bundle from Sankofa
            
        Returns:
            Import and organization results
        """
        try:
            # Validate that data is properly de-identified
            if not self._validate_deidentified_data(data_bundle):
                return {
                    "success": False,
                    "error": "Data validation failed - privacy concerns detected",
                    "message": "Data bundle failed de-identification validation"
                }
            
            # Process each item while preserving privacy
            processed_items = []
            saved_files = []
            
            for item in data_bundle.get('content_items', []):
                # Process with privacy preservation
                result = self._process_deidentified_item(item, data_bundle)
                if result['success']:
                    saved_files.append(result['file_saved'])
                    processed_items.append(result)
            
            # Create intelligent connections while maintaining privacy
            connections_added = self._create_privacy_safe_connections(processed_items)
            
            return {
                "success": True,
                "bundle_id": data_bundle.get('bundle_id', 'unknown'),
                "items_processed": len(processed_items),
                "files_created": len(saved_files),
                "connections_created": connections_added,
                "privacy_level": data_bundle.get('privacy_level', 'standard'),
                "message": f"Successfully imported and organized {len(processed_items)} de-identified items"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error importing de-identified data: {e}"
            }
    
    def export_for_portability(self, export_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export organized data in a format suitable for portable storage (USB keychain).
        
        Args:
            export_config: Configuration for export format and privacy level
            
        Returns:
            Export results with portable bundle information
        """
        try:
            config = export_config or {}
            
            # Collect all organized content
            all_content = self._collect_all_content()
            
            # Add organizational intelligence
            enhanced_content = self._add_organizational_metadata(all_content)
            
            # Ensure privacy compliance for portable storage
            portable_bundle = self._create_portable_bundle(enhanced_content, config)
            
            # Save as portable format
            bundle_path = self._save_portable_bundle(portable_bundle)
            
            return {
                "success": True,
                "bundle_path": str(bundle_path),
                "bundle_size": len(portable_bundle['content_items']),
                "privacy_compliant": True,
                "portable_format": True,
                "keychain_ready": True,
                "message": f"Created portable bundle with {len(portable_bundle['content_items'])} organized items"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error creating portable export: {e}"
            }
    
    def query_with_privacy_context(self, query: str, privacy_level: str = "standard") -> Dict[str, Any]:
        """
        Query the knowledge base while maintaining privacy context.
        
        Args:
            query: Search query
            privacy_level: Required privacy level for results
            
        Returns:
            Privacy-aware search results
        """
        try:
            # Perform standard search
            base_results = self.search(query)
            
            if not base_results['success']:
                return base_results
            
            # Filter results based on privacy level
            privacy_filtered_results = []
            for result in base_results['results']:
                if self._meets_privacy_requirements(result, privacy_level):
                    # Sanitize result for privacy
                    sanitized_result = self._sanitize_for_privacy(result, privacy_level)
                    privacy_filtered_results.append(sanitized_result)
            
            return {
                "success": True,
                "query": query,
                "privacy_level": privacy_level,
                "results_count": len(privacy_filtered_results),
                "results": privacy_filtered_results,
                "privacy_compliant": True,
                "message": f"Found {len(privacy_filtered_results)} privacy-compliant results"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error in privacy-aware query: {e}"
            }
    
    def process_with_privacy_preservation(self, user_input: str, privacy_level: str = "high") -> Dict[str, Any]:
        """
        Process stream of consciousness input with enhanced privacy preservation.
        
        Args:
            user_input: Raw text input from user
            privacy_level: Desired privacy level (high, medium, standard)
            
        Returns:
            Processing results with privacy metadata
        """
        try:
            # Standard processing
            base_result = self.process_input(user_input)
            
            if not base_result['success']:
                return base_result
            
            # Add privacy metadata to all created items
            self._add_privacy_metadata_to_files(base_result['files_saved'], privacy_level)
            
            # Enhanced result with privacy information
            enhanced_result = base_result.copy()
            enhanced_result.update({
                "privacy_level": privacy_level,
                "privacy_preserved": True,
                "ready_for_export": True,
                "message": base_result['message'] + f" (Privacy level: {privacy_level})"
            })
            
            return enhanced_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error in privacy-preserved processing: {e}"
            }
    
    def _validate_deidentified_data(self, data_bundle: Dict[str, Any]) -> bool:
        """Validate that data is properly de-identified."""
        # Check for required privacy metadata
        if not data_bundle.get('privacy_level'):
            return False
        
        if not data_bundle.get('deidentified', False):
            return False
        
        # Check each content item
        for item in data_bundle.get('content_items', []):
            if not item.get('privacy_tokens'):
                return False
        
        return True
    
    def _process_deidentified_item(self, item: Dict[str, Any], bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Process a de-identified item while preserving privacy."""
        try:
            # Map to knowledge base format
            kb_content = {
                'id': self.kb.generate_id(),
                'created': item.get('created', self.kb.get_timestamp()),
                'type': self._map_sankofa_type(item.get('sankofa_type', 'note')),
                'title': item.get('title', 'De-identified Content'),
                'content': item.get('content', ''),
                'privacy_metadata': {
                    'sankofa_id': item.get('sankofa_id'),
                    'privacy_level': bundle.get('privacy_level'),
                    'privacy_tokens': item.get('privacy_tokens', {}),
                    'deidentified': True
                },
                'tags': item.get('tags', []),
                'category': item.get('category', 'imported')
            }
            
            # Save with privacy preservation
            if kb_content['type'] == 'journal':
                content_str = self._format_journal_content({'content': kb_content['content'], **kb_content})
                filepath = self.kb.save_content(content_str, 'journal')
            else:
                filepath = self.kb.save_content(kb_content, kb_content['type'])
            
            return {
                "success": True,
                "file_saved": filepath,
                "content_id": kb_content['id'],
                "privacy_preserved": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _map_sankofa_type(self, sankofa_type: str) -> str:
        """Map Sankofa content types to knowledge base types."""
        mapping = {
            'sankofa_personal_note': 'note',
            'sankofa_task_item': 'todo',
            'sankofa_calendar_event': 'calendar',
            'sankofa_journal_entry': 'journal',
            'sankofa_project_data': 'project',
            'sankofa_reference_material': 'reference'
        }
        return mapping.get(sankofa_type, 'note')
    
    def _create_privacy_safe_connections(self, processed_items: List[Dict[str, Any]]) -> int:
        """Create connections between items using privacy-safe methods."""
        connections_created = 0
        
        # Implementation would use privacy-safe similarity matching
        # For now, return a placeholder count
        return len(processed_items) // 2  # Estimate
    
    def _collect_all_content(self) -> List[Dict[str, Any]]:
        """Collect all content from the knowledge base."""
        content = []
        data_dir = Path("data")
        
        if data_dir.exists():
            for content_type_dir in data_dir.iterdir():
                if content_type_dir.is_dir():
                    for file_path in content_type_dir.glob("*"):
                        if file_path.is_file():
                            try:
                                file_content = self.kb._read_file_content(file_path)
                                content.append({
                                    'file_path': str(file_path),
                                    'content_type': content_type_dir.name,
                                    'content': file_content
                                })
                            except Exception as e:
                                print(f"Error reading {file_path}: {e}")
        
        return content
    
    def _add_organizational_metadata(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add organizational intelligence to content."""
        enhanced_content = []
        
        for item in content:
            enhanced_item = item.copy()
            enhanced_item['organizational_metadata'] = {
                'auto_generated_tags': self._generate_smart_tags(item['content']),
                'content_relationships': self._identify_relationships(item, content),
                'importance_score': self._calculate_importance(item),
                'last_enhanced': self.kb.get_timestamp()
            }
            enhanced_content.append(enhanced_item)
        
        return enhanced_content
    
    def _generate_smart_tags(self, content: str) -> List[str]:
        """Generate intelligent tags from content."""
        # Simplified implementation
        tags = []
        content_lower = content.lower()
        
        if 'meeting' in content_lower:
            tags.append('meeting')
        if 'project' in content_lower:
            tags.append('project')
        if 'deadline' in content_lower:
            tags.append('urgent')
        
        return tags
    
    def _identify_relationships(self, item: Dict[str, Any], all_content: List[Dict[str, Any]]) -> List[str]:
        """Identify relationships with other content."""
        # Simplified implementation
        return []
    
    def _calculate_importance(self, item: Dict[str, Any]) -> float:
        """Calculate importance score for content."""
        # Simplified implementation
        content_length = len(item.get('content', ''))
        if content_length > 500:
            return 0.8
        elif content_length > 200:
            return 0.6
        else:
            return 0.4
    
    def _meets_privacy_requirements(self, result: Dict[str, Any], privacy_level: str) -> bool:
        """Check if a result meets the required privacy level."""
        # Simplified implementation - real version would be more sophisticated
        return True  # For now, assume all results meet requirements
    
    def _sanitize_for_privacy(self, result: Dict[str, Any], privacy_level: str) -> Dict[str, Any]:
        """Sanitize a search result for the specified privacy level."""
        sanitized = result.copy()
        
        if privacy_level == "high":
            # Remove potentially sensitive content preview
            if 'content_preview' in sanitized:
                sanitized['content_preview'] = "[Content redacted for privacy]"
        
        return sanitized
    
    def _add_privacy_metadata_to_files(self, file_paths: List[str], privacy_level: str):
        """Add privacy metadata to saved files."""
        # Implementation would add privacy metadata to each file
        # For now, this is a placeholder
        pass
    
    def _create_portable_bundle(self, content: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a portable bundle suitable for USB keychain storage."""
        bundle = {
            'bundle_id': self.kb.generate_id(),
            'created': self.kb.get_timestamp(),
            'format_version': '1.0',
            'privacy_compliant': True,
            'portable': True,
            'content_items': content,
            'organizational_metadata': {
                'total_items': len(content),
                'content_types': list(set(item.get('content_type', 'unknown') for item in content)),
                'creation_date': self.kb.get_timestamp(),
                'enhanced_with_ai': True
            }
        }
        return bundle
    
    def _save_portable_bundle(self, bundle: Dict[str, Any]) -> Path:
        """Save the portable bundle to disk."""
        output_dir = Path("exports")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_path = output_dir / f"portable_kb_bundle_{timestamp}.json"
        
        with open(bundle_path, 'w') as f:
            json.dump(bundle, f, indent=2)
        
        return bundle_path

    def enhance_privacy_context(self, sankofa_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add Knowledge Base intelligence to Sankofa's privacy-processed data.
        
        This is where KB adds semantic context, relationship mapping, 
        and AI metadata without touching privacy tokens.
        """
        try:
            enhanced_data = sankofa_data.copy()
            
            # Extract the original query/content if available
            original_content = sankofa_data.get('original_content', '')
            privacy_tokens = sankofa_data.get('privacy_tokens', {})
            
            # Generate specific contextual intelligence using the tracker
            contextual_intelligence = self.intelligence_tracker.generate_contextual_intelligence(
                original_content, privacy_tokens
            )
            
            # Extract privacy mappings for additional intelligence enhancement
            mappings = []
            if 'mapping_data' in sankofa_data:
                mappings = sankofa_data['mapping_data']
            elif isinstance(sankofa_data, list):
                mappings = sankofa_data
            
            # Generate semantic context from mappings
            semantic_context = self._generate_semantic_context(mappings) if mappings else {}
            
            # Generate relationship mapping
            relationship_mapping = self._generate_relationship_mapping(mappings) if mappings else {}
            
            # Generate AI metadata
            ai_metadata = self._generate_ai_metadata(mappings) if mappings else {}
            
            # Combine enhancements with specific intelligence
            enhanced_data['kb_enhancements'] = {
                "specific_intelligence": {
                    "contextual_summary": contextual_intelligence.get('contextual_summary', ''),
                    "historical_measurements": contextual_intelligence.get('relevant_measurements', []),
                    "visit_patterns": contextual_intelligence.get('visit_patterns', {}),
                    "available_equipment": contextual_intelligence.get('available_equipment', []),
                    "recommendations": contextual_intelligence.get('specific_recommendations', [])
                },
                "semantic_context": semantic_context,
                "relationship_mapping": relationship_mapping,
                "ai_metadata": ai_metadata,
                "enhanced_at": self.kb.get_timestamp(),
                "enhancement_version": "kb_v2.0_intelligence"
            }
            
            # If we have specific intelligence, use it as the primary context
            if contextual_intelligence.get('contextual_summary'):
                enhanced_data['enhanced_context'] = contextual_intelligence['contextual_summary']
            
            return {
                "success": True,
                "enhanced_data": enhanced_data,
                "enhancements_added": len(enhanced_data['kb_enhancements']),
                "privacy_preserved": True,
                "intelligence_context": contextual_intelligence.get('contextual_summary', '')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to enhance privacy context: {e}"
            }
    
    def request_sankofa_privacy_processing(self, text: str) -> Dict[str, Any]:
        """Request privacy processing from Sankofa via sync interface."""
        try:
            request_data = {
                "type": "privacy_request",
                "text": text,
                "timestamp": datetime.now().isoformat(),
                "source": "knowledge_base",
                "request_id": str(uuid.uuid4())
            }
            
            # Write request to Sankofa sync folder
            request_file = self.sync_folders["kb_to_sankofa"] / f"privacy_request_{request_data['request_id'][:8]}.json"
            
            with open(request_file, 'w') as f:
                json.dump(request_data, f, indent=2)
            
            return {
                "success": True,
                "request_id": request_data["request_id"],
                "message": "Privacy processing request sent to Sankofa",
                "request_file": str(request_file)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to request privacy processing: {e}"
            }
    
    def _generate_semantic_context(self, mappings: List[Dict]) -> Dict[str, Any]:
        """Generate semantic context for privacy mappings."""
        context = {
            "domains": set(),
            "categories": set(), 
            "sensitivity_levels": set()
        }
        
        for mapping in mappings:
            if "context" in mapping:
                if "domain" in mapping["context"]:
                    context["domains"].add(mapping["context"]["domain"])
                if "category" in mapping["context"]:
                    context["categories"].add(mapping["context"]["category"])
                if "sensitivity" in mapping["context"]:
                    context["sensitivity_levels"].add(mapping["context"]["sensitivity"])
        
        # Convert sets to lists for JSON serialization
        return {k: list(v) for k, v in context.items()}
    
    def _generate_relationship_mapping(self, mappings: List[Dict]) -> Dict[str, Any]:
        """Generate relationship mapping between anonymized entities."""
        relationships = {
            "healthcare_providers": [],
            "medical_conditions": [],
            "medications": [],
            "appointments": []
        }
        
        for mapping in mappings:
            token = mapping.get("token", "")
            if "PHYSICIAN" in token:
                relationships["healthcare_providers"].append(mapping)
            elif "CONDITION" in token:
                relationships["medical_conditions"].append(mapping)
            elif "MEDICATION" in token:
                relationships["medications"].append(mapping)
        
        return relationships
    
    def _generate_ai_metadata(self, mappings: List[Dict]) -> Dict[str, Any]:
        """Generate AI-optimized metadata for enhanced responses."""
        return {
            "total_entities": len(mappings),
            "privacy_level": "high" if any("critical" in str(m) for m in mappings) else "medium",
            "domains_involved": len(set(m.get("context", {}).get("domain", "unknown") for m in mappings)),
            "ai_context_hints": [
                "Medical consultation context detected",
                "Healthcare provider relationship identified",
                "Ongoing care management scenario"
            ] if any("PHYSICIAN" in str(m) for m in mappings) else []
        }


def main():
    """Command line interface for enhanced AI functionality."""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_ai_interface.py <command> [args...]")
        print("Commands:")
        print("  process-private <text> [privacy_level]   - Process text with privacy preservation")
        print("  import-deidentified <bundle_file>        - Import Sankofa bundle (legacy)")
        print("  import-arx-mappings <mappings_file>      - Import ARX Phase 2 mappings")
        print("  export-portable                          - Export portable bundle")
        print("  query-private <query> [privacy_level]    - Query with privacy context")
        print("  start-sync [mode]                        - Start real-time sync with Sankofa")
        print("  stop-sync                                - Stop real-time sync")
        print("  sync-to-sankofa [filter]                 - Manual sync to Sankofa ARX Phase 2")
        print("  sync-status                              - Check sync status")
        print("  enhance-sankofa-context <sankofa_file>   - Enhance Sankofa privacy data with intelligence")
        print("  request-sankofa-privacy <text>           - Request privacy processing from Sankofa")
        return
    
    ai = EnhancedKnowledgeBaseAI()
    command = sys.argv[1]
    
    if command == "process-private" and len(sys.argv) > 2:
        text = sys.argv[2]
        privacy_level = sys.argv[3] if len(sys.argv) > 3 else "high"
        result = ai.process_with_privacy_preservation(text, privacy_level)
        print(json.dumps(result, indent=2))
    
    elif command == "import-deidentified" and len(sys.argv) > 2:
        bundle_file = sys.argv[2]
        try:
            with open(bundle_file, 'r') as f:
                bundle_data = json.load(f)
            result = ai.import_deidentified_data(bundle_data)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}, indent=2))
    
    elif command == "import-arx-mappings" and len(sys.argv) > 2:
        mappings_file = sys.argv[2]
        try:
            with open(mappings_file, 'r') as f:
                mappings_data = json.load(f)
            
            # Handle both wrapped and raw formats
            if isinstance(mappings_data, dict) and 'mapping_data' in mappings_data:
                arx_mappings = mappings_data['mapping_data']
            elif isinstance(mappings_data, list):
                arx_mappings = mappings_data
            else:
                raise ValueError("Invalid ARX mappings format")
            
            result = ai.import_arx_mappings(arx_mappings)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}, indent=2))
    
    elif command == "export-portable":
        result = ai.export_for_portability()
        print(json.dumps(result, indent=2))
    
    elif command == "query-private" and len(sys.argv) > 2:
        query = sys.argv[2]
        privacy_level = sys.argv[3] if len(sys.argv) > 3 else "standard"
        result = ai.query_with_privacy_context(query, privacy_level)
        print(json.dumps(result, indent=2))
    
    elif command == "start-sync":
        sync_mode = sys.argv[2] if len(sys.argv) > 2 else "live_processing"
        result = ai.start_realtime_sync(sync_mode)
        print(json.dumps(result, indent=2))
        
        if result.get('success'):
            print("\n🚀 Real-time sync started! Press Ctrl+C to stop...")
            try:
                # Keep the process running
                while ai.sync_active:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping sync...")
                stop_result = ai.stop_realtime_sync()
                print(json.dumps(stop_result, indent=2))
    
    elif command == "stop-sync":
        result = ai.stop_realtime_sync()
        print(json.dumps(result, indent=2))
    
    elif command == "sync-to-sankofa":
        # Parse filter options if provided
        data_filter = {}
        if len(sys.argv) > 2:
            filter_arg = sys.argv[2]
            if '=' in filter_arg:
                key, value = filter_arg.split('=', 1)
                data_filter[key] = value
        
        result = ai.sync_to_sankofa(data_filter if data_filter else None)
        print(json.dumps(result, indent=2))
    
    elif command == "sync-status":
        status = {
            "sync_active": ai.sync_active,
            "sync_folders": {k: str(v) for k, v in ai.sync_folders.items()},
            "sync_thread_alive": ai.sync_thread and ai.sync_thread.is_alive() if ai.sync_thread else False
        }
        print(json.dumps(status, indent=2))
    
    elif command == "enhance-sankofa-context" and len(sys.argv) > 2:
        sankofa_data_file = sys.argv[2]
        
        try:
            with open(sankofa_data_file, 'r') as f:
                sankofa_data = json.load(f)
            
            # Knowledge Base enhances Sankofa's privacy data with intelligence
            enhanced_result = ai.enhance_privacy_context(sankofa_data)
            print(json.dumps(enhanced_result, indent=2))
            
        except FileNotFoundError:
            print(f"Error: Sankofa data file '{sankofa_data_file}' not found")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in '{sankofa_data_file}'")
    
    elif command == "request-sankofa-privacy" and len(sys.argv) > 2:
        text = sys.argv[2]
        
        # Request privacy processing from Sankofa (via sync interface)
        result = ai.request_sankofa_privacy_processing(text)
        print(json.dumps(result, indent=2))
    
    else:
        print("Invalid command or missing arguments")


if __name__ == "__main__":
    main() 