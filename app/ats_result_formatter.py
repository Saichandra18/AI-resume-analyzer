def format_ats_result(ats_result):
    """Format a raw ATS analysis result for user-facing consumption."""

    if not ats_result:
        ats_result = {}

    skills = ats_result.get("skills") or {}
    experience = ats_result.get("experience") or {}
    qualifications = ats_result.get("qualifications") or {}
    keywords = ats_result.get("keywords") or {}

    return {
        "ats_score": ats_result.get("ats_score", 0),

        "matched_skills": skills.get("matched", []),
        "missing_skills": skills.get("missing", []),

        "experience": {
            "required_years": experience.get("required_years"),
            "candidate_years": experience.get("candidate_years"),
            "meets_requirement": experience.get(
                "meets_requirement"
            ),
        },

        "matched_qualifications": qualifications.get(
            "matched", []
        ),
        "missing_qualifications": qualifications.get(
            "missing", []
        ),

        "matched_keywords": keywords.get("matched", []),
        "missing_keywords": keywords.get("missing", []),

        "component_scores": ats_result.get(
            "component_scores", {}
        ),

        "weights": ats_result.get("weights", {}),
    }