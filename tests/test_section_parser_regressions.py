from app.section_parser import (
    parse_experience_entries,
    parse_project_entries,
)


def test_projects_keep_their_own_titles_and_bullets():
    projects = parse_project_entries([
        "AI Resume Analyzer using LLM, NLP and RAG",
        "- Developed an AI-powered resume analyzer.",
        "- Implemented automated ATS evaluation for backward",
        "compatibility.",
        "Cricket Match Analytics Dashboard",
        "- Built an interactive analytics dashboard.",
    ])

    assert len(projects) == 2

    assert projects[0]["title"] == (
        "AI Resume Analyzer using LLM, NLP and RAG"
    )
    assert projects[0]["bullets"] == [
        "Developed an AI-powered resume analyzer.",
        "Implemented automated ATS evaluation for backward compatibility.",
    ]

    assert projects[1]["title"] == "Cricket Match Analytics Dashboard"
    assert projects[1]["bullets"] == [
        "Built an interactive analytics dashboard."
    ]


def test_experience_header_preserves_role_company_and_dates():
    entries = parse_experience_entries([
        "Freelance LLM Trainer - OutlierSep 2023 - Present",
        "Remote, India",
        "- Evaluated prompts and analyzed model outputs.",
    ])

    assert len(entries) == 1

    assert entries[0]["title"] == "Freelance LLM Trainer"
    assert entries[0]["company"] == "Outlier"
    assert entries[0]["dates"] == "Sep 2023 - Present"
    assert entries[0]["location"] == "Remote, India"
    assert entries[0]["bullets"] == [
        "Evaluated prompts and analyzed model outputs."
    ]


def test_empty_project_input_returns_empty_list():
    assert parse_project_entries([]) == []


def test_empty_experience_input_returns_empty_list():
    assert parse_experience_entries([]) == []
