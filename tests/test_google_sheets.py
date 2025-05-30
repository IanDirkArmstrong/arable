"""Tests for Google Sheets integration"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from monday_automation.google_sheets import GoogleSheetsClient, GoogleSheetsError


class TestGoogleSheetsClient:
    """Test Google Sheets client functionality"""

    @pytest.fixture
    def client(self, mock_logger):
        """Create a Google Sheets client for testing"""
        return GoogleSheetsClient(
            credentials_path="test_creds.json",
            sheet_name="Test Sheet",
            logger=mock_logger,
        )

    @patch("src.monday_automation.google_sheets.ServiceAccountCredentials")
    @patch("src.monday_automation.google_sheets.gspread")
    def test_connect_success(self, mock_gspread, mock_creds, client):
        """Test successful connection to Google Sheets"""
        mock_client = Mock()
        mock_workbook = Mock()
        mock_gspread.authorize.return_value = mock_client
        mock_client.open.return_value = mock_workbook

        client.connect()

        assert client.client == mock_client
        assert client.workbook == mock_workbook
        mock_creds.from_json_keyfile_name.assert_called_once()
        mock_gspread.authorize.assert_called_once()

    @patch("src.monday_automation.google_sheets.ServiceAccountCredentials")
    def test_connect_credentials_not_found(self, mock_creds, client):
        """Test connection with missing credentials file"""
        mock_creds.from_json_keyfile_name.side_effect = FileNotFoundError()

        with pytest.raises(GoogleSheetsError, match="Credentials file not found"):
            client.connect()

    @patch("src.monday_automation.google_sheets.ServiceAccountCredentials")
    @patch("src.monday_automation.google_sheets.gspread")
    def test_connect_spreadsheet_not_found(self, mock_gspread, mock_creds, client):
        """Test connection with non-existent spreadsheet"""
        import gspread

        mock_client = Mock()
        mock_gspread.authorize.return_value = mock_client
        mock_client.open.side_effect = gspread.SpreadsheetNotFound()

        with pytest.raises(GoogleSheetsError, match="Spreadsheet not found"):
            client.connect()

    def test_read_projects_success(self, client, sample_projects):
        """Test successful reading of projects"""
        # Setup mock workbook
        mock_worksheet = Mock()
        mock_worksheet.get_all_records.return_value = sample_projects + [
            {"ProjectNumber": ""}
        ]  # Include empty row

        client.workbook = Mock()
        client.workbook.worksheet.return_value = mock_worksheet

        projects = client.read_projects()

        assert len(projects) == 2  # Empty row should be filtered out
        assert projects[0]["ProjectNumber"] == "12345"
        assert projects[1]["ProjectNumber"] == "67890"

    def test_read_projects_worksheet_not_found(self, client):
        """Test reading projects from non-existent worksheet"""
        import gspread

        client.workbook = Mock()
        client.workbook.worksheet.side_effect = gspread.WorksheetNotFound()

        with pytest.raises(GoogleSheetsError, match="Worksheet 'Projects' not found"):
            client.read_projects()

    def test_read_projects_not_connected(self, client):
        """Test reading projects when not connected"""
        with pytest.raises(GoogleSheetsError, match="Not connected"):
            client.read_projects()

    def test_read_milestones_success(self, client, sample_milestones):
        """Test successful reading of milestones"""
        # Add milestone with trailing spaces to test cleaning
        milestones_with_spaces = sample_milestones.copy()
        milestones_with_spaces.append(
            {
                "ProjectNumber": "12345",
                "MileStoneType": "Kickoff ",  # Trailing space
                "DateOfMilestone": "2025-01-20",
                "EndDate": "2025-01-21",
                "Duration": "1",
            }
        )

        mock_worksheet = Mock()
        mock_worksheet.get_all_records.return_value = milestones_with_spaces

        client.workbook = Mock()
        client.workbook.worksheet.return_value = mock_worksheet

        milestones = client.read_milestones()

        assert len(milestones) == 4
        # Check that trailing spaces are cleaned
        kickoff_milestones = [m for m in milestones if m["MileStoneType"] == "Kickoff"]
        assert len(kickoff_milestones) == 2

    def test_read_data_success(self, client, sample_projects, sample_milestones):
        """Test reading both projects and milestones"""
        mock_projects_worksheet = Mock()
        mock_projects_worksheet.get_all_records.return_value = sample_projects

        mock_milestones_worksheet = Mock()
        mock_milestones_worksheet.get_all_records.return_value = sample_milestones

        client.workbook = Mock()
        client.workbook.worksheet.side_effect = [
            mock_projects_worksheet,
            mock_milestones_worksheet,
        ]

        projects, milestones = client.read_data()

        assert len(projects) == 2
        assert len(milestones) == 3
        assert client.workbook.worksheet.call_count == 2
