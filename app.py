"""
app.py — Flask Server (Savio)

Backend: POST /api/mentor, POST /api/followup, POST /api/validate,
GET /api/health, GET /api/test-cases.
Stateless — no database, no auth, no session management.
"""

import json
import os
import logging
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()  # Load .env before anything reads env vars

from flask import Flask, request, jsonify, send_from_directory
from mentor_logic import get_mentor_guidance, get_followup_guidance, validate_problem_statement

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder=".", static_url_path="")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CORS — allow frontend to call API from file:// or different port
# ---------------------------------------------------------------------------
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def serve_index():
    """Serve the frontend HTML."""
    return send_from_directory(".", "index.html")


@app.route("/api/mentor", methods=["POST", "OPTIONS"])
def mentor():
    """Main endpoint — accepts problem statement, returns structured guidance.

    Request:
        { "problem_statement": "string, required", "team_context": "string, optional" }

    Response:
        Full structured guidance JSON (see TECH_STACK.md for schema)

    Errors:
        400: Missing or invalid problem_statement
        500: Unexpected server error (should never happen due to fallback)
    """
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({
                "error": "Invalid request body — expected JSON",
                "details": "Send a JSON object with at least a 'problem_statement' field",
            }), 400

        problem_statement = data.get("problem_statement", "")
        team_context = data.get("team_context", "")
        phase = data.get("phase", "")  # Feature D: phase-aware guidance
        file_name = data.get("file_name", "")
        file_type = data.get("file_type", "")
        file_base64 = data.get("file_base64", "")

        # Input validation
        if not problem_statement.strip() and not file_base64:
            return jsonify({
                "error": "Input required",
                "details": "Provide a problem statement or upload a context document",
            }), 400

        # Feature: Parse Context from File
        if file_base64 and file_name and file_type:
            try:
                from document_parser import extract_context_from_file
                extracted_text = extract_context_from_file(file_name, file_type, file_base64)
                
                # Inject extracted text into the problem statement
                problem_statement = str(problem_statement) + f"\n\n--- EXTRACTED CONTEXT FROM UPLOADED FILE ({file_name}) ---\n{extracted_text}"
            except Exception as parse_e:
                logger.error(f"Error parsing document: {parse_e}")
                # We continue with just the problem statement if parsing fails

        # Get mentor guidance (Groq API → fallback)
        result = get_mentor_guidance(
            problem_statement=str(problem_statement),
            team_context=str(team_context),
            phase=str(phase),
        )

        logger.info("Successfully generated mentor guidance")
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({
            "error": str(e),
            "details": "Input validation failed",
        }), 400

    except Exception as e:
        logger.exception("Unexpected error in /api/mentor")
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e),
        }), 500


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint.

    Returns:
        { "status": "ok", "mode": "ai|rule_based", "timestamp": "..." }
    """
    api_key = os.environ.get("GROQ_API_KEY")
    mode = "ai" if api_key else "rule_based"

    return jsonify({
        "status": "ok",
        "mode": mode,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200


@app.route("/api/test-cases", methods=["GET"])
def test_cases():
    """Load and return test cases from test_cases.json.

    Returns:
        The contents of test_cases.json, or an error if the file is missing.
    """
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_cases.json")
    try:
        with open(test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({
            "error": "test_cases.json not found",
            "details": "Create test_cases.json in the project root",
        }), 404
    except json.JSONDecodeError as e:
        return jsonify({
            "error": "test_cases.json contains invalid JSON",
            "details": str(e),
        }), 500


@app.route("/api/followup", methods=["POST", "OPTIONS"])
def followup():
    """Follow-up question endpoint (Feature B).

    Request:
        {
            "original_guidance": { /* full response from /api/mentor */ },
            "question": "string, required",
            "team_context": "string, optional"
        }

    Response:
        {
            "answer": "string",
            "related_suggestions": ["string"],
            "next_steps": ["string"],
            "warning": "string or null"
        }
    """
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid request body", "details": "Expected JSON"}), 400

        original_guidance = data.get("original_guidance", {})
        question = data.get("question", "")
        team_context = data.get("team_context", "")

        if not question or not str(question).strip():
            return jsonify({"error": "question is required", "details": "Provide a follow-up question"}), 400

        result = get_followup_guidance(
            original_guidance=original_guidance,
            question=str(question),
            team_context=str(team_context),
        )
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e), "details": "Input validation failed"}), 400
    except Exception as e:
        logger.exception("Unexpected error in /api/followup")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@app.route("/api/validate", methods=["POST", "OPTIONS"])
def validate():
    """Problem statement validator endpoint (Feature C).

    Request:
        { "problem_statement": "string, required" }

    Response:
        {
            "score": number,
            "max_score": 10,
            "feedback": [{ "category": "string", "score": number, "status": "string", "note": "string" }],
            "improved_statement": "string or null"
        }
    """
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid request body", "details": "Expected JSON"}), 400

        problem_statement = data.get("problem_statement", "")
        file_name = data.get("file_name", "")
        file_type = data.get("file_type", "")
        file_base64 = data.get("file_base64", "")

        if not problem_statement.strip() and not file_base64:
            return jsonify({"error": "Input required", "details": "Provide a problem statement or upload a context document to validate"}), 400

        # Feature: Parse Context from File
        if file_base64 and file_name and file_type:
            try:
                from document_parser import extract_context_from_file
                extracted_text = extract_context_from_file(file_name, file_type, file_base64)
                problem_statement = str(problem_statement) + f"\n\n--- EXTRACTED CONTEXT FROM UPLOADED FILE ({file_name}) ---\n{extracted_text}"
            except Exception as parse_e:
                logger.error(f"Error parsing document for validation: {parse_e}")

        result = validate_problem_statement(str(problem_statement))
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e), "details": "Input validation failed"}), 400
    except Exception as e:
        logger.exception("Unexpected error in /api/validate")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting Hackathon Mentor AI server on port %d", port)

    if not os.environ.get("GROQ_API_KEY"):
        logger.warning(
            "⚠️  GROQ_API_KEY not set — running in FALLBACK-ONLY mode. "
            "Set the environment variable to enable AI responses."
        )

    app.run(host="0.0.0.0", port=port, debug=True)
