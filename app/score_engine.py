BASE_WEIGHTS = {
    "skills": 50.0,
    "experience": 20.0,
    "qualifications": 15.0,
    "keywords": 15.0,
}


def calculate_match_percentage(matched, total):
    """Calculate a percentage from matched and total items."""

    if not total:
        return None

    return (len(matched) / len(total)) * 100


def calculate_experience_score(experience_result):
    """Calculate the experience component score."""

    if not experience_result:
        return None

    required_years = experience_result.get("required_years")

    if required_years is None:
        return None

    if experience_result.get("meets_requirement") is True:
        return 100.0

    return 0.0


def calculate_qualification_score(qualification_result):
    """Calculate the qualification component score."""

    if not qualification_result:
        return None

    matched = qualification_result.get("matched", [])
    missing = qualification_result.get("missing", [])

    total = len(matched) + len(missing)

    if total == 0:
        return None

    return (len(matched) / total) * 100


def calculate_skill_score(skill_result):
    """Calculate the skill component score."""

    if not skill_result:
        return None

    matched = skill_result.get("matched", [])
    missing = skill_result.get("missing", [])

    total = len(matched) + len(missing)

    if total == 0:
        return None

    return (len(matched) / total) * 100


def calculate_keyword_score(keyword_result):
    """Calculate the keyword component score."""

    if not keyword_result:
        return None

    matched = keyword_result.get("matched", [])
    missing = keyword_result.get("missing", [])

    total = len(matched) + len(missing)

    if total == 0:
        return None

    return (len(matched) / total) * 100


def calculate_normalized_weights(component_scores):
    """Normalize weights across available scoring components."""

    available_components = [
        component
        for component, score in component_scores.items()
        if score is not None
    ]

    if not available_components:
        return {}

    total_weight = sum(
        BASE_WEIGHTS[component]
        for component in available_components
    )

    return {
        component: (
            BASE_WEIGHTS[component] / total_weight
        ) * 100
        for component in available_components
    }


def calculate_ats_score(
    skill_result,
    experience_result,
    qualification_result,
    keyword_result,
):
    """Calculate the final ATS score."""

    component_scores = {
        "skills": calculate_skill_score(skill_result),
        "experience": calculate_experience_score(
            experience_result
        ),
        "qualifications": calculate_qualification_score(
            qualification_result
        ),
        "keywords": calculate_keyword_score(
            keyword_result
        ),
    }

    weights = calculate_normalized_weights(component_scores)

    if not weights:
        return {
            "ats_score": 0,
            "component_scores": component_scores,
            "weights": {},
        }

    weighted_score = 0.0

    for component, weight in weights.items():
        weighted_score += (
            component_scores[component]
            * (weight / 100)
        )

    return {
        "ats_score": round(weighted_score),
        "component_scores": component_scores,
        "weights": weights,
    }