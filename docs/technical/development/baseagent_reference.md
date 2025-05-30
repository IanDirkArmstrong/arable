## BaseAgent Framework

All ARABLE agents inherit from the `BaseAgent` class, which provides:

### Core Structure

```python
from arable.agents.base import BaseAgent, AgentCapability, AgentState
from typing import Dict, Any, List

class CustomAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        # Custom initialization

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Main agent logic
        pass

    def get_capabilities(self) -> List[AgentCapability]:
        # Define what this agent can do
        pass
```

### BaseAgent Methods

| Method               | Purpose                      | When to Override         |
| -------------------- | ---------------------------- | ------------------------ |
| `__init__()`         | Initialize agent with config | Always (call super())    |
| `execute()`          | Main task execution logic    | Always (abstract method) |
| `get_capabilities()` | Define agent abilities       | Always (abstract method) |
| `update_memory()`    | Store state information      | Rarely (utility method)  |
| `get_memory()`       | Retrieve stored state        | Rarely (utility method)  |
| `set_status()`       | Update agent status          | As needed                |
| `get_status()`       | Get current status           | Rarely (utility method)  |

---