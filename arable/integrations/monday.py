"""Monday.com API integration for ARABLE
Migrated from src/monday_automation/monday_api.py
"""

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

    def __init__(self, api_token: str, logger: logging.Logger = None):
        """
        Initialize Monday API client

        Args:
            api_token: Monday.com API token
            logger: Logger instance (optional)
        """
        self.api_token = api_token
        self.api_url = "https://api.monday.com/v2"
        self.headers = {"Authorization": api_token, "Content-Type": "application/json"}
        
        # Use provided logger or create one with proper name
        if logger:
            self.logger = logger
        else:
            from ..utils.logger import setup_logger
            self.logger = setup_logger("arable.integrations.monday")

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
        all_milestones: List[Dict] = None,
        dependency_rules: Dict = None,
    ) -> str:
        """
        Add milestone as item to project board with smart dependencies

        Args:
            board_id: Project board ID
            milestone: Milestone data dictionary
            master_item_id: Master board item ID to link to
            column_mapping: Project board column mappings
            phase_mapping: Milestone type to phase ID mapping
            group_mapping: Milestone type to group ID mapping
            all_milestones: All milestones for this project (for dependency calculation)
            dependency_rules: Dependency rules from config

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
            milestone, master_item_id, column_mapping, phase_mapping, 
            all_milestones, dependency_rules
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
            column_values[column_mapping["status"]] = {"label": "Active"}

        # Start date - handle various formats
        if project.get("DateCreated"):
            date_str = self._parse_date_string(project["DateCreated"])
            if date_str:
                column_values[column_mapping["start_date"]] = {"date": date_str}

        return column_values

    def _calculate_milestone_dependencies(
        self, 
        current_milestone: Dict, 
        all_milestones: List[Dict], 
        dependency_rules: Dict
    ) -> List[int]:
        """
        Calculate smart dependencies for a milestone based on flexible business logic
        
        Args:
            current_milestone: The milestone we're calculating dependencies for
            all_milestones: All milestones in the project
            dependency_rules: Dependency rules from configuration
            
        Returns:
            List of Monday.com item IDs that this milestone depends on
        """
        current_type = current_milestone.get("MileStoneType")
        if not current_type:
            return []
            
        # Get available milestone types in this project
        available_milestones = {m.get("MileStoneType") for m in all_milestones if m.get("MileStoneType")}
        
        # Try workflow rules first (flexible chains)
        workflow_rules = dependency_rules.get("workflow_rules", {})
        dependency_candidates = workflow_rules.get(current_type, [])
        
        # Find the first available dependency from the chain
        found_dependencies = []
        for candidate in dependency_candidates:
            if candidate in available_milestones and candidate != current_type:
                found_dependencies.append(candidate)
                break  # Take the first (most preferred) available dependency
                
        # If no workflow dependencies found, try critical path fallback
        if not found_dependencies:
            critical_path = dependency_rules.get("critical_path", {})
            critical_candidates = critical_path.get(current_type, [])
            
            for candidate in critical_candidates:
                if candidate in available_milestones and candidate != current_type:
                    found_dependencies.append(candidate)
                    break
                    
        if found_dependencies:
            self.logger.info(
                f"Found flexible dependencies for {current_type}: {found_dependencies}"
            )
        else:
            self.logger.debug(
                f"No suitable dependencies found for {current_type} in available milestones: {list(available_milestones)}"
            )
            
        # Return empty for now - we'll resolve actual item IDs in the two-pass system
        return []
        
    def update_milestone_dependencies(
        self, 
        board_id: str, 
        milestones: List[Dict], 
        dependency_rules: Dict,
        column_mapping: Dict[str, str]
    ) -> int:
        """
        Update dependencies for all milestones after they've been created
        
        This is a two-pass approach:
        1. Create all milestone items first
        2. Update dependencies based on created item IDs
        
        Args:
            board_id: Monday.com board ID
            milestones: List of milestones with Monday item IDs
            dependency_rules: Dependency rules from configuration
            column_mapping: Column mappings including dependencies
            
        Returns:
            Number of dependencies updated
        """
        workflow_rules = dependency_rules.get("workflow_rules", {})
        dependencies_column = column_mapping.get("dependencies")
        
        if not dependencies_column:
            self.logger.warning("No dependencies column configured")
            return 0
            
        # Create lookup of milestone types to Monday item IDs
        milestone_lookup = {}
        for milestone in milestones:
            milestone_type = milestone.get("MileStoneType")
            monday_item_id = milestone.get("monday_item_id")
            if milestone_type and monday_item_id:
                milestone_lookup[milestone_type] = monday_item_id
                
        updated_count = 0
        
        # Update dependencies for each milestone
        for milestone in milestones:
            current_type = milestone.get("MileStoneType")
            current_item_id = milestone.get("monday_item_id")
            
            if not current_type or not current_item_id:
                continue
            
            # Get available milestone types in this project
            available_milestone_types = {m.get("MileStoneType") for m in milestones if m.get("MileStoneType")}
            
            # Try workflow rules first (flexible chains)
            workflow_rules = dependency_rules.get("workflow_rules", {})
            dependency_candidates = workflow_rules.get(current_type, [])
            
            # Find the first available dependency from the chain
            selected_dependency = None
            for candidate in dependency_candidates:
                if candidate in milestone_lookup and candidate != current_type:
                    selected_dependency = candidate
                    break  # Take the first (most preferred) available dependency
                    
            # If no workflow dependencies found, try critical path fallback
            if not selected_dependency:
                critical_path = dependency_rules.get("critical_path", {})
                critical_candidates = critical_path.get(current_type, [])
                
                for candidate in critical_candidates:
                    if candidate in milestone_lookup and candidate != current_type:
                        selected_dependency = candidate
                        break
            
            # Set the dependency if found
            if selected_dependency:
                dependency_item_ids = [int(milestone_lookup[selected_dependency])]
                
                self.logger.info(
                    f"Setting flexible dependency for {current_type}: {selected_dependency}"
                )
                
                # Update the Monday item with dependencies
                try:
                    self._update_item_dependencies(
                        current_item_id, dependencies_column, dependency_item_ids
                    )
                    updated_count += 1
                except Exception as e:
                    self.logger.error(
                        f"Failed to update dependencies for {current_type}: {e}"
                    )
                    
        return updated_count
        
    def get_board_columns(self, board_id: str) -> Dict[str, str]:
        """
        Get all columns for a board to help debug column IDs
        
        Args:
            board_id: Monday.com board ID
            
        Returns:
            Dictionary mapping column titles to column IDs
        """
        query = """
        query ($board_id: [ID!]) {
            boards(ids: $board_id) {
                columns {
                    id
                    title
                    type
                }
            }
        }
        """
        
        variables = {"board_id": [board_id]}
        
        try:
            result = self.make_request(query, variables)
            board = result["data"]["boards"][0]
            
            columns = {}
            self.logger.info(f"Board {board_id} columns:")
            for col in board["columns"]:
                columns[col["title"]] = col["id"]
                self.logger.info(f"  {col['title']} ({col['type']}): {col['id']}")
                
            return columns
            
        except Exception as e:
            self.logger.error(f"Failed to get board columns: {e}")
            return {}
        
    def _update_item_dependencies(
        self, 
        item_id: str, 
        dependencies_column: str, 
        dependency_item_ids: List[int]
    ) -> None:
        """
        Update dependencies for a specific Monday item
        
        Args:
            item_id: Monday.com item ID
            dependencies_column: Dependencies column ID
            dependency_item_ids: List of item IDs this item depends on
        """
        query = '''
        mutation ($item_id: Int!, $column_id: String!, $value: JSON!) {
          change_column_value(
            item_id: $item_id,
            column_id: $column_id,
            value: $value
          ) {
            id
          }
        }
        '''
        
        # Try different Monday.com dependency value formats
        formats_to_try = [
            # Format 1: Standard item_ids array
            json.dumps({"item_ids": dependency_item_ids}),
            
            # Format 2: Simple array
            json.dumps(dependency_item_ids),
            
            # Format 3: String of comma-separated IDs
            ",".join(map(str, dependency_item_ids)),
            
            # Format 4: Single item format (if only one dependency)
            json.dumps({"item_id": dependency_item_ids[0]}) if len(dependency_item_ids) == 1 else None,
            
            # Format 5: Array of objects
            json.dumps([{"id": item_id} for item_id in dependency_item_ids])
        ]
        
        # Filter out None values
        formats_to_try = [f for f in formats_to_try if f is not None]
        
        self.logger.debug(f"Updating dependencies for item {item_id}:")
        self.logger.debug(f"  Column ID: {dependencies_column}")
        self.logger.debug(f"  Dependency item IDs: {dependency_item_ids}")
        
        last_error = None
        
        for i, value_format in enumerate(formats_to_try, 1):
            self.logger.debug(f"  Trying format {i}: {value_format}")
            
            variables = {
                "item_id": int(item_id),
                "column_id": dependencies_column,
                "value": value_format
            }
            
            try:
                result = self.make_request(query, variables)
                self.logger.info(f"Dependency update successful with format {i}: {result}")
                return result
            except Exception as e:
                last_error = e
                self.logger.debug(f"  Format {i} failed: {e}")
                continue
        
        # If all formats failed, log detailed error
        self.logger.error(f"All dependency formats failed for item {item_id}:")
        self.logger.error(f"  Last error: {last_error}")
        self.logger.error(f"  Query: {query}")
        self.logger.error(f"  Final variables: {variables}")
        raise last_error

    def _build_milestone_column_values(
        self,
        milestone: Dict,
        master_item_id: str,
        column_mapping: Dict[str, str],
        phase_mapping: Dict[str, int],
        all_milestones: List[Dict] = None,
        dependency_rules: Dict = None,
    ) -> Dict[str, Any]:
        """Build column values for milestone item with smart dependencies"""
        column_values = {}

        # Timeline (start and end dates)
        # RSI.net Duration is ignored; Monday.com duration is always recalculated from timeline dates.
        if milestone.get("DateOfMilestone") and milestone.get("EndDate"):
            start_date = self._parse_date_string(milestone["DateOfMilestone"])
            end_date = self._parse_date_string(milestone["EndDate"])

            if start_date and end_date:
                column_values[column_mapping["timeline"]] = {
                    "from": start_date,
                    "to": end_date,
                }
                # Always calculate duration as (end - start + 1), ignore RSI.net's Duration field.
                # This matches Monday.com convention.
                try:
                    start_dt = parse_date(start_date)
                    end_dt = parse_date(end_date)
                    duration_days = (end_dt - start_dt).days + 1
                    if duration_days > 0:
                        column_values[column_mapping["duration"]] = str(duration_days)
                except Exception as e:
                    self.logger.warning(f"Could not calculate duration for milestone {milestone['MileStoneType']}: {e}")
            elif start_date:
                column_values[column_mapping["timeline"]] = {
                    "from": start_date,
                    "to": start_date,
                }

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

        # RSi milestone ID for sync checking
        if milestone.get("MilestoneID") and "rsi_milestone_id" in column_mapping:
            column_values[column_mapping["rsi_milestone_id"]] = str(milestone["MilestoneID"])

        # Smart dependency calculation
        if dependency_rules and all_milestones and "dependencies" in column_mapping:
            dependencies = self._calculate_milestone_dependencies(
                milestone, all_milestones, dependency_rules
            )
            if dependencies:
                column_values[column_mapping["dependencies"]] = {
                    "item_ids": dependencies
                }

        return column_values

    def get_project_board_milestones(self, board_id: str, rsi_milestone_column: str) -> List[Dict]:
        """
        Get all milestone items from a project board
        
        Args:
            board_id: Monday.com board ID
            rsi_milestone_column: Column ID for RSi milestone IDs
            
        Returns:
            List of milestone dictionaries with dates and RSi IDs
        """
        query = """
        query ($board_id: [ID!]) {
            boards(ids: $board_id) {
                items {
                    id
                    name
                    column_values {
                        id
                        text
                        value
                    }
                }
            }
        }
        """
        
        variables = {"board_id": [board_id]}
        
        try:
            result = self.make_request(query, variables)
            
            if not result.get("data", {}).get("boards"):
                return []
                
            board = result["data"]["boards"][0]
            milestones = []
            
            for item in board.get("items", []):
                milestone = {
                    "monday_id": item["id"],
                    "name": item["name"],
                    "rsi_milestone_id": None,
                    "timeline_start": None,
                    "timeline_end": None
                }
                
                # Extract column values
                for col in item.get("column_values", []):
                    # RSi milestone ID
                    if col["id"] == rsi_milestone_column:
                        milestone["rsi_milestone_id"] = col["text"]
                    
                    # Timeline dates (assuming timeline column)
                    elif col["id"] == "timeline" and col["value"]:
                        try:
                            timeline_data = json.loads(col["value"])
                            milestone["timeline_start"] = timeline_data.get("from")
                            milestone["timeline_end"] = timeline_data.get("to")
                        except (json.JSONDecodeError, TypeError):
                            pass
                
                milestones.append(milestone)
            
            return milestones
            
        except Exception as e:
            self.logger.error(f"Failed to get milestones from board {board_id}: {e}")
            return []

    def find_project_boards(self, master_board_id: str, project_number: str) -> List[str]:
        """
        Find project board IDs by searching master board for project number
        
        Args:
            master_board_id: Master board ID to search
            project_number: Project number to find
            
        Returns:
            List of project board IDs (usually just one)
        """
        query = """
        query ($board_id: [ID!]) {
            boards(ids: $board_id) {
                items {
                    id
                    name
                    column_values {
                        id
                        text
                    }
                }
            }
        }
        """
        
        variables = {"board_id": [master_board_id]}
        
        try:
            result = self.make_request(query, variables)
            
            if not result.get("data", {}).get("boards"):
                return []
                
            board = result["data"]["boards"][0]
            
            # Look for items containing the project number
            for item in board.get("items", []):
                if project_number in item["name"]:
                    # In a real implementation, you'd need to get the linked board ID
                    # For now, return a placeholder - this would need the actual board linking logic
                    self.logger.info(f"Found project {project_number} in master board: {item['name']}")
                    return ["project_board_id_placeholder"]  # TODO: Get actual linked board ID
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to search master board: {e}")
            return []
    
    def get_project_board_items(self, board_id: str) -> List[Dict]:
        """
        Get all items from a project board with milestone data
        
        Args:
            board_id: Monday.com board ID
            
        Returns:
            List of board items with column values
        """
        query = """
        query ($board_id: [ID!]) {
            boards(ids: $board_id) {
                items_page {
                    items {
                        id
                        name
                        column_values {
                            id
                            text
                            value
                        }
                    }
                }
            }
        }
        """
        
        variables = {"board_id": [board_id]}
        
        try:
            result = self.make_request(query, variables)
            items = result["data"]["boards"][0]["items_page"]["items"]
            self.logger.info(f"Retrieved {len(items)} items from board {board_id}")
            return items
        except Exception as e:
            self.logger.error(f"Failed to get board items: {e}")
            return []
    
    def find_project_boards_by_name(self, folder_id: str, project_pattern: str) -> List[Dict]:
        """
        Find project boards in a folder that match a naming pattern
        
        Args:
            folder_id: Monday.com folder ID
            project_pattern: Pattern to match in board names (e.g., project number)
            
        Returns:
            List of matching boards with id and name
        """
        query = """
        query ($folder_id: ID!) {
            folders(ids: [$folder_id]) {
                children {
                    id
                    name
                }
            }
        }
        """
        
        variables = {"folder_id": folder_id}
        
        try:
            result = self.make_request(query, variables)
            all_boards = result["data"]["folders"][0]["children"]
            
            # Filter boards that contain the project pattern
            matching_boards = [
                board for board in all_boards 
                if project_pattern in board["name"]
            ]
            
            self.logger.info(f"Found {len(matching_boards)} boards matching '{project_pattern}'")
            return matching_boards
            
        except Exception as e:
            self.logger.error(f"Failed to find project boards: {e}")
            return []

    def update_timeline_column(self, board_id: str, item_id: str, timeline_column_id: str, from_date: str, to_date: str):
        """
        Update the timeline column for an item on Monday.com.

        Args:
            board_id: Board ID (required by Monday API)
            item_id: Item (milestone) ID
            timeline_column_id: Column ID of the timeline
            from_date: Start date as 'YYYY-MM-DD'
            to_date: End date as 'YYYY-MM-DD'
        """
        if not from_date or not to_date:
            self.logger.warning(f"Skipped timeline update: missing from_date or to_date ({from_date}, {to_date})")
            return None
        query = '''
        mutation ($board_id: ID!, $item_id: ID!, $column_id: String!, $value: JSON!) {
          change_column_value(
            board_id: $board_id,
            item_id: $item_id,
            column_id: $column_id,
            value: $value
          ) {
            id
          }
        }
        '''
        value = json.dumps({"from": from_date, "to": to_date})
        variables = {
            "board_id": board_id,
            "item_id": str(item_id),
            "column_id": timeline_column_id,
            "value": value
        }
        self.logger.info(f"Updating timeline for item {item_id}: from {from_date} to {to_date}")
        return self.make_request(query, variables)

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
            parsed_date = parse_date(date_str)
            return parsed_date.strftime("%Y-%m-%d")
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Could not parse date '{date_str}': {e}")
            return None
