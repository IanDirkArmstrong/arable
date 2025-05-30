"""Main automation logic for Monday.com project creation"""

import argparse
import sys
from typing import List, Dict, Optional
from pathlib import Path

from .config import load_config, validate_config, ConfigError, create_config_template
from .logger import setup_logger
from .google_sheets import GoogleSheetsClient, GoogleSheetsError
from .monday_api import MondayAPI, MondayAPIError


class ProjectAutomation:
    """Main automation orchestrator"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize automation with configuration

        Args:
            config_path: Optional path to config file
        """
        try:
            self.config = load_config(config_path)
            validate_config(self.config)
        except ConfigError as e:
            print(f"Configuration error: {e}")
            sys.exit(1)

        # Setup logging
        self.logger = setup_logger(
            level=self.config.logging["level"], log_file=self.config.logging.get("file")
        )

        # Initialize clients
        self.sheets_client = GoogleSheetsClient(
            self.config.google_sheets.credentials_path,
            self.config.google_sheets.sheet_name,
            self.logger,
        )

        self.monday_api = MondayAPI(self.config.monday.api_token, self.logger)

        self.logger.info("Monday automation initialized")

    def process_project(self, project: Dict, milestones: List[Dict]) -> bool:
        """
        Process a single project and its milestones

        Args:
            project: Project data dictionary
            milestones: List of milestone dictionaries for this project

        Returns:
            True if successful, False otherwise
        """
        project_number = str(project["ProjectNumber"])
        self.logger.info(
            f"Processing project {project_number}: {project['ProjectName']}"
        )

        try:
            # Step 1: Create master board item
            self.logger.debug(
                f"Creating master board item for project {project_number}"
            )
            master_item_id = self.monday_api.create_master_item(
                self.config.monday.master_board_id,
                project,
                self.config.monday.master_columns,
            )

            # Step 2: Create project board from template
            self.logger.debug(f"Creating project board for project {project_number}")
            project_board_id = self.monday_api.create_project_board(
                self.config.monday.template_board_id,
                self.config.monday.active_projects_folder_id,
                project,
            )

            # Step 3: Add milestones to project board
            milestone_count = 0
            milestone_errors = 0

            for milestone in milestones:
                try:
                    self.logger.debug(
                        f"Adding milestone {milestone['MileStoneType']} to project {project_number}"
                    )
                    self.monday_api.add_milestone_item(
                        project_board_id,
                        milestone,
                        master_item_id,
                        self.config.monday.project_board_columns,
                        self.config.milestone_mappings["phase"],
                        self.config.milestone_mappings["groups"],
                    )
                    milestone_count += 1

                except MondayAPIError as e:
                    milestone_errors += 1
                    self.logger.error(
                        f"Failed to add milestone {milestone['MileStoneType']}: {e}"
                    )
                    # Continue with other milestones
                except Exception as e:
                    milestone_errors += 1
                    self.logger.error(
                        f"Unexpected error adding milestone {milestone['MileStoneType']}: {e}"
                    )

            success_rate = milestone_count / len(milestones) if milestones else 1.0
            self.logger.info(
                f"Added {milestone_count}/{len(milestones)} milestones to project {project_number} "
                f"({milestone_errors} errors)"
            )

            # Consider project successful if we got the main items and most milestones
            if success_rate >= 0.5:  # At least 50% of milestones successful
                self.logger.info(f"Successfully processed project {project_number}")
                return True
            else:
                self.logger.error(
                    f"Too many milestone failures for project {project_number}"
                )
                return False

        except MondayAPIError as e:
            self.logger.error(f"Monday API error for project {project_number}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error for project {project_number}: {e}")
            return False

    def run(self, test_project_number: Optional[str] = None) -> None:
        """
        Run the automation workflow

        Args:
            test_project_number: Optional project number for testing single project
        """
        self.logger.info("Starting Monday.com automation")

        try:
            # Connect to Google Sheets and read data
            self.sheets_client.connect()
            projects, milestones = self.sheets_client.read_data()

            # Filter for test project if specified
            if test_project_number:
                projects = [
                    p
                    for p in projects
                    if str(p["ProjectNumber"]) == test_project_number
                ]
                milestones = [
                    m
                    for m in milestones
                    if str(m["ProjectNumber"]) == test_project_number
                ]
                self.logger.info(f"Testing with project {test_project_number} only")

            if not projects:
                self.logger.warning("No projects found to process")
                return

            # Process each project
            success_count = 0
            for project in projects:
                project_number = str(project["ProjectNumber"])
                project_milestones = [
                    m for m in milestones if str(m["ProjectNumber"]) == project_number
                ]

                self.logger.info(
                    f"Found {len(project_milestones)} milestones for project {project_number}"
                )

                if self.process_project(project, project_milestones):
                    success_count += 1

            self.logger.info(
                f"Automation complete: {success_count}/{len(projects)} projects processed successfully"
            )

        except GoogleSheetsError as e:
            self.logger.error(f"Google Sheets error: {e}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Automation failed: {e}")
            sys.exit(1)


def cli():
    """Command-line interface for the automation"""
    parser = argparse.ArgumentParser(
        description="Monday.com Project and Milestone Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run                              # Run with default config
  %(prog)s run --config custom.yaml        # Use custom config
  %(prog)s run --test-project 12345        # Test single project
  %(prog)s init-config                     # Create config template
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run automation command
    run_parser = subparsers.add_parser("run", help="Run the automation")
    run_parser.add_argument("--config", "-c", help="Path to configuration file")
    run_parser.add_argument(
        "--test-project", "-t", help="Test with specific project number only"
    )
    run_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    run_parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be done without making changes",
    )

    # Config template command
    config_parser = subparsers.add_parser(
        "init-config", help="Create configuration template"
    )
    config_parser.add_argument(
        "--output",
        "-o",
        default="config/config.yaml",
        help="Output path for configuration template (default: config/config.yaml)",
    )

    args = parser.parse_args()

    # Handle init-config command
    if args.command == "init-config":
        create_config_template(args.output)
        return

    # Default to 'run' if no command specified or if 'run' specified
    if not args.command or args.command == "run":
        # Override logging level if verbose
        if hasattr(args, "verbose") and args.verbose:
            import logging

            logging.getLogger("monday_automation").setLevel(logging.DEBUG)

        # Run automation
        try:
            automation = ProjectAutomation(getattr(args, "config", None))

            if hasattr(args, "dry_run") and args.dry_run:
                print("🔍 DRY RUN MODE - No changes will be made")
                # TODO: Implement dry run mode
                print("Dry run mode not yet implemented")
                return

            automation.run(getattr(args, "test_project", None))

        except ConfigError as e:
            print(f"❌ Configuration error: {e}")
            print("💡 Try running: python run.py init-config")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Automation failed: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
