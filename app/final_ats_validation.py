"""
Phase 15 - Final ATS Validation

Provides final ATS validation and before/after comparison for the
production ATS result structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ATSValidationResult:
    """Result of validating a final rendered resume."""

    valid: bool
    score: float = 0.0
    skills_score: float = 0.0
    experience_score: float = 0.0
    qualifications_score: float = 0.0
    keywords_score: float = 0.0

    missing_skills: tuple[str, ...] = field(
        default_factory=tuple
    )
    missing_keywords: tuple[str, ...] = field(
        default_factory=tuple
    )

    warnings: tuple[str, ...] = field(
        default_factory=tuple
    )


@dataclass(frozen=True)
class BeforeAfterATSResult:
    """Comparison between original and optimized ATS evaluations."""

    before_score: float
    after_score: float
    score_delta: float

    before_skills_score: float
    after_skills_score: float
    skills_delta: float

    before_experience_score: float
    after_experience_score: float
    experience_delta: float

    before_qualifications_score: float
    after_qualifications_score: float
    qualifications_delta: float

    before_keywords_score: float
    after_keywords_score: float
    keywords_delta: float

    newly_matched_skills: tuple[str, ...] = field(
        default_factory=tuple
    )
    lost_skills: tuple[str, ...] = field(
        default_factory=tuple
    )
    remaining_missing_skills: tuple[str, ...] = field(
        default_factory=tuple
    )

    newly_matched_keywords: tuple[str, ...] = field(
        default_factory=tuple
    )
    lost_keywords: tuple[str, ...] = field(
        default_factory=tuple
    )
    remaining_missing_keywords: tuple[str, ...] = field(
        default_factory=tuple
    )

    score_regression: bool = False

@dataclass(frozen=True)
class ATSDeltaSummary:
    """High-level summary of ATS score changes."""

    before_score: float
    after_score: float
    score_delta: float
    score_improvement_percent: float

    improved_components: tuple[str, ...] = field(
        default_factory=tuple
    )
    unchanged_components: tuple[str, ...] = field(
        default_factory=tuple
    )
    regressed_components: tuple[str, ...] = field(
        default_factory=tuple
    )

    overall_status: str = "unchanged"
@dataclass(frozen=True)
class ATSSafetyGateResult:
    """Final safety-gate result for an optimized resume."""

    passed: bool

    score_valid: bool
    no_score_regression: bool
    no_lost_skills: bool
    no_lost_keywords: bool
    component_scores_valid: bool
    content_extractable: bool

    failures: tuple[str, ...] = field(
        default_factory=tuple
    )

# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def _number(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _sequence(value: Any) -> tuple[str, ...]:
    """Normalize a sequence-like value into a tuple of strings."""

    if value is None:
        return ()

    if isinstance(value, str):
        value = value.strip()
        return (value,) if value else ()

    if isinstance(value, Sequence):
        return tuple(
            str(item).strip()
            for item in value
            if str(item).strip()
        )

    return ()


def _get(
    result: Any,
    name: str,
    default: Any = None,
) -> Any:
    """Read a field from either a mapping or an object."""

    if isinstance(result, Mapping):
        return result.get(name, default)

    return getattr(result, name, default)


def _component(
    result: Any,
    component: str,
) -> float:
    """
    Read a component score from the production ATS result.

    Production structure:

        result["component_scores"]["skills"]
    """

    component_scores = _get(
        result,
        "component_scores",
        {},
    )

    if isinstance(component_scores, Mapping):
        return _number(
            component_scores.get(component),
            0.0,
        )

    return 0.0


def _matched(
    result: Any,
    component: str,
) -> tuple[str, ...]:
    """Return matched values for an ATS component."""

    component_result = _get(
        result,
        component,
        {},
    )

    values = _get(
        component_result,
        "matched",
        (),
    )

    return _sequence(values)


def _missing(
    result: Any,
    component: str,
) -> tuple[str, ...]:
    """Return missing values for an ATS component."""

    component_result = _get(
        result,
        component,
        {},
    )

    values = _get(
        component_result,
        "missing",
        (),
    )

    return _sequence(values)


# ---------------------------------------------------------------------------
# ATS comparison
# ---------------------------------------------------------------------------

def compare_ats_results(
    before: Any,
    after: Any,
) -> BeforeAfterATSResult:
    """
    Compare two production ATS results.

    The function expects the structure returned by:

        app.ats_analyzer.analyze_resume_against_job()

    Both dictionary and object-based inputs are supported.
    """

    before_score = _number(
        _get(before, "ats_score", 0.0)
    )

    after_score = _number(
        _get(after, "ats_score", 0.0)
    )

    # Component scores
    before_skills = _component(
        before,
        "skills",
    )
    after_skills = _component(
        after,
        "skills",
    )

    before_experience = _component(
        before,
        "experience",
    )
    after_experience = _component(
        after,
        "experience",
    )

    before_qualifications = _component(
        before,
        "qualifications",
    )
    after_qualifications = _component(
        after,
        "qualifications",
    )

    before_keywords = _component(
        before,
        "keywords",
    )
    after_keywords = _component(
        after,
        "keywords",
    )

    # Skills
    before_matched_skills = set(
        _matched(before, "skills")
    )
    after_matched_skills = set(
        _matched(after, "skills")
    )

    before_missing_skills = set(
        _missing(before, "skills")
    )
    after_missing_skills = set(
        _missing(after, "skills")
    )

    newly_matched_skills = tuple(
        sorted(
            after_matched_skills
            - before_matched_skills
        )
    )

    lost_skills = tuple(
        sorted(
            before_matched_skills
            - after_matched_skills
        )
    )

    remaining_missing_skills = tuple(
        sorted(after_missing_skills)
    )

    # Keywords
    before_matched_keywords = set(
        _matched(before, "keywords")
    )
    after_matched_keywords = set(
        _matched(after, "keywords")
    )

    before_missing_keywords = set(
        _missing(before, "keywords")
    )
    after_missing_keywords = set(
        _missing(after, "keywords")
    )

    newly_matched_keywords = tuple(
        sorted(
            after_matched_keywords
            - before_matched_keywords
        )
    )

    lost_keywords = tuple(
        sorted(
            before_matched_keywords
            - after_matched_keywords
        )
    )

    remaining_missing_keywords = tuple(
        sorted(after_missing_keywords)
    )

    return BeforeAfterATSResult(
        before_score=before_score,
        after_score=after_score,
        score_delta=after_score - before_score,
        before_skills_score=before_skills,
        after_skills_score=after_skills,
        skills_delta=after_skills - before_skills,
        before_experience_score=before_experience,
        after_experience_score=after_experience,
        experience_delta=(
            after_experience
            - before_experience
        ),
        before_qualifications_score=before_qualifications,
        after_qualifications_score=after_qualifications,
        qualifications_delta=(
            after_qualifications
            - before_qualifications
        ),
        before_keywords_score=before_keywords,
        after_keywords_score=after_keywords,
        keywords_delta=(
            after_keywords
            - before_keywords
        ),
        newly_matched_skills=newly_matched_skills,
        lost_skills=lost_skills,
        remaining_missing_skills=(
            remaining_missing_skills
        ),
        newly_matched_keywords=(
            newly_matched_keywords
        ),
        lost_keywords=lost_keywords,
        remaining_missing_keywords=(
            remaining_missing_keywords
        ),
        score_regression=(
            after_score < before_score
        ),
    )


# ---------------------------------------------------------------------------
# Rendered resume validation
# ---------------------------------------------------------------------------
def summarize_ats_delta(
    comparison: BeforeAfterATSResult,
) -> ATSDeltaSummary:
    """
    Create a high-level summary from a before/after ATS comparison.

    The percentage improvement is calculated relative to the original
    ATS score. When the original score is zero, percentage improvement
    is reported as zero to avoid division by zero.
    """

    before_score = comparison.before_score
    after_score = comparison.after_score
    score_delta = comparison.score_delta

    if before_score == 0:
        score_improvement_percent = 0.0
    else:
        score_improvement_percent = (
            score_delta / before_score
        ) * 100

    component_deltas = {
        "skills": comparison.skills_delta,
        "experience": comparison.experience_delta,
        "qualifications": comparison.qualifications_delta,
        "keywords": comparison.keywords_delta,
    }

    improved_components = tuple(
        sorted(
            component
            for component, delta in component_deltas.items()
            if delta > 0
        )
    )

    unchanged_components = tuple(
        sorted(
            component
            for component, delta in component_deltas.items()
            if delta == 0
        )
    )

    regressed_components = tuple(
        sorted(
            component
            for component, delta in component_deltas.items()
            if delta < 0
        )
    )

    if score_delta > 0:
        overall_status = "improved"
    elif score_delta < 0:
        overall_status = "regressed"
    else:
        overall_status = "unchanged"

    return ATSDeltaSummary(
        before_score=before_score,
        after_score=after_score,
        score_delta=score_delta,
        score_improvement_percent=(
            round(
                score_improvement_percent,
                2,
            )
        ),
        improved_components=(
            improved_components
        ),
        unchanged_components=(
            unchanged_components
        ),
        regressed_components=(
            regressed_components
        ),
        overall_status=overall_status,
    )
def run_ats_safety_gate(
    comparison: BeforeAfterATSResult,
    resume_text: str,
) -> ATSSafetyGateResult:
    """
    Run the final logical ATS safety gate.

    The gate does not re-render documents or replace the existing
    Phase 14 rendering safety tests. It validates the final ATS
    optimization result before it is considered successful.
    """

    failures: list[str] = []

    # ---------------------------------------------------------------
    # Score validity
    # ---------------------------------------------------------------

    score_values = (
        comparison.before_score,
        comparison.after_score,
    )

    score_valid = all(
        0 <= score <= 100
        for score in score_values
    )

    if not score_valid:
        failures.append(
            "ATS score is outside the valid 0-100 range."
        )

    # ---------------------------------------------------------------
    # Regression protection
    # ---------------------------------------------------------------

    no_score_regression = (
        not comparison.score_regression
    )

    if not no_score_regression:
        failures.append(
            "Optimized resume ATS score is lower "
            "than the original score."
        )

    # ---------------------------------------------------------------
    # Skill preservation
    # ---------------------------------------------------------------

    no_lost_skills = (
        len(comparison.lost_skills) == 0
    )

    if not no_lost_skills:
        failures.append(
            "Optimized resume lost previously matched "
            "skills."
        )

    # ---------------------------------------------------------------
    # Keyword preservation
    # ---------------------------------------------------------------

    no_lost_keywords = (
        len(comparison.lost_keywords) == 0
    )

    if not no_lost_keywords:
        failures.append(
            "Optimized resume lost previously matched "
            "keywords."
        )

    # ---------------------------------------------------------------
    # Component score validation
    # ---------------------------------------------------------------

    component_scores = (
        comparison.after_skills_score,
        comparison.after_experience_score,
        comparison.after_qualifications_score,
        comparison.after_keywords_score,
    )

    component_scores_valid = all(
        0 <= score <= 100
        for score in component_scores
    )

    if not component_scores_valid:
        failures.append(
            "One or more ATS component scores are "
            "outside the valid 0-100 range."
        )

    # ---------------------------------------------------------------
    # Rendered content validation
    # ---------------------------------------------------------------

    content_extractable = bool(
        isinstance(resume_text, str)
        and resume_text.strip()
    )

    if not content_extractable:
        failures.append(
            "Final rendered resume contains no "
            "extractable text."
        )

    # ---------------------------------------------------------------
    # Final result
    # ---------------------------------------------------------------

    passed = not failures

    return ATSSafetyGateResult(
        passed=passed,
        score_valid=score_valid,
        no_score_regression=no_score_regression,
        no_lost_skills=no_lost_skills,
        no_lost_keywords=no_lost_keywords,
        component_scores_valid=component_scores_valid,
        content_extractable=content_extractable,
        failures=tuple(failures),
    )
def validate_rendered_resume_text(
    resume_text: str,
    ats_result: Any,
) -> ATSValidationResult:
    """
    Validate ATS analysis against rendered resume text.

    The existing ATS analyzer remains responsible for scoring.
    This function validates the final rendered artifact and exposes
    the production ATS result in a normalized form.
    """

    warnings: list[str] = []

    if (
        not isinstance(resume_text, str)
        or not resume_text.strip()
    ):
        warnings.append(
            "Rendered resume contains no extractable text."
        )

    return ATSValidationResult(
        valid=bool(
            resume_text
            and resume_text.strip()
        ),
        score=_number(
            _get(ats_result, "ats_score", 0.0)
        ),
        skills_score=_component(
            ats_result,
            "skills",
        ),
        experience_score=_component(
            ats_result,
            "experience",
        ),
        qualifications_score=_component(
            ats_result,
            "qualifications",
        ),
        keywords_score=_component(
            ats_result,
            "keywords",
        ),
        missing_skills=_missing(
            ats_result,
            "skills",
        ),
        missing_keywords=_missing(
            ats_result,
            "keywords",
        ),
        warnings=tuple(warnings),
    )


def validate_rendered_resume_file(
    file_path: str | Path,
    ats_result: Any,
) -> ATSValidationResult:
    """
    Validate a rendered resume file.

    DOCX/PDF extraction remains delegated to the project's existing
    document extraction infrastructure.
    """

    path = Path(file_path)

    if not path.exists():
        return ATSValidationResult(
            valid=False,
            warnings=(
                f"Resume file does not exist: {path}",
            ),
        )

    if path.suffix.lower() in {".txt", ".text"}:
        try:
            text = path.read_text(
                encoding="utf-8"
            )
        except (OSError, UnicodeError) as exc:
            return ATSValidationResult(
                valid=False,
                warnings=(
                    f"Unable to read resume file: {exc}",
                ),
            )

        return validate_rendered_resume_text(
            text,
            ats_result,
        )

    if path.suffix.lower() in {
        ".docx",
        ".pdf",
    }:
        return ATSValidationResult(
            valid=False,
            warnings=(
                "DOCX/PDF extraction must use the "
                "project's existing document extraction "
                "pipeline before validation.",
            ),
        )

    return ATSValidationResult(
        valid=False,
        warnings=(
            f"Unsupported resume format: "
            f"{path.suffix or '<none>'}",
        ),
    )