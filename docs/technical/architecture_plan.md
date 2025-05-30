# 🧠 ARABLE Architecture Plan

_Agentic Runtime And Business Logic Engine_  
_For use by project manager agents and system planners._

---

## 🪄 Project Vision

Transform ARABLE from a command-line automation tool into an intelligent, multi-agent orchestration platform for business automation.

Key goals:
- Extract and process structured data from documents
- Reconcile info across systems like Zoho CRM, Monday.com, and SQL
- Automate end-to-end workflows with modular agents

---

## 🧱 Target Project Structure

This layout is proposed for a clean, modular architecture.

```txt
arable/
├── README.md
├── pyproject.toml
├── requirements.txt
├── arable/                          # Main package
│   ├── __init__.py
│   ├── cli/                         # Typer-based CLI interface
│   │   ├── main.py
│   │   ├── commands/                # Core user commands
│   │   └── ui/                      # Rich UI components (tables, prompts)
│   ├── agents/                      # Modular agent system
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── orchestrator.py
│   │   ├── memory.py
│   │   └── specialized/
│   │       ├── document_extractor.py
│   │       ├── crm_matcher.py
│   │       ├── data_reconciler.py
│   │       └── monday_manager.py
│   ├── integrations/               # Connectors to APIs
│   │   ├── monday.py
│   │   ├── google_sheets.py
│   │   └── zoho_crm.py
│   ├── config.py                   # Load/validate config
│   ├── logger.py                   # Logging and audit
│   └── utils/                      # Shared helpers/utilities
```

---

## 🔁 Integration Layers

- **Monday.com**: Board templates, sync APIs, project automation
- **Google Sheets**: Project intake, batch sync workflows
- **Zoho CRM**: Customer and deal data, pricing authority
- **Claude API**: For future document and reasoning agents

---

## 📌 Coordination Docs

This file is best used alongside:

- [`file_index.md`](../user/file_index.md)
- [`project_instructions.md`](../user/project_instructions.md)
- [`agent_patterns.md`](development/agent_patterns.md)
