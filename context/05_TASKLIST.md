# Master Tasklist — Hackathon Mentor AI Assistant

Timeboxed to the 90-minute handbook. Each row: **who / what / by when / depends on**.

## Phase 1 — UNDERSTAND (1:30–1:40)

| Task | Owner | Depends on |
|---|---|---|
| Define User → Input → Output → Success (whiteboard, 10 min, all three present) | Aaron (facilitates) | — |
| Confirm final problem statement scope (P8 as-is, or a specific example domain like canteen wastage) | All | — |

## Phase 2 — SAMPLE DATA (1:40–1:55)

| Task | Owner | Depends on |
|---|---|---|
| Draft 3-5 test cases (normal, alternate, edge) with expected output | Aaron | Phase 1 |
| Lock JSON request/response contract (`TECH_STACK.md`) | Savio + Aaron | Phase 1 |
| Start system prompt draft | Savio | — (parallel) |

**Checkpoint 1:55 — hard sync, 2 min max:** confirm contract matches exactly between input UI and logic layer.

## Phase 3 — BUILD LOGIC (1:55–2:20)

| Task | Owner | Depends on |
|---|---|---|
| Finalize system prompt + JSON schema enforcement | Savio | Contract locked |
| Wire Groq API call (`mentor_logic.py`) | Savio | — |
| Build rule-based fallback (canned + generic) | Savio | Test cases from Aaron |
| Build input form, wire to backend endpoint | Aaron | Contract locked |
| Stub renderer with hardcoded sample JSON (don't wait for live API) | Anurodh | `TECH_STACK.md` schema |

## Phase 4 — OUTPUT VIEW (2:20–2:40)

| Task | Owner | Depends on |
|---|---|---|
| Swap stubbed JSON for live backend response | Anurodh | Savio's logic working |
| Render Decision → Reason → Next Action prominently | Anurodh | — |
| Style sections (personas, features, checklist) | Anurodh | — |
| Smoke test: submit real form → see real output end-to-end | All | Full pipeline connected |

**Checkpoint 2:20 — integration point.** If Savio's logic isn't ready, Anurodh keeps testing against the stub while Savio finishes — no one blocks idle.

## Phase 5 — TEST & DEMO (2:40–3:00)

| Task | Owner | Depends on |
|---|---|---|
| Run all 3-5 test cases against live system, log pass/fail | Anurodh | Full pipeline |
| Fix critical/blocking bugs only | Whoever owns the broken layer | Bug identified |
| Note non-critical limitations for jury Q&A | Anurodh | — |
| Script 5-min demo (Problem → Approach → Solution → Output → Proof → Learning) | Anurodh (draft), All (review) | Working demo |
| Rehearse once, full run-through | All | Script ready |

## Standing Rules
- No one works in isolation past 1:55 without checking the contract file first.
- If blocked, ping the owner immediately — don't silently work around a broken dependency.
- Anurodh has final integration authority during Phase 5 — if there's a merge conflict or last-minute change disagreement, their call wins so the demo stays stable.
