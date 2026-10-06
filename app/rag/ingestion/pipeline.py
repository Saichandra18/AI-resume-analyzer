"""End-to-end knowledge ingestion pipeline."""

from app.rag.ingestion.cleaner import DocumentCleaner
from app.rag.ingestion.chunker import DocumentChunker
from app.rag.ingestion.loader import DocumentLoader
from app.rag.ingestion.parser import DocumentParser


class IngestionPipeline:
    """Load, parse, clean, and chunk knowledge documents."""

    def __init__(
        self,
        loader=None,
        parser=None,
        cleaner=None,
        chunker=None,
    ):
        self.loader = loader or DocumentLoader()
        self.parser = parser or DocumentParser()
        self.cleaner = cleaner or DocumentCleaner()
        self.chunker = chunker or DocumentChunker()

    def ingest(
        self,
        file_path,
        document_id=None,
        metadata=None,
    ):
        """Ingest a document into DocumentChunk objects."""

        raw_text = self.loader.load(file_path)

        parsed_text = self.parser.parse(raw_text)

        cleaned_text = self.cleaner.clean(parsed_text)

        if document_id is None:
            document_id = file_path.stem

        return self.chunker.chunk(
            cleaned_text,
            document_id=document_id,
            metadata=metadata,
        )