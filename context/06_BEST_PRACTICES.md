# Best Practices — Simultaneous Development (3 People, 90 Minutes)

## 1. Contract-first, not integration-last
Lock the JSON request/response shape (`TECH_STACK.md`) at the 1:55 sync **before** anyone writes the code that depends on it. This is the single highest-leverage practice for parallel work — it's what lets all three people build simultaneously without waiting on each other.

## 2. Stub, don't wait
Anurodh should **not** wait for Savio's live API to be working before building the renderer. Hardcode a sample JSON matching the locked schema and build against that. Swap in the real backend call only once both sides are ready. Same applies to Aaron — the input form can POST to a fake/mocked endpoint first, then point at the real one.

## 3. One shared file, not three private ones
Keep `TECH_STACK.md` (the contract) as the single source of truth all three people reference. If the schema needs to change mid-build, **whoever changes it must say so out loud immediately** — a silent field rename breaks someone else's code with no warning.

## 4. Git workflow (if using git)
- One shared repo, `main` branch only — no time for a branching strategy in 90 minutes
- Small, frequent commits (every 5-10 min) so integration issues surface early, not all at once at 2:40
- If a merge conflict happens, the person who owns that file's phase resolves it (see ownership map in `TASKLIST.md`)
- Alternative if git feels slow: shared folder/live-share (VS Code Live Share, Replit) — pick whichever the team is already fast with, don't learn new tooling under time pressure

## 5. Parallel work needs parallel testing
Don't save all testing for Phase 5. Each owner smoke-tests their own layer as they build:
- Aaron: does the form actually send a valid POST?
- Savio: does `get_mentor_guidance()` return valid JSON for at least 2 different inputs?
- Anurodh: does the renderer handle a missing/empty field gracefully (in case the LLM skips one)?

## 6. Fail loud, fail fast, fail into the fallback
Any component that depends on an external call (Groq API, network) must have a fast, visible failure path — not a silent hang. This is why `mentor_logic.py` has a timeout + fallback baked in. Don't build features that can hang the whole demo waiting on a slow response.

## 7. Communication over documentation
With 90 minutes, don't write status updates — just talk. A 10-second "hey, I changed X" beats a Slack message someone reads 5 minutes later. Sit physically/virtually close enough that a question gets answered in seconds, not minutes.

## 8. Protect the last 10 minutes
Nothing new gets built after 2:50. That window is rehearsal only. A working demo you've practiced once beats a slightly-better demo you're seeing for the first time on stage.

## 9. Assign one integration owner
Per `TASKLIST.md`, Anurodh holds final call during Phase 5 merges/conflicts. This isn't about hierarchy — it's about avoiding a 3-way debate eating minutes you don't have during the highest-pressure phase.

## 10. Know what to cut
If BUILD LOGIC runs long, cut Tier 2/3 ideas from `NOVEL_IDEAS.md` first. The core end-to-end path (input → mentor logic → output) is non-negotiable; polish and novel additions are not.
