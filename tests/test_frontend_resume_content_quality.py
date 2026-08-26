from app import create_app


def test_home_page_contains_resume_content_quality_section():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    assert b"resume-content-quality" in response.data
    assert b"resume-content-quality-score" in response.data
    assert b"resume-content-quality-signals" in response.data
    assert b"resume-content-quality-warnings" in response.data
    assert b"resume-content-quality-recommendations" in response.data


def test_home_page_contains_resume_content_quality_labels():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert b"Resume Content Quality" in response.data
    assert b"Contact Information" in response.data
    assert b"Quantified Achievements" in response.data
    assert b"Action-Oriented Experience" in response.data
    assert b"Project Description" in response.data