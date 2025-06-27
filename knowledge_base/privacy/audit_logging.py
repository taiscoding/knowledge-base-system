#!/usr/bin/env python3
"""
Privacy Audit Logging Module for Knowledge Base System.

This module provides comprehensive privacy audit logging capabilities including:
1. Privacy operation logging
2. Tamper-evident audit trail
3. Compliance reporting and verification tools
"""

import os
import json
import time
import logging
import hashlib
import hmac
import uuid
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class PrivacyOperation(str, Enum):
    """Privacy operation types for audit logging."""
    ACCESS = "access"               # Content access
    MODIFICATION = "modification"   # Content modification
    ENCRYPTION = "encryption"       # Content encryption/decryption
    KEY_MANAGEMENT = "key"          # Key management operations
    SETTINGS = "settings"           # Privacy settings changes
    EXPORT = "export"               # Content export
    IMPORT = "import"               # Content import
    TOKENIZATION = "tokenization"   # Privacy tokenization
    DETOKENIZATION = "detokenization"  # Privacy token reversal
    COMPLIANCE = "compliance"       # Compliance-related operations
    ADMIN = "admin"                 # Administrative operations


class PrivacyImpact(str, Enum):
    """Impact levels for privacy operations."""
    LOW = "low"           # Minimal privacy impact
    MEDIUM = "medium"     # Moderate privacy impact
    HIGH = "high"         # Significant privacy impact
    CRITICAL = "critical" # Critical privacy impact


@dataclass
class AuditLogEntry:
    """Privacy audit log entry with operation details."""
    entry_id: str
    timestamp: str
    operation: PrivacyOperation
    content_id: Optional[str]
    user_id: Optional[str]
    impact_level: PrivacyImpact
    details: Dict[str, Any]
    previous_hash: Optional[str] = None
    entry_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "operation": self.operation.value,
            "content_id": self.content_id,
            "user_id": self.user_id,
            "impact_level": self.impact_level.value,
            "details": self.details,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLogEntry':
        """Create log entry from dictionary."""
        return cls(
            entry_id=data["entry_id"],
            timestamp=data["timestamp"],
            operation=PrivacyOperation(data["operation"]),
            content_id=data.get("content_id"),
            user_id=data.get("user_id"),
            impact_level=PrivacyImpact(data["impact_level"]),
            details=data.get("details", {}),
            previous_hash=data.get("previous_hash"),
            entry_hash=data.get("entry_hash")
        )
    
    def compute_hash(self, key: bytes) -> str:
        """
        Compute HMAC hash for this log entry.
        
        Args:
            key: Secret key for HMAC
            
        Returns:
            Hex-encoded HMAC hash
        """
        # Create a deterministic representation of the entry for hashing
        # (exclude the hash fields themselves)
        hashable_content = json.dumps({
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "operation": self.operation.value,
            "content_id": self.content_id,
            "user_id": self.user_id,
            "impact_level": self.impact_level.value,
            "details": self.details,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        
        # Compute HMAC with SHA-256
        h = hmac.new(key, hashable_content.encode(), hashlib.sha256)
        return h.hexdigest()


class PrivacyAuditLogger:
    """
    Logger for privacy-related operations.
    
    This class provides:
    1. Secure, tamper-evident logging of privacy operations
    2. Log rotation and archiving
    3. Compliance verification capabilities
    """
    
    def __init__(self, log_dir: str = None, secret_key: bytes = None):
        """
        Initialize the privacy audit logger.
        
        Args:
            log_dir: Directory for log storage
            secret_key: Secret key for HMAC verification (generated if None)
        """
        # Set up log directory
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path.home() / ".kb_privacy" / "audit_logs"
            
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up directories for current and archived logs
        self.current_log_dir = self.log_dir / "current"
        self.current_log_dir.mkdir(exist_ok=True)
        
        self.archive_log_dir = self.log_dir / "archive"
        self.archive_log_dir.mkdir(exist_ok=True)
        
        # Set up secret key for HMAC verification
        self.secret_key = secret_key or os.urandom(32)
        self._store_secret_key()
        
        # Cache for last entry hash (for chaining)
        self.last_entry_hash: Optional[str] = None
        
        # Load last entry hash if available
        self._load_last_entry_hash()
        
        # Log retention settings (defaults)
        self.retention_days = 90  # Default retention period
        self.max_log_size_mb = 10  # Size threshold for rotation
        
        # Current log file
        self.current_log_file = self._get_current_log_file()
        
        # Track current log size
        self._update_log_size()
    
    def _store_secret_key(self) -> None:
        """Store the secret key securely."""
        key_file = self.log_dir / "audit_key"
        
        # Only write if doesn't exist or we're explicitly setting a new key
        if not key_file.exists():
            try:
                # Write with restricted permissions
                with open(key_file, 'wb') as f:
                    f.write(self.secret_key)
                
                # Set permissions (owner read/write only)
                os.chmod(key_file, 0o600)
                
            except Exception as e:
                logger.error(f"Failed to store audit secret key: {e}")
        else:
            # Read existing key
            try:
                with open(key_file, 'rb') as f:
                    self.secret_key = f.read()
            except Exception as e:
                logger.error(f"Failed to read audit secret key: {e}")
    
    def _get_current_log_file(self) -> Path:
        """Get path to current log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.current_log_dir / f"privacy_audit_{today}.jsonl"
    
    def _update_log_size(self) -> None:
        """Update tracking of current log size."""
        if self.current_log_file.exists():
            self.current_log_size = self.current_log_file.stat().st_size / (1024 * 1024)  # Size in MB
        else:
            self.current_log_size = 0
    
    def _load_last_entry_hash(self) -> None:
        """Load the hash of the last entry for chaining."""
        try:
            # Check all log files in current directory, sorted by modified time
            log_files = sorted(
                self.current_log_dir.glob("privacy_audit_*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            if not log_files:
                return
                
            # Get the most recent file
            latest_log = log_files[0]
            
            # Find the last line
            last_entry = None
            with open(latest_log, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:  # Skip empty lines
                        try:
                            entry_data = json.loads(line)
                            last_entry = entry_data
                        except json.JSONDecodeError:
                            pass
            
            if last_entry and "entry_hash" in last_entry:
                self.last_entry_hash = last_entry["entry_hash"]
                
        except Exception as e:
            logger.error(f"Error loading last entry hash: {e}")
    
    def log_operation(self, 
                     operation: PrivacyOperation,
                     impact_level: PrivacyImpact,
                     details: Dict[str, Any],
                     content_id: str = None,
                     user_id: str = None) -> AuditLogEntry:
        """
        Log a privacy operation.
        
        Args:
            operation: Type of privacy operation
            impact_level: Impact level of the operation
            details: Operation details
            content_id: ID of affected content (if applicable)
            user_id: ID of user performing operation (if applicable)
            
        Returns:
            Created audit log entry
        """
        # Rotate log if needed
        self._check_rotation()
        
        # Generate unique entry ID
        entry_id = f"audit-{uuid.uuid4().hex}"
        
        # Create log entry
        entry = AuditLogEntry(
            entry_id=entry_id,
            timestamp=datetime.now().isoformat(),
            operation=operation,
            content_id=content_id,
            user_id=user_id,
            impact_level=impact_level,
            details=details,
            previous_hash=self.last_entry_hash
        )
        
        # Compute hash for this entry
        entry.entry_hash = entry.compute_hash(self.secret_key)
        
        # Write entry to log file
        self._write_log_entry(entry)
        
        # Update last entry hash
        self.last_entry_hash = entry.entry_hash
        
        return entry
    
    def _write_log_entry(self, entry: AuditLogEntry) -> None:
        """
        Write a log entry to the current log file.
        
        Args:
            entry: Audit log entry to write
        """
        try:
            # Ensure current log file is up to date
            self.current_log_file = self._get_current_log_file()
            
            # Append entry to log file
            with open(self.current_log_file, 'a') as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
                
            # Update log size tracking
            self._update_log_size()
            
        except Exception as e:
            logger.error(f"Failed to write audit log entry: {e}")
    
    def _check_rotation(self) -> None:
        """Check and perform log rotation if needed."""
        # Check if log file is from a different day
        if self.current_log_file != self._get_current_log_file():
            self._rotate_log()
            return
            
        # Check if log file exceeds size threshold
        if self.current_log_size >= self.max_log_size_mb:
            self._rotate_log()
    
    def _rotate_log(self) -> None:
        """Rotate the current log file to archive."""
        # Only rotate if current log file exists
        if not self.current_log_file.exists():
            # Update current log file path
            self.current_log_file = self._get_current_log_file()
            return
            
        try:
            # Generate archive filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = self.current_log_file.name
            archive_name = f"{base_filename.split('.')[0]}_{timestamp}.jsonl"
            archive_path = self.archive_log_dir / archive_name
            
            # Move file to archive
            self.current_log_file.rename(archive_path)
            
            # Update current log file path
            self.current_log_file = self._get_current_log_file()
            self.current_log_size = 0
            
            # Clean up old archives
            self._cleanup_old_archives()
            
        except Exception as e:
            logger.error(f"Failed to rotate audit log: {e}")
    
    def _cleanup_old_archives(self) -> None:
        """Clean up archives older than retention period."""
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            # Check all archives
            for archive_file in self.archive_log_dir.glob("privacy_audit_*.jsonl"):
                try:
                    # Get file modification time
                    mod_time = datetime.fromtimestamp(archive_file.stat().st_mtime)
                    
                    # Remove if older than retention period
                    if mod_time < cutoff_date:
                        archive_file.unlink()
                        
                except Exception as e:
                    logger.warning(f"Failed to check/remove archive {archive_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error during archive cleanup: {e}")
    
    def query_logs(self, 
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  operations: Optional[List[PrivacyOperation]] = None,
                  impact_levels: Optional[List[PrivacyImpact]] = None,
                  content_id: Optional[str] = None,
                  user_id: Optional[str] = None,
                  limit: int = 100) -> List[AuditLogEntry]:
        """
        Query audit logs with optional filters.
        
        Args:
            start_time: Start time for query
            end_time: End time for query
            operations: List of operations to include
            impact_levels: List of impact levels to include
            content_id: Filter by content ID
            user_id: Filter by user ID
            limit: Maximum number of entries to return
            
        Returns:
            List of matching audit log entries
        """
        # Default time range if not specified
        if not end_time:
            end_time = datetime.now()
            
        if not start_time:
            start_time = end_time - timedelta(days=7)  # Default to last 7 days
            
        # Convert operations to set of string values if provided
        op_values = {op.value for op in operations} if operations else None
        
        # Convert impact levels to set of string values if provided
        impact_values = {level.value for level in impact_levels} if impact_levels else None
        
        # Result list
        results: List[AuditLogEntry] = []
        
        # Determine log files to search (both current and archived)
        log_files = list(self.current_log_dir.glob("privacy_audit_*.jsonl"))
        log_files.extend(self.archive_log_dir.glob("privacy_audit_*.jsonl"))
        
        # Sort log files by modification time (newest first)
        log_files = sorted(log_files, key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Process each log file
        for log_file in log_files:
            # Skip if we've reached the limit
            if len(results) >= limit:
                break
                
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                            
                        try:
                            # Parse log entry
                            entry_dict = json.loads(line)
                            entry_time = datetime.fromisoformat(entry_dict["timestamp"])
                            
                            # Check time range
                            if entry_time < start_time or entry_time > end_time:
                                continue
                                
                            # Check operation filter
                            if op_values and entry_dict["operation"] not in op_values:
                                continue
                                
                            # Check impact level filter
                            if impact_values and entry_dict["impact_level"] not in impact_values:
                                continue
                                
                            # Check content ID filter
                            if content_id and entry_dict.get("content_id") != content_id:
                                continue
                                
                            # Check user ID filter
                            if user_id and entry_dict.get("user_id") != user_id:
                                continue
                                
                            # Entry matches all filters, add to results
                            results.append(AuditLogEntry.from_dict(entry_dict))
                            
                            # Check limit
                            if len(results) >= limit:
                                break
                                
                        except Exception as e:
                            logger.warning(f"Error parsing log entry: {e}")
                            continue
                            
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")
        
        return results
    
    def verify_log_integrity(self, 
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Verify the integrity of the audit log chain.
        
        Args:
            start_time: Start time for verification
            end_time: End time for verification
            
        Returns:
            Tuple of (integrity_verified, list of integrity issues)
        """
        # Default time range if not specified
        if not end_time:
            end_time = datetime.now()
            
        if not start_time:
            start_time = end_time - timedelta(days=30)  # Default to last 30 days
            
        # Track verification results
        integrity_verified = True
        issues: List[Dict[str, Any]] = []
        
        # Get log files to verify
        log_files = list(self.current_log_dir.glob("privacy_audit_*.jsonl"))
        log_files.extend(self.archive_log_dir.glob("privacy_audit_*.jsonl"))
        
        # Sort log files by modification time
        log_files = sorted(log_files, key=lambda p: p.stat().st_mtime)
        
        # Hash of previous entry for chain verification
        prev_hash = None
        prev_entry_id = None
        
        # Process each log file
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    # Process entries in the file
                    line_number = 0
                    for line in f:
                        line_number += 1
                        line = line.strip()
                        if not line:
                            continue
                            
                        try:
                            # Parse log entry
                            entry_dict = json.loads(line)
                            entry_time = datetime.fromisoformat(entry_dict["timestamp"])
                            
                            # Skip entries outside time range
                            if entry_time < start_time or entry_time > end_time:
                                continue
                                
                            # Create entry object
                            entry = AuditLogEntry.from_dict(entry_dict)
                            
                            # Verify entry hash
                            computed_hash = entry.compute_hash(self.secret_key)
                            if computed_hash != entry.entry_hash:
                                integrity_verified = False
                                issues.append({
                                    "file": str(log_file),
                                    "line": line_number,
                                    "entry_id": entry.entry_id,
                                    "timestamp": entry.timestamp,
                                    "issue": "Invalid entry hash",
                                    "stored_hash": entry.entry_hash,
                                    "computed_hash": computed_hash
                                })
                            
                            # Verify chain integrity (except for first entry)
                            if prev_hash is not None and entry.previous_hash != prev_hash:
                                integrity_verified = False
                                issues.append({
                                    "file": str(log_file),
                                    "line": line_number,
                                    "entry_id": entry.entry_id,
                                    "timestamp": entry.timestamp,
                                    "previous_entry": prev_entry_id,
                                    "issue": "Chain integrity broken",
                                    "expected_previous_hash": prev_hash,
                                    "actual_previous_hash": entry.previous_hash
                                })
                            
                            # Update previous hash for chain verification
                            prev_hash = entry.entry_hash
                            prev_entry_id = entry.entry_id
                            
                        except Exception as e:
                            integrity_verified = False
                            issues.append({
                                "file": str(log_file),
                                "line": line_number,
                                "issue": f"Error processing entry: {str(e)}"
                            })
                            
            except Exception as e:
                integrity_verified = False
                issues.append({
                    "file": str(log_file),
                    "issue": f"Error reading log file: {str(e)}"
                })
        
        return integrity_verified, issues


class ComplianceReporter:
    """
    Generates compliance reports from audit logs.
    
    This class provides:
    1. Standard compliance reports
    2. Custom report generation
    3. Compliance verification tools
    """
    
    def __init__(self, audit_logger: PrivacyAuditLogger):
        """
        Initialize the compliance reporter.
        
        Args:
            audit_logger: Privacy audit logger instance
        """
        self.audit_logger = audit_logger
    
    def generate_access_report(self, 
                             start_time: datetime,
                             end_time: datetime,
                             content_id: Optional[str] = None,
                             user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a report of content access operations.
        
        Args:
            start_time: Start time for report
            end_time: End time for report
            content_id: Optional content ID to filter by
            user_id: Optional user ID to filter by
            
        Returns:
            Access report dictionary
        """
        # Query access operations
        access_entries = self.audit_logger.query_logs(
            start_time=start_time,
            end_time=end_time,
            operations=[PrivacyOperation.ACCESS],
            content_id=content_id,
            user_id=user_id,
            limit=1000  # Higher limit for comprehensive report
        )
        
        # Aggregate access statistics
        access_by_content = {}
        access_by_user = {}
        access_by_date = {}
        high_impact_accesses = []
        
        for entry in access_entries:
            # Track by content
            if entry.content_id:
                access_by_content[entry.content_id] = access_by_content.get(entry.content_id, 0) + 1
                
            # Track by user
            if entry.user_id:
                access_by_user[entry.user_id] = access_by_user.get(entry.user_id, 0) + 1
                
            # Track by date
            date = entry.timestamp.split("T")[0]  # Extract date part
            access_by_date[date] = access_by_date.get(date, 0) + 1
            
            # Track high impact accesses
            if entry.impact_level in [PrivacyImpact.HIGH, PrivacyImpact.CRITICAL]:
                high_impact_accesses.append(entry.to_dict())
        
        # Create report
        report = {
            "report_type": "access_report",
            "generated_at": datetime.now().isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_accesses": len(access_entries),
            "access_by_content": access_by_content,
            "access_by_user": access_by_user,
            "access_by_date": access_by_date,
            "high_impact_accesses": high_impact_accesses,
            "filters": {
                "content_id": content_id,
                "user_id": user_id
            }
        }
        
        return report
    
    def generate_privacy_operation_report(self,
                                        start_time: datetime,
                                        end_time: datetime) -> Dict[str, Any]:
        """
        Generate a report of all privacy operations.
        
        Args:
            start_time: Start time for report
            end_time: End time for report
            
        Returns:
            Privacy operation report dictionary
        """
        # Query all privacy operations
        entries = self.audit_logger.query_logs(
            start_time=start_time,
            end_time=end_time,
            limit=2000  # Higher limit for comprehensive report
        )
        
        # Aggregate statistics
        operations_count = {}
        impact_levels_count = {}
        critical_operations = []
        modified_content_ids = set()
        encryption_operations = []
        
        for entry in entries:
            # Track by operation type
            op_type = entry.operation.value
            operations_count[op_type] = operations_count.get(op_type, 0) + 1
            
            # Track by impact level
            impact = entry.impact_level.value
            impact_levels_count[impact] = impact_levels_count.get(impact, 0) + 1
            
            # Track critical operations
            if entry.impact_level == PrivacyImpact.CRITICAL:
                critical_operations.append(entry.to_dict())
                
            # Track modified content
            if entry.operation == PrivacyOperation.MODIFICATION and entry.content_id:
                modified_content_ids.add(entry.content_id)
                
            # Track encryption operations
            if entry.operation == PrivacyOperation.ENCRYPTION:
                encryption_operations.append(entry.to_dict())
        
        # Create report
        report = {
            "report_type": "privacy_operation_report",
            "generated_at": datetime.now().isoformat(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_operations": len(entries),
            "operations_by_type": operations_count,
            "operations_by_impact": impact_levels_count,
            "critical_operations": critical_operations,
            "modified_content_count": len(modified_content_ids),
            "encryption_operations": encryption_operations
        }
        
        return report
    
    def generate_compliance_verification_report(self) -> Dict[str, Any]:
        """
        Generate a report verifying compliance with privacy requirements.
        
        Returns:
            Compliance verification report dictionary
        """
        # Start with basic report structure
        report = {
            "report_type": "compliance_verification",
            "generated_at": datetime.now().isoformat(),
            "verification_results": {},
            "issues_detected": False,
            "recommendations": []
        }
        
        # Verify log integrity
        integrity_verified, integrity_issues = self.audit_logger.verify_log_integrity()
        report["verification_results"]["log_integrity"] = {
            "verified": integrity_verified,
            "issues": integrity_issues
        }
        
        if not integrity_verified:
            report["issues_detected"] = True
            report["recommendations"].append({
                "priority": "high",
                "area": "log_integrity",
                "recommendation": "Investigate log integrity issues immediately. Logs may have been tampered with."
            })
        
        # Check for high-impact operations in the last 24 hours
        high_impact_ops = self.audit_logger.query_logs(
            start_time=datetime.now() - timedelta(days=1),
            impact_levels=[PrivacyImpact.HIGH, PrivacyImpact.CRITICAL]
        )
        
        report["verification_results"]["recent_high_impact_operations"] = {
            "count": len(high_impact_ops),
            "operations": [op.to_dict() for op in high_impact_ops]
        }
        
        if len(high_impact_ops) > 5:  # Arbitrary threshold for illustration
            report["issues_detected"] = True
            report["recommendations"].append({
                "priority": "medium",
                "area": "high_impact_operations",
                "recommendation": f"Review the {len(high_impact_ops)} high-impact privacy operations from the last 24 hours."
            })
        
        # Check for encryption operations
        encryption_ops = self.audit_logger.query_logs(
            start_time=datetime.now() - timedelta(days=7),
            operations=[PrivacyOperation.ENCRYPTION]
        )
        
        report["verification_results"]["encryption_usage"] = {
            "count": len(encryption_ops),
            "last_7_days": len(encryption_ops)
        }
        
        if len(encryption_ops) == 0:
            report["issues_detected"] = True
            report["recommendations"].append({
                "priority": "high",
                "area": "encryption",
                "recommendation": "No encryption operations detected in the last 7 days. Verify that encryption is being properly applied."
            })
        
        return report
    
    def generate_custom_report(self, 
                             report_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a custom report based on provided configuration.
        
        Args:
            report_config: Report configuration dictionary
            
        Returns:
            Custom report dictionary
        """
        # Extract configuration
        start_time = datetime.fromisoformat(report_config.get("start_time", 
                                         (datetime.now() - timedelta(days=30)).isoformat()))
        end_time = datetime.fromisoformat(report_config.get("end_time", 
                                       datetime.now().isoformat()))
        operations = [PrivacyOperation(op) for op in report_config.get("operations", [])]
        impact_levels = [PrivacyImpact(level) for level in report_config.get("impact_levels", [])]
        content_id = report_config.get("content_id")
        user_id = report_config.get("user_id")
        
        # Query logs with filters
        entries = self.audit_logger.query_logs(
            start_time=start_time,
            end_time=end_time,
            operations=operations if operations else None,
            impact_levels=impact_levels if impact_levels else None,
            content_id=content_id,
            user_id=user_id,
            limit=report_config.get("limit", 1000)
        )
        
        # Create custom aggregations if specified
        aggregations = {}
        for agg_field in report_config.get("aggregate_by", []):
            if agg_field == "operation":
                operations_count = {}
                for entry in entries:
                    op_type = entry.operation.value
                    operations_count[op_type] = operations_count.get(op_type, 0) + 1
                aggregations["by_operation"] = operations_count
                
            elif agg_field == "impact":
                impact_count = {}
                for entry in entries:
                    impact = entry.impact_level.value
                    impact_count[impact] = impact_count.get(impact, 0) + 1
                aggregations["by_impact"] = impact_count
                
            elif agg_field == "date":
                date_count = {}
                for entry in entries:
                    date = entry.timestamp.split("T")[0]  # Extract date part
                    date_count[date] = date_count.get(date, 0) + 1
                aggregations["by_date"] = date_count
                
            elif agg_field == "content":
                content_count = {}
                for entry in entries:
                    if entry.content_id:
                        content_count[entry.content_id] = content_count.get(entry.content_id, 0) + 1
                aggregations["by_content"] = content_count
                
            elif agg_field == "user":
                user_count = {}
                for entry in entries:
                    if entry.user_id:
                        user_count[entry.user_id] = user_count.get(entry.user_id, 0) + 1
                aggregations["by_user"] = user_count
        
        # Create report
        report = {
            "report_type": "custom_report",
            "generated_at": datetime.now().isoformat(),
            "configuration": report_config,
            "total_entries": len(entries),
            "aggregations": aggregations,
        }
        
        # Include detailed entries if requested
        if report_config.get("include_entries", False):
            report["entries"] = [entry.to_dict() for entry in entries]
        
        return report 