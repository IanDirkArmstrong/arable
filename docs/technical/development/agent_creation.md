## Creating Your First Agent

Let's build a simple document validation agent step by step.

### Step 1: Define the Agent Class

```python
# arable/agents/specialized/document_validator.py
from arable.agents.base import BaseAgent, AgentCapability
from typing import Dict, Any, List
import asyncio
import os

class DocumentValidatorAgent(BaseAgent):
    \"\"\"Agent that validates document format and content\"\"\"

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)

        # Agent-specific configuration
        self.supported_formats = config.get('supported_formats', ['pdf', 'docx', 'txt'])
        self.max_file_size_mb = config.get('max_file_size_mb', 10)
        self.required_fields = config.get('required_fields', [])

        self.logger.info(f\"DocumentValidator initialized for formats: {self.supported_formats}\")
```

### Step 2: Implement Core Methods

```python
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Execute document validation task\"\"\"
        self.set_status(\"processing\")

        # Extract task parameters
        file_path = task.get('file_path')
        validation_rules = task.get('validation_rules', {})

        if not file_path:
            self.set_status(\"error\")
            return {
                \"success\": False,
                \"error\": \"No file_path provided in task\"
            }

        try:
            # Perform validation steps
            validation_result = await self._validate_document(file_path, validation_rules)

            # Update memory with results
            self.update_memory('last_validation', {
                'file_path': file_path,
                'result': validation_result,
                'timestamp': self._get_timestamp()
            })

            self.set_status(\"completed\")
            return {
                \"success\": True,
                \"validation_result\": validation_result,
                \"agent_id\": self.agent_id
            }

        except Exception as e:
            self.logger.error(f\"Validation failed for {file_path}: {e}\")
            self.set_status(\"error\")
            return {
                \"success\": False,
                \"error\": str(e),
                \"file_path\": file_path
            }

    def get_capabilities(self) -> List[AgentCapability]:
        \"\"\"Define what this agent can do\"\"\"
        return [
            AgentCapability(
                name=\"validate_document_format\",
                description=\"Validate document file format and structure\",
                input_types=[\"file_path\", \"validation_rules\"],
                output_types=[\"validation_result\", \"error_report\"]
            ),
            AgentCapability(
                name=\"check_file_size\",
                description=\"Verify document file size limits\",
                input_types=[\"file_path\"],
                output_types=[\"size_check_result\"]
            ),
            AgentCapability(
                name=\"validate_required_fields\",
                description=\"Check for presence of required document fields\",
                input_types=[\"document_content\", \"field_requirements\"],
                output_types=[\"field_validation_result\"]
            )
        ]
```

### Step 3: Implement Helper Methods

```python
    async def _validate_document(self, file_path: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Internal validation logic\"\"\"
        result = {
            \"file_exists\": False,
            \"format_valid\": False,
            \"size_valid\": False,
            \"content_valid\": False,
            \"errors\": [],
            \"warnings\": []
        }

        # Check file existence
        if not os.path.exists(file_path):
            result[\"errors\"].append(f\"File not found: {file_path}\")
            return result
        result[\"file_exists\"] = True

        # Check file format
        file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        if file_ext not in self.supported_formats:
            result[\"errors\"].append(f\"Unsupported format: {file_ext}\")
        else:
            result[\"format_valid\"] = True

        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            result[\"errors\"].append(f\"File too large: {file_size_mb:.1f}MB > {self.max_file_size_mb}MB\")
        else:
            result[\"size_valid\"] = True

        # Additional validation based on rules
        if rules.get('strict_mode', False):
            await self._perform_strict_validation(file_path, result)

        result[\"content_valid\"] = len(result[\"errors\"]) == 0

        return result

    async def _perform_strict_validation(self, file_path: str, result: Dict[str, Any]):
        \"\"\"Perform additional strict validation\"\"\"
        # Example: Check for required content patterns
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for field in self.required_fields:
                if field not in content:
                    result[\"warnings\"].append(f\"Required field '{field}' not found\")

        except Exception as e:
            result[\"errors\"].append(f\"Content validation failed: {e}\")

    def _get_timestamp(self) -> str:
        \"\"\"Get current timestamp for logging\"\"\"
        from datetime import datetime
        return datetime.now().isoformat()
```

### Step 4: Register the Agent

Create an agent configuration:

```yaml
# config/agents.yaml
agents:
  document_validator:
    class: \"arable.agents.specialized.DocumentValidatorAgent\"
    config:
      supported_formats: [\"pdf\", \"docx\", \"txt\"]
      max_file_size_mb: 50
      required_fields: [\"Project Number\", \"Customer\", \"Date\"]
```

---