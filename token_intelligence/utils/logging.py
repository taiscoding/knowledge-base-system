#!/usr/bin/env python3
"""
Logging Utilities
Consistent logging setup for the token intelligence system.
"""

import os
import logging
import sys
from pathlib import Path
from typing import Optional

# Initialize logging configuration
_loggers = {}


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger by name.
    
    Args:
        name: Name of the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    if name in _loggers:
        return _loggers[name]
    
    # Create new logger
    logger = logging.getLogger(name)
    
    # Only configure if it's a new logger
    if not logger.handlers:
        # Default log level (can be overridden by environment variable)
        log_level_name = os.environ.get('TOKEN_INTELLIGENCE_LOG_LEVEL', 'INFO')
        log_level = getattr(logging, log_level_name.upper(), logging.INFO)
        
        logger.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler
        logger.addHandler(console_handler)
    
    _loggers[name] = logger
    return logger


def setup_file_logging(log_dir: str = "./logs", log_level: str = "INFO"):
    """
    Set up file-based logging for the entire application.
    
    Args:
        log_dir: Directory to store log files
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # Create file handler
    log_file = log_path / "token_intelligence.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to the root logger
    root_logger.addHandler(file_handler)
    
    # Log initialization message
    root_logger.info(f"File logging initialized at {log_file}")


def set_log_level(level: str):
    """
    Set the log level for all loggers.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Update root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(log_level)
    
    # Update all existing loggers
    for logger in _loggers.values():
        logger.setLevel(log_level)
        for handler in logger.handlers:
            handler.setLevel(log_level)


def log_exception(logger: logging.Logger, exception: Exception, context: Optional[str] = None):
    """
    Log an exception with context information.
    
    Args:
        logger: Logger instance
        exception: Exception to log
        context: Optional context information
    """
    if context:
        logger.error(f"Exception in {context}: {str(exception)}", exc_info=True)
    else:
        logger.error(f"Exception: {str(exception)}", exc_info=True) 