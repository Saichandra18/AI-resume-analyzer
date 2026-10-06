"""Convert retrieved knowledge chunks into optimization guidance."""

from copy import deepcopy

from app.rag.models import RetrievedChunk


class KnowledgeGuidanceAdapter:
    """Adapt knowledge-base retrieval into safe optimization guidance."""

    def build(self, retrieved_chunks, metadata=None):
        """Build structured guidance from knowledge chunks."""

        if not isinstance(
            retrieved_chunks,
            (list, tuple),
        ):
            raise TypeError(
                "retrieved_chunks must be a list or tuple."
            )

        for chunk in retrieved_chunks:
            if not isinstance(
                chunk,
                RetrievedChunk,
            ):
                raise TypeError(
                    "retrieved_chunks must contain "
                    "RetrievedChunk objects."
                )

        guidance = []

        for chunk in retrieved_chunks:
            category = self._get_category(chunk)

            guidance.append(
                {
                    "text": chunk.text,
                    "source_chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "score": chunk.score,
                    "category": category,
                    "metadata": deepcopy(
                        chunk.metadata
                    ),
                }
            )

        context_metadata = deepcopy(
            metadata or {}
        )

        context_metadata[
            "knowledge_base"
        ] = True

        context_metadata[
            "guidance_count"
        ] = len(guidance)

        return {
            "guidance": guidance,
            "metadata": context_metadata,
        }

    @staticmethod
    def _get_category(chunk):
        """Return the knowledge category from chunk metadata."""

        metadata = chunk.metadata or {}

        category = metadata.get(
            "source_category"
        )

        if category is None:
            category = metadata.get(
                "category",
                "general",
            )

        if not isinstance(category, str):
            return "general"

        category = category.strip()

        return category or "general"