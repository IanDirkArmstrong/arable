"""Logging configuration for Monday automation"""

import logging
import os
from typing import Optional


def setup_logger(
    name: str = "monday_automation",
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
) -> logging.Logger:
    """
    Set up logger with file and console handlers

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        console: Whether to log to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
