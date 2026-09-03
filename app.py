"""
app.py — Flask Server (Savio)

Single-route backend: POST /api/mentor, GET /api/health, GET /api/test-cases.
Stateless — no database, no auth, no session management.
"""

import json
import os
import logging
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()  # Load .env before anything reads env vars

from flask import Flask, request, jsonify, send_from_directory
from mentor_logic import get_mentor_guidance

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

        # Input validation
        if not problem_statement or not str(problem_statement).strip():
            return jsonify({
                "error": "problem_statement is required and cannot be empty",
                "details": "Provide a hackathon problem statement as a non-empty string",
            }), 400

        # Get mentor guidance (Groq API → fallback)
        result = get_mentor_guidance(
            problem_statement=str(problem_statement),
            team_context=str(team_context),
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
