#!/usr/bin/env python3
"""
arable CLI - Main entry point
agentic runtime and business logic engine
"""

from typing import List, Dict

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.logging import RichHandler
from typing import Optional
import sys
from pathlib import Path
import logging

# Import the migrated components
from ..integrations.monday import MondayAPI, MondayAPIError
from ..integrations.google_sheets import GoogleSheetsClient, GoogleSheetsError  
from ..utils.config import load_config, validate_config, ConfigError, create_config_template
from ..utils.logger import setup_logger
from ..agents.registry import registry
from ..agents.orchestrator import orchestrator

app = typer.Typer(
    name="arable",
    help="[bold blue]arable[/bold blue] - agentic runtime and business logic engine",
    rich_markup_mode="rich"
)

console = Console()

class ProjectAutomation:
    """Main automation orchestrator - migrated from original"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize automation with configuration"""
        try:
            self.config = load_config(config_path)
            validate_config(self.config)
        except ConfigError as e:
            console.print(f"[red]❌ Configuration error: {e}[/red]")
            sys.exit(1)

        # Setup logging
        self.logger = setup_logger(
            level=self.config.logging["level"], 
            log_file=self.config.logging.get("file")
        )

        # Initialize clients
        self.sheets_client = GoogleSheetsClient(
            self.config.google_sheets.credentials_path,
            self.config.google_sheets.sheet_name,
            self.logger,
        )

        self.monday_api = MondayAPI(self.config.monday.api_token, self.logger)
        self.logger.info("arable automation initialized")

    def compare_milestone_data(self, sheets_milestones: list, monday_items: list) -> dict:
        """
        Compare milestone data between Google Sheets and Monday.com
        
        Returns:
            Dictionary with sync status and discrepancies
        """
        results = {
            "total_sheets_milestones": len(sheets_milestones),
            "total_monday_items": len(monday_items),
            "matched": [],
            "missing_in_monday": [],
            "date_discrepancies": []
        }
        
        # Create lookup for Monday items by RSi milestone ID
        monday_by_rsi_id = {}
        rsi_column_id = self.config.monday.project_board_columns.get("rsi_milestone_id")
        
        if rsi_column_id:
            for item in monday_items:
                for col in item["column_values"]:
                    if col["id"] == rsi_column_id and col["text"]:
                        monday_by_rsi_id[col["text"]] = item
                        break
        
        # Compare each sheets milestone
        for milestone in sheets_milestones:
            milestone_id = milestone.get("MilestoneID")
            milestone_type = milestone.get("MileStoneType")

            # Use DateOfMilestone and EndDate for sheets_start and sheets_end
            sheets_start = milestone.get("DateOfMilestone")
            sheets_end = milestone.get("EndDate")

            if milestone_id and str(milestone_id) in monday_by_rsi_id:
                # Found match - compare dates
                monday_item = monday_by_rsi_id[str(milestone_id)]

                # Extract timeline dates from Monday item
                timeline_column_id = self.config.monday.project_board_columns.get("timeline")
                monday_dates = None

                if timeline_column_id:
                    for col in monday_item["column_values"]:
                        if col["id"] == timeline_column_id and col["value"]:
                            try:
                                import json
                                timeline_data = json.loads(col["value"])
                                monday_dates = {
                                    "start": timeline_data.get("from"),
                                    "end": timeline_data.get("to")
                                }
                            except:
                                pass
                            break

                # Compare dates (revised logic)
                if monday_dates:
                    sheets_start_str = self.monday_api._parse_date_string(sheets_start) if sheets_start else None
                    sheets_end_str = self.monday_api._parse_date_string(sheets_end) if sheets_end else None
                    monday_start_str = monday_dates.get("start")
                    monday_end_str = monday_dates.get("end")
                    # Compare start
                    if sheets_start_str != monday_start_str:
                        results["date_discrepancies"].append({
                            "milestone_type": milestone_type,
                            "milestone_id": milestone_id,
                            "field": "start",
                            "sheets_date": sheets_start_str,
                            "monday_date": monday_start_str
                        })
                    # Compare end
                    if sheets_end_str != monday_end_str:
                        results["date_discrepancies"].append({
                            "milestone_type": milestone_type,
                            "milestone_id": milestone_id,
                            "field": "end",
                            "sheets_date": sheets_end_str,
                            "monday_date": monday_end_str
                        })

                results["matched"].append({
                    "milestone_type": milestone_type,
                    "milestone_id": milestone_id
                })
            else:
                # Missing in Monday
                results["missing_in_monday"].append({
                    "milestone_type": milestone_type,
                    "milestone_id": milestone_id
                })
        
        return results

    def process_project_with_progress(self, project: dict, milestones: list, progress: Progress) -> bool:
        """Process a single project and its milestones with progress tracking"""
        project_number = str(project["ProjectNumber"])
        self.logger.info(f"Processing project {project_number}: {project['ProjectName']}")

        try:
            # Step 1: Create master board item
            master_task = progress.add_task(f"📋 Creating master item for {project_number}...", total=None)
            master_item_id = self.monday_api.create_master_item(
                self.config.monday.master_board_id,
                project,
                self.config.monday.master_columns,
            )
            progress.update(master_task, completed=1, total=1)

            # Step 2: Create project board from template
            board_task = progress.add_task(f"🏗️  Creating project board for {project_number}...", total=None)
            project_board_id = self.monday_api.create_project_board(
                self.config.monday.template_board_id,
                self.config.monday.active_projects_folder_id,
                project,
            )
            progress.update(board_task, completed=1, total=1)

            # Step 3: Add milestones to project board
            if milestones:
                milestone_task = progress.add_task(f"📅 Adding milestones to {project_number}...", total=len(milestones))
                milestone_count = 0
                milestone_errors = 0
                created_milestones = []  # Track created milestones for dependency updates
                
                for milestone in milestones:
                    try:
                        item_id = self.monday_api.add_milestone_item(
                            project_board_id,
                            milestone,
                            master_item_id,
                            self.config.monday.project_board_columns,
                            self.config.milestone_mappings["phase"],
                            self.config.milestone_mappings["groups"],
                            milestones,  # Pass all milestones for dependency calculation
                            self.config.milestone_mappings.get("dependencies")  # Pass dependency rules
                        )
                        
                        # Track created milestone with its Monday item ID
                        milestone_with_id = milestone.copy()
                        milestone_with_id["monday_item_id"] = item_id
                        created_milestones.append(milestone_with_id)
                        
                        milestone_count += 1
                        progress.update(milestone_task, advance=1)

                    except MondayAPIError as e:
                        milestone_errors += 1
                        progress.update(milestone_task, advance=1)
                        self.logger.error(f"Failed to add milestone {milestone['MileStoneType']}: {e}")
                
                # Step 4: Update dependencies after all milestones are created
                if created_milestones and self.config.milestone_mappings.get("dependencies"):
                    dependency_task = progress.add_task(f"🔗 Setting dependencies for {project_number}...", total=None)
                    try:
                        dependencies_updated = self.monday_api.update_milestone_dependencies(
                            project_board_id,
                            created_milestones,
                            self.config.milestone_mappings["dependencies"],
                            self.config.monday.project_board_columns
                        )
                        progress.update(dependency_task, completed=1, total=1)
                        self.logger.info(f"Updated dependencies for {dependencies_updated} milestones")
                    except Exception as e:
                        progress.update(dependency_task, completed=1, total=1)
                        self.logger.error(f"Failed to update dependencies: {e}")

            success_rate = milestone_count / len(milestones) if milestones else 1.0
            
            if success_rate >= 0.5:  # At least 50% success
                return True
            else:
                return False

        except MondayAPIError as e:
            self.logger.error(f"Monday API error for project {project_number}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error for project {project_number}: {e}")
            return False

    def run(self, test_project_number: Optional[str] = None) -> None:
        """Run the automation workflow"""
        console.print("[bold blue]🚀 Starting arable project automation[/bold blue]")

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                
                # Connect to Google Sheets
                sheets_task = progress.add_task("📊 Connecting to Google Sheets...", total=None)
                self.sheets_client.connect()
                projects, milestones = self.sheets_client.read_data()
                progress.update(sheets_task, completed=1, total=1)

                # Filter for specific project if specified
                if test_project_number:
                    projects = [p for p in projects if str(p["ProjectNumber"]) == test_project_number]
                    milestones = [m for m in milestones if str(m["ProjectNumber"]) == test_project_number]
                    console.print(f"🎯 Testing with project {test_project_number} only")

                if not projects:
                    console.print("[yellow]⚠️  No projects found to process[/yellow]")
                    return

                # Show summary table
                table = Table(title="Projects to Process")
                table.add_column("Project #", style="cyan")
                table.add_column("Project Name", style="magenta") 
                table.add_column("Customer", style="green")
                table.add_column("Milestones", justify="right", style="blue")

                for project in projects:
                    project_number = str(project["ProjectNumber"])
                    project_milestones = [m for m in milestones if str(m["ProjectNumber"]) == project_number]
                    table.add_row(
                        project_number,
                        project["ProjectName"],
                        project["CustomerShortname"], 
                        str(len(project_milestones))
                    )

                console.print(table)
        except Exception as e:
            self.logger.error(f"Unexpected error in run: {e}")
            console.print(f"[red]❌ Automation failed: {e}[/red]")
            sys.exit(1)

@app.command()
def config():
    """Generate configuration file template"""
    console.print("[bold blue]📝 Configuration Setup[/bold blue]")
    console.print("Creating config template at config/config.yaml...")
    
    try:
        create_config_template()
        console.print("[green]✅ Configuration template created![/green]")
    except Exception as e:
        console.print(f"[red]❌ Config template generator failed: {e}[/red]")

@app.command()
def info():
    """Show arable system information"""
    console.print(Panel(
        "[bold blue]arable[/bold blue] - agentic runtime and business logic engine\n\n"
        "🤖 Intelligent document extraction\n"
        "🔄 Cross-platform data reconciliation\n"
        "⚡ Agent-driven workflow automation\n"
        "🎯 Business logic orchestration",
        title="System Information",
        border_style="blue"
    ))

@app.command()
def project(
    project_number: Optional[str] = typer.Argument(None, help="Specific project number to process"),
    all_projects: bool = typer.Option(False, "--all", "-a", help="Process all projects from Google Sheets"),
    config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """
    Create Monday.com projects from Google Sheets data
    
    Examples:
      arable project 12345          # Process specific project
      arable project --all          # Process all projects  
      arable project                # Interactive mode (prompts for project number)
    """
    
    # Handle case where no args provided - prompt for project number
    if not project_number and not all_projects:
        project_number = typer.prompt("Enter project number (or 'all' for all projects)")
        if project_number.lower() == 'all':
            all_projects = True
            project_number = None

    # Override logging if verbose
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize automation
        automation = ProjectAutomation(config_path)
        
        # Run with specific project or all projects
        if all_projects:
            console.print("[yellow]Processing ALL projects from Google Sheets[/yellow]")
            automation.run()
        else:
            console.print(f"[yellow]Processing project {project_number} only[/yellow]")
            automation.run(project_number)
            
    except Exception as e:
        console.print(f"[red]❌ Project automation failed: {e}[/red]")
        sys.exit(1)

    # Process projects with progress bar
    # (This block was previously misplaced inside config(); now correctly placed here)
    # Note: This code assumes it should run after the summary table is displayed.
    # However, in the current implementation, automation.run() handles the progress bar and summary.
    # If you want to keep the logic for processing projects here, you could move the code from automation.run().
    # For now, this is left as a placeholder for the relocated block.

@app.command()
def sync(
    project_number: Optional[str] = typer.Argument(None, help="Specific project number to check"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file")
):
    """
    Check sync status between Google Sheets and Monday.com
    
    This command compares milestone dates and statuses between your Google Sheets
    data and Monday.com boards to identify discrepancies.
    """
    try:
        automation = ProjectAutomation(config)
        
        # Enable debug logging if requested
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            automation.logger.setLevel(logging.DEBUG)
            automation.monday_api.logger.setLevel(logging.DEBUG)
            console.print("[dim]Debug logging enabled[/dim]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Load Google Sheets data
            sheets_task = progress.add_task("📊 Loading Google Sheets data...", total=None)
            automation.sheets_client.connect()
            projects, milestones = automation.sheets_client.read_data()
            progress.update(sheets_task, completed=1, total=1)
            
            # Filter for specific project if specified
            if project_number:
                projects = [p for p in projects if str(p["ProjectNumber"]) == project_number]
                milestones = [m for m in milestones if str(m["ProjectNumber"]) == project_number]
                console.print(f"🎯 Checking sync for project {project_number} only")
            
            if not projects:
                console.print("[yellow]⚠️  No projects found to check[/yellow]")
                return
            
            # Check Monday.com boards for comparison
            monday_task = progress.add_task("📋 Fetching Monday.com data...", total=len(projects))
            
            # Create sync report table
            table = Table(title="Sync Status Report")
            table.add_column("Project #", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Matched", justify="right", style="blue")
            table.add_column("Missing", justify="right", style="yellow")
            table.add_column("Date Issues", justify="right", style="red")
            
            for project in projects:
                project_number = str(project["ProjectNumber"])
                project_milestones = [m for m in milestones if str(m["ProjectNumber"]) == project_number]
                
                # Find project board in Monday
                project_boards = automation.monday_api.find_project_boards_by_name(
                    automation.config.monday.active_projects_folder_id,
                    project_number
                )
                
                if project_boards:
                    # Get board items
                    board_id = project_boards[0]["id"]
                    monday_items = automation.monday_api.get_project_board_items(board_id)
                    
                    # Compare data
                    sync_results = automation.compare_milestone_data(project_milestones, monday_items)
                    
                    table.add_row(
                        project_number,
                        "Board found",
                        str(len(sync_results["matched"])),
                        str(len(sync_results["missing_in_monday"])),
                        str(len(sync_results["date_discrepancies"]))
                    )
                    
                    # Show detailed discrepancies if any
                    if sync_results["missing_in_monday"]:
                        console.print(f"\n[yellow]⚠️  Missing milestones in project {project_number}:[/yellow]")
                        for missing in sync_results["missing_in_monday"][:5]:  # Show first 5
                            console.print(f"  • {missing['milestone_type']} (ID: {missing['milestone_id']})")
                    
                    if sync_results["date_discrepancies"]:
                        console.print(f"\n[red]📅 Date discrepancies in project {project_number}:[/red]")
                        for disc in sync_results["date_discrepancies"][:3]:  # Show first 3
                            console.print(f"  • {disc['milestone_type']}: Sheets={disc['sheets_date']}, Monday={disc['monday_date']}")

                        # === Auto-fix all date discrepancies ===
                        for disc in sync_results["date_discrepancies"]:
                            milestone_id = str(disc["milestone_id"])
                            
                            # Find the Monday item that has this RSi milestone ID in its column
                            monday_item = None
                            rsi_column_id = automation.config.monday.project_board_columns.get("rsi_milestone_id")
                            
                            if rsi_column_id:
                                for item in monday_items:
                                    for col in item["column_values"]:
                                        if col["id"] == rsi_column_id and col["text"] == milestone_id:
                                            monday_item = item
                                            break
                                    if monday_item:
                                        break
                            
                            if not monday_item:
                                console.print(f"[yellow]Skipped: No Monday item found with RSi Milestone ID {milestone_id}[/yellow]")
                                continue

                            # Get timeline column ID
                            timeline_column_id = automation.config.monday.project_board_columns.get("timeline")
                            if not timeline_column_id:
                                console.print("[yellow]Skipped: Timeline column ID not found in config[/yellow]")
                                continue

                            # Get the latest correct dates from sheets for this milestone
                            sheets_start = None
                            sheets_end = None
                            for m in project_milestones:
                                if str(m.get("MilestoneID")) == milestone_id:
                                    sheets_start = automation.monday_api._parse_date_string(m.get("DateOfMilestone"))
                                    sheets_end = automation.monday_api._parse_date_string(m.get("EndDate"))
                                    break

                            if not (sheets_start and sheets_end):
                                console.print(f"[yellow]Skipped: Missing start/end dates for Milestone ID {milestone_id}[/yellow]")
                                continue

                            # Call the Monday API to update the timeline using the Monday item ID
                            automation.monday_api.update_timeline_column(
                                board_id=board_id,
                                item_id=monday_item["id"],  # Use the actual Monday item ID
                                timeline_column_id=timeline_column_id,
                                from_date=sheets_start,
                                to_date=sheets_end
                            )
                            console.print(
                                f"[green]✔ Fixed milestone {disc['milestone_type']} (RSi ID: {milestone_id}, Monday ID: {monday_item['id']}) to: {sheets_start} → {sheets_end}[/green]"
                            )
                else:
                    table.add_row(
                        project_number,
                        "No board found",
                        "0",
                        str(len(project_milestones)),
                        "0"
                    )
                
                progress.update(monday_task, advance=1)
            
        console.print(table)
        console.print("\n[bold yellow]🔄 Full sync checking coming soon![/bold yellow]")
        console.print("This will compare milestone dates, statuses, and RSi IDs between systems.")
        
    except Exception as e:
        console.print(f"[red]❌ Sync check failed: {e}[/red]")
        sys.exit(1)

@app.command()
def dependencies(
    project_number: Optional[str] = typer.Argument(None, help="Specific project number to update dependencies for"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to configuration file"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what dependencies would be set without making changes"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging for troubleshooting")
):
    """
    Update milestone dependencies in Monday.com based on business logic
    
    This command analyzes existing milestones in Monday.com and sets intelligent
    dependencies based on RSi project workflow patterns.
    """
    try:
        automation = ProjectAutomation(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Load Google Sheets data to get project info
            sheets_task = progress.add_task("📆 Loading project data...", total=None)
            automation.sheets_client.connect()
            projects, milestones = automation.sheets_client.read_data()
            progress.update(sheets_task, completed=1, total=1)
            
            # Filter for specific project if specified
            if project_number:
                projects = [p for p in projects if str(p["ProjectNumber"]) == project_number]
                milestones = [m for m in milestones if str(m["ProjectNumber"]) == project_number]
                console.print(f"🎯 Updating dependencies for project {project_number} only")
            
            if not projects:
                console.print("[yellow]⚠️  No projects found to update[/yellow]")
                return
            
            # Process each project
            project_task = progress.add_task("🔗 Updating dependencies...", total=len(projects))
            total_updated = 0
            
            for project in projects:
                project_number = str(project["ProjectNumber"])
                project_milestones = [m for m in milestones if str(m["ProjectNumber"]) == project_number]
                
                # Find project board in Monday
                project_boards = automation.monday_api.find_project_boards_by_name(
                    automation.config.monday.active_projects_folder_id,
                    project_number
                )
                
                if project_boards:
                    board_id = project_boards[0]["id"]
                    console.print(f"\n[blue]Project {project_number}: {project['ProjectName']}[/blue]")
                    
                    # Get existing Monday items
                    monday_items = automation.monday_api.get_project_board_items(board_id)
                    
                    # Create lookup of RSi milestone IDs to Monday items
                    rsi_column_id = automation.config.monday.project_board_columns.get("rsi_milestone_id")
                    milestone_lookup = {}
                    
                    if rsi_column_id:
                        for item in monday_items:
                            for col in item["column_values"]:
                                if col["id"] == rsi_column_id and col["text"]:
                                    # Find matching sheets milestone
                                    for milestone in project_milestones:
                                        if str(milestone.get("MilestoneID")) == col["text"]:
                                            milestone_with_id = milestone.copy()
                                            milestone_with_id["monday_item_id"] = item["id"]
                                            milestone_lookup[milestone["MileStoneType"]] = milestone_with_id
                                            break
                    
                    # Convert to list for dependency update function
                    milestones_with_ids = list(milestone_lookup.values())
                    
                    if dry_run:
                        # Show what would be updated
                        console.print(f"[yellow]Dry run - showing planned dependencies:[/yellow]")
                        _show_planned_dependencies(
                            milestones_with_ids, 
                            automation.config.milestone_mappings.get("dependencies", {})
                        )
                    else:
                        # Actually update dependencies
                        if milestones_with_ids:
                            updated_count = automation.monday_api.update_milestone_dependencies(
                                board_id,
                                milestones_with_ids,
                                automation.config.milestone_mappings.get("dependencies", {}),
                                automation.config.monday.project_board_columns
                            )
                            total_updated += updated_count
                            console.print(f"[green]✓ Updated {updated_count} milestones[/green]")
                        else:
                            console.print("[yellow]No milestones found with RSi IDs[/yellow]")
                else:
                    console.print(f"[yellow]No Monday board found for project {project_number}[/yellow]")
                
                progress.update(project_task, advance=1)
            
            if dry_run:
                console.print(f"\n[bold blue]🔍 Dry run complete - no changes made[/bold blue]")
            else:
                console.print(f"\n[bold green]🎉 Updated dependencies for {total_updated} milestones across {len(projects)} projects[/bold green]")
                
    except Exception as e:
        console.print(f"[red]❌ Dependency update failed: {e}[/red]")
        sys.exit(1)
        
def _show_planned_dependencies(milestones: List[Dict], dependency_rules: Dict):
    """Show what dependencies would be set in dry run mode using flexible logic"""
    workflow_rules = dependency_rules.get("workflow_rules", {})
    critical_path = dependency_rules.get("critical_path", {})
    
    # Create lookup of milestone types to items
    milestone_lookup = {}
    for milestone in milestones:
        milestone_type = milestone.get("MileStoneType")
        if milestone_type:
            milestone_lookup[milestone_type] = milestone
    
    # Get available milestone types in this project
    available_milestone_types = set(milestone_lookup.keys())
    
    table = Table(title="Planned Dependencies (Flexible Logic)")
    table.add_column("Milestone", style="cyan")
    table.add_column("Preferred Dependencies", style="yellow")
    table.add_column("Selected", style="green")
    table.add_column("Status", style="blue")
    
    for milestone in milestones:
        milestone_type = milestone.get("MileStoneType")
        if not milestone_type:
            continue
            
        # Try workflow rules first (flexible chains)
        dependency_candidates = workflow_rules.get(milestone_type, [])
        
        # Find the first available dependency from the chain
        selected_dependency = None
        for candidate in dependency_candidates:
            if candidate in available_milestone_types and candidate != milestone_type:
                selected_dependency = candidate
                break  # Take the first (most preferred) available dependency
                
        # If no workflow dependencies found, try critical path fallback
        if not selected_dependency:
            critical_candidates = critical_path.get(milestone_type, [])
            
            for candidate in critical_candidates:
                if candidate in available_milestone_types and candidate != milestone_type:
                    selected_dependency = candidate
                    break
        
        # Format the display
        if dependency_candidates:
            # Show first few preferred dependencies
            preferred_display = ", ".join(dependency_candidates[:3])
            if len(dependency_candidates) > 3:
                preferred_display += "..."
        else:
            preferred_display = "None defined"
            
        if selected_dependency:
            status = "✓ Will set dependency"
            selected_display = selected_dependency
        elif dependency_candidates:
            status = "⚠️ No suitable dependencies available"
            selected_display = "None found"
        else:
            status = "ℹ️ Independent milestone"
            selected_display = "N/A"
            
        table.add_row(
            milestone_type,
            preferred_display,
            selected_display,
            status
        )
    
    console.print(table)
    
    # Show summary
    total_milestones = len(milestones)
    dependencies_to_set = sum(1 for m in milestones 
                             if _get_selected_dependency(m.get("MileStoneType"), available_milestone_types, workflow_rules, critical_path))
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"Total milestones: {total_milestones}")
    console.print(f"Dependencies to set: {dependencies_to_set}")
    console.print(f"Independent milestones: {total_milestones - dependencies_to_set}")

def _get_selected_dependency(milestone_type: str, available_types: set, workflow_rules: Dict, critical_path: Dict) -> Optional[str]:
    """Helper function to get the selected dependency for a milestone type"""
    if not milestone_type:
        return None
        
    # Try workflow rules first
    dependency_candidates = workflow_rules.get(milestone_type, [])
    for candidate in dependency_candidates:
        if candidate in available_types and candidate != milestone_type:
            return candidate
            
    # Try critical path fallback
    critical_candidates = critical_path.get(milestone_type, [])
    for candidate in critical_candidates:
        if candidate in available_types and candidate != milestone_type:
            return candidate
            
    return None

@app.command()
def agents(
    action: str = typer.Argument(help="Action: list, run, workflow"),
    agent_name: Optional[str] = typer.Option(None, "--agent", "-a", help="Specific agent name"),
    task_data: Optional[str] = typer.Option(None, "--data", "-d", help="JSON task data"),
    workflow_file: Optional[str] = typer.Option(None, "--workflow", "-w", help="Workflow definition file")
):
    """
    Manage and execute arable agents
    
    Examples:
      arable agents list                           # List all available agents
      arable agents run --agent document_extractor --data '{"document_path": "/path/to/doc.pdf"}'
      arable agents workflow --workflow extract_and_sync.yaml
    """
    
    if action == "list":
        _list_agents()
    elif action == "run":
        _run_single_agent(agent_name, task_data)
    elif action == "workflow":
        _run_workflow(workflow_file)
    else:
        console.print(f"[red]❌ Unknown action: {action}[/red]")
        console.print("Available actions: list, run, workflow")
        
def _list_agents():
    """List all registered agents"""
    console.print("[bold blue]🤖 arable agents[/bold blue]")
    
    # Auto-discover agents first
    discovered_count = registry.auto_discover_agents()
    
    if discovered_count > 0:
        console.print(f"[green]Discovered {discovered_count} agents[/green]")
    
    agent_list = registry.list_agents()
    
    if not agent_list:
        console.print("[yellow]⚠️  No agents registered[/yellow]")
        return
        
    # Create agents table
    table = Table(title="Registered Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")
    table.add_column("Capabilities", style="blue")
    
    for agent in agent_list:
        capabilities_str = ""
        if "capabilities" in agent:
            capabilities_str = ", ".join([cap["name"] for cap in agent["capabilities"]])
        elif agent["name"] in ["document_extractor", "monday_manager"]:
            # Show known capabilities for discovered agents
            if agent["name"] == "document_extractor":
                capabilities_str = "document_extraction, proposal_processing"
            elif agent["name"] == "monday_manager":
                capabilities_str = "project_creation, milestone_sync"
                
        status_color = "green" if agent["enabled"] else "red"
        status = f"[{status_color}]{agent['status']}[/{status_color}]"
        
        table.add_row(
            agent["name"],
            agent["description"],
            status,
            capabilities_str
        )
        
    console.print(table)
    
def _run_single_agent(agent_name: Optional[str], task_data: Optional[str]):
    """Run a single agent with task data"""
    
    if not agent_name:
        console.print("[red]❌ Agent name required for run action[/red]")
        return
        
    if not task_data:
        console.print("[red]❌ Task data required for run action[/red]")
        return
        
    try:
        import json
        task_dict = json.loads(task_data)
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ Invalid JSON in task data: {e}[/red]")
        return
        
    console.print(f"[bold blue]🚀 Running agent: {agent_name}[/bold blue]")
    
    try:
        # Auto-discover agents first
        registry.auto_discover_agents()
        
        # Run agent task
        import asyncio
        result = asyncio.run(orchestrator.execute_single_task(agent_name, task_dict))
        
        if result["success"]:
            console.print("[green]✅ Agent execution completed successfully[/green]")
            
            # Show result in formatted way
            if "result" in result:
                agent_result = result["result"]
                if isinstance(agent_result, dict):
                    console.print("\n[bold]Results:[/bold]")
                    for key, value in agent_result.items():
                        if key != "extracted_data":  # Don't print large data blobs
                            console.print(f"  {key}: {value}")
                        else:
                            console.print(f"  {key}: [dim]<data extracted>[/dim]")
        else:
            console.print(f"[red]❌ Agent execution failed: {result.get('error', 'Unknown error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Failed to run agent: {e}[/red]")
        
def _run_workflow(workflow_file: Optional[str]):
    """Run a multi-agent workflow"""
    
    if not workflow_file:
        console.print("[red]❌ Workflow file required[/red]")
        return
        
    console.print(f"[bold blue]🔄 Running workflow: {workflow_file}[/bold blue]")
    console.print("[yellow]⚠️  Workflow execution coming soon![/yellow]")
    
    # TODO: Implement workflow file parsing and execution
    # This would read a YAML/JSON workflow definition and execute it

@app.command()
def demo():
    """
    Run arable agent demonstrations
    
    Shows the hybrid CLI-agent system in action with sample data
    """
    console.print("[bold blue]🎬 arable agent demo[/bold blue]")
    
    # Auto-discover agents
    registry.auto_discover_agents()
    
    console.print("\n[bold]Demo 1: Document Extraction Agent[/bold]")
    
    # Create a sample document for demo
    sample_doc_path = "/tmp/arable_demo.txt"
    sample_content = """
    PROJECT PROPOSAL - DEMO
    Project Number: DEMO-2025-001
    Customer: ARABLE Demo Client
    Project Value: $125,000
    Start Date: 2025-06-01
    Milestones:
    - Design Phase: 2025-06-15
    - Development: 2025-07-30
    - Testing: 2025-08-15
    """
    
    try:
        with open(sample_doc_path, 'w') as f:
            f.write(sample_content)
            
        console.print(f"Created sample document: {sample_doc_path}")
        
        # Run document extraction
        task_data = {
            "document_path": sample_doc_path,
            "extraction_type": "proposal"
        }
        
        import asyncio
        console.print("Running document extraction...")
        
        result = asyncio.run(orchestrator.execute_single_task("documentextractor", task_data))
        
        if result["success"]:
            console.print("[green]✅ Document extraction completed![/green]")
            
            extracted = result["result"]["extracted_data"]["extracted_fields"]
            console.print(f"\n[bold]Extracted Data:[/bold]")
            console.print(f"  Project: {extracted.get('project_number', 'N/A')}")
            console.print(f"  Customer: {extracted.get('customer_name', 'N/A')}")
            console.print(f"  Value: ${extracted.get('project_value', 'N/A'):,}")
            
        else:
            console.print(f"[red]❌ Demo failed: {result.get('error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Demo setup failed: {e}[/red]")
    finally:
        # Cleanup
        import os
        if os.path.exists(sample_doc_path):
            os.remove(sample_doc_path)
            
    console.print("\n[bold]Demo 2: Multi-Agent Workflow (Coming Soon)[/bold]")
    console.print("This will demonstrate document extraction → Monday.com project creation")

if __name__ == "__main__":
    app()
