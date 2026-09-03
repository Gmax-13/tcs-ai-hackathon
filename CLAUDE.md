# CLAUDE.md — TCS Tech Day Hackathon: AI Mentor Assistant

> **This file is the single source of truth.** Every team member uses Claude Code with this file as context. Do NOT create separate design docs — update this file instead.

---

## 1. Project Overview

**What:** An AI-powered Hackathon Mentor Assistant — a conversational tool that guides teams through hackathon problem statements.

**How it works:**
```
[Team Input] → [Knowledge Base + LLM] → [Structured Mentor Output]
```

**Input:** Hackathon problem statement + team context (team size, skills, time available)
**Output:** Structured guidance — problem summary, personas, features, tech stack, demo prep, action plan

**Key principle (from mentor):** 70% knowledge base, 30% LLM response. The assistant should be driven by curated templates/frameworks/patterns, with the LLM adapting and personalizing — NOT generating from scratch.

---

## 2. Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | **HTML + CSS + Vanilla JS** (single `index.html`) | Fast, no build step, demo-ready |
| Backend/Logic | **Python Flask** (`app.py`) | Simple server, easy LLM integration |
| LLM Provider | **Groq API** (Llama 3) — primary | Free tier, fast inference |
| Fallback | **Rule-based** hardcoded responses | Works offline, no API dependency |
| Knowledge Base | **JSON files** (`knowledge/`) | Structured templates, frameworks, patterns |
| Hosting | **Local** (`localhost:5000`) | Demo on single laptop |

**Do NOT use:** React, Node.js, Docker, databases, auth, or anything requiring npm/pip install beyond flask + requests.

---

## 3. File Structure

```
tcs-ai-hackathon/
├── CLAUDE.md              ← THIS FILE (project truth)
├── app.py                 ← Flask server + LLM logic (Savio)
├── index.html             ← Frontend chat UI (Aaron)
├── style.css              ← Styles (Aaron)
├── knowledge/             ← Knowledge base files (Savio)
│   ├── design_thinking.json
│   ├── feature_patterns.json
│   ├── tech_stack.json
│   ├── presentation.json
│   └── sample_problems.json
├── test_cases.json        ← Test cases (Aaron)
├── context.md             ← Original problem statement (reference only)
├── aaron_tasks.md         ← Aaron's task list
├── anurodh_tasks.md       ← Anurodh's task list
└── savio_tasks.md         ← Savio's task list
```

---

## 4. I/O Contract (LOCKED — Do Not Change Without Team Sync)

This is the API contract between frontend and backend. **Aaron and Savio must agree on this before building.**

### Request: `POST /api/mentor`

```json
{
  "problem_statement": "string — the hackathon problem (required)",
  "team_context": {
    "team_size": "number (2-5)",
    "skills": ["string — e.g. 'python', 'react', 'ml']",
    "time_available": "string — e.g. '90 minutes'",
    "experience_level": "string — 'beginner' | 'intermediate' | 'advanced'"
  }
}
```

### Response: `POST /api/mentor` → 200 OK

```json
{
  "problem_summary": "string — plain-language summary of the problem",
  "key_questions": ["string — 3-5 clarifying questions"],
  "user_personas": [
    {
      "name": "string",
      "role": "string",
      "needs": ["string"],
      "pain_points": ["string"]
    }
  ],
  "design_thinking": {
    "empathize": "string — who are the users and what do they feel?",
    "define": "string — what is the core problem in one sentence?",
    "ideate": "string — 2-3 creative approaches",
    "prototype": "string — what to build first (smallest testable thing)",
    "test": "string — how to validate with users"
  },
  "feature_suggestions": [
    {
      "name": "string",
      "priority": "P0 | P1 | P2",
      "effort": "low | medium | high",
      "description": "string"
    }
  ],
  "tech_stack": [
    {
      "layer": "string — e.g. 'frontend', 'backend', 'database', 'ai/ml'",
      "recommendation": "string",
      "reason": "string"
    }
  ],
  "prototype_priorities": [
    "string — ordered list: build THIS first, then THIS"
  ],
  "validation_checkpoints": [
    "string — what to verify before demo"
  ],
  "demo_prep": {
    "narrative_arc": ["string — 5-slide outline"],
    "jury_pitch_checklist": ["string — items to cover in 5-min demo"],
    "time_allocator": {
      "problem_overview": "30 sec",
      "approach_explanation": "1 min",
      "live_demo": "2 min",
      "results_and_learning": "1 min",
      "q_and_a_buffer": "30 sec"
    }
  },
  "action_plan": {
    "immediate_next_steps": ["string — first 3 things to do RIGHT NOW"],
    "assumptions": ["string — what we're assuming to be true"],
    "risks": ["string — what could go wrong"],
    "innovation_prompts": ["string — creative nudges to think beyond basics"]
  },
  "decision_reason_next": {
    "decision": "string — the recommended approach",
    "reason": "string — why this approach",
    "next_action": "string — single most important next step"
  },
  "metadata": {
    "mode": "ai | rule_based_fallback",
    "model": "string — which model was used",
    "timestamp": "ISO 8601"
  }
}
```

### Error Response: `POST /api/mentor` → 400/500

```json
{
  "error": "string — human-readable error message",
  "details": "string — optional technical detail"
}
```

---

## 5. System Prompt (Savio — Final Version)

The LLM must act as a **mentor coach**, NOT a solution builder. Core rules:

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

---

## 6. Knowledge Base Structure (Savio)

Each JSON file in `knowledge/` contains curated templates. The LLM uses these as grounding context — it picks relevant patterns and adapts them, rather than generating from nothing.

### `knowledge/design_thinking.json`
```json
{
  "frameworks": [
    {
      "name": "Design Thinking",
      "steps": ["Empathize", "Define", "Ideate", "Prototype", "Test"],
      "prompts_per_step": {
        "Empathize": ["Who experiences this problem most?", "What are their daily frustrations?"],
        "Define": ["Can you state the problem in one sentence?", "Who is the primary user?"],
        "Ideate": ["What are 3 different approaches?", "What would the ideal solution look like?"],
        "Prototype": ["What is the smallest thing you can build to test this?", "What feature gives 80% of value with 20% effort?"],
        "Test": ["How will you know if this works?", "Who will you test with first?"]
      }
    }
  ],
  "persona_templates": [...],
  "problem_reframing_examples": [...]
}
```

### `knowledge/feature_patterns.json`
```json
{
  "patterns_by_domain": {
    "education": ["attendance tracking", "peer learning", "progress dashboards", "automated grading"],
    "food_wastage": ["demand prediction", "surplus donation matching", "expiry tracking", "portion optimization"],
    "campus_management": ["parking optimization", "room booking", "event scheduling", "resource sharing"],
    "health": ["symptom checker", "appointment scheduling", "health tracking", "medication reminders"]
  },
  "priority_heuristics": {
    "P0": "Must work for demo — core value proposition",
    "P1": "Should work — improves experience significantly",
    "P2": "Nice to have — differentiator if time permits"
  }
}
```

### `knowledge/tech_stack.json`
```json
{
  "recommendations_by_constraint": {
    "beginner_90min": {
      "frontend": "HTML/CSS/JS",
      "backend": "Python Flask",
      "ai": "Groq API (free, fast)",
      "database": "JSON file or none",
      "why": "Minimal setup, fast to build, easy to demo"
    },
    "intermediate_90min": {
      "frontend": "React or Vue",
      "backend": "FastAPI or Flask",
      "ai": "Groq/Claude API",
      "database": "SQLite",
      "why": "More structured, still fast"
    }
  },
  "avoid_in_90min": ["Docker", "Kubernetes", "Microservices", "Complex auth", "Custom ML training"]
}
```

### `knowledge/presentation.json`
```json
{
  "demo_flow": ["Problem", "Approach", "Solution", "Output", "Proof", "Learning"],
  "jury_pitch_template": {
    "opening": "In 1 sentence, what problem does this solve?",
    "approach": "How did you think about it? (design thinking)",
    "demo": "Show the working prototype",
    "proof": "Show test cases passing",
    "closing": "What did you learn? What would you do differently?"
  },
  "common_jury_questions": [
    "How is this different from existing solutions?",
    "What are the limitations?",
    "How would you scale this?",
    "What was the hardest part?",
    "How did you validate user needs?"
  ]
}
```

### `knowledge/sample_problems.json`
```json
{
  "problems": [
    {
      "id": "food_wastage_001",
      "title": "Reduce Food Wastage in College Canteen",
      "description": "College canteens waste 20-40% of prepared food daily. Build a solution to predict demand and reduce waste.",
      "domains": ["food", "sustainability", "education"],
      "sample_output_reference": "..."
    }
  ]
}
```

---

## 7. Test Cases (Aaron)

Store in `test_cases.json`:

```json
{
  "test_cases": [
    {
      "id": "TC01",
      "type": "normal",
      "name": "Food Wastage — Standard",
      "input": {
        "problem_statement": "Reduce food wastage in college canteens. Currently 30% of prepared food is thrown away daily.",
        "team_context": {
          "team_size": 4,
          "skills": ["python", "html", "css"],
          "time_available": "90 minutes",
          "experience_level": "beginner"
        }
      },
      "expected_output_checks": [
        "problem_summary is present and < 100 words",
        "user_personas has at least 2 personas",
        "feature_suggestions has at least 3 features",
        "tech_stack recommendations match beginner skill level",
        "demo_prep.narrative_arc has 5 items",
        "decision_reason_next has all 3 fields"
      ]
    },
    {
      "id": "TC02",
      "type": "alternate",
      "name": "Parking Problem — Advanced Team",
      "input": {
        "problem_statement": "Campus parking is chaotic. Students waste 15 minutes daily finding parking. Design a smart parking solution.",
        "team_context": {
          "team_size": 3,
          "skills": ["react", "node", "ml", "python"],
          "time_available": "90 minutes",
          "experience_level": "advanced"
        }
      },
      "expected_output_checks": [
        "tech_stack includes ML-related recommendation",
        "feature_suggestions include real-time/sensor features",
        "prototype_priorities are ordered and realistic for 90 min"
      ]
    },
    {
      "id": "TC03",
      "type": "edge",
      "name": "Vague Problem — Minimal Context",
      "input": {
        "problem_statement": "Fix education",
        "team_context": {
          "team_size": 2,
          "skills": [],
          "time_available": "90 minutes",
          "experience_level": "beginner"
        }
      },
      "expected_output_checks": [
        "key_questions asks for clarification on scope",
        "problem_summary acknowledges ambiguity",
        "does NOT generate a full solution for an impossibly broad problem",
        "action_plan.immediate_next_steps includes scoping/narrowing"
      ]
    }
  ]
}
```

---

## 8. API Endpoints

### `POST /api/mentor` — Main endpoint
- Accepts problem statement + team context
- Returns full structured guidance (see I/O Contract above)
- Uses Groq API primarily, falls back to rule-based if API fails

### `GET /api/health` — Health check
```json
{ "status": "ok", "mode": "ai|rule_based", "timestamp": "..." }
```

### `GET /api/test-cases` — Load test cases
Returns the test cases from `test_cases.json` for the testing phase.

---

## 9. Fallback Logic (Savio)

When Groq API is unavailable (rate limit, network, etc.), use rule-based responses:

1. **Match problem statement keywords** against `knowledge/sample_problems.json`
2. **If match found** → return the pre-built structured output for that problem
3. **If no match** → return a generic template with:
   - Placeholder problem summary (filled with input text)
   - Default personas (Student, Canteen Staff, Admin)
   - Default feature patterns from the matched domain
   - Generic tech stack for beginner teams
   - Standard demo flow template

The fallback must return **valid JSON matching the same schema** as the AI response.

---

## 10. Rules & Constraints

### DO:
- Keep everything in a single Flask app + single HTML page
- Use the I/O contract exactly as specified — no field name changes without team sync
- Store all knowledge base files in `knowledge/` directory
- Test with the 3 test cases before demo
- Commit working code to `main` — no branches needed for a 1-hour sprint
- Use `curl` or the frontend to test endpoints

### DON'T:
- Install heavy dependencies (no TensorFlow, PyTorch, databases, Docker)
- Build user auth, databases, or complex state management
- Use external APIs beyond Groq (no OpenAI, no paid services)
- Create more than 1 HTML file — single-page app only
- Change the JSON output schema without notifying the team

### Data Rules:
- ALL data is synthetic — no real student data
- Use publicly available examples only
- Canteen food wastage is the primary example problem

---

## 11. Demo Flow (5 Minutes)

```
[0:00 - 0:30]  PROBLEM   — "Teams struggle during hackathons. Here's our mentor assistant."
[0:30 - 1:00]  APPROACH  — "70% knowledge base, 30% LLM. Design thinking framework."
[1:00 - 3:00]  SOLUTION  — LIVE DEMO: Input problem → Get structured guidance
[3:00 - 3:30]  PROOF     — Run test cases, show pass/fail
[3:30 - 4:00]  LEARNING  — "What we learned, limitations, future scope"
[4:00 - 5:00]  Q&A       — Jury questions (see knowledge/presentation.json)
```

**Demo script must be rehearsed.** Anurodh owns the script and timing.

---

## 12. Sync Points

| Time | Who | What |
|------|-----|------|
| **1:55** | Aaron ↔ Savio | Lock I/O contract. Confirm field names match. |
| **2:20** | Savio → Anurodh | Hand off working API. Anurodh starts rendering. |
| **2:40** | All | Testing complete. Demo script locked. |
| **2:50** | All | Final rehearsal. |

---

## 13. Quick Reference: Who Owns What

| File | Owner | Description |
|------|-------|-------------|
| `index.html` | Aaron | Chat UI / input form |
| `style.css` | Aaron | Styles |
| `test_cases.json` | Aaron | 3 test cases |
| `app.py` | Savio | Flask server + LLM logic |
| `knowledge/*.json` | Savio | Knowledge base files |
| `knowledge/` directory | Savio | All knowledge base data |
| Demo script | Anurodh | 5-min demo flow |
| Known limitations doc | Anurodh | For jury Q&A |

---

## 14. Environment Setup

```bash
# Install dependencies (already done or 1 command)
pip install flask requests

# Run the app
python app.py

# App runs at http://localhost:5000

# Test the API directly
curl -X POST http://localhost:5000/api/mentor \
  -H "Content-Type: application/json" \
  -d '{"problem_statement": "Reduce food wastage in college canteens", "team_context": {"team_size": 4, "skills": ["python", "html"], "time_available": "90 minutes", "experience_level": "beginner"}}'
```

---

## 15. Decision Log

| Decision | Chosen | Reason |
|----------|--------|--------|
| Frontend | Vanilla HTML/CSS/JS | No build step, fastest to demo |
| Backend | Python Flask | Simple, everyone knows it |
| LLM | Groq (Llama 3) | Free, fast, no API key hassle |
| Fallback | Rule-based JSON | Works offline, demo-proof |
| Database | None (JSON files) | Not needed for prototype |
| Single page | Yes | Simplicity > features |

---

## 16. Git Workflow

- Work on `main` branch — no PRs, no branches, this is a 1-hour sprint
- Commit often with clear messages: `[Aaron] Added test cases`, `[Savio] Implemented fallback logic`
- Pull before pushing if someone else pushed: `git pull origin main`
- If merge conflict, talk to each other — don't fight git

---

## 17. Emergency Fallback

If everything breaks in the last 10 minutes:
1. Open `index.html` directly (no server needed for static demo)
2. Hardcode 1 example response in the HTML as a JavaScript object
3. Show the structured output for the food wastage problem
4. Explain the architecture verbally — jury cares about thinking, not just code

---

> **Last updated:** Hackathon day — September 2026
> **Maintained by:** Aaron (UI), Savio (Logic), Anurodh (Integration/Demo)
