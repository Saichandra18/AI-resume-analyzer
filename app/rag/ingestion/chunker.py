"""Document chunking for the RAG knowledge base."""

from app.rag.models import DocumentChunk


class DocumentChunker:
    """Split cleaned documents into deterministic chunks."""

    def __init__(self, chunk_size=1000, overlap=200):
        if not isinstance(chunk_size, int):
            raise TypeError("chunk_size must be an integer.")

        if not isinstance(overlap, int):
            raise TypeError("overlap must be an integer.")

        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive.")

        if overlap < 0:
            raise ValueError("overlap cannot be negative.")

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self,
        text,
        document_id="document",
        metadata=None,
    ):
        """Split text into DocumentChunk objects."""

        if text is None:
            raise ValueError("Document text cannot be None.")

        if not isinstance(text, str):
            raise TypeError("Document text must be a string.")

        if not isinstance(document_id, str):
            raise TypeError("document_id must be a string.")

        if not document_id.strip():
            raise ValueError("document_id cannot be empty.")

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        if not text.strip():
            return []

        paragraphs = [
            paragraph.strip()
            for paragraph in text.split("\n")
            if paragraph.strip()
        ]

        chunks = []
        current = ""
        chunk_index = 0

        for paragraph in paragraphs:
            if not current:
                current = paragraph
                continue

            candidate = f"{current}\n{paragraph}"

            if len(candidate) <= self.chunk_size:
                current = candidate
                continue

            chunks.append(
                self._create_chunk(
                    current,
                    document_id,
                    chunk_index,
                    metadata,
                )
            )

            chunk_index += 1

            overlap_text = self._get_overlap(current)

            if overlap_text:
                current = f"{overlap_text}\n{paragraph}"
            else:
                current = paragraph

            if len(current) > self.chunk_size:
                chunks.append(
                    self._create_chunk(
                        current[:self.chunk_size],
                        document_id,
                        chunk_index,
                        metadata,
                    )
                )

                chunk_index += 1
                current = current[self.chunk_size - self.overlap:]

        if current:
            chunks.append(
                self._create_chunk(
                    current,
                    document_id,
                    chunk_index,
                    metadata,
                )
            )

        return chunks

    def _get_overlap(self, text):
        """Return the trailing overlap portion of a chunk."""

        if self.overlap <= 0:
            return ""

        return text[-self.overlap:]

    @staticmethod
    def _create_chunk(
        text,
        document_id,
        chunk_index,
        metadata,
    ):
        """Create a DocumentChunk model with retrieval metadata."""

        chunk_metadata = dict(metadata)

        chunk_metadata.setdefault(
            "document_id",
            document_id,
        )
        chunk_metadata.setdefault(
            "chunk_index",
            chunk_index,
        )

        return DocumentChunk(
            chunk_id=f"{document_id}:{chunk_index}",
            document_id=document_id,
            text=text,
            metadata=chunk_metadata,
        )