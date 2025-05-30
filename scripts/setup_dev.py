#!/usr/bin/env python3
"""
ARABLE Development Setup Script
Sets up development environment for ARABLE agent system
"""

import subprocess
import sys
from pathlib import Path
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def setup_virtual_environment():
    """Set up Python virtual environment"""
    if not run_command("python -m venv arable_env", "Creating virtual environment"):
        return False
    
    # Activation instructions vary by OS
    if os.name == 'nt':  # Windows
        activate_cmd = "arable_env\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_cmd = "source arable_env/bin/activate"
    
    print(f"📝 To activate: {activate_cmd}")
    return True

def install_dependencies():
    """Install ARABLE dependencies"""
    pip_cmd = "arable_env/bin/pip" if os.name != 'nt' else "arable_env\\Scripts\\pip"
    
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -e .", "Installing ARABLE in development mode"),
        (f"{pip_cmd} install -e .[dev]", "Installing development dependencies")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    return True

def setup_pre_commit():
    """Set up pre-commit hooks"""
    pip_cmd = "arable_env/bin/pip" if os.name != 'nt' else "arable_env\\Scripts\\pip"
    pre_commit_cmd = "arable_env/bin/pre-commit" if os.name != 'nt' else "arable_env\\Scripts\\pre-commit"
    
    commands = [
        (f"{pip_cmd} install pre-commit", "Installing pre-commit"),
        (f"{pre_commit_cmd} install", "Setting up pre-commit hooks")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    return True

def create_config_files():
    """Create initial configuration files"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Create example configuration
    arable_config = config_dir / "arable.example.yaml"
    arable_config.write_text("""# ARABLE Configuration Example
# Copy to arable.yaml and customize for your environment

system:
  name: "ARABLE Development"
  version: "0.2.0"
  log_level: "INFO"

agents:
  max_concurrent: 5
  memory_limit_mb: 512
  default_timeout: 300

integrations:
  monday:
    api_url: "https://api.monday.com/v2"
    api_token: "${MONDAY_API_TOKEN}"
    rate_limit: 60  # requests per minute
    
  zoho_crm:
    api_url: "https://www.zohoapis.com/crm/v2"
    client_id: "${ZOHO_CLIENT_ID}"
    client_secret: "${ZOHO_CLIENT_SECRET}"
    
  google_drive:
    credentials_file: "config/google_credentials.json"
    scopes:
      - "https://www.googleapis.com/auth/drive.readonly"
      - "https://www.googleapis.com/auth/spreadsheets"
    
  claude_api:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-sonnet-20240229"
    max_tokens: 4000

database:
  # Legacy SQL database connection
  host: "${DB_HOST}"
  port: 1433
  database: "${DB_NAME}"
  username: "${DB_USER}"
  password: "${DB_PASSWORD}"

storage:
  cache_dir: "data/cache"
  backup_dir: "data/backups"
  extract_dir: "data/extracts"
""")
    
    # Create agents configuration
    agents_config = config_dir / "agents.yaml"
    agents_config.write_text("""# ARABLE Agents Configuration

agents:
  document_extractor:
    class: "arable.agents.specialized.DocumentExtractorAgent"
    config:
      supported_formats: ["pdf", "docx", "txt"]
      max_file_size_mb: 50
      extraction_timeout: 120
      
  crm_matcher:
    class: "arable.agents.specialized.CRMMatcherAgent"
    config:
      similarity_threshold: 0.85
      max_candidates: 10
      fuzzy_matching: true
      
  data_reconciler:
    class: "arable.agents.specialized.DataReconcilerAgent"
    config:
      conflict_resolution: "manual"
      backup_before_update: true
      validation_strict: true
      
  monday_manager:
    class: "arable.agents.specialized.MondayManagerAgent"
    config:
      board_templates_dir: "config/monday_templates"
      default_workspace: "RSi Visual Systems"
      
  workflow_assistant:
    class: "arable.agents.specialized.WorkflowAssistantAgent"
    config:
      max_workflow_steps: 50
      parallel_execution: true
      rollback_on_failure: true

workflows:
  document_to_crm:
    name: "Document Extraction to CRM Sync"
    steps:
      - agent: "document_extractor"
        task: "extract_structured_data"
      - agent: "crm_matcher"
        task: "find_matching_records"
      - agent: "data_reconciler"
        task: "resolve_conflicts"
        
  full_system_sync:
    name: "Complete Cross-Platform Reconciliation"
    steps:
      - agent: "crm_matcher"
        task: "audit_data_consistency"
      - agent: "data_reconciler"
        task: "generate_reconciliation_plan"
      - agent: "monday_manager"
        task: "update_project_boards"
""")
    
    # Create environment file
    env_file = Path(".env.example")
    env_file.write_text("""# ARABLE Environment Variables
# Copy to .env and fill in your actual values

# API Keys
MONDAY_API_TOKEN=your_monday_api_token_here
ZOHO_CLIENT_ID=your_zoho_client_id_here
ZOHO_CLIENT_SECRET=your_zoho_client_secret_here
ANTHROPIC_API_KEY=your_claude_api_key_here

# Database Connection
DB_HOST=your_database_host
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password

# Development Settings
ARABLE_ENV=development
ARABLE_LOG_LEVEL=DEBUG
""")
    
    print("✅ Configuration files created")
    return True

def create_pre_commit_config():
    """Create pre-commit configuration"""
    pre_commit_config = Path(".pre-commit-config.yaml")
    pre_commit_config.write_text("""repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: check-yaml
      - id: check-json
      
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
""")
    
    print("✅ Pre-commit configuration created")
    return True

def test_installation():
    """Test ARABLE installation"""
    python_cmd = "arable_env/bin/python" if os.name != 'nt' else "arable_env\\Scripts\\python"
    
    test_commands = [
        (f"{python_cmd} -c 'import arable; print(\"ARABLE package imported successfully\")'", "Testing package import"),
        (f"{python_cmd} -m arable.cli.main info", "Testing CLI functionality")
    ]
    
    for cmd, desc in test_commands:
        if not run_command(cmd, desc):
            return False
    return True

def main():
    """Main setup function"""
    print("🚀 ARABLE Development Environment Setup")
    print("=======================================")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found. Please run from ARABLE project root.")
        return False
    
    steps = [
        (setup_virtual_environment, "Virtual Environment Setup"),
        (install_dependencies, "Dependency Installation"),
        (create_config_files, "Configuration Setup"),
        (create_pre_commit_config, "Pre-commit Setup"),
        (setup_pre_commit, "Pre-commit Installation"),
        (test_installation, "Installation Testing")
    ]
    
    for step_func, step_name in steps:
        print(f"\n📋 {step_name}")
        print("-" * (len(step_name) + 4))
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print("\n🎉 ARABLE Development Environment Setup Complete!")
    print("\nNext Steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':
        print("   arable_env\\Scripts\\activate")
    else:
        print("   source arable_env/bin/activate")
    print("2. Copy and customize configuration:")
    print("   cp config/arable.example.yaml config/arable.yaml")
    print("   cp .env.example .env")
    print("3. Test the CLI:")
    print("   arable info")
    print("4. Start developing agents!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
