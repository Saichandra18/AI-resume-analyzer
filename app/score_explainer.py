def explain_ats_score(ats_result):
    """Explain how the ATS score is composed."""

    if not ats_result:
        return {
            "ats_score": 0,
            "components": {},
            "total_contribution": 0.0,
        }

    ats_score = ats_result.get("ats_score", 0)
    component_scores = ats_result.get("component_scores", {})
    weights = ats_result.get("weights", {})

    if not component_scores:
        return {
            "ats_score": ats_score,
            "components": {},
            "total_contribution": 0.0,
        }

    components = {}
    total_contribution = 0.0

    for component, score in component_scores.items():
        if score is None:
            components[component] = {
                "score": None,
                "weight": None,
                "contribution": None,
            }
            continue

        weight = weights.get(component)

        if weight is None:
            components[component] = {
                "score": score,
                "weight": None,
                "contribution": None,
            }
            continue

        contribution = score * (weight / 100)

        components[component] = {
            "score": score,
            "weight": weight,
            "contribution": round(contribution, 2),
        }

        total_contribution += contribution

    return {
        "ats_score": ats_score,
        "components": components,
        "total_contribution": round(total_contribution, 2),
    }