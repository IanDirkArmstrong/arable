# 🚀 ARABLE Quick Start Guide

Get ARABLE running and see results in 5 minutes.

---

## 🧠 What Is ARABLE?

ARABLE is a **hybrid CLI + agent system** for automating business workflows:

- 🛠️ Manual CLI tools for direct control
- 🤖 Intelligent agents for smart processing (optional)
- 🔁 Progressive automation — start manual, scale up

> **Current State**: Monday.com project automation with Google Sheets integration  
> **Architecture**: CLI-first, agent-ready

---

## ⚙️ Quick Installation

### 🆕 New Installation

```bash
# 1. Set up environment
python scripts/setup_dev.py
source arable_env/bin/activate  # or activate.bat on Windows

# 2. Configure
cp config/config.example.yaml config/config.yaml
cp .env.example .env
# Edit config files with your API keys

# 3. Test
arable info
```

📎 For full environment setup: [`environment_setup.md`](../technical/setup/environment_setup.md)

---

### 🔁 Migrating from `monday_automation`

```bash
python scripts/migrate_from_monday_automation.py
```

📎 For details: [`migration_guide.md`](../technical/setup/migration_guide.md)

---

## 🧪 CLI Commands

```bash
# View system info
arable info

# Create Monday.com projects
arable project 12345      # One project
arable project --all      # All projects
arable project            # Interactive mode

# Sync check
arable sync 12345
arable sync

# Generate config template
arable config
```

---

## 🧾 Basic Configuration

### `config/config.yaml`
```yaml
monday:
  api_token: "your_token"
  master_board_id: 123456
  template_board_id: 789012

google_sheets:
  credentials_path: "credentials/service-account.json"
  sheet_name: "RSi Project Data"
```

### `.env`
```env
MONDAY_API_TOKEN=your_token_here
ANTHROPIC_API_KEY=your_claude_key  # Optional future use
```

📎 Full guide: [`configuration_guide.md`](../technical/setup/configuration_guide.md)

---

## 🧱 Project Structure

```
ARABLE/
├── cli/                    # Typer-powered CLI
├── agents/                 # Custom agents
├── config/                 # YAML and .env files
├── scripts/                # Setup/migration scripts
└── logs/                   # Optional runtime output
```
