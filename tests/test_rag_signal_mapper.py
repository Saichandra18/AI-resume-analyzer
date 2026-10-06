import pytest

from app.rag.optimization.signal_mapper import (
    RecommendationSignalMapper,
)
from app.rag.optimization.signals import (
    OptimizationSignal,
    OptimizationSignalSet,
)


def make_recommendation(
    category="skill",
    value="Python",
    evidence_id="evidence:0",
):
    return {
        "type": "emphasis",
        "message": "Emphasize supported experience.",
        "evidence_id": evidence_id,
        "source_chunk_ids": [
            "resume:experience:0"
        ],
        "confidence": 0.9,
        "category": category,
        "value": value,
        "metadata": {
            "source": "rag"
        },
    }


def test_maps_skill_recommendation():
    result = RecommendationSignalMapper().map(
        [make_recommendation()]
    )

    assert len(result.signals) == 1
    assert result.signals[0].signal_type == "skill"
    assert result.signals[0].value == "Python"


def test_maps_experience_recommendation():
    result = RecommendationSignalMapper().map(
        [
            make_recommendation(
                category="experience",
                value="REST API development",
            )
        ]
    )

    assert result.signals[0].signal_type == (
        "experience"
    )
    assert result.signals[0].value == (
        "REST API development"
    )


def test_maps_keyword_recommendation():
    result = RecommendationSignalMapper().map(
        [
            make_recommendation(
                category="keyword",
                value="Flask",
            )
        ]
    )

    assert result.signals[0].signal_type == (
        "keyword"
    )


def test_maps_emphasis_recommendation():
    result = RecommendationSignalMapper().map(
        [
            make_recommendation(
                category="emphasis",
                value="API development",
            )
        ]
    )

    assert result.signals[0].signal_type == (
        "emphasis"
    )


def test_preserves_evidence_id():
    result = RecommendationSignalMapper().map(
        [
            make_recommendation(
                evidence_id="evidence:7"
            )
        ]
    )

    assert result.signals[0].evidence_id == (
        "evidence:7"
    )


def test_preserves_source_chunks():
    result = RecommendationSignalMapper().map(
        [make_recommendation()]
    )

    assert result.signals[0].source_chunk_ids == [
        "resume:experience:0"
    ]


def test_preserves_confidence():
    recommendation = make_recommendation()
    recommendation["confidence"] = 0.75

    result = RecommendationSignalMapper().map(
        [recommendation]
    )

    assert result.signals[0].confidence == 0.75


def test_preserves_metadata():
    result = RecommendationSignalMapper().map(
        [make_recommendation()]
    )

    assert result.signals[0].metadata == {
        "source": "rag"
    }


def test_maps_multiple_values():
    result = RecommendationSignalMapper().map(
        [
            make_recommendation(
                category="skill",
                value=[
                    "Python",
                    "Flask",
                    "REST API",
                ],
            )
        ]
    )

    assert [
        signal.value
        for signal in result.signals
    ] == [
        "Python",
        "Flask",
        "REST API",
    ]


def test_skips_uncategorized_recommendation():
    recommendation = make_recommendation()
    recommendation.pop("category")

    result = RecommendationSignalMapper().map(
        [recommendation]
    )

    assert result.signals == []


def test_skips_recommendation_without_value():
    recommendation = make_recommendation()
    recommendation.pop("value")

    result = RecommendationSignalMapper().map(
        [recommendation]
    )

    assert result.signals == []


def test_skips_unknown_category():
    result = RecommendationSignalMapper().map(
        [
            make_recommendation(
                category="unknown",
                value="Python",
            )
        ]
    )

    assert result.signals == []


def test_skips_empty_value():
    result = RecommendationSignalMapper().map(
        [
            make_recommendation(
                value="   "
            )
        ]
    )

    assert result.signals == []


def test_preserves_metadata():
    result = RecommendationSignalMapper().map(
        [],
        metadata={
            "source": "rag",
            "count": 0,
        },
    )

    assert result.metadata == {
        "source": "rag",
        "count": 0,
    }


def test_maps_multiple_recommendations_in_order():
    recommendations = [
        make_recommendation(
            category="skill",
            value="Python",
        ),
        make_recommendation(
            category="skill",
            value="Flask",
        ),
        make_recommendation(
            category="experience",
            value="API development",
        ),
    ]

    result = RecommendationSignalMapper().map(
        recommendations
    )

    assert [
        signal.value
        for signal in result.signals
    ] == [
        "Python",
        "Flask",
        "API development",
    ]


def test_empty_recommendations():
    result = RecommendationSignalMapper().map(
        []
    )

    assert isinstance(
        result,
        OptimizationSignalSet,
    )
    assert result.signals == []


def test_rejects_invalid_recommendations():
    with pytest.raises(TypeError):
        RecommendationSignalMapper().map(
            "invalid"
        )


def test_rejects_invalid_recommendation_item():
    with pytest.raises(TypeError):
        RecommendationSignalMapper().map(
            ["invalid"]
        )


def test_rejects_invalid_metadata():
    with pytest.raises(TypeError):
        RecommendationSignalMapper().map(
            [],
            metadata="invalid",
        )


def test_flatten_returns_signals():
    signal = OptimizationSignal(
        signal_type="skill",
        value="Python",
    )

    signal_set = OptimizationSignalSet(
        signals=[signal]
    )

    result = RecommendationSignalMapper().flatten(
        signal_set
    )

    assert result == [signal]


def test_flatten_rejects_invalid_input():
    with pytest.raises(TypeError):
        RecommendationSignalMapper().flatten(
            []
        )