from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STYLE_CSS = (
    PROJECT_ROOT
    / "frontend"
    / "static"
    / "css"
    / "style.css"
)

INDEX_HTML = (
    PROJECT_ROOT
    / "frontend"
    / "templates"
    / "index.html"
)


def read_css():
    return STYLE_CSS.read_text(encoding="utf-8")


def read_html():
    return INDEX_HTML.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# RESPONSIVE BREAKPOINTS
# ---------------------------------------------------------------------------

def test_responsive_breakpoints_exist():
    source = read_css()

    assert "@media (max-width: 800px)" in source
    assert "@media (max-width: 600px)" in source
    assert "@media (max-width: 450px)" in source


def test_component_scores_have_mobile_layout():
    source = read_css()

    assert "grid-template-columns: 1fr 1fr" in source
    assert "grid-template-columns: 1fr;" in source


def test_match_analysis_has_mobile_layout():
    source = read_css()

    assert ".match-analysis" in source
    assert "grid-template-columns: 1fr;" in source


def test_insights_have_mobile_layout():
    source = read_css()

    assert ".insights" in source
    assert "grid-template-columns: 1fr;" in source


def test_resume_quality_components_are_responsive():
    source = read_css()

    assert ".resume-quality-components" in source
    assert "grid-template-columns: 1fr 1fr" in source
    assert "grid-template-columns: 1fr;" in source


# ---------------------------------------------------------------------------
# ATS RESPONSIVE LAYOUT
# ---------------------------------------------------------------------------

def test_ats_responsive_layout_exists():
    source = read_css()

    assert "/* Responsive ATS layout */" in source
    assert ".ats-comparison-summary" in source
    assert ".ats-gap-comparison" in source


def test_ats_comparison_collapses_on_tablet():
    source = read_css()

    assert "@media (max-width: 800px)" in source
    assert "grid-template-columns: 1fr 1fr" in source


def test_ats_gap_comparison_collapses_on_tablet():
    source = read_css()

    assert ".ats-gap-comparison" in source
    assert "grid-template-columns: 1fr;" in source


def test_ats_comparison_collapses_on_mobile():
    source = read_css()

    assert "@media (max-width: 600px)" in source
    assert ".ats-comparison-summary" in source


def test_ats_component_rows_stack_on_mobile():
    source = read_css()

    assert ".ats-component-score-row" in source
    assert "grid-template-columns: 1fr;" in source


def test_ats_safety_status_stacks_on_mobile():
    source = read_css()

    assert ".ats-safety-status" in source
    assert "flex-direction: column" in source


# ---------------------------------------------------------------------------
# GENERATION UI
# ---------------------------------------------------------------------------

def test_generation_progress_uses_flexible_layout():
    source = read_css()

    assert ".generation-progress-header" in source
    assert "display: flex" in source


def test_generation_steps_stack_vertically():
    source = read_css()

    assert ".generation-steps" in source
    assert "flex-direction: column" in source


# ---------------------------------------------------------------------------
# FORM AND BUTTON USABILITY
# ---------------------------------------------------------------------------

def test_form_groups_have_consistent_spacing():
    source = read_css()

    assert ".form-group" in source
    assert "margin-bottom:" in source


def test_form_labels_are_block_elements():
    source = read_css()

    assert ".form-group label" in source
    assert "display: block" in source


def test_buttons_are_full_width():
    source = read_css()

    assert "button {" in source
    assert "width: 100%" in source


def test_buttons_have_interactive_hover_state():
    source = read_css()

    assert "button:hover" in source


# ---------------------------------------------------------------------------
# PROFESSIONAL VISUAL STRUCTURE
# ---------------------------------------------------------------------------

def test_analysis_cards_have_visual_structure():
    source = read_css()

    assert ".analysis-card" in source
    assert "border-radius:" in source
    assert "box-shadow:" in source


def test_score_cards_have_visual_structure():
    source = read_css()

    assert ".score-card" in source
    assert "background: white" in source
    assert "border-radius:" in source


def test_match_cards_have_visual_structure():
    source = read_css()

    assert ".match-card" in source
    assert "box-shadow:" in source


def test_insight_cards_have_visual_structure():
    source = read_css()

    assert ".insight-card" in source
    assert "box-shadow:" in source


# ---------------------------------------------------------------------------
# TEMPLATE / GENERATION UI HTML
# ---------------------------------------------------------------------------

def test_template_selector_is_present_in_final_ui():
    source = read_html()

    assert 'id="resume-template"' in source


def test_generation_download_controls_are_present():
    source = read_html()

    assert 'id="generation-download"' in source
    assert 'id="download-resume-button"' in source
    assert 'id="download-pdf-button"' in source


def test_generation_progress_elements_are_present():
    source = read_html()

    assert 'id="generation-progress"' in source
    assert 'id="generation-status-message"' in source


# ---------------------------------------------------------------------------
# COMPLETE RESPONSIVE UI CONTRACT
# ---------------------------------------------------------------------------

def test_responsive_ui_contract():
    css = read_css()
    html = read_html()

    required_css = [
        "@media (max-width: 800px)",
        "@media (max-width: 600px)",
        "@media (max-width: 450px)",
        ".generation-progress-header",
        ".generation-steps",
        ".ats-comparison-summary",
        ".ats-component-score-row",
        ".ats-gap-comparison",
        ".ats-safety-status",
    ]

    for pattern in required_css:
        assert pattern in css

    required_html = [
        'id="resume-template"',
        'id="generation-download"',
        'id="download-resume-button"',
        'id="download-pdf-button"',
        'id="generation-progress"',
    ]

    for pattern in required_html:
        assert pattern in html