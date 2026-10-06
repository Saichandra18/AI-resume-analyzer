from pathlib import Path
import logging
import uuid

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.services.resume_parser import (
    extract_resume_text,
    extract_structured_resume,
)
from app.ats_analyzer import analyze_resume_against_job
from app.resume_quality_analyzer import (
    analyze_resume_quality,
)
from app.resume_content_quality import (
    analyze_resume_content_quality,
)
from app.resume_improvement import (
    generate_improvement_suggestions,
)
from app.resume_tailoring import (
    generate_tailoring_plan,
)


logger = logging.getLogger(__name__)

ats_bp = Blueprint("ats", __name__)

UPLOAD_FOLDER = Path("uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@ats_bp.route("/api/analyze", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({
            "status": "error",
            "message": "Resume file is required"
        }), 400

    resume_file = request.files["resume"]

    if not resume_file.filename:
        return jsonify({
            "status": "error",
            "message": "Resume filename is required"
        }), 400

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()

    if not job_description:
        return jsonify({
            "status": "error",
            "message": "Job description is required"
        }), 400

    extension = Path(
        resume_file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({
            "status": "error",
            "message": "Unsupported file format. Use PDF or DOCX."
        }), 400

    UPLOAD_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    original_filename = secure_filename(
        resume_file.filename
    )

    if not original_filename:
        return jsonify({
            "status": "error",
            "message": "Invalid filename"
        }), 400

    unique_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = UPLOAD_FOLDER / unique_filename

    try:
        resume_file.save(file_path)

        # ---------------------------------------------------------
        # Resume extraction
        # ---------------------------------------------------------
        resume_text = extract_resume_text(
            file_path
        )

        resume_data = extract_structured_resume(
            file_path
        )

        # ---------------------------------------------------------
        # ATS analysis
        # ---------------------------------------------------------
        result = analyze_resume_against_job(
            resume_data,
            job_description
        )

        # ---------------------------------------------------------
        # Resume quality analysis
        # ---------------------------------------------------------
        resume_quality = analyze_resume_quality(
            resume_data
        )

        # ---------------------------------------------------------
        # Resume content quality analysis
        # ---------------------------------------------------------
        content_quality = analyze_resume_content_quality(
            resume_data
        )

        # ---------------------------------------------------------
        # Improvement suggestions
        # ---------------------------------------------------------
        improvement_result = (
            generate_improvement_suggestions(
                resume_data=resume_data,
                resume_quality=resume_quality,
                content_quality=content_quality,
                ats_result=result,
            )
        )

        improvement_suggestions = (
            improvement_result.get(
                "improvement_suggestions",
                []
            )
        )

        # ---------------------------------------------------------
        # Tailoring plan
        # ---------------------------------------------------------
        tailoring_result = generate_tailoring_plan(
            resume_data=resume_data,
            ats_result=result,
            resume_quality=resume_quality,
            content_quality=content_quality,
            improvement_suggestions=improvement_suggestions,
        )

        tailoring_plan = tailoring_result.get(
            "tailoring_plan",
            {}
        )

        # ---------------------------------------------------------
        # API response
        # ---------------------------------------------------------
        return jsonify({
            "status": "success",
            "message": "Resume analyzed successfully",
            "filename": original_filename,
            "resume_text": resume_text,

            # ATS score
            "ats_score": result.get("ats_score"),
            "component_scores": result.get(
                "component_scores"
            ),
            "weights": result.get("weights"),

            # Skills
            "skills": result.get("skills"),
            "matched_skills": result.get(
                "matched_skills"
            ),
            "missing_skills": result.get(
                "missing_skills"
            ),

            # Experience
            "experience": result.get(
                "experience"
            ),

            # Qualifications
            "qualifications": result.get(
                "qualifications"
            ),
            "matched_qualifications": result.get(
                "matched_qualifications"
            ),
            "missing_qualifications": result.get(
                "missing_qualifications"
            ),

            # Keywords
            "keywords": result.get("keywords"),
            "matched_keywords": result.get(
                "matched_keywords"
            ),
            "missing_keywords": result.get(
                "missing_keywords"
            ),

            # Explanation
            "score_explanation": result.get(
                "score_explanation"
            ),

            # ATS recommendations
            "strengths": result.get(
                "strengths"
            ),
            "weaknesses": result.get(
                "weaknesses"
            ),
            "recommendations": result.get(
                "recommendations"
            ),

            # Resume quality
            "resume_quality": resume_quality,

            # Content quality
            "content_quality": content_quality,

            # Improvement suggestions
            "improvement_suggestions": (
                improvement_suggestions
            ),

            # Tailoring plan
            "tailoring_plan": tailoring_plan,

            # Complete ATS analysis
            "analysis": result,
        })

    except Exception:
        logger.exception(
            "Failed to analyze uploaded resume."
        )

        return jsonify({
            "status": "error",
            "message": "Could not analyze resume."
        }), 500

    finally:
        try:
            if file_path.exists():
                file_path.unlink()

        except OSError:
            logger.warning(
                "Could not remove temporary ATS upload: %s",
                file_path,
                exc_info=True,
            )