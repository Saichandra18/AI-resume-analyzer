"""Tests for resume template configuration."""

import pytest

from app.templates.config import (
    DEFAULT_TEMPLATE_CONFIG,
    TemplateConfig,
)


def test_default_template_config_has_expected_identity():
    """Default configuration should have stable identity."""

    config = DEFAULT_TEMPLATE_CONFIG

    assert config.name == "default"
    assert config.display_name == "Default"


def test_default_template_config_preserves_current_docx_defaults():
    """Defaults should match the existing renderer configuration."""

    config = DEFAULT_TEMPLATE_CONFIG

    assert config.font_name == "Arial"
    assert config.body_font_size == 10
    assert config.heading_font_size == 12
    assert config.name_font_size == 18
    assert config.contact_font_size == 9
    assert config.item_title_font_size == 10.5
    assert config.secondary_font_size == 9


def test_default_template_config_preserves_current_margins():
    """Defaults should preserve current document margins."""

    config = DEFAULT_TEMPLATE_CONFIG

    assert config.top_margin == 0.55
    assert config.bottom_margin == 0.55
    assert config.left_margin == 0.65
    assert config.right_margin == 0.65


def test_template_config_to_dict():
    """Configuration should serialize predictably."""

    config = TemplateConfig(
        name="test",
        display_name="Test Template",
        font_name="Calibri",
        body_font_size=11,
    )

    data = config.to_dict()

    assert data["name"] == "test"
    assert data["display_name"] == "Test Template"
    assert data["font_name"] == "Calibri"
    assert data["body_font_size"] == 11


def test_template_config_from_dict():
    """Configuration should deserialize from a dictionary."""

    data = {
        "name": "custom",
        "display_name": "Custom Template",
        "font_name": "Calibri",
        "body_font_size": 11,
        "heading_font_size": 13,
    }

    config = TemplateConfig.from_dict(data)

    assert config.name == "custom"
    assert config.display_name == "Custom Template"
    assert config.font_name == "Calibri"
    assert config.body_font_size == 11
    assert config.heading_font_size == 13


def test_template_config_from_empty_dict_uses_defaults():
    """Empty configuration should use defaults."""

    config = TemplateConfig.from_dict({})

    assert config.name == "default"
    assert config.font_name == "Arial"
    assert config.body_font_size == 10


def test_template_config_to_dict_round_trip():
    """Serialization and deserialization should preserve values."""

    original = TemplateConfig(
        name="round_trip",
        display_name="Round Trip",
        font_name="Calibri",
        body_font_size=11,
        heading_font_size=13,
        name_font_size=20,
        top_margin=0.5,
        left_margin=0.7,
    )

    restored = TemplateConfig.from_dict(
        original.to_dict()
    )

    assert restored.to_dict() == original.to_dict()


def test_default_presentation_settings():
    """Default presentation settings should be ATS-safe."""

    config = TemplateConfig()

    assert config.heading_bold is True
    assert config.name_bold is True
    assert config.use_bullets is True
    assert config.single_column is True
    assert config.ats_safe is True


def test_presentation_settings_are_serialized():
    """Presentation settings should be included in serialization."""

    config = TemplateConfig(
        heading_bold=False,
        name_bold=False,
        use_bullets=False,
        single_column=False,
        ats_safe=False,
    )

    data = config.to_dict()

    assert data["heading_bold"] is False
    assert data["name_bold"] is False
    assert data["use_bullets"] is False
    assert data["single_column"] is False
    assert data["ats_safe"] is False


def test_presentation_settings_are_restored():
    """Presentation settings should be restored during deserialization."""

    data = {
        "name": "custom",
        "heading_bold": False,
        "name_bold": False,
        "use_bullets": False,
        "single_column": False,
        "ats_safe": False,
    }

    config = TemplateConfig.from_dict(data)

    assert config.heading_bold is False
    assert config.name_bold is False
    assert config.use_bullets is False
    assert config.single_column is False
    assert config.ats_safe is False


def test_modern_template_is_registered():
    from app.templates.registry import get_template

    template = get_template("modern")

    assert template.name == "modern"
    assert template.display_name == "Modern Professional"


def test_modern_template_has_expected_configuration():
    from app.templates.registry import get_template

    template = get_template("modern")

    assert template.font_name == "Aptos"
    assert template.body_font_size == 10
    assert template.heading_font_size == 13
    assert template.name_font_size == 20
    assert template.contact_font_size == 9
    assert template.item_title_font_size == 11
    assert template.secondary_font_size == 9


def test_modern_template_uses_left_alignment():
    from app.templates.registry import get_template

    template = get_template("modern")

    assert template.name_alignment == "left"
    assert template.contact_alignment == "left"


def test_modern_template_is_ats_safe():
    from app.templates.registry import get_template

    template = get_template("modern")

    assert template.ats_safe is True
    assert template.single_column is True
    assert template.use_bullets is True


def test_list_templates_contains_modern():
    from app.templates.registry import list_templates

    templates = list_templates()

    assert "modern" in templates

def test_technical_template_is_registered():
    from app.templates.registry import get_template

    template = get_template("technical")

    assert template.name == "technical"
    assert template.display_name == "Compact Technical"


def test_technical_template_has_expected_configuration():
    from app.templates.registry import get_template

    template = get_template("technical")

    assert template.font_name == "Arial"
    assert template.body_font_size == 9.5
    assert template.heading_font_size == 11.5
    assert template.name_font_size == 17
    assert template.contact_font_size == 8.5
    assert template.item_title_font_size == 10
    assert template.secondary_font_size == 8.5


def test_technical_template_uses_compact_spacing():
    from app.templates.registry import get_template

    template = get_template("technical")

    assert template.top_margin == 0.45
    assert template.bottom_margin == 0.45
    assert template.left_margin == 0.55
    assert template.right_margin == 0.55
    assert template.section_space_before == 6
    assert template.section_space_after == 2
    assert template.body_space_after == 2
    assert template.line_spacing == 1.0


def test_technical_template_uses_left_alignment():
    from app.templates.registry import get_template

    template = get_template("technical")

    assert template.name_alignment == "left"
    assert template.contact_alignment == "left"


def test_technical_template_is_ats_safe():
    from app.templates.registry import get_template

    template = get_template("technical")

    assert template.ats_safe is True
    assert template.single_column is True
    assert template.use_bullets is True


def test_list_templates_contains_technical():
    from app.templates.registry import list_templates

    templates = list_templates()

    assert "technical" in templates