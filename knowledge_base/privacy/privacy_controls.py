#!/usr/bin/env python3
"""
Privacy Controls Module for Knowledge Base System.

This module provides fine-grained privacy control capabilities including:
1. Privacy level management
2. Privacy rule engine
3. Privacy inheritance through hierarchy
"""

import os
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Set, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class PrivacyLevel(str, Enum):
    """Privacy levels with increasing restriction."""
    PUBLIC = "public"       # Content accessible with no restrictions
    PROTECTED = "protected"  # Content with basic privacy protection
    PRIVATE = "private"     # Content with strong privacy protection
    RESTRICTED = "restricted"  # Content with maximum privacy protection


@dataclass
class PrivacyRule:
    """Defines a privacy rule with conditions and actions."""
    rule_id: str
    name: str
    description: str
    privacy_level: PrivacyLevel
    content_types: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "privacy_level": self.privacy_level.value,
            "content_types": self.content_types,
            "conditions": self.conditions,
            "actions": self.actions,
            "priority": self.priority,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrivacyRule':
        """Create rule from dictionary."""
        return cls(
            rule_id=data["rule_id"],
            name=data["name"],
            description=data["description"],
            privacy_level=PrivacyLevel(data["privacy_level"]),
            content_types=data.get("content_types", []),
            conditions=data.get("conditions", {}),
            actions=data.get("actions", {}),
            priority=data.get("priority", 0),
            created_at=data.get("created_at", datetime.now().isoformat())
        )


@dataclass
class PrivacyProfile:
    """Defines a set of privacy rules for a specific context."""
    profile_id: str
    name: str
    description: str
    default_privacy_level: PrivacyLevel
    rules: List[PrivacyRule] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "description": self.description,
            "default_privacy_level": self.default_privacy_level.value,
            "rules": [rule.to_dict() for rule in self.rules],
            "metadata": self.metadata,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrivacyProfile':
        """Create profile from dictionary."""
        return cls(
            profile_id=data["profile_id"],
            name=data["name"],
            description=data["description"],
            default_privacy_level=PrivacyLevel(data["default_privacy_level"]),
            rules=[PrivacyRule.from_dict(rule) for rule in data.get("rules", [])],
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", datetime.now().isoformat())
        )


@dataclass
class PrivacySettings:
    """Privacy settings for a content item."""
    privacy_level: PrivacyLevel
    profile_id: Optional[str] = None
    access_control: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    inherits_from: Optional[str] = None  # Parent content ID for inheritance
    overrides_parent: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "privacy_level": self.privacy_level.value,
            "profile_id": self.profile_id,
            "access_control": self.access_control,
            "metadata": self.metadata,
            "inherits_from": self.inherits_from,
            "overrides_parent": self.overrides_parent,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrivacySettings':
        """Create settings from dictionary."""
        return cls(
            privacy_level=PrivacyLevel(data["privacy_level"]),
            profile_id=data.get("profile_id"),
            access_control=data.get("access_control", {}),
            metadata=data.get("metadata", {}),
            inherits_from=data.get("inherits_from"),
            overrides_parent=data.get("overrides_parent", False),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )


class PrivacyRuleEngine:
    """
    Engine for evaluating and applying privacy rules.
    
    This class:
    1. Evaluates content against privacy rules
    2. Determines applicable privacy levels
    3. Applies privacy actions based on rules
    """
    
    def __init__(self):
        """Initialize the rule engine."""
        self.profiles: Dict[str, PrivacyProfile] = {}
        self.default_profile = self._create_default_profile()
    
    def _create_default_profile(self) -> PrivacyProfile:
        """Create and return the default privacy profile."""
        # Create basic rules for the default profile
        public_rule = PrivacyRule(
            rule_id="default_public",
            name="Default Public Content",
            description="Basic rule for public content",
            privacy_level=PrivacyLevel.PUBLIC,
            content_types=["note", "project"],
            conditions={},
            actions={"allow_tokenization": False}
        )
        
        protected_rule = PrivacyRule(
            rule_id="default_protected",
            name="Default Protected Content",
            description="Basic protection for general content",
            privacy_level=PrivacyLevel.PROTECTED,
            content_types=["todo", "calendar", "journal"],
            conditions={},
            actions={"allow_tokenization": True}
        )
        
        private_rule = PrivacyRule(
            rule_id="default_private",
            name="Default Private Content",
            description="Strong protection for sensitive content",
            privacy_level=PrivacyLevel.PRIVATE,
            content_types=["sensitive"],
            conditions={"has_sensitive_data": True},
            actions={"allow_tokenization": True, "encrypt": True}
        )
        
        # Create default profile with rules
        return PrivacyProfile(
            profile_id="default",
            name="Default Privacy Profile",
            description="System default privacy profile",
            default_privacy_level=PrivacyLevel.PROTECTED,
            rules=[public_rule, protected_rule, private_rule],
            metadata={"system": True}
        )
    
    def add_profile(self, profile: PrivacyProfile) -> None:
        """
        Add a privacy profile to the engine.
        
        Args:
            profile: Privacy profile to add
        """
        self.profiles[profile.profile_id] = profile
    
    def get_profile(self, profile_id: str) -> Optional[PrivacyProfile]:
        """
        Get a privacy profile by ID.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Privacy profile or None if not found
        """
        if profile_id == "default":
            return self.default_profile
        return self.profiles.get(profile_id)
    
    def evaluate_content(self, content: Dict[str, Any], 
                        profile_id: str = "default") -> PrivacySettings:
        """
        Evaluate content against privacy rules to determine settings.
        
        Args:
            content: Content item to evaluate
            profile_id: ID of privacy profile to use
            
        Returns:
            Privacy settings for the content
        """
        # Get the profile
        profile = self.get_profile(profile_id)
        if not profile:
            logger.warning(f"Privacy profile not found: {profile_id}, using default")
            profile = self.default_profile
        
        # Start with default privacy level
        privacy_level = profile.default_privacy_level
        
        # Get content type
        content_type = content.get("type", "unknown")
        
        # Track matched rules and actions
        matched_actions = {}
        highest_priority = -1
        
        # Evaluate each rule in the profile
        for rule in sorted(profile.rules, key=lambda r: r.priority, reverse=True):
            # Check content type match
            if rule.content_types and content_type not in rule.content_types:
                continue
                
            # Evaluate conditions
            if self._evaluate_conditions(content, rule.conditions):
                # Rule matched - apply privacy level and actions
                # Only update privacy level if rule has higher priority
                if rule.priority > highest_priority:
                    privacy_level = rule.privacy_level
                    highest_priority = rule.priority
                
                # Collect actions from all matching rules
                matched_actions.update(rule.actions)
        
        # Create privacy settings
        settings = PrivacySettings(
            privacy_level=privacy_level,
            profile_id=profile_id,
            access_control=matched_actions.get("access_control", {}),
            metadata={
                "matched_actions": matched_actions,
                "evaluation_time": datetime.now().isoformat()
            }
        )
        
        return settings
    
    def _evaluate_conditions(self, content: Dict[str, Any], 
                           conditions: Dict[str, Any]) -> bool:
        """
        Evaluate conditions against content.
        
        Args:
            content: Content to evaluate
            conditions: Conditions dictionary
            
        Returns:
            True if conditions match, False otherwise
        """
        # If no conditions, rule always matches
        if not conditions:
            return True
        
        # Special condition checks
        if "has_sensitive_data" in conditions:
            has_sensitive = self._check_sensitive_data(content)
            if has_sensitive != conditions["has_sensitive_data"]:
                return False
                
        # Content property checks
        for key, expected_value in conditions.items():
            if key.startswith("content."):
                # Extract property path
                prop_path = key.split("content.")[1]
                actual_value = self._get_nested_property(content, prop_path)
                
                if actual_value != expected_value:
                    return False
                    
        return True
    
    def _check_sensitive_data(self, content: Dict[str, Any]) -> bool:
        """
        Check if content contains sensitive data.
        
        Args:
            content: Content to check
            
        Returns:
            True if content has sensitive data, False otherwise
        """
        # This is a simplified check - in practice, this would use
        # more sophisticated detection methods
        
        # Check if content has marked sensitive data
        if content.get("sensitive", False):
            return True
            
        # Check content text for sensitive keywords
        sensitive_keywords = [
            "password", "secret", "private", "confidential",
            "ssn", "social security", "credit card", "bank account"
        ]
        
        content_text = ""
        
        # Extract text from various content fields
        if "content" in content and isinstance(content["content"], str):
            content_text += content["content"].lower() + " "
            
        if "title" in content and isinstance(content["title"], str):
            content_text += content["title"].lower() + " "
            
        if "notes" in content and isinstance(content["notes"], str):
            content_text += content["notes"].lower() + " "
            
        # Check for sensitive keywords
        for keyword in sensitive_keywords:
            if keyword in content_text:
                return True
                
        return False
    
    def _get_nested_property(self, obj: Dict[str, Any], prop_path: str) -> Any:
        """
        Get nested property from object using dot notation.
        
        Args:
            obj: Object to get property from
            prop_path: Property path (e.g., "metadata.tags.0")
            
        Returns:
            Property value or None if not found
        """
        parts = prop_path.split(".")
        current = obj
        
        for part in parts:
            # Handle array indices
            if part.isdigit() and isinstance(current, list):
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            # Handle dictionary keys
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current


class PrivacyControlManager:
    """
    Manages privacy controls for the knowledge base system.
    
    This class provides:
    1. Privacy profile management
    2. Content privacy settings
    3. Privacy inheritance
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the privacy control manager.
        
        Args:
            storage_dir: Directory for storing privacy settings
        """
        # Set up storage location
        self.storage_dir = storage_dir
        if storage_dir:
            self.privacy_dir = Path(storage_dir) / "privacy_controls"
        else:
            # Default to home directory
            self.privacy_dir = Path.home() / ".kb_privacy" / "controls"
            
        # Create directories
        self.privacy_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_dir = self.privacy_dir / "profiles"
        self.profiles_dir.mkdir(exist_ok=True)
        self.settings_dir = self.privacy_dir / "settings"
        self.settings_dir.mkdir(exist_ok=True)
        
        # Initialize rule engine
        self.rule_engine = PrivacyRuleEngine()
        
        # Content to settings mapping
        self.content_settings: Dict[str, PrivacySettings] = {}
        
        # Content hierarchy for inheritance
        self.content_hierarchy: Dict[str, List[str]] = {}
        
        # Load existing profiles
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load all privacy profiles from storage."""
        try:
            for profile_file in self.profiles_dir.glob("*.json"):
                try:
                    with open(profile_file, 'r') as f:
                        profile_data = json.load(f)
                        profile = PrivacyProfile.from_dict(profile_data)
                        self.rule_engine.add_profile(profile)
                        logger.debug(f"Loaded privacy profile: {profile.profile_id}")
                except Exception as e:
                    logger.error(f"Error loading profile from {profile_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading privacy profiles: {e}")
    
    def create_profile(self, 
                      name: str, 
                      description: str,
                      default_level: PrivacyLevel = PrivacyLevel.PROTECTED,
                      rules: List[PrivacyRule] = None) -> PrivacyProfile:
        """
        Create a new privacy profile.
        
        Args:
            name: Profile name
            description: Profile description
            default_level: Default privacy level
            rules: Initial privacy rules
            
        Returns:
            Created privacy profile
        """
        import uuid
        
        # Generate unique ID
        profile_id = f"profile-{uuid.uuid4().hex[:8]}"
        
        # Create profile
        profile = PrivacyProfile(
            profile_id=profile_id,
            name=name,
            description=description,
            default_privacy_level=default_level,
            rules=rules or []
        )
        
        # Add to rule engine
        self.rule_engine.add_profile(profile)
        
        # Save profile
        self._save_profile(profile)
        
        return profile
    
    def _save_profile(self, profile: PrivacyProfile) -> None:
        """
        Save a privacy profile to storage.
        
        Args:
            profile: Privacy profile to save
        """
        profile_path = self.profiles_dir / f"{profile.profile_id}.json"
        
        try:
            with open(profile_path, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving profile {profile.profile_id}: {e}")
    
    def get_profile(self, profile_id: str) -> Optional[PrivacyProfile]:
        """
        Get a privacy profile by ID.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Privacy profile or None if not found
        """
        return self.rule_engine.get_profile(profile_id)
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """
        List all available privacy profiles.
        
        Returns:
            List of privacy profile dictionaries
        """
        profiles = []
        
        # Add default profile
        profiles.append(self.rule_engine.default_profile.to_dict())
        
        # Add custom profiles
        for profile_id, profile in self.rule_engine.profiles.items():
            profiles.append(profile.to_dict())
            
        return profiles
    
    def set_content_privacy(self, 
                          content_id: str, 
                          privacy_level: PrivacyLevel = None,
                          profile_id: str = None,
                          inherit_from: str = None,
                          override_parent: bool = False) -> PrivacySettings:
        """
        Set privacy settings for a content item.
        
        Args:
            content_id: Content ID
            privacy_level: Privacy level (None to keep existing or use profile default)
            profile_id: Profile ID to use (None to use default)
            inherit_from: Parent content ID for inheritance (None for no inheritance)
            override_parent: Whether to override parent settings
            
        Returns:
            Updated privacy settings
        """
        # Use default profile if none specified
        if not profile_id:
            profile_id = "default"
            
        # Get existing settings or create new
        existing = self.get_content_privacy(content_id)
        if existing:
            settings = existing
            # Update timestamp
            settings.updated_at = datetime.now().isoformat()
        else:
            # Create new settings
            profile = self.rule_engine.get_profile(profile_id) or self.rule_engine.default_profile
            settings = PrivacySettings(
                privacy_level=privacy_level or profile.default_privacy_level,
                profile_id=profile_id
            )
        
        # Set inheritance
        if inherit_from:
            parent_settings = self.get_content_privacy(inherit_from)
            if parent_settings:
                settings.inherits_from = inherit_from
                
                # Update content hierarchy
                if inherit_from not in self.content_hierarchy:
                    self.content_hierarchy[inherit_from] = []
                if content_id not in self.content_hierarchy[inherit_from]:
                    self.content_hierarchy[inherit_from].append(content_id)
                    
                # Set privacy level from parent if not overriding
                if not override_parent and not privacy_level:
                    settings.privacy_level = parent_settings.privacy_level
        
        # Update privacy level if specified
        if privacy_level:
            settings.privacy_level = privacy_level
            settings.overrides_parent = override_parent
        
        # Store settings
        self.content_settings[content_id] = settings
        
        # Save settings to disk
        self._save_content_settings(content_id, settings)
        
        return settings
    
    def _save_content_settings(self, content_id: str, settings: PrivacySettings) -> None:
        """
        Save content privacy settings to storage.
        
        Args:
            content_id: Content ID
            settings: Privacy settings
        """
        settings_path = self.settings_dir / f"{content_id}.json"
        
        try:
            with open(settings_path, 'w') as f:
                json.dump(settings.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving privacy settings for {content_id}: {e}")
    
    def get_content_privacy(self, content_id: str) -> Optional[PrivacySettings]:
        """
        Get privacy settings for a content item.
        
        Args:
            content_id: Content ID
            
        Returns:
            Privacy settings or None if not set
        """
        # Check memory cache first
        if content_id in self.content_settings:
            return self.content_settings[content_id]
            
        # Check disk storage
        settings_path = self.settings_dir / f"{content_id}.json"
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    settings_data = json.load(f)
                    settings = PrivacySettings.from_dict(settings_data)
                    
                    # Cache for future use
                    self.content_settings[content_id] = settings
                    
                    return settings
            except Exception as e:
                logger.error(f"Error loading privacy settings for {content_id}: {e}")
                
        return None
    
    def evaluate_content_privacy(self, 
                               content_id: str, 
                               content: Dict[str, Any]) -> PrivacySettings:
        """
        Evaluate content against privacy rules and settings.
        
        Args:
            content_id: Content ID
            content: Content data
            
        Returns:
            Effective privacy settings
        """
        # Get explicit settings for content
        explicit_settings = self.get_content_privacy(content_id)
        
        if explicit_settings:
            # If content has parent, check inheritance
            if explicit_settings.inherits_from and not explicit_settings.overrides_parent:
                parent_id = explicit_settings.inherits_from
                parent_settings = self.get_content_privacy(parent_id)
                
                if parent_settings:
                    # Inherit settings from parent
                    inherited_settings = PrivacySettings(
                        privacy_level=parent_settings.privacy_level,
                        profile_id=parent_settings.profile_id,
                        access_control=parent_settings.access_control.copy(),
                        metadata={
                            "inherited": True,
                            "parent_id": parent_id
                        },
                        inherits_from=parent_id
                    )
                    
                    # Override with explicit settings if specified
                    if explicit_settings.overrides_parent:
                        inherited_settings.privacy_level = explicit_settings.privacy_level
                        inherited_settings.overrides_parent = True
                    
                    return inherited_settings
            
            # Use explicit settings
            return explicit_settings
        
        # No explicit settings, evaluate based on content
        profile_id = content.get("privacy_profile", "default")
        return self.rule_engine.evaluate_content(content, profile_id)
    
    def propagate_privacy_settings(self, content_id: str) -> List[str]:
        """
        Propagate privacy settings to child content items.
        
        Args:
            content_id: Parent content ID
            
        Returns:
            List of updated child content IDs
        """
        updated_children = []
        
        # Get parent settings
        parent_settings = self.get_content_privacy(content_id)
        if not parent_settings:
            return updated_children
            
        # Get child content IDs
        children = self.content_hierarchy.get(content_id, [])
        
        # Update each child that inherits from parent
        for child_id in children:
            child_settings = self.get_content_privacy(child_id)
            
            # Skip children that override parent settings
            if child_settings and child_settings.overrides_parent:
                continue
                
            # Apply parent settings to child
            updated_settings = self.set_content_privacy(
                content_id=child_id,
                privacy_level=parent_settings.privacy_level,
                profile_id=parent_settings.profile_id,
                inherit_from=content_id
            )
            
            updated_children.append(child_id)
            
            # Recursively propagate to grandchildren
            if child_id in self.content_hierarchy:
                grandchildren = self.propagate_privacy_settings(child_id)
                updated_children.extend(grandchildren)
                
        return updated_children
    
    def apply_privacy_controls(self, 
                             content_id: str, 
                             content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply privacy controls to content based on settings.
        
        Args:
            content_id: Content ID
            content: Original content
            
        Returns:
            Content with privacy controls applied
        """
        # Evaluate effective privacy settings
        settings = self.evaluate_content_privacy(content_id, content)
        
        # Create a copy of content to modify
        modified_content = content.copy()
        
        # Add privacy metadata
        modified_content["privacy"] = {
            "level": settings.privacy_level.value,
            "profile_id": settings.profile_id,
            "inherits_from": settings.inherits_from,
            "overrides_parent": settings.overrides_parent
        }
        
        # Apply controls based on privacy level
        if settings.privacy_level == PrivacyLevel.PUBLIC:
            # No additional controls for public content
            pass
            
        elif settings.privacy_level == PrivacyLevel.PROTECTED:
            # Add basic tokenization flag for protected content
            modified_content["privacy"]["tokenize"] = True
            
        elif settings.privacy_level == PrivacyLevel.PRIVATE:
            # Add stronger privacy controls for private content
            modified_content["privacy"]["tokenize"] = True
            modified_content["privacy"]["encrypt"] = True
            
        elif settings.privacy_level == PrivacyLevel.RESTRICTED:
            # Maximum privacy for restricted content
            modified_content["privacy"]["tokenize"] = True
            modified_content["privacy"]["encrypt"] = True
            modified_content["privacy"]["limit_access"] = True
            
        # Apply access controls if specified
        if settings.access_control:
            modified_content["privacy"]["access_control"] = settings.access_control
            
        return modified_content


# Default privacy profiles for different content types
def create_default_content_profiles() -> Dict[str, PrivacyProfile]:
    """
    Create default privacy profiles for different content types.
    
    Returns:
        Dictionary of content type to profile
    """
    # Notes profile
    notes_rules = [
        PrivacyRule(
            rule_id="notes_default",
            name="Default Notes Privacy",
            description="Standard privacy for notes",
            privacy_level=PrivacyLevel.PROTECTED,
            content_types=["note"],
            conditions={},
            priority=10
        ),
        PrivacyRule(
            rule_id="notes_sensitive",
            name="Sensitive Notes Privacy",
            description="Increased privacy for notes with sensitive content",
            privacy_level=PrivacyLevel.PRIVATE,
            content_types=["note"],
            conditions={"has_sensitive_data": True},
            priority=20
        )
    ]
    
    notes_profile = PrivacyProfile(
        profile_id="notes_default",
        name="Notes Privacy Profile",
        description="Privacy profile for notes",
        default_privacy_level=PrivacyLevel.PROTECTED,
        rules=notes_rules
    )
    
    # Journal profile with stricter defaults
    journal_rules = [
        PrivacyRule(
            rule_id="journal_default",
            name="Default Journal Privacy",
            description="Standard privacy for journal entries",
            privacy_level=PrivacyLevel.PRIVATE,
            content_types=["journal"],
            conditions={},
            priority=10
        ),
        PrivacyRule(
            rule_id="journal_sensitive",
            name="Sensitive Journal Privacy",
            description="Maximum privacy for sensitive journal entries",
            privacy_level=PrivacyLevel.RESTRICTED,
            content_types=["journal"],
            conditions={"has_sensitive_data": True},
            priority=20
        )
    ]
    
    journal_profile = PrivacyProfile(
        profile_id="journal_default",
        name="Journal Privacy Profile",
        description="Privacy profile for journal entries",
        default_privacy_level=PrivacyLevel.PRIVATE,
        rules=journal_rules
    )
    
    # Todo profile
    todo_rules = [
        PrivacyRule(
            rule_id="todo_default",
            name="Default Todo Privacy",
            description="Standard privacy for todos",
            privacy_level=PrivacyLevel.PROTECTED,
            content_types=["todo"],
            conditions={},
            priority=10
        ),
        PrivacyRule(
            rule_id="todo_sensitive",
            name="Sensitive Todo Privacy",
            description="Increased privacy for sensitive todos",
            privacy_level=PrivacyLevel.PRIVATE,
            content_types=["todo"],
            conditions={"has_sensitive_data": True},
            priority=20
        )
    ]
    
    todo_profile = PrivacyProfile(
        profile_id="todo_default",
        name="Todo Privacy Profile",
        description="Privacy profile for todos",
        default_privacy_level=PrivacyLevel.PROTECTED,
        rules=todo_rules
    )
    
    # Calendar profile
    calendar_rules = [
        PrivacyRule(
            rule_id="calendar_default",
            name="Default Calendar Privacy",
            description="Standard privacy for calendar events",
            privacy_level=PrivacyLevel.PROTECTED,
            content_types=["calendar"],
            conditions={},
            priority=10
        ),
        PrivacyRule(
            rule_id="calendar_private",
            name="Private Calendar Privacy",
            description="Increased privacy for private calendar events",
            privacy_level=PrivacyLevel.PRIVATE,
            content_types=["calendar"],
            conditions={"content.metadata.private": True},
            priority=20
        )
    ]
    
    calendar_profile = PrivacyProfile(
        profile_id="calendar_default",
        name="Calendar Privacy Profile",
        description="Privacy profile for calendar events",
        default_privacy_level=PrivacyLevel.PROTECTED,
        rules=calendar_rules
    )
    
    # Return content type to profile mapping
    return {
        "note": notes_profile,
        "journal": journal_profile,
        "todo": todo_profile,
        "calendar": calendar_profile
    } 