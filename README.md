# Hang the DJ — Agentic Matchmaking Simulator

An experimental **agentic application** that simulates dating intake, compatibility evaluation, and relationship dynamics using multiple LLM-powered agents, long-term memory, and MCP-style tools.

This project was built as part of a course on agentic systems, with an emphasis on **ambition, architecture, and reasoning**, rather than production polish.

---

## 🧠 Project Overview

**Hang the DJ** is a multi-agent dating simulator inspired by agentic system design patterns.

The system consists of:
- Multiple **LLM-based agents** with distinct roles
- A **web UI** for live interaction and demonstration
- A **FastAPI backend** for orchestration and simulation
- **Long-term memory** via Letta
- Several **MCP-style tools** that allow agents to act, not just talk

The goal is to explore how agents:
- Gather and refine information over time  
- Coordinate through structured tools  
- Store and retrieve durable memory  
- Produce explainable decisions rather than opaque outputs  

This is intentionally a **toy / research system**, not a real dating app.

---

## 🤖 Agents

The system contains **four agents** (three matchmakers + one evaluator):

### Matchmaker Agents (A, B, C)
Each matchmaker represents a single user and is responsible for:
- Generating or incorporating **intake summaries**
- Maintaining short-term contextual memory
- Writing durable information to long-term memory (via tools)

### Neutral Evaluator (Agent #3)
The evaluator:
- Reads intake summaries from memory
- Simulates date exchanges
- Scores compatibility
- Produces explainable reports and hypotheses about user pairs

> Note: The evaluator is called “Agent #3” for historical reasons — this was left unchanged intentionally.

---

## 🧩 Architecture

### Frontend
- **Next.js** web application
- Used for:
  - Running intake
  - Triggering simulations
  - Demonstrating agent outputs live
- The UI is intentionally lightweight and demo-focused

### Backend
- **FastAPI** service
- Responsibilities:
  - Agent orchestration
  - Simulation execution
  - Tool routing
  - Integration with Letta for long-term memory

---

## 🧠 Memory Design

The system uses **two memory layers** by design:

### 1. Local / In-Process Memory
- Fast and lightweight
- Used during live simulations for responsiveness

### 2. Letta Long-Term Memory
- Durable across backend restarts
- Used to demonstrate persistence and MCP tooling
- Stores:
  - Intake summaries
  - Pair hypotheses
  - Retrieved context for agent reasoning

This split is intentional:

> Local memory keeps the UI responsive; Letta provides durability and tool orchestration.

---

## 🔧 MCP Tools

The project exposes several **MCP-style tools** — structured actions an agent can explicitly choose to invoke.

### Fully Implemented Tools
- **store_intake_summary**
  - Stores structured intake data in Letta
- **retrieve_user_memory**
  - Retrieves stored memory from Letta for agent use

These tools demonstrate:
- Explicit agent choice
- Defined input/output schemas
- Effects on the external world (persistent memory)

### Partially Implemented / Demonstrated Tools
- **run_date_exchange**
- **generate_pipeline_report**
- **score_exchange**

These tools exist conceptually and are wired through the backend, but were constrained during the demo due to token limitations.

This tradeoff was intentional and discussed during presentation.

---

## 🧠 Long-Term Memory (Letta)

Letta is used to demonstrate **true long-term memory**.

Memory blocks include:
- `intake_summary::<user_id>`
- `pair_hypothesis::<user_a>::<user_b>`
- Stored reports and exchange summaries

Persistence was demonstrated by:
- Writing memory via MCP tools
- Restarting the backend
- Retrieving memory from Letta

Not all retrieval paths were fully stabilized under time constraints, but memory writes and reads were successfully demonstrated.

---

## 🧪 Demo Flow

A typical demo flow looks like:

1. Run intake for one or more users  
2. Store intake summaries via MCP tools  
3. Simulate a date exchange  
4. Generate compatibility scores and reports  
5. Retrieve stored memory to explain how conclusions evolved  

---

## 🚧 Known Limitations

- Token constraints limited repeated evaluator runs
- Some MCP tools are demonstrated conceptually rather than exhaustively
- The streaming UI path was deprioritized to preserve system stability
- Letta retrieval after backend restart was partially unstable under time pressure

These limitations were explicitly acknowledged and discussed during the demo.

---

## 🎓 Educational Focus

This project prioritizes:
- Agentic architecture
- Explicit tool usage
- Reasoning transparency
- Memory persistence
- System design tradeoffs

It is intentionally **not optimized** for:
- UX polish
- Cost efficiency
- Production deployment

---

## 🧠 Key Takeaway

> This project demonstrates how agents can be designed to **reason, act, remember, and explain**, rather than simply generate text.

---

## 🚀 Running the Project (Local)

### Backend
```bash
uvicorn app.main:app --reload
```

### Frontend
```bash
npm install
npm run dev
```

## Final Note

This project was built iteratively with AI coding assistance and reflects real-world agentic system development: tradeoffs, partial integrations, and evolving architecture.
