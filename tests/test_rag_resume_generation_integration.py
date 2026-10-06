"""Integration tests for resume-aware RAG in resume generation."""

from copy import deepcopy

import app.resume_generation_pipeline as generation_module


class FakeRAGService:
    """Capture resume data passed through the generation pipeline."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.calls = []

    def get_phase11_payload(self, jd_analysis, resume_data=None):
        self.calls.append(
            {
                "jd_analysis": deepcopy(jd_analysis),
                "resume_data": deepcopy(resume_data),
            }
        )

        return {
            "skills_to_emphasize": ["Python"],
            "experience_to_emphasize": [],
            "keywords_to_emphasize": ["machine learning"],
            "emphasis_instructions": [],
        }


def _sample_resume_data():
    """Return representative structured resume data."""

    return {
        "summary": "Python developer with machine learning experience.",
        "skills": ["Python", "SQL", "Machine Learning"],
        "experience": [
            {
                "company": "Example Company",
                "role": "Python Developer",
                "description": "Built machine learning applications.",
            }
        ],
        "projects": [
            {
                "name": "AI Resume Analyzer",
                "description": "Built an AI-powered resume optimization system.",
            }
        ],
        "education": ["B.Tech"],
    }


def test_get_rag_optimization_passes_resume_data():
    """The generation pipeline RAG helper should pass resume data."""

    resume_data = _sample_resume_data()
    rag_service = FakeRAGService()

    result = generation_module._get_rag_optimization(
        job_description="Python machine learning engineer",
        resume_data=resume_data,
        rag_service=rag_service,
    )

    assert isinstance(result, dict)
    assert len(rag_service.calls) == 1
    assert rag_service.calls[0]["resume_data"] == resume_data


def test_get_rag_optimization_does_not_mutate_resume_data():
    """The RAG handoff must not mutate the original resume."""

    resume_data = _sample_resume_data()
    original = deepcopy(resume_data)

    rag_service = FakeRAGService()

    generation_module._get_rag_optimization(
        job_description="Python machine learning engineer",
        resume_data=resume_data,
        rag_service=rag_service,
    )

    assert resume_data == original


def test_get_rag_optimization_passes_analyzed_jd():
    """The existing JD analysis should be passed to RAG."""

    resume_data = _sample_resume_data()
    rag_service = FakeRAGService()

    expected_jd_analysis = {
        "cleaned_text": "Python machine learning engineer",
        "required_skills": ["Python", "Machine Learning"],
        "qualifications": [],
        "experience": [],
        "keywords": ["machine learning"],
    }

    original_analyzer = generation_module.analyze_job_description

    generation_module.analyze_job_description = (
        lambda text: deepcopy(expected_jd_analysis)
    )

    try:
        generation_module._get_rag_optimization(
            job_description="Python machine learning engineer",
            resume_data=resume_data,
            rag_service=rag_service,
        )
    finally:
        generation_module.analyze_job_description = original_analyzer

    assert len(rag_service.calls) == 1
    assert rag_service.calls[0]["jd_analysis"] == expected_jd_analysis


def test_get_rag_optimization_without_resume_data_remains_compatible():
    """The RAG helper should still work without resume data."""

    rag_service = FakeRAGService()

    result = generation_module._get_rag_optimization(
        job_description="Python machine learning engineer",
        rag_service=rag_service,
    )

    assert isinstance(result, dict)
    assert len(rag_service.calls) == 1
    assert rag_service.calls[0]["resume_data"] is None


def test_get_rag_optimization_disabled_returns_none():
    """Disabled RAG should return None without requesting a payload."""

    rag_service = FakeRAGService(enabled=False)

    result = generation_module._get_rag_optimization(
        job_description="Python machine learning engineer",
        resume_data=_sample_resume_data(),
        rag_service=rag_service,
    )

    assert result is None
    assert rag_service.calls == []