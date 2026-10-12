import json

from app.ai import create_llm_provider
from app.ai.providers import LLMProvider
from app.rewrite_models import build_rewrite_output
from app.rewrite_validator import validate_rewrite


def _extract_labeled_summary(resume_text):
    """Extract an explicitly labeled professional summary from a resume."""
    if not resume_text or not str(resume_text).strip():
        return ""

    summary_headings = {
        "PROFESSIONAL SUMMARY",
        "PROFESSIONAL PROFILE",
        "SUMMARY",
    }
    section_headings = summary_headings | {
        "SKILLS", "TECHNICAL SKILLS", "CORE SKILLS",
        "EXPERIENCE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE",
        "EMPLOYMENT HISTORY", "EDUCATION", "PROJECTS",
        "PERSONAL PROJECTS", "CERTIFICATIONS", "CERTIFICATES",
        "ACHIEVEMENTS", "AWARDS", "PUBLICATIONS", "LANGUAGES",
        "INTERESTS", "CAREER OBJECTIVE", "OBJECTIVE",
    }

    summary_lines = []
    collecting = False

    for line in str(resume_text).splitlines():
        stripped = line.strip()
        normalized = stripped.rstrip(":").strip().upper()

        if not collecting:
            if normalized in summary_headings:
                collecting = True
            continue

        if normalized in section_headings:
            break

        if stripped:
            summary_lines.append(stripped)

    return " ".join(summary_lines).strip()


def rewrite_summary(
    resume_text,
    resume_data=None,
    tailoring_plan=None,
    job_description="",
    client: LLMProvider | None = None,
):
    """Rewrite the existing professional summary using AI."""

    if not resume_text or not str(resume_text).strip():
        return build_rewrite_output()

    client = client or create_llm_provider()

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
2. Check explicitly for a section headed PROFESSIONAL SUMMARY,
   PROFESSIONAL PROFILE, or SUMMARY.
3. If one of these sections exists and contains text, rewrite that text.
4. Extract the summary from the section rather than guessing whether
   a summary exists.
5. Do not return an empty result when this section exists and contains
   text.
6. Return an empty result only when no existing professional summary
   can be identified.
7. Do not create a new summary from information that is not already
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
        extracted_summary = _extract_labeled_summary(resume_text)

        if extracted_summary:
            retry_prompt = f"""
Rewrite the existing professional summary below.

ORIGINAL SUMMARY:
{extracted_summary}

Requirements:
- Rewrite only the supplied summary.
- Preserve the original meaning and every factual claim.
- Do not invent skills, technologies, experience, achievements, or metrics.
- Do not exaggerate the candidate's experience.
- Do not use the job description as evidence of candidate experience.
- Keep the wording clear, professional, and concise.
- The original field must contain the supplied original summary.
- The rewritten field must contain the improved summary.
- Do not return an empty result when this section exists.
- Do not return an empty object when the supplied summary is present.

Return only one valid JSON object in this format:
{{
  "original": "the original summary text",
  "rewritten": "the improved summary text",
  "changes": ["brief description of the change"]
}}
"""
            retry_response = client.generate(retry_prompt)

            try:
                parsed_response = json.loads(retry_response)
            except (TypeError, json.JSONDecodeError):
                parsed_response = {}

            if not isinstance(parsed_response, dict) or not parsed_response:
                return {
                    "summary": {},
                    "validation": {
                        "meaning_preserved": False,
                        "unsupported_claims": [],
                        "grounding_status": "needs_review",
                    },
                }
        else:
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
