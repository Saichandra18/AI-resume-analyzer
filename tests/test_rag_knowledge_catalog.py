import pytest

from app.rag.knowledge.catalog import DefaultKnowledgeCatalog
from app.rag.knowledge.sources import KnowledgeSourceCatalog


def test_default_catalog_builds_three_sources():
    catalog = DefaultKnowledgeCatalog().build()

    assert isinstance(catalog, KnowledgeSourceCatalog)
    assert catalog.count() == 3


def test_default_catalog_contains_expected_sources():
    catalog = DefaultKnowledgeCatalog().build()

    assert catalog.contains("ats-guidelines")
    assert catalog.contains("resume-guidelines")
    assert catalog.contains("role-guidelines")


def test_default_catalog_sources_are_deterministic():
    catalog = DefaultKnowledgeCatalog().build()

    assert [
        source.source_id
        for source in catalog.list_sources()
    ] == [
        "ats-guidelines",
        "resume-guidelines",
        "role-guidelines",
    ]


def test_default_catalog_uses_expected_categories():
    catalog = DefaultKnowledgeCatalog().build()

    assert catalog.get("ats-guidelines").category == "ats"
    assert catalog.get("resume-guidelines").category == "resume"
    assert catalog.get("role-guidelines").category == "role"


def test_default_catalog_uses_existing_source_files():
    catalog = DefaultKnowledgeCatalog().build()

    for source in catalog.list_sources():
        assert source.file_path
        assert source.file_path.endswith(".txt")


def test_default_catalog_source_files_exist():
    catalog = DefaultKnowledgeCatalog().build()

    for source in catalog.list_sources():
        assert source.file_path
        assert __import__("pathlib").Path(
            source.file_path
        ).is_file()


def test_default_catalog_metadata_identifies_built_in_sources():
    catalog = DefaultKnowledgeCatalog().build()

    for source in catalog.list_sources():
        assert source.metadata["source_type"] == "built_in"
        assert source.metadata["filename"].endswith(".txt")


def test_default_catalog_has_descriptions():
    catalog = DefaultKnowledgeCatalog().build()

    for source in catalog.list_sources():
        assert source.description.strip()


def test_custom_sources_directory_is_supported(tmp_path):
    source_dir = tmp_path / "sources"
    source_dir.mkdir()

    (source_dir / "ats_guidelines.txt").write_text("ATS")
    (source_dir / "resume_guidelines.txt").write_text("Resume")
    (source_dir / "role_guidelines.txt").write_text("Role")

    catalog = DefaultKnowledgeCatalog(
        sources_directory=source_dir
    ).build()

    assert catalog.count() == 3

    for source in catalog.list_sources():
        assert __import__("pathlib").Path(
            source.file_path
        ).is_file()


def test_custom_sources_directory_is_stored_as_path(tmp_path):
    catalog_builder = DefaultKnowledgeCatalog(
        sources_directory=tmp_path
    )

    assert catalog_builder.sources_directory == tmp_path


def test_default_sources_directory_points_to_sources_folder():
    catalog_builder = DefaultKnowledgeCatalog()

    assert catalog_builder.sources_directory.name == "sources"


def test_each_default_source_has_unique_id():
    catalog = DefaultKnowledgeCatalog().build()

    source_ids = [
        source.source_id
        for source in catalog.list_sources()
    ]

    assert len(source_ids) == len(set(source_ids))


def test_each_default_source_has_unique_file_path():
    catalog = DefaultKnowledgeCatalog().build()

    file_paths = [
        source.file_path
        for source in catalog.list_sources()
    ]

    assert len(file_paths) == len(set(file_paths))


def test_default_catalog_can_be_built_multiple_times():
    builder = DefaultKnowledgeCatalog()

    first = builder.build()
    second = builder.build()

    assert first.count() == second.count()
    assert [
        source.to_dict()
        for source in first.list_sources()
    ] == [
        source.to_dict()
        for source in second.list_sources()
    ]


def test_build_returns_independent_catalogs():
    builder = DefaultKnowledgeCatalog()

    first = builder.build()
    second = builder.build()

    first.remove("ats-guidelines")

    assert first.count() == 2
    assert second.count() == 3


def test_default_catalog_does_not_modify_source_files():
    catalog = DefaultKnowledgeCatalog().build()

    original_contents = {
        source.source_id: open(
            source.file_path,
            encoding="utf-8",
        ).read()
        for source in catalog.list_sources()
    }

    DefaultKnowledgeCatalog().build()

    for source in catalog.list_sources():
        with open(source.file_path, encoding="utf-8") as file:
            assert file.read() == original_contents[source.source_id]


@pytest.mark.parametrize(
    "source_id, expected_filename",
    [
        ("ats-guidelines", "ats_guidelines.txt"),
        ("resume-guidelines", "resume_guidelines.txt"),
        ("role-guidelines", "role_guidelines.txt"),
    ],
)
def test_default_catalog_maps_ids_to_expected_files(
    source_id,
    expected_filename,
):
    catalog = DefaultKnowledgeCatalog().build()

    source = catalog.get(source_id)

    assert source.metadata["filename"] == expected_filename
    assert source.file_path.endswith(expected_filename)