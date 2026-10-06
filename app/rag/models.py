"""Core data models for the RAG subsystem."""

from copy import deepcopy


class KnowledgeDocument:
    """Represent a source document stored in the RAG knowledge base."""

    def __init__(
        self,
        document_id,
        content,
        title="",
        source="",
        category="general",
        metadata=None,
    ):
        if not document_id:
            raise ValueError(
                "document_id must be provided."
            )

        if not isinstance(content, str):
            raise TypeError(
                "content must be a string."
            )

        self.document_id = str(document_id)
        self.content = content
        self.title = title or ""
        self.source = source or ""
        self.category = category or "general"
        self.metadata = deepcopy(metadata or {})

    def to_dict(self):
        """Return a serialized representation."""

        return {
            "document_id": self.document_id,
            "content": self.content,
            "title": self.title,
            "source": self.source,
            "category": self.category,
            "metadata": deepcopy(self.metadata),
        }

    @classmethod
    def from_dict(cls, data=None):
        """Create a knowledge document from a dictionary."""

        data = data or {}

        return cls(
            document_id=data.get("document_id"),
            content=data.get("content", ""),
            title=data.get("title", ""),
            source=data.get("source", ""),
            category=data.get(
                "category",
                "general",
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )


class DocumentChunk:
    """Represent a retrievable chunk of a knowledge document."""

    def __init__(
        self,
        chunk_id,
        document_id,
        text,
        chunk_index=0,
        metadata=None,
    ):
        if not chunk_id:
            raise ValueError(
                "chunk_id must be provided."
            )

        if not document_id:
            raise ValueError(
                "document_id must be provided."
            )

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        if (
            not isinstance(chunk_index, int)
            or chunk_index < 0
        ):
            raise ValueError(
                "chunk_index must be a non-negative integer."
            )

        self.chunk_id = str(chunk_id)
        self.document_id = str(document_id)
        self.text = text
        self.chunk_index = chunk_index
        self.metadata = deepcopy(metadata or {})

    def to_dict(self):
        """Return a serialized representation."""

        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "chunk_index": self.chunk_index,
            "metadata": deepcopy(self.metadata),
        }

    @classmethod
    def from_dict(cls, data=None):
        """Create a document chunk from a dictionary."""

        data = data or {}

        return cls(
            chunk_id=data.get("chunk_id"),
            document_id=data.get("document_id"),
            text=data.get("text", ""),
            chunk_index=data.get(
                "chunk_index",
                0,
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )


class EmbeddingRecord:
    """Represent an embedding associated with a document chunk."""

    def __init__(
        self,
        chunk_id,
        vector=None,
        model="",
        dimensions=None,
        metadata=None,
    ):
        if not chunk_id:
            raise ValueError(
                "chunk_id must be provided."
            )

        if vector is None:
            vector = []

        if not isinstance(vector, (list, tuple)):
            raise TypeError(
                "vector must be a list or tuple."
            )

        if dimensions is not None:
            if (
                not isinstance(dimensions, int)
                or dimensions < 1
            ):
                raise ValueError(
                    "dimensions must be a positive integer."
                )

            if vector and len(vector) != dimensions:
                raise ValueError(
                    "vector length must match dimensions."
                )

        self.chunk_id = str(chunk_id)
        self.vector = list(vector)
        self.model = model or ""
        self.dimensions = (
            dimensions
            if dimensions is not None
            else len(self.vector)
        )
        self.metadata = deepcopy(metadata or {})

    def to_dict(self):
        """Return a serialized representation."""

        return {
            "chunk_id": self.chunk_id,
            "vector": list(self.vector),
            "model": self.model,
            "dimensions": self.dimensions,
            "metadata": deepcopy(self.metadata),
        }

    @classmethod
    def from_dict(cls, data=None):
        """Create an embedding record from a dictionary."""

        data = data or {}

        return cls(
            chunk_id=data.get("chunk_id"),
            vector=data.get(
                "vector",
                [],
            ),
            model=data.get(
                "model",
                "",
            ),
            dimensions=data.get(
                "dimensions"
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )


class RetrievalQuery:
    """Represent a query sent to the RAG retrieval layer."""

    def __init__(
        self,
        query,
        top_k=5,
        filters=None,
        query_type="general",
        metadata=None,
    ):
        if not isinstance(query, str):
            raise TypeError(
                "query must be a string."
            )

        if not query.strip():
            raise ValueError(
                "query must not be empty."
            )

        if (
            not isinstance(top_k, int)
            or top_k < 1
        ):
            raise ValueError(
                "top_k must be a positive integer."
            )

        self.query = query
        self.top_k = top_k
        self.filters = deepcopy(filters or {})
        self.query_type = query_type or "general"
        self.metadata = deepcopy(metadata or {})

    def to_dict(self):
        """Return a serialized representation."""

        return {
            "query": self.query,
            "top_k": self.top_k,
            "filters": deepcopy(self.filters),
            "query_type": self.query_type,
            "metadata": deepcopy(self.metadata),
        }

    @classmethod
    def from_dict(cls, data=None):
        """Create a retrieval query from a dictionary."""

        data = data or {}

        return cls(
            query=data.get(
                "query",
                "",
            ),
            top_k=data.get(
                "top_k",
                5,
            ),
            filters=data.get(
                "filters",
                {},
            ),
            query_type=data.get(
                "query_type",
                "general",
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )


class RetrievedChunk:
    """Represent a chunk returned by the retrieval layer."""

    def __init__(
        self,
        chunk_id,
        text,
        score=0.0,
        document_id=None,
        metadata=None,
    ):
        if not chunk_id:
            raise ValueError(
                "chunk_id must be provided."
            )

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        if not isinstance(score, (int, float)):
            raise TypeError(
                "score must be numeric."
            )

        self.chunk_id = str(chunk_id)
        self.document_id = (
            str(document_id)
            if document_id is not None
            else None
        )
        self.text = text
        self.score = float(score)
        self.metadata = deepcopy(metadata or {})

    def to_dict(self):
        """Return a serialized representation."""

        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "score": self.score,
            "metadata": deepcopy(self.metadata),
        }

    @classmethod
    def from_dict(cls, data=None):
        """Create a retrieved chunk from a dictionary."""

        data = data or {}

        return cls(
            chunk_id=data.get("chunk_id"),
            document_id=data.get(
                "document_id"
            ),
            text=data.get(
                "text",
                "",
            ),
            score=data.get(
                "score",
                0.0,
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )


class GroundedEvidence:
    """Represent evidence supporting a RAG recommendation or claim."""

    def __init__(
        self,
        evidence_id,
        text,
        source_chunk_ids=None,
        claim="",
        confidence=0.0,
        metadata=None,
    ):
        if not evidence_id:
            raise ValueError(
                "evidence_id must be provided."
            )

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        if not isinstance(
            source_chunk_ids,
            (list, tuple, set),
        ):
            source_chunk_ids = []

        if not isinstance(
            confidence,
            (int, float),
        ):
            raise TypeError(
                "confidence must be numeric."
            )

        self.evidence_id = str(evidence_id)
        self.text = text
        self.source_chunk_ids = [
            str(chunk_id)
            for chunk_id in source_chunk_ids
        ]
        self.claim = claim or ""
        self.confidence = float(confidence)
        self.metadata = deepcopy(metadata or {})

    def to_dict(self):
        """Return a serialized representation."""

        return {
            "evidence_id": self.evidence_id,
            "text": self.text,
            "source_chunk_ids": list(
                self.source_chunk_ids
            ),
            "claim": self.claim,
            "confidence": self.confidence,
            "metadata": deepcopy(self.metadata),
        }

    @classmethod
    def from_dict(cls, data=None):
        """Create grounded evidence from a dictionary."""

        data = data or {}

        return cls(
            evidence_id=data.get(
                "evidence_id"
            ),
            text=data.get(
                "text",
                "",
            ),
            source_chunk_ids=data.get(
                "source_chunk_ids",
                [],
            ),
            claim=data.get(
                "claim",
                "",
            ),
            confidence=data.get(
                "confidence",
                0.0,
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )


class RAGContext:
    """Represent the complete context returned by the RAG layer."""

    def __init__(
        self,
        query=None,
        retrieved_chunks=None,
        evidence=None,
        recommendations=None,
        metadata=None,
    ):
        self.query = (
            query
            if isinstance(
                query,
                RetrievalQuery,
            )
            else (
                RetrievalQuery.from_dict(query)
                if isinstance(query, dict)
                else None
            )
        )

        self.retrieved_chunks = [
            chunk
            if isinstance(
                chunk,
                RetrievedChunk,
            )
            else RetrievedChunk.from_dict(chunk)
            for chunk in (
                retrieved_chunks or []
            )
        ]

        self.evidence = [
            item
            if isinstance(
                item,
                GroundedEvidence,
            )
            else GroundedEvidence.from_dict(item)
            for item in (
                evidence or []
            )
        ]

        self.recommendations = deepcopy(
            recommendations or []
        )

        self.metadata = deepcopy(
            metadata or {}
        )

    def to_dict(self):
        """Return a serialized representation."""

        return {
            "query": (
                self.query.to_dict()
                if self.query is not None
                else None
            ),
            "retrieved_chunks": [
                chunk.to_dict()
                for chunk in self.retrieved_chunks
            ],
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
            "recommendations": deepcopy(
                self.recommendations
            ),
            "metadata": deepcopy(
                self.metadata
            ),
        }

    @classmethod
    def from_dict(cls, data=None):
        """Create RAG context from a dictionary."""

        data = data or {}

        return cls(
            query=data.get("query"),
            retrieved_chunks=data.get(
                "retrieved_chunks",
                [],
            ),
            evidence=data.get(
                "evidence",
                [],
            ),
            recommendations=data.get(
                "recommendations",
                [],
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )