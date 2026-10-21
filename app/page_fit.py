"""Fit a generated resume to the requested number of pages.

The renderer lays text out once; nothing used to react when the result came
out longer than the page target (one stray line on page 2, for example).
This module renders, measures, and then makes the *least destructive*
change that works:

    1. normal layout
    2. slightly tighter vertical spacing (font sizes are never reduced)
    3. drop the lowest-priority bullet, one at a time (last resort)
"""

import logging
from copy import deepcopy

from app.rendered_document_validator import count_pdf_pages
from app.resume_pdf_renderer import render_final_resume_pdf

_LOG = logging.getLogger(__name__)

# Never trim an entry below this many bullets.
MIN_PROJECT_BULLETS = 3
MIN_JOB_BULLETS = 4
MAX_TRIMS = 6


def trim_one_bullet(resume):
    """Remove the last (lowest-priority) bullet of the least important entry.

    Projects are trimmed before jobs, starting from the last entry.
    Returns (trimmed_copy, info) or (None, None) when nothing can be trimmed.
    """
    candidate = deepcopy(resume)

    for section, minimum in (
        ("projects", MIN_PROJECT_BULLETS),
        ("experience", MIN_JOB_BULLETS),
    ):
        for entry in reversed(getattr(candidate, section, None) or []):
            bullets = entry.get("bullets") if isinstance(entry, dict) else None

            if isinstance(bullets, list) and len(bullets) > minimum:
                removed = bullets.pop()
                return candidate, {
                    "section": section,
                    "title": entry.get("title", ""),
                    "bullet": removed,
                }

    return None, None


def fit_pdf_to_pages(
    resume,
    pdf_path,
    target_pages,
    template="default",
    render=None,
    count_pages=None,
    max_trims=MAX_TRIMS,
):
    """Render `resume` to `pdf_path` and make it fit `target_pages`.

    Returns (resume, pdf_path, report).  `resume` is a trimmed copy only when
    bullets had to be removed; `report` says exactly what was done.
    """
    render = render or render_final_resume_pdf
    count_pages = count_pages or count_pdf_pages

    report = {
        "target_pages": target_pages,
        "compact_spacing": False,
        "trimmed": [],
        "actual_pages": None,
    }

    path = render(resume=resume, output_path=pdf_path, template=template)
    pages = count_pages(path)

    if pages > target_pages:
        report["compact_spacing"] = True
        path = render(
            resume=resume,
            output_path=pdf_path,
            template=template,
            compact=True,
        )
        pages = count_pages(path)

    while pages > target_pages and len(report["trimmed"]) < max_trims:
        trimmed, info = trim_one_bullet(resume)

        if trimmed is None:
            break

        resume = trimmed
        report["trimmed"].append(info)
        path = render(
            resume=resume,
            output_path=pdf_path,
            template=template,
            compact=True,
        )
        pages = count_pages(path)

    report["actual_pages"] = pages

    if report["compact_spacing"] or report["trimmed"]:
        _LOG.warning(
            "Page fit: target=%s actual=%s compact_spacing=%s dropped_bullets=%d",
            target_pages,
            pages,
            report["compact_spacing"],
            len(report["trimmed"]),
        )

    return resume, path, report
