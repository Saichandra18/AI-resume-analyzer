"""Application-level runtime services for RAG."""

import os
from pathlib import Path
from threading import Lock


_knowledge_base_service = None
_knowledge_base_lock = Lock()


def _get_default_index_path():
    """Return the default persisted knowledge-index path."""

    project_root = Path(__file__).resolve().parents[2]

    return (
        project_root
        / "generated_rag"
        / "knowledge_index.json"
    )


def _get_index_path():
    """Return the configured persisted knowledge-index path."""

    configured_path = os.getenv(
        "RAG_KNOWLEDGE_INDEX_PATH"
    )

    if configured_path:
        return Path(configured_path)

    return _get_default_index_path()


def _initialize_knowledge_base(service):
    """Load or build the persistent knowledge base."""

    index_path = _get_index_path()

    if index_path.exists():
        try:
            service.load(index_path)
            return
        except ValueError:
            # The persisted index is invalid or incompatible.
            # Rebuild it from the approved knowledge sources.
            pass

    service.index_all()
    service.save(index_path)


def get_knowledge_base_service():
    """Return the shared application-level knowledge-base service."""

    global _knowledge_base_service

    if _knowledge_base_service is not None:
        return _knowledge_base_service

    with _knowledge_base_lock:
        if _knowledge_base_service is not None:
            return _knowledge_base_service

        # Lazy import avoids the RAG package circular-import chain.
        from app.rag.knowledge.service import (
            KnowledgeBaseService,
        )

        service = KnowledgeBaseService()

        if not service.is_indexed():
            _initialize_knowledge_base(service)

        _knowledge_base_service = service

    return _knowledge_base_service