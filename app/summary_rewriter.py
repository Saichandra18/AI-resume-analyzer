import json

from app.ai.client import OpenAIClient
from app.rewrite_models import build_rewrite_output
from app.rewrite_validator import validate_rewrite


def rewrite_summary(
    resume_text,
    resume_data=None,
    tailoring_plan=None,
    job_description="",
    client=None,
):
    """Rewrite the existing professional summary using AI."""

    if not resume_text or not str(resume_text).strip():
        return build_rewrite_output()

    client = client or OpenAIClient()

    prompt = f"""
Rewrite the existing professional summary from the resume below.

ORIGINAL RESUME:
{resume_text}

STRUCTURED RESUME DATA:
{resume_data or {}}

PHASE 9 TAILORING PLAN:
{tailoring_plan or {}}

TARGET JOB DESCRIPTION:
{job_description or "(empty)"}

TASK:

1. Identify the existing professional summary in the resume.
2. If a professional summary exists, rewrite it.
3. If no professional summary exists, return an empty result.
4. Do not create a new summary from information that is not already
   present in the resume.

RULES:

- Preserve the original meaning.
- Preserve all factual information.
- Do not invent skills.
- Do not invent technologies.
- Do not invent experience.
- Do not invent achievements.
- Do not invent metrics or numbers.
- Do not invent job titles or qualifications.
- Use job-description terminology only when supported by the resume.
- Improve clarity, professionalism, and relevance.
- Do not exaggerate the candidate's experience.
- Do not treat the job description as evidence of candidate experience.

Return exactly one object:

{{
    "original": "original summary text",
    "rewritten": "improved summary text",
    "changes": [
        "brief description of the change"
    ]
}}

If no professional summary exists, return:

{{}}

Return only JSON-compatible data.
"""

    response = client.generate(prompt)

    try:
        parsed_response = json.loads(response)
    except (TypeError, json.JSONDecodeError):
        return {
            "summary": {},
            "validation": {
                "meaning_preserved": False,
                "unsupported_claims": [],
                "grounding_status": "needs_review",
            },
        }

    if not isinstance(parsed_response, dict):
        return {
            "summary": {},
            "validation": {
                "meaning_preserved": False,
                "unsupported_claims": [],
                "grounding_status": "needs_review",
            },
        }

    if not parsed_response:
        return {
            "summary": {},
            "validation": {
                "meaning_preserved": True,
                "unsupported_claims": [],
                "grounding_status": "grounded",
            },
        }

    original = parsed_response.get("original", "")
    rewritten = parsed_response.get("rewritten", "")

    if not original or not rewritten:
        return {
            "summary": {},
            "validation": {
                "meaning_preserved": False,
                "unsupported_claims": [
                    "Summary response is incomplete."
                ],
                "grounding_status": "needs_review",
            },
        }

    validation = validate_rewrite(
        original,
        rewritten,
        evidence_text=resume_text,
    )

    parsed_response["validation"] = validation

    return {
        "summary": parsed_response,
        "validation": validation,
    }