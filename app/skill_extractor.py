import re

from app.skill_dictionary import SKILL_DICTIONARY


def extract_skills(resume_text):
    """
    Extract skills from resume text using the skill dictionary.
    Matching is case-insensitive and based on whole words.
    """

    if not resume_text:
        return []

    found_skills = []

    for category_skills in SKILL_DICTIONARY.values():
        for skill in category_skills:
            pattern = r"\b" + re.escape(skill) + r"\b"

            if re.search(pattern, resume_text, re.IGNORECASE):
                found_skills.append(skill)

    return found_skills