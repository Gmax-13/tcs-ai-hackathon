# Novel Ideas — Differentiation for Jury

Most teams building an "AI mentor" will just wrap a chatbot around an LLM call. These are the ideas that separate a working prototype from a memorable one. **Pick 1-2 that fit the remaining time — don't chase all of them.**

## Tier 1 — High impact, low build cost (do these if time allows)

1. **"Guide, not solve" is enforced, not just prompted**
   Add a lightweight check: if the AI output contains actual code blocks or a complete implementation, flag/strip it before rendering. This proves the constraint is a system property, not a hope. Strong jury talking point — "we didn't just ask nicely, we enforced it."

2. **Confidence/assumption tagging**
   Every suggestion the AI makes gets tagged as `[assumption]` if it's inferring something not stated by the team (e.g., assuming a canteen has digital order records). Teaches the team what they still need to validate — ties directly into the "design thinking" goal of the problem statement.

3. **Effort vs. impact visual on feature suggestions**
   You already have `effort: low|medium|high` in the schema — plot suggested features on a simple 2x2 (effort vs. impact) instead of a flat list. Turns a text list into an instant decision tool. Cheap to build (even ASCII/CSS grid), high visual payoff in the demo.

## Tier 2 — Medium effort, strong narrative

4. **Mentor asks *back* before answering**
   Instead of one-shot input → output, the first response could include 1-2 clarifying questions the *team* must answer before getting full guidance — mirroring how a real mentor operates ("what have you tried already?"). Only do this if the 25-min build window has slack; it adds a conversation loop.

5. **Jury-mode summary button**
   A single button that collapses the full mentor output into the exact 6-part demo structure the handbook specifies (Problem → Approach → Solution → Output → Proof → Learning). Directly demos the handbook's own judging criteria back to the jury — subtle but effective.

## Tier 3 — Mention as future work only (don't build)

6. Multi-session memory across a full hackathon (persona/team profile evolves over hours)
7. Mentor calibration based on team skill level (beginner vs. advanced guidance depth)
8. Voice-based mentor interaction (ties to Savio's existing Voice AI pipeline experience — good "future roadmap" line in the pitch, zero build cost now)

## Recommendation

Build **#1 and #3** if BUILD LOGIC finishes early — both are near-zero marginal cost since the schema already has the underlying data (`effort` field, and the guardrail is a regex/keyword check on the LLM output). Mention #6-8 verbally during the demo's "Learning" section to show forward thinking without spending build time.
