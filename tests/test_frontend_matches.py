from app import create_app


def test_home_page_contains_match_sections():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    assert b"matched-skills" in response.data
    assert b"missing-skills" in response.data

    assert b"matched-qualifications" in response.data
    assert b"missing-qualifications" in response.data

    assert b"matched-keywords" in response.data
    assert b"missing-keywords" in response.data