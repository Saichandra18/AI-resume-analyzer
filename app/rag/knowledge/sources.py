"""Knowledge-source definitions and catalog for the RAG knowledge base."""

from dataclasses import dataclass, field
from copy import deepcopy


@dataclass(frozen=True)
class KnowledgeSource:
    """Describe an approved document that belongs to the knowledge base."""

    source_id: str
    file_path: str
    category: str
    description: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.source_id, str) or not self.source_id.strip():
            raise ValueError("source_id must be a non-empty string.")

        if not isinstance(self.file_path, str) or not self.file_path.strip():
            raise ValueError("file_path must be a non-empty string.")

        if not isinstance(self.category, str) or not self.category.strip():
            raise ValueError("category must be a non-empty string.")

        if not isinstance(self.description, str):
            raise TypeError("description must be a string.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        object.__setattr__(
            self,
            "metadata",
            deepcopy(self.metadata),
        )

    def to_dict(self):
        """Return a defensive dictionary representation."""

        return {
            "source_id": self.source_id,
            "file_path": self.file_path,
            "category": self.category,
            "description": self.description,
            "metadata": deepcopy(self.metadata),
        }


class KnowledgeSourceCatalog:
    """Manage the approved sources used to build the RAG knowledge base."""

    def __init__(self, sources=None):
        self._sources = {}

        if sources is None:
            return

        if not isinstance(sources, (list, tuple)):
            raise TypeError("sources must be a list or tuple.")

        for source in sources:
            self.add(source)

    def add(self, source):
        """Add or replace an approved knowledge source."""

        if not isinstance(source, KnowledgeSource):
            raise TypeError("source must be a KnowledgeSource.")

        self._sources[source.source_id] = source
        return source

    def get(self, source_id):
        """Return a source by ID, or None when it does not exist."""

        if not isinstance(source_id, str):
            raise TypeError("source_id must be a string.")

        return self._sources.get(source_id)

    def remove(self, source_id):
        """Remove a source by ID and return it when present."""

        if not isinstance(source_id, str):
            raise TypeError("source_id must be a string.")

        return self._sources.pop(source_id, None)

    def contains(self, source_id):
        """Return whether a source ID is registered."""

        if not isinstance(source_id, str):
            raise TypeError("source_id must be a string.")

        return source_id in self._sources

    def count(self):
        """Return the number of registered knowledge sources."""

        return len(self._sources)

    def clear(self):
        """Remove all registered knowledge sources."""

        self._sources.clear()

    def list_sources(self):
        """Return registered sources in deterministic source-ID order."""

        return [
            self._sources[source_id]
            for source_id in sorted(self._sources)
        ]

    def filter_by_category(self, category):
        """Return sources belonging to a category."""

        if not isinstance(category, str) or not category.strip():
            raise ValueError("category must be a non-empty string.")

        normalized_category = category.strip().lower()

        return [
            source
            for source in self.list_sources()
            if source.category.strip().lower() == normalized_category
        ]