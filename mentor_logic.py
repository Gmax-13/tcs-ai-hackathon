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

OUTPUT FORMAT: You MUST return valid JSON matching the exact schema below. No markdown, no explanation outside JSON.

{
  "problem_summary": "string",
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
def _call_groq(problem_statement: str, team_context: str = "") -> dict | None:
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
            {"role": "system", "content": SYSTEM_PROMPT},
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
# Public API — the single entry point for app.py
# ---------------------------------------------------------------------------
def get_mentor_guidance(problem_statement: str, team_context: str = "") -> dict:
    """Get structured mentor guidance for a hackathon problem statement.

    Tries the Groq API first; falls back to rule-based response on any
    failure (timeout, rate limit, malformed JSON, network error, missing
    API key).

    Args:
        problem_statement: The hackathon problem statement (required, non-empty).
        team_context: Optional team context string (skills, time, experience).

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

    # Try Groq API first
    result = _call_groq(problem_statement, team_context)

    if result is not None:
        logger.info("Returning Groq API response")
        return result

    # Fallback — rule-based
    logger.info("Falling back to rule-based response")
    return _fallback_response(problem_statement)
