# Architecture — Hackathon Mentor AI Assistant

## System Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐      ┌──────────────┐
│   INPUT UI  │─────▶│   BACKEND    │─────▶│   AI MENTOR      │─────▶│  OUTPUT VIEW │
│  (Aaron)    │      │   (Flask)    │      │   LOGIC (Savio)  │      │  (Anurodh)   │
└─────────────┘      └──────────────┘      └─────────────────┘      └──────────────┘
      │                     │                       │                       │
      │                     │                       ▼                       │
      │                     │              ┌─────────────────┐              │
      │                     │              │  Groq API        │              │
      │                     │              │  (llama-3.3-70b) │              │
      │                     │              └─────────────────┘              │
      │                     │                       │                       │
      │                     │                       ▼ (on failure)          │
      │                     │              ┌─────────────────┐              │
      │                     └─────────────▶│  Rule-based      │──────────────┘
      │                                    │  Fallback        │
      │                                    └─────────────────┘
      │
      ▼
Problem statement + team context (name, skills, time left)
```

## Component Breakdown

### 1. Input Layer (Aaron)
- Minimal form/chat box: `problem_statement` (string), `team_context` (string, optional)
- Submits to backend via single POST request
- No client-side validation logic beyond "not empty" — keep it dumb, push logic to backend

### 2. Backend / Orchestration (Flask, shared — Savio owns endpoint, Aaron wires UI to it)
- Single route: `POST /api/mentor`
- Accepts `{ problem_statement, team_context }`
- Calls `get_mentor_guidance()` from `mentor_logic.py`
- Returns the JSON schema (see `TECH_STACK.md` for schema definition) or fallback JSON
- No database — stateless, single request/response. No persistence needed for a 90-min prototype.

### 3. AI Mentor Logic (Savio)
- `mentor_logic.py` — already built
- System prompt enforces "guide, not solve"
- Groq API call in JSON mode
- Rule-based fallback (keyword-matched canned response + generic fallback)

### 4. Output View (Anurodh)
- Consumes the same JSON schema regardless of whether it came from the API or fallback
- Renders as sectioned cards: Summary → Personas → Features → Tech Stack → Priorities → Checkpoints → Demo Tips → Decision/Reason/Next Action
- No re-fetching or polling — single render per submission

## Data Flow (End-to-End)

1. Team enters problem statement + context → Aaron's UI
2. UI POSTs to `/api/mentor` → Backend
3. Backend calls `get_mentor_guidance()` → Savio's logic
4. Logic calls Groq; on failure, drops to fallback — **caller never knows which path was used**, schema is identical either way
5. JSON response returned to UI
6. Anurodh's renderer displays it as structured sections

## Why This Shape

- **Single API contract, two implementations (live + fallback)** — the demo never breaks on stage even if Groq rate-limits or the wifi drops
- **No database** — nothing to seed, migrate, or debug under time pressure
- **Stateless** — every team member can test their layer independently by hardcoding the JSON schema before the other two parts are ready (see `BEST_PRACTICES.md`)
