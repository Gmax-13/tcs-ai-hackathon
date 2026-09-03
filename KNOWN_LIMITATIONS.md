# 🛡️ Known Limitations & Jury Q&A Cheat Sheet

> **Owner:** Anurodh (Integration & Defense Lead)  
> Prepared for jury Q&A during Phase 5 demo.

---

## ❓ Anticipated Jury Questions & Battle-Tested Answers

### Q1: "What happens if Groq API goes down or rate-limits during your demo?"
- **Answer:**
  > *"We built a multi-layered rule-based fallback system in `mentor_logic.py`. If the Groq API fails, times out after 8 seconds, or returns malformed data, the backend automatically drops down to pre-configured domain templates from `knowledge/sample_problems.json`. The frontend renderer consumes the exact same JSON schema regardless of the source, so the user and jury experience zero disruption."*

---

### Q2: "How do you prevent the AI from just giving students complete copy-paste code?"
- **Answer:**
  > *"We enforce 'guide, not solve' through two mechanisms:  
  > 1. **System Prompt Enforcement:** Rules strictly instruct the model to teach frameworks rather than output code.  
  > 2. **Hard Post-Processing Guardrail (`_strip_code_blocks`):** Any markdown code block exceeding 3 lines is programmatically stripped and replaced with a mentor reminder: `[Code block removed — the mentor guides, not solves]`. This is a system-level guarantee."*

---

### Q3: "Is student data or prior hackathon solution data stored?"
- **Answer:**
  > *"No. The architecture is 100% stateless with zero database or session storage. Inputs are processed on-the-fly and returned in a single HTTP request cycle to ensure absolute data privacy and zero persistence overhead."*

---

### Q4: "Why 70% Knowledge Base and 30% LLM?"
- **Answer:**
  > *"Unconstrained LLMs tend to hallucinate unrealistic tech stacks or over-complicate 90-minute hackathon scopes. Grounding the prompt with curated Design Thinking steps (`design_thinking.json`), domain patterns (`feature_patterns.json`), and tech advice (`tech_stack.json`) keeps the AI focused on practical, time-constrained advice."*

---

### Q5: "What would you build next with more time?"
- **Answer:**
  > *"Our future roadmap includes:  
  > 1. **Multi-Session Progress Memory:** Tracking team progress across the full hackathon timeline (Ideation → Build → Demo).  
  > 2. **Mentor Calibration:** Adjusting guidance depth based on self-reported team skill levels (beginner vs. advanced).  
  > 3. **Voice Interaction Loop:** Enabling natural voice discussions using fast speech-to-text pipeline."*

---

## ⚠️ Current Scope Boundaries & Known Limitations

1. **Stateless Nature:** Conversations are single-turn (Input statement → Mentor guidance). No multi-turn chat history in the current prototype.
2. **Preset Knowledge Domains:** Specialized domain knowledge works best for featured domains (Campus food, Parking, Education, Health). General problems default to generic Design Thinking guidance.
3. **Execution Verification:** The mentor suggests prototype priorities and checkpoints, but relies on human confirmation that the code actually builds.
