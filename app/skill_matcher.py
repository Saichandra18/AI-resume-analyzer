def normalize_skill(skill):
    """Normalize a skill for comparison."""
    return skill.strip().lower()


def match_skills(resume_skills, required_skills):
    """Compare resume skills against required job skills."""

    resume_skills = resume_skills or []
    required_skills = required_skills or []

    normalized_resume_skills = {
        normalize_skill(skill)
        for skill in resume_skills
        if skill
    }

    matched = []
    missing = []

    for skill in required_skills:
        if not skill:
            continue

        normalized_skill = normalize_skill(skill)

        if normalized_skill in normalized_resume_skills:
            matched.append(skill)
        else:
            missing.append(skill)

    return {
        "matched": matched,
        "missing": missing,
    }