from app.ai.client import OpenAIClient
from app.rewrite_models import build_rewrite_output
import json
from app.rewrite_validator import validate_rewrite


def rewrite_experience(
    experience,
    resume_text,
    resume_data=None,
    tailoring_plan=None,
    job_description="",
    client=None,
):
    """Rewrite existing resume experience content using AI."""

    if not experience:
        return build_rewrite_output()

    client = client or OpenAIClient()

    prompt = f"""
Rewrite the following existing resume experience content.

EXPERIENCE:
{experience}

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
- Do not invent responsibilities.
- Do not invent technologies or skills.
- Do not invent achievements.
- Do not invent metrics or numbers.
- Use job-description terminology only when supported by the
  original resume.
- Improve clarity, professionalism, and impact.
- Do not exaggerate the candidate's experience.

Return one rewritten item for each original experience item.

Each item must contain:

{{
    "original": "original experience text",
    "rewritten": "improved experience text",
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
            "experience": [],
            "validation": {
                "meaning_preserved": False,
                "unsupported_claims": [],
                "grounding_status": "needs_review",
            },
        }

    if not isinstance(parsed_response, list):
        return {
            "experience": [],
            "validation": {
                "meaning_preserved": False,
                "unsupported_claims": [],
                "grounding_status": "needs_review",
            },
        }

    validated_experience = []
    all_unsupported_claims = []
    all_grounded = True

    for item in parsed_response:
        if not isinstance(item, dict):
            all_grounded = False
            all_unsupported_claims.append(
                "Invalid rewritten experience item."
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

        validated_experience.append(item)

        all_unsupported_claims.extend(
            validation["unsupported_claims"]
        )

        if validation["grounding_status"] != "grounded":
            all_grounded = False

    return {
        "experience": validated_experience,
        "validation": {
            "meaning_preserved": (
                all_grounded
                and bool(validated_experience)
            ),
            "unsupported_claims": all_unsupported_claims,
            "grounding_status": (
                "grounded"
                if all_grounded and validated_experience
                else "needs_review"
            ),
        },
    }