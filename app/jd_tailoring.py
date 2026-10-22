"""Deterministic job-description tailoring.

Only the *order* of things the resume already says is changed.  Nothing is
added, removed or reworded, so this can never introduce a claim the
candidate did not make - it just puts what matters for this job first.

    * skills the job asks for come first
    * within each job/project, bullets that match the job come first
      (so when a page limit forces a trim, the least relevant bullet is the
      one that goes)
"""

import logging
import re
from copy import deepcopy

from app.section_parser import _FUNCTION_STEMS, text_stems

_LOG = logging.getLogger(__name__)

# Words that appear in nearly every job description and say nothing about
# what the job needs.
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
    """Distinctive word stems the job description asks for."""
    text = f"{target_job_title or ''} {job_description or ''}"
    return text_stems(text) - _FUNCTION_STEMS - _GENERIC_STEMS


def _phrase(text):
    return " " + re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip() + " "


def _skill_score(skill, jd_phrase, jd_stems):
    """2 = the skill (as a phrase) is in the job, 1 = all its words are, 0 = no."""
    phrase = _phrase(skill)

    if phrase.strip() and phrase in jd_phrase:
        return 2

    stems = text_stems(skill) - _FUNCTION_STEMS

    if stems and stems <= jd_stems:
        return 1

    return 0


def order_skills(skills, job_description, target_job_title=""):
    """Put the skills the job asks for first; keep the rest in their order."""
    skills = [s for s in (skills or []) if isinstance(s, str)]

    if not skills or not (job_description or target_job_title):
        return skills

    jd_phrase = _phrase(f"{target_job_title or ''} {job_description or ''}")
    jd_stems = job_stems(job_description, target_job_title)

    scored = [
        (-_skill_score(skill, jd_phrase, jd_stems), index, skill)
        for index, skill in enumerate(skills)
    ]
    ordered = [skill for _, _, skill in sorted(scored)]

    moved = sum(1 for a, b in zip(skills, ordered) if a != b)
    if moved:
        _LOG.info("JD tailoring: reordered skills (%d position(s) changed).", moved)

    return ordered


def _relevance(text, jd_stems):
    return len(text_stems(text) & jd_stems)


def order_bullets(bullets, jd_stems):
    """Most job-relevant bullets first (stable); a leading "Technologies:" line stays first."""
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
    """`order_bullets` for every {"bullets": [...]} entry (a reordered copy)."""
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
        _LOG.info("JD tailoring: reordered bullets in %d entr(ies).", changed)

    return result
