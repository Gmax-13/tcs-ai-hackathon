# CLAUDE.md — TCS Tech Day Hackathon: AI Mentor Assistant

> **This file is the single source of truth for Claude Code sessions.**
> The `context/` folder is the project's source of truth for architecture, stack, ideas, guardrails, tasks, and best practices.
> Every team member uses Claude Code with this file as context. Do NOT create separate design docs — update this file instead.

---

## 1. Project Overview

**What:** An AI-powered Hackathon Mentor Assistant — a conversational tool that guides teams through hackathon problem statements.

**How it works:**
```
[Team Input] → [Knowledge Base + LLM] → [Structured Mentor Output]
```

**Input:** Hackathon problem statement + team context (string, optional — name, skills, time left)
**Output:** Structured JSON guidance — problem summary, personas, features, tech stack, demo prep, action plan

**Key principle (from mentor):** 70% knowledge base, 30% LLM response. The assistant should be driven by curated templates/frameworks/patterns, with the LLM adapting and personalizing — NOT generating from scratch.

---

## 2. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | HTML/JS or React (Aaron's call) | Minimal input form — don't over-invest here |
| Backend | Flask (Python) | Fast to stand up, one route, no boilerplate |
| AI | Groq API — `qwen/qwen3.8-27b` | Fast inference (sub-second), JSON mode support, free tier sufficient for demo |
| Fallback | Rule-based Python dict lookup | Zero external dependency, guarantees demo never fails |
| Hosting | Localhost / ngrok for demo | No deployment complexity for a 90-min prototype |
| Data | None persisted — stateless request/response | No DB setup/debugging time cost |

**Explicitly NOT using:** No database, no auth, no frontend framework overhead (unless Aaron has boilerplate ready).

---

## 3. File Structure

```
tcs-ai-hackathon/
├── CLAUDE.md              ← THIS FILE (Claude Code context)
├── context/               ← PROJECT SOURCE OF TRUTH
│   ├── 01_ARCHITECTURE.md
│   ├── 02_TECH_STACK.md
│   ├── 03_NOVEL_IDEAS.md
│   ├── 04_GUARDRAILS.md
│   ├── 05_TASKLIST.md
│   └── 06_BEST_PRACTICES.md
├── app.py                 ← Flask server (Savio owns endpoint)
├── mentor_logic.py        ← AI mentor logic — Groq API + fallback (Savio)
├── index.html             ← Frontend chat UI / input form (Aaron)
├── style.css              ← Styles (Aaron)
├── knowledge/             ← Knowledge base files (Savio)
├── test_cases.json        ← Test cases (Aaron)
└── context.md             ← Original problem statement (reference only)
```

---

## 4. I/O Contract (LOCKED — Do Not Change Without Team Sync)

**Source of truth:** `context/02_TECH_STACK.md`

### Request: `POST /api/mentor`

```json
{
  "problem_statement": "string, required",
  "team_context": "string, optional",
  "phase": "string, optional — one of: understand|build|test|demo"
}
```

> NOTE: `team_context` is a **plain string** (e.g. "4 people, python + html skills, 90 min, beginners") — NOT a structured object.
> NOTE: `phase` tailors the guidance emphasis to where the team is in the hackathon (Feature D).

### Response: `POST /api/mentor` → 200 OK

```json
{
  "problem_summary": "string",
  "assumptions": ["string — things the AI inferred that the team did NOT state"],
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

**This exact JSON is what Aaron's UI sends and what Anurodh's renderer consumes. Nobody changes field names without updating `context/02_TECH_STACK.md` and telling the other two.**

### Error Response: 400/500

```json
{
  "error": "string — human-readable error message",
  "details": "string — optional technical detail"
}
```

---

## 5. System Prompt (Savio — Final Version)

The LLM must act as a **mentor coach**, NOT a solution builder.

```
You are a Hackathon Mentor AI. Your role is to GUIDE teams, not SOLVE their problems.

RULES:
1. NEVER generate complete code or full solutions.
2. ALWAYS ask clarifying questions before diving deep.
3. Use design thinking framework (Empathize → Define → Ideate → Prototype → Test).
4. Suggest features with priorities (P0=must-have, P1=should-have, P2=nice-to-have).
5. Recommend tech stack based on team skills and time constraints.
6. Keep outputs structured and actionable.
7. Focus on teaching the team HOW to think, not WHAT to build.
8. If the problem is vague, help them narrow scope — don't assume.
9. Always end with a clear "Decision → Reason → Next Action" block.
10. Be encouraging but honest about feasibility given their constraints.

OUTPUT FORMAT: Return valid JSON matching the schema provided.
```

**Hard enforcement:** If AI output contains large code blocks beyond trivial snippets, strip or flag them before rendering. This is a system property, not just a prompt instruction. (See `context/03_NOVEL_IDEAS.md` Tier 1 #1)

---

## 6. Knowledge Base (Savio)

`knowledge/` directory contains curated templates. The LLM uses these as grounding context — it picks relevant patterns and adapts them, rather than generating from nothing.

Key files:
- `design_thinking.json` — frameworks, prompts per step, persona templates
- `feature_patterns.json` — patterns by domain (education, food, campus, health)
- `tech_stack.json` — recommendations by constraint (beginner/intermediate × time)
- `presentation.json` — demo flow, jury pitch template, common jury questions
- `sample_problems.json` — synthetic problem statements for fallback matching

---

## 7. Fallback Logic (Savio)

**Fallback is mandatory, not optional.** Every API call path must degrade to rule-based fallback on: timeout, rate limit, malformed JSON, or network failure. The demo must never show a raw error or blank screen.

**Timeout:** Set explicit 5-8s timeout on Groq call — fail fast into fallback.

**Flow:**
1. Match problem statement keywords against `knowledge/sample_problems.json`
2. If match found → return pre-built structured output for that problem
3. If no match → return generic template with placeholder summary, default personas, default features, generic tech stack

**The caller never knows which path was used — schema is identical either way.**

---

## 8. Test Cases (Aaron)

Store in `test_cases.json`. 3-5 test cases covering normal, alternate, and edge cases.

Example cases:
1. **Normal:** Food wastage problem, beginner team, 90 min
2. **Alternate:** Parking problem, advanced team with ML skills
3. **Edge:** Vague problem ("Fix education"), minimal context

Expected output checks: problem_summary present, user_personas has 2+, feature_suggestions has 3+, tech_stack matches skill level, decision/reason/next_action all present.

---

## 9. API Endpoints

### `POST /api/mentor` — Main endpoint
- Accepts `{ problem_statement, team_context, phase }`
- `phase` is optional: `understand|build|test|demo` — tailors guidance emphasis
- Returns full structured guidance (see I/O Contract)
- Response now includes `assumptions` array (Feature A)
- Uses Groq API primarily, falls back to rule-based if API fails

### `POST /api/followup` — Follow-up questions (Feature B)
- Accepts `{ original_guidance, question, team_context }`
- `original_guidance` is the full JSON from `/api/mentor`
- Returns focused guidance: `{ answer, related_suggestions, next_steps, warning }`
- Has its own fallback — never fails

### `POST /api/validate` — Problem statement validator (Feature C)
- Accepts `{ problem_statement }`
- Returns quality score + feedback: `{ score, max_score, feedback[], improved_statement }`
- Rule-based scoring + optional LLM enhancement for improved statement
- Checks: Specificity, User Focus, Scope, Innovation Potential

### `GET /api/health` — Health check
```json
{ "status": "ok", "mode": "ai|rule_based", "timestamp": "..." }
```

### `GET /api/test-cases` — Load test cases
Returns test cases from `test_cases.json` for the testing phase.

---

## 10. Guardrails (Non-Negotiable)

From `context/04_GUARDRAILS.md`:

### Content
- Assistant guides, never fully solves — no complete code, no copy-paste architecture
- No real student data — only synthetic/public examples
- No confidential competition info
- No prior team solutions in fallback examples

### Technical
- Fallback is mandatory on every API path
- JSON schema is single source of truth — no silent field renames
- No secrets in code — `GROQ_API_KEY` via env var only
- Input sanitization: reject empty `problem_statement`, cap at 2000 chars
- Timeouts on API calls (5-8s)

### Process
- Freeze schema after 1:55 sync
- One person owns merge/integration authority during Phase 5 (Anurodh)
- Don't skip testing to save time

---

## 11. Demo Flow (5 Minutes)

```
[0:00 - 0:30]  PROBLEM   — "Teams struggle during hackathons. Here's our mentor assistant."
[0:30 - 1:00]  APPROACH  — "70% knowledge base, 30% LLM. Design thinking framework."
[1:00 - 3:00]  SOLUTION  — LIVE DEMO: Input problem → Get structured guidance
[3:00 - 3:30]  PROOF     — Run test cases, show pass/fail
[3:30 - 4:00]  LEARNING  — "What we learned, limitations, future scope"
[4:00 - 5:00]  Q&A       — Jury questions
```

**Demo script must be rehearsed.** Anurodh owns the script and timing.

---

## 12. Tasklist & Sync Points

From `context/05_TASKLIST.md`:

| Phase | Time | What | Owner |
|-------|------|------|-------|
| UNDERSTAND | 1:30-1:40 | Define User → Input → Output → Success | All (Aaron facilitates) |
| SAMPLE DATA | 1:40-1:55 | Draft test cases, lock JSON contract | Aaron + Savio |
| **SYNC** | **1:55** | **Confirm contract matches exactly** | **All** |
| BUILD LOGIC | 1:55-2:20 | System prompt, Groq call, fallback, input form, stub renderer | Savio + Aaron + Anurodh |
| **SYNC** | **2:20** | **Integration point — swap stubs for live** | **All** |
| OUTPUT VIEW | 2:20-2:40 | Live response rendering, styling, smoke test | Anurodh + All |
| TEST & DEMO | 2:40-3:00 | Run test cases, fix critical bugs, script demo | All |
| REHEARSAL | 2:50-3:00 | Full run-through | All |

---

## 13. Who Owns What

| File | Owner | Description |
|------|-------|-------------|
| `index.html` | Aaron | Chat UI / input form |
| `style.css` | Aaron | Styles |
| `test_cases.json` | Aaron | 3-5 test cases |
| `app.py` | Savio | Flask server endpoint |
| `mentor_logic.py` | Savio | Groq API + rule-based fallback |
| `knowledge/*.json` | Savio | Knowledge base files |
| Output renderer | Anurodh | Consumes JSON, renders structured cards |
| Demo script | Anurodh | 5-min demo flow |
| Known limitations doc | Anurodh | For jury Q&A |

---

## 14. Best Practices

From `context/06_BEST_PRACTICES.md`:

1. **Contract-first** — Lock JSON shape before anyone writes code
2. **Stub, don't wait** — Hardcode sample JSON, build against that, swap for live later
3. **One shared file** — `context/02_TECH_STACK.md` is THE contract
4. **Git: main branch only** — small frequent commits, no branches
5. **Parallel testing** — each person smoke-tests their own layer as they build
6. **Fail loud, fail fast** — no silent hangs, always fall into fallback
7. **Communication over docs** — 10-second "hey I changed X" beats any message
8. **Protect last 10 min** — nothing new after 2:50, rehearsal only
9. **One integration owner** — Anurodh has final call during Phase 5
10. **Know what to cut** — cut Tier 2/3 novel ideas if BUILD LOGIC runs long

---

## 15. Novel Ideas (Pick 1-2 If Time Allows)

From `context/03_NOVEL_IDEAS.md`:

**Build if time allows:**
1. Enforce "guide not solve" with post-processing code-block stripping
2. Effort vs. impact visual on feature suggestions (2x2 grid)
3. Confidence/assumption tagging on AI suggestions

**Mention verbally only:**
- Multi-session memory, mentor calibration, voice interaction

---

## 16. Environment Setup

```bash
pip install flask requests
export GROQ_API_KEY="your_key_here"
python app.py
# App runs at http://localhost:5000
```

Test the API:
```bash
curl -X POST http://localhost:5000/api/mentor \
  -H "Content-Type: application/json" \
  -d '{"problem_statement": "Reduce food wastage in college canteens"}'
```

---

## 17. Emergency Fallback

If everything breaks in the last 10 minutes:
1. Open `index.html` directly (no server needed for static demo)
2. Hardcode 1 example response in the HTML as a JavaScript object
3. Show the structured output for the food wastage problem
4. Explain the architecture verbally — jury cares about thinking, not just code

---

## 18. Decision Log

| Decision | Chosen | Reason |
|----------|--------|--------|
| Frontend | HTML/JS or React (Aaron's call) | Minimal form, don't over-invest |
| Backend | Flask (Python) | One route, no boilerplate |
| LLM | Groq `qwen/qwen3.8-27b` | Available on free tier, fast, JSON mode |
| Fallback | Rule-based dict lookup | Zero dependency, demo-proof |
| Database | None | Stateless, single-session demo |
| team_context | Plain string | Simple, flexible, no parsing needed |
| Assumptions (Feature A) | Tag AI inferences | Teaches teams to validate, strong jury point |
| Follow-up (Feature B) | Separate endpoint | Simulates real mentor conversation |
| Validator (Feature C) | Rule + LLM scoring | Catches vague problems before mentoring |
| Phase-aware (Feature D) | Prompt injection | Tailors guidance to hackathon phase |

---

> **Last updated:** Hackathon day — September 2026
> **Source of truth:** `context/` folder
> **Maintained by:** Aaron (UI), Savio (Logic), Anurodh (Integration/Demo)
