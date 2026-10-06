from copy import deepcopy

from app.final_resume_models import FinalResume
from app.resume_optimization_evaluator import (
    _build_optimized_education,
    _build_optimized_experience,
    _build_optimized_projects,
    _final_resume_to_ats_data,
    evaluate_resume_optimization,
)


JOB_DESCRIPTION = """
We are looking for an AI/ML Engineer.

Required skills:
Python
Machine Learning
RAG
LLMs

Education:
Bachelor's degree

Experience:
2 years

Keywords:
Python
Machine Learning
RAG
LLM
NLP
SQL
"""


def _build_resume():
    return FinalResume(
        personal_info={
            "name": "Test Candidate",
        },
        summary=(
            "AI/ML Engineer with experience in Python, "
            "Machine Learning, LLMs and RAG."
        ),
        skills=[
            "Python",
            "Machine Learning",
            "RAG",
            "LLMs",
        ],
        experience=[
            {
                "job_title": "AI/ML Engineer",
                "company": "Example Company",
                "dates": "2021 – Present",
                "location": "Remote",
                "bullets": [
                    "Built machine learning solutions using Python.",
                    "Developed RAG and LLM evaluation workflows.",
                ],
            }
        ],
        projects=[
            {
                "title": "Generative AI Chatbot",
                "bullets": [
                    "Built a RAG-based chatbot using LLMs.",
                    "Used Python and NLP techniques.",
                ],
            }
        ],
        education=[
            {
                "degree": "Bachelor of Technology – Computer Science",
                "year": "2019 – 2023",
                "institution": "Example Institute",
            }
        ],
        certifications=[
            "Generative AI Professional Certificate",
        ],
    )


def test_build_optimized_education():
    education = [
        {
            "degree": "Bachelor of Technology",
            "year": "2019 – 2023",
            "institution": "Example Institute",
        }
    ]

    result = _build_optimized_education(education)

    assert result["degrees"] == [
        "Bachelor of Technology"
    ]

    section_text = " ".join(result["section"])

    assert "Bachelor of Technology" in section_text
    assert "Example Institute" in section_text
    assert "2019 – 2023" in section_text


def test_build_optimized_experience():
    experience = [
        {
            "job_title": "AI/ML Engineer",
            "company": "Example Company",
            "dates": "2021 – Present",
            "bullets": [
                "Built machine learning systems."
            ],
        }
    ]

    result = _build_optimized_experience(experience)

    assert result["job_titles"] == [
        "AI/ML Engineer"
    ]

    assert result["years"] == [
        "2021 – Present"
    ]

    section_text = " ".join(result["section"])

    assert "AI/ML Engineer" in section_text
    assert "Example Company" in section_text
    assert "machine learning" in section_text.lower()


def test_build_optimized_projects():
    projects = [
        {
            "title": "RAG Chatbot",
            "bullets": [
                "Built an LLM chatbot.",
                "Used Python and NLP.",
            ],
        }
    ]

    result = _build_optimized_projects(projects)

    assert len(result) == 1
    assert "RAG Chatbot" in result[0]
    assert "LLM chatbot" in result[0]
    assert "Python" in result[0]
    assert "NLP" in result[0]


def test_final_resume_to_ats_data():
    resume = _build_resume()

    result = _final_resume_to_ats_data(resume)

    assert result["skills"] == resume.skills

    assert result["education"]["degrees"] == [
        "Bachelor of Technology – Computer Science"
    ]

    assert result["experience"]["job_titles"] == [
        "AI/ML Engineer"
    ]

    assert result["projects"]
    assert result["certifications"] == resume.certifications

    assert "Python" in result["raw_text"]
    assert "Machine Learning" in result["raw_text"]
    assert "RAG" in result["raw_text"]
    assert "Bachelor of Technology" in result["raw_text"]


def test_final_resume_dict_is_supported():
    resume = _build_resume()

    result = _final_resume_to_ats_data(
        resume.to_dict()
    )

    assert result["skills"] == resume.skills
    assert result["education"]["degrees"]


def test_evaluator_returns_before_and_after_scores():
    original_resume = {
        "skills": [
            "Python",
            "Machine Learning",
        ],
        "education": {
            "degrees": [
                "Bachelor of Technology"
            ]
        },
        "experience": {
            "years": [
                "2021 – Present"
            ],
            "job_titles": [
                "AI/ML Engineer"
            ],
            "section": [
                "AI/ML Engineer",
                "Built machine learning systems."
            ],
        },
        "projects": [
            "RAG Chatbot using LLMs"
        ],
        "certifications": [],
        "raw_text": (
            "AI/ML Engineer Python Machine Learning "
            "RAG LLM"
        ),
    }

    optimized_resume = _build_resume()

    result = evaluate_resume_optimization(
        original_resume,
        optimized_resume,
        JOB_DESCRIPTION,
    )

    assert "before_score" in result
    assert "after_score" in result
    assert "improvement" in result

    assert "before" in result
    assert "after" in result

    assert set(result["before"]) == {
        "skills",
        "experience",
        "qualifications",
        "keywords",
    }

    assert set(result["after"]) == {
        "skills",
        "experience",
        "qualifications",
        "keywords",
    }


def test_improvement_is_after_minus_before():
    original_resume = {
        "skills": ["Python"],
        "education": {
            "degrees": [
                "Bachelor of Technology"
            ]
        },
        "experience": {
            "years": ["2021 – Present"],
            "job_titles": ["Developer"],
            "section": ["Developer"],
        },
        "projects": [],
        "certifications": [],
        "raw_text": "Python Developer",
    }

    optimized_resume = _build_resume()

    result = evaluate_resume_optimization(
        original_resume,
        optimized_resume,
        JOB_DESCRIPTION,
    )

    assert result["improvement"] == (
        result["after_score"]
        - result["before_score"]
    )


def test_evaluator_does_not_mutate_original_resume():
    original_resume = {
        "skills": [
            "Python",
            "Machine Learning",
        ],
        "education": {
            "degrees": [
                "Bachelor of Technology"
            ]
        },
        "experience": {
            "years": [
                "2021 – Present"
            ],
            "job_titles": [
                "AI/ML Engineer"
            ],
            "section": [
                "AI/ML Engineer",
            ],
        },
        "projects": [
            "RAG Chatbot"
        ],
        "certifications": [],
        "raw_text": "Python Machine Learning RAG",
    }

    original_snapshot = deepcopy(original_resume)

    evaluate_resume_optimization(
        original_resume,
        _build_resume(),
        JOB_DESCRIPTION,
    )

    assert original_resume == original_snapshot


def test_evaluator_accepts_empty_original_resume():
    result = evaluate_resume_optimization(
        {},
        _build_resume(),
        JOB_DESCRIPTION,
    )

    assert "before_score" in result
    assert "after_score" in result
    assert isinstance(result["improvement"], int)


def test_evaluator_preserves_component_score_structure():
    result = evaluate_resume_optimization(
        {},
        _build_resume(),
        JOB_DESCRIPTION,
    )

    for component in (
        "skills",
        "experience",
        "qualifications",
        "keywords",
    ):
        assert component in result["before"]
        assert component in result["after"]