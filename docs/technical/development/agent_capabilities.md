## Agent Capabilities System

The capabilities system allows agents to declare what they can do, enabling dynamic task routing and validation.

### Defining Capabilities

```python
def get_capabilities(self) -> List[AgentCapability]:
    return [
        AgentCapability(
            name=\"extract_project_data\",
            description=\"Extract project information from proposal documents\",
            input_types=[\"pdf_file\", \"docx_file\"],
            output_types=[\"structured_json\", \"project_summary\"]
        ),
        AgentCapability(
            name=\"validate_customer_data\",
            description=\"Validate customer information against CRM records\",
            input_types=[\"customer_data\", \"crm_records\"],
            output_types=[\"validation_report\", \"match_confidence\"]
        )
    ]
```

### Capability Properties

| Property       | Purpose                                 | Example Values                       |
| -------------- | --------------------------------------- | ------------------------------------ |
| `name`         | Unique identifier for the capability    | `\"extract_project_data\"`           |
| `description`  | Human-readable description              | `\"Extract project info from docs\"` |
| `input_types`  | What data types the capability accepts  | `[\"pdf_file\", \"json_data\"]`      |
| `output_types` | What data types the capability produces | `[\"structured_json\", \"report\"]`  |

### Using Capabilities for Task Routing

```python
# Example: Find agents that can process PDF files
def find_agents_for_pdf_processing(agents: List[BaseAgent]) -> List[BaseAgent]:
    compatible_agents = []

    for agent in agents:
        capabilities = agent.get_capabilities()
        for capability in capabilities:
            if \"pdf_file\" in capability.input_types:
                compatible_agents.append(agent)
                break

    return compatible_agents
```

---