def _empty_plan():
    """Return an empty tailoring plan."""

    return {
        "tailoring_plan": {
            "priorities": [],
            "summary": [],
            "skills": [],
            "experience": [],
            "keywords": [],
            "qualifications": [],
            "warnings": _generate_warnings(),
        }
    }

def _normalize_item(item):
    """Normalize an item for duplicate detection."""

    return str(item).strip().lower()


def _generate_skill_tailoring(ats_result):
    """Generate tailoring guidance for missing skills."""

    missing_skills = ats_result.get(
        "missing_skills",
        [],
    ) or []

    suggestions = []
    seen = set()

    for skill in missing_skills:
        item = str(skill).strip()

        if not item:
            continue

        key = _normalize_item(item)

        if key in seen:
            continue

        seen.add(key)

        suggestions.append({
            "type": "skill",
            "item": item,
            "priority": "high",
            "action": "highlight",
            "recommendation": (
                f"Highlight relevant {item} experience "
                "in your resume if applicable."
            ),
            "reason": (
                f"{item} is required by the target job "
                "but is not currently represented in "
                "the resume."
            ),
        })

    return suggestions


def _generate_keyword_tailoring(ats_result):
    """Generate tailoring guidance for missing keywords."""

    missing_keywords = ats_result.get(
        "missing_keywords",
        [],
    ) or []

    suggestions = []
    seen = set()

    for keyword in missing_keywords:
        item = str(keyword).strip()

        if not item:
            continue

        key = _normalize_item(item)

        if key in seen:
            continue

        seen.add(key)

        suggestions.append({
            "type": "keyword",
            "item": item,
            "priority": "medium",
            "action": "incorporate",
            "recommendation": (
                "Naturally incorporate the keyword "
                f"'{item}' into relevant resume content "
                "if applicable and if it accurately "
                "reflects your experience."
            ),
            "reason": (
                f"The keyword '{item}' appears in the "
                "target job requirements but is missing "
                "from the resume."
            ),
        })

    return suggestions


def _generate_qualification_tailoring(ats_result):
    """Generate tailoring guidance for missing qualifications."""

    missing_qualifications = ats_result.get(
        "missing_qualifications",
        [],
    ) or []

    suggestions = []
    seen = set()

    for qualification in missing_qualifications:
        item = str(qualification).strip()

        if not item:
            continue

        key = _normalize_item(item)

        if key in seen:
            continue

        seen.add(key)

        suggestions.append({
            "type": "qualification",
            "item": item,
            "priority": "high",
            "action": "highlight",
            "recommendation": (
                f"Highlight your {item} qualification "
                "if applicable."
            ),
            "reason": (
                f"{item} is identified by the target job "
                "as a relevant qualification but is not "
                "currently represented in the resume."
            ),
        })

    return suggestions


def _generate_experience_tailoring(ats_result):
    """Generate job-specific experience guidance."""

    experience = ats_result.get(
        "experience",
        {},
    ) or {}

    required_years = experience.get(
        "required_years"
    )
    candidate_years = experience.get(
        "candidate_years"
    )
    meets_requirement = experience.get(
        "meets_requirement"
    )

    if (
        required_years is None
        or candidate_years is None
        or meets_requirement is None
    ):
        return []

    if meets_requirement:
        recommendation = (
            "Prioritize relevant experience and strengthen "
            "experience bullets that align with the target "
            "job's responsibilities."
        )

        reason = (
            "The resume meets the target job's stated "
            "experience requirement."
        )

        action = "strengthen"

    else:
        recommendation = (
            "Do not misrepresent your experience. Emphasize "
            "relevant projects, internships, freelance work, "
            "or other genuine experience where applicable."
        )

        reason = (
            "The resume does not currently meet the target "
            "job's stated experience requirement."
        )

        action = "review"

    return [{
        "type": "experience",
        "priority": "high",
        "action": action,
        "required_years": required_years,
        "candidate_years": candidate_years,
        "recommendation": recommendation,
        "reason": reason,
    }]


def _generate_summary_tailoring(
    resume_data,
):
    """Generate professional summary tailoring guidance."""

    if not resume_data:
        return []

    summary = resume_data.get("summary")

    if not summary:
        return []

    return [{
        "type": "summary",
        "priority": "high",
        "action": "strengthen",
        "recommendation": (
            "Strengthen the professional summary by "
            "aligning it with the target job and emphasizing "
            "relevant skills and experience already supported "
            "by your resume."
        ),
        "reason": (
            "A job-specific summary helps immediately "
            "communicate relevance to the target role."
        ),
    }]


def _convert_improvement_suggestions(
    improvement_suggestions,
):
    """Convert existing Phase 8 suggestions into tailoring items."""

    suggestions = []

    for item in improvement_suggestions or []:
        if not isinstance(item, dict):
            continue

        suggestion_type = item.get("type")

        if suggestion_type == "experience":
            action = "strengthen"
            section = "experience"

        elif suggestion_type == "skill":
            action = "highlight"
            section = "skills"

        elif suggestion_type == "keyword":
            action = "incorporate"
            section = "keywords"

        elif suggestion_type == "qualification":
            action = "highlight"
            section = "qualifications"

        elif suggestion_type == "project":
            action = "strengthen"
            section = "experience"

        else:
            continue

        converted = {
            "type": suggestion_type,
            "priority": item.get(
                "priority",
                "medium",
            ),
            "action": action,
            "recommendation": item.get(
                "suggestion",
                "",
            ),
            "reason": item.get(
                "reason",
                "",
            ),
        }

        if item.get("current_text"):
            converted["current_text"] = item[
                "current_text"
            ]

        if item.get("item"):
            converted["item"] = item["item"]

        suggestions.append(
            (
                section,
                converted,
            )
        )

    return suggestions


def _is_duplicate(existing_items, candidate):
    """Check whether a tailoring item already exists."""

    candidate_type = candidate.get("type")

    candidate_item = _normalize_item(
        candidate.get("item", "")
    )

    candidate_text = _normalize_item(
        candidate.get("current_text", "")
    )

    candidate_recommendation = _normalize_item(
        candidate.get("recommendation", "")
    )

    for existing in existing_items:
        if existing.get("type") != candidate_type:
            continue

        existing_item = _normalize_item(
            existing.get("item", "")
        )

        existing_text = _normalize_item(
            existing.get("current_text", "")
        )

        existing_recommendation = _normalize_item(
            existing.get("recommendation", "")
        )

        if candidate_item and existing_item:
            if candidate_item == existing_item:
                return True

        if candidate_text and existing_text:
            if candidate_text == existing_text:
                return True

        if candidate_recommendation and existing_recommendation:
            if (
                candidate_recommendation
                == existing_recommendation
            ):
                return True

        if candidate_item:
            if candidate_item in existing_recommendation:
                return True

        if existing_item:
            if existing_item in candidate_recommendation:
                return True

    return False


def _build_priorities(plan):
    """Build a short ranked list of the highest-value actions."""

    candidates = []

    for section in (
        "summary",
        "skills",
        "experience",
        "keywords",
        "qualifications",
    ):
        for item in plan.get(section, []):
            candidates.append(
                (
                    item.get("priority", "low"),
                    section,
                    item,
                )
            )

    priority_order = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }

    candidates.sort(
        key=lambda candidate: priority_order.get(
            candidate[0],
            2,
        )
    )

    priorities = []

    for rank, (_, section, item) in enumerate(
        candidates[:5],
        start=1,
    ):
        action_text = item.get(
            "recommendation",
            "",
        )

        priorities.append({
            "rank": rank,
            "area": section,
            "action": action_text,
        })

    return priorities


def _generate_warnings():
    """Return global resume tailoring safety warnings."""

    return [
        (
            "Only add skills or experience that accurately "
            "reflect your background."
        ),
        (
            "Do not fabricate employment history, "
            "qualifications, achievements, or metrics."
        ),
        (
            "Use job-specific keywords naturally rather "
            "than keyword stuffing."
        ),
    ]


def generate_tailoring_plan(
    resume_data,
    ats_result,
    resume_quality,
    content_quality,
    improvement_suggestions=None,
):
    """Generate a job-specific resume tailoring plan."""

    if (
        not resume_data
        and not ats_result
        and not resume_quality
        and not content_quality
        and not improvement_suggestions
    ):
        return _empty_plan()

    resume_data = resume_data or {}
    ats_result = ats_result or {}
    resume_quality = resume_quality or {}
    content_quality = content_quality or {}

    plan = {
        "priorities": [],
        "summary": [],
        "skills": [],
        "experience": [],
        "keywords": [],
        "qualifications": [],
        "warnings": _generate_warnings(),
    }

    plan["skills"].extend(
        _generate_skill_tailoring(
            ats_result
        )
    )

    plan["keywords"].extend(
        _generate_keyword_tailoring(
            ats_result
        )
    )

    plan["qualifications"].extend(
        _generate_qualification_tailoring(
            ats_result
        )
    )

    plan["experience"].extend(
        _generate_experience_tailoring(
            ats_result
        )
    )

    plan["summary"].extend(
        _generate_summary_tailoring(
            resume_data
        )
    )

    converted_suggestions = (
        _convert_improvement_suggestions(
            improvement_suggestions
        )
    )

    for section, suggestion in converted_suggestions:
        if not _is_duplicate(
            plan[section],
            suggestion,
        ):
            plan[section].append(
                suggestion
            )

    plan["priorities"] = _build_priorities(
        plan
    )

    return {
        "tailoring_plan": plan
    }