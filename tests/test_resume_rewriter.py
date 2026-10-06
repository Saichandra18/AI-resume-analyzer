from app.resume_rewriter import rewrite_resume


class FakeClient:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0

    def generate(self, prompt):
        response = self.responses[self.index]
        self.index += 1
        return response


def test_rewrite_resume_combines_all_sections():
    client = FakeClient([
        # Experience
        """
        [
            {
                "original": "Developed Python application",
                "rewritten": "Developed a Python application",
                "changes": ["Improved clarity"]
            }
        ]
        """,
        # Projects
        """
        [
            {
                "original": "Built a Flask project",
                "rewritten": "Built a Flask-based project",
                "changes": ["Improved wording"]
            }
        ]
        """,
        # Summary
        """
        {
            "original": "Python developer with project experience.",
            "rewritten": "Python developer with hands-on project experience.",
            "changes": ["Improved professionalism"]
        }
        """,
        # Skills
        """
        {
            "original": ["Python", "Flask", "SQL"],
            "rewritten": ["Python", "Flask", "SQL"],
            "changes": ["Standardized skill names"]
        }
        """,
    ])

    result = rewrite_resume(
        resume_text="Python developer with project experience.",
        resume_data={
            "skills": ["Python", "Flask", "SQL"]
        },
        tailoring_plan={
            "summary": ["Emphasize Python experience"]
        },
        job_description="Python developer role",
        experience=[
            {"description": "Developed Python application"}
        ],
        projects=[
            {"description": "Built a Flask project"}
        ],
        skills=["Python", "Flask", "SQL"],
        client=client,
    )

    assert "summary" in result
    assert "experience" in result
    assert "projects" in result
    assert "skills" in result
    assert "validation" in result

    assert len(result["experience"]) == 1
    assert len(result["projects"]) == 1

    assert result["summary"]["rewritten"]
    assert result["skills"]["rewritten"]


def test_rewrite_resume_handles_empty_sections():
    client = FakeClient([
        # Summary rewriter is still called because resume_text is non-empty.
        "{}",
    ])

    result = rewrite_resume(
        resume_text="Python developer",
        experience=[],
        projects=[],
        skills=[],
        client=client,
    )

    assert result["experience"] == []
    assert result["projects"] == []
    assert result["summary"] == {}
    assert result["skills"] == {}

    assert "validation" in result

def test_rewrite_resume_preserves_validation_status():
    client = FakeClient([
        # Experience with fabricated number
        """
        [
            {
                "original": "Developed Python application",
                "rewritten": "Developed Python application improving performance by 50%",
                "changes": ["Added performance claim"]
            }
        ]
        """,
        # Projects
        "[]",
        # Summary
        "{}",
        # Skills
        """
        {
            "original": ["Python"],
            "rewritten": ["Python"],
            "changes": []
        }
        """,
    ])

    result = rewrite_resume(
        resume_text="Developed Python application",
        experience=[
            {"description": "Developed Python application"}
        ],
        projects=[],
        skills=["Python"],
        client=client,
    )

    assert result["validation"]["grounding_status"] == "needs_review"
    assert result["validation"]["meaning_preserved"] is False
    assert result["validation"]["unsupported_claims"]


def test_rewrite_resume_passes_client_to_all_rewriters():
    responses = [
        "[]",
        "[]",
        "{}",
        "{}",
    ]

    client = FakeClient(responses)

    rewrite_resume(
        resume_text="Python developer",
        experience=[{"description": "Developed Python application"}],
        projects=[{"description": "Built a project"}],
        skills=["Python"],
        client=client,
    )

    assert client.index == 4