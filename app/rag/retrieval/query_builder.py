"""Build retrieval queries from job-description analysis."""

from app.rag.models import RetrievalQuery


class JDQueryBuilder:
    """Build deterministic RAG queries from JD analysis data."""

    QUERY_FIELDS = (
        ("required_skills", "Required skills"),
        ("technical_keywords", "Technical keywords"),
        ("responsibilities", "Responsibilities"),
        ("domain_knowledge", "Domain knowledge"),
        ("tools", "Tools and platforms"),
        ("experience_requirements", "Experience requirements"),
    )

    def build(self, jd_analysis):
        """Build retrieval queries from JD analysis."""

        if jd_analysis is None:
            raise ValueError(
                "jd_analysis cannot be None."
            )

        if not isinstance(jd_analysis, dict):
            raise TypeError(
                "jd_analysis must be a dictionary."
            )

        queries = []

        for field_name, label in self.QUERY_FIELDS:
            values = jd_analysis.get(field_name)

            if not values:
                continue

            text = self._normalize_values(values)

            if not text:
                continue

            queries.append(
                RetrievalQuery(
                    query=f"{label}: {text}",
                    top_k=5,
                    filters=None,
                )
            )

        return queries

    @staticmethod
    def _normalize_values(values):
        """Normalize query values into deterministic text."""

        if isinstance(values, str):
            return " ".join(values.split())

        if isinstance(values, (list, tuple, set)):
            normalized = []

            for value in values:
                if value is None:
                    continue

                text = " ".join(
                    str(value).split()
                )

                if text:
                    normalized.append(text)

            return ", ".join(normalized)

        return " ".join(str(values).split())