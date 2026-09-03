# Tech Stack — Hackathon Mentor AI Assistant

## Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | HTML/JS or React (Aaron's call) | Minimal input form — don't over-invest here |
| Backend | Flask (Python) | Fast to stand up, one route, no boilerplate |
| AI | Groq API — `qwen/qwen3.8-27b` | Fast inference (sub-second), JSON mode support, free tier sufficient for demo |
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
  "team_context": "string, optional",
  "phase": "string, optional — one of: understand|build|test|demo"
}
```

**Response** (identical shape whether from Groq or fallback):
```json
{
  "problem_summary": "string",
  "assumptions": ["string — things the AI inferred, not stated by the team"],
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

## Additional Endpoints

**Follow-up** (`POST /api/followup`):
```json
// Request
{ "original_guidance": { /* full /api/mentor response */ }, "question": "string", "team_context": "string, optional" }
// Response
{ "answer": "string", "related_suggestions": ["string"], "next_steps": ["string"], "warning": "string|null" }
```

**Validator** (`POST /api/validate`):
```json
// Request
{ "problem_statement": "string" }
// Response
{ "score": number, "max_score": 10, "feedback": [{ "category": "string", "score": number, "status": "good|needs_work|warning", "note": "string" }], "improved_statement": "string|null" }
```
