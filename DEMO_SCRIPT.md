# 🎤 5-Minute Demo Script — Hackathon Mentor AI Assistant

> **Owner:** Anurodh (Pitch Lead & Integration Owner)  
> **Total Timebox:** 5:00 Minutes (Strictly rehearsed)

---

## ⏱️ Pitch Timeline Overview

```
[0:00 - 0:30]  1. PROBLEM    — The 90-Minute Hackathon Paralysis
[0:30 - 1:00]  2. APPROACH   — 70% Knowledge Base + 30% LLM Architecture
[1:00 - 3:00]  3. LIVE DEMO  — End-to-End Pipeline & Jury-Mode View
[3:00 - 3:30]  4. PROOF      — Test Case Suite & Zero-Failure Fallback
[3:30 - 4:00]  5. LEARNING   — Guardrails & System Enforcements
[4:00 - 5:00]  6. JURY Q&A   — Defense & Roadmap
```

---

## 🗣️ Minute-by-Minute Verbal Script

### [0:00 - 0:30] 1. PROBLEM — "The Hackathon Paralysis"
- **Speaker:** Anurodh
- **Script:**
  > *"Good morning judges! Every hackathon team hits the same roadblock during the first 30 minutes: scope creep, choosing the wrong tech stack, or building features that don't solve the core user pain point. Generic AI chat tools like ChatGPT just give vague code blocks that break. Teams don't need code copy-pasted for them—they need structured guidance on **HOW** to think, prioritize, and pitch."*

---

### [0:30 - 1:00] 2. APPROACH — "70% Knowledge Base, 30% LLM"
- **Speaker:** Savio / Aaron
- **Script:**
  > *"To solve this, we architected the **Hackathon Mentor AI Assistant**. It operates on a key principle: 70% curated domain knowledge base combined with 30% LLM adaptation using Groq's fast sub-second inference. If the network drops or API rate-limits hit, our rule-based Python fallback ensures the system **never fails on stage**."*

---

### [1:00 - 3:00] 3. LIVE DEMO — "Live Output View & Decision Hero"
- **Speaker:** Anurodh (Navigating UI)
- **Script & Actions:**
  1. *Action:* Open UI (`http://localhost:5000` or `index.html`).
  2. *Action:* Click **TC-01 (Canteen Food Wastage)** from the Test Suite Runner and click **Get Mentor Guidance**.
  3. *Verbal:*
     > *"Notice our Output View. At the very top, we prominently highlight the **Decision → Reason → Next Action** hero banner. The mentor tells us instantly: 'Build the P0 pre-order form and manager summary dashboard first' because an end-to-end user flow scores higher than broken features."*
  4. *Action:* Scroll down to show **User Personas** and the **2x2 Effort vs Impact Matrix**.
  5. *Verbal:*
     > *"We don't just list features—we plot them on an Effort vs Impact matrix so teams get an instant decision tool. Notice how Quick Wins like the student input form are separated from High Effort notifications."*
  6. *Action:* Click **"🏆 Enable Jury-Mode (6-Part Pitch View)"**.
  7. *Verbal:*
     > *"With one click on 'Jury Mode', the output collapses into the exact 6-part pitch rubric: Problem, Approach, Solution, Output, Proof, and Learning!"*

---

### [3:00 - 3:30] 4. PROOF — "Automated Test Case Runner"
- **Speaker:** Anurodh
- **Script:**
  > *"We validated our pipeline across 5 diverse test cases—ranging from canteen food waste and smart parking to edge cases with vague inputs. Every test case passes strict JSON schema verification and provides actionable personas, checkpoints, and pitch tips."*

---

### [3:30 - 4:00] 5. LEARNING & SYSTEM GUARDRAILS
- **Speaker:** Anurodh
- **Script:**
  > *"Our primary technical takeaway: **The mentor guides, it never solves.** We enforced a system-level guardrail that automatically strips code blocks from the AI response. It guarantees the AI remains a coach rather than a solution builder. Thank you, and we're ready for your questions!"*

---

### [4:00 - 5:00] 6. JURY Q&A PREPARATION
*(Reference `KNOWN_LIMITATIONS.md` for answers to expected jury questions).*
