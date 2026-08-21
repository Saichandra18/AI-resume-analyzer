from app import create_app


def test_home_page_contains_insight_sections():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    assert b"strengths" in response.data.lower()
    assert b"weaknesses" in response.data.lower()
    assert b"recommendations" in response.data.lower()

    assert b"strengths-list" in response.data
    assert b"weaknesses-list" in response.data
    assert b"recommendations-list" in response.data