from app import create_app


def test_home():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.content_type.startswith("text/html")

    assert b"AI Resume Analyzer" in response.data