"""Parse flat resume section lines into structured entries."""

import re


_BULLET_RE = re.compile(
    r"^\s*(?:[-*•●▪◦‣]|\?|\u00e2\u20ac\u00a2)\s*"
)

_DATE_RE = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|"
    r"Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–—]\s*"
    r"(?:Present|Current|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|"
    r"Oct|Nov|Dec)[a-z]*\.?\s+\d{4}))\b",
    re.IGNORECASE,
)


def _clean_line(value):
    """Normalize whitespace without changing factual content."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _is_bullet(line):
    """Return True when a line begins with a recognized bullet marker."""
    return bool(_BULLET_RE.match(line))


def _remove_bullet(line):
    """Remove only the leading bullet marker."""
    return _BULLET_RE.sub("", line, count=1).strip()


def _join_wrapped_lines(lines):
    """Join continuation lines and repair words split by hyphens."""
    result = []

    for raw_line in lines:
        line = _clean_line(raw_line)
        if not line:
            continue

        if result and result[-1].endswith("-"):
            result[-1] = result[-1][:-1] + line
        elif result:
            result[-1] += " " + line
        else:
            result.append(line)

    return result


def parse_project_entries(lines):
    """
    Parse flat project-section lines into dictionaries.

    Each unbulleted heading begins a new project. Bullet lines and wrapped
    continuation lines belong to the current project.
    """
    projects = []
    current = None

    for raw_line in lines or []:
        line = _clean_line(raw_line)
        if not line:
            continue

        if _is_bullet(line):
            bullet = _remove_bullet(line)
            if current is None:
                current = {"title": "", "bullets": []}
                projects.append(current)
            if bullet:
                current["bullets"].append(bullet)
            continue

        # A non-bullet line starts a project or continues its description.
        # Known metadata labels stay attached to the current project.
        if current is None:
            current = {"title": line, "bullets": []}
            projects.append(current)
        elif not current["title"]:
            current["title"] = line
        elif line.lower().startswith(
            ("technologies:", "technology:", "tech stack:")
        ):
            current.setdefault("technologies", []).append(line)
        elif not current["bullets"]:
            # Additional heading text before the first bullet.
            current["title"] = f"{current['title']} {line}".strip()
        else:
            previous_bullet = (
                current["bullets"][-1]
                if current["bullets"]
                else ""
            )

            # A lowercase continuation such as "compatibility."
            # belongs to the previous bullet.
            is_continuation = (
                bool(previous_bullet)
                and line[:1].islower()
                and not previous_bullet.endswith((".", "!", "?"))
            )

            if is_continuation:
                current["bullets"][-1] += " " + line
            else:
                # A new heading starts a separate project.
                current = {
                    "title": line,
                    "bullets": [],
                }
                projects.append(current)

    for project in projects:
        project["title"] = _clean_line(project["title"])
        project["bullets"] = [
            _clean_line(bullet) for bullet in project["bullets"] if _clean_line(bullet)
        ]
        if "technologies" in project:
            project["technologies"] = [
                _clean_line(item) for item in project["technologies"]
            ]

    return [
        project
        for project in projects
        if project["title"] or project["bullets"]
    ]


def _split_experience_header(header):
    """
    Extract role, employer and dates from a combined header when possible.

    Example:
        Freelance LLM Trainer – OutlierSep 2023 – Present
    """
    header = _clean_line(header)
    dates = ""

    date_match = _DATE_RE.search(header)
    if date_match:
        dates = date_match.group(0).strip()
        before_dates = header[:date_match.start()].strip()
    else:
        before_dates = header

    before_dates = before_dates.rstrip(" |,–—-")

    title = before_dates
    company = ""

    # Handle common separators between role and employer.
    for separator in (" | ", " – ", " — ", " - "):
        if separator in before_dates:
            possible_title, possible_company = before_dates.rsplit(
                separator, 1
            )
            if possible_title.strip() and possible_company.strip():
                title = possible_title.strip()
                company = possible_company.strip()
                break

    # Repair a company/date boundary such as "OutlierSep 2023".
    if not company:
        glued = re.search(
            r"\b([A-Z][A-Za-z0-9.& ]+?)"
            r"(?=(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*\.?\s+\d{4})",
            before_dates,
        )
        if glued:
            company = glued.group(1).strip()
            title = before_dates[:glued.start()].rstrip(" |,–—-")

    return {
        "title": _clean_line(title),
        "company": _clean_line(company),
        "dates": _clean_line(dates),
    }


def parse_experience_entries(lines):
    """
    Parse experience lines into structured role entries.

    Expected layout: role/employer/date header, optional location line,
    then bullets. This function deliberately preserves the source wording.
    """
    entries = []
    current = None

    for raw_line in lines or []:
        line = _clean_line(raw_line)
        if not line:
            continue

        if _is_bullet(line):
            bullet = _remove_bullet(line)
            if current is None:
                current = {
                    "title": "",
                    "company": "",
                    "location": "",
                    "dates": "",
                    "bullets": [],
                }
                entries.append(current)
            if bullet:
                current["bullets"].append(bullet)
            continue

        if current is None or current["bullets"]:
            fields = _split_experience_header(line)
            current = {
                **fields,
                "location": "",
                "bullets": [],
            }
            entries.append(current)
            continue

        if not current["location"]:
            current["location"] = line
        else:
            current["bullets"].append(line)

    for entry in entries:
        entry["bullets"] = [
            _clean_line(bullet)
            for bullet in entry["bullets"]
            if _clean_line(bullet)
        ]

    return [
        entry
        for entry in entries
        if entry["title"] or entry["company"] or entry["bullets"]
    ]
