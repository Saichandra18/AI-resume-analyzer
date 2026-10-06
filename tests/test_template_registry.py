"""Tests for resume template registry."""

import pytest

from app.templates.config import TemplateConfig
from app.templates.registry import (
    get_template,
    list_templates,
    register_template,
)


def test_default_template_is_registered():
    template = get_template("default")

    assert isinstance(template, TemplateConfig)
    assert template.name == "default"


def test_default_template_matches_default_config():
    template = get_template("default")

    assert template.display_name == "Default"
    assert template.font_name == "Arial"
    assert template.body_font_size == 10


def test_list_templates_contains_default():
    templates = list_templates()

    assert "default" in templates


def test_unknown_template_is_rejected():
    with pytest.raises(ValueError, match="Unknown resume template"):
        get_template("does-not-exist")


def test_template_name_must_be_string():
    with pytest.raises(TypeError, match="Template name must be a string"):
        get_template(None)


def test_register_template():
    template = TemplateConfig(
        name="test-template",
        display_name="Test Template",
    )

    register_template(template)

    assert get_template("test-template") is template


def test_duplicate_template_is_rejected():
    template = TemplateConfig(
        name="duplicate-template",
        display_name="Duplicate Template",
    )

    register_template(template)

    with pytest.raises(
        ValueError,
        match="Template already registered",
    ):
        register_template(template)


def test_invalid_template_registration_is_rejected():
    with pytest.raises(
        TypeError,
        match="template must be a TemplateConfig instance",
    ):
        register_template("not-a-template")

def test_ats_clean_template_is_registered():
    """ATS Clean template should be available in the registry."""

    template = get_template("ats_clean")

    assert isinstance(template, TemplateConfig)
    assert template.name == "ats_clean"
    assert template.display_name == "ATS Clean"


def test_ats_clean_template_is_ats_safe():
    """ATS Clean should use ATS-safe presentation settings."""

    template = get_template("ats_clean")

    assert template.ats_safe is True
    assert template.single_column is True
    assert template.use_bullets is True


def test_ats_clean_template_uses_expected_typography():
    """ATS Clean should use the defined professional typography."""

    template = get_template("ats_clean")

    assert template.font_name == "Arial"
    assert template.body_font_size == 10
    assert template.heading_font_size == 12
    assert template.name_font_size == 18


def test_ats_clean_template_uses_expected_spacing():
    """ATS Clean should preserve the intended spacing."""

    template = get_template("ats_clean")

    assert template.top_margin == 0.55
    assert template.bottom_margin == 0.55
    assert template.left_margin == 0.65
    assert template.right_margin == 0.65
    assert template.line_spacing == 1.0


def test_list_templates_contains_ats_clean():
    """Template registry should expose ATS Clean."""

    templates = list_templates()

    assert "default" in templates
    assert "ats_clean" in templates