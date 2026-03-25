"""Coffee Brew API — A simple REST API for managing coffee brews.

Linked to Jira: SCRUM-12
"""
import os
import json
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# In-memory brew store
brews = []

DEFAULT_STRENGTHS = ["light", "medium", "strong"]
DEFAULT_STRENGTH = "medium"
DEFAULT_ROAST = "house blend"


def load_config():
    """Load brew config from file, falling back to safe defaults (SCRUM-17)."""
    config_path = os.path.join(os.path.dirname(__file__), "brew_config.json")
    try:
        with open(config_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.logger.warning("brew_config.json not found or invalid — using defaults")
        return {
            "defaults": {"strength": DEFAULT_STRENGTH, "roast": DEFAULT_ROAST},
            "strengths": [
                {"name": s, "grind_seconds": 15 + i * 5, "brew_seconds": 180 + i * 60}
                for i, s in enumerate(DEFAULT_STRENGTHS)
            ],
        }


config = load_config()
BREW_STRENGTHS = [s["name"] for s in config.get("strengths", [])] or DEFAULT_STRENGTHS


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "caffeinated", "timestamp": datetime.utcnow().isoformat()})


@app.route("/brews", methods=["GET"])
def list_brews():
    return jsonify({"brews": brews, "count": len(brews)})


@app.route("/brews", methods=["POST"])
def create_brew():
    data = request.get_json() or {}
    strength = data.get("strength") or config.get("defaults", {}).get("strength", DEFAULT_STRENGTH)
    if strength not in BREW_STRENGTHS:
        return jsonify({"error": f"Invalid strength. Choose from: {BREW_STRENGTHS}"}), 400

    brew = {
        "id": len(brews) + 1,
        "strength": strength,
        "roast": data.get("roast") or config.get("defaults", {}).get("roast", DEFAULT_ROAST),
        "status": "brewing",
        "created_at": datetime.utcnow().isoformat(),
    }
    brews.append(brew)
    return jsonify(brew), 201


@app.route("/brews/<int:brew_id>", methods=["GET"])
def get_brew(brew_id):
    brew = next((b for b in brews if b["id"] == brew_id), None)
    if not brew:
        return jsonify({"error": "Brew not found"}), 404
    return jsonify(brew)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
