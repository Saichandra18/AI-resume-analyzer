"""
Phase 16.5 - Validation Results UI Tests

Tests the frontend validation response contract used by
displayGenerationValidation() in frontend/static/app.js.
"""

import json
from pathlib import Path


APP_JS_PATH = Path("frontend/static/js/app.js")


def load_app_js():
    """Load the current frontend JavaScript source."""
    return APP_JS_PATH.read_text(encoding="utf-8")


def test_app_js_exists():
    """The main frontend JavaScript file must exist."""
    assert APP_JS_PATH.exists()


def test_validation_dom_references_exist():
    """Validation UI DOM references must exist in app.js."""
    source = load_app_js()

    required_references = [
        "generationValidationResults",
        "generationValidationStatus",
        "generationValidationDocxFile",
        "generationValidationDocxReadable",
        "generationValidationDocxText",
        "generationValidationDocxContent",
        "generationValidationDocxHeadings",
        "generationValidationPdfFile",
        "generationValidationPdfReadable",
        "generationValidationPdfText",
        "generationValidationPdfContent",
        "generationValidationPdfHeadings",
        "generationValidationTargetPages",
        "generationValidationActualPages",
        "generationValidationPageMatch",
        "generationValidationErrors",
        "generationValidationWarnings",
    ]

    for reference in required_references:
        assert reference in source


def test_display_generation_validation_function_exists():
    """The validation rendering function must exist."""
    source = load_app_js()

    assert "function displayGenerationValidation(validation)" in source


def test_validation_overall_status_is_supported():
    """The UI must read the overall validation.valid field."""
    source = load_app_js()

    assert "validation.valid === true" in source
    assert '"Passed"' in source
    assert '"Failed"' in source


def test_docx_validation_fields_are_supported():
    """The UI must render all required DOCX validation fields."""
    source = load_app_js()

    required_fields = [
        "docx.file_exists",
        "docx.readable",
        "docx.text_present",
        "docx.required_content_present",
        "docx.standard_headings_present",
    ]

    for field in required_fields:
        assert field in source


def test_pdf_validation_fields_are_supported():
    """The UI must render all required PDF validation fields."""
    source = load_app_js()

    required_fields = [
        "pdf.file_exists",
        "pdf.readable",
        "pdf.text_present",
        "pdf.required_content_present",
        "pdf.standard_headings_present",
    ]

    for field in required_fields:
        assert field in source


def test_pdf_page_count_validation_is_supported():
    """The UI must render target, actual, and page-match values."""
    source = load_app_js()

    required_fields = [
        "pdf.target_pages",
        "pdf.actual_pages",
        "pdf.page_count_match",
    ]

    for field in required_fields:
        assert field in source


def test_validation_errors_are_rendered():
    """The UI must render validation errors."""
    source = load_app_js()

    assert "validation.errors" in source
    assert "No validation errors." in source
    assert "errors.forEach" in source


def test_validation_warnings_are_rendered():
    """The UI must render validation warnings."""
    source = load_app_js()

    assert "validation.warnings" in source
    assert "No validation warnings." in source
    assert "warnings.forEach" in source


def test_missing_validation_data_is_handled():
    """The UI must safely handle a missing validation response."""
    source = load_app_js()

    assert "if (!validation)" in source
    assert 'generationValidationResults.style.display = "none"' in source


def test_missing_docx_and_pdf_objects_are_handled():
    """The UI must safely handle missing DOCX/PDF objects."""
    source = load_app_js()

    assert "validation.docx || {}" in source
    assert "validation.pdf || {}" in source


def test_validation_results_are_shown_after_processing():
    """The validation results container must be displayed after processing."""
    source = load_app_js()

    assert (
        'generationValidationResults.style.display = "block"'
        in source
    )


def test_generation_response_uses_document_validation():
    """
    The generation flow must pass document_validation into
    the validation display function.
    """
    source = load_app_js()

    assert "displayGenerationValidation(" in source
    assert "data.document_validation" in source


def test_generation_ats_results_receives_document_validation():
    """
    Existing ATS results rendering must continue receiving
    document_validation.
    """
    source = load_app_js()

    assert "displayGenerationATSResults(" in source
    assert "data.ats_evaluation" in source
    assert "data.document_validation" in source

def test_validation_display_occurs_after_ats_display():
    """
    Validation UI rendering must occur after ATS results rendering
    in the generation flow.
    """
    source = load_app_js()

    generation_start = source.find(
        "window.resumeGenerationResult"
    )

    assert generation_start != -1

    ats_position = source.find(
        "displayGenerationATSResults(",
        generation_start
    )

    validation_position = source.find(
        "displayGenerationValidation(",
        ats_position
    )

    assert ats_position != -1
    assert validation_position != -1
    assert validation_position > ats_position
def test_expected_document_validation_payload_structure():
    """
    Verify the representative backend payload structure expected
    by the Phase 16.5 frontend.
    """
    validation = {
        "valid": True,
        "ats_safety": {
            "passed": True,
        },
        "docx": {
            "file_exists": True,
            "readable": True,
            "text_present": True,
            "required_content_present": True,
            "standard_headings_present": True,
        },
        "pdf": {
            "file_exists": True,
            "readable": True,
            "text_present": True,
            "required_content_present": True,
            "standard_headings_present": True,
            "target_pages": 2,
            "actual_pages": 2,
            "page_count_match": True,
        },
        "errors": [],
        "warnings": [],
    }

    serialized = json.dumps(validation)
    restored = json.loads(serialized)

    assert restored["valid"] is True
    assert restored["ats_safety"]["passed"] is True

    assert restored["docx"]["file_exists"] is True
    assert restored["docx"]["readable"] is True
    assert restored["docx"]["text_present"] is True
    assert restored["docx"]["required_content_present"] is True
    assert restored["docx"]["standard_headings_present"] is True

    assert restored["pdf"]["file_exists"] is True
    assert restored["pdf"]["readable"] is True
    assert restored["pdf"]["text_present"] is True
    assert restored["pdf"]["required_content_present"] is True
    assert restored["pdf"]["standard_headings_present"] is True

    assert restored["pdf"]["target_pages"] == 2
    assert restored["pdf"]["actual_pages"] == 2
    assert restored["pdf"]["page_count_match"] is True

    assert restored["errors"] == []
    assert restored["warnings"] == []


def test_failed_validation_payload_is_supported():
    """The frontend contract must also support a failed validation."""
    validation = {
        "valid": False,
        "docx": {
            "file_exists": True,
            "readable": False,
            "text_present": False,
            "required_content_present": False,
            "standard_headings_present": False,
        },
        "pdf": {
            "file_exists": True,
            "readable": True,
            "text_present": True,
            "required_content_present": False,
            "standard_headings_present": True,
            "target_pages": 1,
            "actual_pages": 2,
            "page_count_match": False,
        },
        "errors": [
            "DOCX document is not readable.",
            "Required content is missing.",
        ],
        "warnings": [
            "PDF page count differs from target.",
        ],
    }

    assert validation["valid"] is False
    assert len(validation["errors"]) == 2
    assert len(validation["warnings"]) == 1
    assert validation["pdf"]["page_count_match"] is False