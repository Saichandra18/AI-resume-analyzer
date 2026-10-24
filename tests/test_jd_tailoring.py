"""Tests for deterministic job-description tailoring (ordering only)."""

import json
import re

from app.jd_tailoring import (
    job_stems,
    order_bullets,
    order_entry_bullets,
    order_skills,
)
from app.resume_generation_pipeline import (
    _guard_summary_against_job_description,
    generate_optimized_resume,
)
from app.resume_structurer import structure_resume

BI_JOB = (
    "Data Analyst. Build Power BI dashboards and KPI reports, write SQL "
    "queries, clean and transform data with Python and Pandas, perform "
    "exploratory data analysis, communicate insights with data visualization."
)
LLM_JOB = (
    "LLM Engineer. Build RAG pipelines, prompt engineering, embeddings, "
    "evaluate LLM outputs, deploy with Python, PyTorch, CI/CD, Docker."
)
SKILLS = [
    "Python", "Machine Learning", "Deep Learning", "SQL", "Pandas",
    "Power BI", "TensorFlow", "PyTorch", "NLP", "RAG", "LLM", "CI/CD",
]


def test_skills_the_job_asks_for_come_first():
    ordered = order_skills(SKILLS, BI_JOB)

    assert set(ordered[:4]) == {"Python", "SQL", "Pandas", "Power BI"}
    assert sorted(ordered) == sorted(SKILLS)


def test_different_jobs_order_the_same_skills_differently():
    bi = order_skills(SKILLS, BI_JOB)
    llm = order_skills(SKILLS, LLM_JOB)

    assert bi != llm
    assert {"RAG", "LLM", "PyTorch", "CI/CD"} <= set(llm[:5])
    assert llm.index("RAG") < bi.index("RAG")


def test_skills_without_a_match_keep_their_original_order():
    ordered = order_skills(SKILLS, BI_JOB)
    rest = [s for s in ordered if s not in {"Python", "SQL", "Pandas", "Power BI"}]

    assert rest == [s for s in SKILLS if s in rest]


def test_no_job_description_leaves_skills_untouched():
    assert order_skills(SKILLS, "") == SKILLS


def test_most_relevant_bullets_come_first_and_technologies_line_stays_first():
    bullets = [
        "Technologies: Python, SQL, Power BI, Pandas.",
        "Built a chatbot using retrieval augmented generation.",
        "Designed KPI dashboards in Power BI for match outcomes.",
        "Automated data cleaning and transformation using Python and SQL.",
    ]

    ordered = order_bullets(bullets, job_stems(BI_JOB))

    assert ordered[0].startswith("Technologies")
    assert ordered[-1].startswith("Built a chatbot")
    assert sorted(ordered) == sorted(bullets)


def test_ordering_is_stable_for_equally_relevant_bullets():
    bullets = ["First thing done.", "Second thing done.", "Third thing done."]

    assert order_bullets(bullets, job_stems(BI_JOB)) == bullets


def test_entries_are_reordered_without_losing_or_changing_bullets():
    entries = [{"title": "P", "bullets": ["Wrote chatbot code.", "Built Power BI dashboards."]}]

    result = order_entry_bullets(entries, BI_JOB)

    assert result[0]["bullets"][0] == "Built Power BI dashboards."
    assert sorted(result[0]["bullets"]) == sorted(entries[0]["bullets"])
    assert entries[0]["bullets"][0] == "Wrote chatbot code."  # input untouched


# ---------------------------------------------------------------------------
# End to end: same resume, two jobs
# ---------------------------------------------------------------------------

RESUME_TEXT = """Test Candidate
test@example.com +91 9100202628
Professional Summary
AI/ML Engineer with hands-on experience in Machine Learning and Generative AI.
Professional Experience
Analyst – Acme Jan 2022 – Present
Remote, India
•Built chatbot prototypes with retrieval augmented generation for support teams.
•Designed Power BI dashboards and KPI reports for weekly business reviews.
•Cleaned and transformed data with Python and Pandas for analysis.
Core Competencies
Programming: Python, SQL, Pandas
Projects
Sample Project
• Built dashboards.
Education
B.Tech – Computer Science 2019 – 2023
"""


class IdentityClient:
    def generate(self, prompt):
        def items(label):
            m = re.search(label + r":\n(.*?)\n\nORIGINAL RESUME:", prompt, re.S)
            if not m:
                return []
            body = m.group(1).strip()
            return [p.strip() for p in re.split(r"--- ITEM \d+ ---\n", body) if p.strip()]

        if "existing resume experience content" in prompt:
            return json.dumps([{"original": i, "rewritten": i, "changes": []} for i in items("EXPERIENCE")])
        if "existing resume project content" in prompt:
            return json.dumps([{"original": i, "rewritten": i, "changes": []} for i in items("PROJECTS")])
        if '"rewritten": "improved summary text"' in prompt:
            s = "AI/ML Engineer with hands-on experience in Machine Learning and Generative AI."
            return json.dumps({"original": s, "rewritten": s, "changes": []})
        if "SKILLS" in prompt:
            sk = ["Python", "SQL", "Pandas", "Machine Learning"]
            return json.dumps({"original": sk, "rewritten": sk, "changes": []})
        return "{}"


def _generate(job):
    return generate_optimized_resume(
        resume_text=RESUME_TEXT,
        resume_data=structure_resume(RESUME_TEXT),
        job_description=job,
        target_pages=1,
        client=IdentityClient(),
    )["final_resume"]


def test_experience_bullets_follow_the_job_but_keep_every_bullet():
    bi = _generate(BI_JOB).experience[0]["bullets"]
    llm = _generate("Build chatbot and retrieval augmented generation systems for support.").experience[0]["bullets"]

    # The BI job names data cleaning with Python/Pandas, analysis, dashboards
    # and KPIs; the chatbot bullet matches none of that and goes last.
    assert bi[0].startswith("Cleaned and transformed data")
    assert bi[1].startswith("Designed Power BI dashboards")
    assert bi[-1].startswith("Built chatbot prototypes")
    assert llm[0].startswith("Built chatbot prototypes")
    assert sorted(bi) == sorted(llm)
    assert len(bi) == 3


# ---------------------------------------------------------------------------
# Summary: keep the grounded sentences, drop only the job-description ones
# ---------------------------------------------------------------------------

JD_WITH_EXTRAS = (
    "Develop applications utilizing cloud services and image processing "
    "with Kubernetes orchestration. Machine Learning and Generative AI."
)


def test_summary_keeps_grounded_sentences_and_drops_job_description_ones():
    summary = (
        "AI/ML Engineer with hands-on experience in Machine Learning and Generative AI "
        "across analytics projects and model evaluation work. "
        "Utilizes cloud services, image processing and Kubernetes orchestration for applications."
    )

    result = _guard_summary_against_job_description(summary, RESUME_TEXT, JD_WITH_EXTRAS)

    assert result.startswith("AI/ML Engineer with hands-on experience")
    assert "Kubernetes" not in result
    assert "cloud services" not in result

def test_summary_placeholder_falls_back_to_original_summary():
    placeholder = (
        "Rewritten summary text that emphasizes relevant skills and "
        "experience based on the resume data."
    )

    result = _guard_summary_against_job_description(
        placeholder,
        RESUME_TEXT,
        BI_JOB,
    )

    assert result == (
        "AI/ML Engineer with hands-on experience in Machine Learning "
        "and Generative AI."
    )
    assert "Rewritten summary text" not in result
