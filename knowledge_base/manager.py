#!/usr/bin/env python3
"""
Knowledge Base Manager
Main class for intelligent content processing and organization with enhanced privacy.
"""

import os
import json
import yaml
import uuid
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import hashlib

from knowledge_base.content_types import Note, Todo, CalendarEvent, RelationshipType
from knowledge_base.utils.config import Config
from knowledge_base.utils.helpers import (
    generate_id, get_timestamp, KnowledgeBaseError, ContentProcessingError,
    StorageError, ConfigurationError, PrivacyError, ValidationError, NotFoundError
)

# Enhanced Privacy Imports (Milestone 3)
from knowledge_base.privacy import (
    # Legacy privacy components
    PrivacyEngine, PrivacySessionManager, DeidentificationResult,
    # End-to-End Encryption
    KeyManager, ContentEncryptionManager, EncryptedStorageAdapter,
    # Granular Privacy Controls  
    PrivacyLevel, PrivacyControlManager, create_default_content_profiles,
    # Privacy Audit Logging
    PrivacyOperation, PrivacyImpact, PrivacyAuditLogger, ComplianceReporter,
    # Differential Privacy
    PrivacyPreservingAnalytics, BudgetExhaustedException,
    # Privacy Certification Framework
    ComplianceStandard, ComplianceChecker, PrivacyImpactAssessmentTool, CertificationReporter
)

from knowledge_base.core.content_manager import ContentManager
from knowledge_base.core.relationship_manager import RelationshipManager
from knowledge_base.core.hierarchy_manager import HierarchyManager
from knowledge_base.core.semantic_search import SemanticSearch
from knowledge_base.core.recommendation_engine import RecommendationEngine
from knowledge_base.core.knowledge_graph import KnowledgeGraph

logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    """
    Main class for managing the knowledge base system with enhanced privacy features.
    
    This class provides functionality for:
    1. Processing and organizing content with privacy protection
    2. Extracting actionable items (todos, events) with encryption
    3. Generating tags and categories automatically
    4. Searching across content with privacy controls
    5. Saving and retrieving content with audit logging
    6. Privacy-preserving analytics and compliance certification
    """
    
    def __init__(self, base_path: str = ".", privacy_storage_dir: str = None, 
                 enable_encryption: bool = True, enable_audit_logging: bool = True):
        """
        Initialize the knowledge base manager with enhanced privacy.
        
        Args:
            base_path: Path to the knowledge base directory
            privacy_storage_dir: Path for storing privacy session data
            enable_encryption: Whether to enable encryption features
            enable_audit_logging: Whether to enable audit logging
        """
        try:
            self.base_path = Path(base_path)
            self.config = Config(self.base_path).load_config()
            self.conventions = Config(self.base_path).load_conventions()
            
            # Initialize core managers first
            self.relationship_manager = RelationshipManager(self.base_path)
            self.hierarchy_manager = HierarchyManager(self.base_path, relationship_manager=self.relationship_manager)
            self.content_manager = ContentManager(self.base_path, relationship_manager=self.relationship_manager, hierarchy_manager=self.hierarchy_manager)
            self.semantic_search_engine = SemanticSearch(self.base_path, content_manager=self.content_manager)
            self.recommendation_engine = RecommendationEngine(self.base_path, content_manager=self.content_manager, semantic_search=self.semantic_search_engine, relationship_manager=self.relationship_manager)
            self.knowledge_graph = KnowledgeGraph(self.base_path, content_manager=self.content_manager, relationship_manager=self.relationship_manager, hierarchy_manager=self.hierarchy_manager)
            
            # Initialize legacy privacy components
            self.privacy_engine = PrivacyEngine(self.config.get("privacy", {}))
            self.session_manager = PrivacySessionManager(privacy_storage_dir)
            
            # Initialize Milestone 3 Privacy Enhancements
            self._initialize_enhanced_privacy(enable_encryption, enable_audit_logging, privacy_storage_dir)
            
            # Create default privacy session
            if not hasattr(self, 'privacy_session_id') or not self.privacy_session_id:
                self.privacy_session_id = self.session_manager.create_session("balanced")
            
        except FileNotFoundError as e:
            logger.error(f"Configuration file not found: {e}")
            raise ConfigurationError(f"Failed to load configuration: {e}")
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML configuration: {e}")
            raise ConfigurationError(f"Invalid configuration format: {e}")
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise KnowledgeBaseError(f"Failed to initialize knowledge base manager: {e}")
    
    def _initialize_enhanced_privacy(self, enable_encryption: bool, 
                                   enable_audit_logging: bool, 
                                   privacy_storage_dir: str = None) -> None:
        """Initialize Milestone 3 privacy enhancements."""
        try:
            # Set up privacy storage directory
            privacy_dir = privacy_storage_dir or (Path.home() / ".kb_privacy")
            
            # 1. End-to-End Encryption
            if enable_encryption:
                self.key_manager = KeyManager(str(privacy_dir / "keys"))
                self.encryption_manager = ContentEncryptionManager(self.key_manager)
                self.encrypted_storage = EncryptedStorageAdapter(
                    self.encryption_manager, 
                    str(self.base_path / "data")
                )
            else:
                self.key_manager = None
                self.encryption_manager = None
                self.encrypted_storage = None
            
            # 2. Granular Privacy Controls
            self.privacy_control_manager = PrivacyControlManager(str(privacy_dir))
            
            # Create default profiles for different content types
            default_profiles = create_default_content_profiles()
            for content_type, profile in default_profiles.items():
                self.privacy_control_manager.rule_engine.add_profile(profile)
            
            # 3. Privacy Audit Logging
            if enable_audit_logging:
                self.audit_logger = PrivacyAuditLogger(str(privacy_dir / "audit_logs"))
                self.compliance_reporter = ComplianceReporter(self.audit_logger)
            else:
                self.audit_logger = None
                self.compliance_reporter = None
            
            # 4. Differential Privacy Analytics
            self.privacy_analytics = PrivacyPreservingAnalytics()
            
            # 5. Privacy Certification Framework
            self.compliance_checker = ComplianceChecker(str(privacy_dir / "compliance"))
            self.pia_tool = PrivacyImpactAssessmentTool(str(privacy_dir / "pia"))
            self.certification_reporter = CertificationReporter(
                self.compliance_checker, 
                self.pia_tool
            )
            
            logger.info("Enhanced privacy features initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing enhanced privacy: {e}")
            # Set components to None if initialization fails
            self.key_manager = None
            self.encryption_manager = None
            self.encrypted_storage = None
            self.privacy_control_manager = None
            self.audit_logger = None
            self.compliance_reporter = None
            self.privacy_analytics = None
            self.compliance_checker = None
            self.pia_tool = None
            self.certification_reporter = None
            
            logger.warning("Enhanced privacy features disabled due to initialization error")
    
    # Enhanced Privacy Methods for Milestone 3
    
    def encrypt_content(self, content: Union[str, Dict[str, Any]], 
                       searchable_fields: List[str] = None) -> Dict[str, Any]:
        """
        Encrypt content while preserving searchable fields.
        
        Args:
            content: Content to encrypt
            searchable_fields: Fields to keep searchable
            
        Returns:
            Encrypted content metadata
        """
        if not self.encryption_manager:
            raise PrivacyError("Encryption not enabled")
            
        try:
            if isinstance(content, dict):
                # Handle structured content
                if searchable_fields:
                    encrypted_data = self.encryption_manager.encrypt_searchable_content(
                        content, searchable_fields
                    )
                else:
                    # Encrypt entire content
                    encrypted_result = self.encryption_manager.encrypt_content(
                        json.dumps(content).encode('utf-8')
                    )
                    encrypted_data = {
                        "_encrypted": encrypted_result.to_dict(),
                        "_metadata": {
                            "has_encrypted_data": True,
                            "encryption_type": "full",
                            "created_at": datetime.now().isoformat()
                        }
                    }
            else:
                # Handle string content
                encrypted_result = self.encryption_manager.encrypt_content(content)
                encrypted_data = {
                    "_encrypted": encrypted_result.to_dict(),
                    "_metadata": {
                        "has_encrypted_data": True,
                        "encryption_type": "full",
                        "created_at": datetime.now().isoformat()
                    }
                }
            
            # Log encryption operation
            if self.audit_logger:
                self.audit_logger.log_operation(
                    operation=PrivacyOperation.ENCRYPTION,
                    impact_level=PrivacyImpact.HIGH,
                    details={
                        "content_type": type(content).__name__,
                        "encryption_type": encrypted_data["_metadata"]["encryption_type"],
                        "searchable_fields": searchable_fields or []
                    }
                )
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Error encrypting content: {e}")
            raise PrivacyError(f"Encryption failed: {e}")
    
    def decrypt_content(self, encrypted_data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        Decrypt encrypted content.
        
        Args:
            encrypted_data: Encrypted content data
            
        Returns:
            Decrypted content
        """
        if not self.encryption_manager:
            raise PrivacyError("Encryption not enabled")
            
        try:
            if "_encrypted" in encrypted_data:
                # Handle fully encrypted content
                from knowledge_base.privacy.encryption import EncryptionResult
                encrypted_result = EncryptionResult.from_dict(encrypted_data["_encrypted"])
                decrypted_bytes = self.encryption_manager.decrypt_content(encrypted_result)
                
                # Try to parse as JSON first
                try:
                    return json.loads(decrypted_bytes.decode('utf-8'))
                except json.JSONDecodeError:
                    return decrypted_bytes.decode('utf-8')
            else:
                # Handle searchable encrypted content
                return self.encryption_manager.decrypt_searchable_content(encrypted_data)
            
        except Exception as e:
            logger.error(f"Error decrypting content: {e}")
            raise PrivacyError(f"Decryption failed: {e}")
    
    def set_content_privacy(self, content_id: str, privacy_level: PrivacyLevel,
                          inherit_from: str = None, override_parent: bool = False) -> Dict[str, Any]:
        """
        Set privacy settings for content.
        
        Args:
            content_id: Content ID
            privacy_level: Privacy level to set
            inherit_from: Parent content ID for inheritance
            override_parent: Whether to override parent settings
            
        Returns:
            Privacy settings
        """
        if not self.privacy_control_manager:
            raise PrivacyError("Privacy controls not enabled")
            
        try:
            settings = self.privacy_control_manager.set_content_privacy(
                content_id=content_id,
                privacy_level=privacy_level,
                inherit_from=inherit_from,
                override_parent=override_parent
            )
            
            # Log privacy settings change
            if self.audit_logger:
                self.audit_logger.log_operation(
                    operation=PrivacyOperation.SETTINGS,
                    impact_level=PrivacyImpact.MEDIUM,
                    content_id=content_id,
                    details={
                        "privacy_level": privacy_level.value,
                        "inherit_from": inherit_from,
                        "override_parent": override_parent
                    }
                )
            
            return settings.to_dict()
            
        except Exception as e:
            logger.error(f"Error setting content privacy: {e}")
            raise PrivacyError(f"Failed to set privacy: {e}")
    
    def get_private_analytics(self, query_type: str, data: Any, 
                            epsilon: float = 0.1) -> Dict[str, Any]:
        """
        Get privacy-preserving analytics.
        
        Args:
            query_type: Type of analytics query
            data: Data to analyze
            epsilon: Privacy parameter
            
        Returns:
            Privacy-preserving analytics results
        """
        if not self.privacy_analytics:
            raise PrivacyError("Privacy analytics not enabled")
            
        try:
            # Create analytics budget
            budget_id = self.privacy_analytics.create_analytics_budget(
                total_epsilon=1.0,
                purpose=f"analytics_{query_type}"
            )
            
            # Perform privacy-preserving query
            if query_type == "count":
                result = self.privacy_analytics.count_with_privacy(
                    count=data,
                    budget_id=budget_id,
                    epsilon=epsilon
                )
            elif query_type == "stats":
                result = self.privacy_analytics.get_private_stats(
                    values=data,
                    budget_id=budget_id,
                    epsilon=epsilon
                )
            elif query_type == "histogram":
                result = self.privacy_analytics.get_private_histogram(
                    data=data,
                    budget_id=budget_id,
                    epsilon=epsilon
                )
            else:
                raise ValueError(f"Unsupported query type: {query_type}")
            
            # Log analytics operation
            if self.audit_logger:
                self.audit_logger.log_operation(
                    operation=PrivacyOperation.ANALYTICS,
                    impact_level=PrivacyImpact.LOW,
                    details={
                        "query_type": query_type,
                        "epsilon": epsilon,
                        "budget_id": budget_id
                    }
                )
            
            return {
                "result": result,
                "budget_id": budget_id,
                "epsilon_used": epsilon,
                "privacy_preserved": True
            }
            
        except BudgetExhaustedException as e:
            logger.error(f"Privacy budget exhausted: {e}")
            raise PrivacyError(f"Privacy budget exhausted: {e}")
        except Exception as e:
            logger.error(f"Error in private analytics: {e}")
            raise PrivacyError(f"Analytics failed: {e}")
    
    def assess_compliance(self, standard: ComplianceStandard, 
                         evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Assess compliance against a privacy standard.
        
        Args:
            standard: Compliance standard to assess
            evidence: Evidence for compliance
            
        Returns:
            Compliance assessment results
        """
        if not self.compliance_checker:
            raise PrivacyError("Compliance checker not enabled")
            
        try:
            # Assess compliance
            assessments = self.compliance_checker.assess_compliance(standard, evidence)
            
            # Generate gap analysis
            gap_analysis = self.compliance_checker.generate_gap_analysis(assessments)
            
            # Log compliance assessment
            if self.audit_logger:
                self.audit_logger.log_operation(
                    operation=PrivacyOperation.COMPLIANCE,
                    impact_level=PrivacyImpact.HIGH,
                    details={
                        "standard": standard.value,
                        "compliance_score": gap_analysis["summary"]["compliance_score"],
                        "total_requirements": gap_analysis["summary"]["total_requirements"]
                    }
                )
            
            return {
                "standard": standard.value,
                "assessments": {req_id: assessment.to_dict() 
                              for req_id, assessment in assessments.items()},
                "gap_analysis": gap_analysis,
                "assessed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing compliance: {e}")
            raise PrivacyError(f"Compliance assessment failed: {e}")
    
    def create_privacy_impact_assessment(self, title: str, scope: str,
                                       data_categories: List[str],
                                       processing_purposes: List[str],
                                       legal_basis: List[str]) -> Dict[str, Any]:
        """
        Create a Privacy Impact Assessment.
        
        Args:
            title: PIA title
            scope: Assessment scope
            data_categories: Data categories involved
            processing_purposes: Purposes for processing
            legal_basis: Legal basis for processing
            
        Returns:
            Created PIA
        """
        if not self.pia_tool:
            raise PrivacyError("PIA tool not enabled")
            
        try:
            pia = self.pia_tool.create_pia(
                title=title,
                scope=scope,
                data_categories=data_categories,
                processing_purposes=processing_purposes,
                legal_basis=legal_basis
            )
            
            # Log PIA creation
            if self.audit_logger:
                self.audit_logger.log_operation(
                    operation=PrivacyOperation.COMPLIANCE,
                    impact_level=PrivacyImpact.HIGH,
                    details={
                        "action": "pia_created",
                        "pia_id": pia.pia_id,
                        "risk_level": pia.risk_assessment["risk_level"]
                    }
                )
            
            return pia.to_dict()
            
        except Exception as e:
            logger.error(f"Error creating PIA: {e}")
            raise PrivacyError(f"PIA creation failed: {e}")
    
    def generate_certification_report(self, standard: ComplianceStandard,
                                    evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive certification report.
        
        Args:
            standard: Compliance standard
            evidence: Evidence for assessment
            
        Returns:
            Certification report
        """
        if not self.certification_reporter:
            raise PrivacyError("Certification reporter not enabled")
            
        try:
            report = self.certification_reporter.generate_certification_report(
                standard=standard,
                evidence=evidence
            )
            
            # Log certification report generation
            if self.audit_logger:
                self.audit_logger.log_operation(
                    operation=PrivacyOperation.COMPLIANCE,
                    impact_level=PrivacyImpact.HIGH,
                    details={
                        "action": "certification_report_generated",
                        "standard": standard.value,
                        "certification_status": report["certification_status"]["status"]
                    }
                )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating certification report: {e}")
            raise PrivacyError(f"Certification report generation failed: {e}")
    
    def get_audit_logs(self, start_time: datetime = None, end_time: datetime = None,
                      operations: List[PrivacyOperation] = None) -> List[Dict[str, Any]]:
        """
        Get privacy audit logs.
        
        Args:
            start_time: Start time for logs
            end_time: End time for logs  
            operations: Operations to filter by
            
        Returns:
            List of audit log entries
        """
        if not self.audit_logger:
            raise PrivacyError("Audit logging not enabled")
            
        try:
            entries = self.audit_logger.query_logs(
                start_time=start_time,
                end_time=end_time,
                operations=operations
            )
            
            return [entry.to_dict() for entry in entries]
            
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            raise PrivacyError(f"Audit log retrieval failed: {e}")
    
    # Enhanced versions of existing methods with privacy integration
    
    def save_content_with_privacy(self, content_data: Dict[str, Any], content_type: str,
                                privacy_level: PrivacyLevel = PrivacyLevel.PROTECTED,
                                encrypt: bool = False) -> str:
        """
        Save content with privacy controls and optional encryption.
        
        Args:
            content_data: Content to save
            content_type: Type of content
            privacy_level: Privacy level for the content
            encrypt: Whether to encrypt the content
            
        Returns:
            Path to saved content
        """
        try:
            # Generate content ID
            content_id = content_data.get('id', generate_id())
            
            # Apply privacy controls
            if self.privacy_control_manager:
                # Evaluate and apply privacy settings
                privacy_controlled_content = self.privacy_control_manager.apply_privacy_controls(
                    content_id, content_data
                )
            else:
                privacy_controlled_content = content_data
            
            # Set privacy level
            if self.privacy_control_manager:
                self.set_content_privacy(content_id, privacy_level)
            
            # Encrypt if required or requested
            if encrypt and self.encryption_manager:
                # Determine searchable fields based on content type
                searchable_fields = []
                if content_type == "note":
                    searchable_fields = ["title", "tags", "category"]
                elif content_type == "todo":
                    searchable_fields = ["title", "status", "priority"]
                elif content_type == "calendar":
                    searchable_fields = ["title", "category"]
                
                encrypted_content = self.encrypt_content(
                    privacy_controlled_content, 
                    searchable_fields
                )
                content_to_save = encrypted_content
            else:
                content_to_save = privacy_controlled_content
            
            # Save content using original method
            filepath = self.save_content(content_to_save, content_type)
            
            # Log the operation
            if self.audit_logger:
                self.audit_logger.log_operation(
                    operation=PrivacyOperation.MODIFICATION,
                    impact_level=PrivacyImpact.MEDIUM,
                    content_id=content_id,
                    details={
                        "action": "content_saved",
                        "content_type": content_type,
                        "privacy_level": privacy_level.value,
                        "encrypted": encrypt,
                        "filepath": filepath
                    }
                )
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving content with privacy: {e}")
            raise PrivacyError(f"Failed to save content with privacy: {e}")
    
    def process_stream_of_consciousness(self, content: str) -> Dict[str, Any]:
        """
        Process stream of consciousness input and organize intelligently.
        
        This is the main entry point for adding content to the knowledge base.
        The method will extract todos, events, tags, and other useful information.
        
        Args:
            content: Raw text input from user
            
        Returns:
            Dictionary containing organized content and metadata
        """
        try:
            result = {
                "original_content": content,
                "processed_items": [],
                "extracted_info": {
                    "todos": [],
                    "calendar_events": [],
                    "notes": [],
                    "tags": [],
                    "categories": [],
                    "cross_refs": []
                }
            }
            
            # Extract actionable items (todos)
            todos = self._extract_todos(content)
            result["extracted_info"]["todos"] = todos
            
            # Extract dates and events
            events = self._extract_calendar_events(content)
            result["extracted_info"]["calendar_events"] = events
            
            # Extract key topics and generate tags
            tags = self._extract_tags(content)
            result["extracted_info"]["tags"] = tags
            
            # Categorize content
            category = self._categorize_content(content, tags)
            result["extracted_info"]["categories"] = [category]
            
            # Create main note if content doesn't fit other categories
            if not todos and not events:
                note = self._create_note_from_content(content, tags, category)
                result["extracted_info"]["notes"] = [note]
            
            # Automatically save extracted information
            self._save_extracted_info(result["extracted_info"])
            
            return result
            
        except ContentProcessingError as e:
            # Specific content processing error, already logged
            raise
        except Exception as e:
            logger.error(f"Error processing content: {e}")
            raise ContentProcessingError(f"Failed to process content: {e}")
    
    def _extract_todos(self, content: str) -> List[Dict[str, Any]]:
        """Extract actionable items from content."""
        try:
            todos = []
            
            # Keywords that indicate actionable items
            action_patterns = [
                r"(?:need to|must|should|have to|remember to|todo:?)\s+(.+?)(?:\.|$|\n)",
                r"(?:^|\n)-\s*(?:(?:\[ \])|(?:\[\s\]))\s*(.+?)(?:\n|$)",
                r"(?:action|task|do):?\s*(.+?)(?:\.|$|\n)"
            ]
            
            for pattern in action_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else (match[1] if len(match) > 1 else "")
                    
                    todo = Todo(
                        title=match.strip(),
                        description="",
                        priority=self._detect_priority(match),
                        status="active",
                        category="task",
                        tags=self._extract_tags(match),
                        due_date=self._extract_due_date(match),
                        context=self._extract_context(match)
                    ).to_dict()
                    
                    todos.append(todo)
            
            return todos
        except Exception as e:
            logger.error(f"Error extracting todos from content: {e}")
            raise ContentProcessingError(f"Failed to extract todos: {e}")
    
    def _extract_calendar_events(self, content: str) -> List[Dict[str, Any]]:
        """Extract calendar events from content."""
        try:
            events = []
            
            # Date/time patterns
            date_patterns = [
                r"(?:meeting|call|appointment|event)\s+(?:on|at)?\s*([^\.]+?)(?:\.|$|\n)",
                r"([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?\s*(?:at\s+\d{1,2}:\d{2})?)",
                r"((?:today|tomorrow|next week|this week)\s+(?:at\s+)?\d{1,2}:\d{2})"
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    event = CalendarEvent(
                        title=match.strip(),
                        description="",
                        datetime=self._parse_datetime(match),
                        duration="60min",
                        category="meeting",
                        tags=["calendar"]
                    ).to_dict()
                    
                    events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Error extracting calendar events: {e}")
            raise ContentProcessingError(f"Failed to extract calendar events: {e}")
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract and generate relevant tags from content."""
        try:
            tags = []
            
            # Explicit hashtags
            hashtag_pattern = r"#(\w+)"
            hashtags = re.findall(hashtag_pattern, content)
            tags.extend(hashtags)
            
            # Context tags
            if any(word in content.lower() for word in ["work", "office", "meeting", "project"]):
                tags.append("@work")
            if any(word in content.lower() for word in ["home", "personal", "family"]):
                tags.append("@personal")
            
            # Topic-based tags
            topic_keywords = {
                "learning": ["learn", "study", "research", "read", "book", "article"],
                "health": ["exercise", "workout", "doctor", "health", "fitness"],
                "finance": ["money", "budget", "expense", "income", "investment"],
                "creative": ["write", "art", "music", "design", "creative", "idea"]
            }
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in content.lower() for keyword in keywords):
                    tags.append(f"#{topic}")
            
            return list(set(tags))  # Remove duplicates
        except Exception as e:
            logger.warning(f"Error extracting tags: {e}")
            return []  # Return empty tags rather than fail the entire process
    
    def _categorize_content(self, content: str, tags: List[str]) -> str:
        """Categorize content based on patterns and tags."""
        try:
            categories = self.config.get("organization", {}).get("auto_categorization", {})
            
            content_lower = content.lower()
            
            for category, keywords in categories.items():
                if any(keyword in content_lower for keyword in keywords):
                    return category
            
            # Default categorization
            if "@work" in tags:
                return "work"
            elif any(tag.startswith("#") for tag in tags):
                return "learning"
            else:
                return "personal"
        except Exception as e:
            logger.warning(f"Error categorizing content: {e}")
            return "personal"  # Default if categorization fails
    
    def _detect_priority(self, text: str) -> str:
        """Detect priority level from text."""
        try:
            urgent_keywords = self.config.get("organization", {}).get("priority_detection", {}).get("urgent_keywords", [])
            
            text_lower = text.lower()
            if any(keyword in text_lower for keyword in urgent_keywords):
                return "high"
            elif any(word in text_lower for word in ["today", "asap"]):
                return "high"
            elif any(word in text_lower for word in ["important", "priority"]):
                return "medium"
            else:
                return "low"
        except Exception as e:
            logger.warning(f"Error detecting priority: {e}")
            return "medium"  # Default to medium priority if detection fails
    
    def _extract_due_date(self, text: str) -> Optional[str]:
        """Extract due date from text."""
        try:
            # Simple date extraction - can be enhanced
            today_keywords = ["today", "asap"]
            tomorrow_keywords = ["tomorrow"]
            
            text_lower = text.lower()
            if any(keyword in text_lower for keyword in today_keywords):
                return datetime.now(timezone.utc).date().isoformat()
            elif any(keyword in text_lower for keyword in tomorrow_keywords):
                tomorrow = datetime.now(timezone.utc).date().replace(day=datetime.now().day + 1)
                return tomorrow.isoformat()
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting due date: {e}")
            return None
    
    def _extract_context(self, text: str) -> str:
        """Extract context tags from text."""
        try:
            if any(word in text.lower() for word in ["home", "house"]):
                return "@home"
            elif any(word in text.lower() for word in ["work", "office"]):
                return "@work"
            elif any(word in text.lower() for word in ["urgent", "important"]):
                return "@urgent"
            else:
                return "@personal"
        except Exception as e:
            logger.warning(f"Error extracting context: {e}")
            return "@personal"
    
    def _parse_datetime(self, text: str) -> str:
        """Parse datetime from text (simplified)."""
        try:
            # This is a simplified version - real implementation would be more robust
            return get_timestamp()
        except Exception as e:
            logger.warning(f"Error parsing datetime: {e}")
            return get_timestamp()
    
    def _create_note_from_content(self, content: str, tags: List[str], category: str) -> Dict[str, Any]:
        """Create a note entry from general content."""
        try:
            return Note(
                title=self._generate_title_from_content(content),
                content=content,
                category=category,
                tags=tags
            ).to_dict()
        except Exception as e:
            logger.error(f"Error creating note from content: {e}")
            # Create a minimal note with error information
            return Note(
                title="Note Creation Error",
                content=content,
                category="error",
                tags=["error"]
            ).to_dict()
    
    def _generate_title_from_content(self, content: str) -> str:
        """Generate a descriptive title from content."""
        try:
            # Take first meaningful sentence or up to 50 characters
            sentences = content.split('.')
            first_sentence = sentences[0].strip()
            
            if len(first_sentence) <= 50:
                return first_sentence
            else:
                return first_sentence[:47] + "..."
        except Exception as e:
            logger.warning(f"Error generating title: {e}")
            return "Untitled Note"  # Default if title generation fails
    
    def _save_extracted_info(self, extracted_info: Dict[str, List]) -> None:
        """Save all extracted information to appropriate files."""
        try:
            # Save todos
            for todo in extracted_info["todos"]:
                self.save_content(todo, "todo")
            
            # Save calendar events
            for event in extracted_info["calendar_events"]:
                self.save_content(event, "calendar")
                
            # Save notes
            for note in extracted_info["notes"]:
                self.save_content(note, "note")
        except Exception as e:
            logger.error(f"Error saving extracted information: {e}")
            raise StorageError(f"Failed to save extracted information: {e}")
    
    def save_content(self, content_data: Dict[str, Any], content_type: str) -> str:
        """Save content to appropriate file with proper naming."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            
            if content_type == "journal":
                date_str = datetime.now().strftime("%Y-%m-%d")
                filename = f"{date_str}.md"
                filepath = self.base_path / "data" / "journal" / filename
            elif content_type == "todo":
                filename = f"todo-{timestamp}.json"
                filepath = self.base_path / "data" / "todos" / filename
            elif content_type == "calendar":
                filename = f"event-{timestamp}.json"
                filepath = self.base_path / "data" / "calendar" / filename
            elif content_type == "note":
                filename = f"note-{timestamp}.md"
                filepath = self.base_path / "data" / "notes" / filename
            else:
                filename = f"{content_type}-{timestamp}.json"
                filepath = self.base_path / "data" / "notes" / filename
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Save content
            if filepath.suffix == '.json':
                with open(filepath, 'w') as f:
                    json.dump(content_data, f, indent=2)
            else:
                # Handle notes that come as dictionaries
                if isinstance(content_data, dict) and content_type == "note":
                    # Format note dictionary as markdown
                    with open(filepath, 'w') as f:
                        f.write(f"# {content_data.get('title', 'Untitled Note')}\n\n")
                        f.write(f"{content_data.get('content', '')}\n\n")
                        
                        # Add metadata at the bottom
                        f.write("---\n")
                        if 'tags' in content_data:
                            tags = ' '.join([f"#{tag}" if not tag.startswith('#') else tag 
                                           for tag in content_data['tags']])
                            f.write(f"Tags: {tags}\n")
                        if 'category' in content_data:
                            f.write(f"Category: {content_data['category']}\n")
                        f.write(f"Created: {timestamp}\n")
                else:
                    with open(filepath, 'w') as f:
                        f.write(content_data)
            
            logger.info(f"Content saved successfully: {filepath}")
            return str(filepath)
            
        except IOError as e:
            logger.error(f"Error writing to file: {e}")
            raise StorageError(f"Failed to save content: {e}")
        except Exception as e:
            logger.error(f"Error saving content: {e}")
            raise StorageError(f"Unknown error while saving content: {e}")
    
    def search_content(self, query: str, content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search across all content in the knowledge base."""
        if not query:
            logger.warning("Empty search query provided")
            return []
            
        results = []
        
        try:
            data_dir = self.base_path / "data"
            
            if not data_dir.exists():
                logger.warning(f"Data directory does not exist: {data_dir}")
                return []
            
            search_dirs = []
            if content_type:
                search_dir = data_dir / content_type
                if not search_dir.exists():
                    logger.warning(f"Content type directory does not exist: {search_dir}")
                    return []
                search_dirs = [search_dir]
            else:
                search_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
            
            for search_dir in search_dirs:
                for file_path in search_dir.rglob("*"):
                    if file_path.is_file():
                        try:
                            content = self._read_file_content(file_path)
                            if query.lower() in content.lower():
                                results.append({
                                    "file": str(file_path),
                                    "type": search_dir.name,
                                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                                })
                        except Exception as e:
                            logger.error(f"Error reading {file_path}: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            raise ContentProcessingError(f"Search failed: {e}")
    
    def _read_file_content(self, file_path: Path) -> str:
        """Read content from file, handling both JSON and text files."""
        try:
            if not file_path.exists():
                raise NotFoundError(f"File does not exist: {file_path}")
                
            if file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            else:
                with open(file_path, 'r') as f:
                    return f.read()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise StorageError(f"Invalid JSON format: {e}")
        except IOError as e:
            logger.error(f"IO error reading {file_path}: {e}")
            raise StorageError(f"File read error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error reading {file_path}: {e}")
            raise StorageError(f"File read error: {e}")
    
    def process_with_privacy(self, content: str, session_id: str = None, 
                            privacy_level: str = "balanced") -> Dict[str, Any]:
        """
        Process content with privacy preservation.
        
        This method first anonymizes the content using the privacy engine,
        then processes it normally, maintaining the privacy throughout.
        
        Args:
            content: Raw text input from user
            session_id: Privacy session ID (created if None)
            privacy_level: Privacy level for anonymization
            
        Returns:
            Dictionary containing organized content and privacy metadata
        """
        try:
            # Create or get privacy session
            if session_id is None:
                session_id = self.session_manager.create_session(privacy_level)
            elif not self.session_manager.get_session(session_id):
                session_id = self.session_manager.create_session(privacy_level)
                
            # Anonymize the content
            result = self.privacy_engine.deidentify(content, session_id)
            
            # Extract context keywords to preserve
            context_keywords = self._extract_context_keywords(content)
            self.session_manager.add_context(session_id, context_keywords)
            
            # Process the anonymized content
            processed_result = self.process_stream_of_consciousness(result.text)
            
            # Add privacy metadata
            processed_result["privacy"] = {
                "session_id": session_id,
                "privacy_level": result.privacy_level,
                "tokens": result.tokens,
                "is_anonymized": True
            }
            
            # Mark extracted items as privacy-safe
            self._mark_privacy_safe(processed_result["extracted_info"])
            
            return processed_result
            
        except PrivacyError as e:
            logger.error(f"Privacy error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in privacy processing: {e}")
            raise PrivacyError(f"Privacy processing failed: {e}")
    
    def process_and_respond(self, content: str, session_id: str = None) -> Dict[str, Any]:
        """
        Process content with privacy and generate intelligent response.
        
        This method handles the complete flow:
        1. Privacy-preserving content processing
        2. Extracting todos, events, etc.
        3. Generating intelligent follow-up suggestions
        4. Creating a natural language response
        5. De-anonymizing responses for human readability
        
        Args:
            content: Raw text input from user
            session_id: Privacy session ID (created if None)
            
        Returns:
            Dictionary with processing results and response
        """
        try:
            # Process with privacy
            result = self.process_with_privacy(content, session_id)
            session_id = result["privacy"]["session_id"]
            
            # Generate suggestions based on extracted information
            suggestions = self._generate_suggestions(result["extracted_info"])
            
            try:
                # De-anonymize suggestions for user readability
                for suggestion in suggestions:
                    suggestion["text"] = self.privacy_engine.reconstruct(suggestion["text"], session_id)
            
                # Generate AI response with privacy enhancement and de-anonymization
                ai_response = self._generate_ai_response(result, session_id)
                
                # Return complete result
                return {
                    **result,
                    "response": {
                        "message": ai_response,
                        "suggestions": suggestions
                    }
                }
            except Exception as e:
                # Log the error but provide a basic response
                logger.error(f"Error in response generation: {e}")
                return {
                    **result,
                    "response": {
                        "message": "I've processed your input.",
                        "suggestions": []
                    }
                }
                
        except Exception as e:
            logger.error(f"Critical error in process_and_respond: {e}")
            # Return a minimal response in case of critical failure
            return {
                "original_content": content,
                "extracted_info": {
                    "todos": [],
                    "calendar_events": [],
                    "notes": [],
                    "tags": [],
                    "categories": ["error"],
                    "cross_refs": []
                },
                "response": {
                    "message": "I'm having trouble processing your request. Please try again later.",
                    "suggestions": []
                },
                "error": str(e)
            }
    
    def _extract_context_keywords(self, content: str) -> List[str]:
        """Extract important context keywords from content."""
        try:
            keywords = []
            
            # Extract nouns and verbs (simplified implementation)
            words = content.split()
            for word in words:
                # Remove punctuation
                clean_word = word.strip(".,;:!?")
                if len(clean_word) > 3 and clean_word.lower() not in ["the", "and", "for", "with"]:
                    keywords.append(clean_word.lower())
            
            return keywords
        except Exception as e:
            logger.warning(f"Error extracting context keywords: {e}")
            return []  # Return empty list to avoid breaking the process
    
    def _mark_privacy_safe(self, extracted_info: Dict[str, List]) -> None:
        """Mark all extracted information as privacy-safe."""
        try:
            for item_list in extracted_info.values():
                for item in item_list:
                    if isinstance(item, dict):
                        item["privacy_safe"] = True
        except Exception as e:
            logger.warning(f"Error marking items as privacy-safe: {e}")
    
    def _generate_suggestions(self, extracted_info: Dict[str, List]) -> List[Dict[str, Any]]:
        """Generate intelligent suggestions based on extracted information."""
        try:
            suggestions = []
            
            # Suggest based on todos
            if extracted_info["todos"]:
                suggestions.append({
                    "type": "todo_followup",
                    "text": "Would you like to set a reminder for this task?",
                    "action": "set_reminder"
                })
            
            # Suggest based on events
            if extracted_info["calendar_events"]:
                suggestions.append({
                    "type": "calendar_followup",
                    "text": "Do you need help preparing for this meeting?",
                    "action": "meeting_prep"
                })
            
            # Suggestion for notes
            if extracted_info["notes"]:
                suggestions.append({
                    "type": "note_followup",
                    "text": "Would you like to add more details to this note?",
                    "action": "edit_note"
                })
            
            return suggestions
        except Exception as e:
            logger.warning(f"Error generating suggestions: {e}")
            return []  # Return empty list rather than breaking the whole process
    
    def _generate_ai_response(self, result: Dict[str, Any], session_id: str) -> str:
        """Generate an AI response with privacy enhancement."""
        try:
            extracted = result["extracted_info"]
            
            # Build response acknowledging what was extracted
            response_parts = []
            
            if extracted["todos"]:
                response_parts.append(f"I've added {len(extracted['todos'])} task(s) to your to-do list.")
            
            if extracted["calendar_events"]:
                response_parts.append(f"I've scheduled {len(extracted['calendar_events'])} event(s) in your calendar.")
            
            if extracted["notes"]:
                response_parts.append(f"I've saved a note with this information.")
            
            # Add a follow-up if appropriate
            if extracted["todos"] or extracted["calendar_events"]:
                response_parts.append("Is there anything else you need help with regarding this?")
            
            # Use the privacy engine to ensure response is privacy-safe
            response = " ".join(response_parts)
            
            # De-anonymize the response before returning to the user
            # This ensures any privacy tokens are replaced with the original values
            response = self.privacy_engine.reconstruct(response, session_id)
            
            return response
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I've processed your input."  # Fallback response 

    # ------------------------------------------------------------------
    # Hierarchical, Relationship, Search & Recommendation API
    # ------------------------------------------------------------------

    # Content CRUD operations
    def create_content(self, content_data: Dict[str, Any], content_type: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a content item using the integrated ContentManager."""
        return self.content_manager.create_content(content_data, content_type, parent_id)

    def get_content(self, content_id: str, include_relationships: bool = False) -> Dict[str, Any]:
        """Retrieve a content item by ID."""
        return self.content_manager.get_content(content_id, include_relationships)

    def update_content(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a content item."""
        return self.content_manager.update_content(content_id, updates)

    def delete_content(self, content_id: str) -> bool:
        """Delete a content item."""
        return self.content_manager.delete_content(content_id)

    # Folder helpers
    def create_folder(self, title: str, parent_id: Optional[str] = None, description: str = "", icon: str = "folder") -> Dict[str, Any]:
        """Create a new folder in the hierarchy."""
        return self.content_manager.create_folder(title, parent_id, description, icon)

    def get_folder_tree(self, folder_id: Optional[str] = None, max_depth: int = -1) -> Dict[str, Any]:
        """Get a tree representation of folders."""
        return self.content_manager.get_folder_tree(folder_id, max_depth)

    def list_folder_contents(self, folder_id: str) -> List[Dict[str, Any]]:
        """List contents of a folder."""
        return self.content_manager.list_folder_contents(folder_id)

    def move_content_to_folder(self, content_id: str, folder_id: str) -> Dict[str, Any]:
        """Move content into a different folder."""
        return self.content_manager.move_content_to_folder(content_id, folder_id)

    # Relationship helpers
    def create_relationship(self, source_id: str, target_id: str, relationship_type: Union[RelationshipType, str] = RelationshipType.RELATED, description: str = "", metadata: Optional[Dict[str, Any]] = None):
        """Create a relationship between two content items."""
        return self.content_manager.create_relationship(source_id, target_id, relationship_type, description, metadata)

    def get_related_content(self, content_id: str, relationship_type: Optional[Union[RelationshipType, str]] = None, include_content: bool = False):
        """Fetch content related to the given item."""
        return self.content_manager.get_related_content(content_id, relationship_type, include_content)

    def delete_relationship(self, source_id: str, target_id: str) -> bool:
        """Delete a relationship between two content items."""
        return self.relationship_manager.delete_relationship(source_id, target_id)

    # Semantic search
    def search_semantic(self, query: str, top_k: int = 10, content_types: Optional[List[str]] = None, categories: Optional[List[str]] = None, tags: Optional[List[str]] = None, min_similarity: float = 0.0):
        """Perform a semantic search across the knowledge base."""
        return self.semantic_search_engine.search(query, top_k, content_types, categories, tags, min_similarity)

    def similar_content(self, content_id: str, top_k: int = 5, min_similarity: float = 0.7):
        """Find content similar to the specified item."""
        return self.semantic_search_engine.similar_content(content_id, top_k, min_similarity)

    # Recommendations
    def get_recommendations(self, content_id: str, max_items: int = 5):
        """Get recommended content items related to the specified item."""
        return self.recommendation_engine.get_related_items(content_id, max_items)

    def get_contextual_suggestions(self, current_context: Dict[str, Any], max_items: int = 3):
        """Get contextual content suggestions based on current user context."""
        return self.recommendation_engine.get_contextual_suggestions(current_context, max_items)

    # Knowledge Graph
    def build_knowledge_graph(self, root_ids: Optional[List[str]] = None, max_depth: int = 2, relationship_types: Optional[List[Union[RelationshipType, str]]] = None):
        """Build a graph representation of content relationships."""
        return self.knowledge_graph.build_graph(root_ids, max_depth, relationship_types) 