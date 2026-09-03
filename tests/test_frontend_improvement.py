from pathlib import Path

from app import create_app


BASE_DIR = Path(__file__).resolve().parents[1]

INDEX_PATH = (
    BASE_DIR
    / "frontend"
    / "templates"
    / "index.html"
)

APP_JS_PATH = (
    BASE_DIR
    / "frontend"
    / "static"
    / "js"
    / "app.js"
)


def test_home_page_contains_improvement_suggestions_section():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    assert b"resume-improvement" in response.data
    assert b"resume-improvement-suggestions" in response.data
    assert b"Resume Improvement Suggestions" in response.data


def test_home_page_contains_improvement_suggestion_fields():
    html = INDEX_PATH.read_text(
        encoding="utf-8"
    )

    assert 'id="resume-improvement"' in html
    assert 'id="resume-improvement-suggestions"' in html


def test_app_js_contains_improvement_suggestion_labels():
    javascript = APP_JS_PATH.read_text(
        encoding="utf-8"
    )

    assert "Current Text" in javascript
    assert "How to Improve" in javascript
    assert "Why" in javascript

def test_app_js_contains_improvement_suggestion_renderer():
    javascript = APP_JS_PATH.read_text(
        encoding="utf-8"
    )

    assert "displayImprovementSuggestions" in javascript
    assert "improvement_suggestions" in javascript
    assert "current_text" in javascript
    assert "suggestion" in javascript
    assert "reason" in javascript


def test_app_js_calls_improvement_suggestion_renderer():
    javascript = APP_JS_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "displayImprovementSuggestions(data);"
        in javascript
    )

    def test_app_js_uses_improvement_suggestion_data():
        javascript = APP_JS_PATH.read_text(
            encoding="utf-8"
        )

        assert "data.improvement_suggestions" in javascript
        assert "suggestion.type" in javascript
        assert "suggestion.priority" in javascript
        assert "suggestion.current_text" in javascript
        assert "suggestion.suggestion" in javascript
        assert "suggestion.reason" in javascript


def test_app_js_handles_empty_improvement_suggestions():
    javascript = APP_JS_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "No improvement suggestions available."
        in javascript
    )


def test_app_js_handles_missing_current_text():
    javascript = APP_JS_PATH.read_text(
        encoding="utf-8"
    )

    assert "if (suggestion.current_text)" in javascript

def test_app_js_supports_ats_gap_suggestion_types():
    javascript = APP_JS_PATH.read_text(
        encoding="utf-8"
    )

    assert "skill" in javascript
    assert "keyword" in javascript
    assert "qualification" in javascript

def test_app_js_defines_format_label_helper():
    javascript = APP_JS_PATH.read_text(
        encoding="utf-8"
    )

    assert "function formatLabel(" in javascript