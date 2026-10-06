"""
Phase 16.6 - Download Experience UI Tests

Tests the frontend download contract for generated DOCX and PDF
resume documents.
"""

from pathlib import Path


APP_JS_PATH = Path("frontend/static/js/app.js")
INDEX_HTML_PATH = Path("frontend/templates/index.html")


def load_app_js():
    """Load the current frontend JavaScript source."""
    return APP_JS_PATH.read_text(encoding="utf-8")


def load_index_html():
    """Load the current frontend HTML source."""
    return INDEX_HTML_PATH.read_text(encoding="utf-8")


def test_app_js_exists():
    """The main frontend JavaScript file must exist."""
    assert APP_JS_PATH.exists()


def test_index_html_exists():
    """The main frontend HTML file must exist."""
    assert INDEX_HTML_PATH.exists()


def test_docx_download_button_exists():
    """The DOCX download button must exist."""
    source = load_index_html()

    assert 'id="download-resume-button"' in source
    assert "Download DOCX" in source


def test_pdf_download_button_exists():
    """The PDF download button must exist."""
    source = load_index_html()

    assert 'id="download-pdf-button"' in source
    assert "Download PDF" in source


def test_generation_download_container_exists():
    """The generation download container must exist."""
    source = load_index_html()

    assert 'id="generation-download"' in source


def test_pdf_download_dom_reference_exists():
    """The JavaScript must reference the PDF download button."""
    source = load_app_js()

    assert "downloadPdfButton" in source
    assert 'getElementById(' in source
    assert '"download-pdf-button"' in source


def test_docx_path_is_supported():
    """The frontend must use document_path for DOCX downloads."""
    source = load_app_js()

    assert "result.document_path" in source


def test_pdf_path_is_supported():
    """The frontend must use pdf_path for PDF downloads."""
    source = load_app_js()

    assert "result.pdf_path" in source


def test_download_endpoint_is_used():
    """Downloads must use the backend resume download endpoint."""
    source = load_app_js()

    assert "/api/resume/download?filename=" in source


def test_docx_download_extracts_filename():
    """The DOCX path must be converted into a filename."""
    source = load_app_js()

    assert "result.document_path" in source
    assert ".split(/[\\\\/]/)" in source


def test_pdf_download_extracts_filename():
    """The PDF path must be converted into a filename."""
    source = load_app_js()

    assert "result.pdf_path" in source
    assert ".split(/[\\\\/]/)" in source


def test_docx_download_handles_missing_result():
    """DOCX download must handle a missing generation result."""
    source = load_app_js()

    assert "Please generate an optimized resume first." in source
    assert "result.document_path" in source


def test_pdf_download_handles_missing_result():
    """PDF download must handle a missing generation result."""
    source = load_app_js()

    assert "Please generate an optimized resume first." in source
    assert "result.pdf_path" in source


def test_docx_download_has_click_handler():
    """The DOCX download button must have a click handler."""
    source = load_app_js()

    assert "downloadResumeButton.addEventListener(" in source
    assert '"click"' in source


def test_pdf_download_has_click_handler():
    """The PDF download button must have a click handler."""
    source = load_app_js()

    assert "downloadPdfButton.addEventListener(" in source
    assert '"click"' in source


def test_download_uses_encoded_filename():
    """Download filenames must be URL encoded."""
    source = load_app_js()

    assert "encodeURIComponent(" in source


def test_download_redirects_to_backend():
    """The browser must navigate to the generated download URL."""
    source = load_app_js()

    assert "window.location.href" in source


def test_generation_download_is_shown_after_generation():
    """The download container must be shown after successful generation."""
    source = load_app_js()

    assert 'generationDownload.style.display = "block"' in source


def test_both_generated_paths_are_supported():
    """Both DOCX and PDF generated paths must be available."""
    source = load_app_js()

    assert "result.document_path" in source
    assert "result.pdf_path" in source


def test_download_endpoint_is_shared():
    """
    DOCX and PDF downloads should use the same backend download
    endpoint.
    """
    source = load_app_js()

    endpoint = "/api/resume/download?filename="

    assert source.count(endpoint) >= 2