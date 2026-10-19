
import hmac
import os

import requests
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
PROXY_TOKEN = os.environ.get("OLLAMA_PROXY_TOKEN", "")

ALLOWED_PATHS = {
    "/v1/responses",
    "/v1/models",
}


@app.before_request
def authenticate_and_validate():
    if not PROXY_TOKEN:
        return jsonify(error="Proxy authentication is not configured"), 503

    auth_header = request.headers.get("Authorization", "")
    expected_header = f"Bearer {PROXY_TOKEN}"

    if not hmac.compare_digest(auth_header, expected_header):
        return jsonify(error="Unauthorized"), 401

    if request.method != "POST" and request.path != "/v1/models":
        return jsonify(error="Method not allowed"), 405

    if request.path not in ALLOWED_PATHS:
        return jsonify(error="Endpoint not allowed"), 404

    if request.content_length and request.content_length > 1_000_000:
        return jsonify(error="Request too large"), 413


@app.route("/v1/responses", methods=["POST"])
def responses():
    try:
        upstream = requests.post(
            f"{OLLAMA_BASE_URL}/v1/responses",
            json=request.get_json(silent=True),
            timeout=(10, 300),
        )
        return Response(
            upstream.content,
            status=upstream.status_code,
            content_type=upstream.headers.get(
                "Content-Type", "application/json"
            ),
        )
    except requests.RequestException:
        return jsonify(error="Local Ollama request failed"), 502


@app.route("/v1/models", methods=["GET", "POST"])
def models():
    try:
        upstream = requests.get(
            f"{OLLAMA_BASE_URL}/v1/models",
            timeout=(5, 15),
        )
        return Response(
            upstream.content,
            status=upstream.status_code,
            content_type=upstream.headers.get(
                "Content-Type", "application/json"
            ),
        )
    except requests.RequestException:
        return jsonify(error="Local Ollama request failed"), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8765, debug=False)
