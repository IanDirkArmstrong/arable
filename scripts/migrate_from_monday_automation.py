#!/usr/bin/env python3
"""
ARABLE Migration Script
Migrates from monday_automation to ARABLE agent-based architecture
"""

import os
import shutil
from pathlib import Path
import re
from typing import List, Dict

class ARABLEMigrator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_dir = project_root / "migration_backup"
        
    def create_backup(self):
        """Create backup of current state"""
        print("🔄 Creating migration backup...")
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Backup key directories
        for dir_name in ["src", "config", "tests"]:
            src_dir = self.project_root / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, self.backup_dir / dir_name)
        
        # Backup key files
        for file_name in ["requirements.txt", "pyproject.toml", "run.py"]:
            src_file = self.project_root / file_name
            if src_file.exists():
                shutil.copy2(src_file, self.backup_dir / file_name)
                
        print("✅ Backup created in migration_backup/")
    
    def create_new_structure(self):
        """Create new ARABLE directory structure"""
        print("🏗️  Creating new ARABLE structure...")
        
        # Main package structure
        structure = {
            "arable": {
                "__init__.py": "",
                "cli": {
                    "__init__.py": "",
                    "main.py": "",
                    "commands": {
                        "__init__.py": "",
                        "agents.py": "",
                        "data.py": "",
                        "config.py": "",
                        "monitor.py": ""
                    },
                    "ui": {
                        "__init__.py": "",
                        "progress.py": "",
                        "tables.py": "",
                        "prompts.py": ""
                    }
                },
                "agents": {
                    "__init__.py": "",
                    "base.py": "",
                    "registry.py": "",
                    "orchestrator.py": "",
                    "memory.py": "",
                    "specialized": {
                        "__init__.py": "",
                        "document_extractor.py": "",
                        "crm_matcher.py": "",
                        "data_reconciler.py": "",
                        "monday_manager.py": "",
                        "workflow_assistant.py": ""
                    }
                },
                "integrations": {
                    "__init__.py": "",
                    "monday.py": "",
                    "zoho_crm.py": "",
                    "google_drive.py": "",
                    "sheets.py": "",
                    "sql_legacy.py": "",
                    "claude_api.py": ""
                },
                "data": {
                    "__init__.py": "",
                    "models.py": "",
                    "extractors.py": "",
                    "matchers.py": "",
                    "reconcilers.py": ""
                },
                "config": {
                    "__init__.py": "",
                    "settings.py": "",
                    "agent_configs.py": ""
                },
                "utils": {
                    "__init__.py": "",
                    "logging.py": "",
                    "validation.py": "",
                    "exceptions.py": ""
                }
            },
            "scripts": {
                "setup_dev.py": "",
                "generate_agent_templates.py": ""
            },
            "docs": {
                "README.md": "",
                "agents": {},
                "integrations": {},
                "workflows": {}
            }
        }
        
        self._create_structure(self.project_root, structure)
        print("✅ New structure created")
    
    def _create_structure(self, base_path: Path, structure: Dict):
        """Recursively create directory structure"""
        for name, content in structure.items():
            path = base_path / name
            if isinstance(content, dict):
                path.mkdir(exist_ok=True)
                self._create_structure(path, content)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.write_text(content)
    
    def migrate_existing_code(self):
        """Migrate existing monday_automation code to new structure"""
        print("🔄 Migrating existing code...")
        
        old_src = self.project_root / "src" / "monday_automation"
        new_integrations = self.project_root / "arable" / "integrations"
        new_utils = self.project_root / "arable" / "utils"
        
        if not old_src.exists():
            print("⚠️  No src/monday_automation directory found to migrate")
            return
        
        # Migration mapping
        migrations = [
            (old_src / "monday_api.py", new_integrations / "monday.py"),
            (old_src / "google_sheets.py", new_integrations / "sheets.py"),
            (old_src / "config.py", new_utils / "config_legacy.py"),
            (old_src / "logger.py", new_utils / "logging.py"),
            (old_src / "main.py", new_integrations / "legacy_main.py"),
            (old_src / "rsi_validation.py", new_utils / "rsi_validation.py")
        ]
        
        for old_file, new_file in migrations:
            if old_file.exists():
                new_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(old_file, new_file)
                print(f"  ✅ Migrated {old_file.name} → {new_file.relative_to(self.project_root)}")
        
        # Update imports in migrated files
        self._update_imports()
    
    def _update_imports(self):
        """Update import statements in migrated files"""
        print("🔄 Updating import statements...")
        
        arable_dir = self.project_root / "arable"
        python_files = list(arable_dir.rglob("*.py"))
        
        for py_file in python_files:
            if py_file.name == "__init__.py":
                continue
                
            try:
                content = py_file.read_text()
                # Replace monday_automation imports with arable imports
                content = re.sub(
                    r'from monday_automation',
                    'from arable',
                    content
                )
                content = re.sub(
                    r'import monday_automation',
                    'import arable',
                    content
                )
                py_file.write_text(content)
            except Exception as e:
                print(f"  ⚠️  Could not update imports in {py_file}: {e}")
    
    def update_requirements(self):
        """Update requirements.txt with new dependencies"""
        print("🔄 Updating requirements...")
        
        new_requirements = [
            "# Existing dependencies",
            "pyyaml>=6.0",
            "requests>=2.28.0", 
            "python-dotenv>=0.19.0",
            "",
            "# New ARABLE dependencies",
            "typer[all]>=0.9.0",
            "rich>=13.0.0",
            "textual>=0.44.0",
            "pydantic>=2.0.0",
            "anthropic>=0.8.0",
            "",
            "# Development dependencies",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0"
        ]
        
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            # Backup existing requirements
            shutil.copy2(req_file, self.backup_dir / "requirements.txt.bak")
        
        req_file.write_text("\n".join(new_requirements))
        print("✅ Requirements updated")
    
    def create_initial_files(self):
        """Create initial implementation files"""
        print("🔄 Creating initial implementation files...")
        
        # Create main CLI entry point
        cli_main = self.project_root / "arable" / "cli" / "main.py"
        cli_main.write_text('''#!/usr/bin/env python3
"""
ARABLE CLI - Main entry point
Agentic Runtime And Business Logic Engine
"""

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="arable",
    help="[bold blue]ARABLE[/bold blue] - Agentic Runtime And Business Logic Engine",
    rich_markup_mode="rich"
)

console = Console()

@app.command()
def info():
    """Show ARABLE system information"""
    console.print(Panel(
        "[bold blue]ARABLE[/bold blue] - Agentic Runtime And Business Logic Engine\\n\\n"
        "🤖 Intelligent document extraction\\n"
        "🔄 Cross-platform data reconciliation\\n"
        "⚡ Agent-driven workflow automation\\n"
        "🎯 Business logic orchestration",
        title="System Information",
        border_style="blue"
    ))

@app.command()
def migrate():
    """Run migration from monday_automation to ARABLE"""
    console.print("[yellow]Migration functionality coming soon...[/yellow]")

if __name__ == "__main__":
    app()
''')
        
        # Create base agent class
        base_agent = self.project_root / "arable" / "agents" / "base.py"
        base_agent.write_text('''"""
Base agent class for ARABLE agent system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

class AgentCapability(BaseModel):
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]

class AgentState(BaseModel):
    agent_id: str
    status: str
    memory: Dict[str, Any] = {}
    last_action: Optional[str] = None
    metrics: Dict[str, float] = {}

class BaseAgent(ABC):
    """Base class for all ARABLE agents"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.state = AgentState(agent_id=agent_id, status="initialized")
        self.logger = logging.getLogger(f"arable.agents.{agent_id}")
        
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific task"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Define what this agent can do"""
        pass
        
    def update_memory(self, key: str, value: Any):
        """Update agent memory state"""
        self.state.memory[key] = value
        
    def get_memory(self, key: str) -> Any:
        """Retrieve from agent memory"""
        return self.state.memory.get(key)
        
    def get_status(self) -> str:
        """Get current agent status"""
        return self.state.status
        
    def set_status(self, status: str):
        """Update agent status"""
        self.state.status = status
        self.logger.info(f"Agent {self.agent_id} status: {status}")
''')
        
        print("✅ Initial files created")
    
    def update_pyproject_toml(self):
        """Update pyproject.toml for new structure"""
        print("🔄 Updating pyproject.toml...")
        
        pyproject_content = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "arable"
version = "0.2.0"
description = "Agentic Runtime And Business Logic Engine"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.0.0",
    "textual>=0.44.0",
    "pydantic>=2.0.0",
    "anthropic>=0.8.0",
    "pyyaml>=6.0",
    "requests>=2.28.0",
    "python-dotenv>=0.19.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.5.0"
]

[project.scripts]
arable = "arable.cli.main:app"

[tool.setuptools.packages.find]
where = ["."]
include = ["arable*"]

[tool.black]
line-length = 88
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
'''
        
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            shutil.copy2(pyproject_file, self.backup_dir / "pyproject.toml.bak")
        
        pyproject_file.write_text(pyproject_content)
        print("✅ pyproject.toml updated")
    
    def run_migration(self):
        """Execute complete migration process"""
        print("🚀 Starting ARABLE migration...")
        print("   From: monday_automation")
        print("   To: ARABLE (Agentic Runtime And Business Logic Engine)")
        print()
        
        try:
            self.create_backup()
            self.create_new_structure()
            self.migrate_existing_code()
            self.update_requirements()
            self.create_initial_files()
            self.update_pyproject_toml()
            
            print()
            print("🎉 Migration completed successfully!")
            print()
            print("Next steps:")
            print("1. Review migrated code in arable/ directory")
            print("2. Install new dependencies: pip install -e .")
            print("3. Test CLI: python -m arable.cli.main info")
            print("4. Begin agent development")
            print()
            print("📁 Backup available in: migration_backup/")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("📁 Backup preserved in: migration_backup/")
            raise


def main():
    """Main migration script entry point"""
    project_root = Path(__file__).parent.parent  # Go up from scripts/ to project root
    migrator = ARABLEMigrator(project_root)
    migrator.run_migration()


if __name__ == "__main__":
    main()
