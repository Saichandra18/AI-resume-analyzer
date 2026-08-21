from app import create_app


def test_home_page_contains_complete_results_dashboard():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    html = response.data

    # ATS score
    assert b"ats-score-value" in html

    # Component scores
    assert b"skills-score" in html
    assert b"experience-score" in html
    assert b"qualifications-score" in html
    assert b"keywords-score" in html

    # Match analysis
    assert b"matched-skills" in html
    assert b"missing-skills" in html
    assert b"matched-qualifications" in html
    assert b"missing-qualifications" in html
    assert b"matched-keywords" in html
    assert b"missing-keywords" in html

    # Insights
    assert b"strengths-list" in html
    assert b"weaknesses-list" in html
    assert b"recommendations-list" in html


def test_home_page_loads_frontend_javascript():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    assert (
        b'/static/js/app.js' in response.data
    )