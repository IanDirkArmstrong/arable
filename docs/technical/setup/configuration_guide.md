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