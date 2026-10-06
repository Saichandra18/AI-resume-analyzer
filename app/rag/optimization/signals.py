"""Optimization signal models for RAG-to-Phase-11 integration."""

from copy import deepcopy


class OptimizationSignal:
    """Represent one grounded advisory signal."""

    VALID_TYPES = {
        "skill",
        "experience",
        "keyword",
        "emphasis",
    }

    def __init__(
        self,
        signal_type,
        value,
        evidence_id=None,
        source_chunk_ids=None,
        confidence=0.0,
        metadata=None,
    ):
        if signal_type not in self.VALID_TYPES:
            raise ValueError(
                "Unsupported optimization signal type."
            )

        if not isinstance(value, str):
            raise TypeError(
                "value must be a string."
            )

        if not value.strip():
            raise ValueError(
                "value cannot be empty."
            )

        if evidence_id is not None and not isinstance(
            evidence_id,
            str,
        ):
            raise TypeError(
                "evidence_id must be a string or None."
            )

        if source_chunk_ids is not None and not isinstance(
            source_chunk_ids,
            (list, tuple),
        ):
            raise TypeError(
                "source_chunk_ids must be a list or tuple."
            )

        if not isinstance(
            confidence,
            (int, float),
        ):
            raise TypeError(
                "confidence must be numeric."
            )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0."
            )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary or None."
            )

        self.signal_type = signal_type
        self.value = value.strip()
        self.evidence_id = evidence_id
        self.source_chunk_ids = list(
            source_chunk_ids or []
        )
        self.confidence = confidence
        self.metadata = deepcopy(
            metadata or {}
        )

    def to_dict(self):
        """Serialize the optimization signal."""

        return {
            "signal_type": self.signal_type,
            "value": self.value,
            "evidence_id": self.evidence_id,
            "source_chunk_ids": list(
                self.source_chunk_ids
            ),
            "confidence": self.confidence,
            "metadata": deepcopy(
                self.metadata
            ),
        }

    @classmethod
    def from_dict(cls, data):
        """Create an optimization signal from a dictionary."""

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary."
            )

        return cls(
            signal_type=data.get(
                "signal_type"
            ),
            value=data.get("value"),
            evidence_id=data.get(
                "evidence_id"
            ),
            source_chunk_ids=data.get(
                "source_chunk_ids"
            ),
            confidence=data.get(
                "confidence",
                0.0,
            ),
            metadata=data.get(
                "metadata"
            ),
        )


class OptimizationSignalSet:
    """Collection of grounded optimization signals."""

    def __init__(
        self,
        signals=None,
        metadata=None,
    ):
        if signals is not None and not isinstance(
            signals,
            (list, tuple),
        ):
            raise TypeError(
                "signals must be a list or tuple."
            )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary or None."
            )

        self.signals = []

        for signal in signals or []:
            if isinstance(
                signal,
                OptimizationSignal,
            ):
                self.signals.append(signal)
            elif isinstance(
                signal,
                dict,
            ):
                self.signals.append(
                    OptimizationSignal.from_dict(
                        signal
                    )
                )
            else:
                raise TypeError(
                    "signals must contain "
                    "OptimizationSignal objects "
                    "or dictionaries."
                )

        self.metadata = deepcopy(
            metadata or {}
        )

    def to_dict(self):
        """Serialize the signal set."""

        return {
            "signals": [
                signal.to_dict()
                for signal in self.signals
            ],
            "metadata": deepcopy(
                self.metadata
            ),
        }

    @classmethod
    def from_dict(cls, data):
        """Create a signal set from a dictionary."""

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary."
            )

        return cls(
            signals=data.get("signals"),
            metadata=data.get("metadata"),
        )