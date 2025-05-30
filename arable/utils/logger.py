"""Logging configuration for ARABLE
Migrated from src/monday_automation/logger.py
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "arable",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup logging configuration for ARABLE

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        console_output: Whether to output to console

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
