# ARABLE Agent Development Guide

Learn how to build intelligent agents using ARABLE's BaseAgent framework for document processing, data reconciliation, and workflow automation.

## Table of Contents

- [Agent Architecture Overview](#agent-architecture-overview)
- [BaseAgent Framework](#baseagent-framework)
- [Creating Your First Agent](#creating-your-first-agent)
- [Agent Capabilities System](#agent-capabilities-system)
- [Memory and State Management](#memory-and-state-management)
- [Integration Patterns](#integration-patterns)
- [Testing and Validation](#testing-and-validation)
- [Advanced Agent Patterns](#advanced-agent-patterns)

---

## Agent Architecture Overview

ARABLE agents are autonomous components that perform specific business logic tasks. They follow a consistent pattern:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input Data    │───▶│   Agent Logic    │───▶│  Output Data    │
│   (Documents,   │    │  (Intelligence,  │    │  (Structured,   │
│    Records,     │    │   Processing,    │    │   Validated,    │
│    Requests)    │    │   Validation)    │    │   Actionable)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Agent Memory   │
                    │   (State, Cache, │
                    │    Metrics)      │
                    └──────────────────┘
```

### Core Principles

1. **Single Responsibility**: Each agent has one primary function
2. **Stateful Operation**: Agents maintain memory across tasks
3. **Capability Declaration**: Agents explicitly define what they can do
4. **Async Operation**: All agents support asynchronous execution
5. **Rich Logging**: Comprehensive logging for debugging and monitoring

---

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

## Memory and State Management

ARABLE agents maintain persistent state across tasks using the memory system.

### Basic Memory Operations

```python
class StatefulAgent(BaseAgent):
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Store task results
        self.update_memory('processed_files', task.get('file_path'))
        self.update_memory('task_count', self.get_memory('task_count', 0) + 1)

        # Retrieve previous results
        last_result = self.get_memory('last_result')
        if last_result:
            self.logger.info(f\"Previous result: {last_result}\")

        # Process current task
        result = await self._process_task(task)

        # Store current result for next time
        self.update_memory('last_result', result)

        return result
```

### Advanced Memory Patterns

#### Caching Results

```python
async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
    file_path = task.get('file_path')

    # Check cache first
    cache_key = f\"processed_{hash(file_path)}\"
    cached_result = self.get_memory(cache_key)

    if cached_result:
        self.logger.info(f\"Using cached result for {file_path}\")
        return cached_result

    # Process and cache result
    result = await self._process_file(file_path)
    self.update_memory(cache_key, result)

    return result
```

#### Progress Tracking

```python
async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
    total_items = len(task.get('items', []))
    processed_count = 0

    for item in task['items']:
        # Process item
        await self._process_item(item)
        processed_count += 1

        # Update progress in memory
        progress = (processed_count / total_items) * 100
        self.update_memory('current_progress', progress)

        self.logger.info(f\"Progress: {progress:.1f}%\")

    return {\"processed\": processed_count, \"total\": total_items}
```

### Memory Best Practices

1. **Use descriptive keys**: `'last_processed_file'` vs `'file'`
2. **Store timestamps**: Always include when data was stored
3. **Limit memory size**: Clean up old data to prevent memory bloat
4. **Type consistency**: Store data in consistent formats

---

## Integration Patterns

ARABLE agents integrate with external systems through standardized patterns.

### Claude API Integration

```python
from anthropic import Anthropic

class ClaudeEnabledAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.claude = Anthropic(api_key=config['claude_api_key'])
        self.model = config.get('claude_model', 'claude-3-sonnet-20240229')

    async def _analyze_with_claude(self, document_text: str, analysis_prompt: str) -> str:
        \"\"\"Use Claude for document analysis\"\"\"
        try:
            message = self.claude.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    \"role\": \"user\",
                    \"content\": f\"{analysis_prompt}\
                    {
  `path`: `/Users/ian/Library/CloudStorage/GoogleDrive-ian@wowitsian.com/My Drive/AI/ARABLE/docs/user_guides/agent_development.md`,
  `edits`: [
    {
      `newText`: `from anthropic import Anthropic

class ClaudeEnabledAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.claude = Anthropic(api_key=config['claude_api_key'])
        self.model = config.get('claude_model', 'claude-3-sonnet-20240229')

    async def _analyze_with_claude(self, document_text: str, analysis_prompt: str) -> str:
        \"\"\"Use Claude for document analysis\"\"\"
        try:
            message = self.claude.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    \"role\": \"user\",
                    \"content\": f\"{analysis_prompt}\
\
Document:\
{document_text}\"
                }]
            )

            response_text = message.content[0].text
            self.update_memory('last_claude_call', {
                'prompt': analysis_prompt,
                'response': response_text,
                'timestamp': self._get_timestamp()
            })

            return response_text

        except Exception as e:
            self.logger.error(f\"Claude API error: {e}\")
            raise
```

### Monday.com Integration

```python
from arable.integrations.monday import MondayAPI

class MondayIntegratedAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.monday = MondayAPI(
            api_token=config['monday_api_token'],
            logger=self.logger
        )

    async def _create_project_board(self, project_data: Dict[str, Any]) -> str:
        \"\"\"Create Monday.com board from project data\"\"\"
        try:
            board_id = self.monday.create_project_board(
                template_board_id=self.config['template_board_id'],
                folder_id=self.config['projects_folder_id'],
                project=project_data
            )

            self.update_memory('created_boards',
                self.get_memory('created_boards', []) + [board_id]
            )

            return board_id

        except Exception as e:
            self.logger.error(f\"Monday.com board creation failed: {e}\")
            raise
```

### Google Sheets Integration

```python
from arable.integrations.google_sheets import GoogleSheetsClient

class SheetsIntegratedAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.sheets = GoogleSheetsClient(
            credentials_path=config['google_credentials_path'],
            sheet_name=config['sheet_name'],
            logger=self.logger
        )

    async def _read_source_data(self) -> Dict[str, Any]:
        \"\"\"Read data from Google Sheets\"\"\"
        try:
            self.sheets.connect()
            projects, milestones = self.sheets.read_data()

            self.update_memory('source_data_timestamp', self._get_timestamp())
            self.update_memory('source_project_count', len(projects))

            return {
                'projects': projects,
                'milestones': milestones
            }

        except Exception as e:
            self.logger.error(f\"Google Sheets read failed: {e}\")
            raise`,
      `oldText`: `from anthropic import Anthropic

class ClaudeEnabledAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.claude = Anthropic(api_key=config['claude_api_key'])
        self.model = config.get('claude_model', 'claude-3-sonnet-20240229')

    async def _analyze_with_claude(self, document_text: str, analysis_prompt: str) -> str:
        \"\"\"Use Claude for document analysis\"\"\"
        try:
            message = self.claude.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    \"role\": \"user\",
                    \"content\": f\"{analysis_prompt}\
\
Document:\
{`
    },
    {
      `newText`: `
```

---

## Testing and Validation

Testing agents requires both unit tests for individual methods and integration tests for full workflows.

### Unit Testing Pattern

```python
# tests/agents/test_document_validator.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from arable.agents.specialized.document_validator import DocumentValidatorAgent

@pytest.fixture
def validator_agent():
    config = {
        'supported_formats': ['pdf', 'txt'],
        'max_file_size_mb': 10,
        'required_fields': ['Project Number']
    }
    return DocumentValidatorAgent('test_validator', config)

@pytest.mark.asyncio
async def test_validate_existing_file(validator_agent, tmp_path):
    # Create test file
    test_file = tmp_path / \"test.txt\"
    test_file.write_text(\"Project Number: 12345\")

    task = {
        'file_path': str(test_file),
        'validation_rules': {}
    }

    result = await validator_agent.execute(task)

    assert result['success'] is True
    assert result['validation_result']['file_exists'] is True
    assert result['validation_result']['format_valid'] is True

@pytest.mark.asyncio
async def test_validate_missing_file(validator_agent):
    task = {
        'file_path': '/nonexistent/file.txt',
        'validation_rules': {}
    }

    result = await validator_agent.execute(task)

    assert result['success'] is True  # Agent runs successfully
    assert result['validation_result']['file_exists'] is False
    assert len(result['validation_result']['errors']) > 0

def test_capabilities_declaration(validator_agent):
    capabilities = validator_agent.get_capabilities()

    assert len(capabilities) == 3
    assert any(cap.name == 'validate_document_format' for cap in capabilities)
    assert any('file_path' in cap.input_types for cap in capabilities)
```

### Integration Testing

```python
# tests/integration/test_agent_workflow.py
import pytest
import asyncio
from arable.agents.specialized.document_validator import DocumentValidatorAgent
from arable.agents.specialized.document_extractor import DocumentExtractorAgent

@pytest.mark.asyncio
async def test_validation_to_extraction_workflow(tmp_path):
    # Setup test document
    test_doc = tmp_path / \"proposal.txt\"
    test_doc.write_text(\"\"\"
    Project Number: 12345
    Customer: ACME Corp
    Amount: $150,000
    \"\"\")

    # Initialize agents
    validator = DocumentValidatorAgent('validator', {
        'supported_formats': ['txt'],
        'max_file_size_mb': 10
    })

    extractor = DocumentExtractorAgent('extractor', {
        'extraction_fields': ['Project Number', 'Customer', 'Amount']
    })

    # Step 1: Validate document
    validation_task = {'file_path': str(test_doc)}
    validation_result = await validator.execute(validation_task)

    assert validation_result['success'] is True
    assert validation_result['validation_result']['content_valid'] is True

    # Step 2: Extract data (only if validation passes)
    if validation_result['validation_result']['content_valid']:
        extraction_task = {'file_path': str(test_doc)}
        extraction_result = await extractor.execute(extraction_task)

        assert extraction_result['success'] is True
        assert 'Project Number' in extraction_result['extracted_data']
        assert extraction_result['extracted_data']['Project Number'] == '12345'
```

### Mock External Services

```python
@pytest.mark.asyncio
@patch('arable.integrations.monday.MondayAPI')
async def test_monday_integration(mock_monday_api, tmp_path):
    # Mock Monday.com API responses
    mock_monday_api.return_value.create_project_board.return_value = '123456789'

    agent = MondayIntegratedAgent('test_agent', {
        'monday_api_token': 'fake_token',
        'template_board_id': '111',
        'projects_folder_id': '222'
    })

    project_data = {
        'ProjectNumber': '12345',
        'ProjectName': 'Test Project',
        'Customer': 'ACME Corp'
    }

    board_id = await agent._create_project_board(project_data)

    assert board_id == '123456789'
    assert '123456789' in agent.get_memory('created_boards')
```

---

## Advanced Agent Patterns

### Multi-Step Processing Agent

```python
class MultiStepProcessorAgent(BaseAgent):
    \"\"\"Agent that processes tasks in multiple stages\"\"\"

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        steps = [
            self._step_1_validate,
            self._step_2_transform,
            self._step_3_enrich,
            self._step_4_output
        ]

        current_data = task.get('input_data')
        step_results = []

        for i, step_func in enumerate(steps, 1):
            self.set_status(f\"step_{i}_processing\")

            try:
                step_result = await step_func(current_data)
                step_results.append(step_result)
                current_data = step_result.get('output_data', current_data)

                self.update_memory(f'step_{i}_result', step_result)

            except Exception as e:
                self.logger.error(f\"Step {i} failed: {e}\")
                self.set_status(f\"step_{i}_failed\")
                return {
                    'success': False,
                    'failed_step': i,
                    'error': str(e),
                    'completed_steps': step_results
                }

        self.set_status(\"completed\")
        return {
            'success': True,
            'final_data': current_data,
            'step_results': step_results
        }

    async def _step_1_validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Validation logic
        return {'status': 'validated', 'output_data': data}

    async def _step_2_transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Transformation logic
        return {'status': 'transformed', 'output_data': data}
```

### Error Recovery Agent

```python
class ErrorRecoveryAgent(BaseAgent):
    \"\"\"Agent with built-in error recovery and retry logic\"\"\"

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay_seconds', 5)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        for attempt in range(self.max_retries + 1):
            try:
                self.set_status(f\"attempt_{attempt + 1}\")
                result = await self._process_task(task)

                self.update_memory('successful_attempts',
                    self.get_memory('successful_attempts', 0) + 1
                )

                return result

            except Exception as e:
                self.logger.warning(f\"Attempt {attempt + 1} failed: {e}\")

                if attempt < self.max_retries:
                    self.logger.info(f\"Retrying in {self.retry_delay} seconds...\")
                    await asyncio.sleep(self.retry_delay)
                else:
                    self.set_status(\"failed\")
                    self.update_memory('failed_attempts',
                        self.get_memory('failed_attempts', 0) + 1
                    )
                    return {
                        'success': False,
                        'error': str(e),
                        'attempts': attempt + 1
                    }
```

### Batch Processing Agent

```python
class BatchProcessingAgent(BaseAgent):
    \"\"\"Agent that processes multiple items efficiently\"\"\"

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.batch_size = config.get('batch_size', 10)
        self.max_concurrent = config.get('max_concurrent', 3)

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        items = task.get('items', [])

        if not items:
            return {'success': True, 'processed': 0, 'results': []}

        # Process items in batches
        results = []
        total_items = len(items)

        for i in range(0, total_items, self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1

            self.logger.info(f\"Processing batch {batch_num} ({len(batch)} items)\")
            self.set_status(f\"batch_{batch_num}_processing\")

            # Process batch with concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent)
            batch_tasks = [
                self._process_item_with_semaphore(semaphore, item)
                for item in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)

            # Update progress
            progress = (i + len(batch)) / total_items * 100
            self.update_memory('progress_percent', progress)

        self.set_status(\"completed\")
        return {
            'success': True,
            'processed': len(results),
            'results': results,
            'batches_processed': (total_items // self.batch_size) + 1
        }

    async def _process_item_with_semaphore(self, semaphore: asyncio.Semaphore, item: Any) -> Dict[str, Any]:
        async with semaphore:
            return await self._process_single_item(item)

    async def _process_single_item(self, item: Any) -> Dict[str, Any]:
        # Override this method with specific processing logic
        await asyncio.sleep(0.1)  # Simulate processing time
        return {'item': item, 'status': 'processed'}
```

---

## Agent Development Best Practices

### 1. Configuration Management

```python
class WellConfiguredAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)

        # Validate required configuration
        required_keys = ['api_key', 'endpoint_url']
        for key in required_keys:
            if key not in config:
                raise ValueError(f\"Required config key missing: {key}\")

        # Set defaults for optional configuration
        self.timeout = config.get('timeout_seconds', 30)
        self.retries = config.get('max_retries', 3)
        self.debug_mode = config.get('debug', False)

        # Initialize resources
        self._setup_connections()
```

### 2. Comprehensive Logging

```python
async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
    task_id = task.get('id', 'unknown')

    self.logger.info(f\"Starting task {task_id}\")
    self.logger.debug(f\"Task details: {task}\")

    start_time = time.time()

    try:
        result = await self._process_task(task)

        execution_time = time.time() - start_time
        self.logger.info(f\"Task {task_id} completed in {execution_time:.2f}s\")

        return result

    except Exception as e:
        execution_time = time.time() - start_time
        self.logger.error(f\"Task {task_id} failed after {execution_time:.2f}s: {e}\")
        raise
```

### 3. Resource Cleanup

```python
class ResourceManagedAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.connections = []
        self.temp_files = []

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return await self._process_task(task)
        finally:
            await self._cleanup_resources()

    async def _cleanup_resources(self):
        # Close connections
        for conn in self.connections:
            try:
                await conn.close()
            except Exception as e:
                self.logger.warning(f\"Error closing connection: {e}\")

        # Remove temporary files
        for temp_file in self.temp_files:
            try:
                os.remove(temp_file)
            except Exception as e:
                self.logger.warning(f\"Error removing temp file {temp_file}: {e}\")
```

### 4. Performance Monitoring

```python
def get_capabilities(self) -> List[AgentCapability]:
    # Update metrics when capabilities are queried
    self.update_memory('capability_queries',
        self.get_memory('capability_queries', 0) + 1
    )

    return self._capabilities

async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
    start_time = time.time()

    try:
        result = await self._process_task(task)

        # Record success metrics
        execution_time = time.time() - start_time
        self.update_memory('total_executions',
            self.get_memory('total_executions', 0) + 1
        )
        self.update_memory('total_execution_time',
            self.get_memory('total_execution_time', 0.0) + execution_time
        )

        return result

    except Exception as e:
        # Record failure metrics
        self.update_memory('failed_executions',
            self.get_memory('failed_executions', 0) + 1
        )
        raise
```

---

## Next Steps

After mastering the BaseAgent framework:

1. **Implement Specialized Agents**: Create domain-specific agents for your use case
2. **Build Agent Orchestration**: Coordinate multiple agents for complex workflows
3. **Add Claude Integration**: Leverage LLM intelligence for complex reasoning
4. **Create Custom CLI Commands**: Expose agent functionality through the CLI
5. **Develop Monitoring**: Build dashboards for agent performance and health

The BaseAgent framework provides the foundation for building sophisticated, production-ready agents that integrate seamlessly with ARABLE's hybrid CLI-agent architecture.
