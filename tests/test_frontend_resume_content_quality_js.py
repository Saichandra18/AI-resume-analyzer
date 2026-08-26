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


def test_resume_content_quality_javascript_contains_elements():
    javascript = get_javascript()

    assert "resume-content-quality-score" in javascript
    assert "resume-content-quality-signals" in javascript
    assert "resume-content-quality-warnings" in javascript
    assert "resume-content-quality-recommendations" in javascript


def test_resume_content_quality_javascript_uses_api_data():
    javascript = get_javascript()

    assert "data.resume_content_quality" in javascript
    assert "resume_content_quality.score" in javascript
    assert "resume_content_quality.signals" in javascript
    assert "resume_content_quality.warnings" in javascript
    assert "resume_content_quality.recommendations" in javascript


def test_resume_content_quality_javascript_handles_all_signals():
    javascript = get_javascript()

    assert "contact_information" in javascript
    assert "quantified_achievements" in javascript
    assert "action_oriented_experience" in javascript
    assert "project_description" in javascript