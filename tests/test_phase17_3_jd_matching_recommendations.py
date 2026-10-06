from app import create_app

from app.ats_analyzer import analyze_resume_against_job
from app.recommendation_engine import generate_recommendations


def create_test_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def sample_resume_data():
    return {
        "personal_info": {
            "name": "Alex Johnson",
            "email": "alex@example.com",
        },
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
            "Pandas",
            "Flask",
            "Generative AI",
            "RAG",
        ],
        "education": [
            {
                "degree": "B.Tech",
                "institution": "Example University",
                "year": "2024",
            }
        ],
        "experience": [
            {
                "job_title": "AI/ML Engineer",
                "company": "Example Technologies",
                "dates": "2024 – 2025",
                "description": (
                    "Built machine learning and Generative AI "
                    "applications using Python and RAG."
                ),
            }
        ],
        "projects": [
            {
                "name": "AI Resume Analyzer",
                "description": (
                    "Built resume and job-description matching "
                    "using Python, SQL and RAG."
                ),
            }
        ],
        "certifications": [
            "Python Certification",
        ],
    }


def sample_job_description():
    return """
    We are looking for an AI/ML Engineer with experience in
    Python, machine learning, SQL, Generative AI and RAG.

    The candidate should have experience building AI applications,
    implementing retrieval-augmented generation workflows,
    working with structured data and developing production-ready
    Python applications.

    Experience with Docker, AWS and Kubernetes is preferred.
    """


def test_job_description_endpoint_accepts_valid_jd():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/job-description",
            json={
                "job_description": sample_job_description()
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert "job_description" in data
    assert "Python" in data["job_description"]


def test_job_description_endpoint_rejects_missing_body():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/job-description",
            json={},
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Request body must contain JSON data"


def test_job_description_endpoint_rejects_empty_jd():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/job-description",
            json={
                "job_description": "   "
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "empty" in data["message"].lower()


def test_resume_matches_job_description():
    resume_data = sample_resume_data()
    job_description = sample_job_description()

    result = analyze_resume_against_job(
        resume_data,
        job_description,
    )

    assert isinstance(result, dict)

    assert "ats_score" in result
    assert "skills" in result

    assert result["ats_score"] >= 0
    assert result["ats_score"] <= 100

    assert result["skills"]["matched"]


def test_matching_detects_missing_skills():
    resume_data = sample_resume_data()

    job_description = """
    We need an engineer with Python, machine learning,
    Kubernetes, AWS, Docker and Terraform experience.
    """

    result = analyze_resume_against_job(
        resume_data,
        job_description,
    )

    assert isinstance(result, dict)

    assert "skills" in result
    assert result["skills"]["missing"]

    missing_text = " ".join(
        str(item).lower()
        for item in result["skills"]["missing"]
    )

    assert (
        "kubernetes" in missing_text
        or "aws" in missing_text
        or "docker" in missing_text
        or "terraform" in missing_text
    )


def test_matching_detects_resume_strengths():
    resume_data = sample_resume_data()

    job_description = """
    We need an AI/ML Engineer with Python,
    machine learning, SQL, Generative AI and RAG.
    """

    result = analyze_resume_against_job(
        resume_data,
        job_description,
    )

    assert "skills" in result
    assert result["skills"]["matched"]

    matched_text = " ".join(
        str(item).lower()
        for item in result["skills"]["matched"]
    )

    assert (
        "python" in matched_text
        or "machine" in matched_text
        or "sql" in matched_text
    )


def test_recommendation_engine_returns_recommendations():
    resume_data = sample_resume_data()

    job_description = """
    We need Python, Machine Learning, Kubernetes,
    AWS, Docker and Terraform experience.
    """

    ats_result = analyze_resume_against_job(
        resume_data,
        job_description,
    )

    recommendations = generate_recommendations(
        ats_result
    )

    assert recommendations is not None

    if isinstance(recommendations, list):
        assert len(recommendations) > 0

    elif isinstance(recommendations, dict):
        assert recommendations


def test_complete_jd_to_recommendation_flow():
    resume_data = sample_resume_data()
    job_description = sample_job_description()

    ats_result = analyze_resume_against_job(
        resume_data,
        job_description,
    )

    assert ats_result
    assert "ats_score" in ats_result
    assert "skills" in ats_result

    recommendations = generate_recommendations(
        ats_result
    )

    assert recommendations is not None

    assert isinstance(
        recommendations,
        (list, dict),
    )