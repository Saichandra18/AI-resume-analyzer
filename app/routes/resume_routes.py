
from pathlib import Path
import logging
import uuid

from app.services.text_cleaner import clean_resume_text

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.services.resume_parser import extract_resume_text


logger = logging.getLogger(__name__)

resume_bp = Blueprint("resume", __name__)

UPLOAD_FOLDER = Path("uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@resume_bp.route("/api/resume/upload", methods=["POST"])
def upload_resume():
    """Upload a resume and extract its text."""

    if "resume" not in request.files:
        return jsonify({
            "status": "error",
            "message": "No resume file was provided"
        }), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({
            "status": "error",
            "message": "No file was selected"
        }), 400

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({
            "status": "error",
            "message": "Unsupported file format. Use PDF or DOCX."
        }), 400

    UPLOAD_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    original_filename = secure_filename(file.filename)

    if not original_filename:
        return jsonify({
            "status": "error",
            "message": "Invalid filename."
        }), 400

    # Use a unique server-side filename so that one upload
    # cannot overwrite another uploaded resume.
    unique_filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = UPLOAD_FOLDER / unique_filename

    try:
        file.save(file_path)

        resume_text = extract_resume_text(file_path)
        cleaned_text = clean_resume_text(resume_text)

        return jsonify({
            "status": "success",
            "message": "Resume uploaded successfully",
            "filename": original_filename,
            "text": cleaned_text
        })

    except Exception:
        logger.exception(
            "Failed to process uploaded resume."
        )

        return jsonify({
            "status": "error",
            "message": "Could not process resume."
        }), 500

    finally:
        # The extracted resume text is returned immediately,
        # so the temporary uploaded file is no longer needed.
        try:
            if file_path.exists():
                file_path.unlink()
        except OSError:
            logger.warning(
                "Could not remove temporary uploaded file: %s",
                file_path,
                exc_info=True,
            )

