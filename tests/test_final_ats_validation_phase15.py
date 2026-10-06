from pathlib import Path

from app.final_ats_validation import (
    ATSValidationResult,
    BeforeAfterATSResult,
    compare_ats_results,
    validate_rendered_resume_file,
    validate_rendered_resume_text,
)
from app.final_ats_validation import (
    ATSDeltaSummary,
    ATSSafetyGateResult,
    ATSValidationResult,
    BeforeAfterATSResult,
    compare_ats_results,
    run_ats_safety_gate,
    summarize_ats_delta,
    validate_rendered_resume_file,
    validate_rendered_resume_text,
)


def make_ats_result(
    score=80,
    skills_matched=None,
    skills_missing=None,
    experience_score=80,
    qualification_score=80,
    keyword_score=80,
    keywords_matched=None,
    keywords_missing=None,
):
    return {
        "ats_score": score,
        "skills": {
            "matched": skills_matched or [],
            "missing": skills_missing or [],
        },
        "experience": {
            "required_years": 3,
            "candidate_years": 4,
            "meets_requirement": True,
        },
        "qualifications": {
            "matched": ["Bachelor's degree"],
            "missing": [],
        },
        "keywords": {
            "matched": keywords_matched or [],
            "missing": keywords_missing or [],
        },
        "component_scores": {
            "skills": (
                100
                if not skills_missing
                else 50
            ),
            "experience": experience_score,
            "qualifications": qualification_score,
            "keywords": keyword_score,
        },
        "weights": {
            "skills": 50.0,
            "experience": 20.0,
            "qualifications": 15.0,
            "keywords": 15.0,
        },
    }


def test_compare_returns_expected_result_type():
    before = make_ats_result(
        score=70,
        skills_matched=["Python"],
        skills_missing=["SQL"],
        keywords_matched=["Python"],
        keywords_missing=["SQL"],
    )

    after = make_ats_result(
        score=85,
        skills_matched=["Python", "SQL"],
        skills_missing=[],
        keywords_matched=["Python", "SQL"],
        keywords_missing=[],
    )

    result = compare_ats_results(
        before,
        after,
    )

    assert isinstance(
        result,
        BeforeAfterATSResult,
    )


def test_score_delta_is_calculated():
    before = make_ats_result(score=70)
    after = make_ats_result(score=85)

    result = compare_ats_results(
        before,
        after,
    )

    assert result.before_score == 70
    assert result.after_score == 85
    assert result.score_delta == 15


def test_component_deltas_are_calculated():
    before = make_ats_result(
        experience_score=60,
        qualification_score=70,
        keyword_score=50,
    )

    after = make_ats_result(
        experience_score=80,
        qualification_score=90,
        keyword_score=75,
    )

    result = compare_ats_results(
        before,
        after,
    )

    assert result.experience_delta == 20
    assert result.qualifications_delta == 20
    assert result.keywords_delta == 25


def test_newly_matched_skills_are_detected():
    before = make_ats_result(
        skills_matched=["Python"],
        skills_missing=["SQL", "Pandas"],
    )

    after = make_ats_result(
        skills_matched=[
            "Python",
            "SQL",
        ],
        skills_missing=["Pandas"],
    )

    result = compare_ats_results(
        before,
        after,
    )

    assert result.newly_matched_skills == (
        "SQL",
    )


def test_remaining_missing_skills_are_detected():
    before = make_ats_result(
        skills_missing=[
            "SQL",
            "Pandas",
        ],
    )

    after = make_ats_result(
        skills_missing=[
            "Pandas",
        ],
    )

    result = compare_ats_results(
        before,
        after,
    )

    assert result.remaining_missing_skills == (
        "Pandas",
    )


def test_lost_skills_are_detected():
    before = make_ats_result(
        skills_matched=[
            "Python",
            "SQL",
        ],
    )

    after = make_ats_result(
        skills_matched=[
            "Python",
        ],
        skills_missing=["SQL"],
    )

    result = compare_ats_results(
        before,
        after,
    )

    assert result.lost_skills == (
        "SQL",
    )


def test_newly_matched_keywords_are_detected():
    before = make_ats_result(
        keywords_matched=["Python"],
        keywords_missing=["SQL", "ETL"],
    )

    after = make_ats_result(
        keywords_matched=[
            "Python",
            "SQL",
        ],
        keywords_missing=["ETL"],
    )

    result = compare_ats_results(
        before,
        after,
    )

    assert result.newly_matched_keywords == (
        "SQL",
    )


def test_remaining_missing_keywords_are_detected():
    before = make_ats_result(
        keywords_missing=[
            "SQL",
            "ETL",
        ],
    )

    after = make_ats_result(
        keywords_missing=[
            "ETL",
        ],
    )

    result = compare_ats_results(
        before,
        after,
    )

    assert result.remaining_missing_keywords == (
        "ETL",
    )


def test_lost_keywords_are_detected():
    before = make_ats_result(
        keywords_matched=[
            "Python",
            "SQL",
        ],
    )

    after = make_ats_result(
        keywords_matched=[
            "Python",
        ],
        keywords_missing=["SQL"],
    )

    result = compare_ats_results(
        before,
        after,
    )

    assert result.lost_keywords == (
        "SQL",
    )


def test_score_regression_is_false_when_score_improves():
    before = make_ats_result(score=70)
    after = make_ats_result(score=85)

    result = compare_ats_results(
        before,
        after,
    )

    assert result.score_regression is False


def test_score_regression_is_true_when_score_drops():
    before = make_ats_result(score=85)
    after = make_ats_result(score=70)

    result = compare_ats_results(
        before,
        after,
    )

    assert result.score_regression is True


def test_equal_scores_are_not_regression():
    before = make_ats_result(score=80)
    after = make_ats_result(score=80)

    result = compare_ats_results(
        before,
        after,
    )

    assert result.score_delta == 0
    assert result.score_regression is False


def test_rendered_text_validation():
    ats_result = make_ats_result(
        score=85,
        skills_matched=["Python"],
        skills_missing=["SQL"],
        keywords_matched=["Python"],
        keywords_missing=["SQL"],
    )

    result = validate_rendered_resume_text(
        "John Doe\nPython Developer\nSkills: Python",
        ats_result,
    )

    assert isinstance(
        result,
        ATSValidationResult,
    )

    assert result.valid is True
    assert result.score == 85
    assert result.skills_score == 50
    assert result.missing_skills == ("SQL",)
    assert result.missing_keywords == ("SQL",)
    assert result.warnings == ()


def test_empty_rendered_text_is_invalid():
    ats_result = make_ats_result()

    result = validate_rendered_resume_text(
        "",
        ats_result,
    )

    assert result.valid is False
    assert (
        "Rendered resume contains no extractable text."
        in result.warnings
    )


def test_missing_file_is_invalid(tmp_path):
    file_path = tmp_path / "missing.txt"

    result = validate_rendered_resume_file(
        file_path,
        make_ats_result(),
    )

    assert result.valid is False
    assert "does not exist" in result.warnings[0]


def test_plain_text_file_validation(tmp_path):
    file_path = tmp_path / "resume.txt"

    file_path.write_text(
        "John Doe\nPython Developer\nSkills: Python SQL",
        encoding="utf-8",
    )

    result = validate_rendered_resume_file(
        file_path,
        make_ats_result(
            score=90,
            skills_matched=[
                "Python",
                "SQL",
            ],
        ),
    )

    assert result.valid is True
    assert result.score == 90


def test_path_object_is_supported(tmp_path):
    file_path = Path(tmp_path) / "resume.txt"

    file_path.write_text(
        "Resume content",
        encoding="utf-8",
    )

    result = validate_rendered_resume_file(
        file_path,
        make_ats_result(score=75),
    )

    assert result.valid is True
    assert result.score == 75


def test_unsupported_file_format_is_invalid(tmp_path):
    file_path = tmp_path / "resume.xyz"

    file_path.write_text(
        "Resume content",
        encoding="utf-8",
    )

    result = validate_rendered_resume_file(
        file_path,
        make_ats_result(),
    )

    assert result.valid is False
    assert "Unsupported resume format" in result.warnings[0]


def test_docx_extraction_is_delegated(tmp_path):
    file_path = tmp_path / "resume.docx"

    file_path.write_bytes(b"fake docx")

    result = validate_rendered_resume_file(
        file_path,
        make_ats_result(),
    )

    assert result.valid is False
    assert "DOCX/PDF extraction" in result.warnings[0]


def test_pdf_extraction_is_delegated(tmp_path):
    file_path = tmp_path / "resume.pdf"

    file_path.write_bytes(b"fake pdf")

    result = validate_rendered_resume_file(
        file_path,
        make_ats_result(),
    )

    assert result.valid is False
    assert "DOCX/PDF extraction" in result.warnings[0]

def test_summarize_ats_delta_returns_expected_type():
    before = make_ats_result(
        score=70,
        skills_matched=["Python"],
        skills_missing=["SQL"],
    )

    after = make_ats_result(
        score=85,
        skills_matched=[
            "Python",
            "SQL",
        ],
        skills_missing=[],
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    summary = summarize_ats_delta(
        comparison
    )

    assert isinstance(
        summary,
        ATSDeltaSummary,
    )


def test_score_improvement_percent_is_calculated():
    before = make_ats_result(
        score=50,
    )

    after = make_ats_result(
        score=75,
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    summary = summarize_ats_delta(
        comparison
    )

    assert summary.score_delta == 25
    assert (
        summary.score_improvement_percent
        == 50.0
    )


def test_improved_components_are_detected():
    before = make_ats_result(
        score=70,
        experience_score=60,
        qualification_score=70,
        keyword_score=50,
    )

    after = make_ats_result(
        score=85,
        experience_score=80,
        qualification_score=90,
        keyword_score=75,
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    summary = summarize_ats_delta(
        comparison
    )

    assert "experience" in (
        summary.improved_components
    )

    assert "qualifications" in (
        summary.improved_components
    )

    assert "keywords" in (
        summary.improved_components
    )


def test_unchanged_components_are_detected():
    before = make_ats_result(
        score=80,
        experience_score=80,
        qualification_score=80,
        keyword_score=80,
    )

    after = make_ats_result(
        score=85,
        experience_score=80,
        qualification_score=80,
        keyword_score=80,
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    summary = summarize_ats_delta(
        comparison
    )

    assert "experience" in (
        summary.unchanged_components
    )

    assert "qualifications" in (
        summary.unchanged_components
    )

    assert "keywords" in (
        summary.unchanged_components
    )


def test_regressed_components_are_detected():
    before = make_ats_result(
        score=80,
        experience_score=90,
        qualification_score=90,
        keyword_score=90,
    )

    after = make_ats_result(
        score=75,
        experience_score=70,
        qualification_score=90,
        keyword_score=80,
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    summary = summarize_ats_delta(
        comparison
    )

    assert "experience" in (
        summary.regressed_components
    )

    assert "keywords" in (
        summary.regressed_components
    )

    assert "qualifications" not in (
        summary.regressed_components
    )


def test_overall_status_is_improved():
    before = make_ats_result(score=70)
    after = make_ats_result(score=85)

    comparison = compare_ats_results(
        before,
        after,
    )

    summary = summarize_ats_delta(
        comparison
    )

    assert summary.overall_status == "improved"


def test_overall_status_is_regressed():
    before = make_ats_result(score=85)
    after = make_ats_result(score=70)

    comparison = compare_ats_results(
        before,
        after,
    )

    summary = summarize_ats_delta(
        comparison
    )

    assert summary.overall_status == "regressed"


def test_overall_status_is_unchanged():
    before = make_ats_result(score=80)
    after = make_ats_result(score=80)

    comparison = compare_ats_results(
        before,
        after,
    )

    summary = summarize_ats_delta(
        comparison
    )

    assert summary.overall_status == "unchanged"


def test_zero_before_score_does_not_divide_by_zero():
    before = make_ats_result(score=0)
    after = make_ats_result(score=50)

    comparison = compare_ats_results(
        before,
        after,
    )

    summary = summarize_ats_delta(
        comparison
    )

    assert summary.score_delta == 50
    assert (
        summary.score_improvement_percent
        == 0.0
    )

def test_safety_gate_returns_expected_type():
    before = make_ats_result(
        score=70,
        skills_matched=["Python"],
        skills_missing=["SQL"],
        keywords_matched=["Python"],
        keywords_missing=["SQL"],
    )

    after = make_ats_result(
        score=85,
        skills_matched=[
            "Python",
            "SQL",
        ],
        skills_missing=[],
        keywords_matched=[
            "Python",
            "SQL",
        ],
        keywords_missing=[],
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    result = run_ats_safety_gate(
        comparison,
        "Python SQL resume content",
    )

    assert isinstance(
        result,
        ATSSafetyGateResult,
    )


def test_safety_gate_passes_for_safe_optimization():
    before = make_ats_result(
        score=70,
        skills_matched=["Python"],
        skills_missing=["SQL"],
        keywords_matched=["Python"],
        keywords_missing=["SQL"],
    )

    after = make_ats_result(
        score=85,
        skills_matched=[
            "Python",
            "SQL",
        ],
        skills_missing=[],
        keywords_matched=[
            "Python",
            "SQL",
        ],
        keywords_missing=[],
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    result = run_ats_safety_gate(
        comparison,
        "Python SQL resume content",
    )

    assert result.passed is True
    assert result.score_valid is True
    assert result.no_score_regression is True
    assert result.no_lost_skills is True
    assert result.no_lost_keywords is True
    assert result.component_scores_valid is True
    assert result.content_extractable is True
    assert result.failures == ()


def test_safety_gate_fails_on_score_regression():
    before = make_ats_result(
        score=85,
        skills_matched=["Python"],
        keywords_matched=["Python"],
    )

    after = make_ats_result(
        score=70,
        skills_matched=["Python"],
        keywords_matched=["Python"],
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    result = run_ats_safety_gate(
        comparison,
        "Resume content",
    )

    assert result.passed is False
    assert result.no_score_regression is False
    assert any(
        "score is lower" in failure
        for failure in result.failures
    )


def test_safety_gate_fails_on_lost_skills():
    before = make_ats_result(
        score=80,
        skills_matched=[
            "Python",
            "SQL",
        ],
    )

    after = make_ats_result(
        score=80,
        skills_matched=["Python"],
        skills_missing=["SQL"],
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    result = run_ats_safety_gate(
        comparison,
        "Resume content",
    )

    assert result.passed is False
    assert result.no_lost_skills is False


def test_safety_gate_fails_on_lost_keywords():
    before = make_ats_result(
        score=80,
        keywords_matched=[
            "Python",
            "SQL",
        ],
    )

    after = make_ats_result(
        score=80,
        keywords_matched=["Python"],
        keywords_missing=["SQL"],
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    result = run_ats_safety_gate(
        comparison,
        "Resume content",
    )

    assert result.passed is False
    assert result.no_lost_keywords is False


def test_safety_gate_fails_on_empty_content():
    before = make_ats_result(
        score=70,
    )

    after = make_ats_result(
        score=80,
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    result = run_ats_safety_gate(
        comparison,
        "",
    )

    assert result.passed is False
    assert result.content_extractable is False


def test_safety_gate_detects_invalid_score():
    before = make_ats_result(
        score=70,
    )

    after = make_ats_result(
        score=101,
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    result = run_ats_safety_gate(
        comparison,
        "Resume content",
    )

    assert result.passed is False
    assert result.score_valid is False


def test_safety_gate_detects_invalid_component_score():
    before = make_ats_result(
        score=70,
    )

    after = make_ats_result(
        score=80,
        experience_score=101,
    )

    comparison = compare_ats_results(
        before,
        after,
    )

    result = run_ats_safety_gate(
        comparison,
        "Resume content",
    )

    assert result.passed is False
    assert result.component_scores_valid is False