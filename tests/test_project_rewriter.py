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

def test_group_project_lines_preserves_project_boundaries():
    from app.project_rewriter import _group_project_lines

    projects = [
        "AI Resume Analyzer using LLM, NLP and RAG",
        "\u2022 Developed an AI-powered resume analysis system.",
        "\u2022 Implemented ATS evaluation for backward",
        "compatibility.",
        "Cricket Match Analytics Dashboard",
        "\u2022 Technologies: Python, SQL, Power BI, Pandas.",
        "\u2022 Built an interactive analytics dashboard.",
        "Generative AI Chatbot using LLM and RAG",
        "\u2022 Implemented embedding-based semantic search.",
    ]

    grouped = _group_project_lines(projects)

    assert len(grouped) == 3
    assert grouped[0].startswith(
        "AI Resume Analyzer using LLM, NLP and RAG"
    )
    assert "backward compatibility." in grouped[0]
    assert grouped[1].startswith("Cricket Match Analytics Dashboard")
    assert grouped[2].startswith("Generative AI Chatbot")


import json

from app.project_rewriter import rewrite_projects


class FakeProjectClient:
    def __init__(self, response):
        self.response = response
        self.prompt = None

    def generate(self, prompt):
        self.prompt = prompt
        return json.dumps(self.response)


def test_project_rewriter_keeps_projects_in_separate_input_blocks():
    client = FakeProjectClient([
        {
            "original": (
                "AI Resume Analyzer\n"
                "• Developed an AI-powered resume analyzer.\n"
                "• Implemented backward compatibility."
            ),
            "rewritten": (
                "AI Resume Analyzer\n"
                "• Developed an AI-powered resume analyzer.\n"
                "• Implemented backward compatibility."
            ),
            "changes": [],
        },
        {
            "original": (
                "Cricket Match Analytics Dashboard\n"
                "• Built an interactive analytics dashboard."
            ),
            "rewritten": (
                "Cricket Match Analytics Dashboard\n"
                "• Built an interactive analytics dashboard."
            ),
            "changes": [],
        },
    ])

    projects = [
        "AI Resume Analyzer",
        "- Developed an AI-powered resume analyzer.",
        "- Implemented backward",
        "compatibility.",
        "Cricket Match Analytics Dashboard",
        "- Built an interactive analytics dashboard.",
    ]

    result = rewrite_projects(
        projects=projects,
        resume_text="\n".join(projects),
        client=client,
    )

    assert client.prompt is not None
    assert "AI Resume Analyzer" in client.prompt
    assert "Cricket Match Analytics Dashboard" in client.prompt
    assert "backward compatibility." in client.prompt
    assert len(result["projects"]) == 2


def test_project_grouping_preserves_existing_structured_inputs():
    from app.project_rewriter import _group_project_lines

    structured = [
        {
            "title": "AI Resume Analyzer",
            "bullets": ["Implemented ATS matching."],
        }
    ]

    assert _group_project_lines(structured) == structured


from app.project_rewriter import _group_project_lines


def test_project_grouping_joins_uppercase_wrapped_bullet():
    projects = [
        "AI Resume Analyzer",
        "- Implemented ATS matching for backward",
        "Compatibility with existing workflows.",
    ]

    grouped = _group_project_lines(projects)

    assert len(grouped) == 1
    assert "backward Compatibility with existing workflows." in grouped[0]


def test_project_grouping_keeps_separate_project_titles():
    projects = [
        "AI Resume Analyzer",
        "- Implemented resume matching.",
        "Cricket Match Analytics Dashboard",
        "- Built match analytics.",
    ]

    grouped = _group_project_lines(projects)

    assert len(grouped) == 2
    assert grouped[0].startswith("AI Resume Analyzer\n")
    assert "Cricket Match Analytics Dashboard" not in grouped[0]
    assert grouped[1].startswith("Cricket Match Analytics Dashboard\n")
