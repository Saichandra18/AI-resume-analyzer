"""Regression tests for duplicated projects, missing experience header,
split bullets and keyword noise in the generated resume."""

import ast
import json
import re

from app.resume_generation_pipeline import generate_optimized_resume
from app.resume_structurer import structure_resume
from app.section_parser import (
    merge_rewritten_entries,
    parse_experience_entries,
    parse_project_entries,
)


RESUME_TEXT = """Sai Chandra Mudda
saichandraa18@gmail.com +91 9100202628
Professional Summary
AI/ML Engineer with hands-on experience in Machine Learning, Generative AI and Big Data Processing.
Professional Experience
Freelance LLM Trainer – OutlierSep 2023 – Present
Remote, India
•Contributed to training and evaluation of Large Language Models (LLMs) through structured data annotation,
response validation, and content quality assessment.
•Identified hallucinations, factual inaccuracies, bias, and logical inconsistencies in AI-generated content using ana-
lytical reasoning.
•Maintained productivity and quality benchmarks while working independently in a remote environment under
defined SLAs.
Core Competencies
Programming: Python, SQL, PySpark
Deployment Concepts: Model Serialization, REST APIs, Git Version Control, CI/CD Basics
Projects
AI Resume Analyzer using LLM, NLP and RAG
• Developed an AI-powered resume analysis and optimization system using Python, Flask, NLP, LLMs, and RAG.
• Implemented automated ATS evaluation and comprehensive testing to ensure accuracy, consistency, and backward
compatibility.
Cricket Match Analytics Dashboard
• Technologies: Python, SQL, Power BI, Pandas.
• Built an interactive analytics dashboard to track team performance, player statistics, win probability.
Generative AI Chatbot using LLM and Retrieval-Augmented Generation (RAG)
• Developed an AI chatbot integrating Large Language Models (LLMs) with structured prompt engineering.
• Integrated Retrieval-Augmented Generation (RAG) to enhance response accuracy and contextual relevance.
Education
Bachelor of Technology (B.Tech) – Computer Science and Engineering
Dadi Institute of Engineering and Technology 2019 – 2023
Professional Certifications
• IBM AI Developer Professional Certificate
"""

JOB_DESCRIPTION = (
    "AI/ML Engineer to build and deploy machine learning and Generative AI "
    "solutions using Python, SQL, PySpark, LLMs, RAG and CI/CD."
)


class IdentityClient:
    """Fake LLM that returns each source item unchanged (one per item)."""

    def generate(self, prompt):
        def items(label):
            match = re.search(
                label + r":\n(.*?)\n\nORIGINAL RESUME:",
                prompt,
                re.S,
            )
            if not match:
                return []
            body = match.group(1).strip()
            if body.startswith("--- ITEM"):
                return [
                    part.strip()
                    for part in re.split(r"--- ITEM \d+ ---\n", body)
                    if part.strip()
                ]
            value = ast.literal_eval(body)
            return value.get("section", []) if isinstance(value, dict) else value

        if "existing resume project content" in prompt:
            return json.dumps([
                {"original": i, "rewritten": i, "changes": []}
                for i in items("PROJECTS")
            ])

        if "existing resume experience content" in prompt:
            return json.dumps([
                {"original": i, "rewritten": i, "changes": []}
                for i in items("EXPERIENCE")
            ])

        if '"rewritten": "improved summary text"' in prompt:
            summary = (
                "AI/ML Engineer with hands-on experience in Machine "
                "Learning and Generative AI."
            )
            return json.dumps(
                {"original": summary, "rewritten": summary, "changes": []}
            )

        if "SKILLS" in prompt:
            skills = ["Python", "SQL", "PySpark", "RAG"]
            return json.dumps(
                {"original": skills, "rewritten": skills, "changes": []}
            )

        return "{}"


def _generate():
    resume_data = structure_resume(RESUME_TEXT)
    return generate_optimized_resume(
        resume_text=RESUME_TEXT,
        resume_data=resume_data,
        job_description=JOB_DESCRIPTION,
        target_pages=2,
        client=IdentityClient(),
    )["final_resume"]


# ---------------------------------------------------------------------------
# Parser unit tests
# ---------------------------------------------------------------------------

def test_wrapped_bullet_is_joined_not_split():
    entries = parse_project_entries([
        "AI Resume Analyzer",
        "•Implemented testing to ensure accuracy, consistency, and "
        "backward ........................",
        "compatibility.",
    ])

    assert len(entries) == 1
    assert len(entries[0]["bullets"]) == 1
    assert entries[0]["bullets"][0].endswith("backward ........................ compatibility.")


def test_hyphenated_line_break_is_repaired():
    entries = parse_experience_entries([
        "Analyst – Acme Jan 2020 – Present",
        "•Identified inconsistencies in AI-generated content using ana-",
        "lytical reasoning.",
    ])

    assert entries[0]["bullets"] == [
        "Identified inconsistencies in AI-generated content using analytical reasoning."
    ]


def test_projects_are_split_by_title():
    data = structure_resume(RESUME_TEXT)
    entries = parse_project_entries(data["projects"])

    assert [e["title"] for e in entries] == [
        "AI Resume Analyzer using LLM, NLP and RAG",
        "Cricket Match Analytics Dashboard",
        "Generative AI Chatbot using LLM and Retrieval-Augmented Generation (RAG)",
    ]
    assert [len(e["bullets"]) for e in entries] == [2, 2, 2]
    assert any("backward compatibility" in b for b in entries[0]["bullets"])


def test_experience_header_is_parsed_even_when_company_and_date_are_glued():
    data = structure_resume(RESUME_TEXT)
    entry = data["experience"]["entries"][0]

    assert entry["title"] == "Freelance LLM Trainer"
    assert entry["company"] == "Outlier"
    assert entry["location"] == "Remote, India"
    assert entry["dates"] == "Sep 2023 – Present"
    assert len(entry["bullets"]) == 3


def test_multiple_jobs_are_separated():
    entries = parse_experience_entries([
        "Data Analyst – Acme Corp Jan 2022 – Present",
        "• Built dashboards.",
        "Intern – Beta Labs Jun 2021 – Dec 2021",
        "• Cleaned data.",
    ])

    assert [e["title"] for e in entries] == ["Data Analyst", "Intern"]
    assert [e["company"] for e in entries] == ["Acme Corp", "Beta Labs"]
    assert entries[1]["dates"] == "Jun 2021 – Dec 2021"


def test_section_without_bullets_falls_back_to_legacy_behavior():
    assert parse_experience_entries(["Worked at Acme as an analyst."]) == []


# ---------------------------------------------------------------------------
# Merge safety
# ---------------------------------------------------------------------------

def _source():
    return [
        {"title": "Project A", "bullets": ["Did A one.", "Did A two."]},
        {"title": "Project B", "bullets": ["Did B one."]},
    ]


def test_merge_keeps_source_headers_and_one_entry_per_source():
    merged = merge_rewritten_entries(
        _source(),
        [
            {"rewritten": "Renamed A\n\u2022 Improved A one.\n\u2022 Improved A two."},
            {"rewritten": "Project B\n\u2022 Improved B one."},
        ],
    )

    assert [e["title"] for e in merged] == ["Project A", "Project B"]
    assert merged[0]["bullets"] == ["Improved A one.", "Improved A two."]


def test_merge_never_adds_extra_entries():
    merged = merge_rewritten_entries(
        _source(),
        [{"rewritten": "x"}, {"rewritten": "y"}, {"rewritten": "z"}, {"rewritten": "w"}],
    )

    assert len(merged) == 2


def test_merge_falls_back_to_source_when_rewrite_missing_or_empty():
    merged = merge_rewritten_entries(_source(), [{"rewritten": ""}])

    assert merged[0]["bullets"] == ["Did A one.", "Did A two."]
    assert merged[1]["bullets"] == ["Did B one."]


def test_merge_rejects_rewrite_that_mixes_in_another_project():
    merged = merge_rewritten_entries(
        _source(),
        [{"rewritten": "Project A\n\u2022 Mixed in: Project B did something."}, {}],
    )

    assert merged[0]["bullets"] == ["Did A one.", "Did A two."]


def test_merge_rejects_rewrite_with_unsupported_claims():
    merged = merge_rewritten_entries(
        _source(),
        [
            {
                "rewritten": "\u2022 Increased revenue 300%.",
                "validation": {"unsupported_claims": ["300%"]},
            }
        ],
    )

    assert merged[0]["bullets"] == ["Did A one.", "Did A two."]


# ---------------------------------------------------------------------------
# End-to-end: the four reported problems
# ---------------------------------------------------------------------------

def test_projects_are_not_duplicated_or_mixed():
    resume = _generate()
    titles = [p["title"] for p in resume.projects]

    assert sorted(titles) == sorted(set(titles))
    assert len(titles) == 3

    for project in resume.projects:
        for other in titles:
            if other != project["title"]:
                assert other not in " ".join(project["bullets"])


def test_experience_keeps_title_company_dates_and_location():
    resume = _generate()
    job = resume.experience[0]

    assert job["title"] == "Freelance LLM Trainer"
    assert job["company"] == "Outlier"
    assert job["dates"] == "Sep 2023 – Present"
    assert job["location"] == "Remote, India"


def test_wrapped_bullet_stays_one_bullet_in_final_resume():
    resume = _generate()
    bullets = [b for p in resume.projects for b in p["bullets"]]

    assert any("backward compatibility" in b for b in bullets)
    assert not any(b.strip().lower().startswith("compatibility") for b in bullets)


def test_summary_has_no_keyword_noise():
    resume = _generate()

    assert "Core areas include" not in resume.summary
    assert "ci cd" not in resume.summary.lower()


def test_supported_keywords_are_formatted_and_added_to_skills():
    resume = _generate()
    skills = [s.lower() for s in resume.skills]

    assert "ci/cd" in skills
    assert "cd" not in skills


# ---------------------------------------------------------------------------
# Real-LLM failure modes (second round)
# ---------------------------------------------------------------------------

from app.resume_generation_pipeline import (  # noqa: E402
    _dedupe_skills,
    _guard_summary_against_job_description,
)

JD_STYLE_JOB_DESCRIPTION = (
    "Develop applications and systems that utilize AI tools and cloud AI "
    "services. Work on deep learning, neural networks, chatbots and image "
    "processing to enhance functionality. Python, SQL, PySpark, CI/CD."
)


class MessyClient:
    """Fake LLM that misbehaves the way a real one did on Render.

    * experience: one item PER BULLET instead of one per job, first verb upgraded
    * projects:   one item per line (title item, then bullet items)
    * summary:    copied from the job description
    * skills:     duplicates
    """

    def generate(self, prompt):
        def blocks(label):
            match = re.search(label + r":\n(.*?)\n\nORIGINAL RESUME:", prompt, re.S)
            body = match.group(1).strip() if match else ""
            return [
                part.strip()
                for part in re.split(r"--- ITEM \d+ ---\n", body)
                if part.strip()
            ]

        def item(text):
            return {"original": text, "rewritten": text, "changes": []}

        if "existing resume experience content" in prompt:
            out = []
            for block in blocks("EXPERIENCE"):
                for line in block.splitlines()[1:]:
                    out.append(item(line.replace("Contributed to", "Developed")))
            return json.dumps(out)

        if "existing resume project content" in prompt:
            out = []
            for block in blocks("PROJECTS"):
                for line in block.splitlines():
                    out.append(item(line))
            return json.dumps(out)

        if '"rewritten": "improved summary text"' in prompt:
            text = (
                "Develops applications and systems that utilize AI tools and "
                "cloud AI services. Works on deep learning, neural networks, "
                "chatbots and image processing to enhance functionality."
            )
            return json.dumps({"original": text, "rewritten": text, "changes": []})

        if "SKILLS" in prompt:
            skills = ["Python", "Neural Networks", "Neural Network", "LLM",
                      "Large Language Models", "SQL"]
            return json.dumps({"original": skills, "rewritten": skills, "changes": []})

        return "{}"


def _generate_messy():
    resume_data = structure_resume(RESUME_TEXT)
    return generate_optimized_resume(
        resume_text=RESUME_TEXT,
        resume_data=resume_data,
        job_description=JD_STYLE_JOB_DESCRIPTION,
        target_pages=2,
        client=MessyClient(),
    )["final_resume"]


def test_per_bullet_rewrite_keeps_all_experience_bullets():
    source = [{"title": "Trainer", "company": "Outlier", "bullets": ["a one.", "b two.", "c three."]}]
    items = [{"rewritten": "A one."}, {"rewritten": "B two."}, {"rewritten": "C three."}]

    merged = merge_rewritten_entries(source, items)

    assert merged[0]["bullets"] == ["A one.", "B two.", "C three."]


def test_lossy_rewrite_falls_back_to_source_bullets():
    source = [{"title": "Trainer", "bullets": ["a.", "b.", "c.", "d.", "e.", "f."]}]

    merged = merge_rewritten_entries(source, [{"rewritten": "\u2022 Only one bullet."}])

    assert merged[0]["bullets"] == ["a.", "b.", "c.", "d.", "e.", "f."]


def test_per_line_project_items_are_regrouped_by_title():
    source = [
        {"title": "Project A", "bullets": ["Did A one.", "Did A two."]},
        {"title": "Project B", "bullets": ["Did B one.", "Did B two."]},
    ]
    items = [
        {"rewritten": "Project A"}, {"rewritten": "\u2022 Made A one."}, {"rewritten": "\u2022 Made A two."},
        {"rewritten": "Project B"}, {"rewritten": "\u2022 Made B one."}, {"rewritten": "\u2022 Made B two."},
    ]

    merged = merge_rewritten_entries(source, items)

    assert merged[0]["bullets"] == ["Made A one.", "Made A two."]
    assert merged[1]["bullets"] == ["Made B one.", "Made B two."]


def test_experience_is_not_truncated_by_a_per_bullet_llm():
    resume = _generate_messy()

    assert len(resume.experience[0]["bullets"]) == 3
    assert [len(p["bullets"]) for p in resume.projects] == [2, 2, 2]


def test_summary_copied_from_job_description_is_replaced_by_original():
    resume = _generate_messy()

    assert resume.summary.startswith("AI/ML Engineer with hands-on experience")
    assert "cloud AI services" not in resume.summary


def test_grounded_summary_is_kept():
    summary = "AI/ML Engineer building machine learning and Generative AI systems in Python."

    assert _guard_summary_against_job_description(
        summary, RESUME_TEXT, JD_STYLE_JOB_DESCRIPTION
    ) == summary


def test_duplicate_skills_are_removed():
    skills = _dedupe_skills(
        ["Neural Networks", "Neural Network", "LLM", "Large Language Models", "SQL"]
    )

    assert skills == ["Neural Networks", "LLM", "SQL"]


def test_final_skills_have_no_duplicates():
    resume = _generate_messy()
    lowered = [s.lower() for s in resume.skills]

    assert not ("neural networks" in lowered and "neural network" in lowered)
    assert not ("llm" in lowered and "large language models" in lowered)


# ---------------------------------------------------------------------------
# Third round: lost summary, "maintain ing", hyphen breaks
# ---------------------------------------------------------------------------

from app.resume_generation_pipeline import _repair_glued_words  # noqa: E402
from app.section_parser import hyphen_join, repair_hyphen_breaks  # noqa: E402


def _is_summary_prompt(prompt):
    return "ORIGINAL SUMMARY" in prompt or '"rewritten": "improved summary text"' in prompt


class EmptySummaryClient(IdentityClient):
    """The model answers the summary request with an empty JSON object."""

    def generate(self, prompt):
        if _is_summary_prompt(prompt):
            return "{}"
        return super().generate(prompt)


class ProseSummaryClient(IdentityClient):
    """The model answers the summary request with prose instead of JSON."""

    def generate(self, prompt):
        if _is_summary_prompt(prompt):
            return "Sure! Here is an improved summary of your profile."
        return super().generate(prompt)


def _generate_with(client):
    return generate_optimized_resume(
        resume_text=RESUME_TEXT,
        resume_data=structure_resume(RESUME_TEXT),
        job_description=JOB_DESCRIPTION,
        target_pages=2,
        client=client,
    )["final_resume"]


def test_empty_summary_rewrite_keeps_the_resumes_own_summary():
    summary = _generate_with(EmptySummaryClient()).summary

    assert summary.startswith("AI/ML Engineer with hands-on experience")


def test_non_json_summary_rewrite_keeps_the_resumes_own_summary():
    summary = _generate_with(ProseSummaryClient()).summary

    assert summary.startswith("AI/ML Engineer with hands-on experience")


def test_glued_word_repair_never_splits_off_a_suffix():
    vocabulary = {"maintain", "ing", "ensure", "perform", "ed", "prompt", "evaluation"}

    repaired = _repair_glued_words("maintaining ensuring performed", vocabulary)

    assert repaired == "maintaining ensuring performed"


def test_glued_word_repair_still_splits_real_glued_words():
    vocabulary = {"performed", "prompt", "output", "analysis"}

    assert _repair_glued_words("performedprompt outputanalysis", vocabulary) == (
        "performed prompt output analysis"
    )


def test_words_broken_across_lines_are_rejoined():
    assert repair_hyphen_breaks("Natural Language Process-\ning, and Big Data") == (
        "Natural Language Processing, and Big Data"
    )
    assert repair_hyphen_breaks("Natural Language Process- ing") == (
        "Natural Language Processing"
    )


def test_real_hyphenated_compounds_are_left_alone():
    text = "cross-validation, role-specific, AI-powered, end-to-end, pre- and post-processing"

    assert repair_hyphen_breaks(text) == text
    assert hyphen_join("Retrieval-", "Augmented") == "Retrieval-Augmented"
    assert hyphen_join("AI-", "powered") == "AI-powered"
    assert hyphen_join("role-", "specific") == "role-specific"
