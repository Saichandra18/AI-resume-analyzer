from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INDEX_HTML = (
    PROJECT_ROOT
    / "frontend"
    / "templates"
    / "index.html"
)

APP_JS = (
    PROJECT_ROOT
    / "frontend"
    / "static"
    / "js"
    / "app.js"
)

GENERATION_ROUTES = (
    PROJECT_ROOT
    / "app"
    / "routes"
    / "generation_routes.py"
)


def read_file(path):
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# FINAL UI INPUTS
# ---------------------------------------------------------------------------

def test_resume_upload_input_exists():
    source = read_file(INDEX_HTML)

    assert "type=\"file\"" in source
    assert "resume" in source.lower()


def test_job_description_input_exists():
    source = read_file(INDEX_HTML)

    assert "job-description" in source.lower()


def test_template_selector_exists():
    source = read_file(INDEX_HTML)

    assert 'id="resume-template"' in source


def test_generation_button_exists():
    source = read_file(INDEX_HTML)

    assert "generate" in source.lower()


# ---------------------------------------------------------------------------
# GENERATION WORKFLOW
# ---------------------------------------------------------------------------

def test_generation_api_endpoint_exists_in_frontend():
    source = read_file(APP_JS)

    assert "/api/resume/generate" in source


def test_generation_request_uses_resume_data():
    source = read_file(APP_JS)

    assert "resume" in source.lower()


def test_generation_request_uses_job_description():
    source = read_file(APP_JS)

    assert "job_description" in source


def test_generation_request_uses_template():
    source = read_file(APP_JS)

    assert "resumeTemplateInput.value" in source
    assert "template:" in source


# ---------------------------------------------------------------------------
# GENERATION STATE / PROGRESS
# ---------------------------------------------------------------------------

def test_generation_progress_function_exists():
    source = read_file(APP_JS)

    assert "updateGenerationProgress" in source


def test_generation_progress_is_updated_during_generation():
    source = read_file(APP_JS)

    assert "updateGenerationProgress(" in source


# ---------------------------------------------------------------------------
# ATS RESULTS
# ---------------------------------------------------------------------------

def test_generation_ats_results_function_exists():
    source = read_file(APP_JS)

    assert "displayGenerationATSResults" in source


def test_generation_ats_results_uses_api_response():
    source = read_file(APP_JS)

    assert "data.ats_evaluation" in source


# ---------------------------------------------------------------------------
# VALIDATION RESULTS
# ---------------------------------------------------------------------------

def test_generation_validation_function_exists():
    source = read_file(APP_JS)

    assert "displayGenerationValidation" in source


def test_generation_validation_uses_api_response():
    source = read_file(APP_JS)

    assert "data.document_validation" in source


def test_validation_is_displayed_after_ats_results():
    source = read_file(APP_JS)

    generation_start = source.find(
        "window.resumeGenerationResult"
    )

    assert generation_start != -1

    ats_position = source.find(
        "displayGenerationATSResults(",
        generation_start,
    )

    validation_position = source.find(
        "displayGenerationValidation(",
        ats_position,
    )

    assert ats_position != -1
    assert validation_position != -1
    assert validation_position > ats_position


# ---------------------------------------------------------------------------
# DOWNLOAD WORKFLOW
# ---------------------------------------------------------------------------

def test_docx_download_button_exists():
    source = read_file(INDEX_HTML)

    assert 'id="download-resume-button"' in source


def test_pdf_download_button_exists():
    source = read_file(INDEX_HTML)

    assert 'id="download-pdf-button"' in source


def test_docx_download_handler_exists():
    source = read_file(APP_JS)

    assert "download-resume-button" in source
    assert "document_path" in source


def test_pdf_download_handler_exists():
    source = read_file(APP_JS)

    assert "download-pdf-button" in source
    assert "pdf_path" in source


def test_download_endpoint_is_used():
    source = read_file(APP_JS)

    assert "/api/resume/download?filename=" in source


# ---------------------------------------------------------------------------
# FINAL GENERATION RESPONSE
# ---------------------------------------------------------------------------

def test_frontend_consumes_document_path():
    source = read_file(APP_JS)

    assert "window.resumeGenerationResult" in source
    assert "result.document_path" in source


def test_frontend_consumes_pdf_path():
    source = read_file(APP_JS)

    assert "window.resumeGenerationResult" in source
    assert "result.pdf_path" in source


def test_frontend_consumes_ats_evaluation():
    source = read_file(APP_JS)

    assert "data.ats_evaluation" in source


def test_frontend_consumes_document_validation():
    source = read_file(APP_JS)

    assert "data.document_validation" in source


# ---------------------------------------------------------------------------
# BACKEND / FRONTEND CONTRACT
# ---------------------------------------------------------------------------

def test_generation_route_returns_document_paths():
    source = read_file(GENERATION_ROUTES)

    assert '"document_path"' in source
    assert '"pdf_path"' in source


def test_generation_route_returns_ats_evaluation():
    source = read_file(GENERATION_ROUTES)

    assert '"ats_evaluation"' in source


def test_generation_route_returns_document_validation():
    source = read_file(GENERATION_ROUTES)

    assert '"document_validation"' in source


# ---------------------------------------------------------------------------
# COMPLETE FRONTEND FLOW
# ---------------------------------------------------------------------------

def test_complete_generation_ui_flow_is_connected():
    html = read_file(INDEX_HTML)
    js = read_file(APP_JS)
    routes = read_file(GENERATION_ROUTES)

    # Input layer
    assert 'id="resume-template"' in html

    # Generation layer
    assert "/api/resume/generate" in js
    assert "resumeTemplateInput.value" in js

    # Progress layer
    assert "updateGenerationProgress" in js

    # Results layer
    assert "displayGenerationATSResults" in js
    assert "displayGenerationValidation" in js

    # Download layer
    assert 'id="download-resume-button"' in html
    assert 'id="download-pdf-button"' in html
    assert "/api/resume/download?filename=" in js

    # Backend contract
    assert '"document_path"' in routes
    assert '"pdf_path"' in routes
    assert '"ats_evaluation"' in routes
    assert '"document_validation"' in routes