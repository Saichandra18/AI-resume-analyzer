"""Validation for the composed final resume."""

from collections import Counter

from app.final_resume_models import (
    DEFAULT_SECTION_ORDER,
    FinalResume,
)


REQUIRED_PERSONAL_INFO_FIELDS = {
    "name",
}


def _normalize_text(value):
    """Normalize text for comparison."""
    if value is None:
        return ""

    return " ".join(
        str(value).lower().split()
    )


def _is_non_empty(value):
    """Return whether a value contains usable content."""
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)

    return True


def _validate_personal_info(resume, errors):
    """Validate essential personal information."""

    personal_info = resume.personal_info

    if not isinstance(personal_info, dict):
        errors.append(
            "personal_info must be a dictionary."
        )
        return

    for field in REQUIRED_PERSONAL_INFO_FIELDS:
        if not _is_non_empty(
            personal_info.get(field)
        ):
            errors.append(
                f"Missing required personal information: {field}."
            )


def _validate_summary(resume, warnings):
    """Validate summary content."""

    if not resume.summary:
        warnings.append(
            "Professional summary is empty."
        )


def _validate_sections(resume, errors):
    """Validate section ordering."""

    section_order = resume.section_order

    if not isinstance(
        section_order,
        list,
    ):
        errors.append(
            "section_order must be a list."
        )
        return

    valid_sections = set(
        DEFAULT_SECTION_ORDER
    )

    unknown = (
        set(section_order)
        - valid_sections
    )

    if unknown:
        errors.append(
            "Unknown sections: "
            + ", ".join(sorted(unknown))
        )

    duplicates = [
        section
        for section, count in Counter(
            section_order
        ).items()
        if count > 1
    ]

    if duplicates:
        errors.append(
            "Duplicate sections: "
            + ", ".join(
                sorted(duplicates)
            )
        )


def _validate_collection(
    collection,
    section,
    errors,
):
    """Validate a resume section collection."""

    if not isinstance(
        collection,
        list,
    ):
        errors.append(
            f"{section} must be a list."
        )
        return

    for index, item in enumerate(
        collection
    ):
        if not _is_non_empty(item):
            errors.append(
                f"{section}[{index}] is empty."
            )


def _validate_duplicates(
    collection,
    section,
    warnings,
):
    """Detect duplicate resume entries."""

    normalized_items = []

    for item in collection:
        if isinstance(item, dict):
            values = item.values()
            text = " ".join(
                str(value)
                for value in values
                if value is not None
            )
        else:
            text = str(item)

        normalized_items.append(
            _normalize_text(text)
        )

    counts = Counter(
        item
        for item in normalized_items
        if item
    )

    duplicate_count = sum(
        count - 1
        for count in counts.values()
        if count > 1
    )

    if duplicate_count:
        warnings.append(
            f"{section} contains "
            f"{duplicate_count} duplicate entry/entries."
        )


def _validate_metadata(resume, errors):
    """Validate final-resume metadata."""

    metadata = resume.metadata

    if metadata.target_pages < 1:
        errors.append(
            "target_pages must be positive."
        )

    if not isinstance(
        metadata.optimization_enabled,
        bool,
    ):
        errors.append(
            "optimization_enabled must be boolean."
        )


def validate_final_resume(
    resume,
    require_summary=False,
):
    """
    Validate a FinalResume.

    Returns:

        {
            "valid": bool,
            "errors": [...],
            "warnings": [...]
        }
    """

    errors = []
    warnings = []

    if not isinstance(
        resume,
        FinalResume,
    ):
        errors.append(
            "resume must be a FinalResume instance."
        )

        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
        }

    _validate_personal_info(
        resume,
        errors,
    )

    if require_summary and not resume.summary:
        errors.append(
            "Professional summary is required."
        )
    else:
        _validate_summary(
            resume,
            warnings,
        )

    _validate_sections(
        resume,
        errors,
    )

    _validate_collection(
        resume.skills,
        "skills",
        errors,
    )

    _validate_collection(
        resume.experience,
        "experience",
        errors,
    )

    _validate_collection(
        resume.projects,
        "projects",
        errors,
    )

    _validate_collection(
        resume.education,
        "education",
        errors,
    )

    _validate_collection(
        resume.certifications,
        "certifications",
        errors,
    )

    _validate_duplicates(
        resume.experience,
        "experience",
        warnings,
    )

    _validate_duplicates(
        resume.projects,
        "projects",
        warnings,
    )

    _validate_duplicates(
        resume.education,
        "education",
        warnings,
    )

    _validate_duplicates(
        resume.certifications,
        "certifications",
        warnings,
    )

    _validate_metadata(
        resume,
        errors,
    )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def is_valid_final_resume(
    resume,
    require_summary=False,
):
    """Return only the final validity status."""

    return validate_final_resume(
        resume,
        require_summary=require_summary,
    )["valid"]