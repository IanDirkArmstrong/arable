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