import pytest

from app.ai.providers import LLMProvider
from app.resume_generation_pipeline import generate_optimized_resume


class FakeProvider(LLMProvider):
    def __init__(self, result="Generated result"):
        self.result = result
        self.calls = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.result


def test_application_generation_uses_provider_factory(
    monkeypatch,
):
    fake_provider = FakeProvider(
        "AI-generated resume content"
    )

    monkeypatch.setattr(
        "app.resume_rewriter.create_llm_provider",
        lambda: fake_provider,
    )

    result = generate_optimized_resume(
        resume_text="John Doe\nPython Developer",
        resume_data={
            "personal_info": {
                "name": "John Doe",
            },
            "skills": ["Python", "SQL"],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
        },
        job_description=(
            "Looking for a Python Developer with SQL experience."
        ),
    )

    assert result is not None
    assert fake_provider.calls


def test_application_does_not_require_openai_client(
    monkeypatch,
):
    fake_provider = FakeProvider(
        "Provider-generated content"
    )

    monkeypatch.setattr(
        "app.resume_rewriter.create_llm_provider",
        lambda: fake_provider,
    )

    result = generate_optimized_resume(
        resume_text="Python Developer",
        resume_data={
            "personal_info": {
                "name": "John Doe",
            },
            "skills": ["Python", "SQL"],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
        },
        job_description="Python developer with SQL.",
    )

    assert result is not None
    assert fake_provider.calls


def test_application_accepts_substitutable_provider(
    monkeypatch,
):
    provider = FakeProvider(
        "Alternative provider output"
    )

    monkeypatch.setattr(
        "app.resume_rewriter.create_llm_provider",
        lambda: provider,
    )

    result = generate_optimized_resume(
        resume_text="Software Developer",
        resume_data={
            "personal_info": {
                "name": "John Doe",
            },
            "skills": ["Python"],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
        },
        job_description="Software Developer with Python.",
    )

    assert result is not None
    assert len(provider.calls) >= 1


def test_provider_failure_propagates_through_application(
    monkeypatch,
):
    class FailingProvider(LLMProvider):
        def generate(self, prompt: str) -> str:
            raise RuntimeError("Provider unavailable")

    monkeypatch.setattr(
        "app.resume_rewriter.create_llm_provider",
        lambda: FailingProvider(),
    )

    with pytest.raises(
        RuntimeError,
        match="Provider unavailable",
    ):
        generate_optimized_resume(
            resume_text="Software Developer",
            resume_data={
                "personal_info": {
                    "name": "John Doe",
                },
                "skills": ["Python"],
                "experience": [],
                "projects": [],
                "education": [],
                "certifications": [],
            },
            job_description="Python Developer",
        )
