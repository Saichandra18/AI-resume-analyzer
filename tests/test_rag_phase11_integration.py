"""Tests for Phase 11 integration with optional RAG optimization."""

from copy import deepcopy

import pytest

from app.final_resume_models import FinalResume
from app.resume_generation_pipeline import generate_optimized_resume


def _resume_data():
    return {
        "personal_info": {
            "name": "John Doe",
            "email": "john@example.com",
        },
        "summary": "Software engineer.",
        "skills": ["Python", "SQL"],
        "experience": [
            {
                "job_title": "Software Developer",
                "company": "ABC",
                "dates": "2024-2026",
                "bullets": ["Built Python applications."],
            }
        ],
        "projects": [],
        "education": [],
        "certifications": [],
    }


def _ats_result():
    return {
        "keywords": ["python", "sql"],
        "skills": ["Python"],
        "missing_skills": [],
        "missing_keywords": [],
        "missing_qualifications": [],
    }


def _jd_analysis():
    return {
        "cleaned_text": "Python developer",
        "required_skills": ["Python"],
        "qualifications": [],
        "experience": None,
        "keywords": ["Python"],
    }


def _rewrite_result():
    return {
        "summary": "Software engineer with Python experience.",
        "experience": [
            {
                "job_title": "Software Developer",
                "company": "ABC",
                "dates": "2024-2026",
                "bullets": ["Built Python applications."],
            }
        ],
        "projects": [],
        "skills": ["Python", "SQL"],
        "validation": {
            "valid": True,
            "unsupported_claims": [],
        },
    }


def _rag_payload():
    return {
        "skills_to_emphasize": ["Python"],
        "experience_to_emphasize": [
            "Python application development"
        ],
        "keywords_to_emphasize": ["SQL"],
        "emphasis_instructions": [
            "Emphasize supported Python experience."
        ],
        "grounding": [
            {
                "evidence_id": "evidence:0",
                "source_chunk_ids": ["doc:0"],
            }
        ],
        "metadata": {
            "rag_enabled": True,
            "retrieval_count": 1,
        },
    }


class FakeRAGService:
    def __init__(self, enabled=False, payload=None):
        self.enabled = enabled
        self.payload = deepcopy(payload or _rag_payload())
        self.calls = []

    def get_phase11_payload(self, jd_analysis):
        self.calls.append(deepcopy(jd_analysis))
        return deepcopy(self.payload)


class ResumeAwareFakeRAGService:
    """Fake service matching the current production RAG contract."""

    def __init__(self, enabled=True, payload=None):
        self.enabled = enabled
        self.payload = deepcopy(payload or _rag_payload())
        self.calls = []

    def get_phase11_payload(self, jd_analysis, resume_data=None):
        self.calls.append(
            {
                "jd_analysis": deepcopy(jd_analysis),
                "resume_data": deepcopy(resume_data),
            }
        )
        return deepcopy(self.payload)


def test_rag_disabled_does_not_call_service(monkeypatch):
    service = FakeRAGService(enabled=False)

    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert service.calls == []
    assert result["rag_optimization"] is None
    assert isinstance(result["final_resume"], FinalResume)


def test_rag_disabled_preserves_existing_tailoring_behavior(monkeypatch):
    service = FakeRAGService(enabled=False)
    captured = {}

    def fake_rewrite(**kwargs):
        captured["tailoring_plan"] = deepcopy(
            kwargs["tailoring_plan"]
        )
        return _rewrite_result()

    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        fake_rewrite,
    )

    custom_plan = {
        "tailoring_plan": {
            "priorities": [],
            "summary": [],
            "skills": [],
            "experience": [],
            "keywords": [],
            "qualifications": [],
            "warnings": ["Do not fabricate experience."],
        }
    }

    generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        tailoring_plan=custom_plan,
        rag_service=service,
    )

    assert captured["tailoring_plan"] == custom_plan


def test_rag_enabled_calls_existing_jd_analyzer(monkeypatch):
    service = FakeRAGService(enabled=True)
    captured = {}

    def fake_analyzer(job_description):
        captured["job_description"] = job_description
        return _jd_analysis()

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        fake_analyzer,
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description=" Python developer ",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert captured["job_description"] == " Python developer "
    assert service.calls == [_jd_analysis()]


def test_rag_enabled_payload_is_added_to_nested_tailoring_plan(
    monkeypatch,
):
    service = FakeRAGService(enabled=True)
    captured = {}

    def fake_rewrite(**kwargs):
        captured["tailoring_plan"] = kwargs["tailoring_plan"]
        return _rewrite_result()

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        fake_rewrite,
    )

    custom_plan = {
        "tailoring_plan": {
            "priorities": [{"rank": 1}],
            "summary": [{"type": "summary"}],
            "skills": [{"type": "skill"}],
            "experience": [],
            "keywords": [],
            "qualifications": [],
            "warnings": ["Keep claims grounded."],
        }
    }

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        tailoring_plan=custom_plan,
        rag_service=service,
    )

    nested = captured["tailoring_plan"]["tailoring_plan"]

    assert nested["priorities"] == [{"rank": 1}]
    assert nested["summary"] == [{"type": "summary"}]
    assert nested["skills"] == [{"type": "skill"}]
    assert nested["warnings"] == ["Keep claims grounded."]
    assert nested["rag_optimization"] == service.payload
    assert result["rag_optimization"] == service.payload


def test_rag_enabled_does_not_replace_existing_tailoring_plan(
    monkeypatch,
):
    service = FakeRAGService(enabled=True)
    captured = {}

    def fake_rewrite(**kwargs):
        captured["tailoring_plan"] = deepcopy(
            kwargs["tailoring_plan"]
        )
        return _rewrite_result()

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        fake_rewrite,
    )

    custom_plan = {
        "tailoring_plan": {
            "priorities": ["existing"],
            "summary": ["existing summary"],
            "skills": ["existing skill"],
            "experience": ["existing experience"],
            "keywords": ["existing keyword"],
            "qualifications": ["existing qualification"],
            "warnings": ["existing warning"],
        }
    }

    generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        tailoring_plan=custom_plan,
        rag_service=service,
    )

    nested = captured["tailoring_plan"]["tailoring_plan"]

    assert nested["priorities"] == ["existing"]
    assert nested["summary"] == ["existing summary"]
    assert nested["skills"] == ["existing skill"]
    assert nested["experience"] == ["existing experience"]
    assert nested["keywords"] == ["existing keyword"]
    assert nested["qualifications"] == ["existing qualification"]
    assert nested["warnings"] == ["existing warning"]


def test_rag_payload_is_defensively_copied(monkeypatch):
    service = FakeRAGService(enabled=True)
    captured = {}

    def fake_rewrite(**kwargs):
        captured["tailoring_plan"] = deepcopy(
            kwargs["tailoring_plan"]
        )
        return _rewrite_result()

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        fake_rewrite,
    )

    original_payload = deepcopy(service.payload)

    generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        tailoring_plan={
            "tailoring_plan": {
                "priorities": [],
                "summary": [],
                "skills": [],
                "experience": [],
                "keywords": [],
                "qualifications": [],
                "warnings": [],
            }
        },
        rag_service=service,
    )

    captured["tailoring_plan"]["tailoring_plan"][
        "rag_optimization"
    ]["skills_to_emphasize"].append("Docker")

    assert service.payload == original_payload


def test_rag_enabled_result_is_exposed_without_changing_final_resume(
    monkeypatch,
):
    service = FakeRAGService(enabled=True)

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert result["rag_optimization"]["skills_to_emphasize"] == [
        "Python"
    ]
    assert result["final_resume"].skills == [
        "Python",
        "SQL",
    ]


def test_rag_service_receives_a_copy_of_jd_analysis(monkeypatch):
    service = FakeRAGService(enabled=True)

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert service.calls
    assert service.calls[0]["required_skills"] == ["Python"]


def test_rag_failure_is_propagated_without_corrupting_pipeline(
    monkeypatch,
):
    class FailingRAGService:
        enabled = True

        def get_phase11_payload(self, jd_analysis):
            raise RuntimeError("RAG retrieval failed")

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )

    with pytest.raises(RuntimeError, match="RAG retrieval failed"):
        generate_optimized_resume(
            resume_text="Original resume",
            resume_data=_resume_data(),
            job_description="Python developer",
            ats_result=_ats_result(),
            rag_service=FailingRAGService(),
        )


def test_rag_service_rejects_invalid_payload(monkeypatch):
    class InvalidRAGService:
        enabled = True

        def get_phase11_payload(self, jd_analysis):
            return None

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )

    with pytest.raises(TypeError):
        generate_optimized_resume(
            resume_text="Original resume",
            resume_data=_resume_data(),
            job_description="Python developer",
            ats_result=_ats_result(),
            rag_service=InvalidRAGService(),
        )


# ---------------------------------------------------------------------------
# Additional Phase 12 integration coverage
# ---------------------------------------------------------------------------


def test_resume_aware_rag_service_receives_resume_data(monkeypatch):
    service = ResumeAwareFakeRAGService(enabled=True)
    resume_data = _resume_data()

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    generate_optimized_resume(
        resume_text="Original resume",
        resume_data=resume_data,
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert len(service.calls) == 1
    assert service.calls[0]["jd_analysis"] == _jd_analysis()
    assert service.calls[0]["resume_data"] == resume_data


def test_resume_aware_rag_service_receives_copy_of_resume_data(
    monkeypatch,
):
    service = ResumeAwareFakeRAGService(enabled=True)
    resume_data = _resume_data()

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    generate_optimized_resume(
        resume_text="Original resume",
        resume_data=resume_data,
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    service.calls[0]["resume_data"]["skills"].append("InjectedSkill")

    assert resume_data["skills"] == ["Python", "SQL"]


def test_rag_payload_reaches_rewrite_resume(monkeypatch):
    service = FakeRAGService(enabled=True)
    captured = {}

    def fake_rewrite(**kwargs):
        captured["tailoring_plan"] = deepcopy(
            kwargs["tailoring_plan"]
        )
        return _rewrite_result()

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        fake_rewrite,
    )

    generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    tailoring_plan = captured["tailoring_plan"]

    assert "rag_optimization" in tailoring_plan["tailoring_plan"]
    assert (
        tailoring_plan["tailoring_plan"]["rag_optimization"]
        == service.payload
    )


def test_rag_payload_preserves_phase9_tailoring_fields(monkeypatch):
    service = FakeRAGService(enabled=True)
    captured = {}

    custom_plan = {
        "tailoring_plan": {
            "priorities": [
                {"section": "summary", "priority": 1},
            ],
            "summary": [
                "Keep the existing Python experience."
            ],
            "skills": [
                "Emphasize Python and SQL."
            ],
            "experience": [
                "Highlight existing application development."
            ],
            "keywords": [
                "python",
                "sql",
            ],
            "qualifications": [
                "Use only verified qualifications."
            ],
            "warnings": [
                "Do not fabricate experience.",
            ],
            "custom_phase9_field": {
                "preserve": True,
            },
        }
    }

    def fake_rewrite(**kwargs):
        captured["tailoring_plan"] = deepcopy(
            kwargs["tailoring_plan"]
        )
        return _rewrite_result()

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        fake_rewrite,
    )

    generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        tailoring_plan=custom_plan,
        rag_service=service,
    )

    nested = captured["tailoring_plan"]["tailoring_plan"]

    assert nested["priorities"] == custom_plan["tailoring_plan"][
        "priorities"
    ]
    assert nested["summary"] == custom_plan["tailoring_plan"][
        "summary"
    ]
    assert nested["skills"] == custom_plan["tailoring_plan"][
        "skills"
    ]
    assert nested["experience"] == custom_plan["tailoring_plan"][
        "experience"
    ]
    assert nested["keywords"] == custom_plan["tailoring_plan"][
        "keywords"
    ]
    assert nested["qualifications"] == custom_plan[
        "tailoring_plan"
    ]["qualifications"]
    assert nested["warnings"] == custom_plan["tailoring_plan"][
        "warnings"
    ]
    assert nested["custom_phase9_field"] == {
        "preserve": True
    }
    assert nested["rag_optimization"] == service.payload


def test_rag_payload_is_separate_from_candidate_resume_content(
    monkeypatch,
):
    service = FakeRAGService(
        enabled=True,
        payload={
            **_rag_payload(),
            "experience_to_emphasize": [
                "General Python development guidance"
            ],
        },
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert result["rag_optimization"] is not None
    assert (
        result["rag_optimization"]["experience_to_emphasize"]
        == ["General Python development guidance"]
    )

    final_experience = result["final_resume"].experience

    assert all(
        "General Python development guidance"
        not in str(item)
        for item in final_experience
    )


def test_rag_grounding_information_is_not_inserted_as_resume_claim(
    monkeypatch,
):
    service = FakeRAGService(
        enabled=True,
        payload={
            **_rag_payload(),
            "grounding": [
                {
                    "evidence_id": "knowledge:evidence:123",
                    "source_chunk_ids": ["knowledge:chunk:456"],
                    "text": (
                        "Candidates may benefit from distributed "
                        "systems terminology."
                    ),
                }
            ],
        },
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert result["rag_optimization"]["grounding"]
    assert all(
        "distributed systems terminology"
        not in str(value)
        for value in result["final_resume"].__dict__.values()
    )


def test_rag_metadata_is_preserved(monkeypatch):
    service = FakeRAGService(
        enabled=True,
        payload={
            **_rag_payload(),
            "metadata": {
                "rag_enabled": True,
                "retrieval_count": 3,
                "source": "knowledge_base",
                "version": "phase12",
            },
        },
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert result["rag_optimization"]["metadata"] == {
        "rag_enabled": True,
        "retrieval_count": 3,
        "source": "knowledge_base",
        "version": "phase12",
    }


def test_rag_result_is_defensively_copied_from_pipeline_result(
    monkeypatch,
):
    service = FakeRAGService(enabled=True)

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    result["rag_optimization"]["metadata"]["mutated"] = True
    result["rag_optimization"]["skills_to_emphasize"].append(
        "Docker"
    )

    assert "mutated" not in service.payload["metadata"]
    assert service.payload["skills_to_emphasize"] == ["Python"]


def test_rag_optimization_is_exposed_separately_from_tailoring_plan(
    monkeypatch,
):
    service = FakeRAGService(enabled=True)

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert result["rag_optimization"] == service.payload
    assert (
        result["tailoring_plan"]["tailoring_plan"][
            "rag_optimization"
        ]
        == service.payload
    )

    assert (
        result["rag_optimization"]
        is not result["tailoring_plan"]["tailoring_plan"][
            "rag_optimization"
        ]
    )


def test_rag_disabled_keeps_result_contract(monkeypatch):
    service = FakeRAGService(enabled=False)

    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    expected_keys = {
        "final_resume",
        "tailoring_plan",
        "rewrite_result",
        "length_control",
        "validation",
        "rag_optimization",
    }

    assert expected_keys.issubset(result.keys())
    assert result["rag_optimization"] is None


def test_rag_enabled_produces_final_resume_after_integration(
    monkeypatch,
):
    service = FakeRAGService(enabled=True)

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert isinstance(result["final_resume"], FinalResume)
    assert result["final_resume"].summary
    assert result["final_resume"].skills
    assert result["final_resume"].experience


def test_rag_service_backward_compatible_without_resume_data(
    monkeypatch,
):
    """Ensure legacy RAG services remain supported by the pipeline."""

    service = FakeRAGService(enabled=True)

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert service.calls == [_jd_analysis()]
    assert result["rag_optimization"] == service.payload


def test_rag_payload_with_empty_optional_sections_is_accepted(
    monkeypatch,
):
    service = FakeRAGService(
        enabled=True,
        payload={
            "skills_to_emphasize": [],
            "experience_to_emphasize": [],
            "keywords_to_emphasize": [],
            "emphasis_instructions": [],
            "grounding": [],
            "metadata": {},
        },
    )

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=service,
    )

    assert result["rag_optimization"] == service.payload
    assert isinstance(result["final_resume"], FinalResume)


def test_rag_payload_does_not_mutate_original_tailoring_plan(
    monkeypatch,
):
    service = FakeRAGService(enabled=True)

    original_plan = {
        "tailoring_plan": {
            "priorities": [{"rank": 1}],
            "summary": ["Existing summary"],
            "skills": ["Python"],
            "experience": ["Existing experience"],
            "keywords": ["python"],
            "qualifications": [],
            "warnings": [],
        }
    }

    original_copy = deepcopy(original_plan)

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: _jd_analysis(),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        tailoring_plan=original_plan,
        rag_service=service,
    )

    assert original_plan == original_copy
    assert (
        result["tailoring_plan"]["tailoring_plan"][
            "rag_optimization"
        ]
        == service.payload
    )


def test_rag_service_mutation_does_not_change_pipeline_jd_analysis(
    monkeypatch,
):
    class MutatingRAGService:
        enabled = True

        def get_phase11_payload(self, jd_analysis):
            jd_analysis["required_skills"].append("MutatedSkill")
            return deepcopy(_rag_payload())

    analysis = _jd_analysis()

    monkeypatch.setattr(
        "app.resume_generation_pipeline.analyze_job_description",
        lambda job_description: deepcopy(analysis),
    )
    monkeypatch.setattr(
        "app.resume_generation_pipeline.rewrite_resume",
        lambda **kwargs: _rewrite_result(),
    )

    result = generate_optimized_resume(
        resume_text="Original resume",
        resume_data=_resume_data(),
        job_description="Python developer",
        ats_result=_ats_result(),
        rag_service=MutatingRAGService(),
    )

    assert result["rag_optimization"] == _rag_payload()