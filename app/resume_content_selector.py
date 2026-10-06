"""Deterministic content selection for JD-optimized resumes."""

from copy import deepcopy
import re


def _normalize_text(value):
    """Normalize arbitrary text for matching."""

    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        value = " ".join(str(item) for item in value)

    return re.sub(
        r"\s+",
        " ",
        str(value).lower(),
    ).strip()


def _tokenize(value):
    """Return normalized word tokens."""

    text = _normalize_text(value)

    return set(
        re.findall(
            r"[a-z0-9+#.-]+",
            text,
        )
    )


def _extract_item_text(item):
    """Extract searchable text from a resume item."""

    if item is None:
        return ""

    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        parts = []

        for key, value in item.items():
            if value is None:
                continue

            if isinstance(value, (list, tuple, set)):
                parts.extend(
                    str(v)
                    for v in value
                    if v is not None
                )
            elif isinstance(value, dict):
                parts.append(
                    " ".join(
                        str(v)
                        for v in value.values()
                        if v is not None
                    )
                )
            else:
                parts.append(str(value))

        return " ".join(parts)

    return str(item)


def _overlap_score(item_tokens, target_tokens):
    """Return percentage overlap between two token sets."""

    if not target_tokens:
        return 0.0

    overlap = item_tokens & target_tokens

    return (
        len(overlap) / len(target_tokens)
    ) * 100


def score_content(
    item,
    target_keywords=None,
    target_skills=None,
    relevance_score=0,
):
    """
    Calculate a deterministic 0-100 score for one item.

    The score combines:
    - JD keyword overlap
    - skill overlap
    - supplied relevance score
    - basic content-quality signal
    """

    target_keywords = target_keywords or []
    target_skills = target_skills or []

    item_text = _extract_item_text(item)
    item_tokens = _tokenize(item_text)

    keyword_tokens = _tokenize(
        target_keywords
    )
    skill_tokens = _tokenize(
        target_skills
    )

    keyword_score = _overlap_score(
        item_tokens,
        keyword_tokens,
    )

    skill_score = _overlap_score(
        item_tokens,
        skill_tokens,
    )

    try:
        relevance = float(
            relevance_score
        )
    except (TypeError, ValueError):
        relevance = 0.0

    relevance = max(
        0.0,
        min(100.0, relevance),
    )

    text_length = len(
        _normalize_text(item_text)
    )

    if text_length == 0:
        quality_score = 0.0
    elif text_length < 20:
        quality_score = 40.0
    elif text_length < 80:
        quality_score = 70.0
    else:
        quality_score = 100.0

    score = (
        keyword_score * 0.30
        + skill_score * 0.35
        + relevance * 0.25
        + quality_score * 0.10
    )

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


def rank_content(
    items,
    target_keywords=None,
    target_skills=None,
    relevance_scores=None,
):
    """
    Rank content deterministically.

    Returns a new list and never mutates the input.
    """

    items = deepcopy(items or [])
    relevance_scores = (
        relevance_scores or {}
    )

    ranked = []

    for index, item in enumerate(items):
        relevance = relevance_scores.get(
            index,
            0,
        )

        score = score_content(
            item=item,
            target_keywords=target_keywords,
            target_skills=target_skills,
            relevance_score=relevance,
        )

        ranked.append(
            {
                "item": item,
                "score": score,
                "original_index": index,
            }
        )

    ranked.sort(
        key=lambda entry: (
            -entry["score"],
            entry["original_index"],
        )
    )

    return ranked


def select_content(
    items,
    target_keywords=None,
    target_skills=None,
    relevance_scores=None,
    max_items=None,
):
    """
    Select the highest-ranked content items.

    Returns:
        {
            "selected": [...],
            "excluded": [...],
        }
    """

    ranked = rank_content(
        items=items,
        target_keywords=target_keywords,
        target_skills=target_skills,
        relevance_scores=relevance_scores,
    )

    if max_items is None:
        selected = ranked
        excluded = []
    else:
        if not isinstance(
            max_items,
            int,
        ) or max_items < 0:
            raise ValueError(
                "max_items must be a non-negative integer or None."
            )

        selected = ranked[:max_items]
        excluded = ranked[max_items:]

    return {
        "selected": selected,
        "excluded": excluded,
    }