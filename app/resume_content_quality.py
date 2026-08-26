def _has_contact_information(resume_data):
    personal_info = resume_data.get(
        "personal_info",
        {},
    ) or {}

    return bool(
        personal_info.get("email")
        and personal_info.get("phone")
    )


def _has_quantified_achievements(resume_data):
    experience = resume_data.get(
        "experience",
        {},
    ) or {}

    section = experience.get(
        "section",
        [],
    ) or []

    text = " ".join(
        str(item)
        for item in section
    ).lower()

    # Quantified achievements can use percentages,
    # numbers, measurements, counts, or multipliers.
    if "%" in text or "percent" in text:
        return any(
            character.isdigit()
            for character in text
        )

    achievement_patterns = (
        " by ",
        " to ",
        " from ",
        " with ",
        " x",
        "x ",
    )

    has_number = any(
        character.isdigit()
        for character in text
    )

    has_achievement_pattern = any(
        pattern in text
        for pattern in achievement_patterns
    )

    return has_number and has_achievement_pattern

def _has_action_oriented_experience(resume_data):
    experience = resume_data.get(
        "experience",
        {},
    ) or {}

    section = experience.get(
        "section",
        [],
    ) or []

    action_words = {
        "developed",
        "created",
        "built",
        "implemented",
        "designed",
        "improved",
        "reduced",
        "increased",
        "managed",
        "led",
        "automated",
        "analyzed",
        "optimized",
        "spearheaded",
        "streamlined",
        "delivered",
        "engineered",
        "launched",
        "deployed",
        "established",
        "coordinated",
        "executed",
        "generated",
        "enhanced",
        "transformed",
    }

    text = " ".join(
        str(item).lower()
        for item in section
    )

    return any(
        word in text
        for word in action_words
    )


def _has_project_description(resume_data):
    projects = resume_data.get(
        "projects",
        [],
    ) or []

    if len(projects) < 2:
        return False

    return any(
        len(str(project).split()) >= 4
        for project in projects[1:]
    )


def analyze_resume_content_quality(resume_data):
    """Analyze qualitative content signals in a structured resume."""

    if not resume_data:
        return {
            "score": 0,
            "signals": {},
            "warnings": [],
            "recommendations": [],
        }

    signals = {
        "contact_information": (
            _has_contact_information(resume_data)
        ),
        "quantified_achievements": (
            _has_quantified_achievements(resume_data)
        ),
        "action_oriented_experience": (
            _has_action_oriented_experience(resume_data)
        ),
        "project_description": (
            _has_project_description(resume_data)
        ),
    }

    warnings = []
    recommendations = []

    if not signals["contact_information"]:
        warnings.append(
            "Contact information is incomplete."
        )
        recommendations.append(
            "Add complete contact information, "
            "including email and phone number."
        )

    if not signals["quantified_achievements"]:
        warnings.append(
            "No quantified achievements were detected."
        )
        recommendations.append(
            "Add measurable results or metrics "
            "to experience achievements where applicable."
        )

    if not signals["action_oriented_experience"]:
        warnings.append(
            "Action-oriented experience statements "
            "were not detected."
        )
        recommendations.append(
            "Start experience bullets with strong "
            "action-oriented verbs where applicable."
        )

    if not signals["project_description"]:
        warnings.append(
            "Project descriptions are missing or limited."
        )
        recommendations.append(
            "Add a concise description of your "
            "projects and their impact."
        )

    score = round(
        (
            sum(signals.values())
            / len(signals)
        ) * 100
    )

    return {
        "score": score,
        "signals": signals,
        "warnings": warnings,
        "recommendations": recommendations,
    }