"""Coffee Brew API — A simple REST API for managing coffee brews.

Linked to Jira: SCRUM-12
"""
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# In-memory brew store
brews = []

BREW_STRENGTHS = ["light", "medium", "strong"]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "caffeinated", "timestamp": datetime.utcnow().isoformat()})


@app.route("/brews", methods=["GET"])
def list_brews():
    return jsonify({"brews": brews, "count": len(brews)})


@app.route("/brews", methods=["POST"])
def create_brew():
    data = request.get_json() or {}
    strength = data.get("strength", "medium")
    if strength not in BREW_STRENGTHS:
        return jsonify({"error": f"Invalid strength. Choose from: {BREW_STRENGTHS}"}), 400

    brew = {
        "id": len(brews) + 1,
        "strength": strength,
        "roast": data.get("roast", "house blend"),
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
