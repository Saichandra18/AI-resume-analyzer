import logging

from flask import Blueprint, jsonify, request


logger = logging.getLogger(__name__)

job_bp = Blueprint("job", __name__)


@job_bp.route("/api/job-description", methods=["POST"])
def submit_job_description():
    data = request.get_json()

    if not isinstance(data, dict) or not data:
        return jsonify({
            "status": "error",
            "message": "Request body must contain JSON data"
        }), 400

    job_description = data.get(
        "job_description",
        ""
    )

    if not isinstance(job_description, str):
        return jsonify({
            "status": "error",
            "message": "Job description must be a string"
        }), 400

    job_description = job_description.strip()

    if not job_description:
        return jsonify({
            "status": "error",
            "message": "Job description cannot be empty"
        }), 400

    try:
        return jsonify({
            "status": "success",
            "message": "Job description received successfully",
            "job_description": job_description
        })

    except Exception:
        logger.exception(
            "Failed to process job description."
        )

        return jsonify({
            "status": "error",
            "message": "Could not process job description."
        }), 500
