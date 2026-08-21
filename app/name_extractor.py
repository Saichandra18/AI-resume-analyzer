import re

from app.skill_dictionary import SKILL_DICTIONARY


COMMON_HEADINGS = {
    "resume",
    "cv",
    "curriculum vitae",
    "curriculum-vitae",
    "profile",
    "professional profile",
}


COMMON_JOB_TITLES = {
    "data analyst",
    "data scientist",
    "software engineer",
    "software developer",
    "python developer",
    "web developer",
    "machine learning engineer",
    "ml engineer",
    "ai engineer",
    "ai developer",
    "full stack developer",
    "frontend developer",
    "backend developer",
    "business analyst",
    "project manager",
    "product manager",
    "devops engineer",
    "system administrator",
    "database administrator",
}


def contains_known_skill(text):
    """Check whether a line contains a known technical skill."""

    text_lower = text.lower()

    for category_skills in SKILL_DICTIONARY.values():
        for skill in category_skills:
            pattern = r"\b" + re.escape(skill.lower()) + r"\b"

            if re.search(pattern, text_lower):
                return True

    return False


def extract_name(text):
    """Extract a likely candidate name from the beginning of a resume."""

    if not text:
        return None

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines[:10]:
        cleaned_line = line.strip(":-| ")

        if not cleaned_line:
            continue

        if cleaned_line.lower() in COMMON_HEADINGS:
            continue

        if cleaned_line.lower() in COMMON_JOB_TITLES:
            continue

        if contains_known_skill(cleaned_line):
            continue

        if "@" in cleaned_line:
            continue

        if re.search(r"\d", cleaned_line):
            continue

        words = cleaned_line.split()

        if 2 <= len(words) <= 4:
            if all(
                re.fullmatch(r"[A-Za-z]+(?:[-'][A-Za-z]+)?", word)
                for word in words
            ):
                return cleaned_line

    return None