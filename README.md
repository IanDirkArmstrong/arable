# ARABLE

**Agentic Runtime And Business Logic Engine**
A sophisticated multi-agent system for intelligent document extraction, cross-platform data reconciliation, and automated business workflow orchestration

## ![Version](https://img.shields.io/badge/version-0.2.0-blue) ![Status](https://img.shields.io/badge/status-in--progress-yellow) ![License](https://img.shields.io/badge/license-RSi%20Internal-lightgrey)

---

## 🎯 Vision

Transform business operations through intelligent agents that extract structured information from documents, match data across CRM and legacy systems, and automate complex workflows with minimal human intervention.

---

## 🚀 Key Capabilities

- **📄 Document Intelligence**: Extract structured data from proposals, contracts, and purchase orders
- **🔄 Data Reconciliation**: Intelligently match and sync data across Monday.com, Zoho CRM, and legacy databases
- **🤖 Agent Orchestration**: Coordinate multiple specialized agents for complex business processes
- **⚡ CLI Automation**: Rich terminal interface with progress tracking and interactive workflows
- **🎯 Business Logic**: Encode domain-specific rules and validation for aerospace/simulation industry

---

## 📈 Example Use Cases

- **Sales Operations**  
  Automatically extract pricing and milestone data from proposals and populate Zoho CRM + Monday.com boards.

- **Finance & Procurement**  
  Reconcile customer purchase orders with internal sales and contract records. Flag mismatches or discrepancies automatically.

- **Project Management**  
  Instantly create, schedule, and assign projects based on contract terms — no manual setup or double entry.

- **Legacy System Integration**  
  Bridge the gap between old .NET tools and modern platforms via smart agents that translate and sync key data.

---

## 🏗️ Architecture

```txt
ARABLE/
├── arable/                    # Core agent system
│   ├── cli/                   # Typer + Rich CLI interface
│   ├── agents/                # Agent framework and implementations
│   │   ├── base.py           # BaseAgent class
│   │   ├── orchestrator.py   # Multi-agent coordination
│   │   └── specialized/      # Domain-specific agents
│   ├── integrations/         # External system connectors
│   ├── data/                 # Models, extractors, matchers
│   └── utils/                # Logging, validation, exceptions
├── config/                   # Configuration templates
├── data/                     # Storage and cache
└── scripts/                  # Migration and setup utilities
```

---

## 🤖 Agent Ecosystem

### Core Agents

| Agent                 | Purpose                       | Input                | Output                        |
| --------------------- | ----------------------------- | -------------------- | ----------------------------- |
| **DocumentExtractor** | Parse business documents      | PDF, DOCX files      | Structured JSON data          |
| **CRMatcher**         | Find matching CRM records     | Data + record sets   | Match candidates + confidence |
| **DataReconciler**    | Resolve data conflicts        | Conflict sets        | Reconciliation plans          |
| **MondayManager**     | Orchestrate project workflows | Project data         | Board updates, automations    |
| **WorkflowAssistant** | Multi-step process automation | Workflow definitions | Execution results             |

### Agent Coordination

- **Registry System**: Dynamic agent discovery and capability matching
- **Memory Management**: Persistent state across agent interactions
- **Orchestration Engine**: Workflow execution with error handling and rollback
- **Claude Integration**: LLM-powered intelligence for complex reasoning tasks

---

## 🛠️ Getting Started

### Migration from monday_automation

If upgrading from the previous monday_automation system:

```bash
# 1. Run migration script
python scripts/migrate_from_monday_automation.py

# 2. Set up development environment
python scripts/setup_dev.py

# 3. Activate virtual environment
source arable_env/bin/activate  # macOS/Linux
# or
arable_env\Scripts\activate     # Windows

# 4. Configure system
cp config/arable.example.yaml config/arable.yaml
cp .env.example .env
# Edit configuration files with your API keys and settings

# 5. Test installation
arable info
```

### Fresh Installation

```bash
# 1. Clone and setup
git clone <repository-url>
cd arable
python scripts/setup_dev.py

# 2. Configure environment
source arable_env/bin/activate
cp config/arable.example.yaml config/arable.yaml
cp .env.example .env

# 3. Install and test
pip install -e .
arable info
```

---

## 📋 Configuration

### Main Configuration (`config/arable.yaml`)

```yaml
system:
  name: "ARABLE Production"
  log_level: "INFO"

agents:
  max_concurrent: 5
  memory_limit_mb: 512

integrations:
  monday:
    api_token: "${MONDAY_API_TOKEN}"
    rate_limit: 60
  zoho_crm:
    client_id: "${ZOHO_CLIENT_ID}"
    client_secret: "${ZOHO_CLIENT_SECRET}"
  claude_api:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-sonnet-20240229"
```

### Agent Configuration (`config/agents.yaml`)

```yaml
agents:
  document_extractor:
    class: "arable.agents.specialized.DocumentExtractorAgent"
    config:
      supported_formats: ["pdf", "docx", "txt"]
      max_file_size_mb: 50

workflows:
  document_to_crm:
    name: "Document Extraction to CRM Sync"
    steps:
      - agent: "document_extractor"
        task: "extract_structured_data"
      - agent: "crm_matcher"
        task: "find_matching_records"
```

---

## 🖥️ CLI Usage

```bash
# System information
arable info

# Extract data from documents
arable extract ./proposals/ --agent document_extractor --output ./results/

# Reconcile data between systems
arable reconcile zoho monday --dry-run

# Run agent workflows
arable workflow run document_to_crm --config config/workflows.yaml

# Monitor system status
arable monitor --follow
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Test specific agent
pytest tests/agents/test_document_extractor.py

# Integration tests
pytest tests/integration/ -v

# Test CLI commands
arable info
```

---

## 🔧 Development

### Creating a New Agent

```python
from arable.agents.base import BaseAgent, AgentCapability

class CustomAgent(BaseAgent):
    def get_capabilities(self):
        return [
            AgentCapability(
                name="custom_processing",
                description="Process custom business logic",
                input_types=["json"],
                output_types=["json", "report"]
            )
        ]

    async def execute(self, task):
        # Implementation here
        return {"status": "completed", "results": [...]}
```

### Adding New Integrations

```python
# arable/integrations/new_system.py
class NewSystemIntegration:
    def __init__(self, config):
        self.config = config

    async def fetch_data(self, query):
        # Integration logic
        pass
```

---

## 📊 Current Status

### ✅ Completed (v0.1 - monday_automation)

- Monday.com API integration
- Google Sheets data processing
- Zoho CRM export handling
- RSi validation logic
- Basic project automation

### 🚧 In Progress (v0.2 - ARABLE)

- Agent framework architecture
- Typer CLI with Rich UI
- Migration tooling
- Configuration system

### 📋 Planned (v0.3+)

- Document extraction agents
- Claude API integration
- CRM matching intelligence
- Workflow orchestration
- Advanced reconciliation

---

## 🤝 Contributing

1. **Agent Development**: Create specialized agents for domain-specific tasks
2. **Integration Expansion**: Add new system connectors
3. **Workflow Templates**: Build reusable business process templates
4. **Documentation**: Enhance guides and API documentation

---

## 📚 Documentation

- **[Agent Development Guide](docs/agents/)** - Creating custom agents
- **[Integration Setup](docs/integrations/)** - Connecting external systems
- **[API Reference](docs/api/)** - Complete API documentation
- **[Workflow Examples](docs/workflows/)** - Business process templates

---

## 🏢 Production Deployment

### RSi Visual Systems Integration

ARABLE is currently deployed for RSi Visual Systems with:

- **Monday.com project management** automation
- **Zoho CRM data synchronization**
- **Legacy .NET system integration**
- **Custom aerospace industry workflows**

Contact: <ian@wowitsian.com> for enterprise deployment and customization.

---

## 🏷️ Versioning

ARABLE follows [Semantic Versioning](https://semver.org/) for all official releases.  
Versions are structured as `MAJOR.MINOR.PATCH`, where:

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible feature additions
- **PATCH**: Backward-compatible bug fixes

For pre-release versions (`v0.x.x`), stability is not guaranteed and changes may occur frequently.

---

## 📄 License

This software is developed and maintained by Ian Dirk Armstrong under contract with RSi Visual Systems.  
All rights to the ARABLE system, including its source code, documentation, and associated tooling, are held by RSi Visual Systems as part of the work-for-hire agreement.  
Use, modification, and distribution are subject to RSi internal policy.  
Contact <ian@wowitsian.com> for questions related to licensing or enterprise customization.

---

> _"I do know that they’re talking. I hear them every day. I just don’t always understand what they’re saying."_  
> — **Fern Arable**, _Charlotte’s Web_ by E.B. White
