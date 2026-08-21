from pathlib import Path


def test_match_javascript_contains_match_elements():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    assert "matched-skills" in javascript
    assert "missing-skills" in javascript
    assert "matched-qualifications" in javascript
    assert "missing-qualifications" in javascript
    assert "matched-keywords" in javascript
    assert "missing-keywords" in javascript


def test_match_javascript_uses_api_match_data():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    assert "matched_skills" in javascript
    assert "missing_skills" in javascript
    assert "matched_qualifications" in javascript
    assert "missing_qualifications" in javascript
    assert "matched_keywords" in javascript
    assert "missing_keywords" in javascript

def test_match_javascript_groups_equivalent_keywords():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    assert "groupMatchedKeywords" in javascript
    assert "Artificial Intelligence (AI)" in javascript
    assert "Machine Learning (ML)" in javascript
    assert "Generative AI (GenAI)" in javascript
    assert "Large Language Models (LLM)" in javascript
    assert "Retrieval Augmented Generation (RAG)" in javascript
    assert "Neural Networks" in javascript
    assert "CI/CD" in javascript