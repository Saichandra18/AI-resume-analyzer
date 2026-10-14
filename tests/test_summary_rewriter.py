from app.summary_rewriter import rewrite_summary


class FakeClient:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return (
            '{"original": "Python developer with Flask experience.", '
            '"rewritten": "Python developer with Flask experience.", '
            '"changes": ["Improved clarity."]}'
        )


def test_rewrite_summary_returns_ai_result():
    client = FakeClient()

    result = rewrite_summary(
        resume_text="Python developer with Flask experience.",
        client=client,
    )

    assert "summary" in result
    assert result["summary"]["original"] == (
        "Python developer with Flask experience."
    )


def test_rewrite_summary_returns_rewritten_text():
    class JSONClient:
        def generate(self, prompt):
            return (
                '{"original": "Python developer with Flask experience.", '
                '"rewritten": "Python developer experienced with Flask.", '
                '"changes": ["Improved wording."]}'
            )

    result = rewrite_summary(
        resume_text="Python developer with Flask experience.",
        client=JSONClient(),
    )

    assert (
        result["summary"]["rewritten"]
        == "Python developer experienced with Flask."
    )


def test_rewrite_summary_sends_resume_context():
    client = FakeClient()

    rewrite_summary(
        resume_text="Python developer with Flask experience.",
        client=client,
    )

    assert "Python developer with Flask experience." in client.prompts[0]


def test_rewrite_summary_sends_tailoring_plan():
    client = FakeClient()

    tailoring_plan = {
        "summary": [
            {
                "item": "Python",
                "recommendation": "Strengthen Python positioning.",
            }
        ]
    }

    rewrite_summary(
        resume_text="Python developer with Flask experience.",
        tailoring_plan=tailoring_plan,
        client=client,
    )

    assert "Strengthen Python positioning." in client.prompts[0]


def test_rewrite_summary_sends_job_description():
    client = FakeClient()

    rewrite_summary(
        resume_text="Python developer with Flask experience.",
        job_description="Backend developer with Python experience.",
        client=client,
    )

    assert "Backend developer with Python experience." in client.prompts[0]


def test_rewrite_summary_handles_empty_resume():
    client = FakeClient()

    result = rewrite_summary(
        resume_text="",
        client=client,
    )

    assert result["summary"] == {}
    assert client.prompts == []


def test_rewrite_summary_handles_no_summary():
    class EmptyClient:
        def generate(self, prompt):
            return "{}"

    result = rewrite_summary(
        resume_text="Skills: Python, Flask",
        client=EmptyClient(),
    )

    assert result["summary"] == {}
    assert result["validation"]["grounding_status"] == "grounded"


def test_rewrite_summary_handles_invalid_json():
    class InvalidJSONClient:
        def generate(self, prompt):
            return "Not JSON"

    result = rewrite_summary(
        resume_text="Python developer.",
        client=InvalidJSONClient(),
    )

    assert result["summary"] == {}
    assert result["validation"]["grounding_status"] == "needs_review"


def test_rewrite_summary_validates_rewrite():
    class JSONClient:
        def generate(self, prompt):
            return (
                '{"original": "Python developer.", '
                '"rewritten": "Python developer with 50000 users.", '
                '"changes": ["Added impact."]}'
            )

    result = rewrite_summary(
        resume_text="Python developer.",
        client=JSONClient(),
    )

    assert result["summary"]["validation"]["grounding_status"] == (
        "needs_review"
    )
    assert result["validation"]["grounding_status"] == "needs_review"


def test_rewrite_summary_does_not_allow_unsupported_claim_strengthening():
    class JSONClient:
        def generate(self, prompt):
            return (
                '{'
                '"original": "Worked on Python applications.", '
                '"rewritten": "Successfully delivered Python applications.", '
                '"changes": ["Made the summary more concise."]'
                '}'
            )

    result = rewrite_summary(
        resume_text="Worked on Python applications.",
        client=JSONClient(),
    )

    validation = result["summary"]["validation"]

    assert validation["grounding_status"] == "needs_review"
    assert any(
        "Unsupported claim strengthening detected: delivered" in claim
        for claim in validation["unsupported_claims"]
    )


def test_rewrite_summary_prompt_protects_explicit_summary_section():
    class CapturingClient:
        def __init__(self):
            self.prompt = ""

        def generate(self, prompt):
            self.prompt = prompt
            return "{}"

    resume_text = """
    PROFESSIONAL SUMMARY
    Entry-level Python developer with experience building Flask APIs
    and SQL data analysis projects.

    SKILLS
    Python, SQL, Flask
    """

    client = CapturingClient()

    rewrite_summary(
        resume_text=resume_text,
        client=client,
    )

    prompt = client.prompt.lower()

    assert "professional summary" in prompt
    assert (
        "do not return an empty result when this section exists" in prompt
    )

def test_rewrite_summary_retries_with_explicit_section_when_model_returns_empty():
    class RetryClient:
        def __init__(self):
            self.prompts = []
            self.calls = 0

        def generate(self, prompt):
            import json

            self.prompts.append(prompt)
            self.calls += 1

            if self.calls == 1:
                return "{}"

            return json.dumps(
                {
                    "original": (
                        "Entry-level Python developer with experience "
                        "building Flask APIs and SQL data analysis projects."
                    ),
                    "rewritten": (
                        "Entry-level Python developer experienced in "
                        "building Flask APIs and conducting SQL data analysis."
                    ),
                    "changes": [
                        "Improved clarity while preserving the original facts."
                    ],
                }
            )

    resume_text = """
    PROFESSIONAL SUMMARY
    Entry-level Python developer with experience building Flask APIs
    and SQL data analysis projects.

    SKILLS
    Python, SQL, Flask
    """

    client = RetryClient()

    result = rewrite_summary(
        resume_text=resume_text,
        client=client,
    )

    assert client.calls == 2
    assert result["summary"]["rewritten"]
    assert result["summary"]["original"].startswith("Entry-level")
