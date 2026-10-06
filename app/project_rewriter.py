import json

from app.ai.client import OpenAIClient
from app.rewrite_models import build_rewrite_output
from app.rewrite_validator import validate_rewrite


def rewrite_projects(
    projects,
    resume_text,
    resume_data=None,
    tailoring_plan=None,
    job_description="",
    client=None,
):
    """Rewrite existing resume project content using AI."""

    if not projects:
        return build_rewrite_output()

    client = client or OpenAIClient()

    prompt = f"""
Rewrite the following existing resume project content.

PROJECTS:
{projects}

ORIGINAL RESUME:
{resume_text}

STRUCTURED RESUME DATA:
{resume_data or {}}

PHASE 9 TAILORING PLAN:
{tailoring_plan or {}}

TARGET JOB DESCRIPTION:
{job_description or "(empty)"}

RULES:

- Preserve the original meaning.
- Preserve all factual information.
- Do not invent project functionality.
- Do not invent technologies or skills.
- Do not invent achievements.
- Do not invent metrics or numbers.
- Do not invent users, customers, performance results, or scale.
- Use job-description terminology only when supported by the
  original resume.
- Improve clarity, professionalism, and impact.
- Do not exaggerate the project.
- Do not change the actual scope of the project.

Return one rewritten item for each original project item.

Each item must contain:

{{
    "original": "original project text",
    "rewritten": "improved project text",
    "changes": [
        "brief description of the change"
    ]
}}

Return only JSON-compatible data.
"""

    response = client.generate(prompt)

    try:
        parsed_response = json.loads(response)
    except (TypeError, json.JSONDecodeError):
        return {
            "projects": [],
            "validation": {
                "meaning_preserved": False,
                "unsupported_claims": [],
                "grounding_status": "needs_review",
            },
        }

    if not isinstance(parsed_response, list):
        return {
            "projects": [],
            "validation": {
                "meaning_preserved": False,
                "unsupported_claims": [],
                "grounding_status": "needs_review",
            },
        }

    validated_projects = []
    all_unsupported_claims = []
    all_grounded = True

    for item in parsed_response:
        if not isinstance(item, dict):
            all_grounded = False
            all_unsupported_claims.append(
                "Invalid rewritten project item."
            )
            continue

        original = item.get("original", "")
        rewritten = item.get("rewritten", "")

        validation = validate_rewrite(
            original,
            rewritten,
            evidence_text=resume_text,
        )

        item["validation"] = validation

        validated_projects.append(item)

        all_unsupported_claims.extend(
            validation["unsupported_claims"]
        )

        if validation["grounding_status"] != "grounded":
            all_grounded = False

    return {
        "projects": validated_projects,
        "validation": {
            "meaning_preserved": (
                all_grounded
                and bool(validated_projects)
            ),
            "unsupported_claims": all_unsupported_claims,
            "grounding_status": (
                "grounded"
                if all_grounded and validated_projects
                else "needs_review"
            ),
        },
    }