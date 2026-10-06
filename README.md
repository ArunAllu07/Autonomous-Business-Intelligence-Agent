# AURA — Autonomous Business Intelligence Agent

AURA is a production-oriented agentic AI system designed to research information, analyze business data, use external tools, maintain conversational memory, and evaluate its own responses.

The system combines multi-agent orchestration, tool calling, RAG, SQL analytics, Redis memory/cache, PostgreSQL, MCP, guardrails, observability, and automated evaluation into a single application.

---

## 🚀 Overview

Traditional chatbots mainly generate responses from a language model.

AURA is designed differently.

Instead of relying only on the LLM, AURA can:

- Understand the user's intent
- Route tasks to specialized agents
- Query structured business data
- Perform calculations
- Search external information
- Retrieve information from documents
- Maintain short-term conversational memory
- Maintain long-term memory
- Use Redis for caching
- Use PostgreSQL for persistent business data
- Use MCP for tool integration
- Apply SQL safety guardrails
- Detect prompt-injection attempts
- Evaluate generated answers
- Retry weak answers
- Track latency and system events
- Serve the system through a FastAPI backend
- Provide a React frontend
- Run through Docker

---

# 🧠 System Architecture

```text
                         USER
                           │
                           ▼
                    React Frontend
                           │
                           ▼
                     FastAPI API
                           │
                           ▼
                    AURA ORCHESTRATOR
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
       Research Agent   SQL Agent   Data Analyst
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                       TOOL LAYER
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Web Search      Calculator      SQL
             │             │             │
             ├─────────────┼─────────────┤
             │             │             │
             ▼             ▼             ▼
             RAG        PostgreSQL      MCP
                           │
                           ▼
                     MEMORY LAYER
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
                  Redis        Long-term
              Session Memory     Memory
                    │
                    ▼
                 Evaluator
                    │
              ┌─────┴─────┐
              │           │
            PASS         RETRY
              │           │
              └─────┬─────┘
                    ▼
                FINAL ANSWER