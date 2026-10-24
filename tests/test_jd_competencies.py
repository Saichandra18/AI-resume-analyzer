"""The resume's own competencies and summary must respond to the job description."""

import json
import re

from app.jd_tailoring import (
    MAX_ADDED_SKILLS,
    add_supported_competencies,
    order_summary,
    resume_competencies,
)
from app.resume_generation_pipeline import generate_optimized_resume
from app.resume_structurer import structure_resume

RESUME_TEXT = """Test Candidate
test@example.com +91 9100202628
Professional Summary
AI/ML Engineer with hands-on experience in Machine Learning and Generative AI. Proficient in Python, SQL, and PySpark for data transformation. Experienced in LLM evaluation, prompt engineering, embeddings, and Retrieval-Augmented Generation (RAG) workflows. Strong understanding of statistics, data structures, and algorithms.
Professional Experience
Analyst \u2013 Acme Jan 2022 \u2013 Present
Remote, India
\u2022Built chatbot prototypes with retrieval augmented generation for support teams.
\u2022Designed Power BI dashboards and KPI reports for weekly business reviews.
Core Competencies
Programming: Python, SQL, PySpark
Machine Learning: Supervised Learning, Classification, Regression, Model Evaluation,
Cross Validation, Hyperparameter Tuning
Generative AI: Large Language Models (LLMs), Prompt Engineering, Embeddings, Vector Search, Retrieval-Augmented Generation (RAG)
Big Data Processing: PySpark, DataFrames, Distributed Computing, ETL Pipelines
Deployment Concepts: Model Serialization, REST APIs, Git Version Control, CI/CD Basics
Core Concepts: Statistics, Probability, Linear Algebra
Projects
Sample Project
\u2022 Technologies: Python, SQL, Power BI, Pandas.
\u2022 Built dashboards.
Education
B.Tech \u2013 Computer Science 2019 \u2013 2023
CGPA: 7.69
"""

DATA_PLATFORM_JOB = (
    "Machine Learning Engineer. Build ETL pipelines and distributed data "
    "processing in PySpark, expose models through REST APIs, run model "
    "evaluation and feature engineering, apply statistics, use Git and CI/CD."
)
BASE_SKILLS = ["Python", "SQL", "Machine Learning"]


# --------------------------------------------------------------------------
# Reading the resume's own competencies
# --------------------------------------------------------------------------

def test_competencies_are_read_from_the_resumes_own_lines():
    items = resume_competencies(RESUME_TEXT)

    for expected in ("PySpark", "Model Evaluation", "Hyperparameter Tuning",
                     "Embeddings", "Vector Search", "ETL Pipelines",
                     "REST APIs", "Model Serialization", "Statistics"):
        assert expected in items


def test_wrapped_competency_line_is_joined():
    assert "Cross Validation" in resume_competencies(RESUME_TEXT)


def test_parenthetical_acronyms_are_dropped_from_items():
    items = resume_competencies(RESUME_TEXT)

    assert "Large Language Models" in items
    assert not any("(" in item for item in items)


def test_only_the_skills_section_is_read():
    items = resume_competencies(RESUME_TEXT)

    assert "7.69" not in items and "CGPA" not in items
    assert "Technologies" not in items
    assert "Power BI" not in items          # a project bullet, not a competency


def test_resume_without_a_skills_section_yields_nothing():
    assert resume_competencies("Name\nProfessional Summary\nHello.\nEducation\nB.Tech") == []


# --------------------------------------------------------------------------
# Adding the ones the job asks for
# --------------------------------------------------------------------------

def test_only_competencies_the_job_asks_for_are_added():
    result = add_supported_competencies(BASE_SKILLS, RESUME_TEXT, DATA_PLATFORM_JOB)
    added = result[len(BASE_SKILLS):]

    assert {"PySpark", "ETL Pipelines", "REST APIs", "Statistics"} <= set(added)
    assert "Vector Search" not in added and "Linear Algebra" not in added
    assert result[: len(BASE_SKILLS)] == BASE_SKILLS


def test_nothing_is_added_that_the_resume_does_not_state():
    job = "Build Kubernetes operators in Go and run workloads on AWS with Terraform."

    assert add_supported_competencies(BASE_SKILLS, RESUME_TEXT, job) == BASE_SKILLS


def test_existing_skills_are_not_duplicated():
    result = add_supported_competencies(["Python", "SQL", "PySpark"], RESUME_TEXT, DATA_PLATFORM_JOB)

    assert result.count("PySpark") == 1


def test_number_of_added_competencies_is_capped():
    job = " ".join(resume_competencies(RESUME_TEXT))

    added = add_supported_competencies([], RESUME_TEXT, job)

    assert len(added) == MAX_ADDED_SKILLS


def test_no_job_description_adds_nothing():
    assert add_supported_competencies(BASE_SKILLS, RESUME_TEXT, "") == BASE_SKILLS


# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------

SUMMARY = (
    "AI/ML Engineer with hands-on experience in Machine Learning and Generative AI. "
    "Proficient in Python, SQL, and PySpark for data transformation. "
    "Experienced in LLM evaluation, prompt engineering, embeddings, and RAG workflows. "
    "Strong understanding of statistics, data structures, and algorithms."
)


def test_summary_orders_all_sentences_by_job_relevance():
    summary = (
        "AI/ML Engineer with hands-on experience in Machine Learning "
        "and Generative AI. "
        "Experienced in LLM evaluation and prompt engineering. "
        "Strong understanding of Python, SQL, Flask, and API development."
    )

    job = (
        "Python Developer. Python, SQL, Flask, REST APIs, "
        "and backend application development."
    )

    result = order_summary(summary, job)

    assert result.startswith(
        "Strong understanding of Python, SQL, Flask, and API development."
    )
    assert sorted(result.split()) == sorted(summary.split())
def test_summary_wording_is_never_changed():
    for job in (DATA_PLATFORM_JOB, "Prompt engineering and embeddings for LLM evaluation.", "Unrelated words here."):
        assert sorted(order_summary(SUMMARY, job).split()) == sorted(SUMMARY.split())


def test_short_summaries_are_left_alone():
    one = "AI/ML Engineer with hands-on experience."

    assert order_summary(one, DATA_PLATFORM_JOB) == one


# --------------------------------------------------------------------------
# End to end
# --------------------------------------------------------------------------

class IdentityClient:
    def generate(self, prompt):
        def items(label):
            m = re.search(label + r":\n(.*?)\n\nORIGINAL RESUME:", prompt, re.S)
            body = m.group(1).strip() if m else ""
            return [p.strip() for p in re.split(r"--- ITEM \d+ ---\n", body) if p.strip()]

        if "existing resume experience content" in prompt:
            return json.dumps([{"original": i, "rewritten": i, "changes": []} for i in items("EXPERIENCE")])
        if "existing resume project content" in prompt:
            return json.dumps([{"original": i, "rewritten": i, "changes": []} for i in items("PROJECTS")])
        if '"rewritten": "improved summary text"' in prompt:
            return json.dumps({"original": SUMMARY, "rewritten": SUMMARY, "changes": []})
        if "SKILLS" in prompt:
            return json.dumps({"original": BASE_SKILLS, "rewritten": BASE_SKILLS, "changes": []})
        return "{}"


def _generate(job):
    return generate_optimized_resume(
        resume_text=RESUME_TEXT,
        resume_data=structure_resume(RESUME_TEXT),
        job_description=job,
        target_job_title="Machine Learning Engineer",
        target_pages=1,
        client=IdentityClient(),
    )["final_resume"]


def test_generated_skills_include_the_competencies_the_job_asks_for():
    skills = _generate(DATA_PLATFORM_JOB).skills

    for expected in ("PySpark", "ETL Pipelines", "REST APIs", "Statistics"):
        assert expected in skills


def test_the_same_resume_gives_different_skills_for_different_jobs():
    data_platform = _generate(DATA_PLATFORM_JOB).skills
    llm = _generate("Build LLM applications with prompt engineering, embeddings and vector search.").skills

    assert "ETL Pipelines" in data_platform and "ETL Pipelines" not in llm
    assert "Vector Search" in llm and "Vector Search" not in data_platform
