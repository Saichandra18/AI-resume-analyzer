def validate_full_rewrite(
    summary=None,
    experience=None,
    projects=None,
    skills=None,
):
    """Aggregate validation results from all rewritten sections."""

    sections = {
        "summary": summary or {},
        "experience": experience or [],
        "projects": projects or [],
        "skills": skills or {},
    }

    unsupported_claims = []
    needs_review_sections = []

    for section_name, section_data in sections.items():
        if not section_data:
            continue

        if section_name == "experience":
            items = section_data

            for item in items:
                validation = item.get("validation", {})

                unsupported_claims.extend(
                    validation.get("unsupported_claims", [])
                )

                if validation.get("grounding_status") == "needs_review":
                    needs_review_sections.append(section_name)

        elif section_name == "projects":
            items = section_data

            for item in items:
                validation = item.get("validation", {})

                unsupported_claims.extend(
                    validation.get("unsupported_claims", [])
                )

                if validation.get("grounding_status") == "needs_review":
                    needs_review_sections.append(section_name)

        else:
            validation = section_data.get("validation", {})

            unsupported_claims.extend(
                validation.get("unsupported_claims", [])
            )

            if validation.get("grounding_status") == "needs_review":
                needs_review_sections.append(section_name)
    unsupported_claims = list(
        dict.fromkeys(unsupported_claims)
    )
    needs_review_sections = list(
        dict.fromkeys(needs_review_sections)
    )

    if unsupported_claims or needs_review_sections:
        return {
            "meaning_preserved": False,
            "unsupported_claims": unsupported_claims,
            "grounding_status": "needs_review",
            "needs_review_sections": needs_review_sections,
        }

    return {
        "meaning_preserved": True,
        "unsupported_claims": [],
        "grounding_status": "grounded",
        "needs_review_sections": [],
    }