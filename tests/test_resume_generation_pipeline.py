import pytest

from app.final_resume_models import FinalResume
from app.resume_generation_pipeline import (
    generate_optimized_resume,
)


def _resume_data():
    return {
        "personal_info": {
            "name": "John Doe",
            "email": "john@example.com",
        },
        "summary": "Software engineer.",
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
        ],
        "experience": [
            {
                "job_title": "ML Engineer",
                "company": "ABC",
                "dates": "2024-2026",
                "bullets": [
                    "Built Python machine learning models."
                ],
            }
        ],
        "projects": [
            {
                "title": "Recommendation System",
                "description": "Built a recommendation system.",
            }
        ],
        "education": [
            {
                "degree": "B.Tech",
                "institution": "ABC University",
                "year": "2024",
            }
        ],
        "certifications": [],
    }


def _ats_result():
    return {
        "keywords": [
            "machine learning",
            "python",
            "sql",
        ],
        "skills": [
            "Python",
            "Machine Learning",
        ],
        "missing_skills": [],
        "missing_keywords": [],
        "missing_qualifications": [],
    }


def _rewrite_result():
    return {
        "summary": "Machine learning engineer with Python experience.",
        "experience": [
            {
                "job_title": "ML Engineer",
                "company": "ABC",
                "dates": "2024-2026",
                "bullets": [
                    "Built Python machine learning models."
                ],
            }
        ],
        "projects": [
            {
                "title": "Recommendation System",
                "description": "Built a recommendation system.",
            }
        ],
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
        ],
        "validation": {
            "valid": True,
            "unsupported_claims": [],
        },
    }


def test_pipeline_returns_final_resume(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Machine learning Python SQL",
        ats_result=_ats_result(),
    )

    assert isinstance(
        result["final_resume"],
        FinalResume,
    )


def test_pipeline_generates_valid_final_resume(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Machine learning Python SQL",
        ats_result=_ats_result(),
    )

    assert result["validation"]["valid"] is True
    assert result["validation"]["errors"] == []


def test_pipeline_preserves_personal_information(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        ats_result=_ats_result(),
    )

    personal_info = result["final_resume"].personal_info

    assert personal_info["name"] == "John Doe"
    assert personal_info["email"] == "john@example.com"


def test_pipeline_uses_rewritten_content(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        ats_result=_ats_result(),
    )

    resume = result["final_resume"]

    assert (
        resume.summary
        == "Machine learning engineer with Python experience."
    )

    assert resume.experience[0]["job_title"] == "ML Engineer"


def test_pipeline_applies_length_control(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        ats_result=_ats_result(),
        target_pages=1,
    )

    assert result["length_control"]["target_pages"] == 1
    assert "sections" in result["length_control"]


def test_pipeline_returns_tailoring_plan(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        ats_result=_ats_result(),
    )

    assert "tailoring_plan" in result
    assert isinstance(
        result["tailoring_plan"],
        dict,
    )


def test_pipeline_returns_rewrite_result(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        ats_result=_ats_result(),
    )

    assert result["rewrite_result"]["summary"]


def test_pipeline_preserves_input_data(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    resume_data = _resume_data()
    ats_result = _ats_result()

    original_resume_data = {
        key: value.copy()
        if isinstance(value, dict)
        else list(value)
        if isinstance(value, list)
        else value
        for key, value in resume_data.items()
    }

    original_ats = {
        key: value.copy()
        if isinstance(value, list)
        else value
        for key, value in ats_result.items()
    }

    generate_optimized_resume(
        resume_text="Original resume",
        resume_data=resume_data,
        ats_result=ats_result,
    )

    assert resume_data == original_resume_data
    assert ats_result == original_ats


def test_pipeline_supports_custom_tailoring_plan(monkeypatch):
    monkeypatch.setenv(
        "RAG_ENABLED",
        "false",
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    custom_plan = {
        "tailoring_plan": {
            "priorities": [],
            "summary": [],
            "skills": [],
            "experience": [],
            "keywords": [],
            "qualifications": [],
            "warnings": [],
        }
    }

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        ats_result=_ats_result(),
        tailoring_plan=custom_plan,
    )

    assert result["tailoring_plan"] == custom_plan

    


def test_pipeline_sets_metadata(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        ats_result=_ats_result(),
        target_pages=2,
        target_job_title="Machine Learning Engineer",
    )

    metadata = result["final_resume"].metadata

    assert metadata.target_pages == 2
    assert metadata.optimization_enabled is True
    assert (
        metadata.target_job_title
        == "Machine Learning Engineer"
    )


def test_pipeline_orders_sections_for_fresher(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        ats_result=_ats_result(),
        experience_level="fresher",
    )

    order = result["final_resume"].section_order

    assert "projects" in order
    assert "skills" in order
    assert "experience" in order


def test_pipeline_rejects_invalid_target_pages(monkeypatch):
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    with pytest.raises(ValueError):
        generate_optimized_resume(
            resume_text="Original resume",
            resume_data=_resume_data(),
            ats_result=_ats_result(),
            target_pages=0,
        )

def test_normalize_rewrite_sections_extracts_summary():
    from app.resume_generation_pipeline import (
        _normalize_rewrite_sections,
    )

    result = _normalize_rewrite_sections(
        rewrite_result={
            "summary": {
                "original": "Original summary",
                "rewritten": "Rewritten summary",
                "changes": [
                    "Improved clarity"
                ],
                "validation": {
                    "meaning_preserved": True,
                    "unsupported_claims": [],
                    "grounding_status": "grounded",
                },
            },
        },
        resume_data={},
    )

    assert result["summary"] == (
        "Rewritten summary"
    )


def test_normalize_rewrite_sections_extracts_skills_only():
    from app.resume_generation_pipeline import (
        _normalize_rewrite_sections,
    )

    result = _normalize_rewrite_sections(
        rewrite_result={
            "skills": {
                "original": [
                    "Python",
                    "SQL",
                ],
                "rewritten": [
                    "Python",
                    "SQL",
                    "Flask",
                ],
                "changes": [
                    "Improved naming"
                ],
                "validation": {
                    "meaning_preserved": True,
                    "unsupported_claims": [],
                    "grounding_status": "grounded",
                },
            },
        },
        resume_data={
            "skills": [
                "Python",
                "SQL",
            ],
        },
    )

    assert result["skills"] == [
        "Python",
        "SQL",
        "Flask",
    ]

    assert all(
        isinstance(skill, str)
        for skill in result["skills"]
    )


def test_normalize_rewrite_sections_preserves_experience_structure():
    from app.resume_generation_pipeline import (
        _normalize_rewrite_sections,
    )

    result = _normalize_rewrite_sections(
        rewrite_result={
            "experience": [
                {
                    "original": "Built Flask app.",
                    "rewritten": (
                        "Developed a Flask application."
                    ),
                    "changes": [
                        "Improved wording"
                    ],
                    "validation": {
                        "meaning_preserved": True,
                        "unsupported_claims": [],
                        "grounding_status": "grounded",
                    },
                }
            ],
        },
        resume_data={
            "experience": [
                {
                    "job_title": "Software Developer",
                    "company": "ABC Technologies",
                    "dates": "2023 - Present",
                    "bullets": [
                        "Built Flask app."
                    ],
                }
            ],
        },
    )

    item = result["experience"][0]

    assert item["job_title"] == (
        "Software Developer"
    )

    assert item["company"] == (
        "ABC Technologies"
    )

    assert item["dates"] == (
        "2023 - Present"
    )

    assert item["bullets"] == [
        "Developed a Flask application."
    ]

    assert "original" not in item
    assert "changes" not in item
    assert "validation" not in item


def test_normalize_rewrite_sections_converts_string_source():
    from app.resume_generation_pipeline import (
        _normalize_rewrite_sections,
    )

    result = _normalize_rewrite_sections(
        rewrite_result={
            "projects": [
                {
                    "original": "Built an ML project.",
                    "rewritten": (
                        "Developed a machine learning project."
                    ),
                }
            ],
        },
        resume_data={
            "projects": [
                "Built an ML project."
            ],
        },
    )

    assert result["projects"] == [
        {
            "description": (
                "Developed a machine learning project."
            )
        }
    ]


def test_normalize_rewrite_sections_does_not_leak_validation_metadata():
    from app.resume_generation_pipeline import (
        _normalize_rewrite_sections,
    )

    result = _normalize_rewrite_sections(
        rewrite_result={
            "summary": {
                "original": "Original",
                "rewritten": "Rewritten",
                "changes": ["Changed wording"],
                "validation": {
                    "meaning_preserved": True,
                    "unsupported_claims": [],
                    "grounding_status": "grounded",
                },
            },
            "skills": {
                "original": ["Python"],
                "rewritten": ["Python"],
                "changes": ["Normalized"],
                "validation": {
                    "meaning_preserved": True,
                    "unsupported_claims": [],
                    "grounding_status": "grounded",
                },
            },
            "experience": [
                {
                    "original": "Built systems.",
                    "rewritten": "Developed systems.",
                    "changes": ["Improved wording"],
                    "validation": {
                        "meaning_preserved": True,
                        "unsupported_claims": [],
                        "grounding_status": "grounded",
                    },
                }
            ],
            "projects": [
                {
                    "original": "Built project.",
                    "rewritten": "Developed project.",
                    "changes": ["Improved wording"],
                    "validation": {
                        "meaning_preserved": True,
                        "unsupported_claims": [],
                        "grounding_status": "grounded",
                    },
                }
            ],
        },
        resume_data={
            "experience": [
                {
                    "job_title": "Developer",
                }
            ],
            "projects": [
                {
                    "title": "Project",
                }
            ],
            "skills": ["Python"],
        },
    )

    final_text = str(result)

    assert "meaning_preserved" not in final_text
    assert "unsupported_claims" not in final_text
    assert "grounding_status" not in final_text
    assert "changes" not in final_text

def test_generate_optimized_resume_uses_clean_summary(
    monkeypatch,
):
    from app.resume_generation_pipeline import (
        generate_optimized_resume,
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.generate_tailoring_plan",
        lambda **kwargs: {},
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: {
            "summary": {
                "original": "Old summary",
                "rewritten": "Clean rewritten summary",
                "changes": ["Improved clarity"],
                "validation": {
                    "meaning_preserved": True,
                    "unsupported_claims": [],
                    "grounding_status": "grounded",
                },
            },
            "experience": [],
            "projects": [],
            "skills": {},
            "validation": {},
        },
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data={
            "personal_info": {
                "name": "Test User",
            },
            "summary": "Old summary",
            "skills": [],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
        },
        job_description="Python Developer",
        ats_result={},
    )

    final_resume = result["final_resume"]

    assert final_resume.summary == (
        "Clean rewritten summary"
    )

    assert isinstance(
        final_resume.summary,
        str,
    )


def test_generate_optimized_resume_uses_clean_skills(
    monkeypatch,
):
    from app.resume_generation_pipeline import (
        generate_optimized_resume,
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.generate_tailoring_plan",
        lambda **kwargs: {},
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: {
            "summary": {},
            "experience": [],
            "projects": [],
            "skills": {
                "original": [
                    "Python",
                    "SQL",
                ],
                "rewritten": [
                    "Python",
                    "SQL",
                    "Flask",
                ],
                "changes": [
                    "Improved naming",
                ],
                "validation": {
                    "meaning_preserved": True,
                    "unsupported_claims": [],
                    "grounding_status": "grounded",
                },
            },
            "validation": {},
        },
    )

    result = generate_optimized_resume(
        resume_text="Python SQL resume",
        resume_data={
            "personal_info": {
                "name": "Test User",
            },
            "summary": "",
            "skills": [
                "Python",
                "SQL",
            ],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
        },
        job_description="Python Developer",
        ats_result={},
    )

    final_resume = result["final_resume"]

    assert final_resume.skills == [
        "Python",
        "SQL",
        "Flask",
    ]

    assert all(
        isinstance(skill, str)
        for skill in final_resume.skills
    )


def test_generate_optimized_resume_uses_clean_experience_and_projects(
    monkeypatch,
):
    from app.resume_generation_pipeline import (
        generate_optimized_resume,
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.generate_tailoring_plan",
        lambda **kwargs: {},
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: {
            "summary": {},
            "skills": {},
            "experience": [
                {
                    "original": "Built Flask app.",
                    "rewritten": (
                        "Developed a Flask application."
                    ),
                    "changes": [
                        "Improved wording",
                    ],
                    "validation": {
                        "meaning_preserved": True,
                        "unsupported_claims": [],
                        "grounding_status": "grounded",
                    },
                }
            ],
            "projects": [
                {
                    "original": "Built resume analyzer.",
                    "rewritten": (
                        "Developed an AI resume analyzer."
                    ),
                    "changes": [
                        "Improved clarity",
                    ],
                    "validation": {
                        "meaning_preserved": True,
                        "unsupported_claims": [],
                        "grounding_status": "grounded",
                    },
                }
            ],
            "validation": {},
        },
    )

    result = generate_optimized_resume(
        resume_text="Developer resume",
        resume_data={
            "personal_info": {
                "name": "Test User",
            },
            "summary": "",
            "skills": [],
            "experience": [
                {
                    "job_title": "Software Developer",
                    "company": "ABC",
                    "dates": "2023 - Present",
                    "bullets": [
                        "Built Flask app.",
                    ],
                }
            ],
            "projects": [
                {
                    "title": "AI Resume Analyzer",
                    "technologies": [
                        "Python",
                    ],
                    "bullets": [
                        "Built resume analyzer.",
                    ],
                }
            ],
            "education": [],
            "certifications": [],
        },
        job_description="Python Developer",
        ats_result={},
    )

    final_resume = result["final_resume"]

    assert len(final_resume.experience) == 1
    assert len(final_resume.projects) == 1

    experience = final_resume.experience[0]
    project = final_resume.projects[0]

    assert experience["job_title"] == (
        "Software Developer"
    )

    assert experience["company"] == "ABC"

    assert experience["bullets"] == [
        "Developed a Flask application."
    ]

    assert project["title"] == (
        "AI Resume Analyzer"
    )

    assert project["technologies"] == [
        "Python"
    ]

    assert project["bullets"] == [
        "Developed an AI resume analyzer."
    ]

    final_text = str(final_resume.to_dict())

    assert "meaning_preserved" not in final_text
    assert "unsupported_claims" not in final_text
    assert "grounding_status" not in final_text
    assert "'changes'" not in final_text
    assert "'original'" not in final_text


def test_generate_optimized_resume_falls_back_to_original_skills(
    monkeypatch,
):
    from app.resume_generation_pipeline import (
        generate_optimized_resume,
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.generate_tailoring_plan",
        lambda **kwargs: {},
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: {
            "summary": {},
            "experience": [],
            "projects": [],
            "skills": {
                "original": [
                    "Python",
                ],
                "rewritten": [],
                "changes": [],
                "validation": {
                    "meaning_preserved": False,
                    "unsupported_claims": [],
                    "grounding_status": "needs_review",
                },
            },
            "validation": {},
        },
    )

    result = generate_optimized_resume(
        resume_text="Python developer",
        resume_data={
            "personal_info": {
                "name": "Test User",
            },
            "summary": "",
            "skills": [
                "Python",
            ],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
        },
        job_description="Python Developer",
        ats_result={},
    )

    assert result["final_resume"].skills == [
        "Python"
    ]
def test_normalize_education_combines_years_and_preserves_institution():
    from app.resume_generation_pipeline import _normalize_education

    education = {
        "section": [
            "Bachelor of Technology (B.Tech) – Computer Science and Engineering",
            "Dadi Institute of Engineering and Technology 2019 – 2023",
            "CGPA: 7.69",
        ],
        "degrees": [
            "Bachelor of Technology (B.Tech) – Computer Science and Engineering"
        ],
        "years": [
            "2019",
            "2023",
        ],
    }

    result = _normalize_education(education)

    assert result == [
        {
            "degree": (
                "Bachelor of Technology (B.Tech) – "
                "Computer Science and Engineering"
            ),
            "year": "2019 – 2023",
            "institution": "Dadi Institute of Engineering and Technology",
        }
    ]

def test_normalize_rewritten_collection_groups_multiple_rewrites_into_one_experience():
    from app.resume_generation_pipeline import (
        _normalize_rewritten_collection,
    )

    original_items = [
        {
            "job_title": "Freelance LLM Trainer",
            "company": "Outlier",
            "dates": "Sep 2023 – Present",
            "location": "Remote, India",
        }
    ]

    rewritten_items = [
        {
            "rewritten": (
                "Freelance LLM Trainer – Outlier | "
                "September 2023 – Present"
            )
        },
        {
            "rewritten": (
                "Contributed to the training and evaluation "
                "of Large Language Models (LLMs)."
            )
        },
        {
            "rewritten": (
                "Performed prompt evaluation and output "
                "analysis to support model accuracy."
            )
        },
        {
            "rewritten": (
                "Identified hallucinations and logical "
                "inconsistencies in AI-generated responses."
            )
        },
    ]

    result = _normalize_rewritten_collection(
        rewritten_items=rewritten_items,
        original_items=original_items,
    )

    assert len(result) == 1

    assert result[0]["job_title"] == (
        "Freelance LLM Trainer"
    )

    assert result[0]["company"] == "Outlier"

    assert result[0]["dates"] == (
        "September 2023 – Present"
    )


    assert result[0]["location"] == (
        "Remote, India"
    )

    assert result[0]["bullets"] == [
        (
            "Contributed to the training and evaluation "
            "of Large Language Models (LLMs)."
        ),
        (
            "Performed prompt evaluation and output "
            "analysis to support model accuracy."
        ),
        (
            "Identified hallucinations and logical "
            "inconsistencies in AI-generated responses."
        ),
    ]

def test_normalize_rewritten_collection_splits_multiline_experience_rewrite():
    from app.resume_generation_pipeline import (
        _normalize_rewritten_collection,
    )

    original_items = [
        {
            "job_title": "Freelance LLM Trainer",
            "company": "Outlier",
            "dates": "2023 – Present",
            "location": "Remote, India",
        }
    ]

    rewritten_items = [
        {
            "rewritten": (
                "Freelance LLM Trainer – Outlier | Sep 2023 – Present\n"
                "Remote, India\n"
                "• Supported the training and evaluation of Large Language Models (LLMs) "
                "through structured data annotation, response validation, and content "
                "quality assessment.\n"
                "• Evaluated prompts and analyzed model outputs to assess accuracy, "
                "contextual relevance, and response consistency.\n"
                "• Detected hallucinations, factual inaccuracies, bias, and logical "
                "inconsistencies in LLM-generated responses using analytical reasoning.\n"
                "• Applied quality assurance (QA) guidelines to produce high-precision "
                "training data and maintain standardized model evaluation processes.\n"
                "• Assisted with prompt engineering improvements to enhance response "
                "quality and reduce ambiguity.\n"
                "• Consistently met productivity and quality benchmarks while working "
                "independently in a remote environment under defined SLAs."
            )
        }
    ]

    result = _normalize_rewritten_collection(
        rewritten_items=rewritten_items,
        original_items=original_items,
    )

    assert len(result) == 1

    assert result[0]["job_title"] == (
        "Freelance LLM Trainer"
    )

    assert result[0]["company"] == "Outlier"

    assert result[0]["dates"] == (
        "Sep 2023 – Present"
    )

    assert result[0]["location"] == (
        "Remote, India"
    )

    assert len(result[0]["bullets"]) == 6

    assert result[0]["bullets"][0].startswith(
        "• Supported the training and evaluation"
    )

    assert result[0]["bullets"][5].startswith(
        "• Consistently met productivity"
    )

    assert "years" not in result[0]

def test_normalize_projects_splits_title_and_bullets():
    from app.resume_generation_pipeline import _normalize_projects

    projects = [
        {
            "description": (
                "End-to-End Machine Learning Pipeline – Heart Disease Prediction\n"
                "•Developed an end-to-end machine learning pipeline covering data preprocessing, "
                "feature engineering, model training, and evaluation.\n"
                "•Applied Scikit-learn Logistic Regression for binary heart disease classification.\n"
                "•Conducted exploratory data analysis, addressed missing values, and prepared "
                "structured datasets for modeling."
            )
        }
    ]

    result = _normalize_projects(projects)

    assert result == [
        {
            "title": (
                "End-to-End Machine Learning Pipeline – "
                "Heart Disease Prediction"
            ),
            "bullets": [
                (
                    "•Developed an end-to-end machine learning pipeline covering "
                    "data preprocessing, feature engineering, model training, "
                    "and evaluation."
                ),
                (
                    "•Applied Scikit-learn Logistic Regression for binary "
                    "heart disease classification."
                ),
                (
                    "•Conducted exploratory data analysis, addressed missing "
                    "values, and prepared structured datasets for modeling."
                ),
            ],
        }
    ]


def test_normalize_projects_preserves_multiple_projects():
    from app.resume_generation_pipeline import _normalize_projects

    projects = [
        {
            "description": (
                "Project One\n"
                "•Built project one.\n"
                "•Tested project one."
            )
        },
        {
            "description": (
                "Project Two\n"
                "•Built project two.\n"
                "•Tested project two."
            )
        },
    ]

    result = _normalize_projects(projects)

    assert result == [
        {
            "title": "Project One",
            "bullets": [
                "•Built project one.",
                "•Tested project one.",
            ],
        },
        {
            "title": "Project Two",
            "bullets": [
                "•Built project two.",
                "•Tested project two.",
            ],
        },
    ]