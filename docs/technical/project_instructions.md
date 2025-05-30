# 🗂️ ARABLE Project Instructions

High-level project context and operational guidance for maintaining and evolving the ARABLE automation platform.

---

## 🧭 Project Overview

**ARABLE** (Agentic Runtime And Business Logic Engine) is a modular automation framework designed to:

- Extract structured data from business documents
- Match and reconcile information across Zoho CRM, Monday.com, and legacy systems
- Automate workflows through CLI tools and intelligent agent orchestration

> **Current State**: Monday.com + Google Sheets automation  
> **Target**: Multi-agent system supporting document parsing, decision support, and workflow automation

---

## 🧰 Core Capabilities

- 📄 Document extraction (proposals, POs, contracts)
- 🔁 Cross-system data reconciliation
- 🧠 Agent-capable CLI with Rich components
- 🤖 Multi-agent orchestration (planned)
- 📋 Workflow automation for administrative assistants

---

## 👥 Project Roles

### 📌 Project Manager (Agent or Human)
**Purpose**: Coordinates planning and strategy  
**Responsibilities**:
- Maintain roadmap and milestones
- Update project docs when scope shifts
- Track timelines and deliverables
- Align communication across stakeholders

---

### 🗃️ Index Keeper
**Purpose**: Maintains documentation integrity  
**Responsibilities**:
- Update `file_index.md` as files change
- Track version history and structure
- Flag outdated or missing documentation

---

### 🧑‍💻 Code Developer
**Purpose**: Implements the system logic  
**Responsibilities**:
- Develop and refactor CLI and agent code
- Manage integration points with external APIs
- Build and test agent capabilities

---

## 📎 Related Docs

- [`file_index.md`](file_index.md) – File structure, versions, and change tracking
- [`architecture.md`](architecture.md) – System architecture for human maintainers
- [`architecture_plan.md`](../technical/architecture_plan.md) – Long-term architecture vision
