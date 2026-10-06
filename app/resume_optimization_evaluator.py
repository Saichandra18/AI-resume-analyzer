"""Before-vs-after ATS evaluation for optimized resumes.

This module evaluates an original resume and its optimized FinalResume
against the same job description.

The evaluator intentionally reuses the existing ATS analysis and scoring
architecture instead of implementing a second scoring system.
"""

from copy import deepcopy

from app.ats_analyzer import analyze_resume_against_job
from app.final_ats_validation import compare_ats_results
from app.final_resume_models import FinalResume


def _safe_text(value):
    """Convert a value to clean searchable text."""

    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (list, tuple, set)):
        return " ".join(
            text
            for text in (_safe_text(item) for item in value)
            if text
        ).strip()

    if isinstance(value, dict):
        return " ".join(
            text
            for text in (
                _safe_text(item)
                for item in value.values()
            )
            if text
        ).strip()

    return str(value).strip()


def _extract_text_from_item(item):
    """Extract searchable text from a canonical resume item."""

    if item is None:
        return ""

    if isinstance(item, str):
        return item.strip()

    if not isinstance(item, dict):
        return _safe_text(item)

    parts = []

    preferred_fields = (
        "title",
        "job_title",
        "name",
        "company",
        "organization",
        "institution",
        "degree",
        "year",
        "years",
        "date",
        "dates",
        "location",
        "summary",
        "description",
        "descriptions",
        "bullet",
        "bullets",
        "responsibility",
        "responsibilities",
        "achievement",
        "achievements",
        "technologies",
        "technology",
        "skills",
        "tools",
    )

    for field in preferred_fields:
        if field not in item:
            continue

        value = item.get(field)

        if value is None:
            continue

        text = _safe_text(value)

        if text:
            parts.append(text)

    return " ".join(parts).strip()


def _extract_year_values(experience):
    """Extract date/year strings from canonical experience entries."""

    years = []

    for item in experience or []:
        if isinstance(item, str):
            text = item.strip()

            if text:
                years.append(text)

            continue

        if not isinstance(item, dict):
            continue

        for field in (
            "dates",
            "date",
            "years",
            "year",
        ):
            value = item.get(field)

            if value is None:
                continue

            if isinstance(value, (list, tuple)):
                for entry in value:
                    text = _safe_text(entry)

                    if text:
                        years.append(text)
            else:
                text = _safe_text(value)

                if text:
                    years.append(text)

            break

    return years


def _build_optimized_experience(experience):
    """Convert canonical experience into the legacy ATS format."""

    experience = deepcopy(experience or [])

    job_titles = []
    section = []

    for item in experience:
        if isinstance(item, str):
            text = item.strip()

            if text:
                section.append(text)

            continue

        if not isinstance(item, dict):
            continue

        job_title = item.get("job_title")

        if job_title:
            job_titles.append(
                _safe_text(job_title)
            )

        text = _extract_text_from_item(item)

        if text:
            section.append(text)

    result = {
        "section": section,
        "job_titles": job_titles,
    }

    years = _extract_year_values(experience)

    if years:
        result["years"] = years

    return result


def _build_optimized_education(education):
    """Convert canonical education into the legacy ATS format."""

    education = deepcopy(education or [])

    degrees = []
    section = []

    for item in education:
        if isinstance(item, str):
            text = item.strip()

            if text:
                section.append(text)

            continue

        if not isinstance(item, dict):
            continue

        degree = item.get("degree")

        if degree:
            degree_text = _safe_text(degree)

            if degree_text:
                degrees.append(degree_text)

        text = _extract_text_from_item(item)

        if text:
            section.append(text)

    return {
        "degrees": degrees,
        "section": section,
    }


def _build_optimized_projects(projects):
    """Convert canonical projects into keyword-searchable values."""

    projects = deepcopy(projects or [])

    normalized = []

    for item in projects:
        text = _extract_text_from_item(item)

        if text:
            normalized.append(text)

    return normalized


def _build_raw_text(resume):
    """Flatten a canonical FinalResume into searchable resume text."""

    parts = []

    if resume.summary:
        parts.append(
            _safe_text(resume.summary)
        )

    for section in (
        resume.skills,
        resume.experience,
        resume.projects,
        resume.education,
        resume.certifications,
    ):
        for item in section or []:
            text = _extract_text_from_item(item)

            if text:
                parts.append(text)

    return "\n".join(parts).strip()


def _final_resume_to_ats_data(final_resume):
    """Convert FinalResume into the structure expected by the ATS analyzer."""

    if isinstance(final_resume, dict):
        final_resume = FinalResume.from_dict(
            final_resume
        )

    if not isinstance(final_resume, FinalResume):
        raise TypeError(
            "final_resume must be a FinalResume instance "
            "or a dictionary representation of FinalResume."
        )

    return {
        "personal_info": deepcopy(
            final_resume.personal_info
        ),
        "summary": final_resume.summary,
        "skills": deepcopy(
            final_resume.skills
        ),
        "experience": _build_optimized_experience(
            final_resume.experience
        ),
        "projects": _build_optimized_projects(
            final_resume.projects
        ),
        "education": _build_optimized_education(
            final_resume.education
        ),
        "certifications": deepcopy(
            final_resume.certifications
        ),
        "raw_text": _build_raw_text(
            final_resume
        ),
    }


def _extract_component_scores(analysis_result):
    """Return normalized component scores from an ATS result."""

    scores = analysis_result.get(
        "component_scores",
        {},
    )

    return {
        "skills": scores.get("skills"),
        "experience": scores.get("experience"),
        "qualifications": scores.get(
            "qualifications"
        ),
        "keywords": scores.get("keywords"),
    }


def evaluate_resume_optimization(
    original_resume_data,
    optimized_resume,
    job_description,
):
    """Compare original and optimized resume ATS performance.

    Parameters
    ----------
    original_resume_data:
        Original structured resume data accepted by the existing ATS
        analyzer.

    optimized_resume:
        Canonical FinalResume instance or its dictionary representation.

    job_description:
        Job description used for both evaluations.

    Returns
    -------
    dict
        Before/after ATS scores, component scores, detailed ATS
        comparison, and remaining skill/keyword gaps.
    """

    # ------------------------------------------------------------------
    # Prepare independent inputs.
    # ------------------------------------------------------------------

    original_input = deepcopy(
        original_resume_data or {}
    )

    optimized_input = _final_resume_to_ats_data(
        optimized_resume
    )

    # ------------------------------------------------------------------
    # Run the existing ATS analyzer.
    #
    # Both resumes are evaluated against the exact same JD.
    # ------------------------------------------------------------------

    before_result = analyze_resume_against_job(
        original_input,
        job_description,
    )

    after_result = analyze_resume_against_job(
        optimized_input,
        job_description,
    )

    # ------------------------------------------------------------------
    # Extract overall scores.
    # ------------------------------------------------------------------

    before_score = before_result.get(
        "ats_score",
        0,
    )

    after_score = after_result.get(
        "ats_score",
        0,
    )

    improvement = (
        after_score - before_score
    )

    # ------------------------------------------------------------------
    # Phase 15.2 / 15.3 / 15.4
    #
    # Reuse the centralized ATS comparison layer.
    # ------------------------------------------------------------------

    ats_comparison = compare_ats_results(
        before_result,
        after_result,
    )

    # ------------------------------------------------------------------
    # Build the detailed gap analysis.
    # ------------------------------------------------------------------

    gap_analysis = {
        "newly_matched_skills": (
            ats_comparison.newly_matched_skills
        ),
        "lost_skills": (
            ats_comparison.lost_skills
        ),
        "remaining_missing_skills": (
            ats_comparison.remaining_missing_skills
        ),
        "newly_matched_keywords": (
            ats_comparison.newly_matched_keywords
        ),
        "lost_keywords": (
            ats_comparison.lost_keywords
        ),
        "remaining_missing_keywords": (
            ats_comparison.remaining_missing_keywords
        ),
        "remaining_skill_count": len(
            ats_comparison.remaining_missing_skills
        ),
        "remaining_keyword_count": len(
            ats_comparison.remaining_missing_keywords
        ),
    }

    # ------------------------------------------------------------------
    # Return the complete evaluation.
    # ------------------------------------------------------------------

    return {
        "before_score": before_score,
        "after_score": after_score,
        "improvement": improvement,

        "before": _extract_component_scores(
            before_result
        ),

        "after": _extract_component_scores(
            after_result
        ),

        "before_analysis": before_result,
        "after_analysis": after_result,

        "comparison": ats_comparison,

        "gap_analysis": gap_analysis,
    }


__all__ = [
    "evaluate_resume_optimization",
]