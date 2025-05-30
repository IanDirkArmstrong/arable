# ARABLE File System Index

_Last Updated: 2025-05-29_  
_Maintained by: Index Keeper Agent_
_Project: ARABLE (Agentic Runtime And Business Logic Engine)_

## Project Status: Migration to Agent-Based Architecture

**Current State**: Transitioning from monday_automation to ARABLE agent system  
**Target Architecture**: Multi-agent platform for document extraction, data reconciliation, and workflow automation  
**Key Technologies**: Typer CLI, Rich UI, Pydantic models, Claude API integration

## Project Root Files

| File                       | Purpose                                  | Status | Notes                        |
| -------------------------- | ---------------------------------------- | ------ | ---------------------------- |
| `README.md`                | Project overview and setup instructions  | Active | Main project documentation   |
| `requirements.txt`         | Python dependencies                      | Active | Standard pip requirements    |
| `pyproject.toml`           | Project configuration and build settings | Active | Modern Python project config |
| `run.py`                   | Main application entry point             | Active | Primary execution script     |
| `setup_dev.py`             | Development environment setup            | Active | Developer onboarding         |
| `generate_rsi_config.py`   | RSi-specific configuration generator     | Active | Client customization         |
| `final_validation.py`      | End-to-end validation script             | Active | QA and deployment validation |
| `test_rsi_validation.py`   | RSi validation unit tests                | Active | Client-specific testing      |
| `test_runner.py`           | Test execution utility                   | Active | Test orchestration           |
| `zoho_crm_data_model.json` | Zoho CRM schema definition               | Active | Integration reference        |

## Source Code (`/src/monday_automation/`)

| File                | Purpose                       | Status | Dependencies             |
| ------------------- | ----------------------------- | ------ | ------------------------ |
| `__init__.py`       | Package initialization        | Active | None                     |
| `main.py`           | Core application logic        | Active | All modules              |
| `config.py`         | Configuration management      | Active | yaml config files        |
| `monday_api.py`     | Monday.com API integration    | Active | requests, config         |
| `google_sheets.py`  | Google Sheets API integration | Active | google-api-python-client |
| `logger.py`         | Logging configuration         | Active | Python logging           |
| `rsi_validation.py` | RSi-specific validation logic | Active | main, config             |

## Configuration (`/config/`)

| File                  | Purpose                  | Status | Notes                                 |
| --------------------- | ------------------------ | ------ | ------------------------------------- |
| `config.yaml`         | Production configuration | Active | Contains sensitive data - not in repo |
| `config.example.yaml` | Configuration template   | Active | Safe to commit - no secrets           |

## Data & CRM Integration (`/data/`)

| Directory/File  | Purpose                  | Status  | Size          | Notes                            |
| --------------- | ------------------------ | ------- | ------------- | -------------------------------- |
| `crm/backups/`  | Zoho CRM data exports    | Archive | 65+ CSV files | Historical data snapshots        |
| `crm/metadata/` | CRM schema and structure | Active  | 15 files      | Field definitions, layouts, etc. |
| `crm/schema/`   | Data model definitions   | Empty   | -             | Future schema documentation      |

### Key CRM Backup Files

- `Accounts_001.csv` - Company/account records
- `Contacts_001.csv` - Individual contact records
- `Prospects_001.csv` - Sales pipeline data
- `Products_001.csv` - Product catalog
- `Pricing_Offers_001.csv` - Quote and pricing data
- `Sales_Orders_001.csv` - Order management
- Custom modules: Training Centers, Visuals, Certifications

## Testing (`/tests/`)

| File          | Purpose                           | Status | Coverage             |
| ------------- | --------------------------------- | ------ | -------------------- |
| `conftest.py` | pytest configuration and fixtures | Active | Test setup           |
| `pytest.ini`  | pytest settings                   | Active | Test runner config   |
| `Makefile`    | Test automation commands          | Active | Build/test shortcuts |
| `test_*.py`   | Unit test modules                 | Active | Per-module testing   |

### Test Coverage

- `test_config.py` - Configuration loading and validation
- `test_google_sheets.py` - Google Sheets API integration
- `test_integration.py` - End-to-end integration tests
- `test_logger.py` - Logging functionality
- `test_main.py` - Core application logic
- `test_monday_api.py` - Monday.com API integration

## Logs (`/logs/`)

| File                    | Purpose                  | Status | Retention     |
| ----------------------- | ------------------------ | ------ | ------------- |
| `monday_automation.log` | Application runtime logs | Active | Rotated daily |

## Migration & Development Scripts (`/scripts/`)

| File                                | Purpose                               | Status  | Usage                                              |
| ----------------------------------- | ------------------------------------- | ------- | -------------------------------------------------- |
| `migrate_from_monday_automation.py` | Complete migration from old structure | Ready   | `python scripts/migrate_from_monday_automation.py` |
| `setup_dev.py`                      | Development environment setup         | Ready   | `python scripts/setup_dev.py`                      |
| `generate_agent_templates.py`       | Agent scaffolding generator           | Planned | Future agent development                           |

## New Architecture Files (Post-Migration)

### ARABLE Core Package (`/arable/`)

| Module                       | Purpose                           | Status           | Dependencies                     |
| ---------------------------- | --------------------------------- | ---------------- | -------------------------------- |
| `cli/main.py`                | Typer-based CLI entry point       | Template created | typer, rich                      |
| `cli/commands/`              | CLI command modules               | Planned          | Per-command functionality        |
| `cli/ui/`                    | Rich UI components                | Planned          | rich, progress bars              |
| `agents/base.py`             | Base agent architecture           | Template created | pydantic, abc                    |
| `agents/registry.py`         | Agent discovery/management        | Planned          | Dynamic loading                  |
| `agents/orchestrator.py`     | Multi-agent coordination          | Planned          | asyncio, workflows               |
| `agents/memory.py`           | Agent state management            | Planned          | json, persistence                |
| `agents/specialized/`        | Specialized agent implementations | Planned          | domain-specific logic            |
| `integrations/monday.py`     | Monday.com API (migrated)         | Active           | requests, rate limiting          |
| `integrations/sheets.py`     | Google Sheets API (migrated)      | Active           | google-api-client                |
| `integrations/claude_api.py` | Claude API integration            | Planned          | anthropic SDK                    |
| `integrations/zoho_crm.py`   | Zoho CRM integration              | Planned          | Enhanced from backups            |
| `data/models.py`             | Pydantic data models              | Planned          | cross-platform schemas           |
| `data/extractors.py`         | Document parsing logic            | Planned          | PDF, DOCX, structured extraction |
| `data/matchers.py`           | Intelligent matching algorithms   | Planned          | fuzzy matching, ML               |
| `config/settings.py`         | Pydantic configuration            | Planned          | environment-based config         |
| `utils/logging.py`           | Enhanced logging (migrated)       | Active           | rich integration                 |

### Specialized Agents (Planned)

| Agent                    | Purpose                                    | Input Types              | Output Types                     |
| ------------------------ | ------------------------------------------ | ------------------------ | -------------------------------- |
| `DocumentExtractorAgent` | Extract structured data from business docs | PDF, DOCX, TXT           | JSON schemas                     |
| `CRMMatcherAgent`        | Match extracted data with CRM records      | JSON data, CRM records   | Match candidates with confidence |
| `DataReconcilerAgent`    | Resolve data conflicts across systems      | Conflict sets            | Reconciliation plans             |
| `MondayManagerAgent`     | Manage Monday.com boards and workflows     | Project data, milestones | Board updates, automations       |
| `WorkflowAssistantAgent` | Orchestrate multi-step business processes  | Workflow definitions     | Execution results                |

## Configuration Templates (New)

| File                         | Purpose                         | Status  | Notes                    |
| ---------------------------- | ------------------------------- | ------- | ------------------------ |
| `config/arable.example.yaml` | Main configuration template     | Created | Copy to arable.yaml      |
| `config/agents.yaml`         | Agent definitions and workflows | Created | Runtime agent config     |
| `.env.example`               | Environment variables template  | Created | API keys, DB credentials |
| `.pre-commit-config.yaml`    | Code quality automation         | Created | black, isort, mypy       |

## Legacy Files (Pre-Migration)

### Source Code (`/src/monday_automation/`) - TO BE MIGRATED

| File                | Purpose                       | Status | Migration Target                     |
| ------------------- | ----------------------------- | ------ | ------------------------------------ |
| `main.py`           | Core application logic        | Active | `arable/integrations/legacy_main.py` |
| `monday_api.py`     | Monday.com API integration    | Active | `arable/integrations/monday.py`      |
| `google_sheets.py`  | Google Sheets API integration | Active | `arable/integrations/sheets.py`      |
| `config.py`         | Configuration management      | Active | `arable/utils/config_legacy.py`      |
| `logger.py`         | Logging configuration         | Active | `arable/utils/logging.py`            |
| `rsi_validation.py` | RSi-specific validation logic | Active | `arable/utils/rsi_validation.py`     |

## System Integration Points (Current + Planned)

### Monday.com API

- **Current**: Primary integration target for project management
- **Planned**: Agent-driven board creation and milestone tracking
- Rate limits: 60 requests/minute
- Authentication: API token in config
- Main modules: `monday_api.py` → `arable/integrations/monday.py`

### Google Sheets API

- **Current**: Data staging and validation
- **Planned**: Agent-driven data extraction and temporary storage
- Service account authentication
- Main modules: `google_sheets.py` → `arable/integrations/sheets.py`

### Zoho CRM

- **Current**: Data source for account/contact sync (CSV export-based)
- **Planned**: Real-time API integration with intelligent matching
- Schema documented in `zoho_crm_data_model.json`
- Target module: `arable/integrations/zoho_crm.py`

### Claude API (New)

- **Purpose**: Intelligent document extraction and data matching
- **Capabilities**: Structured data extraction, fuzzy matching, conflict resolution
- Target module: `arable/integrations/claude_api.py`
- Model: Claude-3-Sonnet for production workflows

### RSi.Net Legacy System

- **Current**: Read-only SQL database access
- **Planned**: Agent-driven data reconciliation and validation
- Custom validation in `rsi_validation.py`
- Configuration via `generate_rsi_config.py`

### Google Drive (New)

- **Purpose**: Document extraction from shared business folders
- **Target**: Proposals, purchase orders, contracts, project docs
- Target module: `arable/integrations/google_drive.py`
- Authentication: Service account with Drive API access

## Development Workflow (Updated for ARABLE)

### Migration Path

1. **Migration**: Run `python scripts/migrate_from_monday_automation.py`
2. **Setup**: Run `python scripts/setup_dev.py` for complete environment
3. **Configuration**: Customize `config/arable.yaml` and `.env` files
4. **Testing**: Validate with `arable info` CLI command
5. **Development**: Begin agent implementation and testing

### Agent Development Cycle

1. **Design**: Define agent capabilities and data models
2. **Implement**: Create agent class extending BaseAgent
3. **Register**: Add agent to registry and configuration
4. **Test**: Unit and integration testing with pytest
5. **Document**: Update agent documentation and workflows

### Current Development Priorities

1. **Phase 1**: Migration and CLI foundation (Week 1)
2. **Phase 2**: Document extraction agent (Week 2)
3. **Phase 3**: CRM matching and reconciliation agents (Week 3)
4. **Phase 4**: Full workflow integration and RSi deployment (Week 4)

## File System Maintenance Notes

### Index Keeper Protocols (Updated)

- Update this file when any files are added, removed, or significantly changed
- Track migration status and agent development progress
- Include agent capability specifications and integration status
- Document workflow templates and configuration changes
- Flag deprecated legacy files for cleanup post-migration
- Maintain section organization as agent system grows

## Documentation Structure (Reorganized)

### User Documentation (`/docs/user/`)
End-user focused documentation for getting ARABLE running and using it effectively:

| File | Purpose | Status | Notes |
|------|---------|--------|---------|
| `README.md` | User documentation overview | Active | Navigation and audience guide |
| `quick_start.md` | 5-minute getting started guide | Active | New users start here |
| `setup.md` | Complete setup and configuration | Active | Installation, config, integrations |
| `architecture.md` | System design overview for users | Active | Understanding how ARABLE works |
| `cli_reference.md` | Comprehensive CLI command guide | Active | Command reference and workflows |

### Technical Documentation (`/docs/technical/`)
Technical project documentation for development, architecture, and team coordination:

| File/Directory | Purpose | Status | Notes |
|----------------|---------|--------|---------|
| `README.md` | Technical documentation overview | Active | Developer and maintainer guide |
| `project_instructions.md` | Agent roles and protocols | Active | Team coordination guidelines |
| `file_index.md` | This file - system organization | Active | Maintained by Index Keeper Agent |
| `architecture_plan.md` | Original architecture planning | Archive | Historical reference and design decisions |
| `agents/` | Agent-specific technical documentation | Planned | Individual agent implementation guides |
| `integrations/` | Integration setup and API documentation | Planned | API patterns and troubleshooting |
| `workflows/` | Business process templates | Planned | Automation patterns and technical implementation |

### Main Documentation (`/docs/`)

| File | Purpose | Status | Notes |
|------|---------|--------|---------|
| `README.md` | Documentation hub and navigation | Active | Main entry point for all docs |

### Recent Changes

_This section should be updated by agents making file system changes_

- 2025-05-29: Initial index created with monday_automation structure
- 2025-05-29: Added ARABLE architecture planning and migration scripts
- 2025-05-29: Created development setup and configuration templates
- 2025-05-29: **MIGRATION COMPLETED** - Core ARABLE structure in place
  - ✅ Created `/arable/` package with CLI, agents, integrations
  - ✅ Migrated Monday.com API to `arable/integrations/monday.py`
  - ✅ Created BaseAgent class and agent framework
  - ✅ Updated pyproject.toml for new dependencies and CLI entry point
  - ✅ CLI commands: `arable info` and `arable monday` functional
- 2025-05-29: **DOCUMENTATION COMPLETED** - Comprehensive user documentation created
  - ✅ Created documentation hub (`docs/README.md`) with navigation
  - ✅ Created Quick Start Guide for 5-minute setup
  - ✅ Created comprehensive Setup & Configuration guide
  - ✅ Created Architecture Overview explaining hybrid CLI-agent approach
  - ✅ Created detailed CLI User Guide with command reference and workflows
  - ✅ Updated file index to reflect new documentation structure
- 2025-05-29: **DOCUMENTATION REORGANIZED** - Separated user and technical documentation
  - ✅ Created `/docs/user/` directory for end-user documentation
  - ✅ Created `/docs/technical/` directory for project and development documentation
  - ✅ Moved user-facing docs: quick_start.md, setup.md, architecture.md, cli_reference.md
  - ✅ Moved technical docs: project_instructions.md, file_index.md, architecture_plan.md
  - ✅ Created README files for each subdirectory explaining purpose and audience
  - ✅ Updated main documentation hub with new structure and navigation
  - ✅ Updated file index to reflect reorganized structure
- Next updates will be logged here by agents

---

**Usage Instructions for Agents:**

1. Check this index before working with files to understand current state
2. Update relevant sections when making changes
3. Contact Index Keeper Agent for major reorganization needs
4. Keep status and notes current for effective collaboration
