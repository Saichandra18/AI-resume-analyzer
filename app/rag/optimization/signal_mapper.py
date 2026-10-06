"""Map safe RAG recommendations to optimization signals."""

from copy import deepcopy

from app.rag.optimization.signals import (
    OptimizationSignal,
    OptimizationSignalSet,
)


class RecommendationSignalMapper:
    """Convert safe recommendations into grounded signals."""

    CATEGORY_TO_SIGNAL_TYPE = {
        "skill": "skill",
        "experience": "experience",
        "keyword": "keyword",
        "emphasis": "emphasis",
    }

    def map(
        self,
        recommendations,
        metadata=None,
    ):
        """Map recommendations into an optimization signal set."""

        if not isinstance(
            recommendations,
            (list, tuple),
        ):
            raise TypeError(
                "recommendations must be a list or tuple."
            )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary or None."
            )

        signals = []

        for recommendation in recommendations:
            if not isinstance(
                recommendation,
                dict,
            ):
                raise TypeError(
                    "recommendations must contain "
                    "dictionaries."
                )

            mapped = self._map_recommendation(
                recommendation
            )

            if mapped is None:
                continue

            if isinstance(
                mapped,
                OptimizationSignal,
            ):
                signals.append(mapped)
            else:
                signals.extend(mapped)

        return OptimizationSignalSet(
            signals=signals,
            metadata=deepcopy(
                metadata or {}
            ),
        )

    def _map_recommendation(
        self,
        recommendation,
    ):
        """Map one recommendation to one or more signals."""

        category = recommendation.get(
            "category"
        )

        value = recommendation.get(
            "value"
        )

        if category is None or value is None:
            return None

        signal_type = (
            self.CATEGORY_TO_SIGNAL_TYPE.get(
                category
            )
        )

        if signal_type is None:
            return None

        evidence_id = recommendation.get(
            "evidence_id"
        )

        source_chunk_ids = recommendation.get(
            "source_chunk_ids",
            [],
        )

        confidence = recommendation.get(
            "confidence",
            0.0,
        )

        metadata = deepcopy(
            recommendation.get(
                "metadata",
                {},
            )
        )

        values = (
            value
            if isinstance(
                value,
                (list, tuple),
            )
            else [value]
        )

        if not values:
            return None

        signals = []

        for item in values:
            normalized = " ".join(
                str(item).split()
            )

            if not normalized:
                continue

            signals.append(
                OptimizationSignal(
                    signal_type=signal_type,
                    value=normalized,
                    evidence_id=evidence_id,
                    source_chunk_ids=source_chunk_ids,
                    confidence=confidence,
                    metadata=metadata,
                )
            )

        if not signals:
            return None

        if len(signals) == 1:
            return signals[0]

        return signals

    @staticmethod
    def flatten(signal_set):
        """Return a flat list of signals from a signal set."""

        if not isinstance(
            signal_set,
            OptimizationSignalSet,
        ):
            raise TypeError(
                "signal_set must be an "
                "OptimizationSignalSet."
            )

        return [
            signal
            for signal in signal_set.signals
            if isinstance(
                signal,
                OptimizationSignal,
            )
        ]