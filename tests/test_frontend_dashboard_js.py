from pathlib import Path


def test_dashboard_javascript_contains_score_elements():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    assert "ats-score-value" in javascript
    assert "skills-score" in javascript
    assert "experience-score" in javascript
    assert "qualifications-score" in javascript
    assert "keywords-score" in javascript


def test_dashboard_javascript_displays_results():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    assert "atsAnalysisResult" in javascript
    assert "results" in javascript