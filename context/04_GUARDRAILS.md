# Guardrails — Hackathon Mentor AI Assistant

## Scope Guardrails (from the problem statement — non-negotiable)

- **The assistant guides, never fully solves.** It must not output complete working code, a full architecture ready to copy-paste, or a finished solution. Enforced via:
  - System prompt instruction (soft enforcement)
  - Post-processing check: if response contains large code blocks (```...```) beyond trivial snippets, strip or flag them (hard enforcement — see Novel Ideas #1)
- **No real student performance data.** Only synthetic/public example problem statements and templates go into prompts or test cases.
- **No confidential competition information.** Don't hardcode real TCS/FCRIT evaluation criteria if they were shared privately — use publicly available or invented rubrics.
- **No prior team solutions.** Fallback examples must be original/synthetic, not scraped from past hackathon submissions.

## Technical Guardrails

- **Fallback is mandatory, not optional.** Every API call path must degrade to the rule-based fallback on: timeout, rate limit, malformed JSON, or network failure. The demo must never show a raw error or blank screen.
- **JSON schema is the single source of truth.** No field renamed or added without updating `TECH_STACK.md` and notifying both other team members — a silent schema drift breaks the renderer or the input form without warning.
- **No secrets in code.** `GROQ_API_KEY` via environment variable only — never hardcoded, never committed. Add `.env` to `.gitignore` immediately if using git.
- **Input sanitization (minimal but present):** reject empty `problem_statement`; cap length (e.g., 2000 chars) to avoid prompt-injection-style abuse or runaway token costs during the demo.
- **Timeouts on the API call.** Set an explicit timeout (5-8s) on the Groq call so a hung request doesn't stall the whole demo — fail fast into fallback instead.

## Content Guardrails (LLM output)

- Model must not fabricate specific statistics, named tools with false claims, or invented "research" — guidance should stay at the level of practical suggestions, not authoritative fact claims.
- Personas and examples must stay clearly fictional/illustrative, not implying real people or real institutional data.
- If the team's `problem_statement` input is empty, nonsensical, or off-topic (not a hackathon-style problem), the assistant should ask for clarification rather than inventing a problem to mentor on.

## Process Guardrails (for the team, during build)

- **Don't skip testing to save time.** The handbook's own rule: "we are judging whether your solution works." A flashy but broken demo scores worse than a plain one that runs cleanly end-to-end.
- **Freeze the schema after the 1:55 sync.** Changing the contract mid-build (2:20+) risks breaking two people's work simultaneously for the sake of one feature idea.
- **One person owns merge/integration authority** during TEST & DEMO (recommend Anurodh, since they own that phase) to avoid last-minute conflicting edits.
