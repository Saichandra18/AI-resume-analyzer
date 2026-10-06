"""Template selection helpers for resume generation."""

from app.templates.registry import get_template, list_templates


DEFAULT_TEMPLATE_NAME = "default"


def normalize_template_name(template=None):
    """Normalize a user-selected template name.

    None or an empty/whitespace-only value resolves to the default template.
    Template names are case-insensitive and surrounding whitespace is ignored.
    """
    if template is None:
        return DEFAULT_TEMPLATE_NAME

    if not isinstance(template, str):
        raise TypeError("Template name must be a string or None.")

    normalized = template.strip().lower()

    if not normalized:
        return DEFAULT_TEMPLATE_NAME

    return normalized


def select_template(template=None):
    """Resolve a template selection to its registered TemplateConfig."""
    name = normalize_template_name(template)
    return get_template(name)


def available_templates():
    """Return the names of all registered templates."""
    return list_templates()


def is_valid_template(template=None):
    """Return True when the supplied selection resolves to a registered template."""
    try:
        select_template(template)
    except (TypeError, ValueError):
        return False

    return True
