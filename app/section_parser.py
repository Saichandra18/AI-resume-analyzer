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

# Words that normally follow a hyphen in a compound ("role-specific",
# "AI-powered"), so a line break after the hyphen must keep the hyphen.
_COMPOUND_TAILS = {
    "friendly", "powered", "driven", "specific", "based", "aware", "level",
    "time", "quality", "scale", "ready", "oriented", "centric", "wide",
    "first", "free", "grade", "tuned", "enabled", "native", "class", "end",
    "party", "facing", "aligned", "focused", "critical", "ended", "sourced",
}
# After a dangling hyphen these start a *new* word ("pre- and post-").
_SEPARATE_WORDS = {"and", "or", "to", "of", "the", "through", "for", "in"}


def hyphen_join(left, right):
    """Join text ending in '-' with the next line's text.

    "Process-" + "ing"          -> "Processing"      (word broken by wrapping)
    "ana-" + "lytical"          -> "analytical"
    "Retrieval-" + "Augmented"  -> "Retrieval-Augmented"
    "AI-" + "powered"           -> "AI-powered"
    "role-" + "specific"        -> "role-specific"
    "pre-" + "and post"         -> "pre- and post"
    """
    stem = left[:-1]
    tail = re.search(r"[A-Za-z]+$", stem)
    head = re.match(r"[A-Za-z]+", right)

    if not tail or not head:
        return left + right

    first_word = head.group(0)

    if first_word.lower() in _SEPARATE_WORDS:
        return left + " " + right

    if (
        tail.group(0).isupper()
        or first_word[0].isupper()
        or first_word.lower() in _COMPOUND_TAILS
    ):
        return left + right

    return stem + right


def repair_hyphen_breaks(text):
    """Re-join words that a PDF broke across lines (or left as 'Word- ing')."""
    if not text:
        return text

    # Require an actual break (newline or space) after the hyphen so that
    # normal compounds such as "cross-validation" are never touched.
    return re.sub(
        r"([A-Za-z]+-)(?:[ \t]*\n[ \t]*|[ \t]+)([A-Za-z]+)",
        lambda m: hyphen_join(m.group(1), m.group(2)),
        text,
    )


def _join_wrapped(previous, line):
    """Join a wrapped continuation line onto the previous text."""
    if previous.endswith("-") and len(previous) > 1 and previous[-2].isalpha():
        return hyphen_join(previous, line)
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


_LOG = logging.getLogger(__name__)

# A rewritten bullet replaces a source bullet only when the two clearly talk
# about the same thing (Dice similarity of their word stems).
MIN_BULLET_MATCH = 0.35
_STEM_LENGTH = 5


def _bullet_stems(text):
    return {
        word[:_STEM_LENGTH]
        for word in re.findall(r"[a-z0-9]{3,}", str(text).lower())
    }


def _similarity(first, second):
    a, b = _bullet_stems(first), _bullet_stems(second)

    if not a or not b:
        return 0.0

    return 2 * len(a & b) / (len(a) + len(b))


# ---------------------------------------------------------------------------
# Faithfulness: a rewrite may not add claims the source entry does not make
# ---------------------------------------------------------------------------

# A rewrite may introduce at most this many new content words (verb swaps
# such as "Performed" -> "Carried out" are fine; whole new claims are not).
MAX_NEW_TERMS = 2

_FUNCTION_WORDS = {
    "and", "the", "for", "with", "also", "while", "that", "this", "from",
    "into", "using", "use", "used", "its", "their", "through", "across",
    "such", "per", "via", "are", "was", "were", "has", "have", "had", "not",
    "but", "all", "any", "can", "our", "out", "over", "under", "between",
    "within", "both", "of", "to", "in", "on", "by", "as", "at", "an", "or",
}
_FUNCTION_STEMS = {word[:_STEM_LENGTH] for word in _FUNCTION_WORDS}

# Claims of leading or owning work must already be in the source entry.
_OWNERSHIP_VERBS = {
    "managed", "manage", "led", "lead", "owned", "directed", "spearheaded",
    "oversaw", "headed", "architected", "orchestrated",
}
_WEAK_OPENERS = {
    "contributed", "assisted", "supported", "helped", "participated", "aided",
}
_STRONG_OPENERS = {
    "developed", "built", "led", "designed", "architected", "created",
    "implemented", "engineered", "managed", "owned", "spearheaded",
    "delivered", "launched", "established",
}


def _words(text):
    return re.findall(r"[a-z][a-z-]*", str(text).lower())


def is_faithful_rewrite(rewritten, source_bullet, entry_text):
    """True when `rewritten` makes no claim the source entry does not make.

    Rejects: a weak opener upgraded to a strong one ("Contributed" ->
    "Developed"), new ownership claims ("managed"), and rewrites that add
    more than MAX_NEW_TERMS content words absent from the whole source entry
    ("... and automated detection tools").
    """
    new_words = _words(rewritten)
    source_words = _words(source_bullet)
    entry_words = set(_words(entry_text))

    if new_words and source_words:
        if source_words[0] in _WEAK_OPENERS and new_words[0] in _STRONG_OPENERS:
            return False

    if {w for w in new_words if w in _OWNERSHIP_VERBS} - entry_words:
        return False

    novel = (
        _bullet_stems(rewritten)
        - _bullet_stems(entry_text)
        - _FUNCTION_STEMS
    )

    return len(novel) <= MAX_NEW_TERMS


def text_stems(text):
    """Distinctive word stems (first 5 letters, 3+ letter words) of a text."""
    return _bullet_stems(text)


def text_similarity(first, second):
    """Dice similarity (0..1) of the word stems of two texts."""
    return _similarity(first, second)


def _align_bullets(source_bullets, candidates, entry_text=""):
    """Pair each source bullet with its best-matching rewritten bullet.

    The result always has exactly one bullet per source bullet: the rewrite
    when one clearly corresponds to it, otherwise the source bullet itself.
    Rewritten bullets that match nothing (for example project bullets a
    model wandered into a job's answer) are ignored.

    A matched rewrite is used only if it is faithful to the source entry
    (see `is_faithful_rewrite`); otherwise the source bullet is kept.

    Returns (bullets, ignored_rewrites, kept_source_bullets).
    """
    pairs = sorted(
        (
            (-_similarity(source, candidate), i, j)
            for i, source in enumerate(source_bullets)
            for j, candidate in enumerate(candidates)
        )
    )

    chosen = {}
    used = set()

    for negative_score, i, j in pairs:
        if -negative_score < MIN_BULLET_MATCH:
            break
        if i in chosen or j in used:
            continue
        used.add(j)
        if entry_text and not is_faithful_rewrite(
            candidates[j], source_bullets[i], entry_text
        ):
            continue
        chosen[i] = candidates[j]

    bullets = [chosen.get(i, source) for i, source in enumerate(source_bullets)]

    return (
        bullets,
        len(candidates) - len(used),
        len(source_bullets) - len(chosen),
    )


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


def merge_rewritten_entries(source_entries, rewritten_items):
    """Re-attach rewritten bullets to the *source* entry headers.

    * Headers (title, company, location, dates) always come from the source.
    * Output has exactly one entry per source entry - a rewrite can never
      duplicate, reorder, or invent entries.
    * Each source bullet is paired with the rewritten bullet that clearly
      corresponds to it; unmatched source bullets are kept as written and
      unrelated rewritten bullets are ignored, so an entry never grows,
      shrinks, or absorbs another section's content.
    * Falls back to the source bullets when the rewrite is missing, empty,
      contains unsupported claims, or contains another entry's title.
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
                candidates = _bullets_from_rewrite(joined, source)

                if candidates and source_bullets:
                    entry_text = " ".join(
                        [str(source.get("title", "")), str(source.get("company", ""))]
                        + source_bullets
                    )
                    bullets, ignored, kept = _align_bullets(
                        source_bullets,
                        candidates,
                        entry_text,
                    )

                    if ignored or kept:
                        _LOG.warning(
                            "Entry %d: ignored %d unrelated rewritten bullet(s); "
                            "kept %d original bullet(s).",
                            index, ignored, kept,
                        )
                elif candidates:
                    bullets = candidates

        entry["bullets"] = bullets or source_bullets
        merged.append(entry)

    return merged
