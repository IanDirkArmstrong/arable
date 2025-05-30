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