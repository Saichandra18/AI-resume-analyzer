from app import create_app


def test_home_page_contains_results_dashboard():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    assert b"results" in response.data.lower()
    assert b"ats-score" in response.data.lower()
    assert b"component-scores" in response.data.lower()


def test_home_page_contains_score_elements():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert b"ats-score-value" in response.data
    assert b"skills-score" in response.data
    assert b"experience-score" in response.data
    assert b"qualifications-score" in response.data
    assert b"keywords-score" in response.data

def test_home_page_contains_score_breakdown():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    assert b"score-breakdown" in response.data
    assert b"score-breakdown-list" in response.data