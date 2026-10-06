from pathlib import Path

from app import create_app
from app.ats_analyzer import analyze_resume_against_job
from app.final_ats_validation import (
    compare_ats_results,
    run_ats_safety_gate,
    summarize_ats_delta,
)


def create_test_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def sample_resume_text():
    return """
    Alex Johnson
    alex@example.com

    AI/ML Engineer

    SUMMARY
    AI/ML Engineer with experience in Python, Machine Learning,
    SQL, Pandas and Generative AI.

    SKILLS
    Python
    Machine Learning
    SQL
    Pandas
    Generative AI

    EXPERIENCE
    AI/ML Engineer - Example Technologies - 2024-2025
    Built machine learning applications using Python and SQL.
    Developed data processing workflows with Pandas.

    PROJECTS
    AI Resume Analyzer
    Built a resume analysis platform using Python,
    Machine Learning and SQL.

    EDUCATION
    B.Tech - Computer Science - Example University - 2024
    """


def sample_job_description():
    return """
    We are looking for an AI/ML Engineer with experience in:

    Python
    Machine Learning
    SQL
    Pandas
    Generative AI
    Retrieval-Augmented Generation

    The candidate should build production-ready AI applications,
    develop machine learning solutions and work with
    retrieval-augmented generation workflows.
    """


def sample_resume_data():
    return {
        "personal_info": {
            "name": "Alex Johnson",
            "email": "alex@example.com",
        },
        "summary": (
            "AI/ML Engineer with experience in Python, Machine Learning, "
            "SQL, Pandas and Generative AI."
        ),
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
            "Pandas",
            "Generative AI",
        ],
        "experience": [
            {
                "job_title": "AI/ML Engineer",
                "company": "Example Technologies",
                "dates": "2024-2025",
                "description": (
                    "Built machine learning applications using Python "
                    "and SQL. Developed data processing workflows "
                    "with Pandas."
                ),
            }
        ],
        "projects": [
            {
                "name": "AI Resume Analyzer",
                "description": (
                    "Built a resume analysis platform using Python, "
                    "Machine Learning and SQL."
                ),
            }
        ],
        "education": [
            {
                "degree": "B.Tech",
                "field": "Computer Science",
                "institution": "Example University",
                "year": "2024",
            }
        ],
        "certifications": [],
    }


def test_original_resume_can_be_ats_analyzed():
    result = analyze_resume_against_job(
        sample_resume_data(),
        sample_job_description(),
    )

    assert isinstance(result, dict)
    assert "ats_score" in result
    assert isinstance(result["ats_score"], (int, float))
    assert 0 <= result["ats_score"] <= 100

    assert "skills" in result
    assert "matched" in result["skills"]
    assert "missing" in result["skills"]


def test_original_resume_has_expected_ats_structure():
    result = analyze_resume_against_job(
        sample_resume_data(),
        sample_job_description(),
    )

    assert "experience" in result
    assert "qualifications" in result
    assert "keywords" in result

    assert isinstance(result["skills"]["matched"], list)
    assert isinstance(result["skills"]["missing"], list)


def test_generated_resume_can_be_ats_analyzed():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": sample_resume_text(),
                "resume_data": sample_resume_data(),
                "job_description": sample_job_description(),
                "target_pages": 1,
                "template": "ats_clean",
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert "final_resume" in data

    generated_resume = data["final_resume"]

    assert generated_resume is not None
    assert str(generated_resume).strip()


def test_before_after_ats_comparison_contract():
    before = analyze_resume_against_job(
        sample_resume_data(),
        sample_job_description(),
    )

    after = dict(before)

    comparison = compare_ats_results(
        before,
        after,
    )

    assert comparison.before_score == before["ats_score"]
    assert comparison.after_score == after["ats_score"]
    assert comparison.score_delta == 0
    assert comparison.score_regression is False


def test_before_after_summary_is_generated():
    before = analyze_resume_against_job(
        sample_resume_data(),
        sample_job_description(),
    )

    after = dict(before)

    comparison = compare_ats_results(
        before,
        after,
    )

    summary = summarize_ats_delta(comparison)

    assert summary.score_delta == 0
    assert summary.overall_status == "unchanged"


def test_ats_safety_gate_accepts_valid_before_after_result():
    before = analyze_resume_against_job(
        sample_resume_data(),
        sample_job_description(),
    )

    after = dict(before)

    comparison = compare_ats_results(
        before,
        after,
    )

    result = run_ats_safety_gate(
        comparison,
        sample_resume_text(),
    )

    assert result.passed is True
    assert result.score_valid is True
    assert result.no_score_regression is True
    assert result.no_lost_skills is True
    assert result.no_lost_keywords is True
    assert result.component_scores_valid is True
    assert result.content_extractable is True


def test_generated_resume_contains_candidate_content():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": sample_resume_text(),
                "resume_data": sample_resume_data(),
                "job_description": sample_job_description(),
                "target_pages": 1,
                "template": "ats_clean",
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    generated_resume = str(
        data["final_resume"]
    ).lower()

    assert "python" in generated_resume
    assert "machine learning" in generated_resume


def test_generated_document_exists_for_ats_pipeline():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": sample_resume_text(),
                "resume_data": sample_resume_data(),
                "job_description": sample_job_description(),
                "target_pages": 1,
                "template": "ats_clean",
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    document_path = Path(data["document_path"])

    assert document_path.is_file()
    assert document_path.stat().st_size > 0
