from app.final_resume_models import FinalResume
from app.final_resume_validator import (
    is_valid_final_resume,
    validate_final_resume,
)


def make_valid_resume():
    return FinalResume(
        personal_info={
            "name": "John Doe",
            "email": "john@example.com",
        },
        summary="Machine learning engineer.",
        skills=[
            "Python",
            "SQL",
        ],
        experience=[
            {
                "job_title": "ML Engineer",
                "company": "Example",
            }
        ],
        projects=[
            {
                "name": "Resume Analyzer",
            }
        ],
        education=[
            {
                "degree": "B.Tech",
            }
        ],
    )


def test_valid_resume_passes():
    result = validate_final_resume(
        make_valid_resume()
    )

    assert result["valid"] is True
    assert result["errors"] == []


def test_valid_resume_helper_returns_true():
    assert is_valid_final_resume(
        make_valid_resume()
    ) is True


def test_missing_name_fails_validation():
    resume = make_valid_resume()
    resume.personal_info.pop("name")

    result = validate_final_resume(resume)

    assert result["valid"] is False
    assert any(
        "name" in error
        for error in result["errors"]
    )


def test_invalid_personal_info_type_fails():
    resume = make_valid_resume()
    resume.personal_info = "John Doe"

    result = validate_final_resume(resume)

    assert result["valid"] is False
    assert any(
        "personal_info" in error
        for error in result["errors"]
    )


def test_empty_summary_is_warning_by_default():
    resume = make_valid_resume()
    resume.summary = ""

    result = validate_final_resume(resume)

    assert result["valid"] is True
    assert any(
        "summary" in warning.lower()
        for warning in result["warnings"]
    )


def test_summary_can_be_required():
    resume = make_valid_resume()
    resume.summary = ""

    result = validate_final_resume(
        resume,
        require_summary=True,
    )

    assert result["valid"] is False
    assert any(
        "summary" in error.lower()
        for error in result["errors"]
    )


def test_invalid_section_order_fails():
    resume = make_valid_resume()
    resume.section_order = [
        "summary",
        "unknown",
    ]

    result = validate_final_resume(resume)

    assert result["valid"] is False
    assert any(
        "unknown" in error.lower()
        for error in result["errors"]
    )


def test_duplicate_sections_fail():
    resume = make_valid_resume()
    resume.section_order = [
        "summary",
        "skills",
        "skills",
    ]

    result = validate_final_resume(resume)

    assert result["valid"] is False
    assert any(
        "duplicate" in error.lower()
        for error in result["errors"]
    )


def test_non_list_skills_fail():
    resume = make_valid_resume()
    resume.skills = "Python, SQL"

    result = validate_final_resume(resume)

    assert result["valid"] is False
    assert any(
        "skills" in error.lower()
        for error in result["errors"]
    )


def test_non_list_experience_fails():
    resume = make_valid_resume()
    resume.experience = {
        "job_title": "Engineer"
    }

    result = validate_final_resume(resume)

    assert result["valid"] is False
    assert any(
        "experience" in error.lower()
        for error in result["errors"]
    )


def test_empty_experience_item_fails():
    resume = make_valid_resume()
    resume.experience = [
        {
            "job_title": "Engineer"
        },
        None,
    ]

    result = validate_final_resume(resume)

    assert result["valid"] is False
    assert any(
        "experience[1]" in error
        for error in result["errors"]
    )


def test_duplicate_experience_entries_generate_warning():
    resume = make_valid_resume()

    duplicate = {
        "job_title": "ML Engineer",
        "company": "Example",
    }

    resume.experience = [
        duplicate,
        duplicate.copy(),
    ]

    result = validate_final_resume(resume)

    assert result["valid"] is True
    assert any(
        "duplicate" in warning.lower()
        for warning in result["warnings"]
    )


def test_duplicate_projects_generate_warning():
    resume = make_valid_resume()

    project = {
        "name": "Resume Analyzer"
    }

    resume.projects = [
        project,
        project.copy(),
    ]

    result = validate_final_resume(resume)

    assert result["valid"] is True
    assert any(
        "projects" in warning.lower()
        for warning in result["warnings"]
    )


def test_invalid_metadata_fails():
    resume = make_valid_resume()
    resume.metadata.target_pages = 0

    result = validate_final_resume(resume)

    assert result["valid"] is False
    assert any(
        "target_pages" in error
        for error in result["errors"]
    )


def test_non_final_resume_object_fails():
    result = validate_final_resume(
        {
            "personal_info": {
                "name": "John Doe"
            }
        }
    )

    assert result["valid"] is False
    assert result["errors"]


def test_empty_resume_fails_due_to_missing_name():
    resume = FinalResume()

    result = validate_final_resume(resume)

    assert result["valid"] is False


def test_valid_resume_with_empty_optional_sections_passes():
    resume = FinalResume(
        personal_info={
            "name": "John Doe"
        },
        summary="Engineer.",
    )

    result = validate_final_resume(resume)

    assert result["valid"] is True


def test_validation_result_has_expected_shape():
    result = validate_final_resume(
        make_valid_resume()
    )

    assert set(result.keys()) == {
        "valid",
        "errors",
        "warnings",
    }

    assert isinstance(
        result["valid"],
        bool,
    )

    assert isinstance(
        result["errors"],
        list,
    )

    assert isinstance(
        result["warnings"],
        list,
    )