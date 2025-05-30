"""Monday.com API wrapper for project automation"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from dateutil.parser import parse as parse_date


class MondayAPIError(Exception):
    """Monday.com API-related errors"""

    pass


class MondayAPI:
    """Monday.com API client for project automation"""

    def __init__(self, api_token: str, logger: logging.Logger):
        """
        Initialize Monday API client

        Args:
            api_token: Monday.com API token
            logger: Logger instance
        """
        self.api_token = api_token
        self.api_url = "https://api.monday.com/v2"
        self.headers = {"Authorization": api_token, "Content-Type": "application/json"}
        self.logger = logger

    def make_request(self, query: str, variables: Dict = None) -> Dict:
        """
        Make GraphQL request to Monday API with rate limiting

        Args:
            query: GraphQL query string
            variables: Optional query variables

        Returns:
            API response data

        Raises:
            MondayAPIError: If request fails
        """
        data = {"query": query}
        if variables:
            data["variables"] = variables

        try:
            response = requests.post(
                self.api_url, json=data, headers=self.headers, timeout=30
            )
            response.raise_for_status()

            result = response.json()

            # Check for GraphQL errors
            if "errors" in result:
                error_msg = "; ".join([str(err) for err in result["errors"]])
                raise MondayAPIError(f"GraphQL errors: {error_msg}")

            # Rate limiting - Monday allows ~300 requests/minute
            time.sleep(0.2)  # 200ms between requests = 300/min max

            return result

        except requests.exceptions.RequestException as e:
            raise MondayAPIError(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise MondayAPIError(f"Invalid JSON response: {e}")

    def create_master_item(
        self, board_id: str, project: Dict, column_mapping: Dict[str, str]
    ) -> str:
        """
        Create item in master board

        Args:
            board_id: Master board ID
            project: Project data dictionary
            column_mapping: Column ID mappings

        Returns:
            Created item ID
        """
        project_name = (
            f"{project['CustomerShortname']} - "
            f"{project['ProjectName']} - "
            f"{project['ProjectNumber']}"
        )

        query = """
        mutation ($board_id: ID!, $item_name: String!, $column_values: JSON!) {
            create_item (
                board_id: $board_id, 
                item_name: $item_name, 
                column_values: $column_values
            ) {
                id
                name
            }
        }
        """

        column_values = self._build_master_column_values(project, column_mapping)

        variables = {
            "board_id": board_id,
            "item_name": project_name,
            "column_values": json.dumps(column_values),
        }

        self.logger.debug(f"Creating master item: {project_name}")
        self.logger.debug(f"Column values: {json.dumps(column_values, indent=2)}")

        result = self.make_request(query, variables)

        item_id = result["data"]["create_item"]["id"]
        self.logger.info(f"Created master board item: {project_name} (ID: {item_id})")

        return item_id

    def create_project_board(
        self, template_id: str, folder_id: str, project: Dict
    ) -> str:
        """
        Create project board from template

        Args:
            template_id: Template board ID
            folder_id: Target folder ID
            project: Project data dictionary

        Returns:
            Created board ID
        """
        board_name = (
            f"{project['CustomerShortname']} - "
            f"{project['ProjectName']} - "
            f"{project['ProjectNumber']}"
        )

        query = """
        mutation ($board_name: String!, $template_id: ID!, $folder_id: ID!) {
            duplicate_board (
                board_id: $template_id, 
                board_name: $board_name, 
                duplicate_type: duplicate_board_with_structure,
                folder_id: $folder_id
            ) {
                board {
                    id
                    name
                }
            }
        }
        """

        variables = {
            "board_name": board_name,
            "template_id": template_id,
            "folder_id": folder_id,
        }

        result = self.make_request(query, variables)

        board_id = result["data"]["duplicate_board"]["board"]["id"]
        self.logger.info(f"Created project board: {board_name} (ID: {board_id})")

        return board_id

    def add_milestone_item(
        self,
        board_id: str,
        milestone: Dict,
        master_item_id: str,
        column_mapping: Dict[str, str],
        phase_mapping: Dict[str, int],
        group_mapping: Dict[str, str],
    ) -> str:
        """
        Add milestone as item to project board

        Args:
            board_id: Project board ID
            milestone: Milestone data dictionary
            master_item_id: Master board item ID to link to
            column_mapping: Project board column mappings
            phase_mapping: Milestone type to phase ID mapping
            group_mapping: Milestone type to group ID mapping

        Returns:
            Created milestone item ID
        """
        milestone_name = milestone["MileStoneType"]
        group_id = group_mapping.get(milestone_name)

        query = """
        mutation ($board_id: ID!, $group_id: String, $item_name: String!, $column_values: JSON!) {
            create_item (
                board_id: $board_id, 
                group_id: $group_id, 
                item_name: $item_name, 
                column_values: $column_values
            ) {
                id
                name
            }
        }
        """

        column_values = self._build_milestone_column_values(
            milestone, master_item_id, column_mapping, phase_mapping
        )

        variables = {
            "board_id": board_id,
            "group_id": group_id,
            "item_name": milestone_name,
            "column_values": json.dumps(column_values),
        }

        if group_id:
            self.logger.debug(
                f"Adding milestone '{milestone_name}' to group '{group_id}'"
            )
        else:
            self.logger.debug(f"Adding milestone '{milestone_name}' to default group")

        result = self.make_request(query, variables)

        item_id = result["data"]["create_item"]["id"]
        self.logger.info(f"Added milestone: {milestone_name} to board {board_id}")

        return item_id

    def _build_master_column_values(
        self, project: Dict, column_mapping: Dict[str, str]
    ) -> Dict[str, Any]:
        """Build column values for master board item"""
        column_values = {}

        # Project number
        if project.get("ProjectNumber"):
            column_values[column_mapping["project_number"]] = str(
                project["ProjectNumber"]
            )

        # Status - set to Active if Current
        if project.get("Status") == "Current":
            column_values[column_mapping["status"]] = {
                "label": "Active"
            }  # Use label instead of index

        # Start date - handle various formats
        if project.get("DateCreated"):
            date_str = self._parse_date_string(project["DateCreated"])
            if date_str:
                column_values[column_mapping["start_date"]] = {"date": date_str}

        # Customer - if available - Causing errors
        # if project.get('CustomerShortname') and 'customer' in column_mapping:
        #     column_values[column_mapping["customer"]] = str(project['CustomerShortname'])

        return column_values

    def _build_milestone_column_values(
        self,
        milestone: Dict,
        master_item_id: str,
        column_mapping: Dict[str, str],
        phase_mapping: Dict[str, int],
    ) -> Dict[str, Any]:
        """Build column values for milestone item"""
        column_values = {}

        # Timeline (start and end dates)
        if milestone.get("DateOfMilestone") and milestone.get("EndDate"):
            start_date = self._parse_date_string(milestone["DateOfMilestone"])
            end_date = self._parse_date_string(milestone["EndDate"])

            if start_date and end_date:
                column_values[column_mapping["timeline"]] = {
                    "from": start_date,
                    "to": end_date,
                }
            elif start_date:  # Handle case with only start date
                column_values[column_mapping["timeline"]] = {
                    "from": start_date,
                    "to": start_date,  # Use same date for single-day milestone
                }

        # Duration
        if milestone.get("Duration"):
            try:
                duration = float(milestone["Duration"])
                if duration > 0:  # Only set positive durations
                    column_values[column_mapping["duration"]] = duration
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid duration: {milestone['Duration']}")

        # Phase based on milestone type
        milestone_type = milestone["MileStoneType"]
        phase_id = phase_mapping.get(milestone_type)
        if phase_id is not None:
            column_values[column_mapping["phase"]] = {"index": phase_id}

        # Link to master board item
        try:
            column_values[column_mapping["master_link"]] = {
                "item_ids": [int(master_item_id)]
            }
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid master item ID: {master_item_id}")

        return column_values

    def _parse_date_string(self, date_input: Any) -> Optional[str]:
        """
        Parse various date formats into YYYY-MM-DD string

        Args:
            date_input: Date in various formats

        Returns:
            Formatted date string or None if parsing fails
        """
        if not date_input:
            return None

        date_str = str(date_input).strip()
        if not date_str:
            return None

        try:
            # Try parsing with dateutil (handles many formats)
            parsed_date = parse_date(date_str)
            return parsed_date.strftime("%Y-%m-%d")
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Could not parse date '{date_str}': {e}")
            return None


def make_request_with_retry(
    self, query: str, variables: Dict = None, max_retries: int = 3
) -> Dict:
    """
    Make GraphQL request with retry logic

    Args:
        query: GraphQL query string
        variables: Optional query variables
        max_retries: Maximum number of retry attempts

    Returns:
        API response data

    Raises:
        MondayAPIError: If all retries fail
    """
    import time
    import random

    for attempt in range(max_retries + 1):
        try:
            return self.make_request(query, variables)

        except MondayAPIError as e:
            if attempt == max_retries:
                raise  # Last attempt failed

            # Check if it's a rate limit error
            if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                # Exponential backoff with jitter
                wait_time = (2**attempt) + random.uniform(0, 1)
                self.logger.warning(
                    f"Rate limited, retrying in {wait_time:.1f}s (attempt {attempt + 1})"
                )
                time.sleep(wait_time)
            else:
                # For other errors, shorter wait
                time.sleep(1)
                self.logger.warning(f"API error, retrying (attempt {attempt + 1}): {e}")
