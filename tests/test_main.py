"""Tests for main automation logic"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.monday_automation.main import ProjectAutomation


class TestProjectAutomation:
    """Test main project automation functionality"""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration"""
        config = Mock()
        config.monday.master_board_id = "123456789"
        config.monday.template_board_id = "987654321"
        config.monday.active_projects_folder_id = "456789"
        config.monday.master_columns = {"project_number": "col1"}
        config.monday.project_board_columns = {"timeline": "col5"}
        config.milestone_mappings = {
            "phase": {"Kickoff": 1},
            "groups": {"Kickoff": "topics"},
        }
        config.google_sheets.credentials_path = "test_creds.json"
        config.google_sheets.sheet_name = "Test Sheet"
        config.logging = {"level": "INFO", "file": "test.log"}
        return config

    @patch("src.monday_automation.main.load_config")
    @patch("src.monday_automation.main.validate_config")
    @patch("src.monday_automation.main.setup_logger")
    @patch("src.monday_automation.main.GoogleSheetsClient")
    @patch("src.monday_automation.main.MondayAPI")
    def test_initialization_success(
        self,
        mock_monday_api,
        mock_sheets_client,
        mock_logger,
        mock_validate,
        mock_load_config,
        mock_config,
    ):
        """Test successful automation initialization"""
        mock_load_config.return_value = mock_config
        mock_logger.return_value = Mock()

        automation = ProjectAutomation()

        mock_load_config.assert_called_once()
        mock_validate.assert_called_once_with(mock_config)
        mock_logger.assert_called_once()
        mock_sheets_client.assert_called_once()
        mock_monday_api.assert_called_once()

    @patch("src.monday_automation.main.load_config")
    def test_initialization_config_error(self, mock_load_config):
        """Test initialization with configuration error"""
        from src.monday_automation.config import ConfigError

        mock_load_config.side_effect = ConfigError("Test config error")

        with pytest.raises(SystemExit):
            ProjectAutomation()

    @patch("src.monday_automation.main.load_config")
    @patch("src.monday_automation.main.validate_config")
    @patch("src.monday_automation.main.setup_logger")
    @patch("src.monday_automation.main.GoogleSheetsClient")
    @patch("src.monday_automation.main.MondayAPI")
    def test_process_project_success(
        self,
        mock_monday_api_class,
        mock_sheets_client_class,
        mock_logger,
        mock_validate,
        mock_load_config,
        mock_config,
        sample_projects,
        sample_milestones,
    ):
        """Test successful project processing"""
        mock_load_config.return_value = mock_config
        mock_logger.return_value = Mock()

        # Setup mock Monday API
        mock_monday_api = Mock()
        mock_monday_api.create_master_item.return_value = "master_999"
        mock_monday_api.create_project_board.return_value = "board_888"
        mock_monday_api.add_milestone_item.return_value = "milestone_777"
        mock_monday_api_class.return_value = mock_monday_api

        automation = ProjectAutomation()

        # Get milestones for the first project
        project_milestones = [
            m for m in sample_milestones if m["ProjectNumber"] == "12345"
        ]

        result = automation.process_project(sample_projects[0], project_milestones)

        assert result is True
        mock_monday_api.create_master_item.assert_called_once()
        mock_monday_api.create_project_board.assert_called_once()
        assert (
            mock_monday_api.add_milestone_item.call_count == 2
        )  # Two milestones for project 12345

    @patch("src.monday_automation.main.load_config")
    @patch("src.monday_automation.main.validate_config")
    @patch("src.monday_automation.main.setup_logger")
    @patch("src.monday_automation.main.GoogleSheetsClient")
    @patch("src.monday_automation.main.MondayAPI")
    def test_process_project_api_error(
        self,
        mock_monday_api_class,
        mock_sheets_client_class,
        mock_logger,
        mock_validate,
        mock_load_config,
        mock_config,
        sample_projects,
        sample_milestones,
    ):
        """Test project processing with API error"""
        from src.monday_automation.monday_api import MondayAPIError

        mock_load_config.return_value = mock_config
        mock_logger.return_value = Mock()

        # Setup mock Monday API with error
        mock_monday_api = Mock()
        mock_monday_api.create_master_item.side_effect = MondayAPIError("API Error")
        mock_monday_api_class.return_value = mock_monday_api

        automation = ProjectAutomation()

        project_milestones = [
            m for m in sample_milestones if m["ProjectNumber"] == "12345"
        ]

        result = automation.process_project(sample_projects[0], project_milestones)

        assert result is False

    @patch("src.monday_automation.main.load_config")
    @patch("src.monday_automation.main.validate_config")
    @patch("src.monday_automation.main.setup_logger")
    @patch("src.monday_automation.main.GoogleSheetsClient")
    @patch("src.monday_automation.main.MondayAPI")
    def test_run_full_workflow(
        self,
        mock_monday_api_class,
        mock_sheets_client_class,
        mock_logger,
        mock_validate,
        mock_load_config,
        mock_config,
        sample_projects,
        sample_milestones,
    ):
        """Test full automation workflow"""
        mock_load_config.return_value = mock_config
        mock_logger.return_value = Mock()

        # Setup mock Google Sheets client
        mock_sheets_client = Mock()
        mock_sheets_client.read_data.return_value = (sample_projects, sample_milestones)
        mock_sheets_client_class.return_value = mock_sheets_client

        # Setup mock Monday API
        mock_monday_api = Mock()
        mock_monday_api.create_master_item.return_value = "master_999"
        mock_monday_api.create_project_board.return_value = "board_888"
        mock_monday_api.add_milestone_item.return_value = "milestone_777"
        mock_monday_api_class.return_value = mock_monday_api

        automation = ProjectAutomation()
        automation.run()

        # Verify workflow steps
        mock_sheets_client.connect.assert_called_once()
        mock_sheets_client.read_data.assert_called_once()

        # Should process both projects
        assert mock_monday_api.create_master_item.call_count == 2
        assert mock_monday_api.create_project_board.call_count == 2

    @patch("src.monday_automation.main.load_config")
    @patch("src.monday_automation.main.validate_config")
    @patch("src.monday_automation.main.setup_logger")
    @patch("src.monday_automation.main.GoogleSheetsClient")
    @patch("src.monday_automation.main.MondayAPI")
    def test_run_with_test_project(
        self,
        mock_monday_api_class,
        mock_sheets_client_class,
        mock_logger,
        mock_validate,
        mock_load_config,
        mock_config,
        sample_projects,
        sample_milestones,
    ):
        """Test automation with specific test project"""
        mock_load_config.return_value = mock_config
        mock_logger.return_value = Mock()

        # Setup mock Google Sheets client
        mock_sheets_client = Mock()
        mock_sheets_client.read_data.return_value = (sample_projects, sample_milestones)
        mock_sheets_client_class.return_value = mock_sheets_client

        # Setup mock Monday API
        mock_monday_api = Mock()
        mock_monday_api.create_master_item.return_value = "master_999"
        mock_monday_api.create_project_board.return_value = "board_888"
        mock_monday_api.add_milestone_item.return_value = "milestone_777"
        mock_monday_api_class.return_value = mock_monday_api

        automation = ProjectAutomation()
        automation.run(test_project_number="12345")

        # Should only process the test project
        assert mock_monday_api.create_master_item.call_count == 1
        assert mock_monday_api.create_project_board.call_count == 1
