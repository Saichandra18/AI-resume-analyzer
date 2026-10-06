from copy import deepcopy

from app.rag.optimization.signals import (
    OptimizationSignal,
    OptimizationSignalSet,
)


class Phase11OptimizationAdapter:
    """Adapt grounded RAG optimization signals for Phase 11."""

    SIGNAL_FIELD_MAP = {
        "skill": "skills_to_emphasize",
        "experience": "experience_to_emphasize",
        "keyword": "keywords_to_emphasize",
        "emphasis": "emphasis_instructions",
    }

    def adapt(self, signal_set):
        """Convert validated RAG signals into a Phase 11 payload."""

        if not isinstance(signal_set, OptimizationSignalSet):
            raise TypeError(
                "signal_set must be an OptimizationSignalSet"
            )

        payload = {
            "skills_to_emphasize": [],
            "experience_to_emphasize": [],
            "keywords_to_emphasize": [],
            "emphasis_instructions": [],
            "grounding": [],
            "metadata": deepcopy(signal_set.metadata),
        }

        for signal in signal_set.signals:
            if not isinstance(signal, OptimizationSignal):
                raise TypeError(
                    "signal_set must contain OptimizationSignal "
                    "instances"
                )

            field_name = self.SIGNAL_FIELD_MAP.get(signal.signal_type)

            if field_name is None:
                continue

            payload[field_name].append(signal.value)

            payload["grounding"].append(
                {
                    "signal_type": signal.signal_type,
                    "value": signal.value,
                    "evidence_id": signal.evidence_id,
                    "source_chunk_ids": list(
                        signal.source_chunk_ids
                    ),
                    "confidence": signal.confidence,
                    "metadata": deepcopy(signal.metadata),
                }
            )

        return payload