import app.resume_rewriter as resume_rewriter_module


class FakeProvider:
    def __init__(self):
        self.calls = []

    def generate(self, prompt):
        self.calls.append(prompt)
        return "{}"


def test_rewrite_resume_creates_provider_when_client_is_missing(
    monkeypatch,
):
    provider = FakeProvider()

    monkeypatch.setattr(
        resume_rewriter_module,
        "create_llm_provider",
        lambda: provider,
    )

    result = resume_rewriter_module.rewrite_resume(
        resume_text="Python developer",
        experience=[],
        projects=[],
        skills=[],
        client=None,
    )

    assert result["summary"] == {}
    assert len(provider.calls) == 1


def test_rewrite_resume_reuses_injected_provider(monkeypatch):
    provider = FakeProvider()

    def fail_factory():
        raise AssertionError(
            "Factory should not be called when a provider is injected."
        )

    monkeypatch.setattr(
        resume_rewriter_module,
        "create_llm_provider",
        fail_factory,
    )

    result = resume_rewriter_module.rewrite_resume(
        resume_text="Python developer",
        experience=[],
        projects=[],
        skills=[],
        client=provider,
    )

    assert result["summary"] == {}
    assert len(provider.calls) == 1


def test_rewrite_resume_uses_one_provider_for_all_sections(
    monkeypatch,
):
    provider = FakeProvider()

    monkeypatch.setattr(
        resume_rewriter_module,
        "create_llm_provider",
        lambda: provider,
    )

    resume_rewriter_module.rewrite_resume(
        resume_text="Python developer",
        experience=[
            {"description": "Developed Python application"}
        ],
        projects=[
            {"description": "Built a Python project"}
        ],
        skills=["Python"],
        client=None,
    )

    # Experience + projects + summary + skills.
    assert len(provider.calls) == 4


def test_injected_provider_is_not_replaced(monkeypatch):
    provider = FakeProvider()

    factory_called = False

    def fake_factory():
        nonlocal factory_called
        factory_called = True
        return FakeProvider()

    monkeypatch.setattr(
        resume_rewriter_module,
        "create_llm_provider",
        fake_factory,
    )

    resume_rewriter_module.rewrite_resume(
        resume_text="Python developer",
        experience=[],
        projects=[],
        skills=[],
        client=provider,
    )

    assert factory_called is False