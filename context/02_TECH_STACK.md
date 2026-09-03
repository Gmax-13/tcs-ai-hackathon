# Tech Stack — Hackathon Mentor AI Assistant

## Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | HTML/JS or React (Aaron's call) | Minimal input form — don't over-invest here |
| Backend | Flask (Python) | Fast to stand up, one route, no boilerplate |
| AI | Groq API — `llama-3.3-70b-versatile` | Fast inference (sub-second), JSON mode support, free tier sufficient for demo |
| Fallback | Rule-based Python dict lookup | Zero external dependency, guarantees demo never fails |
| Hosting (if needed) | Localhost / ngrok for demo | No deployment complexity for a 90-min prototype |
| Data | None persisted — stateless request/response | No DB setup/debugging time cost |

## Explicitly Not Using
- No database (Postgres/Mongo/etc.) — nothing to persist across a single-session demo
- No auth — not relevant to the prototype scope
- No frontend framework overhead (Next.js, routing, state management) unless Aaron already has boilerplate ready — a static form is enough

## The Contract (lock this before 1:55 sync)

**Request** (`POST /api/mentor`):
```json
{
  "problem_statement": "string, required",
  "team_context": "string, optional"
}
```

**Response** (identical shape whether from Groq or fallback):
```json
{
  "problem_summary": "string",
  "key_questions": ["string", "string", "string"],
  "user_personas": [
    { "name": "string", "need": "string", "pain_point": "string" }
  ],
  "design_thinking_guidance": "string",
  "feature_suggestions": [
    { "feature": "string", "why": "string", "effort": "low|medium|high" }
  ],
  "tech_stack_options": ["string", "string", "string"],
  "prototype_priorities": ["string", "string", "string"],
  "validation_checkpoints": ["string", "string"],
  "demo_prep_tips": ["string", "string", "string"],
  "decision": "string",
  "reason": "string",
  "next_action": "string"
}
```

This exact JSON is what Aaron's UI sends and what Anurodh's renderer consumes. **Nobody changes field names without updating this file and telling the other two.**
