"""
Configuration Utilities
Tools for loading and managing configuration settings.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager for the Knowledge Base System."""
    
    def __init__(self, base_path: Path):
        """
        Initialize the configuration manager.
        
        Args:
            base_path: Base path for loading configuration files
        """
        self.base_path = base_path
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load AI instructions and configuration.
        
        Returns:
            Dictionary containing configuration settings
        """
        config_path = self.base_path / "config" / "ai_instructions.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return self._apply_env_overrides(config)
        return self._get_default_config()
    
    def load_conventions(self) -> Dict[str, Any]:
        """
        Load naming conventions and standards.
        
        Returns:
            Dictionary containing naming conventions
        """
        conv_path = self.base_path / "config" / "conventions.yaml"
        if conv_path.exists():
            with open(conv_path, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_conventions()
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to the configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with environment overrides applied
        """
        # Example environment variable overrides
        if os.environ.get("KB_LOG_LEVEL"):
            if "logging" not in config:
                config["logging"] = {}
            config["logging"]["level"] = os.environ.get("KB_LOG_LEVEL")
        
        if os.environ.get("KB_DATA_PATH"):
            if "storage" not in config:
                config["storage"] = {}
            config["storage"]["data_path"] = os.environ.get("KB_DATA_PATH")
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration if file not found.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "organization": {
                "auto_categorization": {
                    "work": ["office", "meeting", "project", "deadline", "report", "client"],
                    "personal": ["home", "family", "personal", "self", "life"],
                    "learning": ["learn", "study", "research", "book", "course", "read"],
                    "health": ["health", "fitness", "exercise", "doctor", "medical"]
                },
                "priority_detection": {
                    "urgent_keywords": ["urgent", "asap", "immediately", "critical", "emergency"]
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "storage": {
                "data_path": "data"
            }
        }
    
    def _get_default_conventions(self) -> Dict[str, Any]:
        """
        Get default naming conventions if file not found.
        
        Returns:
            Default naming conventions dictionary
        """
        return {
            "file_naming": {
                "notes": "note-{timestamp}.md",
                "todos": "todo-{timestamp}.json",
                "events": "event-{timestamp}.json",
                "projects": "project-{timestamp}.json",
                "references": "reference-{timestamp}.json"
            },
            "content_types": {
                "note": {
                    "extensions": [".md", ".txt"],
                    "template": "templates/note_template.md"
                },
                "todo": {
                    "extensions": [".json"],
                    "template": "templates/todo_template.json"
                },
                "calendar": {
                    "extensions": [".json"],
                    "template": "templates/calendar_template.json"
                },
                "project": {
                    "extensions": [".json", ".md"],
                    "template": "templates/project_template.json"
                }
            }
        } 