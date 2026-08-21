from flask import Blueprint, jsonify, request


job_bp = Blueprint("job", __name__)


@job_bp.route("/api/job-description", methods=["POST"])
def submit_job_description():
    """Receive and validate a job description."""

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON data"
        }), 400

    job_description = data.get("job_description", "").strip()

    if not job_description:
        return jsonify({
            "status": "error",
            "message": "Job description cannot be empty"
        }), 400

    return jsonify({
        "status": "success",
        "message": "Job description received successfully",
        "job_description": job_description
    })