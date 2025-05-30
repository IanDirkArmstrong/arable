"""Tests for logging functionality"""

import pytest
import tempfile
import os
from pathlib import Path
import logging

from src.monday_automation.logger import setup_logger


class TestLogger:
    """Test logging setup functionality"""

    def test_setup_basic_logger(self):
        """Test setting up a basic logger"""
        logger = setup_logger(name="test_logger", level="INFO")

        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1  # Console handler only

    def test_setup_logger_with_file(self):
        """Test setting up logger with file output"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name

        try:
            logger = setup_logger(
                name="test_logger", level="DEBUG", log_file=log_file, console=True
            )

            assert logger.level == logging.DEBUG
            assert len(logger.handlers) == 2  # Console + file handlers

            # Test logging to file
            logger.info("Test message")

            with open(log_file, "r") as f:
                content = f.read()
                assert "Test message" in content

        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_setup_logger_file_only(self):
        """Test setting up logger with file output only"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name

        try:
            logger = setup_logger(
                name="test_logger", level="WARNING", log_file=log_file, console=False
            )

            assert logger.level == logging.WARNING
            assert len(logger.handlers) == 1  # File handler only

        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_setup_logger_creates_directory(self):
        """Test that logger creates log directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "logs", "test.log")

            logger = setup_logger(name="test_logger", log_file=log_file)

            # Directory should be created
            assert os.path.exists(os.path.dirname(log_file))

            # Test logging
            logger.info("Test message")
            assert os.path.exists(log_file)

    def test_logger_handler_cleanup(self):
        """Test that existing handlers are cleared"""
        logger = setup_logger(name="test_cleanup")
        initial_handler_count = len(logger.handlers)

        # Setup again - should clear existing handlers
        logger = setup_logger(name="test_cleanup")
        assert len(logger.handlers) == initial_handler_count
