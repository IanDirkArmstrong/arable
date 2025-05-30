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