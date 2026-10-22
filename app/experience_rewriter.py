from app.ai import create_llm_provider
from app.ai.providers import LLMProvider
from app.rewrite_models import build_rewrite_output
import json
from app.rewrite_validator import validate_rewrite
from app.section_parser import entry_to_block, format_items_for_prompt


def _source_experience_text(item):
    """Serialize trusted input for one experience item, never model output."""
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        if isinstance(item.get("text"), str):
            return item["text"].strip()
        if any(key in item for key in ("title", "company", "location", "dates", "bullets")):
            return entry_to_block(item)
        return json.dumps(item, ensure_ascii=False, sort_keys=True)
    return str(item).strip() if item is not None else ""


def rewrite_experience(
    experience,
    resume_text,
    resume_data=None,
    tailoring_plan=None,
    job_description="",
    client=None,
):
    """Rewrite existing resume experience content using AI."""

    
    # Normalize legacy dictionary-shaped experience data to a list.
    if isinstance(experience, dict):
        experience = [experience]
    elif not isinstance(experience, list):
        experience = []


    if not experience:
        return build_rewrite_output()

    client = client or create_llm_provider()

    prompt = f"""
Rewrite the following existing resume experience content.

EXPERIENCE:
{format_items_for_prompt(experience)}

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
- Do not upgrade annotation, review, or evaluation work into developing
  pipelines, deploying models, managing systems, or owning production work
  unless the original experience item explicitly says so.
- Keep each responsibility within the scope of the supplied experience item;
  another project elsewhere in the resume is not evidence that this job included it.
- Use job-description terminology only when supported by the
  original resume.
- Improve clarity, professionalism, and impact.
- Do not exaggerate the candidate's experience.
- Never upgrade the candidate's role: do not change "Contributed to", "Assisted", or "Supported" into "Developed", "Built", or "Led".
- Treat each ITEM as exactly one job; never merge or split items.
- Keep each item's bullets on separate lines starting with a bullet.

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

    for index, item in enumerate(parsed_response):
        if not isinstance(item, dict):
            all_grounded = False
            all_unsupported_claims.append(
                "Invalid rewritten experience item."
            )
            continue

        # The model's "original" field is untrusted. Anchor validation to the
        # actual source item at the same position so it cannot fabricate an
        # original statement to justify a stronger rewrite.
        original = (
            _source_experience_text(experience[index])
            if index < len(experience)
            else ""
        )
        rewritten = item.get("rewritten", "")
        item["original"] = original

        # Validate experience claims against this experience item, not the
        # entire resume. Project experience must not be used to substantiate
        # responsibilities attributed to an employer or role.
        validation = validate_rewrite(
            original,
            rewritten,
            evidence_text=original,
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