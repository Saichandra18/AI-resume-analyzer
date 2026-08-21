from app.keyword_matcher import (
    extract_resume_keywords,
    match_keywords,
    normalize_keyword,
)


def test_normalize_keyword():
    assert normalize_keyword(" Python ") == "python"
    assert normalize_keyword("Power-BI") == "power bi"
    assert normalize_keyword("SQL!") == "sql"


def test_extract_resume_keywords_from_skills():
    resume_data = {
        "skills": [
            "Python",
            "SQL",
            "Pandas",
        ]
    }

    keywords = extract_resume_keywords(resume_data)

    assert "python" in keywords
    assert "sql" in keywords
    assert "pandas" in keywords


def test_extract_resume_keywords_from_education():
    resume_data = {
        "education": {
            "degrees": [
                "Bachelor of Technology in Computer Science"
            ]
        }
    }

    keywords = extract_resume_keywords(resume_data)

    assert "bachelor" in keywords
    assert "technology" in keywords
    assert "computer" in keywords
    assert "science" in keywords


def test_extract_resume_keywords_from_experience():
    resume_data = {
        "experience": {
            "section": [
                "Created Power BI dashboards"
            ],
            "job_titles": [
                "Data Analyst"
            ]
        }
    }

    keywords = extract_resume_keywords(resume_data)

    assert "created" in keywords
    assert "power" in keywords
    assert "bi" in keywords
    assert "dashboards" in keywords
    assert "data" in keywords
    assert "analyst" in keywords


def test_extract_resume_keywords_from_projects():
    resume_data = {
        "projects": [
            "Sales Analytics Dashboard"
        ]
    }

    keywords = extract_resume_keywords(resume_data)

    assert "sales" in keywords
    assert "analytics" in keywords
    assert "dashboard" in keywords


def test_extract_resume_keywords_from_certifications():
    resume_data = {
        "certifications": [
            "Microsoft Power BI Certification"
        ]
    }

    keywords = extract_resume_keywords(resume_data)

    assert "microsoft" in keywords
    assert "power" in keywords
    assert "bi" in keywords
    assert "certification" in keywords

def test_extract_resume_keywords_preserves_multi_word_phrases():
    resume_data = {
        "skills": [
            "Machine Learning",
            "Power BI",
            "Artificial Intelligence",
        ]
    }

    keywords = extract_resume_keywords(resume_data)

    assert "machine" in keywords
    assert "learning" in keywords
    assert "machine learning" in keywords

    assert "power" in keywords
    assert "bi" in keywords
    assert "power bi" in keywords

    assert "artificial intelligence" in keywords

def test_match_multi_word_job_keywords():
    resume_data = {
        "skills": [
            "Python",
            "Machine Learning",
            "Power BI",
            "Artificial Intelligence",
        ]
    }

    job_keywords = [
        "python",
        "machine learning",
        "power bi",
        "artificial intelligence",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "python",
        "machine learning",
        "power bi",
        "artificial intelligence",
    ]

    assert result["missing"] == []

def test_match_ai_aliases():
    resume_data = {
        "skills": [
            "Artificial Intelligence",
            "Machine Learning",
            "Large Language Models",
            "Retrieval Augmented Generation",
        ]
    }

    job_keywords = [
        "ai",
        "ml",
        "llm",
        "rag",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "ai",
        "ml",
        "llm",
        "rag",
    ]

    assert result["missing"] == []

def test_match_ci_cd_variations():
    resume_data = {
        "skills": [
            "CI/CD",
        ]
    }

    job_keywords = [
        "ci cd",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "ci cd"
    ]

    assert result["missing"] == []


def test_basic_keyword_matching():
    resume_data = {
        "skills": [
            "Python",
            "SQL",
        ],
        "experience": {
            "section": [
                "Data Analyst"
            ],
            "job_titles": [
                "Data Analyst"
            ]
        }
    }

    job_keywords = [
        "python",
        "sql",
        "analyst",
        "dashboard",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "python",
        "sql",
        "analyst",
    ]

    assert result["missing"] == [
        "dashboard"
    ]


def test_case_insensitive_matching():
    resume_data = {
        "skills": [
            "Python",
            "SQL",
        ]
    }

    job_keywords = [
        "PYTHON",
        "sql",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "PYTHON",
        "sql",
    ]

    assert result["missing"] == []


def test_missing_keywords():
    resume_data = {
        "skills": [
            "Python"
        ]
    }

    job_keywords = [
        "python",
        "sql",
        "power",
        "bi",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "python"
    ]

    assert result["missing"] == [
        "sql",
        "power",
        "bi",
    ]


def test_duplicate_job_keywords():
    resume_data = {
        "skills": [
            "Python"
        ]
    }

    job_keywords = [
        "python",
        "python",
        "Python",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "python"
    ]


def test_empty_resume():
    result = match_keywords(
        {},
        ["python", "sql"],
    )

    assert result["matched"] == []
    assert result["missing"] == [
        "python",
        "sql",
    ]


def test_empty_job_keywords():
    resume_data = {
        "skills": [
            "Python",
            "SQL",
        ]
    }

    result = match_keywords(
        resume_data,
        [],
    )

    assert result["matched"] == []
    assert result["missing"] == []


def test_none_inputs():
    result = match_keywords(None, None)

    assert result["matched"] == []
    assert result["missing"] == []

def test_match_full_terms_against_resume_abbreviations():
    resume_data = {
        "skills": [
            "AI",
            "ML",
            "LLM",
            "RAG",
            "CI/CD",
        ]
    }

    job_keywords = [
        "artificial intelligence",
        "machine learning",
        "large language models",
        "retrieval augmented generation",
        "ci cd",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "artificial intelligence",
        "machine learning",
        "large language models",
        "retrieval augmented generation",
        "ci cd",
    ]

    assert result["missing"] == []

def test_match_neural_network_singular_plural():
    resume_data = {
        "skills": [
            "Neural Networks",
        ]
    }

    job_keywords = [
        "neural network",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "neural network"
    ]

    assert result["missing"] == []

def test_match_ci_cd_against_ci_cd():
    resume_data = {
        "skills": [
            "CI/CD",
        ]
    }

    job_keywords = [
        "ci cd",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "ci cd"
    ]

    assert result["missing"] == []

def test_match_keywords_against_raw_resume_text():
    resume_data = {
        "skills": [],
        "raw_text": """
        Core Competencies

        Deep Learning: TensorFlow, PyTorch, Neural Networks

        Deployment Concepts:
        Git Version Control, CI/CD Basics
        """,
    }

    job_keywords = [
        "neural networks",
        "neural network",
        "ci cd",
    ]

    result = match_keywords(
        resume_data,
        job_keywords,
    )

    assert result["matched"] == [
        "neural networks",
        "neural network",
        "ci cd",
    ]

    assert result["missing"] == []