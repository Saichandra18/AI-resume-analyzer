"""JD-aware retrieval orchestration."""

from app.rag.optimization.resume_context import (
    ResumeContextBuilder,
)
from app.rag.retrieval.query_builder import JDQueryBuilder


class JDAwareRetriever:
    """Retrieve relevant chunks using JD and candidate context."""

    def __init__(
        self,
        retrieval_service,
        query_builder=None,
        hydrator=None,
        resume_context_builder=None,
    ):
        if retrieval_service is None:
            raise ValueError(
                "retrieval_service cannot be None."
            )

        if not hasattr(retrieval_service, "retrieve"):
            raise TypeError(
                "retrieval_service must implement retrieve."
            )

        if hydrator is not None and not hasattr(
            hydrator,
            "hydrate",
        ):
            raise TypeError(
                "hydrator must implement hydrate."
            )

        if (
            resume_context_builder is not None
            and not hasattr(
                resume_context_builder,
                "build",
            )
        ):
            raise TypeError(
                "resume_context_builder must implement build."
            )

        self.retrieval_service = retrieval_service

        self.query_builder = (
            query_builder or JDQueryBuilder()
        )

        self.hydrator = hydrator

        self.resume_context_builder = (
            resume_context_builder
            or ResumeContextBuilder()
        )

    def retrieve(
        self,
        jd_analysis,
        resume_context=None,
    ):
        """Retrieve chunks using JD and optional resume context."""

        queries = self.query_builder.build(
            jd_analysis
        )

        # -------------------------------------------------
        # Add candidate-aware retrieval context.
        #
        # The original JD queries are preserved exactly.
        # Candidate context only adds an additional query,
        # allowing the vector store to surface evidence
        # relevant to both the JD and candidate.
        # -------------------------------------------------
        if resume_context is not None:
            if isinstance(
                resume_context,
                dict,
            ):
                context = resume_context
            else:
                context = (
                    self.resume_context_builder.build(
                        resume_context
                    )
                )

            candidate_text = (
                self.resume_context_builder.to_query_text(
                    context
                )
            )

            if candidate_text:
                from app.rag.models import RetrievalQuery

                queries.append(
                    RetrievalQuery(
                        query=candidate_text,
                    )
                )

        retrieved_chunks = []
        seen_chunk_ids = set()

        for query in queries:
            chunks = self.retrieval_service.retrieve(
                query
            )

            for chunk in chunks:
                chunk_id = getattr(
                    chunk,
                    "chunk_id",
                    None,
                )

                if chunk_id is None:
                    continue

                if chunk_id in seen_chunk_ids:
                    continue

                seen_chunk_ids.add(chunk_id)
                retrieved_chunks.append(chunk)

        if self.hydrator is not None:
            return self.hydrator.hydrate(
                retrieved_chunks
            )

        return retrieved_chunks