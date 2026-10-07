"""Grounded AI rewriting for resume skills."""

import json
import re

from app.ai import create_llm_provider
from app.ai.providers import LLMProvider
from app.rewrite_models import build_rewrite_output
from app.rewrite_validator import validate_rewrite


MAX_REWRITTEN_SKILLS = 20


def _normalize_skill(value):
    """Normalize a skill for deterministic comparison."""

    if value is None:
        return ""

    text = str(value).lower().strip()

    # Normalize common punctuation.
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")

    # Normalize common abbreviations.
    replacements = {
        "large language models": "llm",
        "large language model": "llm",
        "retrieval augmented generation": "rag",
        "natural language processing": "nlp",
    }

    text = re.sub(r"\s+", " ", text).strip()

    for source, replacement in replacements.items():
        if text == source:
            text = replacement

    return text


def _skill_tokens(value):
    """Return normalized tokens for a skill."""

    normalized = _normalize_skill(value)

    if not normalized:
        return set()

    return set(
        re.findall(
            r"[a-z0-9+#.]+",
            normalized,
        )
    )


def _skills_are_equivalent(first, second):
    """Determine whether two skills represent the same concept."""

    first_normalized = _normalize_skill(first)
    second_normalized = _normalize_skill(second)

    if not first_normalized or not second_normalized:
        return False

    if first_normalized == second_normalized:
        return True

    first_tokens = _skill_tokens(first)
    second_tokens = _skill_tokens(second)

    if not first_tokens or not second_tokens:
        return False

    # Exact token-set equivalence.
    if first_tokens == second_tokens:
        return True

    # Handle known abbreviation equivalence.
    aliases = {
        frozenset({"nlp"}): frozenset(
            {"natural", "language", "processing"}
        ),
        frozenset({"llm"}): frozenset(
            {"large", "language", "models"}
        ),
        frozenset({"rag"}): frozenset(
            {"retrieval", "augmented", "generation"}
        ),
    }

    for alias_short, alias_long in aliases.items():
        if (
            first_tokens == alias_short
            and second_tokens == alias_long
        ) or (
            first_tokens == alias_long
            and second_tokens == alias_short
        ):
            return True

    return False


def _clean_skill_list(skills):
    """Clean a skill list while preserving order."""

    if not isinstance(skills, list):
        return []

    cleaned = []

    for skill in skills:
        if skill is None:
            continue

        value = str(skill).strip()

        if not value:
            continue

        # Remove accidental bullet prefixes.
        value = re.sub(
            r"^[•\-\u2013\u2014]+\s*",
            "",
            value,
        ).strip()

        if not value:
            continue

        cleaned.append(value)

    return cleaned


def _deduplicate_skills(skills):
    """Remove semantic duplicate skills while preserving order."""

    result = []

    for skill in _clean_skill_list(skills):
        if any(
            _skills_are_equivalent(
                skill,
                existing,
            )
            for existing in result
        ):
            continue

        result.append(skill)

    return result


def _find_matching_original_skill(
    rewritten_skill,
    original_skills,
):
    """Find the original skill represented by a rewritten skill."""

    for original_skill in original_skills:
        if _skills_are_equivalent(
            rewritten_skill,
            original_skill,
        ):
            return original_skill

    return None


def _merge_rewritten_with_original(
    rewritten_skills,
    original_skills,
):
    """
    Merge AI-rewritten skills with trusted original skills.

    AI output may improve naming, but it may never cause an
    existing candidate skill to disappear.
    """

    original_skills = _deduplicate_skills(
        original_skills
    )

    rewritten_skills = _clean_skill_list(
        rewritten_skills
    )

    merged = []
    matched_originals = set()

    # -----------------------------------------------------
    # Preserve useful AI naming where it maps to an actual
    # candidate skill.
    # -----------------------------------------------------
    for rewritten_skill in rewritten_skills:
        matched_original = _find_matching_original_skill(
            rewritten_skill,
            original_skills,
        )

        if matched_original is None:
            # Unsupported AI-generated skill.
            continue

        original_key = _normalize_skill(
            matched_original
        )

        if original_key in matched_originals:
            continue

        merged.append(
            rewritten_skill
        )

        matched_originals.add(
            original_key
        )

    # -----------------------------------------------------
    # Preserve every original skill that was not represented
    # by the AI output.
    # -----------------------------------------------------
    for original_skill in original_skills:
        original_key = _normalize_skill(
            original_skill
        )

        if original_key in matched_originals:
            continue

        merged.append(
            original_skill
        )

    # -----------------------------------------------------
    # Final semantic deduplication.
    # -----------------------------------------------------
    return _deduplicate_skills(
        merged
    )[:MAX_REWRITTEN_SKILLS]


def _fallback_result():
    """Return a safe result when AI output cannot be parsed."""

    return {
        "skills": {},
        "validation": {
            "meaning_preserved": False,
            "unsupported_claims": [],
            "grounding_status": "needs_review",
        },
    }


def rewrite_skills(
    skills,
    resume_text,
    resume_data=None,
    tailoring_plan=None,
    job_description="",
    client: LLMProvider | None = None,
):
    """Improve existing resume skills using grounded AI rewriting."""

    if not skills:
        return build_rewrite_output()

    client = client or create_llm_provider()

    prompt = f"""
Improve the existing skills section of the resume.

EXISTING SKILLS:
{skills}

ORIGINAL RESUME:
{resume_text}

STRUCTURED RESUME DATA:
{resume_data or {}}

PHASE 9 TAILORING PLAN:
{tailoring_plan or {}}

TARGET JOB DESCRIPTION:
{job_description or "(empty)"}

RULES:

- Preserve the candidate's existing skills.
- Do not add skills that are not supported by the original resume.
- Never add a skill solely because it appears in the job description.
- Do not invent technical skills.
- Do not invent tools, frameworks, platforms, or programming languages.
- Improve naming consistency and clarity where appropriate.
- Group equivalent existing skills when useful.
- Use job-description terminology only when the candidate's existing
  resume supports that terminology.
- Do not remove an existing skill merely because it is not mentioned
  in the job description.
- Do not exaggerate the candidate's proficiency.
- Do not assign proficiency levels unless supported by the resume.
- Prefer meaningful skill names over long lists of subtopics.
- Avoid creating separate skills from concepts that are merely
  variations of the same existing skill.
- Aim for approximately 10-20 skills when the source material
  supports that many.

IMPORTANT:

Every rewritten skill must correspond to an existing candidate skill.

The application will independently preserve original candidate
skills after this response, so do not assume that omitted skills
will be discarded.

Return a JSON-compatible object:

{{
    "original": [
        "original skill"
    ],
    "rewritten": [
        "improved skill"
    ],
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
        return _fallback_result()

    if not isinstance(parsed_response, dict):
        return _fallback_result()

    if not parsed_response:
        return {
            "skills": {},
            "validation": {
                "meaning_preserved": False,
                "unsupported_claims": [
                    "Skills response is empty."
                ],
                "grounding_status": "needs_review",
            },
        }

    # -----------------------------------------------------
    # TRUSTED APPLICATION INPUT
    # -----------------------------------------------------
    #
    # Never use the AI-generated "original" field as evidence.
    #
    original_skills = _clean_skill_list(
        skills
    )

    rewritten_skills = parsed_response.get(
        "rewritten",
        [],
    )

    if not isinstance(
        rewritten_skills,
        list,
    ):
        rewritten_skills = []

    # -----------------------------------------------------
    # Validate the RAW AI output BEFORE removing unsupported
    # skills.
    #
    # This preserves the grounding contract: unsupported
    # claims made by the AI must still be detected and flagged.
    # -----------------------------------------------------
    raw_rewritten_skills = _clean_skill_list(
        rewritten_skills
    )

    raw_original_text = ", ".join(
        str(skill)
        for skill in original_skills
    )

    raw_rewritten_text = ", ".join(
        str(skill)
        for skill in raw_rewritten_skills
    )

    raw_validation = validate_rewrite(
        raw_original_text,
        raw_rewritten_text,
        evidence_text=resume_text,
    )

    # -----------------------------------------------------
    # Ground the AI output AFTER validation.
    #
    # Unsupported AI-generated skills are removed from the
    # final resume, while legitimate candidate skills are
    # preserved.
    # -----------------------------------------------------
    merged_skills = _merge_rewritten_with_original(
        rewritten_skills=raw_rewritten_skills,
        original_skills=original_skills,
    )

    parsed_response["rewritten"] = merged_skills

    # The original field must always represent trusted
    # application input, never the AI-generated "original".
    parsed_response["original"] = original_skills[:]

    # Preserve the raw-AI validation result so unsupported
    # claims remain visible to the application and tests.
    validation = raw_validation

    parsed_response["validation"] = validation

    return {
        "skills": parsed_response,
        "validation": validation,
    }