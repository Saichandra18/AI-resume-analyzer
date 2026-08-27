WEAK_EXPERIENCE_PHRASES = (
    "worked on",
    "responsible for",
    "helped with",
    "worked with",
    "involved in",
    "assisted with",
    "participated in",
)


def _get_experience_section(resume_data):
    """Return experience entries from structured resume data."""

    experience = resume_data.get(
        "experience",
        {},
    ) or {}

    return experience.get(
        "section",
        [],
    ) or []


def _detect_weak_experience_statements(resume_data):
    """Detect generic or weak experience statements."""

    suggestions = []
    seen_text = set()

    for item in _get_experience_section(resume_data):
        current_text = str(item).strip()

        if not current_text:
            continue

        normalized_text = current_text.lower()

        if normalized_text in seen_text:
            continue

        matched_phrase = next(
            (
                phrase
                for phrase in WEAK_EXPERIENCE_PHRASES
                if normalized_text.startswith(phrase)
            ),
            None,
        )

        if not matched_phrase:
            continue

        seen_text.add(normalized_text)

        suggestions.append({
            "type": "experience",
            "priority": "high",
            "current_text": current_text,
            "suggestion": (
                "Replace the generic opening with a specific "
                "action verb and describe what you developed, "
                "optimized, implemented, or delivered."
            ),
            "reason": (
                "The current statement does not clearly "
                "communicate your specific contribution."
            ),
        })

    return suggestions


def _generate_achievement_suggestion(content_quality):
    """Generate a suggestion when achievements lack measurable results."""

    signals = content_quality.get(
        "signals",
        {},
    ) or {}

    if signals.get("quantified_achievements") is not False:
        return None

    return {
        "type": "achievement",
        "priority": "high",
        "current_text": "",
        "suggestion": (
            "Add measurable results where possible, such as "
            "accuracy, performance improvement, processing time, "
            "scale, revenue, users, or cost reduction."
        ),
        "reason": (
            "Quantified results help demonstrate the measurable "
            "impact of your work."
        ),
    }


def _generate_project_suggestion(content_quality):
    """Generate a suggestion when project descriptions are limited."""

    signals = content_quality.get(
        "signals",
        {},
    ) or {}

    if signals.get("project_description") is not False:
        return None

    return {
        "type": "project",
        "priority": "medium",
        "current_text": "",
        "suggestion": (
            "Expand project descriptions with the project's "
            "purpose, technologies used, your contribution, "
            "and measurable outcome."
        ),
        "reason": (
            "A stronger project description makes your technical "
            "work and contribution easier to evaluate."
        ),
    }


def _generate_section_suggestions(resume_quality):
    """Generate suggestions for missing resume sections."""

    missing_sections = resume_quality.get(
        "missing_sections",
        [],
    ) or {}

    suggestions = []

    for section in missing_sections:
        section_name = str(section).strip()

        if not section_name:
            continue

        suggestions.append({
            "type": "section",
            "priority": "medium",
            "current_text": "",
            "suggestion": (
                f"Add a {section_name} section with relevant "
                "information from your background."
            ),
            "reason": (
                f"The {section_name} section is currently missing "
                "from the resume."
            ),
        })

    return suggestions


def _generate_ats_gap_suggestions(ats_result):
    """Generate improvement suggestions from ATS gaps."""

    ats_result = ats_result or {}

    suggestions = []

    missing_skills = ats_result.get(
        "missing_skills",
        [],
    ) or []

    missing_qualifications = ats_result.get(
        "missing_qualifications",
        [],
    ) or []

    missing_keywords = ats_result.get(
        "missing_keywords",
        [],
    ) or []

    seen = set()

    for skill in missing_skills:
        item = str(skill).strip()

        if not item:
            continue

        key = ("skill", item.lower())

        if key in seen:
            continue

        seen.add(key)

        suggestions.append({
            "type": "skill",
            "priority": "medium",
            "current_text": "",
            "suggestion": (
                f"Highlight relevant {item} experience "
                "in your resume if applicable."
            ),
            "reason": (
                f"The job description identifies {item} as "
                "a relevant skill that is not currently "
                "represented in your resume."
            ),
        })

    for qualification in missing_qualifications:
        item = str(qualification).strip()

        if not item:
            continue

        key = ("qualification", item.lower())

        if key in seen:
            continue

        seen.add(key)

        suggestions.append({
            "type": "qualification",
            "priority": "medium",
            "current_text": "",
            "suggestion": (
                f"Highlight your {item} qualification "
                "if applicable."
            ),
            "reason": (
                f"The job description identifies {item} "
                "as a relevant qualification that is not "
                "currently represented in your resume."
            ),
        })

    for keyword in missing_keywords:
        item = str(keyword).strip()

        if not item:
            continue

        key = ("keyword", item.lower())

        if key in seen:
            continue

        seen.add(key)

        suggestions.append({
            "type": "keyword",
            "priority": "medium",
            "current_text": "",
            "suggestion": (
                "Naturally incorporate the keyword "
                f"'{item}' into relevant resume content "
                "if applicable and if it accurately reflects "
                "your experience."
            ),
            "reason": (
                f"The keyword '{item}' appears in the job "
                "requirements but is not currently represented "
                "in your resume."
            ),
        })

    return suggestions


def generate_improvement_suggestions(
    resume_data,
    resume_quality,
    content_quality,
    ats_result=None,
):
    """Generate specific, actionable resume improvement suggestions."""

    if (
        not resume_data
        and not resume_quality
        and not content_quality
        and not ats_result
    ):
        return {
            "improvement_suggestions": []
        }

    resume_data = resume_data or {}
    resume_quality = resume_quality or {}
    content_quality = content_quality or {}
    ats_result = ats_result or {}

    suggestions = []

    suggestions.extend(
        _generate_ats_gap_suggestions(
            ats_result
        )
    )

    suggestions.extend(
        _detect_weak_experience_statements(
            resume_data
        )
    )

    achievement_suggestion = (
        _generate_achievement_suggestion(
            content_quality
        )
    )

    if achievement_suggestion:
        suggestions.append(
            achievement_suggestion
        )

    project_suggestion = (
        _generate_project_suggestion(
            content_quality
        )
    )

    if project_suggestion:
        suggestions.append(
            project_suggestion
        )

    suggestions.extend(
        _generate_section_suggestions(
            resume_quality
        )
    )

    return {
        "improvement_suggestions": suggestions
    }