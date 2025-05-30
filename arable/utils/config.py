"""Configuration management for ARABLE with environment variable support
Migrated from src/monday_automation/config.py
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class MondayConfig:
    """Monday.com API configuration"""
    api_token: str
    master_board_id: str
    template_board_id: str
    active_projects_folder_id: str
    master_columns: Dict[str, str]
    project_board_columns: Dict[str, str]


@dataclass
class GoogleSheetsConfig:
    """Google Sheets configuration"""
    credentials_path: str
    sheet_name: str


@dataclass
class Config:
    """Main configuration container"""
    monday: MondayConfig
    google_sheets: GoogleSheetsConfig
    milestone_mappings: Dict[str, Dict[str, Any]]
    testing: Dict[str, Any]
    logging: Dict[str, str]


class ConfigError(Exception):
    """Configuration-related errors"""
    pass


def load_environment_variables() -> None:
    """
    Load environment variables from .env file
    
    Looks for .env file in current directory and parent directories
    """
    # Find .env file
    current_dir = Path.cwd()
    env_file = None
    
    # Search up the directory tree for .env file
    for path in [current_dir] + list(current_dir.parents):
        potential_env = path / ".env"
        if potential_env.exists():
            env_file = potential_env
            break
    
    if env_file:
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from: {env_file}")
    else:
        print("⚠️  No .env file found - using system environment variables only")


def find_config_file(config_name: str = "config.yaml") -> Path:
    """
    Find configuration file in standard locations

    Args:
        config_name: Name of config file

    Returns:
        Path to config file

    Raises:
        ConfigError: If config file not found
    """
    # Search paths in order of preference
    search_paths = [
        Path.cwd() / "config" / config_name,  # ./config/config.yaml
        Path.cwd() / config_name,  # ./config.yaml
        Path(__file__).parent.parent.parent / "config" / config_name,  # Package config
    ]

    for path in search_paths:
        if path.exists():
            return path

    raise ConfigError(
        f"Config file '{config_name}' not found in any of: {[str(p) for p in search_paths]}"
    )


def resolve_path(path: str, config_dir: Path) -> str:
    """
    Resolve relative paths relative to config directory

    Args:
        path: Path string (absolute or relative)
        config_dir: Directory containing config file

    Returns:
        Resolved absolute path
    """
    if os.path.isabs(path):
        return path

    # Handle case where path is already relative to current working directory
    if Path(path).exists():
        return str(Path(path).resolve())

    # Try relative to config directory
    resolved = (config_dir / path).resolve()
    return str(resolved)


def get_required_env_var(var_name: str, description: str = "") -> str:
    """
    Get required environment variable with helpful error message
    
    Args:
        var_name: Environment variable name
        description: Human-readable description
        
    Returns:
        Environment variable value
        
    Raises:
        ConfigError: If environment variable is not set
    """
    value = os.getenv(var_name)
    if not value:
        desc_text = f" ({description})" if description else ""
        raise ConfigError(
            f"Required environment variable {var_name}{desc_text} is not set. "
            f"Please add it to your .env file or set it in your environment."
        )
    return value


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file and environment variables

    Args:
        config_path: Optional path to config file

    Returns:
        Parsed configuration object

    Raises:
        ConfigError: If config file cannot be loaded or parsed
    """
    # Load environment variables first
    load_environment_variables()
    
    try:
        if config_path:
            config_file = Path(config_path)
            if not config_file.exists():
                raise ConfigError(f"Config file not found: {config_path}")
        else:
            config_file = find_config_file()

        config_dir = config_file.parent

        with open(config_file, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        # Get credentials from environment variables
        monday_api_token = get_required_env_var("MONDAY_API_TOKEN", "Monday.com API token")
        sheets_credentials_path = get_required_env_var("GOOGLE_SHEETS_CREDENTIALS_PATH", "Google Sheets credentials file path")
        sheets_sheet_name = get_required_env_var("GOOGLE_SHEETS_SHEET_NAME", "Google Sheets sheet name")

        # Resolve relative paths for credentials
        sheets_credentials_path = resolve_path(sheets_credentials_path, config_dir)

        # Build Monday config with API token from environment
        monday_config_data = raw_config["monday"].copy()
        monday_config_data["api_token"] = monday_api_token

        # Build Google Sheets config with credentials from environment
        google_sheets_config = GoogleSheetsConfig(
            credentials_path=sheets_credentials_path,
            sheet_name=sheets_sheet_name
        )

        # Build structured config
        config = Config(
            monday=MondayConfig(**monday_config_data),
            google_sheets=google_sheets_config,
            milestone_mappings=raw_config["milestone_mappings"],
            testing=raw_config.get(
                "testing", {"test_project_number": None, "enabled": True}
            ),
            logging=raw_config.get(
                "logging", {"level": "INFO", "file": "logs/arable.log"}
            ),
        )

        return config

    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {e}")
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in config file: {e}")
    except KeyError as e:
        raise ConfigError(f"Missing required config key in YAML: {e}")
    except Exception as e:
        raise ConfigError(f"Error loading config: {e}")


def validate_config(config: Config) -> None:
    """
    Enhanced configuration validation with milestone checking

    Args:
        config: Configuration to validate

    Raises:
        ConfigError: If configuration is invalid
    """
    # Basic validation
    if not config.monday.api_token:
        raise ConfigError("Monday.com API token is required (set MONDAY_API_TOKEN in .env)")
    
    if not config.google_sheets.credentials_path:
        raise ConfigError("Google Sheets credentials path is required (set GOOGLE_SHEETS_CREDENTIALS_PATH in .env)")
    
    if not config.google_sheets.sheet_name:
        raise ConfigError("Google Sheets sheet name is required (set GOOGLE_SHEETS_SHEET_NAME in .env)")
    
    # Check credentials file exists
    if not Path(config.google_sheets.credentials_path).exists():
        raise ConfigError(f"Google Sheets credentials file not found: {config.google_sheets.credentials_path}")

    # Milestone validation
    milestone_mappings = config.milestone_mappings

    # Check that we have both phase and group mappings
    if not milestone_mappings.get("phase"):
        raise ConfigError("Milestone phase mappings are required")

    if not milestone_mappings.get("groups"):
        raise ConfigError("Milestone group mappings are required")

    # Check for consistency between phase and group mappings
    phase_milestones = set(milestone_mappings["phase"].keys())
    group_milestones = set(milestone_mappings["groups"].keys())

    # Warn about milestones with phase mapping but no group mapping
    phase_only = phase_milestones - group_milestones
    if phase_only:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Milestones with phase mapping but no group mapping: {phase_only}"
        )

    # Warn about milestones with group mapping but no phase mapping
    group_only = group_milestones - phase_milestones
    if group_only:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Milestones with group mapping but no phase mapping: {group_only}"
        )

    # Validate phase IDs are reasonable (0-8 range for Monday.com)
    invalid_phases = []
    for milestone_type, phase_id in milestone_mappings["phase"].items():
        if not isinstance(phase_id, int) or phase_id < 0 or phase_id > 8:
            invalid_phases.append(f"{milestone_type}: {phase_id}")

    if invalid_phases:
        raise ConfigError(f"Invalid phase IDs (must be 0-8): {invalid_phases}")


def create_config_template(output_path: str = "config/config.yaml") -> None:
    """
    Create configuration file templates (both YAML and .env)

    Args:
        output_path: Where to create the YAML template
    """
    # Create YAML config template
    yaml_template = """# ARABLE Configuration
# Agentic Runtime And Business Logic Engine
# 
# NOTE: Credentials are now loaded from .env file
# This file contains only structural configuration

monday:
  # Board and folder IDs (get from Monday.com URLs)
  master_board_id: "your_master_board_id"
  template_board_id: "your_template_board_id"
  active_projects_folder_id: "your_folder_id"
  
  # Column IDs for master board (inspect board to get these)
  master_columns:
    project_number: "your_project_number_column_id"
    project_milestones: "your_milestones_column_id"
    customer: "your_customer_column_id"
    start_date: "your_start_date_column_id"
    status: "status"  # Usually just "status"
  
  # Column IDs for project boards
  project_board_columns:
    timeline: "your_timeline_column_id"
    duration: "your_duration_column_id"
    phase: "your_phase_column_id"
    status: "status"
    master_link: "your_master_link_column_id"
    rsi_milestone_id: "your_rsi_milestone_id_column_id"  # For sync checking

# Map milestone types to Monday.com phase IDs and group IDs
milestone_mappings:
  # Phase mapping (0=Design, 1=Introduction, 2=Procurement, 3=Assembly, 4=Testing, 6=Shipping, 7=Installation, 8=Debrief)
  phase:
    "Kickoff": 1
    "SRR": 0
    "PDR": 0
    "CDR": 0
    "Release To Production": 2
    "Source Inspection": 2
    "Begin Assembly": 3
    "Build": 3
    "FAT": 4
    "CERT": 4
    "Ship": 6
    "Deliver via RSI FTP": 6
    "Travel": 7
    "Site Survey": 7
    "Pre-Install Meeting": 7
    "Ready For Training": 7
    "Install": 7
    "I TRDWN": 7
    "TRDWN": 7
    "SiteSpt": 7
    "ACCPT - Acceptance": 4
    "C END": 8
    "Debrief": 8
  
  # Group mapping (organize milestones into Monday.com board groups)
  groups:
    "Kickoff": "topics"
    "Debrief": "topics"
    "C END": "topics"
    "Release To Production": "group_purchasing"
    "Source Inspection": "group_purchasing"
    "SRR": "group_engineering"
    "PDR": "group_engineering"
    "CDR": "group_engineering"
    "Build": "group_operations"
    "Begin Assembly": "group_operations"
    "Ship": "group_operations"
    "Deliver via RSI FTP": "group_operations"
    "FAT": "group_testing"
    "CERT": "group_testing"
    "ACCPT - Acceptance": "group_testing"
    "Install": "group_field_service"
    "Pre-Install Meeting": "group_field_service"
    "Site Survey": "group_field_service"
    "Travel": "group_field_service"
    "I TRDWN": "group_field_service"
    "TRDWN": "group_field_service"
    "SiteSpt": "group_field_service"
    "Ready For Training": "group_field_service"

# Testing configuration
testing:
  test_project_number: null  # Set to specific project number for testing
  enabled: true

# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "logs/arable.log"
"""

    # Create .env template
    env_template = """# ARABLE Environment Variables
# Copy this file to .env and fill in your actual credentials
# DO NOT commit .env to version control

# Monday.com API Configuration
MONDAY_API_TOKEN=your_monday_api_token_here

# Google Sheets Configuration  
GOOGLE_SHEETS_CREDENTIALS_PATH=credentials/google-service-account.json
GOOGLE_SHEETS_SHEET_NAME=Your Google Sheet Name

# Optional: Claude API (for future agent functionality)
CLAUDE_API_KEY=your_claude_api_key_here

# Optional: Development/Testing Settings
ENVIRONMENT=development
DEBUG_MODE=false
LOG_LEVEL=INFO
"""

    # Write YAML config
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(yaml_template)

    # Write .env template
    env_file = Path(".env.example")
    with open(env_file, "w") as f:
        f.write(env_template)

    print(f"✅ Configuration template created at: {output_file}")
    print(f"✅ Environment template created at: {env_file}")
    print("\n📝 Next steps:")
    print("   1. Copy .env.example to .env: cp .env.example .env")
    print("   2. Edit .env with your actual credentials")
    print("   3. Update config/config.yaml with your Monday.com board IDs")
    print("   4. Customize milestone mappings for your workflow")
    print("   5. Add RSi milestone ID column to your Monday board template")
    print("\n🔒 Security notes:")
    print("   • .env file contains secrets - DO NOT commit to version control")
    print("   • Add .env to your .gitignore file")
    print("   • config.yaml is safe to commit (no credentials)")
