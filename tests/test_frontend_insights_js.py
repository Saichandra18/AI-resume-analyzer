from pathlib import Path


def test_insights_javascript_contains_insight_elements():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    assert "strengths-list" in javascript
    assert "weaknesses-list" in javascript
    assert "recommendations-list" in javascript


def test_insights_javascript_uses_api_insight_data():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    assert "data.strengths" in javascript
    assert "data.weaknesses" in javascript
    assert "data.recommendations" in javascript

def test_insights_javascript_renders_object_descriptions():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    assert "value.description" in javascript
    assert "value.recommendation" in javascript

def test_insights_javascript_uses_canonical_keyword_labels():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    assert "Artificial Intelligence (AI)" in javascript
    assert "Machine Learning (ML)" in javascript
    assert "Generative AI (GenAI)" in javascript
    assert "Large Language Models (LLM)" in javascript
    assert "Retrieval Augmented Generation (RAG)" in javascript
    assert "Neural Networks" in javascript
    assert "CI/CD" in javascript

def test_insights_javascript_groups_mlops_before_ai_ml():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    mlops_position = javascript.index(
        '"MLOps & Production"'
    )
    ai_ml_position = javascript.index(
        '"AI/ML Foundation"'
    )

    assert mlops_position < ai_ml_position

def test_insights_javascript_contains_insight_grouping_categories():
    js_path = (
        Path(__file__).resolve().parents[1]
        / "frontend"
        / "static"
        / "js"
        / "app.js"
    )

    javascript = js_path.read_text(encoding="utf-8")

    assert "MLOps & Production" in javascript
    assert "Model Evaluation" in javascript
    assert "Engineering & Development" in javascript
    assert "Machine Learning Operations" in javascript
    assert "Model Validation" in javascript
    assert "LLMOps" in javascript