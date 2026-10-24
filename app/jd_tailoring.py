
"""Deterministic job-description tailoring.

Only the order of existing resume content is changed, except that supported
competencies already stated in the resume may be added to the Skills section.

Nothing is invented: skills must be supported by the resume and relevant to
the target job description.
"""

import logging
import re
from copy import deepcopy

from app.section_parser import _FUNCTION_STEMS, text_stems

_LOG = logging.getLogger(__name__)

# Words that appear in nearly every job description and say little about
# the specific requirements.
_GENERIC_WORDS = {
    "experience", "experienced", "skills", "skill", "ability", "strong",
    "team", "teams", "work", "working", "build", "building", "develop",
    "developing", "design", "knowledge", "years", "year", "required",
    "preferred", "responsible", "responsibilities", "including", "related",
    "ensure", "support", "great", "good", "excellent", "communication",
    "environment", "solutions", "solution", "business", "role", "position",
    "candidate", "company", "engineer", "engineering", "using", "must",
    "will", "plus", "etc", "other", "new", "high", "quality", "projects",
    "project", "perform", "write", "help", "apply", "looking", "join",
}
_GENERIC_STEMS = {word[:5] for word in _GENERIC_WORDS}


def job_stems(job_description, target_job_title=""):
    """Return distinctive stems requested by the job description."""
    text = f"{target_job_title or ''} {job_description or ''}"
    return text_stems(text) - _FUNCTION_STEMS - _GENERIC_STEMS


def _phrase(text):
    """Normalize text for case-insensitive phrase comparisons."""
    return " " + re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip() + " "


def _skill_score(skill, jd_phrase, jd_stems):
    """Return 2 for a phrase match, 1 for a stem match, or 0 for no match."""
    phrase = _phrase(skill)

    if phrase.strip() and phrase in jd_phrase:
        return 2

    stems = text_stems(skill) - _FUNCTION_STEMS

    if stems and stems <= jd_stems:
        return 1

    return 0


def order_skills(skills, job_description, target_job_title=""):
    """Put job-relevant skills first while preserving other skills' order."""
    skills = [skill for skill in (skills or []) if isinstance(skill, str)]

    if not skills or not (job_description or target_job_title):
        return skills

    jd_phrase = _phrase(f"{target_job_title or ''} {job_description or ''}")
    jd_stems = job_stems(job_description, target_job_title)

    scored = [
        (-_skill_score(skill, jd_phrase, jd_stems), index, skill)
        for index, skill in enumerate(skills)
    ]
    ordered = [skill for _, _, skill in sorted(scored)]

    moved = sum(
        1 for original, reordered in zip(skills, ordered)
        if original != reordered
    )
    if moved:
        _LOG.info(
            "JD tailoring: reordered skills (%d position(s) changed).",
            moved,
        )

    return ordered


def _relevance(text, jd_stems):
    """Count the job-description stems present in a piece of resume text."""
    return len(text_stems(text) & jd_stems)


def order_bullets(bullets, jd_stems):
    """Order relevant bullets first; preserve a leading Technologies line."""
    bullets = list(bullets or [])

    if len(bullets) < 2 or not jd_stems:
        return bullets

    head = []
    if str(bullets[0]).lstrip("\u2022 -").lower().startswith("technologies"):
        head, bullets = [bullets[0]], bullets[1:]

    scored = [
        (-_relevance(bullet, jd_stems), index, bullet)
        for index, bullet in enumerate(bullets)
    ]

    return head + [bullet for _, _, bullet in sorted(scored)]


def order_entry_bullets(entries, job_description, target_job_title=""):
    """Return a copy of entries with each entry's bullets reordered."""
    if not isinstance(entries, list):
        return entries

    jd_stems = job_stems(job_description, target_job_title)
    result = []
    changed = 0

    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("bullets"), list):
            entry = deepcopy(entry)
            ordered = order_bullets(entry["bullets"], jd_stems)
            changed += ordered != entry["bullets"]
            entry["bullets"] = ordered

        result.append(entry)

    if changed:
        _LOG.info(
            "JD tailoring: reordered bullets in %d entr(ies).",
            changed,
        )

    return result


# ---------------------------------------------------------------------------
# Competencies explicitly listed in the resume
# ---------------------------------------------------------------------------

MAX_ADDED_SKILLS = 8

_SKILL_HEADINGS = {
    "core competencies",
    "technical skills",
    "skills",
    "key skills",
    "core skills",
    "technical competencies",
}
_OTHER_HEADINGS = {
    "projects",
    "education",
    "experience",
    "professional experience",
    "work experience",
    "certifications",
    "professional certifications",
    "professional summary",
    "summary",
    "achievements",
    "awards",
    "publications",
}

# Matches category lines such as "Programming: Python, SQL".
_CATEGORY_LINE = re.compile(r"^[A-Za-z][A-Za-z0-9 /&+.-]{0,40}:\s*")


def _split_items(text):
    """Split comma-separated competencies, preserving commas in parentheses."""
    items = []
    depth = 0
    current = ""

    for char in text:
        if char == "(":
            depth += 1
        elif char == ")" and depth > 0:
            depth -= 1

        if char == "," and depth == 0:
            items.append(current)
            current = ""
        else:
            current += char

    items.append(current)

    clean = []
    for item in items:
        # Remove explanatory parenthetical text, then normalize whitespace.
        item = re.sub(r"\s*\([^)]*\)", "", item)
        item = re.sub(r"\s+", " ", item).strip(" .;\u2022-")

        if item and re.search(r"[A-Za-z]", item) and len(item) <= 50:
            clean.append(item)

    return clean


def _is_category_label(item):
    """Identify a category label accidentally presented as a skill."""
    return bool(_CATEGORY_LINE.match(item))


def resume_competencies(resume_text):
    """Extract competencies from the resume's own skills section.

    Supports category lines such as "Programming: Python, SQL", plain
    comma-separated lists, and category values that wrap onto later lines.
    """
    entries = []
    current = ""
    in_section = False

    for raw in str(resume_text or "").splitlines():
        line = raw.strip()
        if not line:
            continue

        key = line.lower().rstrip(":")

        if key in _SKILL_HEADINGS:
            if current:
                entries.append(current)
                current = ""
            in_section = True
            continue

        if in_section and key in _OTHER_HEADINGS:
            if current:
                entries.append(current)
                current = ""
            break

        if not in_section:
            continue

        if _CATEGORY_LINE.match(line):
            if current:
                entries.append(current)

            # Keep only the category's value, never its label.
            current = line.split(":", 1)[1].strip()

        elif current.rstrip().endswith(","):
            current += " " + line

        else:
            if current:
                entries.append(current)
            current = line

    if current:
        entries.append(current)

    seen = set()
    result = []

    for entry in entries:
        for item in _split_items(entry):
            # Defensive guard against a category label surviving extraction.
            if _is_category_label(item):
                continue

            normalized = item.casefold()
            if normalized not in seen:
                seen.add(normalized)
                result.append(item)

    return result


def add_supported_competencies(
    skills,
    resume_text,
    job_description,
    target_job_title="",
    limit=MAX_ADDED_SKILLS,
):
    """Add resume-listed competencies relevant to the target job."""
    skills = [skill for skill in (skills or []) if isinstance(skill, str)]

    if not (job_description or target_job_title) or limit <= 0:
        return skills

    jd_phrase = _phrase(f"{target_job_title or ''} {job_description or ''}")
    jd_stems = job_stems(job_description, target_job_title)

    known = {
        _phrase(skill) for skill in skills
    } | {
        frozenset(text_stems(skill)) for skill in skills
    }

    added = []

    for item in resume_competencies(resume_text):
        if len(added) >= limit:
            break

        if _is_category_label(item):
            continue

        normalized_phrase = _phrase(item)
        normalized_stems = frozenset(text_stems(item))

        if normalized_phrase in known or normalized_stems in known:
            continue

        if _skill_score(item, jd_phrase, jd_stems) > 0:
            added.append(item)
            known.add(normalized_phrase)
            known.add(normalized_stems)

    if added:
        _LOG.info(
            "JD tailoring: added %d competency(ies) from the resume: %s",
            len(added),
            added,
        )

    return skills + added


# ---------------------------------------------------------------------------
# Professional summary
# ---------------------------------------------------------------------------

def order_summary(summary, job_description, target_job_title=""):
    """Order summary sentences by job relevance without changing their wording."""
    summary = str(summary or "").strip()

    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", summary)
        if sentence.strip()
    ]

    if len(sentences) < 2 or not (job_description or target_job_title):
        return summary

    jd_stems = job_stems(job_description, target_job_title)

    ordered = [
        sentence
        for _, _, sentence in sorted(
            (
                -_relevance(sentence, jd_stems),
                index,
                sentence,
            )
            for index, sentence in enumerate(sentences)
        )
    ]

    result = " ".join(ordered)

    # Safety net: preserve the exact whitespace-separated tokens.
    if sorted(result.split()) != sorted(summary.split()):
        return summary

    if result != summary:
        _LOG.info("JD tailoring: reordered summary sentences.")

    return result
