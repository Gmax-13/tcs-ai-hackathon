"""
mentor_logic.py — AI Mentor Logic (Savio)

Core module: Groq API call with JSON mode + rule-based fallback.
The caller (app.py) never knows which path was used — the schema is
identical either way.
"""

import os
import json
import re
import time
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "qwen/qwen3.8-27b"
GROQ_TIMEOUT = 8  # seconds — fail fast into fallback
MAX_INPUT_LENGTH = 2000

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge")

# ---------------------------------------------------------------------------
# System prompt — enforces "guide, not solve"
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a Hackathon Mentor AI. Your role is to GUIDE teams, not SOLVE their problems.

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
11. Tag your ASSUMPTIONS: if you infer something the team didn't explicitly state, add it to the "assumptions" array. This teaches teams what they still need to validate.

OUTPUT FORMAT: You MUST return valid JSON matching the exact schema below. No markdown, no explanation outside JSON.

{
  "problem_summary": "string",
  "assumptions": ["string — things you inferred that the team did NOT explicitly state"],
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
}"""

# Phase-specific prompt additions (Feature D)
PHASE_PROMPTS = {
    "understand": "The team is in the UNDERSTAND phase. Focus heavily on empathy, user identification, problem scoping, and key questions. De-emphasize tech stack and demo tips.",
    "build": "The team is in the BUILD phase. Focus on tech stack choices, feature prioritization, prototype strategy, and architecture decisions. Keep design thinking brief.",
    "test": "The team is in the TEST phase. Focus on validation checkpoints, edge cases, bug priorities, and what to cut. De-emphasize ideation.",
    "demo": "The team is in the DEMO phase. Focus heavily on demo_prep_tips, presentation flow, jury Q&A prep, and the Decision/Reason/Next Action narrative. Keep tech details minimal.",
}

FOLLOWUP_SYSTEM_PROMPT = """You are a Hackathon Mentor AI providing follow-up guidance. The team already received initial mentoring and has a specific question.

RULES:
1. NEVER generate complete code or full solutions.
2. Be focused and concise — answer the specific question asked.
3. Reference the original guidance context when relevant.
4. Provide actionable next steps.

OUTPUT FORMAT: Return valid JSON matching this schema. No markdown wrapping.
{
  "answer": "string — focused guidance answering the question",
  "related_suggestions": ["string", "string"],
  "next_steps": ["string", "string"],
  "warning": "string or null — only if the question conflicts with a guardrail"
}
"""

VALIDATOR_SYSTEM_PROMPT = """You are a Hackathon Problem Statement Analyzer. Evaluate the quality of a problem statement for a hackathon team.

Score each category 1-3 and provide brief feedback. Return valid JSON matching this schema. No markdown wrapping.
{
  "score": "number 1-10 overall",
  "max_score": 10,
  "feedback": [
    { "category": "string", "score": "number 1-3", "status": "good|needs_work|warning", "note": "string" }
  ],
  "improved_statement": "string — a refined version of their problem statement"
}

Categories to evaluate:
- Specificity: Is the problem clearly defined or too vague?
- User Focus: Is the target user identified?
- Scope: Is it achievable in a hackathon timeframe?
- Innovation Potential: Does it allow for creative solutions?
"""

# ---------------------------------------------------------------------------
# Knowledge base loader
# ---------------------------------------------------------------------------
_knowledge_cache: dict = {}


def _load_knowledge(filename: str) -> dict:
    """Load a knowledge base JSON file, with caching."""
    if filename in _knowledge_cache:
        return _knowledge_cache[filename]
    filepath = os.path.join(KNOWLEDGE_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        _knowledge_cache[filename] = data
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning("Could not load knowledge file %s: %s", filename, e)
        return {}


def _build_knowledge_context(problem_statement: str) -> str:
    """Build relevant knowledge context to inject into the LLM prompt.

    Matches the problem statement keywords against feature_patterns domains
    and includes relevant design thinking + tech stack guidance.
    """
    context_parts = []

    # 1. Design thinking framework (always included)
    dt = _load_knowledge("design_thinking.json")
    if dt:
        steps = dt.get("framework", {}).get("steps", [])
        step_names = [s["step"] for s in steps]
        context_parts.append(
            f"Use the Design Thinking framework: {' → '.join(step_names)}."
        )
        # Include persona templates
        templates = dt.get("persona_templates", [])
        if templates:
            roles = [t["role"] for t in templates]
            context_parts.append(
                f"Consider these persona roles: {', '.join(roles)}."
            )

    # 2. Feature patterns — find matching domain
    fp = _load_knowledge("feature_patterns.json")
    if fp:
        domains = fp.get("domains", {})
        problem_lower = problem_statement.lower()
        for domain_key, domain_data in domains.items():
            keywords = domain_data.get("keywords", [])
            if any(kw in problem_lower for kw in keywords):
                label = domain_data.get("label", domain_key)
                features = domain_data.get("features", [])
                feature_names = [f["feature"] for f in features[:4]]
                context_parts.append(
                    f"This problem relates to '{label}'. "
                    f"Relevant feature patterns: {', '.join(feature_names)}."
                )
                break  # Use first matching domain

    # 3. Tech stack guidance (always included)
    ts = _load_knowledge("tech_stack.json")
    if ts:
        advice = ts.get("general_advice", [])
        if advice:
            context_parts.append(
                "Tech stack advice: " + " ".join(advice[:3])
            )

    # 4. Presentation tips
    pres = _load_knowledge("presentation.json")
    if pres:
        context_parts.append(
            "Help the team prepare a 5-minute demo following: "
            "Problem → Approach → Solution → Proof → Learning."
        )

    return "\n".join(context_parts)


# ---------------------------------------------------------------------------
# Post-processing: strip code blocks (Novel Idea #1 — enforce "guide not solve")
# ---------------------------------------------------------------------------
def _strip_code_blocks(text: str) -> str:
    """Remove large code blocks from AI output.

    Keeps trivial snippets (≤ 3 lines) but strips anything longer.
    This enforces the 'guide, not solve' constraint as a system property.
    """
    def _replace_block(match):
        code_content = match.group(2)
        lines = code_content.strip().split("\n")
        if len(lines) <= 3:
            return match.group(0)  # Keep short snippets
        return "[Code block removed — the mentor guides, not solves. Ask your team to implement this.]"

    # Match fenced code blocks: ```...```
    return re.sub(
        r"```(\w*)\n(.*?)```",
        _replace_block,
        text,
        flags=re.DOTALL,
    )


# ---------------------------------------------------------------------------
# Groq API call
# ---------------------------------------------------------------------------
def _call_groq(problem_statement: str, team_context: str = "", phase: str = "") -> dict | None:
    """Call the Groq API with the problem statement and return parsed JSON.

    Returns None on any failure — caller falls through to fallback.
    """
    import requests  # Import here to keep fallback zero-dependency

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY not set — skipping API call")
        return None

    # Build knowledge-grounded context
    knowledge_context = _build_knowledge_context(problem_statement)

    # Build system prompt with optional phase emphasis (Feature D)
    system_prompt = SYSTEM_PROMPT
    if phase and phase in PHASE_PROMPTS:
        system_prompt += f"\n\nPHASE CONTEXT: {PHASE_PROMPTS[phase]}"

    user_message = f"""Problem Statement: {problem_statement}"""
    if team_context:
        user_message += f"\nTeam Context: {team_context}"
    user_message += f"""

KNOWLEDGE BASE CONTEXT (use this to ground your response — adapt, don't copy):
{knowledge_context}

Return ONLY valid JSON matching the required schema. No markdown wrapping, no explanation outside the JSON object."""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        logger.info("Calling Groq API...")
        start = time.time()
        resp = requests.post(
            GROQ_API_URL,
            json=payload,
            headers=headers,
            timeout=GROQ_TIMEOUT,
        )
        elapsed = time.time() - start
        logger.info("Groq API responded in %.2fs (status %d)", elapsed, resp.status_code)

        if resp.status_code != 200:
            logger.warning("Groq API error: %s", resp.text[:500])
            return None

        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        # Strip any accidental code blocks in the guidance text
        content = _strip_code_blocks(content)

        result = json.loads(content)

        # Validate required fields
        required_fields = [
            "problem_summary", "key_questions", "user_personas",
            "design_thinking_guidance", "feature_suggestions",
            "tech_stack_options", "prototype_priorities",
            "validation_checkpoints", "demo_prep_tips",
            "decision", "reason", "next_action",
        ]
        for field in required_fields:
            if field not in result:
                logger.warning("Missing field in API response: %s", field)
                return None

        return result

    except json.JSONDecodeError as e:
        logger.warning("Failed to parse Groq response as JSON: %s", e)
        return None
    except requests.exceptions.Timeout:
        logger.warning("Groq API timed out after %ds", GROQ_TIMEOUT)
        return None
    except requests.exceptions.RequestException as e:
        logger.warning("Groq API request failed: %s", e)
        return None
    except (KeyError, IndexError) as e:
        logger.warning("Unexpected Groq response structure: %s", e)
        return None


# ---------------------------------------------------------------------------
# Rule-based fallback
# ---------------------------------------------------------------------------
def _fallback_response(problem_statement: str) -> dict:
    """Generate a rule-based fallback response.

    1. Try to match keywords against sample_problems.json
    2. If no match → return generic template

    The caller never knows this wasn't from the LLM — same schema.
    """
    sample_data = _load_knowledge("sample_problems.json")

    if sample_data:
        # Try keyword matching against sample problems
        problem_lower = problem_statement.lower()
        problems = sample_data.get("problems", [])
        for problem in problems:
            keywords = problem.get("keywords", [])
            if any(kw in problem_lower for kw in keywords):
                logger.info(
                    "Fallback: matched sample problem '%s'",
                    problem.get("id", "unknown"),
                )
                return problem["response"]

        # No keyword match → use generic fallback
        generic = sample_data.get("generic_fallback")
        if generic:
            logger.info("Fallback: using generic template")
            # Personalize the generic fallback slightly
            generic = dict(generic)  # shallow copy
            generic["problem_summary"] = (
                f"Your problem — '{problem_statement[:100]}' — "
                + generic["problem_summary"]
            )
            return generic

    # Ultimate fallback — hardcoded (should never reach here if knowledge files exist)
    logger.warning("Fallback: knowledge files not available, using hardcoded response")
    return {
        "problem_summary": f"You're working on: {problem_statement[:200]}. Let's break this down step by step using design thinking.",
        "key_questions": [
            "Who is the primary user of your solution?",
            "What is the single most important problem you're solving for them?",
            "What does a working prototype look like in the time you have?",
        ],
        "user_personas": [
            {
                "name": "Primary User",
                "need": "A solution that addresses their core pain point",
                "pain_point": "Current process is manual, slow, or inaccessible",
            }
        ],
        "design_thinking_guidance": "Start with Empathize: understand your user. Then Define: state the problem in one sentence. Ideate: brainstorm 3 approaches. Prototype: build the simplest working version. Test: validate with at least 2 test cases.",
        "feature_suggestions": [
            {"feature": "Core user input form", "why": "Every solution needs user interaction", "effort": "low"},
            {"feature": "Processing logic (AI or rule-based)", "why": "The brain of your solution", "effort": "medium"},
            {"feature": "Structured output display", "why": "The jury sees this — make it clear", "effort": "low"},
        ],
        "tech_stack_options": [
            "HTML/CSS/JavaScript for the frontend",
            "Python with Flask for the backend",
            "In-memory storage or JSON files — skip the database",
        ],
        "prototype_priorities": [
            "P0: One complete input-to-output flow",
            "P1: Handle an alternate input scenario",
            "P2: Polish the output for demo impact",
        ],
        "validation_checkpoints": [
            "Does the solution work end-to-end for the normal case?",
            "Can someone unfamiliar with your code understand the output?",
        ],
        "demo_prep_tips": [
            "Have your demo inputs ready — don't type live under pressure",
            "Practice the flow once: Problem → Approach → Solution → Proof → Learning",
            "Prepare for 'what would you do with more time?' — have an answer ready",
        ],
        "decision": "Build one complete user journey first",
        "reason": "A working end-to-end flow scores higher than multiple broken features",
        "next_action": "Define your single most important user flow, then build it end-to-end before adding anything else",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_mentor_guidance(problem_statement: str, team_context: str = "", phase: str = "") -> dict:
    """Get structured mentor guidance for a hackathon problem statement.

    Tries the Groq API first; falls back to rule-based response on any
    failure (timeout, rate limit, malformed JSON, network error, missing
    API key).

    Args:
        problem_statement: The hackathon problem statement (required, non-empty).
        team_context: Optional team context string (skills, time, experience).
        phase: Optional hackathon phase (understand|build|test|demo) for
               phase-aware guidance emphasis.

    Returns:
        dict matching the locked JSON schema from TECH_STACK.md.

    Raises:
        ValueError: If problem_statement is empty or too long.
    """
    # Input validation
    if not problem_statement or not problem_statement.strip():
        raise ValueError("problem_statement is required and cannot be empty")

    problem_statement = problem_statement.strip()
    if len(problem_statement) > MAX_INPUT_LENGTH:
        raise ValueError(
            f"problem_statement exceeds maximum length of {MAX_INPUT_LENGTH} characters"
        )

    team_context = (team_context or "").strip()
    phase = (phase or "").strip().lower()

    # Try Groq API first
    result = _call_groq(problem_statement, team_context, phase)

    if result is not None:
        # Ensure assumptions field exists (Feature A)
        result.setdefault("assumptions", [])
        logger.info("Returning Groq API response")
        return result

    # Fallback — rule-based
    logger.info("Falling back to rule-based response")
    fallback = _fallback_response(problem_statement)
    fallback.setdefault("assumptions", [
        "No team context provided — guidance is generic",
        "Assuming a beginner team with limited time",
    ])
    return fallback


def get_followup_guidance(original_guidance: dict, question: str, team_context: str = "") -> dict:
    """Get focused follow-up guidance based on a specific question (Feature B).

    Args:
        original_guidance: The full response dict from get_mentor_guidance().
        question: The team's follow-up question.
        team_context: Optional team context string.

    Returns:
        dict with answer, related_suggestions, next_steps, warning.
    """
    import requests

    if not question or not question.strip():
        raise ValueError("question is required and cannot be empty")

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        # Rule-based followup fallback
        return {
            "answer": f"Regarding your question about '{question[:100]}': focus on your prototype priorities and test against your validation checkpoints. Break it into smaller steps.",
            "related_suggestions": [
                "Review your feature suggestions and pick the one with lowest effort + highest impact",
                "Re-read the design thinking guidance for this phase",
            ],
            "next_steps": [
                "Identify the single most important thing to build next",
                "Time-box it to 15 minutes, then reassess",
            ],
            "warning": None,
        }

    # Summarize original guidance for context
    context_summary = json.dumps({
        "problem_summary": original_guidance.get("problem_summary", ""),
        "decision": original_guidance.get("decision", ""),
        "feature_suggestions": original_guidance.get("feature_suggestions", []),
    }, indent=2)

    user_message = f"""Original mentoring context:
{context_summary}

Team's follow-up question: {question}"""
    if team_context:
        user_message += f"\nTeam Context: {team_context}"

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": FOLLOWUP_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        logger.info("Calling Groq API for follow-up...")
        start = time.time()
        resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=GROQ_TIMEOUT)
        elapsed = time.time() - start
        logger.info("Groq follow-up responded in %.2fs (status %d)", elapsed, resp.status_code)

        if resp.status_code != 200:
            logger.warning("Groq follow-up error: %s", resp.text[:300])
            return _followup_fallback(question)

        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        content = _strip_code_blocks(content)
        result = json.loads(content)
        result.setdefault("warning", None)
        return result

    except Exception as e:
        logger.warning("Follow-up API call failed: %s", e)
        return _followup_fallback(question)


def _followup_fallback(question: str) -> dict:
    """Rule-based fallback for follow-up questions."""
    return {
        "answer": f"Great question about '{question[:100]}'. Break this down: what's the smallest testable piece? Build that first, then iterate.",
        "related_suggestions": [
            "Focus on one feature at a time",
            "Test each piece before moving to the next",
        ],
        "next_steps": [
            "Identify the core user action for this feature",
            "Build the simplest version and validate it works",
        ],
        "warning": None,
    }


def validate_problem_statement(problem_statement: str) -> dict:
    """Validate and score a problem statement quality (Feature C).

    Uses rule-based checks first, then optionally enhances with LLM.

    Args:
        problem_statement: The problem statement to evaluate.

    Returns:
        dict with score, feedback array, and improved_statement.
    """
    if not problem_statement or not problem_statement.strip():
        raise ValueError("problem_statement is required")

    problem_statement = problem_statement.strip()
    feedback = []
    total_score = 0

    # --- Rule-based checks ---

    # 1. Specificity: length and detail
    word_count = len(problem_statement.split())
    if word_count >= 15:
        feedback.append({"category": "Specificity", "score": 3, "status": "good", "note": "Problem statement is detailed and specific."})
        total_score += 3
    elif word_count >= 8:
        feedback.append({"category": "Specificity", "score": 2, "status": "needs_work", "note": "Add more detail — who, what, where, why?"})
        total_score += 2
    else:
        feedback.append({"category": "Specificity", "score": 1, "status": "warning", "note": "Too vague. Expand with context: who has this problem and why does it matter?"})
        total_score += 1

    # 2. User Focus: mentions a user type
    user_keywords = ["student", "user", "customer", "patient", "driver", "teacher", "people", "team", "worker", "citizen", "visitor", "commuter", "resident"]
    problem_lower = problem_statement.lower()
    has_user = any(kw in problem_lower for kw in user_keywords)
    if has_user:
        feedback.append({"category": "User Focus", "score": 3, "status": "good", "note": "Target user is identified."})
        total_score += 3
    else:
        feedback.append({"category": "User Focus", "score": 1, "status": "needs_work", "note": "Who is the target user? Specify who benefits from this solution."})
        total_score += 1

    # 3. Scope: hackathon-feasible
    scope_red_flags = ["entire", "all of", "global", "nationwide", "revolutionize", "completely", "every"]
    has_scope_issue = any(flag in problem_lower for flag in scope_red_flags)
    if has_scope_issue:
        feedback.append({"category": "Scope", "score": 1, "status": "warning", "note": "Scope seems too broad for a hackathon. Narrow to one specific aspect."})
        total_score += 1
    elif word_count > 50:
        feedback.append({"category": "Scope", "score": 2, "status": "needs_work", "note": "Problem is detailed but may be too broad. Consider narrowing focus."})
        total_score += 2
    else:
        feedback.append({"category": "Scope", "score": 3, "status": "good", "note": "Scope appears manageable for a hackathon."})
        total_score += 3

    # 4. Innovation Potential: domain matching
    fp = _load_knowledge("feature_patterns.json")
    matched_domain = None
    if fp:
        for domain_key, domain_data in fp.get("domains", {}).items():
            if any(kw in problem_lower for kw in domain_data.get("keywords", [])):
                matched_domain = domain_data.get("label", domain_key)
                break

    if matched_domain:
        feedback.append({"category": "Innovation Potential", "score": 3, "status": "good", "note": f"Recognized domain: {matched_domain}. Rich feature space available."})
        total_score += 3
    else:
        feedback.append({"category": "Innovation Potential", "score": 2, "status": "needs_work", "note": "Novel domain — more creative freedom but less template guidance available."})
        total_score += 2

    # Normalize to 1-10 scale
    score = round(total_score * 10 / 12)

    result = {
        "score": score,
        "max_score": 10,
        "feedback": feedback,
        "improved_statement": None,
    }

    # Try LLM for improved statement if API available
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key and score < 8:
        try:
            import requests
            payload = {
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": VALIDATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Evaluate this problem statement: {problem_statement}"},
                ],
                "temperature": 0.5,
                "max_tokens": 512,
                "response_format": {"type": "json_object"},
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=GROQ_TIMEOUT)
            if resp.status_code == 200:
                llm_result = json.loads(resp.json()["choices"][0]["message"]["content"])
                result["improved_statement"] = llm_result.get("improved_statement")
                # Merge LLM feedback if available
                if "feedback" in llm_result:
                    result["llm_feedback"] = llm_result["feedback"]
        except Exception as e:
            logger.warning("Validator LLM enhancement failed: %s", e)

    return result
