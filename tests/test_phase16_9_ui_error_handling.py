from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

APP_JS = (
    PROJECT_ROOT
    / "frontend"
    / "static"
    / "js"
    / "app.js"
)


def read_app_js():
    return APP_JS.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# INPUT VALIDATION
# ---------------------------------------------------------------------------

def test_generation_validates_resume_file():
    source = read_app_js()

    assert "if (!resumeFile)" in source
    assert "Please select a resume." in source


def test_generation_validates_job_description():
    source = read_app_js()

    assert "if (!jobDescription)" in source
    assert "Please enter a job description." in source


# ---------------------------------------------------------------------------
# API ERROR HANDLING
# ---------------------------------------------------------------------------

def test_generation_checks_response_status():
    source = read_app_js()

    assert "if (!response.ok)" in source


def test_generation_uses_backend_error_message():
    source = read_app_js()

    assert "data.message" in source


def test_generation_has_fallback_error_message():
    source = read_app_js()

    assert "Resume generation failed." in source


def test_generation_has_catch_handler():
    source = read_app_js()

    assert "} catch (error)" in source


def test_generation_logs_errors():
    source = read_app_js()

    assert '"Resume generation error:"' in source
    assert "console.error" in source


def test_generation_displays_error_message():
    source = read_app_js()

    assert "error.message" in source
    assert "Could not generate optimized resume." in source


# ---------------------------------------------------------------------------
# GENERATION BUTTON STATE
# ---------------------------------------------------------------------------

def test_generation_disables_button_during_request():
    source = read_app_js()

    assert "generateResumeButton.disabled" in source
    assert "generateResumeButton.disabled = true" in source


def test_generation_restores_button_after_request():
    source = read_app_js()

    assert "generateResumeButton.disabled =" in source
    assert "false;" in source


def test_generation_uses_finally_for_button_cleanup():
    source = read_app_js()

    assert "} finally {" in source


# ---------------------------------------------------------------------------
# DOWNLOAD ERROR HANDLING
# ---------------------------------------------------------------------------

def test_docx_download_checks_generation_result():
    source = read_app_js()

    assert "!result || !result.document_path" in source


def test_docx_download_has_missing_result_message():
    source = read_app_js()

    assert "Please generate an optimized resume first." in source


def test_docx_download_checks_filename():
    source = read_app_js()

    assert "if (!filename)" in source
    assert "The generated DOCX file could not be identified." in source


def test_pdf_download_checks_generation_result():
    source = read_app_js()

    assert "!result || !result.pdf_path" in source


def test_pdf_download_checks_filename():
    source = read_app_js()

    assert "The generated PDF file could not be identified." in source


# ---------------------------------------------------------------------------
# ERROR RESPONSE SAFETY
# ---------------------------------------------------------------------------

def test_generation_parses_json_before_using_error_message():
    source = read_app_js()

    json_position = source.find("await response.json()")
    status_position = source.find("if (!response.ok)")

    assert json_position != -1
    assert status_position != -1
    assert json_position < status_position


def test_generation_error_handling_is_inside_try_block():
    source = read_app_js()

    try_position = source.find("try {")
    catch_position = source.find("} catch (error)")

    assert try_position != -1
    assert catch_position != -1
    assert try_position < catch_position


# ---------------------------------------------------------------------------
# VALIDATION ERROR DISPLAY
# ---------------------------------------------------------------------------

def test_validation_handles_missing_errors_array():
    source = read_app_js()

    assert "Array.isArray(validation.errors)" in source


def test_validation_handles_empty_errors():
    source = read_app_js()

    assert "errors.length === 0" in source
    assert "No validation errors." in source


def test_validation_displays_individual_errors():
    source = read_app_js()

    assert "errors.forEach" in source
    assert "item.textContent = error" in source


def test_validation_handles_warnings():
    source = read_app_js()

    assert "validation.warnings" in source


# ---------------------------------------------------------------------------
# COMPLETE ERROR-HANDLING CONTRACT
# ---------------------------------------------------------------------------

def test_generation_error_handling_contract():
    source = read_app_js()

    required_patterns = [
        "if (!resumeFile)",
        "if (!jobDescription)",
        "if (!response.ok)",
        "data.message",
        "} catch (error)",
        "console.error",
        "error.message",
        "} finally {",
        "generateResumeButton.disabled",
        "!result || !result.document_path",
        "!result || !result.pdf_path",
    ]

    for pattern in required_patterns:
        assert pattern in source