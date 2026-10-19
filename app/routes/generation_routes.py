"""Flask routes for optimized resume generation."""

from pathlib import Path
import logging

from flask import (
    Blueprint,
    jsonify,
    request,
    send_from_directory,
)

from app.rag.runtime import get_knowledge_base_service
from app.rag.config import RAGConfig
from app.rag.optimization.service import RAGOptimizationService
from app.resume_structurer import structure_resume
from app.resume_generation_service import (
    generate_optimized_resume_documents,
)


logger = logging.getLogger(__name__)


generation_bp = Blueprint(
    "generation",
    __name__,
)

GENERATED_RESUMES_DIR = (
    Path(__file__).resolve().parents[2]
    / "generated_resumes"
)


@generation_bp.route(
    "/api/resume/generate",
    methods=["POST"],
)
def generate_resume():
    """Generate JD-optimized resume documents in DOCX and PDF."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(
            {
                "status": "error",
                "message": "Request body must contain JSON data.",
            }
        ), 400

    resume_text = data.get(
        "resume_text",
        "",
    )

    job_description = data.get(
        "job_description",
        "",
    )

    if (
        not isinstance(resume_text, str)
        or not resume_text.strip()
    ):
        return jsonify(
            {
                "status": "error",
                "message": "Resume text is required.",
            }
        ), 400

    if (
        not isinstance(job_description, str)
        or not job_description.strip()
    ):
        return jsonify(
            {
                "status": "error",
                "message": "Job description is required.",
            }
        ), 400

    target_pages = data.get(
        "target_pages",
        1,
    )

    try:
        target_pages = int(target_pages)
    except (TypeError, ValueError):
        return jsonify(
            {
                "status": "error",
                "message": (
                    "target_pages must be a positive integer."
                ),
            }
        ), 400

    if target_pages <= 0:
        return jsonify(
            {
                "status": "error",
                "message": (
                    "target_pages must be a positive integer."
                ),
            }
        ), 400

    template = data.get(
        "template",
        "ats_clean",
    )

    if not isinstance(template, str):
        return jsonify(
            {
                "status": "error",
                "message": "template must be a string.",
            }
        ), 400

    template = template.strip()

    if not template:
        template = "ats_clean"

    experience_level = data.get(
        "experience_level",
        "experienced",
    )

    if not isinstance(experience_level, str):
        return jsonify(
            {
                "status": "error",
                "message": "experience_level must be a string.",
            }
        ), 400

    experience_level = experience_level.strip()

    if not experience_level:
        experience_level = "experienced"

    target_job_title = data.get(
        "target_job_title"
    )

    if (
        target_job_title is not None
        and not isinstance(target_job_title, str)
    ):
        return jsonify(
            {
                "status": "error",
                "message": "target_job_title must be a string.",
            }
        ), 400

    if isinstance(target_job_title, str):
        target_job_title = target_job_title.strip()

        if not target_job_title:
            target_job_title = None

    GENERATED_RESUMES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    docx_output_path = (
        GENERATED_RESUMES_DIR
        / "optimized_resume.docx"
    )

    pdf_output_path = (
        GENERATED_RESUMES_DIR
        / "optimized_resume.pdf"
    )

    try:
        # Initialize RAG inside the protected generation block.
        rag_config = RAGConfig()
        rag_config.enabled = True

        knowledge_base_service = (
            get_knowledge_base_service()
        )

        rag_service = RAGOptimizationService(
            config=rag_config,
            knowledge_base_service=(
                knowledge_base_service
            ),
        )

        # Generate the optimized FinalResume once and
        # render that same result to both DOCX and PDF.
        resume_data = data.get("resume_data")
        if not isinstance(resume_data, dict) or not resume_data:
            resume_data = structure_resume(resume_text)

        result = generate_optimized_resume_documents(
            resume_text=resume_text,
            docx_output_path=docx_output_path,
            pdf_output_path=pdf_output_path,
            resume_data=resume_data,
            job_description=job_description,
            ats_result=data.get(
                "ats_result"
            ),
            resume_quality=data.get(
                "resume_quality"
            ),
            content_quality=data.get(
                "content_quality"
            ),
            improvement_suggestions=data.get(
                "improvement_suggestions"
            ),
            tailoring_plan=data.get(
                "tailoring_plan"
            ),
            experience_level=experience_level,
            target_pages=target_pages,
            target_job_title=target_job_title,
            template=template,
            rag_service=rag_service,
        )

        response_data = {
            "status": "success",
            "message": (
                "Optimized resume generated successfully "
                "in DOCX and PDF formats."
            ),
            "document_path": str(
                result["document_path"]
            ),
            "pdf_path": str(
                result["pdf_path"]
            ),
            "final_resume": result[
                "final_resume"
            ].to_dict(),
            "validation": result[
                "validation"
            ],
            "document_validation": result.get(
                "document_validation",
                {},
            ),
        }

        if "ats_evaluation" in result:
            response_data["ats_evaluation"] = result[
                "ats_evaluation"
            ]

        return jsonify(response_data), 200

    except Exception:
        logger.exception(
            "Failed to generate optimized resume documents."
        )

        return jsonify(
            {
                "status": "error",
                "message": (
                    "Could not generate optimized resume."
                ),
            }
        ), 500


@generation_bp.route(
    "/api/resume/download",
    methods=["GET"],
)
def download_resume():
    """Download a generated optimized resume in DOCX or PDF format."""

    filename = request.args.get(
        "filename",
        "",
    )

    if not filename:
        return jsonify(
            {
                "status": "error",
                "message": "Filename is required.",
            }
        ), 400

    requested_path = Path(filename)

    allowed_extensions = {
        ".docx",
        ".pdf",
    }

    if (
        requested_path.name != filename
        or requested_path.suffix.lower()
        not in allowed_extensions
    ):
        return jsonify(
            {
                "status": "error",
                "message": "Invalid resume filename.",
            }
        ), 400

    if not GENERATED_RESUMES_DIR.exists():
        return jsonify(
            {
                "status": "error",
                "message": "Generated resume not found.",
            }
        ), 404

    file_path = GENERATED_RESUMES_DIR / filename

    if not file_path.is_file():
        return jsonify(
            {
                "status": "error",
                "message": "Generated resume not found.",
            }
        ), 404

    extension = requested_path.suffix.lower()

    if extension == ".pdf":
        mimetype = "application/pdf"
    else:
        mimetype = (
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

    try:
        return send_from_directory(
            GENERATED_RESUMES_DIR,
            filename,
            as_attachment=True,
            mimetype=mimetype,
        )

    except Exception:
        logger.exception(
            "Failed to download generated resume: %s",
            filename,
        )

        return jsonify(
            {
                "status": "error",
                "message": "Could not download resume.",
            }
        ), 500
