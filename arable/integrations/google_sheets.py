"""Google Sheets integration for ARABLE
Migrated from src/monday_automation/google_sheets.py
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Tuple
import logging


class GoogleSheetsError(Exception):
    """Google Sheets-related errors"""
    pass


class GoogleSheetsClient:
    """Google Sheets client for reading project and milestone data"""

    def __init__(self, credentials_path: str, sheet_name: str, logger: logging.Logger):
        """
        Initialize Google Sheets client

        Args:
            credentials_path: Path to service account credentials JSON
            sheet_name: Name of the Google Sheet to access
            logger: Logger instance
        """
        self.credentials_path = credentials_path
        self.sheet_name = sheet_name
        self.logger = logger
        self.client = None
        self.workbook = None

    def connect(self) -> None:
        """
        Establish connection to Google Sheets

        Raises:
            GoogleSheetsError: If connection fails
        """
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]

            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, scope
            )

            self.client = gspread.authorize(creds)
            self.workbook = self.client.open(self.sheet_name)

            self.logger.info(f"Connected to Google Sheet: {self.sheet_name}")

        except FileNotFoundError:
            raise GoogleSheetsError(
                f"Credentials file not found: {self.credentials_path}"
            )
        except gspread.SpreadsheetNotFound:
            raise GoogleSheetsError(f"Spreadsheet not found: {self.sheet_name}")
        except Exception as e:
            raise GoogleSheetsError(f"Failed to connect to Google Sheets: {e}")

    def read_projects(self, worksheet_name: str = "Projects") -> List[Dict]:
        """
        Read project data from specified worksheet

        Args:
            worksheet_name: Name of worksheet containing projects

        Returns:
            List of project dictionaries

        Raises:
            GoogleSheetsError: If reading fails
        """
        if not self.workbook:
            raise GoogleSheetsError("Not connected to Google Sheets")

        try:
            worksheet = self.workbook.worksheet(worksheet_name)
            projects_data = worksheet.get_all_records()

            # Filter out empty rows (missing ProjectNumber)
            projects = [
                row
                for row in projects_data
                if row.get("ProjectNumber") and str(row["ProjectNumber"]).strip()
            ]

            self.logger.info(
                f"Loaded {len(projects)} projects from worksheet '{worksheet_name}'"
            )
            return projects

        except gspread.WorksheetNotFound:
            raise GoogleSheetsError(f"Worksheet '{worksheet_name}' not found")
        except Exception as e:
            raise GoogleSheetsError(f"Error reading projects: {e}")

    def read_milestones(self, worksheet_name: str = "Milestones") -> List[Dict]:
        """
        Read milestone data from specified worksheet

        Args:
            worksheet_name: Name of worksheet containing milestones

        Returns:
            List of milestone dictionaries

        Raises:
            GoogleSheetsError: If reading fails
        """
        if not self.workbook:
            raise GoogleSheetsError("Not connected to Google Sheets")

        try:
            worksheet = self.workbook.worksheet(worksheet_name)
            milestones_data = worksheet.get_all_records()

            # Filter out empty rows and clean milestone types
            milestones = []
            for row in milestones_data:
                if row.get("ProjectNumber") and row.get("MileStoneType"):
                    # Clean up milestone type (remove trailing spaces)
                    row["MileStoneType"] = str(row["MileStoneType"]).strip()
                    milestones.append(row)

            self.logger.info(
                f"Loaded {len(milestones)} milestones from worksheet '{worksheet_name}'"
            )
            return milestones

        except gspread.WorksheetNotFound:
            raise GoogleSheetsError(f"Worksheet '{worksheet_name}' not found")
        except Exception as e:
            raise GoogleSheetsError(f"Error reading milestones: {e}")

    def read_data(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Read both projects and milestones data with enhanced validation

        Returns:
            Tuple of (projects, milestones)
        """
        projects = self.read_projects()
        milestones = self.read_milestones()

        # Validate the data
        self.validate_data(projects, milestones)

        # Log milestone types found
        milestone_types = set(
            m.get("MileStoneType", "").strip() for m in milestones
        )
        milestone_types.discard("")  # Remove empty strings

        self.logger.info(f"📊 Found {len(milestone_types)} unique milestone types:")
        for milestone_type in sorted(milestone_types):
            self.logger.debug(f"   - {milestone_type}")

        return projects, milestones

    def validate_data(self, projects: List[Dict], milestones: List[Dict]) -> None:
        """
        Validate loaded data for completeness

        Args:
            projects: List of project dictionaries
            milestones: List of milestone dictionaries

        Raises:
            GoogleSheetsError: If data validation fails
        """
        if not projects:
            raise GoogleSheetsError("No valid projects found in spreadsheet")

        # Check for required project fields
        required_project_fields = ["ProjectNumber", "ProjectName", "CustomerShortname"]
        for i, project in enumerate(projects):
            for field in required_project_fields:
                if not project.get(field):
                    raise GoogleSheetsError(
                        f"Project row {i + 1} missing required field: {field}"
                    )

        # Check for duplicate project numbers
        project_numbers = [str(p["ProjectNumber"]) for p in projects]
        duplicates = [
            num for num in set(project_numbers) if project_numbers.count(num) > 1
        ]
        if duplicates:
            raise GoogleSheetsError(f"Duplicate project numbers found: {duplicates}")

        # Check milestones reference valid projects
        if milestones:
            milestone_project_numbers = set(str(m["ProjectNumber"]) for m in milestones)
            project_numbers_set = set(project_numbers)
            orphaned = milestone_project_numbers - project_numbers_set
            if orphaned:
                self.logger.warning(
                    f"Milestones reference non-existent projects: {orphaned}"
                )
