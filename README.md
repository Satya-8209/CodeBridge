# 🌉 CodeBridge: DevOps Incident Memory Agent

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Hindsight Memory](https://img.shields.io/badge/Memory-Vectorize%20Hindsight-6C5CE7.svg?style=flat)](https://hindsight.vectorize.io/)
[![Groq LLM](https://img.shields.io/badge/LLM-Groq%20(gpt--oss--120b)-F55036.svg?style=flat)](https://groq.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Autonomous on-call SRE/DevOps agent that remembers past production outages, learns from resolutions, and provides instant root-cause diagnostics with proven runbook fixes.**

Built for **HackWithHyderabad 3.0** under the theme *"AI Agents That Learn Using Hindsight"*.

---

## 📌 The Problem: Production Amnesia

When critical production services crash at 3 AM:
- **Engineers waste 30–60 minutes** digging through stale Slack channels, old Jira tickets, scattered Confluence runbooks, and raw PagerDuty logs to see if anyone encountered this failure before.
- **The same incidents repeat** (OOM container kills from retry leaks, database pool exhaustion, misconfigured Kubernetes manifests, expired SSL certificates).
- **Tribal knowledge is lost** when team members leave or are off-shift.
- **Post-mortems are written but forgotten**, buried in documentation wikis.

### 🔴 Without Memory (Stateless AI Chatbot)
> *"I noticed an OOMKilled error on payment-service. You should check your memory limits, examine your logs, or review your container configuration."*  
> ⚠️ **Generic, slow, unhelpful in high-severity outages.**

### 🟢 With CodeBridge (Hindsight Persistent Memory)
> *"This exact incident occurred on payment-service. In that incident, an unbounded list in the Stripe webhook retry handler accumulated payloads until hitting the 512Mi limit. Engineers resolved it by rolling back to `v2.3.1` using `kubectl rollout undo deployment/payment-service` and capping the queue at 100 entries. Similarity match: 88.3%."*  
> ⚡ **Actionable, precise, resolves incidents in minutes instead of hours.**

---

## 🧠 The Star: How Hindsight Memory Works

CodeBridge leverages [Vectorize Hindsight](https://hindsight.vectorize.io/), a purpose-built long-term memory engine for AI agents. Rather than relying on simple stateless vector search, Hindsight creates **evolving institutional memory banks**.

```mermaid
flowchart TD
    subgraph Ingestion ["1. Incident Trigger"]
        Alert["🚨 Production Alert\n(K8s / Datadog / CloudWatch)"]
    end

    subgraph MemoryLayer ["2. Hindsight Memory Bank"]
        RecallAPI["🔍 hindsight.recall()\nbank_id: devops-incident-memory"]
        MemoryBank[("🧠 Vectorized Incident Memory\n• Root Causes\n• Applied Fixes\n• Time to Resolve")]
        PastMatches["📋 Top Similar Past Incidents\n(Scores: 0.88, 0.86)"]
    end

    subgraph Reasoning ["3. LLM Synthesis"]
        Groq["⚡ Groq High-Speed Inference\n(openai/gpt-oss-120b)"]
        Diagnostic["💡 AI Root-Cause Diagnostic\n& Step-by-Step Runbook Commands"]
    end

    subgraph Interfaces ["4. Multi-Channel Response"]
        WebUI["🌐 Interactive Web UI\n(http://localhost:8000/ui)"]
        CLI["⌨️ Rich Terminal CLI"]
        Slack["🔔 Slack Bot\n(/incident command)"]
    end

    subgraph Learning ["5. Feedback Loop (Learning)"]
        Resolve["✅ Incident Resolved\n(Cause + Verified Fix)"]
        RetainAPI["💾 hindsight.retain()"]
    end

    Alert --> RecallAPI
    RecallAPI <--> MemoryBank
    RecallAPI --> PastMatches
    PastMatches --> Groq
    Alert --> Groq
    Groq --> Diagnostic
    Diagnostic --> WebUI
    Diagnostic --> CLI
    Diagnostic --> Slack
    Resolve --> RetainAPI
    RetainAPI --> MemoryBank
```

### The Learning Curve (Why Judges Love It)

| Phase | Agent Behavior | Memory Status |
|---|---|---|
| **Interaction 1 (Cold Start)** | Provides general troubleshooting guidelines based on standard Kubernetes practices. | `0 memories stored` |
| **Interaction 5 (Trained)** | Identifies recurring failure modes across services and suggests matching team runbooks. | `8 memories stored` |
| **Interaction 20 (Expert SRE)** | Immediately correlates error logs to historical commits, gives exact rollback commands, and warns about secondary cascade risks. | `20+ memories stored` |

---

## ✨ Features & Multi-Interface Support

CodeBridge delivers a unified backend powering three distinct developer workflows:

### 1. 🌐 Interactive Web Dashboard (`/ui`)
- Dark-themed single-page application built for command-center monitoring.
- Real-time alert dispatching with live similarity scoring badges (`🧠 Memory Hit: 88.3%`).
- Collapsible view of historical incident snippets.
- One-click incident resolution form to instantly commit new learnings to Hindsight.

### 2. ⌨️ Rich Terminal CLI (`cli/cli.py`)
- Built with `Typer` and `Rich` for beautiful command-line formatting and colorized tables.
- Commands:
  - `python cli/cli.py alert <service> -e "<error log>"`: Query memory and retrieve diagnosis.
  - `python cli/cli.py resolve <alert_id> --service <name> --title <title> --cause <cause> --fix <fix>`: Train the agent with the resolution.
  - `python cli/cli.py health`: Instant system & backend diagnostic check.

### 3. 🔔 Slack Bot Integration (`slack_bot/bot.py`)
- Built with `slack-bolt` running over **Socket Mode**.
- Slash command: `/incident <service> | <error description>`
- Delivers rich Slack Block Kit notifications directly into on-call engineering channels.

---

## 🛠️ Tech Stack & Architecture

- **Memory Engine:** [Hindsight](https://hindsight.vectorize.io/) Python Client (`hindsight-client`)
- **Language Model:** Groq API (`openai/gpt-oss-120b` / `llama-3.1-8b-instant`)
- **Backend Framework:** FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings
- **Terminal UX:** Typer, Rich, Colorama
- **ChatOps:** Slack Bolt for Python (Socket Mode)
- **HTTP Client:** HTTPX

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- Hindsight API Key ([Vectorize Hindsight](https://ui.hindsight.vectorize.io/))
- Groq API Key ([Groq Console](https://console.groq.com/))

### 1. Clone the Repository
```bash
git clone https://github.com/Satya-8209/CodeBridge.git
cd CodeBridge
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the example environment file and add your credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```env
HINDSIGHT_API_KEY=hsk_your_hindsight_key_here
HINDSIGHT_BANK_ID=devops-incident-memory
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=openai/gpt-oss-120b
LLM_PROVIDER=groq

# Optional: Slack Bot credentials
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
SLACK_SIGNING_SECRET=your-secret
```

### 4. Start the FastAPI Backend
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- Web UI: [http://localhost:8000/ui](http://localhost:8000/ui)
- Interactive API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Seed Historical Memory (For Demo & Testing)
Pre-populate the Hindsight bank with 8 real-world production incident records:
```bash
python scripts/seed.py
```

---

## 🧪 Live Demo Walkthrough

### Step 1: Fire an Incident Alert via CLI
Simulate an on-call alert for an OOMKilled payment pod:
```bash
python cli/cli.py alert payment-service -e "OOMKilled: payment-service pod restarted 3 times in the last 5 minutes. Container exceeded memory limit of 512Mi."
```

**Output:**
```
🔍 Querying Hindsight memory...
   Service: payment-service
   Alert:   OOMKilled: payment-service pod restarted 3 times...

┌───────────────────────────── Hindsight Memory ──────────────────────────────┐
│ 🧠 Found 5 similar past incident(s) in memory                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                Past Incidents                                 
┌─────┬────────────────────────────────────────────────────────────┬──────────┐
│ #   │ Memory Snippet                                             │ Score    │
├─────┼────────────────────────────────────────────────────────────┼──────────┤
│ 1   │ payment-service pod experienced OOMKilled restarts 4 times │ 0.883    │
│     │ in 10 minutes due to a memory leak in the Stripe webhook   │          │
│     │ retry handler. | Unbounded list caused memory to exceed... │          │
│ 2   │ The payment-service pod suffered 4 OOMKilled restarts...   │ 0.860    │
└─────┴────────────────────────────────────────────────────────────┴──────────┘

┌────────────────── 💡 AI Suggestion (Alert ID: 6FFAC39E) ───────────────────┐
│ Root Cause:                                                                 │
│ The pod is hitting the 512Mi memory limit because the Stripe webhook retry   │
│ handler is leaking memory. An unbounded in-memory list grows with each retry│
│ (500+ payloads). Matches 2 high-similarity past incidents.                  │
│                                                                             │
│ Fix Steps:                                                                  │
│ 1. Roll back the deployment:                                                │
│    kubectl set image deployment/payment-service payment-service=v2.3.1       │
│ 2. Patch the handler in v2.3.3 to cap the retry list at 100 entries.        │
│ 3. Monitor container_memory_usage_bytes < 400Mi.                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Step 2: Open the Web UI
Visit **`http://localhost:8000/ui`** in your browser to inspect the visual incident dashboard, view similarity scores, and test real-time incident resolution.

---

## 📡 API Reference

| Endpoint | Method | Payload | Description |
|---|---|---|---|
| `/alert` | `POST` | `{"title": str, "service": str, "severity": str, "error_log": str}` | Queries Hindsight memory, synthesizes context with LLM, returns root cause & fix. |
| `/resolve` | `POST` | `{"alert_id": str, "service": str, "title": str, "root_cause": str, "fix_applied": str, "time_to_resolve_minutes": int}` | Commits resolved incident and fix into Hindsight persistent memory bank. |
| `/health` | `GET` | _None_ | Returns service uptime and connectivity status. |
| `/ui` | `GET` | _None_ | Serves the interactive Single Page Application. |

---

## 📁 Repository Structure

```
CodeBridge/
├── backend/
│   ├── __init__.py           # Package marker
│   ├── config.py             # Pydantic Settings configuration
│   ├── schemas.py            # API request/response models
│   ├── hindsight_client.py   # Vectorize Hindsight retain & recall wrappers
│   ├── agent.py              # Core reasoning engine (Hindsight + Groq)
│   └── main.py               # FastAPI application entrypoint
├── cli/
│   └── cli.py                # Typer & Rich interactive CLI tool
├── slack_bot/
│   └── bot.py                # Slack Bolt Socket Mode bot
├── web_ui/
│   └── index.html            # Dark-mode dashboard UI
├── data/
│   └── seed_incidents.json   # 8 production outage benchmark scenarios
├── scripts/
│   └── seed.py               # Database/Memory seeding automation script
├── .env.example              # Template environment variables
├── .gitignore                # Excludes secrets, cache, logs, docx files
├── requirements.txt          # Python project dependencies
└── README.md                 # Complete project documentation
```

---

## 🏆 Hackathon Submission Checklist

- [x] **Core Technology:** Deeply integrated with **Vectorize Hindsight** (`bank_id`, `retain`, `recall`).
- [x] **Centrality of Memory:** Memory is the foundational engine (25% judging criteria).
- [x] **Innovation:** Real-world DevOps / SRE workflow solving multi-million dollar downtime incidents.
- [x] **Technical Implementation:** FastAPI asynchronous architecture, multiple interfaces (Web, CLI, Slack), and production schema validation.
- [x] **Clean Repository:** Fully documented, secrets protected with `.gitignore`, synthetic benchmark data included.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
