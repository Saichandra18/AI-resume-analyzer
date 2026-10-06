
import logging

from flask import Blueprint, jsonify, request

from app.resume_rewriter import rewrite_resume


logger = logging.getLogger(__name__)

rewrite_bp = Blueprint("rewrite", __name__)


@rewrite_bp.route("/api/resume/rewrite", methods=["POST"])
def rewrite_resume_route():
    """Rewrite resume content using the Phase 9 tailoring plan."""

    data = request.get_json(silent=True) or {}

    resume_text = data.get("resume_text", "")
    resume_data = data.get("resume_data", {})
    tailoring_plan = data.get("tailoring_plan", {})
    job_description = data.get("job_description", "")

    experience = data.get("experience", [])
    projects = data.get("projects", [])
    skills = data.get("skills", [])

    if not isinstance(resume_text, str) or not resume_text.strip():
        return jsonify({
            "status": "error",
            "message": "Resume text is required."
        }), 400

    try:
        result = rewrite_resume(
            resume_text=resume_text,
            resume_data=resume_data,
            tailoring_plan=tailoring_plan,
            job_description=job_description,
            experience=experience,
            projects=projects,
            skills=skills,
        )

        return jsonify({
            "status": "success",
            "rewrite": result,
        })

    except Exception:
        logger.exception(
            "Failed to rewrite resume."
        )

        return jsonify({
            "status": "error",
            "message": "Could not rewrite resume."
        }), 500

