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

GENERATION_SERVICE = (
    PROJECT_ROOT
    / "app"
    / "resume_generation_service.py"
)


def read_file(path):
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# HTML TEMPLATE SELECTOR
# ---------------------------------------------------------------------------

def test_template_selector_exists():
    source = read_file(INDEX_HTML)

    assert 'id="resume-template"' in source
    assert 'name="template"' in source


def test_template_selector_has_default_template():
    source = read_file(INDEX_HTML)

    assert '<option value="default">' in source


def test_template_selector_has_ats_clean_template():
    source = read_file(INDEX_HTML)

    assert '<option value="ats_clean" selected>' in source


def test_template_selector_has_modern_template():
    source = read_file(INDEX_HTML)

    assert '<option value="modern">' in source


def test_template_selector_has_technical_template():
    source = read_file(INDEX_HTML)

    assert '<option value="technical">' in source


def test_template_selector_has_all_expected_templates():
    source = read_file(INDEX_HTML)

    expected_templates = [
        'value="default"',
        'value="ats_clean"',
        'value="modern"',
        'value="technical"',
    ]

    for template in expected_templates:
        assert template in source


def test_ats_clean_is_selected_by_default():
    source = read_file(INDEX_HTML)

    assert '<option value="ats_clean" selected>' in source


# ---------------------------------------------------------------------------
# FRONTEND JAVASCRIPT
# ---------------------------------------------------------------------------

def test_app_js_reads_template_selector():
    source = read_file(APP_JS)

    assert 'getElementById(' in source
    assert '"resume-template"' in source


def test_generation_payload_contains_template():
    source = read_file(APP_JS)

    assert "template:" in source
    assert "resumeTemplateInput.value" in source


def test_template_is_sent_in_generation_request():
    source = read_file(APP_JS)

    template_position = source.find("resumeTemplateInput.value")
    generate_position = source.find("/api/resume/generate")

    assert template_position != -1
    assert generate_position != -1

    # The template field must occur in the generation workflow.
    assert abs(template_position - generate_position) < 5000


# ---------------------------------------------------------------------------
# BACKEND ROUTE
# ---------------------------------------------------------------------------

def test_generation_route_reads_template():
    source = read_file(GENERATION_ROUTES)

    assert 'data.get(' in source
    assert '"template"' in source


def test_generation_route_defaults_template_to_ats_clean():
    source = read_file(GENERATION_ROUTES)

    assert '"template",' in source
    assert '"ats_clean"' in source


def test_generation_route_validates_template_type():
    source = read_file(GENERATION_ROUTES)

    assert "isinstance(template, str)" in source
    assert "template must be a string." in source


def test_generation_route_strips_template():
    source = read_file(GENERATION_ROUTES)

    assert "template = template.strip()" in source


def test_generation_route_defaults_empty_template():
    source = read_file(GENERATION_ROUTES)

    assert "if not template:" in source
    assert 'template = "ats_clean"' in source


def test_generation_route_passes_template_to_service():
    source = read_file(GENERATION_ROUTES)

    assert "template=template" in source


# ---------------------------------------------------------------------------
# GENERATION SERVICE
# ---------------------------------------------------------------------------

def test_generation_service_accepts_template():
    source = read_file(GENERATION_SERVICE)

    assert 'template="default"' in source


def test_generation_service_passes_template_to_docx_renderer():
    source = read_file(GENERATION_SERVICE)

    assert "render_final_resume(" in source
    assert "template=template" in source


def test_generation_service_passes_template_to_pdf_renderer():
    source = read_file(GENERATION_SERVICE)

    assert "render_final_resume_pdf(" in source
    assert "template=template" in source


# ---------------------------------------------------------------------------
# END-TO-END TEMPLATE FLOW
# ---------------------------------------------------------------------------

def test_template_flow_exists_across_frontend_backend_and_service():
    html = read_file(INDEX_HTML)
    js = read_file(APP_JS)
    routes = read_file(GENERATION_ROUTES)
    service = read_file(GENERATION_SERVICE)

    assert 'id="resume-template"' in html
    assert "resumeTemplateInput.value" in js
    assert '"template"' in routes
    assert "template=template" in routes
    assert 'template="default"' in service
    assert "template=template" in service