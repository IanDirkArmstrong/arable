"""Tests for Monday.com API integration"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime

from src.monday_automation.monday_api import MondayAPI, MondayAPIError


class TestMondayAPI:
    """Test Monday.com API client functionality"""

    @pytest.fixture
    def api_client(self, mock_logger):
        """Create a Monday API client for testing"""
        return MondayAPI(api_token="test_token_123", logger=mock_logger)

    @patch("src.monday_automation.monday_api.requests")
    @patch("src.monday_automation.monday_api.time.sleep")
    def test_make_request_success(self, mock_sleep, mock_requests, api_client):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"test": "success"}}
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        result = api_client.make_request("query { test }")

        assert result == {"data": {"test": "success"}}
        mock_requests.post.assert_called_once()
        mock_sleep.assert_called_once_with(0.2)  # Rate limiting

    @patch("src.monday_automation.monday_api.requests")
    def test_make_request_graphql_errors(self, mock_requests, api_client):
        """Test API request with GraphQL errors"""
        mock_response = Mock()
        mock_response.json.return_value = {"errors": [{"message": "Test error"}]}
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        with pytest.raises(MondayAPIError, match="GraphQL errors"):
            api_client.make_request("query { test }")

    @patch("src.monday_automation.monday_api.requests")
    def test_make_request_http_error(self, mock_requests, api_client):
        """Test API request with HTTP error"""
        import requests

        mock_requests.post.side_effect = requests.exceptions.RequestException(
            "HTTP Error"
        )

        with pytest.raises(MondayAPIError, match="API request failed"):
            api_client.make_request("query { test }")

    @patch("src.monday_automation.monday_api.requests")
    @patch("src.monday_automation.monday_api.time.sleep")
    def test_create_master_item_success(
        self, mock_sleep, mock_requests, api_client, sample_projects
    ):
        """Test successful master item creation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {"create_item": {"id": "999", "name": "Test Item"}}
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        column_mapping = {
            "project_number": "col1",
            "status": "status",
            "start_date": "col4",
        }

        item_id = api_client.create_master_item(
            "123456789", sample_projects[0], column_mapping
        )

        assert item_id == "999"
        mock_requests.post.assert_called_once()

        # Check that the request includes proper column values
        call_args = mock_requests.post.call_args
        request_data = call_args[1]["json"]
        variables = request_data["variables"]
        column_values = json.loads(variables["column_values"])

        assert column_values["col1"] == "12345"  # Project number
        assert "status" in column_values  # Status should be set

    @patch("src.monday_automation.monday_api.requests")
    @patch("src.monday_automation.monday_api.time.sleep")
    def test_create_project_board_success(
        self, mock_sleep, mock_requests, api_client, sample_projects
    ):
        """Test successful project board creation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {"duplicate_board": {"board": {"id": "888", "name": "Test Board"}}}
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        board_id = api_client.create_project_board(
            "template_123", "folder_456", sample_projects[0]
        )

        assert board_id == "888"
        mock_requests.post.assert_called_once()

    @patch("src.monday_automation.monday_api.requests")
    @patch("src.monday_automation.monday_api.time.sleep")
    def test_add_milestone_item_success(
        self, mock_sleep, mock_requests, api_client, sample_milestones
    ):
        """Test successful milestone item creation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {"create_item": {"id": "777", "name": "Kickoff"}}
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        column_mapping = {
            "timeline": "col5",
            "duration": "col6",
            "phase": "col7",
            "master_link": "col8",
        }
        phase_mapping = {"Kickoff": 1}
        group_mapping = {"Kickoff": "topics"}

        item_id = api_client.add_milestone_item(
            "board_123",
            sample_milestones[0],
            "master_999",
            column_mapping,
            phase_mapping,
            group_mapping,
        )

        assert item_id == "777"
        mock_requests.post.assert_called_once()

    def test_parse_date_string_valid_formats(self, api_client):
        """Test parsing various valid date formats"""
        # Test ISO format
        result = api_client._parse_date_string("2025-01-15")
        assert result == "2025-01-15"

        # Test US format
        result = api_client._parse_date_string("01/15/2025")
        assert result == "2025-01-15"

        # Test datetime string
        result = api_client._parse_date_string("2025-01-15 10:30:00")
        assert result == "2025-01-15"

    def test_parse_date_string_invalid_formats(self, api_client):
        """Test parsing invalid date formats"""
        # Test invalid date
        result = api_client._parse_date_string("invalid-date")
        assert result is None

        # Test empty string
        result = api_client._parse_date_string("")
        assert result is None

        # Test None
        result = api_client._parse_date_string(None)
        assert result is None
