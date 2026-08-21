import re

from app.skill_dictionary import SKILL_DICTIONARY


def extract_required_skills(job_description):
    """Extract skills from a job description using the skill dictionary."""

    if not job_description:
        return []

    found_skills = []

    for skills in SKILL_DICTIONARY.values():
        for skill in skills:
            # Escape the skill so characters such as + and . are treated literally.
            pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

            if re.search(pattern, job_description, re.IGNORECASE):
                found_skills.append(skill)

    return found_skills