# 🚀 AURA — Autonomous Business Intelligence Agent

> An agentic AI system that autonomously researches, analyzes, queries business data, remembers context, and produces grounded answers using specialized AI agents and tools.

---

## 🌐 Try AURA

### 💬 AURA Chatbot
[Open AURA Chatbot](http://localhost:5173)

### ⚡ FastAPI Backend
[Open FastAPI Backend](http://127.0.0.1:8000)

### 📚 API Documentation
[Open Swagger Docs](http://127.0.0.1:8000/docs)

### ❤️ API Health
[Check AURA Health](http://127.0.0.1:8000/health)

> These links work when AURA is running locally.

---

# 🧠 What is AURA?

AURA is a production-oriented **multi-agent AI system** designed to answer business and research questions by selecting the appropriate agent and tools instead of relying only on an LLM response.

AURA can:

- 🔎 Perform web research
- 📊 Analyze business data
- 🗄️ Query PostgreSQL databases
- 📄 Retrieve information from documents/CV using RAG
- 🧠 Maintain short-term and long-term memory
- 🧮 Perform calculations
- 🛡️ Block unsafe SQL operations
- 🔄 Coordinate multiple specialized agents
- 🧪 Evaluate generated responses
- 📈 Monitor requests and agent execution

---

# 🏗️ System Architecture

```text
                         USER
                           │
                           ▼
                 ┌──────────────────┐
                 │    AURA API      │
                 │     FastAPI      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   ORCHESTRATOR   │
                 │  Agent Manager   │
                 └────────┬─────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │ Research   │  │ SQL Agent  │  │ Data       │
   │ Agent      │  │            │  │ Analyst    │
   └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
         │               │                │
         ▼               ▼                ▼
     Web Search      PostgreSQL        Business Data
         │
         ▼
       RAG
         │
         └───────────────┐
                         ▼
                    ┌───────────┐
                    │  Memory   │
                    │Redis + DB │
                    └─────┬─────┘
                          │
                          ▼
                   ┌────────────┐
                   │  Critic /  │
                   │ Evaluator  │
                   └─────┬──────┘
                         │
                         ▼
                    FINAL ANSWER