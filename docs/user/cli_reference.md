# ARABLE CLI User Guide

A comprehensive guide to using the ARABLE command-line interface for document intelligence, data reconciliation, and workflow automation.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Commands](#core-commands)
- [Project Management](#project-management)
- [Data Synchronization](#data-synchronization)
- [Configuration](#configuration)
- [Workflows and Examples](#workflows-and-examples)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

ARABLE provides a powerful CLI built with Typer and Rich for beautiful terminal output. All commands follow a consistent pattern and provide helpful feedback.

### Installation Check

```bash
# Verify ARABLE is installed and working
arable info
```

**Expected Output:**

```
╭─ System Information ─────────────────────────────────╮
│ ARABLE - Agentic Runtime And Business Logic Engine  │
│                                                      │
│ 🤖 Intelligent document extraction                  │
│ 🔄 Cross-platform data reconciliation              │
│ ⚡ Agent-driven workflow automation                  │
│ 🎯 Business logic orchestration                     │
╰──────────────────────────────────────────────────────╯
```

### Getting Help

```bash
# Show all available commands
arable --help

# Get help for a specific command
arable project --help
arable sync --help
```

---

## Core Commands

### `arable info`

Display system information and verify installation.

```bash
arable info
```

**Use Cases:**

- Verify ARABLE installation
- Check system capabilities
- Quick reference for available features

---

### `arable config`

Generate or manage configuration files.

```bash
# Create configuration template
arable config
```

**What it does:**

- Creates `config/config.yaml` from template
- Sets up required directory structure
- Provides examples for all integration settings

**Output:**

```
📝 Configuration Setup
Creating config template at config/config.yaml...
✅ Configuration template created!
```

---

## Project Management

The project management commands handle the creation and synchronization of Monday.com project boards from Google Sheets data.

### `arable project`

Create Monday.com projects from Google Sheets data with rich progress tracking.

#### Basic Usage

```bash
# Process a specific project
arable project 12345

# Process all projects from Google Sheets
arable project --all

# Interactive mode (prompts for project number)
arable project
```

#### Advanced Options

```bash
# Use custom configuration file
arable project 12345 --config /path/to/custom/config.yaml

# Enable verbose logging for debugging
arable project 12345 --verbose

# Process all projects with verbose output
arable project --all --verbose
```

#### What It Does

1. **📊 Connects to Google Sheets** - Reads project and milestone data
2. **📋 Creates Master Board Item** - Adds project to Monday.com master tracking board
3. **🏗️ Creates Project Board** - Duplicates template board for the specific project
4. **📅 Adds Milestones** - Populates project board with milestone items from sheets data

#### Example Workflow

```bash
$ arable project 12345
🚀 Starting Monday.com Project Automation
📊 Connecting to Google Sheets... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Project # ┃ Project Name                ┃ Customer        ┃ Milestones ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 12345     │ Flight Simulator Training   │ ACME Aviation   │         15 │
└───────────┴─────────────────────────────┴─────────────────┴────────────┘

Processing projects... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
📋 Creating master item for 12345... ━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
🏗️ Creating project board for 12345... ━━━━━━━━━━━━━━━━━━━━━━━ 100%
📅 Adding milestones to 12345... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

🎉 Automation Complete: 1/1 projects processed successfully
```

#### Error Handling

The CLI provides detailed error reporting:

```bash
# Configuration error
❌ Configuration error: Monday.com API token not found in config

# Google Sheets connection error
❌ Google Sheets error: Unable to access spreadsheet. Check credentials.

# Monday.com API error
❌ Monday API error for project 12345: Rate limit exceeded (60/min)
```

---

## Data Synchronization

### `arable sync`

Check synchronization status between Google Sheets and Monday.com to identify discrepancies.

#### Basic Usage

```bash
# Check sync status for specific project
arable sync 12345

# Check sync status for all projects
arable sync
```

#### Advanced Options

```bash
# Use custom configuration
arable sync 12345 --config /path/to/config.yaml
```

#### What It Does

1. **📊 Loads Google Sheets Data** - Retrieves current project and milestone information
2. **📋 Fetches Monday.com Data** - Gets corresponding board items and timeline data
3. **🔍 Compares Data** - Identifies matches, missing items, and date discrepancies
4. **📊 Generates Report** - Shows detailed sync status with actionable insights

#### Example Output

```bash
$ arable sync 12345
🎯 Checking sync for project 12345 only
📊 Loading Google Sheets data... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
📋 Fetching Monday.com data... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Project # ┃ Status      ┃ Matched ┃ Missing ┃ Date Issues ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 12345     │ Board found │      12 │       3 │           1 │
└───────────┴─────────────┴─────────┴─────────┴─────────────┘

⚠️ Missing milestones in project 12345:
  • Final Delivery (ID: 15001)
  • Customer Acceptance (ID: 15002)
  • Project Closeout (ID: 15003)

📅 Date discrepancies in project 12345:
  • Design Review: Sheets=2024-06-15, Monday=2024-06-20
```

#### Understanding Sync Results

- **Matched**: Milestones found in both systems with consistent data
- **Missing**: Milestones in Google Sheets but not in Monday.com boards
- **Date Issues**: Milestones with different dates between systems

---

## Configuration

ARABLE uses YAML configuration files for system settings and integrations.

### Configuration File Structure

```yaml
# config/config.yaml
system:
  name: "ARABLE Production"
  log_level: "INFO"

monday:
  api_token: "your_monday_api_token"
  master_board_id: 123456789
  template_board_id: 987654321
  active_projects_folder_id: 111222333

google_sheets:
  credentials_path: "credentials/service-account.json"
  sheet_name: "RSi Project Data"

logging:
  level: "INFO"
  file: "logs/arable.log"
```

### Environment Variables

Sensitive configuration can be stored in `.env`:

```bash
# .env
MONDAY_API_TOKEN=your_token_here
GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json
ANTHROPIC_API_KEY=your_claude_api_key
```

### Configuration Commands

```bash
# Generate template configuration
arable config

# Validate current configuration (coming soon)
arable config validate

# Show current configuration (coming soon)
arable config show
```

---

## Workflows and Examples

### Complete Project Setup Workflow

```bash
# 1. Set up configuration
arable config
# Edit config/config.yaml with your API tokens

# 2. Test with a single project first
arable project 12345 --verbose

# 3. Check sync status
arable sync 12345

# 4. Process all projects once validated
arable project --all
```

### Batch Processing Multiple Projects

```bash
# Process specific projects by running multiple commands
for project in 12345 12346 12347; do
    echo "Processing project $project..."
    arable project $project
    arable sync $project
    echo "Project $project complete"
done
```

### Daily Sync Check Workflow

```bash
# Morning sync check for all active projects
arable sync > daily_sync_report.txt

# Process any new projects
arable project --all --verbose
```

### Development and Testing

```bash
# Test with single project and verbose output
arable project 99999 --verbose --config config/test.yaml

# Check specific project sync status
arable sync 99999

# Validate configuration before production run
arable info
```

---

## Command Reference Quick Guide

| Command                | Purpose                  | Example                |
| ---------------------- | ------------------------ | ---------------------- |
| `arable info`          | System information       | `arable info`          |
| `arable config`        | Create config template   | `arable config`        |
| `arable project <num>` | Process specific project | `arable project 12345` |
| `arable project --all` | Process all projects     | `arable project --all` |
| `arable sync <num>`    | Check project sync       | `arable sync 12345`    |
| `arable sync`          | Check all project sync   | `arable sync`          |

### Global Options

All commands support these options:

- `--help` - Show command help
- `--config PATH` - Use custom configuration file
- `--verbose` - Enable detailed logging (where applicable)

---

## Troubleshooting

### Common Issues

#### Configuration Errors

```bash
❌ Configuration error: Monday.com API token not found in config
```

**Solution:**

1. Run `arable config` to create template
2. Edit `config/config.yaml` with your API tokens
3. Verify file permissions and format

#### Google Sheets Connection Issues

```bash
❌ Google Sheets error: Unable to access spreadsheet. Check credentials.
```

**Solution:**

1. Verify credentials file exists at specified path
2. Check Google Sheets API is enabled
3. Ensure service account has access to the spreadsheet
4. Validate JSON credentials file format

#### Monday.com API Errors

```bash
❌ Monday API error: Rate limit exceeded (60/min)
```

**Solution:**

1. Wait for rate limit reset (usually 1 minute)
2. Process projects in smaller batches
3. Use `--verbose` flag to see detailed API calls

#### Project Not Found

```bash
⚠️ No projects found to process
```

**Solution:**

1. Verify project number exists in Google Sheets
2. Check Google Sheets connection and data format
3. Ensure project data is in expected columns

### Debug Commands

```bash
# Enable verbose logging
arable project 12345 --verbose

# Test system components
arable info

# Validate configuration
arable config
```

### Log File Locations

- **Application logs**: `logs/arable.log`
- **Configuration**: `config/config.yaml`
- **Credentials**: `credentials/` directory

### Getting Help

1. **Check command help**: `arable <command> --help`
2. **Review configuration**: Ensure all required fields are set
3. **Check logs**: Look at `logs/arable.log` for detailed error information
4. **Test connectivity**: Use `arable info` to verify system status

---

## What's Next?

This CLI interface is the foundation for ARABLE's hybrid approach. Coming soon:

- **Agent Integration**: CLI commands to trigger intelligent agents
- **Document Processing**: `arable extract` for document intelligence
- **Workflow Orchestration**: `arable workflow run` for complex automation
- **Real-time Monitoring**: `arable monitor` for system status

The current project and sync commands demonstrate the power of CLI-driven automation while providing the foundation for more sophisticated agent-based workflows.
