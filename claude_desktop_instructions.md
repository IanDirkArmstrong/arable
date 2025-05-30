# ARABLE - Claude Desktop Project Instructions

## Project Context

**ARABLE (Agentic Runtime And Business Logic Engine)** - Multi-agent system for document extraction, CRM reconciliation, and workflow automation.

**Current Phase**: Migration from monday_automation to agent-based architecture  
**Tech Stack**: Python 3.9+, Typer CLI, Rich UI, Pydantic, Claude API  
**Client**: RSi Visual Systems (contractor relationship)

## File Structure

- `/arable/` - Main Python package (agents, CLI, integrations)
- `/config/` - YAML configuration templates
- `/data/` - CRM backups, cache, extraction results
- `/scripts/` - Migration and development utilities
- `/docs/` - Architecture, guides, and API documentation
- Key files: `docs/file_index.md`, `docs/project_instructions.md`

## Available Agent Roles

Activate with: "Acting as [Role] Agent for ARABLE"

- **Project Manager** - Coordination, roadmap, stakeholder management
- **Index Keeper** - File system maintenance, documentation organization
- **Code Developer** - Python development, agent implementation, CLI commands
- **Integration Architect** - System design, API integration, data flow
- **Documentation** - Technical writing, guides, knowledge management
- **QA/Testing** - Quality assurance, validation, regression testing

## Key Integrations

- Monday.com API (60 req/min limit), Google Sheets API, Zoho CRM
- Claude API for document intelligence and matching
- RSi.Net legacy SQL (read-only access)
- Google Drive for document extraction

## Working Protocols

1. Check `docs/file_index.md` for current project state
2. Update file index when making changes
3. Use direct, technical language with actionable next steps
4. Focus on quick wins and visible progress for post-layoff environment
5. Maintain code quality standards (black, isort, mypy, pytest)

## Current Priorities

Phase 1 (Week 1): Migration tooling and CLI foundation  
Phase 2 (Week 2): Document extraction agent with Claude integration  
Phase 3 (Week 3): CRM matching and reconciliation agents  
Phase 4 (Week 4): Full workflow integration and RSi deployment

## Success Metrics

- Reliable cross-platform data synchronization
- Reduced manual data entry and reconciliation
- Maintainable agent codebase for client handoff
- Clear audit trails and process documentation
