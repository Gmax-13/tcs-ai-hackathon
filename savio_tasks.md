# Savio — AI/Prompt Logic Lead

**Role:** Owns BUILD LOGIC (1:55–2:20) + logic side of OUTPUT VIEW (2:20–2:40)

## Tasks

- [ ] Design system prompt for the mentor persona — must **guide, not solve** (coach toward answers, never generate the full solution)
- [ ] Define output schema (JSON or structured markdown):
  - Problem summary (plain language)
  - Key clarifying questions
  - User personas
  - Design thinking guidance
  - Feature suggestions
  - Tech stack recommendations
  - Prototype priorities
  - Validation checkpoints
  - Demo prep / jury pitch checklist
- [ ] Wire up LLM API call (Groq/Claude — reuse existing pipeline patterns)
- [ ] Implement "Decision → Reason → Next Action" logic for OUTPUT VIEW handoff
- [ ] Build a rule-based fallback for 1–2 canned problem statements (in case of API failure/rate limit)
- [ ] Sync with Aaron at 1:55 to lock input/output contract before building
- [ ] Hand off working output format to Anurodh by 2:20

## Constraints
- No real student data — synthetic/public examples only
- Must run end-to-end, not just look good in isolation
- Keep it simple enough to explain in under a minute during the demo

## Checkpoint
**1:55** — Confirm I/O contract with Aaron
**2:20** — Logic must be functional and handed off to Anurodh
