# ARABLE Examples

This directory contains example workflows, configurations, and demonstrations of the ARABLE agent system.

## Examples

- `extract_and_sync_workflow.yaml` - Complete document extraction to Monday.com sync workflow
- `sample_proposal.txt` - Sample proposal document for testing extraction
- `agent_demo.py` - Python script demonstrating programmatic agent usage

## Usage

Run examples using the ARABLE CLI:

```bash
# List available agents
arable agents list

# Run document extraction demo
arable demo

# Execute single agent
arable agents run --agent documentextractor --data '{"document_path": "examples/sample_proposal.txt", "extraction_type": "proposal"}'
```
