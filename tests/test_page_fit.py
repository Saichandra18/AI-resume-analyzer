"""Tests for fitting the generated PDF to the requested page count."""

from app.final_resume_models import build_final_resume
from app.page_fit import (
    MIN_JOB_BULLETS,
    MIN_PROJECT_BULLETS,
    fit_pdf_to_pages,
    trim_one_bullet,
)
from app.rendered_document_validator import count_pdf_pages


def _resume(job_bullets=6, project_bullets=(6, 6, 4)):
    return build_final_resume(
        personal_info={"name": "Test Candidate", "email": "t@example.com"},
        summary="Short summary.",
        skills=["Python", "SQL"],
        experience=[
            {
                "title": "Trainer",
                "company": "Acme",
                "bullets": [f"Job bullet {i}." for i in range(job_bullets)],
            }
        ],
        projects=[
            {
                "title": f"Project {n}",
                "bullets": [f"P{n} bullet {i}." for i in range(count)],
            }
            for n, count in enumerate(project_bullets)
        ],
    )


# ---------------------------------------------------------------------------
# trim_one_bullet
# ---------------------------------------------------------------------------

def test_trim_removes_last_bullet_of_last_project_first():
    trimmed, info = trim_one_bullet(_resume())

    assert info["section"] == "projects"
    assert info["title"] == "Project 2"
    assert info["bullet"] == "P2 bullet 3."


def test_trim_leaves_the_original_resume_untouched():
    resume = _resume()
    before = [len(p["bullets"]) for p in resume.projects]

    trim_one_bullet(resume)

    assert [len(p["bullets"]) for p in resume.projects] == before


def test_trim_never_goes_below_the_minimums():
    resume = _resume(
        job_bullets=MIN_JOB_BULLETS,
        project_bullets=(MIN_PROJECT_BULLETS, MIN_PROJECT_BULLETS),
    )

    assert trim_one_bullet(resume) == (None, None)


def test_trim_falls_back_to_experience_when_projects_are_minimal():
    resume = _resume(job_bullets=6, project_bullets=(MIN_PROJECT_BULLETS,))

    trimmed, info = trim_one_bullet(resume)

    assert info["section"] == "experience"
    assert len(trimmed.experience[0]["bullets"]) == 5


# ---------------------------------------------------------------------------
# fit_pdf_to_pages decision logic (fake renderer / page counter)
# ---------------------------------------------------------------------------

class FakeRenderer:
    """Pages = 2 while the resume has many bullets and spacing is normal."""

    def __init__(self, fits_when_compact=False, bullets_needed=999):
        self.calls = []
        self.fits_when_compact = fits_when_compact
        self.bullets_needed = bullets_needed
        self.pages = 2

    def render(self, resume, output_path, template="default", compact=False):
        total = sum(len(p["bullets"]) for p in resume.projects)
        self.calls.append({"compact": compact, "bullets": total})
        fits = (compact and self.fits_when_compact) or total <= self.bullets_needed
        self.pages = 1 if fits else 2
        return output_path

    def count(self, path):
        return self.pages


def test_fitting_resume_is_not_touched():
    fake = FakeRenderer(bullets_needed=999)

    resume, _, report = fit_pdf_to_pages(
        _resume(), "x.pdf", 1, render=fake.render, count_pages=fake.count
    )

    assert report["compact_spacing"] is False
    assert report["trimmed"] == []
    assert len(fake.calls) == 1


def test_tighter_spacing_is_tried_before_removing_anything():
    fake = FakeRenderer(fits_when_compact=True, bullets_needed=0)

    resume, _, report = fit_pdf_to_pages(
        _resume(), "x.pdf", 1, render=fake.render, count_pages=fake.count
    )

    assert report["compact_spacing"] is True
    assert report["trimmed"] == []
    assert report["actual_pages"] == 1


def test_bullets_are_dropped_one_at_a_time_only_as_last_resort():
    fake = FakeRenderer(bullets_needed=14)  # starts with 16 project bullets

    resume, _, report = fit_pdf_to_pages(
        _resume(), "x.pdf", 1, render=fake.render, count_pages=fake.count
    )

    assert len(report["trimmed"]) == 2
    assert report["actual_pages"] == 1
    assert sum(len(p["bullets"]) for p in resume.projects) == 14


def test_gives_up_gracefully_when_nothing_more_can_be_trimmed():
    fake = FakeRenderer(bullets_needed=0)  # can never fit

    resume, _, report = fit_pdf_to_pages(
        _resume(), "x.pdf", 1, render=fake.render, count_pages=fake.count
    )

    assert report["actual_pages"] == 2
    assert report["fits"] is False
    assert all(len(p["bullets"]) >= MIN_PROJECT_BULLETS for p in resume.projects)
    assert len(resume.experience[0]["bullets"]) >= MIN_JOB_BULLETS


def test_no_bullets_are_dropped_when_trimming_cannot_reach_the_target():
    original = _resume()
    fake = FakeRenderer(bullets_needed=0)  # can never fit, however much is trimmed

    resume, _, report = fit_pdf_to_pages(
        original, "x.pdf", 1, render=fake.render, count_pages=fake.count
    )

    assert report["trimmed"] == []
    assert [p["bullets"] for p in resume.projects] == [p["bullets"] for p in original.projects]
    assert resume.experience[0]["bullets"] == original.experience[0]["bullets"]


# ---------------------------------------------------------------------------
# Real renderer: the exact content that spilled one line onto page 2
# ---------------------------------------------------------------------------

def _overflowing_resume():
    return build_final_resume(
        personal_info={
            "name": "Sai Chandra Mudda",
            "email": "saichandraa18@gmail.com",
            "phone": "+91 9100202628",
        },
        summary=(
            "AI/ML Engineer with hands-on experience in Machine Learning, "
            "Generative AI, Natural Language Processing, and Big Data "
            "Processing. Proficient in Python, SQL, and PySpark for scalable "
            "data transformation and analytics. Experienced in LLM "
            "evaluation, prompt engineering, embeddings, and "
            "Retrieval-Augmented Generation (RAG) workflows. Strong "
            "understanding of statistics, data structures, and algorithms "
            "with exposure to model deployment and performance optimization."
        ),
        skills=[
            "Python", "Deep Learning", "Artificial Intelligence",
            "Generative AI", "LLM", "RAG", "SQL", "Pandas", "Power BI",
            "Machine Learning", "TensorFlow", "PyTorch", "NLP", "Flask",
            "Git", "Neural Networks", "CI/CD",
        ],
        experience=[
            {
                "title": "Freelance LLM Trainer",
                "company": "Outlier",
                "location": "Remote, India",
                "dates": "Sep 2023 \u2013 Present",
                "bullets": [
                    "Conducted structured data annotation, response validation, and content quality assessment for training and evaluation of Large Language Models (LLMs).",
                    "Carried out prompt evaluation and analyzed outputs to improve model accuracy, contextual relevance, and response consistency.",
                    "Detected hallucinations, factual inaccuracies, bias, and logical inconsistencies in AI-generated content through analytical reasoning.",
                    "Adopted defined quality assurance (QA) guidelines to ensure high-precision training data and standardized evaluation processes.",
                    "Supported refining prompt engineering techniques to enhance response quality and minimize ambiguity.",
                    "Kept productivity and quality benchmarks while independently managing remote tasks according to specified Service Level Agreements (SLAs).",
                ],
            }
        ],
        projects=[
            {
                "title": "AI Resume Analyzer using LLM, NLP and RAG",
                "bullets": [
                    "Developed an AI-powered resume analysis and optimization system using Python, Flask, NLP, LLMs, and RAG.",
                    "Analyzed resumes against job descriptions to identify skill gaps, keywords, and ATS optimization opportunities.",
                    "Implemented JD-aware content selection, prioritization, AI-based rewriting, and resume length control.",
                    "Generated structured, ATS-friendly resumes with automated validation and DOCX rendering.",
                    "Integrated RAG architecture for grounded, role-specific recommendations and contextual resume optimization.",
                    "Implemented automated ATS evaluation and comprehensive testing to ensure accuracy, consistency, and backward compatibility.",
                ],
            },
            {
                "title": "Generative AI Chatbot using LLM and Retrieval-Augmented Generation (RAG)",
                "bullets": [
                    "Developed an AI chatbot integrating Large Language Models (LLMs) with structured prompt engineering.",
                    "Implemented embedding-based semantic similarity search for contextual information retrieval.",
                    "Integrated Retrieval-Augmented Generation (RAG) to enhance response accuracy and contextual relevance.",
                    "Structured chatbot workflow for improved response consistency and user interaction quality.",
                ],
            },
            {
                "title": "Cricket Match Analytics Dashboard",
                "bullets": [
                    "Technologies: Python, SQL, Power BI, Pandas.",
                    "Built an interactive analytics dashboard to track team performance, player statistics, win probability.",
                    "Performed exploratory data analysis on cricket datasets containing player and match-level statistics.",
                    "Designed KPI dashboards for batting, bowling, strike rate, economy rate, and match outcomes.",
                    "Automated data cleaning and transformation workflows using Python and SQL.",
                    "Generated actionable insights through visualizations and statistical analysis.",
                ],
            },
        ],
        education=[
            {
                "degree": "Bachelor of Technology (B.Tech) \u2013 Computer Science and Engineering",
                "year": "2019 \u2013 2023",
                "institution": "Dadi Institute of Engineering and Technology",
            }
        ],
        certifications=[
            "IBM Generative AI Engineering Professional Certificate",
            "IBM AI Developer Professional Certificate",
            "Google Data Analytics Professional Certificate",
        ],
    )


def test_real_render_that_spilled_to_page_two_now_fits_one_page(tmp_path):
    from app.resume_pdf_renderer import render_final_resume_pdf

    resume = _overflowing_resume()

    # Sanity check: this content really does overflow in the normal layout.
    plain = render_final_resume_pdf(
        resume=resume, output_path=tmp_path / "plain.pdf", template="ats_clean"
    )
    assert count_pdf_pages(plain) == 2

    fitted, path, report = fit_pdf_to_pages(
        resume, tmp_path / "fit.pdf", 1, template="ats_clean"
    )

    assert count_pdf_pages(path) == 1
    assert report["actual_pages"] == 1
    assert report["compact_spacing"] is True
    # No content was lost: spacing alone was enough.
    assert report["trimmed"] == []
    assert fitted.experience[0]["bullets"] == resume.experience[0]["bullets"]
    assert [p["bullets"] for p in fitted.projects] == [p["bullets"] for p in resume.projects]
