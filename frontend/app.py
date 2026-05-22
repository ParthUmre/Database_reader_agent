from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# ── Point this at your existing backend ──────────────────────────────────────
BACKEND_URL = "http://localhost:8000/chat/query"   # ← change to your endpoint


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Thin proxy: forwards the user message to your backend and returns its response."""
    payload = request.get_json()
    try:
        resp = requests.post(BACKEND_URL, json=payload, timeout=60)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot reach backend. Is it running?"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)