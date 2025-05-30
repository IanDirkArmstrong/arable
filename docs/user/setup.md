# ARABLE Setup & Configuration Guide

Complete setup instructions for different environments and configuration options.

## Table of Contents

- [Environment Setup](#environment-setup)
- [Configuration Guide](#configuration-guide)
- [Integration Setup](#integration-setup)
- [Deployment Scenarios](#deployment-scenarios)
- [Troubleshooting Setup](#troubleshooting-setup)

---

## Environment Setup

### Development Environment

**Option 1: Automated Setup (Recommended)**
```bash
# Clone/navigate to ARABLE directory
cd /path/to/arable

# Run setup script (creates virtual environment, installs dependencies)
python scripts/setup_dev.py

# Activate environment
source arable_env/bin/activate      # macOS/Linux
# or
arable_env\Scripts\activate         # Windows

# Verify installation
arable info
```

**Option 2: Manual Setup**
```bash
# Create virtual environment
python -m venv arable_env
source arable_env/bin/activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Verify
arable --help
```

### Migration from monday_automation

If you have an existing monday_automation installation:

```bash
# Run migration script first
python scripts/migrate_from_monday_automation.py

# Then follow development setup
python scripts/setup_dev.py
source arable_env/bin/activate
```

**What migration does**:
- Creates new ARABLE package structure
- Moves configuration files to new locations
- Updates import paths and dependencies
- Preserves existing data and credentials

---

## Configuration Guide

### Configuration Files Overview

| File | Purpose | Required |
|------|---------|----------|
| `config/config.yaml` | Main application settings | Yes |
| `.env` | API keys and secrets | Yes |
| `credentials/service-account.json` | Google Sheets access | Yes |

### Creating Configuration

**Step 1: Generate Templates**
```bash
# Creates config/config.yaml from template
arable config

# Copy environment template
cp .env.example .env
```

**Step 2: Edit Main Configuration**

Edit `config/config.yaml`:
```yaml
system:
  name: "ARABLE Production"        # Environment identifier
  log_level: "INFO"                # DEBUG, INFO, WARNING, ERROR

monday:
  api_token: "${MONDAY_API_TOKEN}" # From .env file
  master_board_id: 123456789       # Your master tracking board
  template_board_id: 987654321     # Project template board
  active_projects_folder_id: 111222333  # Where new boards go
  project_board_columns:           # Column mappings for project boards
    timeline: "timeline"
    status: "status4"
    rsi_milestone_id: "text8"
  master_columns:                  # Column mappings for master board
    project_number: "text"
    project_name: "text5"
    customer: "text6"

google_sheets:
  credentials_path: "credentials/rsinet-service-account.json"
  sheet_name: "RSi Project Data"   # Exact sheet name in Google Drive

logging:
  level: "INFO"
  file: "logs/arable.log"          # Log file location
```

**Step 3: Set Environment Variables**

Edit `.env`:
```bash
# Monday.com API token (get from Monday.com > Admin > API)
MONDAY_API_TOKEN=your_monday_token_here

# Claude API key (for future agent features)
ANTHROPIC_API_KEY=your_claude_key_here

# Optional: Override config file location
ARABLE_CONFIG_PATH=config/custom_config.yaml
```

### Configuration Validation

```bash
# Test configuration
arable info

# Test specific integrations
arable project --help    # Should show command without errors

# Test with verbose output
arable project 99999 --verbose  # Use non-existent project to test config loading
```

---

## Integration Setup

### Monday.com Setup

**1. Get API Token**
- Go to Monday.com > Admin > API
- Generate new token with full permissions
- Add to `.env` as `MONDAY_API_TOKEN`

**2. Find Board and Folder IDs**

Use Monday.com URLs to find IDs:
```
https://mycompany.monday.com/boards/123456789
                              ^^^^^^^^^^^
                              This is your board ID

https://mycompany.monday.com/folders/111222333
                               ^^^^^^^^^^^  
                               This is your folder ID
```

**3. Map Column IDs**

Find column IDs in Monday.com:
- Go to board > Settings > Columns
- Each column has an ID (usually like "text", "text5", "status4", etc.)
- Update `config.yaml` with correct column mappings

### Google Sheets Setup

**1. Create Service Account**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create new project or select existing
- Enable Google Sheets API
- Create service account
- Download JSON credentials file

**2. Install Credentials**
```bash
# Place credentials file in credentials directory
cp ~/Downloads/service-account-key.json credentials/rsinet-service-account.json

# Update config.yaml with correct path
```

**3. Grant Sheet Access**
- Open your Google Sheet
- Share with service account email (found in JSON file)
- Give "Editor" permissions

**4. Verify Sheet Structure**

ARABLE expects these columns in Google Sheets:
- `ProjectNumber`
- `ProjectName` 
- `CustomerShortname`
- `MilestoneID`
- `MileStoneType`
- `DateOfMilestone`

### Zoho CRM Setup (Optional)

Currently uses CSV exports rather than API:
```bash
# Place CRM exports in data/crm/backups/
# Files like: Accounts_001.csv, Contacts_001.csv, etc.
```

---

## Deployment Scenarios

### Local Development
```yaml
# config/config.yaml
system:
  name: "ARABLE Development"
  log_level: "DEBUG"

logging:
  level: "DEBUG"
  file: "logs/arable-dev.log"
```

### RSi Production
```yaml
# config/config.yaml  
system:
  name: "ARABLE Production - RSi Visual Systems"
  log_level: "INFO"

logging:
  level: "INFO" 
  file: "/var/log/arable/arable.log"
```

### Testing Environment
```yaml
# config/test.yaml
system:
  name: "ARABLE Testing"
  log_level: "DEBUG"

monday:
  # Use test boards
  master_board_id: 999999999
  template_board_id: 888888888
```

**Using different configs**:
```bash
# Specify config file
arable project 12345 --config config/test.yaml

# Or set environment variable
export ARABLE_CONFIG_PATH=config/test.yaml
arable project 12345
```

---

## Advanced Configuration

### Multiple Environments

**Structure**:
```
config/
├── config.yaml          # Default/production
├── development.yaml     # Development overrides
├── testing.yaml         # Testing configuration
└── config.example.yaml  # Template
```

**Usage**:
```bash
# Development
arable project 12345 --config config/development.yaml

# Testing  
arable project 12345 --config config/testing.yaml
```

### Environment Variable Substitution

Configuration supports environment variable substitution:
```yaml
monday:
  api_token: "${MONDAY_API_TOKEN}"              # Required
  backup_token: "${MONDAY_BACKUP_TOKEN:-}"     # Optional with default
  rate_limit: "${MONDAY_RATE_LIMIT:-60}"       # Default to 60
```

### Logging Configuration

**Log Levels**:
- `DEBUG`: Detailed information for debugging
- `INFO`: General operational information  
- `WARNING`: Warning messages
- `ERROR`: Error messages only

**Log Destinations**:
```yaml
logging:
  level: "INFO"
  file: "logs/arable.log"        # File logging
  console: true                  # Also log to console
  max_size_mb: 50               # Rotate at 50MB
  backup_count: 3               # Keep 3 backup files
```

---

## Troubleshooting Setup

### Common Setup Issues

**"arable command not found"**
```bash
# Make sure virtual environment is activated
source arable_env/bin/activate

# Or install globally (not recommended)
pip install -e .
```

**"Configuration file not found"**
```bash
# Generate config template
arable config

# Or specify config location
arable project --config /full/path/to/config.yaml
```

**"Google Sheets authentication failed"**
```bash
# Check credentials file exists
ls -la credentials/

# Check file permissions
chmod 600 credentials/service-account.json

# Verify service account email has sheet access
```

**"Monday.com API authentication failed"**
```bash
# Verify token in .env file
cat .env | grep MONDAY_API_TOKEN

# Test token directly
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.monday.com/v2 -d 'query="{me{name}}"'
```

### Validation Commands

```bash
# Test overall system
arable info

# Test configuration loading
arable config

# Test Google Sheets connection (with verbose output)
arable project --verbose

# Test Monday.com connection
arable sync
```

### Reset Configuration

```bash
# Start over with clean config
rm config/config.yaml
rm .env
arable config
cp .env.example .env
# Edit files with correct values
```

### Debug Mode

```bash
# Enable maximum logging
export ARABLE_LOG_LEVEL=DEBUG
arable project 12345 --verbose

# Check logs
tail -f logs/arable.log
```

---

## Configuration Best Practices

### Security
- Never commit `.env` files to version control
- Use restrictive permissions on credentials files: `chmod 600`
- Rotate API tokens regularly
- Use separate tokens for development and production

### Maintenance
- Document custom configuration changes
- Keep backups of working configurations
- Test configuration changes in development first
- Use version control for `config.yaml` (without secrets)

### Performance
- Set appropriate rate limits for APIs
- Configure log rotation to prevent disk issues
- Use DEBUG logging only when needed
- Monitor API usage and quotas

---

## Next Steps After Setup

Once configuration is complete:

1. **Test basic functionality**: `arable project 12345 --verbose`
2. **Check sync status**: `arable sync 12345`
3. **Run full workflow**: `arable project --all`
4. **Monitor results**: Check Monday.com boards and logs
5. **Customize**: Adjust configuration based on actual usage patterns

The system is designed to work reliably with minimal configuration - most complexity is optional for advanced use cases.
