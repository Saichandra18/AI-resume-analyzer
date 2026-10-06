"""Safety result models for RAG recommendations."""

from copy import deepcopy


class RecommendationSafetyResult:
    """Represent the safety evaluation of a recommendation."""

    def __init__(
        self,
        safe,
        recommendation=None,
        reason=None,
        unsupported_terms=None,
        evidence_id=None,
        metadata=None,
    ):
        if not isinstance(safe, bool):
            raise TypeError("safe must be a boolean.")

        if recommendation is not None and not isinstance(
            recommendation,
            dict,
        ):
            raise TypeError(
                "recommendation must be a dictionary or None."
            )

        if reason is not None and not isinstance(
            reason,
            str,
        ):
            raise TypeError(
                "reason must be a string or None."
            )

        if unsupported_terms is not None and not isinstance(
            unsupported_terms,
            (list, tuple),
        ):
            raise TypeError(
                "unsupported_terms must be a list or tuple."
            )

        if evidence_id is not None and not isinstance(
            evidence_id,
            str,
        ):
            raise TypeError(
                "evidence_id must be a string or None."
            )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary or None."
            )

        self.safe = safe
        self.recommendation = deepcopy(
            recommendation
        )
        self.reason = reason
        self.unsupported_terms = list(
            unsupported_terms or []
        )
        self.evidence_id = evidence_id
        self.metadata = deepcopy(
            metadata or {}
        )

    def to_dict(self):
        """Serialize the safety result."""

        return {
            "safe": self.safe,
            "recommendation": deepcopy(
                self.recommendation
            ),
            "reason": self.reason,
            "unsupported_terms": list(
                self.unsupported_terms
            ),
            "evidence_id": self.evidence_id,
            "metadata": deepcopy(
                self.metadata
            ),
        }

    @classmethod
    def from_dict(cls, data):
        """Create a safety result from a dictionary."""

        if not isinstance(data, dict):
            raise TypeError(
                "data must be a dictionary."
            )

        return cls(
            safe=data.get("safe"),
            recommendation=data.get(
                "recommendation"
            ),
            reason=data.get("reason"),
            unsupported_terms=data.get(
                "unsupported_terms"
            ),
            evidence_id=data.get(
                "evidence_id"
            ),
            metadata=data.get(
                "metadata"
            ),
        )