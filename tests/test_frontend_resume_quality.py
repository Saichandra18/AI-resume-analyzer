from app import create_app


def test_home_page_contains_resume_quality_section():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    assert b"resume-quality" in response.data
    assert b"resume-quality-score" in response.data
    assert b"resume-quality-components" in response.data
    assert b"resume-quality-missing" in response.data


def test_home_page_contains_resume_quality_labels():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert b"Resume Completeness" in response.data
    assert b"Name" in response.data
    assert b"Email" in response.data
    assert b"Phone" in response.data
    assert b"Skills" in response.data
    assert b"Education" in response.data
    assert b"Experience" in response.data
    assert b"Projects" in response.data
    assert b"Certifications" in response.data