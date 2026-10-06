"""Default approved knowledge-base source catalog."""

from pathlib import Path

from app.rag.knowledge.sources import (
    KnowledgeSource,
    KnowledgeSourceCatalog,
)


class DefaultKnowledgeCatalog:
    """Build the catalog of approved built-in knowledge sources."""

    SOURCES = (
        (
            "ats-guidelines",
            "ats_guidelines.txt",
            "ats",
            "General ATS resume optimization guidance.",
        ),
        (
            "resume-guidelines",
            "resume_guidelines.txt",
            "resume",
            "General resume writing and optimization guidance.",
        ),
        (
            "role-guidelines",
            "role_guidelines.txt",
            "role",
            "General job-role and requirement alignment guidance.",
        ),
    )

    def __init__(self, sources_directory=None):
        if sources_directory is None:
            sources_directory = (
                Path(__file__).resolve().parent / "sources"
            )

        self.sources_directory = Path(sources_directory)

    def build(self):
        """Build and return the approved knowledge-source catalog."""

        catalog = KnowledgeSourceCatalog()

        for (
            source_id,
            filename,
            category,
            description,
        ) in self.SOURCES:
            file_path = self.sources_directory / filename

            source = KnowledgeSource(
                source_id=source_id,
                file_path=str(file_path),
                category=category,
                description=description,
                metadata={
                    "source_type": "built_in",
                    "filename": filename,
                },
            )

            catalog.add(source)

        return catalog