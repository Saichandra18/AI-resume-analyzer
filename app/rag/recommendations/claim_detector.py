"""Detect recommendation claims that are unsupported by evidence."""

import re


class UnsupportedClaimDetector:
    """Detect unsupported claims in grounded recommendations."""

    def detect(self, recommendation, evidence):
        """Return unsupported claim terms found in a recommendation."""

        if not isinstance(recommendation, dict):
            raise TypeError(
                "recommendation must be a dictionary."
            )

        if not isinstance(evidence, str):
            raise TypeError(
                "evidence must be a string."
            )

        message = recommendation.get("message")

        if not isinstance(message, str):
            raise TypeError(
                "recommendation message must be a string."
            )

        normalized_message = self._normalize(message)
        normalized_evidence = self._normalize(evidence)

        if not normalized_message:
            return []

        if not normalized_evidence:
            return self._extract_terms(
                normalized_message
            )

        message_terms = self._extract_terms(
            normalized_message
        )

        evidence_terms = set(
            self._extract_terms(
                normalized_evidence
            )
        )

        return [
            term
            for term in message_terms
            if term not in evidence_terms
        ]

    @staticmethod
    def _normalize(text):
        """Normalize text for deterministic comparison."""

        text = text.lower()

        text = re.sub(
            r"[^a-z0-9+#.\- ]+",
            " ",
            text,
        )

        return " ".join(text.split())

    @staticmethod
    def _extract_terms(text):
        """Extract meaningful terms from normalized text."""

        stop_words = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "consider",
            "emphasize",
            "emphasizing",
            "experience",
            "for",
            "from",
            "in",
            "is",
            "of",
            "on",
            "supported",
            "the",
            "this",
            "to",
            "with",
        }

        terms = []

        for token in text.split():
            token = token.strip(".-")

            if not token:
                continue

            if token in stop_words:
                continue

            if len(token) < 2:
                continue

            terms.append(token)

        return terms