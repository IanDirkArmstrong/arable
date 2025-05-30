"""Integration tests for the complete workflow"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
import yaml
import json

from src.monday_automation.main import ProjectAutomation


class TestIntegration:
    """Integration tests for complete workflows"""

    @pytest.fixture
    def integration_config(self):
        """Create a complete configuration for integration testing"""
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
                "phase": {"Kickoff": 1, "Testing": 4, "Delivery": 8},
                "groups": {
                    "Kickoff": "topics",
                    "Testing": "group_123",
                    "Delivery": "group_456",
                },
            },
            "testing": {"test_project_number": None, "enabled": True},
            "logging": {"level": "INFO", "file": "test.log"},
        }

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_file = f.name

        # Create temporary credentials file
        creds_data = {
            "type": "service_account",
            "project_id": "test-project",
            "client_email": "test@test-project.iam.gserviceaccount.com",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(creds_data, f)
            creds_file = f.name

        # Update config to use actual credentials file path
        config_data["google_sheets"]["credentials_path"] = creds_file
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        yield config_file, creds_file

        # Cleanup
        os.unlink(config_file)
        os.unlink(creds_file)

    @patch("src.monday_automation.google_sheets.ServiceAccountCredentials")
    @patch("src.monday_automation.google_sheets.gspread")
    @patch("src.monday_automation.monday_api.requests")
    @patch("src.monday_automation.monday_api.time.sleep")
    def test_end_to_end_workflow(
        self,
        mock_sleep,
        mock_requests,
        mock_gspread,
        mock_creds,
        integration_config,
        sample_projects,
        sample_milestones,
    ):
        """Test complete end-to-end workflow"""
        config_file, creds_file = integration_config

        # Setup Google Sheets mocks
        mock_client = Mock()
        mock_workbook = Mock()
        mock_gspread.authorize.return_value = mock_client
        mock_client.open.return_value = mock_workbook

        # Setup worksheets
        mock_projects_worksheet = Mock()
        mock_projects_worksheet.get_all_records.return_value = sample_projects

        mock_milestones_worksheet = Mock()
        mock_milestones_worksheet.get_all_records.return_value = sample_milestones

        mock_workbook.worksheet.side_effect = [
            mock_projects_worksheet,
            mock_milestones_worksheet,
        ]

        # Setup Monday API mocks
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        # Different responses for different API calls
        responses = [
            {"data": {"create_item": {"id": "999", "name": "Master Item 1"}}},
            {"data": {"duplicate_board": {"board": {"id": "888", "name": "Board 1"}}}},
            {"data": {"create_item": {"id": "777", "name": "Milestone 1"}}},
            {"data": {"create_item": {"id": "776", "name": "Milestone 2"}}},
            {"data": {"create_item": {"id": "998", "name": "Master Item 2"}}},
            {"data": {"duplicate_board": {"board": {"id": "887", "name": "Board 2"}}}},
            {"data": {"create_item": {"id": "775", "name": "Milestone 3"}}},
        ]

        mock_response.json.side_effect = responses
        mock_requests.post.return_value = mock_response

        # Run automation
        automation = ProjectAutomation(config_file)
        automation.run()

        # Verify all steps were called
        mock_gspread.authorize.assert_called_once()
        mock_client.open.assert_called_once()

        # Should have made API calls for both projects
        expected_calls = 7  # 2 master items + 2 boards + 3 milestones
        assert mock_requests.post.call_count == expected_calls

    @patch("src.monday_automation.google_sheets.ServiceAccountCredentials")
    @patch("src.monday_automation.google_sheets.gspread")
    def test_google_sheets_error_handling(
        self, mock_gspread, mock_creds, integration_config
    ):
        """Test error handling when Google Sheets fails"""
        config_file, creds_file = integration_config

        # Setup Google Sheets to fail
        import gspread

        mock_client = Mock()
        mock_gspread.authorize.return_value = mock_client
        mock_client.open.side_effect = gspread.SpreadsheetNotFound()

        # Run automation - should exit with error
        automation = ProjectAutomation(config_file)

        with pytest.raises(SystemExit):
            automation.run()

    @patch("src.monday_automation.google_sheets.ServiceAccountCredentials")
    @patch("src.monday_automation.google_sheets.gspread")
    @patch("src.monday_automation.monday_api.requests")
    def test_monday_api_error_handling(
        self,
        mock_requests,
        mock_gspread,
        mock_creds,
        integration_config,
        sample_projects,
        sample_milestones,
    ):
        """Test error handling when Monday API fails"""
        config_file, creds_file = integration_config

        # Setup Google Sheets mocks
        mock_client = Mock()
        mock_workbook = Mock()
        mock_gspread.authorize.return_value = mock_client
        mock_client.open.return_value = mock_workbook

        mock_projects_worksheet = Mock()
        mock_projects_worksheet.get_all_records.return_value = sample_projects[
            :1
        ]  # Just one project

        mock_milestones_worksheet = Mock()
        mock_milestones_worksheet.get_all_records.return_value = sample_milestones[
            :1
        ]  # Just one milestone

        mock_workbook.worksheet.side_effect = [
            mock_projects_worksheet,
            mock_milestones_worksheet,
        ]

        # Setup Monday API to fail
        import requests

        mock_requests.post.side_effect = requests.exceptions.RequestException(
            "API Error"
        )

        # Run automation - should handle the error gracefully
        automation = ProjectAutomation(config_file)
        automation.run()  # Should not raise exception

        # Should have attempted API call
        mock_requests.post.assert_called()
