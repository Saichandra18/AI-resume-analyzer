from app.skills_rewriter import rewrite_skills


class FakeClient:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return (
            '{"original": ["Python", "Flask", "SQL"], '
            '"rewritten": ["Python", "Flask", "SQL"], '
            '"changes": ["Improved consistency."]}'
        )


def test_rewrite_skills_returns_ai_result():
    client = FakeClient()

    result = rewrite_skills(
        skills=["Python", "Flask", "SQL"],
        resume_text="Python Flask SQL developer.",
        client=client,
    )

    assert "skills" in result
    assert isinstance(result["skills"], dict)
    assert result["skills"]["rewritten"] == [
        "Python",
        "Flask",
        "SQL",
    ]


def test_rewrite_skills_sends_resume_context():
    client = FakeClient()

    rewrite_skills(
        skills=["Python", "Flask"],
        resume_text="Developed applications using Python and Flask.",
        client=client,
    )

    assert (
        "Developed applications using Python and Flask."
        in client.prompts[0]
    )


def test_rewrite_skills_sends_tailoring_plan():
    client = FakeClient()

    tailoring_plan = {
        "skills": [
            {
                "item": "Python",
                "recommendation": "Highlight Python experience."
            }
        ]
    }

    rewrite_skills(
        skills=["Python", "Flask"],
        resume_text="Python Flask",
        tailoring_plan=tailoring_plan,
        client=client,
    )

    assert "Highlight Python experience." in client.prompts[0]


def test_rewrite_skills_sends_job_description():
    client = FakeClient()

    rewrite_skills(
        skills=["Python", "Flask"],
        resume_text="Python Flask",
        job_description="Backend developer with Python experience.",
        client=client,
    )

    assert (
        "Backend developer with Python experience."
        in client.prompts[0]
    )


def test_rewrite_skills_rejects_empty_skills():
    client = FakeClient()

    result = rewrite_skills(
        skills=[],
        resume_text="Python Flask",
        client=client,
    )

    assert result["skills"] == {}
    assert client.prompts == []


def test_rewrite_skills_handles_invalid_json():
    class InvalidJSONClient:
        def generate(self, prompt):
            return "Not valid JSON"

    result = rewrite_skills(
        skills=["Python"],
        resume_text="Python",
        client=InvalidJSONClient(),
    )

    assert result["skills"] == {}
    assert result["validation"]["grounding_status"] == "needs_review"


def test_rewrite_skills_rejects_non_object_json():
    class ListClient:
        def generate(self, prompt):
            return '["Python", "Flask"]'

    result = rewrite_skills(
        skills=["Python"],
        resume_text="Python",
        client=ListClient(),
    )

    assert result["skills"] == {}
    assert result["validation"]["grounding_status"] == "needs_review"


def test_rewrite_skills_validates_grounded_result():
    client = FakeClient()

    result = rewrite_skills(
        skills=["Python", "Flask", "SQL"],
        resume_text="Python Flask SQL developer.",
        client=client,
    )

    assert result["skills"]["validation"]["grounding_status"] == (
        "grounded"
    )
    assert result["validation"]["grounding_status"] == "grounded"


def test_rewrite_skills_flags_unsupported_skill():
    class JSONClient:
        def generate(self, prompt):
            return (
                '{"original": ["Python", "Flask"], '
                '"rewritten": ["Python", "Flask", "Docker"], '
                '"changes": ["Added relevant technology."]}'
            )

    result = rewrite_skills(
        skills=["Python", "Flask"],
        resume_text="Python Flask developer.",
        client=JSONClient(),
    )

    assert result["skills"]["validation"]["grounding_status"] == (
        "needs_review"
    )
    assert result["validation"]["grounding_status"] == "needs_review"
    assert result["validation"]["meaning_preserved"] is False

def test_rewrite_skills_does_not_trust_ai_original_skills():
    class JSONClient:
        def generate(self, prompt):
            return (
                '{"original": ["Python", "Flask", "Docker"], '
                '"rewritten": ["Python", "Flask", "Docker"], '
                '"changes": ["Improved skills section."]}'
            )

    result = rewrite_skills(
        skills=["Python", "Flask"],
        resume_text="Python Flask developer.",
        client=JSONClient(),
    )

    assert result["validation"]["grounding_status"] == "needs_review"
    assert result["validation"]["meaning_preserved"] is False

def test_rewrite_skills_accepts_skill_supported_by_resume_evidence():
    class JSONClient:
        def generate(self, prompt):
            return (
                '{"original": ["Python", "Flask"], '
                '"rewritten": ["Python", "Flask", "Docker"], '
                '"changes": ["Included an existing resume skill."]}'
            )

    result = rewrite_skills(
        skills=["Python", "Flask"],
        resume_text="Python Flask developer. Built and deployed applications using Docker.",
        client=JSONClient(),
    )

    assert result["validation"]["grounding_status"] == "grounded"
    assert result["validation"]["meaning_preserved"] is True

def test_rewrite_skills_limits_excessive_skill_expansion():
    class JSONClient:
        def generate(self, prompt):
            return (
                '{"original": ["Python", "SQL"], '
                '"rewritten": ['
                '"Python", "SQL", "Machine Learning", "Deep Learning", '
                '"NLP", "TensorFlow", "PyTorch", "Scikit-learn", '
                '"Pandas", "NumPy", "Flask", "Git", "Docker", '
                '"AWS", "REST APIs", "Statistics", "Probability", '
                '"Linear Algebra", "Feature Engineering", '
                '"Hyperparameter Tuning", "Cross-Validation", '
                '"Model Evaluation", "Data Cleaning", "ETL", '
                '"Prompt Engineering", "Embeddings", "Vector Search"'
                '], '
                '"changes": ["Expanded skills section."]}'
            )

    result = rewrite_skills(
        skills=["Python", "SQL"],
        resume_text=(
            "Developed applications using Python and SQL. "
            "Worked on machine learning projects."
        ),
        client=JSONClient(),
    )

    assert len(result["skills"]["rewritten"]) <= 20