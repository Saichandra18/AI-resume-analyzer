"""Build grounded recommendations from RAG evidence."""

from copy import deepcopy

from app.rag.models import GroundedEvidence


class RecommendationBuilder:
    """Build deterministic resume recommendations from grounded evidence."""

    def build(
        self,
        evidence,
        requirements=None,
    ):
        """Build recommendations supported by grounded evidence."""

        if not isinstance(
            evidence,
            (list, tuple),
        ):
            raise TypeError(
                "evidence must be a list or tuple."
            )

        for item in evidence:
            if not isinstance(
                item,
                GroundedEvidence,
            ):
                raise TypeError(
                    "evidence must contain "
                    "GroundedEvidence objects."
                )

        if requirements is not None and not isinstance(
            requirements,
            (list, tuple),
        ):
            raise TypeError(
                "requirements must be a list or tuple."
            )

        normalized_requirements = (
            self._normalize_requirements(
                requirements or []
            )
        )

        recommendations = []

        for item in evidence:
            recommendation = self._build_recommendation(
                item,
                normalized_requirements,
            )

            if recommendation is not None:
                recommendations.append(
                    recommendation
                )

        return recommendations

    @staticmethod
    def _normalize_requirements(requirements):
        """Normalize requirement values."""

        normalized = []

        for requirement in requirements:
            if requirement is None:
                continue

            if isinstance(requirement, dict):
                text = requirement.get(
                    "text",
                    requirement.get(
                        "requirement",
                        "",
                    ),
                )
            else:
                text = requirement

            text = " ".join(
                str(text).split()
            )

            if text:
                normalized.append(text)

        return normalized

    @staticmethod
    def _build_recommendation(
        evidence,
        requirements,
    ):
        """Build one grounded recommendation."""

        evidence_text = evidence.text.strip()

        if not evidence_text:
            return None

        matched_requirement = None

        evidence_lower = evidence_text.lower()

        for requirement in requirements:
            if requirement.lower() in evidence_lower:
                matched_requirement = requirement
                break

        if matched_requirement:
            message = (
                "Emphasize evidence relevant to "
                f"'{matched_requirement}': "
                f"{evidence_text}"
            )
        else:
            message = (
                "Consider emphasizing this supported "
                f"experience: {evidence_text}"
            )

        return {
            "type": "emphasis",
            "message": message,
            "evidence_id": evidence.evidence_id,
            "source_chunk_ids": list(
                evidence.source_chunk_ids
            ),
            "confidence": evidence.confidence,
            "metadata": deepcopy(
                evidence.metadata
            ),
        }