#!/usr/bin/env python3
"""
Tests for configuration utilities.
"""

import os
import pytest
import yaml
from pathlib import Path
import tempfile
from knowledge_base.utils.config import Config


class TestConfig:
    """Test suite for Config class."""
    
    @pytest.fixture
    def sample_config_dir(self):
        """Create a temporary directory with sample config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            config_dir = base_path / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a sample AI instructions config file
            ai_instructions = {
                "organization": {
                    "auto_categorization": {
                        "work": ["office", "meeting", "project"],
                        "personal": ["home", "family", "personal"]
                    },
                    "priority_detection": {
                        "urgent_keywords": ["urgent", "asap", "critical"]
                    }
                },
                "logging": {
                    "level": "INFO",
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "storage": {
                    "data_path": "custom_data"
                }
            }
            
            # Create a sample conventions config file
            conventions = {
                "file_naming": {
                    "notes": "note-{timestamp}.md",
                    "todos": "todo-{timestamp}.json"
                },
                "content_types": {
                    "note": {
                        "extensions": [".md", ".txt"],
                        "template": "templates/note_template.md"
                    },
                    "todo": {
                        "extensions": [".json"],
                        "template": "templates/todo_template.json"
                    }
                }
            }
            
            # Write config files
            with open(config_dir / "ai_instructions.yaml", 'w') as f:
                yaml.dump(ai_instructions, f)
                
            with open(config_dir / "conventions.yaml", 'w') as f:
                yaml.dump(conventions, f)
            
            yield base_path
    
    def test_initialization(self, sample_config_dir):
        """Test Config initialization."""
        config = Config(sample_config_dir)
        assert config.base_path == sample_config_dir
    
    def test_load_config(self, sample_config_dir):
        """Test loading configuration from file."""
        config = Config(sample_config_dir)
        loaded_config = config.load_config()
        
        # Check that config has expected structure and values
        assert "organization" in loaded_config
        assert "auto_categorization" in loaded_config["organization"]
        assert "work" in loaded_config["organization"]["auto_categorization"]
        assert "office" in loaded_config["organization"]["auto_categorization"]["work"]
        
        assert "logging" in loaded_config
        assert loaded_config["logging"]["level"] == "INFO"
        
        assert "storage" in loaded_config
        assert loaded_config["storage"]["data_path"] == "custom_data"
    
    def test_load_conventions(self, sample_config_dir):
        """Test loading conventions from file."""
        config = Config(sample_config_dir)
        conventions = config.load_conventions()
        
        # Check that conventions have expected structure and values
        assert "file_naming" in conventions
        assert "notes" in conventions["file_naming"]
        assert conventions["file_naming"]["notes"] == "note-{timestamp}.md"
        
        assert "content_types" in conventions
        assert "note" in conventions["content_types"]
        assert "extensions" in conventions["content_types"]["note"]
        assert ".md" in conventions["content_types"]["note"]["extensions"]
    
    def test_default_config(self):
        """Test that default configuration is returned when file not found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with a directory that doesn't have config files
            config = Config(Path(temp_dir))
            default_config = config.load_config()
            
            # Check that default config is returned
            assert "organization" in default_config
            assert "auto_categorization" in default_config["organization"]
            assert "work" in default_config["organization"]["auto_categorization"]
            assert "logging" in default_config
            assert "storage" in default_config
    
    def test_default_conventions(self):
        """Test that default conventions are returned when file not found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with a directory that doesn't have config files
            config = Config(Path(temp_dir))
            default_conventions = config.load_conventions()
            
            # Check that default conventions are returned
            assert "file_naming" in default_conventions
            assert "content_types" in default_conventions
    
    def test_env_overrides(self, sample_config_dir, monkeypatch):
        """Test that environment variables override config values."""
        # Set environment variables
        monkeypatch.setenv("KB_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("KB_DATA_PATH", "/custom/path")
        
        config = Config(sample_config_dir)
        loaded_config = config.load_config()
        
        # Check that environment variables override file values
        assert loaded_config["logging"]["level"] == "DEBUG"
        assert loaded_config["storage"]["data_path"] == "/custom/path"
    
    def test_env_overrides_with_defaults(self, monkeypatch):
        """Test that environment variables create new sections in default config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set environment variables
            monkeypatch.setenv("KB_LOG_LEVEL", "DEBUG")
            monkeypatch.setenv("KB_DATA_PATH", "/custom/path")
            
            # Create config with a directory that doesn't have config files
            config = Config(Path(temp_dir))
            loaded_config = config.load_config()
            
            # Check that environment variables override default values
            assert loaded_config["logging"]["level"] == "DEBUG"
            assert loaded_config["storage"]["data_path"] == "/custom/path" 