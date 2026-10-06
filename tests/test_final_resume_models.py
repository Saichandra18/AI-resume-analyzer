from app.final_resume_models import (
    DEFAULT_SECTION_ORDER,
    FinalResume,
    FinalResumeMetadata,
    build_final_resume,
)


def test_final_resume_has_expected_defaults():
    resume = FinalResume()

    assert resume.personal_info == {}
    assert resume.summary == ""
    assert resume.skills == []
    assert resume.experience == []
    assert resume.projects == []
    assert resume.education == []
    assert resume.certifications == []
    assert resume.section_order == DEFAULT_SECTION_ORDER


def test_final_resume_metadata_defaults():
    metadata = FinalResumeMetadata()

    assert metadata.target_pages == 1
    assert metadata.optimization_enabled is True
    assert metadata.target_job_title is None


def test_build_final_resume():
    resume = build_final_resume(
        personal_info={
            "name": "John Doe",
            "email": "john@example.com",
        },
        summary="Machine learning engineer.",
        skills=["Python", "SQL"],
        experience=[
            {
                "job_title": "ML Engineer",
                "company": "Example",
            }
        ],
    )

    assert resume.personal_info["name"] == "John Doe"
    assert resume.summary == (
        "Machine learning engineer."
    )
    assert resume.skills == ["Python", "SQL"]
    assert len(resume.experience) == 1


def test_final_resume_serialization_round_trip():
    resume = FinalResume(
        personal_info={
            "name": "John Doe",
            "email": "john@example.com",
        },
        summary="Experienced engineer.",
        skills=["Python", "SQL"],
        experience=[
            {"job_title": "Engineer"}
        ],
        projects=[
            {"name": "Resume Analyzer"}
        ],
        education=[
            {"degree": "B.Tech"}
        ],
        certifications=[
            {"name": "AWS Certified"}
        ],
        metadata={
            "target_pages": 2,
            "optimization_enabled": True,
            "target_job_title": "ML Engineer",
        },
    )

    serialized = resume.to_dict()
    restored = FinalResume.from_dict(
        serialized
    )

    assert restored.to_dict() == serialized


def test_final_resume_rejects_duplicate_sections():
    try:
        FinalResume(
            section_order=[
                "summary",
                "skills",
                "skills",
            ]
        )
    except ValueError as exc:
        assert "duplicates" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_final_resume_rejects_unknown_sections():
    try:
        FinalResume(
            section_order=[
                "summary",
                "unknown_section",
            ]
        )
    except ValueError as exc:
        assert "Unknown resume sections" in str(
            exc
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_metadata_rejects_invalid_target_pages():
    for value in [0, -1, "1", None]:
        try:
            FinalResumeMetadata(
                target_pages=value
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Expected ValueError"
            )


def test_final_resume_does_not_mutate_input_data():
    personal_info = {
        "name": "John Doe"
    }

    skills = ["Python"]

    resume = FinalResume(
        personal_info=personal_info,
        skills=skills,
    )

    resume.personal_info["name"] = "Changed"
    resume.skills.append("SQL")

    assert personal_info == {
        "name": "John Doe"
    }
    assert skills == ["Python"]