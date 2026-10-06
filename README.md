# AURA — Autonomous Business Intelligence Agent

> An agentic AI system that combines multi-agent reasoning, business-data analysis, SQL execution, research, RAG, memory, evaluation, and a modern web interface into a single AI business assistant.

## 🚀 Overview

**AURA (Autonomous Business Intelligence Agent)** is a full-stack Agentic AI project designed to help users interact with business data and information using natural language.

Instead of manually writing SQL queries, searching through documents, or switching between multiple tools, users can ask AURA questions in natural language.

AURA determines the appropriate capability, retrieves or computes the required information, and returns a grounded response.

### Example

**User**

> What is the total revenue?

**AURA**

> The total revenue is **7,055,000**.

The business database is queried through a dedicated SQL Agent rather than allowing the language model to invent numerical results.

---

# 🧠 Architecture

```text
                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │   AURA UI   │
                    │ React + CSS │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    │   Backend   │
                    └──────┬──────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ AURA Orchestrator  │
                 └─────────┬──────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
      ┌───────────┐  ┌───────────┐  ┌─────────────┐
      │ Research  │  │ SQL Agent │  │Data Analyst │
      │   Agent   │  │           │  │    Agent    │
      └─────┬─────┘  └─────┬─────┘  └──────┬──────┘
            │              │               │
            ▼              ▼               ▼
        Web / RAG       Business DB     Analytics
            │              │               │
            └──────────────┼───────────────┘
                           ▼
                    ┌─────────────┐
                    │   Critic /  │
                    │  Evaluator  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Response  │
                    └─────────────┘
```

---

# ✨ Key Features

### 🤖 Multi-Agent Architecture

AURA uses specialized agents rather than relying on a single general-purpose prompt.

| Agent | Responsibility |
|---|---|
| **Orchestrator** | Routes and coordinates user requests |
| **Research Agent** | Research, web retrieval, CV/RAG and memory-related tasks |
| **SQL Agent** | Executes grounded, read-only business database queries |
| **Data Analyst Agent** | Performs business analysis, rankings, comparisons and profitability analysis |
| **Critic Agent** | Evaluates accuracy, completeness, grounding and relevance |

### 🗄️ Natural-Language SQL

Users can ask questions such as:

```text
What is the total revenue?

Which region has the highest revenue?

Which region is the most profitable?

What is the revenue by region?
```

AURA converts the request into an appropriate read-only SQL operation and uses the database result as the source of truth.

### 🔒 SQL Safety

Database operations are restricted to analytical read-only queries.

The system validates SQL before execution and prevents destructive operations such as:

```text
DELETE
UPDATE
DROP
INSERT
ALTER
```

### 🧠 Conversational Memory

AURA maintains short-term conversation context using Redis-backed session memory.

The memory layer supports:

- Conversation history
- Recent-context retrieval
- Session clearing
- Message limits
- Session expiration
- Basic fact extraction

### 📚 RAG

AURA includes a retrieval layer using a vector database for document-based information retrieval.

The system can retrieve relevant information instead of relying entirely on model memory.

### 🔬 Research Agent

For research-oriented questions, AURA can use retrieval tools and synthesize information rather than blindly generating an answer.

### 🧪 Critic & Evaluation

AURA includes an evaluation layer designed to assess:

- Accuracy
- Completeness
- Grounding
- Relevance
- Clarity

The system can identify insufficient evidence and trigger additional reasoning when required.

### ⚡ SQL Fast Path

Simple database questions can bypass unnecessary orchestration and go directly to the SQL Agent.

```text
Simple DB Question
       ↓
SQL Fast Path
       ↓
SQL Agent
       ↓
Database
       ↓
Grounded Answer
```

More complex requests continue through the full orchestration layer.

### 🌐 Full-Stack Interface

AURA includes:

- React frontend
- FastAPI backend
- REST API
- Interactive chat interface
- Session-based conversations
- Agent backend

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Backend | FastAPI |
| Agent Runtime | OpenAI Agents SDK |
| LLM Interface | OpenAI-compatible API |
| Database | SQLite / PostgreSQL-compatible architecture |
| Vector Database | ChromaDB |
| Memory | Redis |
| RAG | Sentence Transformers + ChromaDB |
| Frontend | React |
| API Server | Uvicorn |
| Database Access | SQL |
| Tool Protocol | MCP |
| Testing | Python / evaluation framework |
| Version Control | Git + GitHub |

---

# 📁 Project Structure

```text
AURA/
│
├── app/
│   ├── agent.py
│   ├── api.py
│   ├── auth.py
│   ├── cache.py
│   ├── config.py
│   ├── critic_agent.py
│   ├── data_analyst_agent.py
│   ├── database.py
│   ├── evaluation.py
│   ├── evaluation_dataset.py
│   ├── guardrails.py
│   ├── ingest.py
│   ├── main.py
│   ├── mcp_client.py
│   ├── mcp_server.py
│   ├── memory.py
│   ├── memory_manager.py
│   ├── memory_store.py
│   ├── model_config.py
│   ├── observability.py
│   ├── orchestrator.py
│   ├── rate_limiter.py
│   ├── research_agent.py
│   ├── retriever.py
│   ├── seed_database.py
│   ├── sql_agent.py
│   ├── tools.py
│   └── vector_store.py
│
├── data/
│   ├── business.db
│   ├── chroma/
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── Markdown.jsx
│   └── package.json
│
├── tests/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

# ▶️ Running AURA Locally

## 1. Clone the repository

```bash
git clone https://github.com/ArunAllu07/Autonomous-Business-Intelligence-Agent.git

cd Autonomous-Business-Intelligence-Agent
```

## 2. Create the environment

```bash
python -m venv venv
```

### Windows

```powershell
.\venv\Scripts\Activate.ps1
```

## 3. Configure environment variables

Create a local `.env` file with the required configuration.

**Do not commit `.env` to GitHub.**

The repository is designed to keep credentials outside version control.

## 4. Start the backend

```powershell
uvicorn app.api:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## 5. Start the frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🌐 Demo / HR Links

For a local demonstration, start both the backend and frontend.

### 💬 AURA Chatbot

[http://localhost:5173](http://localhost:5173?utm_source=chatgpt.com)

### ⚙️ Backend API

[http://127.0.0.1:8000](http://127.0.0.1:8000?utm_source=chatgpt.com)

### ❤️ Health Check

[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health?utm_source=chatgpt.com)

### 📚 Interactive API Documentation

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs?utm_source=chatgpt.com)

> **Note:** These are local development URLs. They work when AURA is running on the demonstration machine. They are not public internet links.

---

# 💬 Example Questions for an HR Demo

Use these questions to demonstrate different capabilities.

### Business Intelligence

```text
What is the total revenue?
```

```text
Which region has the highest revenue?
```

```text
Which region is the most profitable?
```

```text
What is the revenue by region?
```

### Research

```text
Research the latest developments in generative AI.
```

### Memory

```text
Remember that AURA is my autonomous business intelligence project.
```

Then ask a follow-up question that requires the stored context.

### Database Reasoning

```text
Compare regional revenue and profitability.
```

---

# 🔐 Security & Reliability

AURA was designed with several defensive mechanisms:

- Read-only SQL validation
- Prompt-injection-aware agent instructions
- No credentials in source code
- Environment-variable configuration
- Tool-result grounding
- Agent evaluation
- Request tracing
- Session isolation
- Database access restrictions
- Human approval architecture for sensitive operations

The system treats retrieved documents, web content, database values and tool outputs as **data rather than trusted instructions**.

---

# 📊 Engineering Highlights

The project demonstrates practical implementation of:

```text
Agentic AI
Multi-Agent Systems
LLM Tool Calling
Natural Language → SQL
RAG
Vector Databases
Conversational Memory
MCP
FastAPI
React
REST APIs
Database Engineering
SQL Guardrails
Prompt Injection Defense
Agent Evaluation
Observability
Git / GitHub
```

---

# 🧪 Evaluation

AURA includes an evaluation framework for testing agent responses against predefined business questions.

Evaluation criteria include:

- Accuracy
- Grounding
- Completeness
- Relevance
- Clarity
- Numerical correctness
- Tool-use correctness

The evaluation framework is designed to catch cases where an agent produces a plausible answer without sufficient evidence.

---

# 🚧 Current Status

### Working

- FastAPI backend
- React frontend
- AURA orchestrator
- SQL Agent
- Business database
- SQL validation
- MCP server
- RAG infrastructure
- Conversation memory architecture
- Critic/evaluation infrastructure
- Observability/logging
- Natural-language business queries

### Development / Future Work

- Production-grade latency optimization
- Redis production deployment
- Full PostgreSQL deployment
- Docker deployment
- Cloud hosting
- Advanced frontend agent tracing
- Expanded evaluation benchmark
- Human-in-the-loop approval UI

---

# 🗺️ Future Roadmap

```text
Current
  │
  ├── Agentic orchestration
  ├── SQL analytics
  ├── RAG
  ├── Memory
  ├── MCP
  └── Evaluation
       │
       ▼
Production Hardening
       │
       ├── Redis
       ├── PostgreSQL
       ├── Docker
       ├── Observability
       └── Automated testing
       │
       ▼
Deployment
       │
       ├── Cloud backend
       ├── Public frontend
       └── CI/CD
```

---

# 👨‍💻 Author

**Kethavath Arun**

Integrated Dual Degree  
Metallurgical & Materials Engineering  
IIT Kharagpur

GitHub:

[ArunAllu07](https://github.com/ArunAllu07?utm_source=chatgpt.com)

Project:

[Autonomous Business Intelligence Agent](https://github.com/ArunAllu07/Autonomous-Business-Intelligence-Agent?utm_source=chatgpt.com)

---

# ⭐ Project Summary

**AURA is an end-to-end Agentic AI system that connects LLM reasoning with real business data, tools, retrieval, memory and evaluation.**

The primary engineering goal is not simply to build a chatbot, but to demonstrate how an AI system can **reason, select tools, retrieve evidence, execute safe database operations, maintain context and evaluate its own responses.**