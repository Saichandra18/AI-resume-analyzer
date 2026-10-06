import pytest

from app.rag.models import GroundedEvidence
from app.rag.recommendations.builder import RecommendationBuilder
from app.rag.recommendations.validator import (
    RecommendationGroundingValidator,
)


def make_evidence(
    evidence_id="evidence:0",
    text="Python Flask REST API experience",
    claim="Python Flask REST API experience",
    confidence=0.9,
):
    return GroundedEvidence(
        evidence_id=evidence_id,
        text=text,
        source_chunk_ids=[
            "resume:experience:0"
        ],
        claim=claim,
        confidence=confidence,
        metadata={
            "section": "experience"
        },
    )


def make_recommendation(
    evidence=None,
    **kwargs,
):
    evidence = evidence or make_evidence()

    recommendation = RecommendationBuilder().build(
        [evidence]
    )[0]

    recommendation.update(kwargs)

    return recommendation


def test_valid_recommendation_passes():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence
    )

    validator = RecommendationGroundingValidator()

    assert validator.validate(
        [recommendation],
        [evidence],
    ) is True


def test_empty_recommendations_pass():
    validator = RecommendationGroundingValidator()

    assert validator.validate(
        [],
        [make_evidence()],
    ) is True


def test_rejects_invalid_recommendations():
    validator = RecommendationGroundingValidator()

    with pytest.raises(TypeError):
        validator.validate(
            "invalid",
            [make_evidence()],
        )


def test_rejects_invalid_evidence():
    validator = RecommendationGroundingValidator()

    with pytest.raises(TypeError):
        validator.validate(
            [],
            ["invalid"],
        )


def test_rejects_unknown_evidence_id():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        evidence_id="evidence:999",
    )

    validator = RecommendationGroundingValidator()

    with pytest.raises(ValueError):
        validator.validate(
            [recommendation],
            [evidence],
        )


def test_rejects_missing_source_chunks():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        source_chunk_ids=[],
    )

    validator = RecommendationGroundingValidator()

    with pytest.raises(ValueError):
        validator.validate(
            [recommendation],
            [evidence],
        )


def test_rejects_unknown_source_chunk():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        source_chunk_ids=[
            "resume:experience:999"
        ],
    )

    validator = RecommendationGroundingValidator()

    with pytest.raises(ValueError):
        validator.validate(
            [recommendation],
            [evidence],
        )


def test_rejects_empty_message():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        message="",
    )

    validator = RecommendationGroundingValidator()

    with pytest.raises(ValueError):
        validator.validate(
            [recommendation],
            [evidence],
        )


def test_rejects_confidence_mismatch():
    evidence = make_evidence(
        confidence=0.9
    )

    recommendation = make_recommendation(
        evidence=evidence,
        confidence=0.5,
    )

    validator = RecommendationGroundingValidator()

    with pytest.raises(ValueError):
        validator.validate(
            [recommendation],
            [evidence],
        )


def test_rejects_confidence_above_one():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        confidence=1.5,
    )

    validator = RecommendationGroundingValidator()

    with pytest.raises(ValueError):
        validator.validate(
            [recommendation],
            [evidence],
        )


def test_rejects_unsupported_recommendation_content():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        message=(
            "Emphasize Kubernetes production "
            "deployment experience."
        ),
    )

    validator = RecommendationGroundingValidator()

    with pytest.raises(ValueError):
        validator.validate(
            [recommendation],
            [evidence],
        )


def test_preserves_grounding_for_multiple_recommendations():
    evidence_one = make_evidence(
        evidence_id="evidence:1",
        text="Python experience",
        claim="Python experience",
    )

    evidence_two = make_evidence(
        evidence_id="evidence:2",
        text="Flask experience",
        claim="Flask experience",
    )

    builder = RecommendationBuilder()

    recommendations = builder.build(
        [
            evidence_one,
            evidence_two,
        ]
    )

    validator = RecommendationGroundingValidator()

    assert validator.validate(
        recommendations,
        [
            evidence_one,
            evidence_two,
        ],
    ) is True

def test_rejects_unsupported_claim_through_detector():
    evidence = make_evidence(
        text="Python Flask experience",
        claim="Python Flask experience",
    )

    recommendation = make_recommendation(
        evidence=evidence,
        message=(
            "Emphasize Python Kubernetes experience."
        ),
    )

    validator = RecommendationGroundingValidator()

    with pytest.raises(
        ValueError,
        match="unsupported claim terms",
    ):
        validator.validate(
            [recommendation],
            [evidence],
        )


def test_accepts_supported_claim_through_detector():
    evidence = make_evidence(
        text="Python Flask experience",
        claim="Python Flask experience",
    )

    recommendation = make_recommendation(
        evidence=evidence,
        message=(
            "Emphasize Python Flask experience."
        ),
    )

    validator = RecommendationGroundingValidator()

    assert validator.validate(
        [recommendation],
        [evidence],
    ) is True


def test_supports_custom_claim_detector():
    class DummyClaimDetector:
        def detect(
            self,
            recommendation,
            evidence,
        ):
            return []

    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
    )

    validator = RecommendationGroundingValidator(
        claim_detector=DummyClaimDetector()
    )

    assert validator.validate(
        [recommendation],
        [evidence],
    ) is True