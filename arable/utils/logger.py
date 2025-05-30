"""Logging configuration for ARABLE
Migrated from src/monday_automation/logger.py with Rich integration
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console


def setup_logger(
    name: str = "arable",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    rich_tracebacks: bool = True
) -> logging.Logger:
    """
    Setup logging configuration for ARABLE with Rich integration

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        console_output: Whether to output to console
        rich_tracebacks: Whether to use Rich for tracebacks

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Prevent propagation to root logger to avoid duplicates
    logger.propagate = False

    # Rich console handler for beautiful output
    if console_output:
        console = Console(stderr=True)  # Use stderr for logs to not interfere with CLI output
        rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_level=True,
            show_path=False,
            rich_tracebacks=rich_tracebacks,
            tracebacks_show_locals=level.upper() == "DEBUG"
        )
        rich_handler.setLevel(getattr(logging, level.upper()))
        logger.addHandler(rich_handler)

    # File handler for persistence
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create formatter for file output
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def set_debug_logging():
    """Enable debug logging for all ARABLE components"""
    # Set debug for all arable loggers
    for logger_name in ['arable', 'arable.cli', 'arable.integrations', 'arable.agents']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        
        # Update handler levels
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
    
    # Also set root logger to debug to catch everything
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
