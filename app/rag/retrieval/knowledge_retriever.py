"""Retrieval of general optimization guidance from the RAG knowledge base."""

from app.rag.models import RetrievalQuery


class KnowledgeRetriever:
    """Retrieve relevant knowledge-base guidance for a job description."""

    def __init__(self, retrieval_service, top_k=5):
        if retrieval_service is None:
            raise ValueError("retrieval_service is required.")

        if not hasattr(retrieval_service, "retrieve"):
            raise TypeError(
                "retrieval_service must provide a retrieve method."
            )

        if not isinstance(top_k, int) or isinstance(top_k, bool):
            raise TypeError("top_k must be an integer.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        self.retrieval_service = retrieval_service
        self.top_k = top_k

    def retrieve(self, jd_analysis):
        """Retrieve knowledge guidance relevant to a JD analysis."""

        if not isinstance(jd_analysis, dict):
            raise TypeError(
                "jd_analysis must be a dictionary."
            )

        query_text = self._build_query(jd_analysis)

        if not query_text:
            return []

        query = RetrievalQuery(
            query=query_text,
            top_k=self.top_k,
        )

        results = self.retrieval_service.retrieve(query)

        if not isinstance(results, (list, tuple)):
            raise TypeError(
                "retrieval_service must return a list or tuple."
            )

        return list(results)

    @staticmethod
    def _build_query(jd_analysis):
        """Build a deterministic knowledge-retrieval query."""

        parts = []

        required_skills = jd_analysis.get(
            "required_skills",
            [],
        )

        if isinstance(required_skills, (list, tuple, set)):
            parts.extend(
                str(skill)
                for skill in required_skills
                if str(skill).strip()
            )
        elif required_skills:
            parts.append(str(required_skills))

        keywords = jd_analysis.get(
            "keywords",
            [],
        )

        if isinstance(keywords, (list, tuple, set)):
            parts.extend(
                str(keyword)
                for keyword in keywords
                if str(keyword).strip()
            )
        elif keywords:
            parts.append(str(keywords))

        experience = jd_analysis.get(
            "experience",
            [],
        )

        if isinstance(experience, (list, tuple, set)):
            parts.extend(
                str(item)
                for item in experience
                if str(item).strip()
            )
        elif experience:
            parts.append(str(experience))

        query_parts = [
            "resume optimization",
            "ATS",
            "job description alignment",
        ]

        query_parts.extend(parts)

        return " ".join(
            part.strip()
            for part in query_parts
            if str(part).strip()
        )