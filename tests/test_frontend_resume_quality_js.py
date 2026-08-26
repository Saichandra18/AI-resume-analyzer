from pathlib import Path


def get_javascript():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    return js_path.read_text(encoding="utf-8")


def test_resume_quality_javascript_contains_elements():
    javascript = get_javascript()

    assert "resume-quality-score" in javascript
    assert "resume-quality-components" in javascript
    assert "resume-quality-missing" in javascript


def test_resume_quality_javascript_uses_api_data():
    javascript = get_javascript()

    assert "data.resume_quality" in javascript
    assert "resume_quality.score" in javascript
    assert "resume_quality.components" in javascript
    assert "resume_quality.missing_sections" in javascript


def test_resume_quality_javascript_handles_optional_sections():
    javascript = get_javascript()

    assert "optional_sections" in javascript
    assert "certifications" in javascript