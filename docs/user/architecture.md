# 🏗️ ARABLE System Architecture

Understand ARABLE's hybrid CLI-agent design and how the components work together.

---

## 🔧 Architecture Philosophy

**Hybrid Approach**: Manual CLI tools + intelligent agent extensions.

- 🛠️ **CLI-first**: Typer-based commands for consistent, predictable operation
- 🤖 **Agent-enhanced**: Add smart features when needed
- 🔁 **Progressive automation**: Start manual, automate incrementally

> ARABLE does **not** replace the CLI with agents — it **enhances** it with modular intelligence.

---

## 🧱 System Overview

```
ARABLE System Stack

┌───────────────────────────────┐
│       CLI Interface           │
│  (Typer + Rich terminal UI)  │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│     Command Processors        │
│ ┌──────┐  ┌──────┐  ┌───────┐ │
│ │project│  │sync  │  │...    │ │
│ └──────┘  └──────┘  └───────┘ │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│     Integration Layer         │
│ ┌──────────┐ ┌─────────────┐ │
│ │Monday.com│ │Google Sheets│ │
│ └──────────┘ └─────────────┘ │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│      Agent Framework (🧠)      │
│     (Modular, Optional)       │
└───────────────────────────────┘
```

---

## 🧠 Agent Framework (Future-Ready)

- Runs in parallel with CLI commands or can act autonomously
- Receives inputs from command processors
- Can read and update state via memory management
- Tied into sync logic and reconciliation logic

📎 Learn more:  
- [`agent_basics.md`](../technical/development/agent_basics.md)  
- [`baseagent_reference.md`](../technical/development/baseagent_reference.md)
