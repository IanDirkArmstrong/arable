"""Pytest configuration and shared fixtures"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
import yaml
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from monday_automation.config import Config, MondayConfig, GoogleSheetsConfig


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    config_data = {
        "monday": {
            "api_token": "test_token_123",
            "master_board_id": "123456789",
            "template_board_id": "987654321",
            "active_projects_folder_id": "456789",
            "master_columns": {
                "project_number": "col1",
                "project_milestones": "col2",
                "customer": "col3",
                "start_date": "col4",
                "status": "status",
            },
            "project_board_columns": {
                "timeline": "col5",
                "duration": "col6",
                "phase": "col7",
                "status": "status",
                "master_link": "col8",
            },
        },
        "google_sheets": {
            "credentials_path": "test_creds.json",
            "sheet_name": "Test Sheet",
        },
        "milestone_mappings": {
            "phase": {"Kickoff": 1, "Testing": 4},
            "groups": {"Kickoff": "topics", "Testing": "group_123"},
        },
        "testing": {"test_project_number": None, "enabled": True},
        "logging": {"level": "INFO", "file": "test.log"},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        yield f.name

    os.unlink(f.name)


@pytest.fixture
def temp_credentials_file():
    """Create a temporary credentials file"""
    creds_data = {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        import json

        json.dump(creds_data, f)
        yield f.name

    os.unlink(f.name)


@pytest.fixture
def sample_projects():
    """Sample project data for testing"""
    return [
        {
            "ProjectNumber": "12345",
            "ProjectName": "Test Project Alpha",
            "CustomerShortname": "ACME",
            "Status": "Current",
            "DateCreated": "2025-01-15",
        },
        {
            "ProjectNumber": "67890",
            "ProjectName": "Test Project Beta",
            "CustomerShortname": "BETA",
            "Status": "Inactive",
            "DateCreated": "2025-02-01",
        },
    ]


@pytest.fixture
def sample_milestones():
    """Sample milestone data for testing"""
    return [
        {
            "ProjectNumber": "12345",
            "MileStoneType": "Kickoff",
            "DateOfMilestone": "2025-01-20",
            "EndDate": "2025-01-21",
            "Duration": "1",
        },
        {
            "ProjectNumber": "12345",
            "MileStoneType": "Testing",
            "DateOfMilestone": "2025-03-01",
            "EndDate": "2025-03-15",
            "Duration": "14",
        },
        {
            "ProjectNumber": "67890",
            "MileStoneType": "Kickoff",
            "DateOfMilestone": "2025-02-05",
            "EndDate": "2025-02-06",
            "Duration": "1",
        },
    ]


@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    return Mock()


@pytest.fixture
def mock_requests():
    """Mock requests module for API testing"""
    mock = Mock()
    mock.post.return_value.json.return_value = {
        "data": {
            "create_item": {"id": "999", "name": "Test Item"},
            "duplicate_board": {"board": {"id": "888", "name": "Test Board"}},
        }
    }
    mock.post.return_value.raise_for_status.return_value = None
    return mock
