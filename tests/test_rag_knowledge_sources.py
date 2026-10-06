import pytest

from app.rag.knowledge.sources import (
    KnowledgeSource,
    KnowledgeSourceCatalog,
)


def make_source(
    source_id="ats-guidelines",
    file_path="knowledge/ats_guidelines.txt",
    category="ats",
    description="ATS optimization guidance",
    metadata=None,
):
    return KnowledgeSource(
        source_id=source_id,
        file_path=file_path,
        category=category,
        description=description,
        metadata=metadata or {"version": 1},
    )


def test_knowledge_source_requires_source_id():
    with pytest.raises(ValueError):
        KnowledgeSource(
            source_id="",
            file_path="guide.txt",
            category="ats",
        )


def test_knowledge_source_requires_file_path():
    with pytest.raises(ValueError):
        KnowledgeSource(
            source_id="source-1",
            file_path="",
            category="ats",
        )


def test_knowledge_source_requires_category():
    with pytest.raises(ValueError):
        KnowledgeSource(
            source_id="source-1",
            file_path="guide.txt",
            category="",
        )


def test_knowledge_source_rejects_invalid_description():
    with pytest.raises(TypeError):
        KnowledgeSource(
            source_id="source-1",
            file_path="guide.txt",
            category="ats",
            description=None,
        )


def test_knowledge_source_rejects_invalid_metadata():
    with pytest.raises(TypeError):
        KnowledgeSource(
            source_id="source-1",
            file_path="guide.txt",
            category="ats",
            metadata=[],
        )


def test_knowledge_source_preserves_values():
    source = make_source()

    assert source.source_id == "ats-guidelines"
    assert source.file_path == "knowledge/ats_guidelines.txt"
    assert source.category == "ats"
    assert source.description == "ATS optimization guidance"
    assert source.metadata == {"version": 1}


def test_knowledge_source_to_dict():
    source = make_source()

    result = source.to_dict()

    assert result == {
        "source_id": "ats-guidelines",
        "file_path": "knowledge/ats_guidelines.txt",
        "category": "ats",
        "description": "ATS optimization guidance",
        "metadata": {"version": 1},
    }


def test_knowledge_source_to_dict_returns_defensive_metadata():
    source = make_source()

    result = source.to_dict()
    result["metadata"]["version"] = 99

    assert source.metadata == {"version": 1}


def test_catalog_starts_empty():
    catalog = KnowledgeSourceCatalog()

    assert catalog.count() == 0
    assert catalog.list_sources() == []


def test_catalog_adds_source():
    catalog = KnowledgeSourceCatalog()
    source = make_source()

    result = catalog.add(source)

    assert result is source
    assert catalog.count() == 1
    assert catalog.get("ats-guidelines") is source


def test_catalog_rejects_invalid_source():
    catalog = KnowledgeSourceCatalog()

    with pytest.raises(TypeError):
        catalog.add(object())


def test_catalog_constructor_accepts_sources():
    source1 = make_source("ats-guidelines")
    source2 = make_source(
        "resume-guidelines",
        "knowledge/resume_guidelines.txt",
        "resume",
    )

    catalog = KnowledgeSourceCatalog([source1, source2])

    assert catalog.count() == 2
    assert catalog.get("ats-guidelines") is source1
    assert catalog.get("resume-guidelines") is source2


def test_catalog_rejects_invalid_constructor_input():
    with pytest.raises(TypeError):
        KnowledgeSourceCatalog(object())


def test_catalog_contains():
    catalog = KnowledgeSourceCatalog([make_source()])

    assert catalog.contains("ats-guidelines") is True
    assert catalog.contains("missing") is False


def test_catalog_get_requires_string_id():
    catalog = KnowledgeSourceCatalog()

    with pytest.raises(TypeError):
        catalog.get(None)


def test_catalog_contains_requires_string_id():
    catalog = KnowledgeSourceCatalog()

    with pytest.raises(TypeError):
        catalog.contains(None)


def test_catalog_remove():
    source = make_source()
    catalog = KnowledgeSourceCatalog([source])

    result = catalog.remove("ats-guidelines")

    assert result is source
    assert catalog.count() == 0
    assert catalog.get("ats-guidelines") is None


def test_catalog_remove_missing_source_returns_none():
    catalog = KnowledgeSourceCatalog()

    assert catalog.remove("missing") is None


def test_catalog_clear():
    catalog = KnowledgeSourceCatalog(
        [
            make_source("source-1"),
            make_source("source-2"),
        ]
    )

    catalog.clear()

    assert catalog.count() == 0
    assert catalog.list_sources() == []


def test_catalog_lists_sources_deterministically():
    source_z = make_source("z-source")
    source_a = make_source("a-source")
    source_m = make_source("m-source")

    catalog = KnowledgeSourceCatalog(
        [source_z, source_a, source_m]
    )

    result = catalog.list_sources()

    assert [source.source_id for source in result] == [
        "a-source",
        "m-source",
        "z-source",
    ]


def test_catalog_filter_by_category():
    ats = make_source("ats", category="ATS")
    resume = make_source("resume", category="resume")
    ats2 = make_source("ats-2", category="ats")

    catalog = KnowledgeSourceCatalog(
        [ats, resume, ats2]
    )

    result = catalog.filter_by_category("ats")

    assert [source.source_id for source in result] == [
        "ats",
        "ats-2",
    ]


def test_catalog_filter_by_category_is_case_insensitive():
    source = make_source("source-1", category="ATS")
    catalog = KnowledgeSourceCatalog([source])

    result = catalog.filter_by_category("ats")

    assert result == [source]


def test_catalog_filter_requires_category():
    catalog = KnowledgeSourceCatalog()

    with pytest.raises(ValueError):
        catalog.filter_by_category("")


def test_catalog_replaces_source_with_same_id():
    original = make_source(
        "source-1",
        description="Original",
    )
    replacement = make_source(
        "source-1",
        description="Replacement",
    )

    catalog = KnowledgeSourceCatalog([original])
    catalog.add(replacement)

    assert catalog.count() == 1
    assert catalog.get("source-1") is replacement


def test_knowledge_source_metadata_is_copied():
    metadata = {"category": "ats"}

    source = KnowledgeSource(
        source_id="source-1",
        file_path="guide.txt",
        category="ats",
        metadata=metadata,
    )

    metadata["category"] = "changed"

    assert source.metadata == {"category": "ats"}