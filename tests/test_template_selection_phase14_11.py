import pytest

from app.templates.selector import (
    DEFAULT_TEMPLATE_NAME,
    available_templates,
    is_valid_template,
    normalize_template_name,
    select_template,
)
from app.templates.registry import get_template


TEMPLATES = ("default", "ats_clean", "modern", "technical")


def test_default_template_is_used_when_selection_is_omitted():
    assert normalize_template_name() == DEFAULT_TEMPLATE_NAME
    assert select_template().name == DEFAULT_TEMPLATE_NAME


@pytest.mark.parametrize("value", [None, "", "   "])
def test_empty_selection_falls_back_to_default(value):
    assert normalize_template_name(value) == "default"
    assert select_template(value).name == "default"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("DEFAULT", "default"),
        (" ATS_CLEAN ", "ats_clean"),
        ("Modern", "modern"),
        (" TECHNICAL ", "technical"),
    ],
)
def test_template_selection_is_normalized(value, expected):
    assert normalize_template_name(value) == expected
    assert select_template(value).name == expected


@pytest.mark.parametrize("template", TEMPLATES)
def test_all_registered_templates_are_selectable(template):
    selected = select_template(template)

    assert selected.name == template
    assert selected == get_template(template)


def test_available_templates_contains_all_phase_14_templates():
    templates = available_templates()

    for template in TEMPLATES:
        assert template in templates


@pytest.mark.parametrize("template", TEMPLATES)
def test_valid_template_detection(template):
    assert is_valid_template(template) is True


@pytest.mark.parametrize("template", ["missing", "professional", "ats", "foo"])
def test_unknown_template_is_rejected(template):
    assert is_valid_template(template) is False

    with pytest.raises(ValueError, match="Unknown resume template"):
        select_template(template)


@pytest.mark.parametrize("value", [123, 1.5, [], {}, True])
def test_non_string_template_is_rejected(value):
    assert is_valid_template(value) is False

    with pytest.raises(TypeError, match="Template name must be a string"):
        select_template(value)


def test_selection_returns_registered_configuration_not_a_new_template():
    selected = select_template("modern")
    registered = get_template("modern")

    assert selected is registered


def test_selection_preserves_template_configuration():
    selected = select_template("technical")

    assert selected.font_name == "Arial"
    assert selected.single_column is True
    assert selected.ats_safe is True


def test_selection_does_not_change_registered_template_list():
    before = list(available_templates())

    select_template("ats_clean")
    select_template("modern")
    select_template("technical")

    assert available_templates() == before
