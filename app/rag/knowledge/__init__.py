"""Knowledge-base source management and runtime retrieval."""

from app.rag.knowledge.catalog import DefaultKnowledgeCatalog
from app.rag.knowledge.manager import KnowledgeBaseManager
from app.rag.knowledge.service import KnowledgeBaseService
from app.rag.knowledge.sources import (
    KnowledgeSource,
    KnowledgeSourceCatalog,
)

__all__ = [
    "KnowledgeSource",
    "KnowledgeSourceCatalog",
    "DefaultKnowledgeCatalog",
    "KnowledgeBaseManager",
    "KnowledgeBaseService",
]