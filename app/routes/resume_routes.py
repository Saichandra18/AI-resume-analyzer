from pathlib import Path

from app.services.text_cleaner import clean_resume_text

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.services.resume_parser import extract_resume_text


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

    UPLOAD_FOLDER.mkdir(exist_ok=True)

    filename = secure_filename(file.filename)
    file_path = UPLOAD_FOLDER / filename

    file.save(file_path)

    try:
        resume_text = extract_resume_text(file_path)
        cleaned_text = clean_resume_text(resume_text)

        return jsonify({
            "status": "success",
            "message": "Resume uploaded successfully",
            "filename": filename,
            "text": cleaned_text
        })

    except Exception as error:
        return jsonify({
            "status": "error",
            "message": f"Could not process resume: {str(error)}"
        }), 500