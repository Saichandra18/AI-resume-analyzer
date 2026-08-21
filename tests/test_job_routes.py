from app import create_app


def test_job_description_success():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/job-description",
        json={
            "job_description": "Python SQL Data Analysis"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["job_description"] == "Python SQL Data Analysis"


def test_job_description_empty():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/job-description",
        json={
            "job_description": ""
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"