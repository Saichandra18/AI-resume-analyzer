from pathlib import Path

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.ats_analyzer import analyze_resume_against_job
from app.ats_result_formatter import format_ats_result
from app.recommendation_engine import generate_recommendations
from app.score_explainer import explain_ats_score
from app.services.resume_parser import extract_structured_resume
from app.strengths_weaknesses import generate_strengths_weaknesses


ats_bp = Blueprint("ats", __name__)

UPLOAD_FOLDER = Path("uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@ats_bp.route("/api/analyze", methods=["POST"])
def analyze_resume():
    """Analyze a resume against a job description."""

    if "resume" not in request.files:
        return jsonify({
            "status": "error",
            "message": "No resume file was provided"
        }), 400

    resume_file = request.files["resume"]

    if resume_file.filename == "":
        return jsonify({
            "status": "error",
            "message": "No file was selected"
        }), 400

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()

    if not job_description:
        return jsonify({
            "status": "error",
            "message": "Job description cannot be empty"
        }), 400

    extension = Path(
        resume_file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({
            "status": "error",
            "message": "Unsupported file format. Use PDF or DOCX."
        }), 400

    UPLOAD_FOLDER.mkdir(exist_ok=True)

    filename = secure_filename(resume_file.filename)

    file_path = UPLOAD_FOLDER / filename

    resume_file.save(file_path)

    try:
        resume_data = extract_structured_resume(
            file_path
        )

        result = analyze_resume_against_job(
            resume_data,
            job_description,
        )

        formatted_result = format_ats_result(result)

        score_explanation = explain_ats_score(
            formatted_result
        )

        strengths_weaknesses = generate_strengths_weaknesses(
            formatted_result
        )

        recommendations = generate_recommendations(
            formatted_result
        )

        return jsonify({
            "status": "success",

            # Existing ATS result
            **result,

            # New user-facing formatted result
            **formatted_result,

            # Phase 6 analysis
            "score_explanation": score_explanation,
            "strengths": strengths_weaknesses["strengths"],
            "weaknesses": strengths_weaknesses["weaknesses"],
            "recommendations": recommendations[
                "recommendations"
            ],
        })

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": f"Could not analyze resume: {str(error)}"
        }), 500