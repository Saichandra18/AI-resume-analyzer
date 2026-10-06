from app.rag.models import GroundedEvidence, RetrievedChunk
from app.rag.optimization.signals import (
    OptimizationSignal,
    OptimizationSignalSet,
)
from app.rag.recommendations.claim_detector import UnsupportedClaimDetector


class SignalGroundingValidator:
    """Validate that optimization signals remain grounded in RAG evidence."""

    VALID_SIGNAL_TYPES = {
        "skill",
        "experience",
        "keyword",
        "emphasis",
    }

    def __init__(self, claim_detector=None):
        self.claim_detector = claim_detector or UnsupportedClaimDetector()

    def validate(self, signals, evidence, retrieved_chunks):
        """Validate optimization signals against their source evidence.

        Returns True when every signal is grounded.

        Raises:
            TypeError: for invalid input types.
            ValueError: when a signal is not safely grounded.
        """

        signal_list = self._normalize_signals(signals)

        if not isinstance(evidence, (list, tuple)):
            raise TypeError("evidence must be a list or tuple")

        if not isinstance(retrieved_chunks, (list, tuple)):
            raise TypeError("retrieved_chunks must be a list or tuple")

        for item in evidence:
            if not isinstance(item, GroundedEvidence):
                raise TypeError(
                    "evidence must contain GroundedEvidence instances"
                )

        for chunk in retrieved_chunks:
            if not isinstance(chunk, RetrievedChunk):
                raise TypeError(
                    "retrieved_chunks must contain RetrievedChunk instances"
                )

        evidence_by_id = {
            item.evidence_id: item
            for item in evidence
        }

        retrieved_by_id = {
            chunk.chunk_id: chunk
            for chunk in retrieved_chunks
        }

        for signal in signal_list:
            self._validate_signal(
                signal=signal,
                evidence_by_id=evidence_by_id,
                retrieved_by_id=retrieved_by_id,
            )

        return True

    def validate_set(self, signal_set, evidence, retrieved_chunks):
        """Validate an OptimizationSignalSet."""

        if not isinstance(signal_set, OptimizationSignalSet):
            raise TypeError(
                "signal_set must be an OptimizationSignalSet"
            )

        return self.validate(
            signal_set.signals,
            evidence,
            retrieved_chunks,
        )

    def _normalize_signals(self, signals):
        if isinstance(signals, OptimizationSignalSet):
            return list(signals.signals)

        if not isinstance(signals, (list, tuple)):
            raise TypeError(
                "signals must be a list, tuple, or OptimizationSignalSet"
            )

        normalized = []

        for signal in signals:
            if not isinstance(signal, OptimizationSignal):
                raise TypeError(
                    "signals must contain OptimizationSignal instances"
                )

            normalized.append(signal)

        return normalized

    def _validate_signal(
        self,
        signal,
        evidence_by_id,
        retrieved_by_id,
    ):
        if signal.signal_type not in self.VALID_SIGNAL_TYPES:
            raise ValueError(
                f"Invalid optimization signal type: "
                f"{signal.signal_type}"
            )

        value = self._normalize_text(signal.value)

        if not value:
            raise ValueError(
                "Optimization signal value cannot be empty"
            )

        if not signal.evidence_id:
            raise ValueError(
                "Optimization signal must reference evidence"
            )

        evidence = evidence_by_id.get(signal.evidence_id)

        if evidence is None:
            raise ValueError(
                f"Unknown evidence reference: {signal.evidence_id}"
            )

        source_chunk_ids = list(signal.source_chunk_ids or [])

        if not source_chunk_ids:
            raise ValueError(
                "Optimization signal must reference source chunks"
            )

        missing_chunks = [
            chunk_id
            for chunk_id in source_chunk_ids
            if chunk_id not in retrieved_by_id
        ]

        if missing_chunks:
            raise ValueError(
                "Optimization signal references unknown source chunks: "
                + ", ".join(str(item) for item in missing_chunks)
            )

        evidence_chunk_ids = set(evidence.source_chunk_ids or [])
        signal_chunk_ids = set(source_chunk_ids)

        if not signal_chunk_ids.issubset(evidence_chunk_ids):
            raise ValueError(
                "Optimization signal source chunks do not match "
                "its evidence"
            )

        if not signal_chunk_ids.intersection(evidence_chunk_ids):
            raise ValueError(
                "Optimization signal has no traceable evidence chunk"
            )

        self._validate_confidence(signal, evidence)

        evidence_text = self._normalize_text(evidence.text)
        evidence_claim = self._normalize_text(evidence.claim)

        if not evidence_text:
            raise ValueError(
                "Referenced evidence must contain text"
            )

        if not evidence_claim:
            raise ValueError(
                "Referenced evidence must contain a claim"
            )

        if evidence_claim not in evidence_text:
            raise ValueError(
                "Referenced evidence claim is not contained in "
                "the evidence text"
            )

        self._validate_claim(
            value=value,
            evidence_text=evidence_text,
            evidence_claim=evidence_claim,
        )

        self._validate_metadata_traceability(signal, evidence)

        return True

    @staticmethod
    def _validate_confidence(signal, evidence):
        if not isinstance(signal.confidence, (int, float)):
            raise TypeError(
                "Optimization signal confidence must be numeric"
            )

        if not 0.0 <= signal.confidence <= 1.0:
            raise ValueError(
                "Optimization signal confidence must be between "
                "0.0 and 1.0"
            )

        if not isinstance(evidence.confidence, (int, float)):
            raise TypeError(
                "Evidence confidence must be numeric"
            )

        if not 0.0 <= evidence.confidence <= 1.0:
            raise ValueError(
                "Evidence confidence must be between 0.0 and 1.0"
            )

        if signal.confidence != evidence.confidence:
            raise ValueError(
                "Optimization signal confidence must match "
                "referenced evidence confidence"
            )

    def _validate_claim(self, value, evidence_text, evidence_claim):
        """Ensure the signal does not introduce unsupported terminology."""

        recommendation = {
            "message": value,
            "claim": value,
            "value": value,
        }

        unsupported = self.claim_detector.detect(
            recommendation,
            evidence_text,
        )

        if unsupported:
            raise ValueError(
                "Optimization signal contains unsupported terms: "
                + ", ".join(unsupported)
            )

        normalized_value = value.lower()

        if (
            normalized_value not in evidence_text.lower()
            and normalized_value not in evidence_claim.lower()
        ):
            raise ValueError(
                "Optimization signal value is not supported by "
                "referenced evidence"
            )

    @staticmethod
    def _validate_metadata_traceability(signal, evidence):
        signal_metadata = signal.metadata or {}
        evidence_metadata = evidence.metadata or {}

        signal_document_id = signal_metadata.get("document_id")
        evidence_document_id = evidence_metadata.get("document_id")

        if (
            signal_document_id is not None
            and evidence_document_id is not None
            and signal_document_id != evidence_document_id
        ):
            raise ValueError(
                "Optimization signal document metadata does not "
                "match referenced evidence"
            )

    @staticmethod
    def _normalize_text(value):
        if value is None:
            return ""

        return " ".join(str(value).split())