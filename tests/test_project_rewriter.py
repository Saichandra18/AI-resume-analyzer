from app.project_rewriter import rewrite_projects


class FakeClient:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return (
            '[{"original": "Built Flask app.", '
            '"rewritten": "Developed a Flask application.", '
            '"changes": ["Improved clarity."]}]'
        )


def test_rewrite_projects_returns_ai_result():
    client = FakeClient()

    result = rewrite_projects(
        projects=["Built Flask app."],
        resume_text="Built Flask app.",
        client=client,
    )

    assert "projects" in result
    assert isinstance(result["projects"], list)
    assert (
        result["projects"][0]["rewritten"]
        == "Developed a Flask application."
    )


def test_rewrite_projects_sends_resume_context():
    client = FakeClient()

    rewrite_projects(
        projects=["Built Flask app."],
        resume_text="Developed web applications using Flask.",
        client=client,
    )

    assert "Developed web applications using Flask." in client.prompts[0]


def test_rewrite_projects_sends_tailoring_plan():
    client = FakeClient()

    tailoring_plan = {
        "experience": [
            {
                "item": "Flask",
                "recommendation": "Strengthen relevant Flask experience."
            }
        ]
    }

    rewrite_projects(
        projects=["Built Flask app."],
        resume_text="Built Flask app.",
        tailoring_plan=tailoring_plan,
        client=client,
    )

    assert "Flask" in client.prompts[0]
    assert "Strengthen relevant Flask experience." in client.prompts[0]


def test_rewrite_projects_sends_job_description():
    client = FakeClient()

    rewrite_projects(
        projects=["Built Flask app."],
        resume_text="Built Flask app.",
        job_description="Python backend developer with Flask experience.",
        client=client,
    )

    assert "Python backend developer with Flask experience." in client.prompts[0]


def test_rewrite_projects_rejects_empty_projects():
    client = FakeClient()

    result = rewrite_projects(
        projects=[],
        resume_text="Built Flask app.",
        client=client,
    )

    assert result["projects"] == []
    assert client.prompts == []


def test_rewrite_projects_handles_invalid_json():
    class InvalidJSONClient:
        def generate(self, prompt):
            return "This is not valid JSON."

    result = rewrite_projects(
        projects=["Built Flask app."],
        resume_text="Built Flask app.",
        client=InvalidJSONClient(),
    )

    assert result["projects"] == []
    assert result["validation"]["grounding_status"] == "needs_review"


def test_rewrite_projects_rejects_non_list_json():
    class ObjectClient:
        def generate(self, prompt):
            return '{"rewritten": "Developed a Flask application."}'

    result = rewrite_projects(
        projects=["Built Flask app."],
        resume_text="Built Flask app.",
        client=ObjectClient(),
    )

    assert result["projects"] == []
    assert result["validation"]["grounding_status"] == "needs_review"


def test_rewrite_projects_validates_each_item():
    class JSONClient:
        def generate(self, prompt):
            return (
                '[{"original": "Built a Flask app.", '
                '"rewritten": "Developed a Flask application.", '
                '"changes": ["Improved clarity."]}]'
            )

    result = rewrite_projects(
        projects=["Built a Flask app."],
        resume_text="Built a Flask app.",
        client=JSONClient(),
    )

    item = result["projects"][0]

    assert "validation" in item
    assert item["validation"]["grounding_status"] == "grounded"
    assert result["validation"]["grounding_status"] == "grounded"


def test_rewrite_projects_flags_unsupported_claim():
    class JSONClient:
        def generate(self, prompt):
            return (
                '[{"original": "Built a Flask app.", '
                '"rewritten": "Developed a Flask application for 50000 users.", '
                '"changes": ["Added impact."]}]'
            )

    result = rewrite_projects(
        projects=["Built a Flask app."],
        resume_text="Built a Flask app.",
        client=JSONClient(),
    )

    item = result["projects"][0]

    assert item["validation"]["grounding_status"] == "needs_review"
    assert result["validation"]["grounding_status"] == "needs_review"
    assert result["validation"]["meaning_preserved"] is False

def test_rewrite_projects_does_not_allow_unsupported_claim_strengthening():
    class JSONClient:
        def generate(self, prompt):
            return (
                '['
                '{'
                '"original": "Worked on a resume analyzer.", '
                '"rewritten": "Successfully delivered a resume analyzer.", '
                '"changes": ["Strengthened the project description."]'
                '}'
                ']'
            )

    result = rewrite_projects(
        projects=[
            {
                "text": "Worked on a resume analyzer."
            }
        ],
        resume_text="Worked on a resume analyzer.",
        client=JSONClient(),
    )

    validation = result["projects"][0]["validation"]

    assert validation["grounding_status"] == "needs_review"
    assert any(
        "Unsupported claim strengthening detected: delivered" in claim
        for claim in validation["unsupported_claims"]
    )