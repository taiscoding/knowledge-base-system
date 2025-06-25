#!/usr/bin/env python3
"""
Configuration Management
Loading and management of configuration settings for token intelligence.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manager for loading and accessing configuration settings."""
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the configuration manager.
        
        Args:
            base_path: Base path for configuration files
        """
        self.base_path = Path(base_path)
        self.config_dir = self.base_path / "config"
        self.config_cache = {}
    
    def load_config(self, config_name: str = "ai_instructions") -> Dict[str, Any]:
        """
        Load a configuration file by name.
        
        Args:
            config_name: Name of the configuration file (without extension)
            
        Returns:
            Dictionary containing configuration settings
        """
        if config_name in self.config_cache:
            return self.config_cache[config_name]
        
        config_file = self.config_dir / f"{config_name}.yaml"
        if not config_file.exists():
            return {}
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.config_cache[config_name] = config
                return config
        except Exception as e:
            print(f"Error loading configuration '{config_name}': {e}")
            return {}
    
    def get_value(self, key_path: str, config_name: str = "ai_instructions", default: Any = None) -> Any:
        """
        Get a specific configuration value using dot notation.
        
        Args:
            key_path: Path to the configuration value using dot notation (e.g., "storage.profiles.enabled")
            config_name: Name of the configuration file
            default: Default value if the specified key is not found
            
        Returns:
            Configuration value or default if not found
        """
        config = self.load_config(config_name)
        
        # Split the key path by dots and navigate through the config
        parts = key_path.split('.')
        current = config
        
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        
        return current
    
    def get_env_config(self, env_var: str, default: Any = None) -> Any:
        """
        Get a configuration value from an environment variable.
        
        Args:
            env_var: Name of the environment variable
            default: Default value if the environment variable is not set
            
        Returns:
            Environment variable value or default if not set
        """
        return os.environ.get(env_var, default)
    
    def get_combined_config(self, key_path: str, env_var: Optional[str] = None, 
                           config_name: str = "ai_instructions", default: Any = None) -> Any:
        """
        Get a configuration value with environment variable override.
        
        Args:
            key_path: Path to the configuration value using dot notation
            env_var: Environment variable that can override the config value
            config_name: Name of the configuration file
            default: Default value if neither config nor environment variable is found
            
        Returns:
            Configuration value from environment variable if set, otherwise from config file
        """
        # Try environment variable first if specified
        if env_var and env_var in os.environ:
            return self.get_env_config(env_var)
        
        # Fall back to configuration file
        return self.get_value(key_path, config_name, default)


# Global config manager instance
_config_manager = None


def get_config_manager(base_path: str = ".") -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Args:
        base_path: Base path for configuration files
        
    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(base_path)
    return _config_manager


def get_config(config_name: str = "ai_instructions") -> Dict[str, Any]:
    """
    Get configuration dictionary by name.
    
    Args:
        config_name: Name of the configuration file
        
    Returns:
        Dictionary containing configuration settings
    """
    return get_config_manager().load_config(config_name) 