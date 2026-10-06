from app.experience_rewriter import rewrite_experience


class FakeClient:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return '[{"original": "Built Flask app.", "rewritten": "Developed a Flask application.", "changes": ["Improved clarity."]}]'


def test_rewrite_experience_returns_ai_result():
    client = FakeClient()

    result = rewrite_experience(
        experience=["Built Flask app."],
        resume_text="Built Flask app.",
        client=client,
    )

    assert "experience" in result
    assert isinstance(result["experience"], list)
    assert (
        result["experience"][0]["rewritten"]
        == "Developed a Flask application."
    )

def test_rewrite_experience_sends_resume_context():
    client = FakeClient()

    rewrite_experience(
        experience=["Built Flask app."],
        resume_text="Developed web applications using Flask.",
        client=client,
    )

    assert "Developed web applications using Flask." in client.prompts[0]


def test_rewrite_experience_sends_tailoring_plan():
    client = FakeClient()

    tailoring_plan = {
        "experience": [
            {
                "item": "Flask",
                "recommendation": "Strengthen relevant Flask experience."
            }
        ]
    }

    rewrite_experience(
        experience=["Built Flask app."],
        resume_text="Built Flask app.",
        tailoring_plan=tailoring_plan,
        client=client,
    )

    assert "Flask" in client.prompts[0]
    assert "Strengthen relevant Flask experience." in client.prompts[0]


def test_rewrite_experience_sends_job_description():
    client = FakeClient()

    rewrite_experience(
        experience=["Built Flask app."],
        resume_text="Built Flask app.",
        job_description="Python backend developer with Flask experience.",
        client=client,
    )

    assert "Python backend developer with Flask experience." in client.prompts[0]


def test_rewrite_experience_rejects_empty_experience():
    client = FakeClient()

    result = rewrite_experience(
        experience=[],
        resume_text="Built Flask app.",
        client=client,
    )

    assert result["experience"] == []
    assert client.prompts == []


def test_rewrite_experience_contains_validation():
    client = FakeClient()

    result = rewrite_experience(
        experience=["Built Flask app."],
        resume_text="Built Flask app.",
        client=client,
    )

    assert "validation" in result
    assert result["validation"]["grounding_status"] == "grounded"

def test_rewrite_experience_parses_json_response():
    class JSONClient:
        def generate(self, prompt):
            return (
                '[{"original": "Built Flask app.", '
                '"rewritten": "Developed a Flask application.", '
                '"changes": ["Improved clarity."]}]'
            )

    result = rewrite_experience(
        experience=["Built Flask app."],
        resume_text="Built Flask app.",
        client=JSONClient(),
    )

    assert isinstance(result["experience"], list)
    assert result["experience"][0]["original"] == "Built Flask app."
    assert (
        result["experience"][0]["rewritten"]
        == "Developed a Flask application."
    )


def test_rewrite_experience_handles_invalid_json():
    class InvalidJSONClient:
        def generate(self, prompt):
            return "This is not valid JSON."

    result = rewrite_experience(
        experience=["Built Flask app."],
        resume_text="Built Flask app.",
        client=InvalidJSONClient(),
    )

    assert result["experience"] == []
    assert result["validation"]["grounding_status"] == "needs_review"


def test_rewrite_experience_rejects_non_list_json():
    class ObjectClient:
        def generate(self, prompt):
            return '{"rewritten": "Developed a Flask application."}'

    result = rewrite_experience(
        experience=["Built Flask app."],
        resume_text="Built Flask app.",
        client=ObjectClient(),
    )

    assert result["experience"] == []
    assert result["validation"]["grounding_status"] == "needs_review"

def test_rewrite_experience_validates_each_item():
    class JSONClient:
        def generate(self, prompt):
            return (
                '[{"original": "Built a Flask app.", '
                '"rewritten": "Developed a Flask application.", '
                '"changes": ["Improved clarity."]}]'
            )

    result = rewrite_experience(
        experience=["Built a Flask app."],
        resume_text="Built a Flask app.",
        client=JSONClient(),
    )

    item = result["experience"][0]

    assert "validation" in item
    assert item["validation"]["grounding_status"] == "grounded"
    assert result["validation"]["grounding_status"] == "grounded"


def test_rewrite_experience_flags_unsupported_claim():
    class JSONClient:
        def generate(self, prompt):
            return (
                '[{"original": "Built a Flask app.", '
                '"rewritten": "Developed a Flask application for 50000 users.", '
                '"changes": ["Added impact."]}]'
            )

    result = rewrite_experience(
        experience=["Built a Flask app."],
        resume_text="Built a Flask app.",
        client=JSONClient(),
    )

    item = result["experience"][0]

    assert item["validation"]["grounding_status"] == "needs_review"
    assert result["validation"]["grounding_status"] == "needs_review"
    assert result["validation"]["meaning_preserved"] is False

def test_rewrite_experience_does_not_allow_unsupported_claim_strengthening():
    class JSONClient:
        def generate(self, prompt):
            return (
                '['
                '{'
                '"original": "Maintained productivity and quality benchmarks.", '
                '"rewritten": "Consistently exceeded productivity and quality benchmarks.", '
                '"changes": ["Strengthened the impact of the statement."]'
                '}'
                ']'
            )
    result = rewrite_experience(
        experience=[
            {
                "text": "Maintained productivity and quality benchmarks."
            }
        ],
        resume_text="Maintained productivity and quality benchmarks.",
        client=JSONClient(),
    )

    assert result["experience"][0]["validation"]["grounding_status"] == (
        "needs_review"
    )
    assert result["experience"][0]["validation"]["meaning_preserved"] is False

def test_rewrite_experience_accepts_existing_improvement_claim():
    class JSONClient:
        def generate(self, prompt):
            return (
                '['
                '{'
                '"original": "Improved response quality through prompt evaluation.", '
                '"rewritten": "Improved response quality through structured prompt evaluation.", '
                '"changes": ["Improved clarity."]'
                '}'
                ']'
            )

    result = rewrite_experience(
        experience=[
            {
                "text": "Improved response quality through prompt evaluation."
            }
        ],
        resume_text=(
            "Improved response quality through prompt evaluation."
        ),
        client=JSONClient(),
    )

    assert result["experience"][0]["validation"]["grounding_status"] == (
        "grounded"
    )

def test_rewrite_experience_detects_unsupported_leadership_claim():
    class JSONClient:
        def generate(self, prompt):
            return (
                '['
                '{'
                '"original": "Supported model evaluation.", '
                '"rewritten": "Led model evaluation.", '
                '"changes": ["Strengthened ownership language."]'
                '}'
                ']'
            )

    result = rewrite_experience(
        experience=[
            {
                "text": "Supported model evaluation."
            }
        ],
        resume_text="Supported model evaluation.",
        client=JSONClient(),
    )

    assert result["experience"][0]["validation"]["grounding_status"] == (
        "needs_review"
    )
    assert result["experience"][0]["validation"]["meaning_preserved"] is False

def test_rewrite_experience_detects_unsupported_achievement_claim():
    class JSONClient:
        def generate(self, prompt):
            return (
                '['
                '{'
                '"original": "Worked on resume analysis features.", '
                '"rewritten": "Delivered high-impact resume analysis features.", '
                '"changes": ["Added stronger achievement wording."]'
                '}'
                ']'
            )

    result = rewrite_experience(
        experience=[
            {
                "text": "Worked on resume analysis features."
            }
        ],
        resume_text="Worked on resume analysis features.",
        client=JSONClient(),
    )

    assert result["experience"][0]["validation"]["grounding_status"] == (
        "needs_review"
    )
    assert result["experience"][0]["validation"]["meaning_preserved"] is False

def test_rewrite_experience_accepts_claim_strengthening_supported_by_resume():
    class JSONClient:
        def generate(self, prompt):
            return (
                '['
                '{'
                '"original": "Worked on response quality.", '
                '"rewritten": "Improved response quality through evaluation.", '
                '"changes": ["Made the contribution more concise."]'
                '}'
                ']'
            )

    result = rewrite_experience(
        experience=[
            {
                "text": "Worked on response quality."
            }
        ],
        resume_text=(
            "Worked on response quality. "
            "Improved response quality through evaluation."
        ),
        client=JSONClient(),
    )

    assert result["experience"][0]["validation"]["grounding_status"] == (
        "grounded"
    )