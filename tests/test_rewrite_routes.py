from app import create_app


def test_rewrite_route_requires_resume_text():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/resume/rewrite",
        json={}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "Resume text is required" in data["message"]


def test_rewrite_route_accepts_resume_data(monkeypatch):
    fake_result = {
        "summary": {},
        "experience": [],
        "projects": [],
        "skills": {},
        "validation": {
            "meaning_preserved": True,
            "unsupported_claims": [],
            "grounding_status": "grounded",
            "needs_review_sections": [],
        },
    }

    def fake_rewrite_resume(**kwargs):
        assert kwargs["resume_text"] == "Python developer"
        assert kwargs["job_description"] == "Python developer role"
        assert kwargs["experience"] == [
            {"description": "Built Python application"}
        ]
        assert kwargs["projects"] == [
            {"description": "Resume project"}
        ]
        assert kwargs["skills"] == ["Python"]

        return fake_result

    monkeypatch.setattr(
        "app.routes.rewrite_routes.rewrite_resume",
        fake_rewrite_resume,
    )

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/resume/rewrite",
        json={
            "resume_text": "Python developer",
            "resume_data": {
                "skills": ["Python"]
            },
            "tailoring_plan": {
                "priorities": ["Improve relevance"]
            },
            "job_description": "Python developer role",
            "experience": [
                {"description": "Built Python application"}
            ],
            "projects": [
                {"description": "Resume project"}
            ],
            "skills": ["Python"],
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["rewrite"] == fake_result