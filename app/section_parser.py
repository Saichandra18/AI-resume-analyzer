"""Deterministic parsing of resume Experience and Projects sections.

The extractors hand the pipeline *flat lists of text lines*.  Everything
downstream used to guess which line was a title, which was a bullet and
which was the wrapped tail of a bullet.  This module does that once, at the
source, and produces structured entries:

    experience entry: {"title", "company", "location", "dates", "bullets"}
    project entry:    {"title", "bullets"}

It also provides `merge_rewritten_entries`, which re-attaches the rewritten
bullets to the *source* entry headers by position, so a rewrite can never
duplicate, reorder, rename or mix entries.
"""

import logging
import math
import re
from copy import deepcopy

# A line starts a bullet when it begins with a bullet glyph (or a dash that
# is followed by whitespace).
_BULLET_RE = re.compile(r"^\s*(?:[\u2022\u25CF\u25AA\u25E6\u2219\u00B7*\uf0b7]|[-\u2013\u2014](?=\s))\s*")

# PDF lines wrap at roughly this many characters.  A line that is at least
# this long and does not end a sentence is probably wrapped onto the next line.
_WRAP_WIDTH = 70
_TERMINAL = (".", "!", "?")

_MONTH = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|"
    r"Dec(?:ember)?)"
)
_DATE = rf"(?:{_MONTH}\.?\s*\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}})"
_END = rf"(?:Present|Current|Now|Ongoing|{_DATE})"
# NOTE: no leading word boundary on purpose.  PDF extraction often glues the
# company and the start date together ("OutlierSep 2023 - Present").
_RANGE_RE = re.compile(rf"({_DATE})\s*[\u2013\u2014-]+\s*({_END})\s*$", re.IGNORECASE)
_TITLE_COMPANY_SPLIT = re.compile(r"\s+[\u2013\u2014@|-]\s+|\s*\|\s*|\s+at\s+")


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _join_wrapped(previous, line):
    """Join a wrapped continuation line onto the previous text."""
    if previous.endswith("-") and len(previous) > 1 and previous[-2].isalpha():
        if line[:1].islower():
            # "ana-" + "lytical" -> "analytical"
            return previous[:-1] + line
        # "Retrieval-" + "Augmented" -> "Retrieval-Augmented"
        return previous + line
    return previous + " " + line


def _looks_like_continuation(previous, line):
    if line[:1].islower():
        return True
    text = previous["text"]
    if text.endswith("-"):
        return True
    return (
        previous["raw_len"] >= _WRAP_WIDTH
        and not text.endswith(_TERMINAL)
    )


def tokenize_lines(lines):
    """Turn raw lines into ordered tokens.

    Each token is {"kind": "bullet" | "text", "text": str}.  Wrapped bullet
    lines are merged into their bullet, so "...consistency, and backward" +
    "compatibility." becomes one bullet.
    """
    tokens = []

    for raw in lines or []:
        line = str(raw).strip()
        if not line:
            continue

        match = _BULLET_RE.match(line)

        if match:
            content = line[match.end():].strip()
            if content:
                tokens.append({
                    "kind": "bullet",
                    "text": content,
                    "raw_len": len(line),
                })
            continue

        previous = tokens[-1] if tokens else None

        if (
            previous is not None
            and previous["kind"] == "bullet"
            and _looks_like_continuation(previous, line)
        ):
            previous["text"] = _join_wrapped(previous["text"], line)
            previous["raw_len"] = len(line)
            continue

        tokens.append({
            "kind": "text",
            "text": line,
            "raw_len": len(line),
        })

    return tokens


def _norm(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def parse_project_entries(lines):
    """Group flat project lines into [{"title", "bullets"}]."""
    entries = []
    current = None

    for token in tokenize_lines(lines):
        if token["kind"] == "text":
            if current is not None and not current["bullets"]:
                # Second heading-like line before any bullet: wrapped title.
                current["title"] = _join_wrapped(
                    current["title"],
                    token["text"],
                )
            else:
                current = {"title": token["text"], "bullets": []}
                entries.append(current)
        else:
            if current is None:
                current = {"title": "", "bullets": []}
                entries.append(current)
            current["bullets"].append(token["text"])

    return [e for e in entries if e["title"] or e["bullets"]]


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

def _parse_experience_header(header_lines):
    title = company = location = dates = ""
    remaining = []

    for index, line in enumerate(header_lines):
        match = _RANGE_RE.search(line)

        if match and not dates:
            dates = line[match.start():].strip()
            line = line[:match.start()].strip(" \u2013\u2014-|,")

        if not line:
            continue

        if index == 0 or not (title or company):
            parts = _TITLE_COMPANY_SPLIT.split(line, maxsplit=1)
            title = parts[0].strip()
            if len(parts) > 1:
                company = parts[1].strip()
        else:
            remaining.append(line)

    # First leftover short line is normally the location.
    for line in remaining:
        if not location and len(line) <= 60:
            location = line
        elif not company:
            company = line

    return {
        "title": title,
        "company": company,
        "location": location,
        "dates": dates,
    }


def parse_experience_entries(lines):
    """Group flat experience lines into structured job entries.

    Returns [] when the section has no bullets, so callers can fall back to
    the legacy flat behaviour instead of guessing.
    """
    tokens = tokenize_lines(lines)

    if not any(token["kind"] == "bullet" for token in tokens):
        return []

    entries = []
    header_lines = []
    current = None

    for token in tokens:
        if token["kind"] == "text":
            if current is not None and current["bullets"]:
                # Header text after bullets starts a new job.
                current = None
                header_lines = []
            header_lines.append(token["text"])
        else:
            if current is None:
                current = _parse_experience_header(header_lines)
                current["bullets"] = []
                entries.append(current)
                header_lines = []
            current["bullets"].append(token["text"])

    return entries


# ---------------------------------------------------------------------------
# Attach entries to resume_data
# ---------------------------------------------------------------------------

def attach_entries(resume_data):
    """Add structured entries to resume_data in place (additive, idempotent).

    experience["entries"] and resume_data["project_entries"] are added; the
    legacy flat keys are left untouched for the ATS analyzer.
    """
    if not isinstance(resume_data, dict):
        return resume_data

    experience = resume_data.get("experience")

    if isinstance(experience, dict) and not experience.get("entries"):
        entries = parse_experience_entries(experience.get("section") or [])
        if entries:
            experience["entries"] = entries

    projects = resume_data.get("projects")

    if (
        isinstance(projects, list)
        and projects
        and all(isinstance(item, str) for item in projects)
        and not resume_data.get("project_entries")
    ):
        entries = parse_project_entries(projects)
        if entries:
            resume_data["project_entries"] = entries

    return resume_data


def get_experience_entries(resume_data):
    experience = (resume_data or {}).get("experience")
    if isinstance(experience, dict):
        entries = experience.get("entries")
        if isinstance(entries, list):
            return [e for e in entries if isinstance(e, dict)]
    return []


def get_project_entries(resume_data):
    entries = (resume_data or {}).get("project_entries")
    if isinstance(entries, list):
        return [e for e in entries if isinstance(e, dict)]
    return []


# ---------------------------------------------------------------------------
# Prompt formatting and rewrite merging
# ---------------------------------------------------------------------------

def entry_to_block(entry):
    """Render one structured entry as a text block for an LLM prompt."""
    header_parts = [
        entry.get("title"),
        entry.get("company"),
        entry.get("location"),
        entry.get("dates"),
    ]
    header = " | ".join(str(part) for part in header_parts if part)
    lines = [header] if header else []
    lines.extend(f"\u2022 {bullet}" for bullet in entry.get("bullets", []))
    return "\n".join(lines)


def format_items_for_prompt(items):
    """Present a list of block strings as clearly separated ITEMs."""
    if (
        isinstance(items, list)
        and items
        and all(isinstance(item, str) for item in items)
    ):
        return "\n\n".join(
            f"--- ITEM {index} ---\n{item}"
            for index, item in enumerate(items, start=1)
        )
    return items


def _rewritten_text(item):
    if isinstance(item, dict):
        return str(item.get("rewritten") or item.get("description") or "")
    return item if isinstance(item, str) else ""


def _has_unsupported_claims(item):
    if not isinstance(item, dict):
        return False
    validation = item.get("validation")
    return bool(
        isinstance(validation, dict)
        and validation.get("unsupported_claims")
    )


def _header_like(line, source):
    line_key = _norm(line)
    if not line_key:
        return False
    for field in ("title", "company"):
        value = _norm(source.get(field))
        if value and value in line_key:
            return True
    return False


def _bullets_from_rewrite(text, source):
    tokens = tokenize_lines(str(text).splitlines())
    bullets = [t["text"] for t in tokens if t["kind"] == "bullet"]

    if not bullets:
        texts = [t["text"] for t in tokens]
        if len(texts) > 1 and _header_like(texts[0], source):
            texts = texts[1:]
        bullets = texts

    seen = set()
    unique = []
    for bullet in bullets:
        key = _norm(bullet)
        if key and key not in seen:
            seen.add(key)
            unique.append(bullet)

    return unique


# A rewrite that keeps fewer than this share of the source bullets is treated
# as lossy and the source bullets are used instead.
MIN_BULLET_COVERAGE = 0.6

_LOG = logging.getLogger(__name__)


def _group_rewritten_items(source_entries, rewritten_items):
    """Return one list of rewritten items per source entry.

    The model is asked for one item per entry, but some answer with one item
    per bullet.  Items are therefore grouped, never dropped:

    * same count as the sources      -> positional
    * a single source entry          -> every item belongs to it
    * several entries, counts differ -> align by title; unmatched items are
                                        attached to the entry before them
    """
    count = len(source_entries)
    groups = [[] for _ in source_entries]

    if not rewritten_items or not count:
        return groups

    if len(rewritten_items) == count:
        return [[item] for item in rewritten_items]

    if count == 1:
        return [list(rewritten_items)]

    titles = [_norm(entry.get("title")) for entry in source_entries]
    current = None

    for item in rewritten_items:
        text = _rewritten_text(item).strip()
        first_line = _norm(text.splitlines()[0]) if text else ""

        for index, title in enumerate(titles):
            if title and first_line and (title in first_line or first_line == title):
                current = index
                break

        if current is not None:
            groups[current].append(item)

    return groups


def _covers(candidate_bullets, source_bullets):
    if not source_bullets:
        return bool(candidate_bullets)
    needed = math.ceil(MIN_BULLET_COVERAGE * len(source_bullets))
    return len(candidate_bullets) >= needed


def merge_rewritten_entries(source_entries, rewritten_items):
    """Re-attach rewritten bullets to the *source* entry headers.

    * Headers (title, company, location, dates) always come from the source.
    * Output has exactly one entry per source entry - a rewrite can never
      duplicate, reorder, or invent entries.
    * Falls back to the source bullets when the rewrite is missing, empty,
      lossy (keeps too few bullets), contains unsupported claims, or
      contains another entry's title.
    """
    rewritten_items = rewritten_items if isinstance(rewritten_items, list) else []
    groups = _group_rewritten_items(source_entries, rewritten_items)
    merged = []

    for index, source in enumerate(source_entries):
        entry = {k: deepcopy(v) for k, v in source.items() if k != "bullets"}
        source_bullets = list(source.get("bullets", []))
        bullets = None
        group = groups[index]

        if group:
            joined = "\n".join(
                text for text in (_rewritten_text(item) for item in group)
                if text.strip()
            )
            other_titles = [
                _norm(other.get("title"))
                for other_index, other in enumerate(source_entries)
                if other_index != index and _norm(other.get("title"))
            ]
            joined_key = _norm(joined)
            mixed = any(title in joined_key for title in other_titles)
            unsupported = any(_has_unsupported_claims(item) for item in group)

            if joined.strip() and not unsupported and not mixed:
                candidate = _bullets_from_rewrite(joined, source)
                if candidate and _covers(candidate, source_bullets):
                    bullets = candidate
                else:
                    _LOG.warning(
                        "Rewrite kept %d of %d bullets for entry %d; using source bullets.",
                        len(candidate or []), len(source_bullets), index,
                    )

        entry["bullets"] = bullets or source_bullets
        merged.append(entry)

    return merged
