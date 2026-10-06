"""Resume template configuration and rendering support."""

from app.templates.config import (
    DEFAULT_TEMPLATE_CONFIG,
    TemplateConfig,
)

__all__ = [
    "TemplateConfig",
    "DEFAULT_TEMPLATE_CONFIG",
]

from app.templates.config import (
    DEFAULT_TEMPLATE_CONFIG,
    TemplateConfig,
)
from app.templates.registry import (
    get_template,
    list_templates,
    register_template,
)

__all__ = [
    "TemplateConfig",
    "DEFAULT_TEMPLATE_CONFIG",
    "get_template",
    "list_templates",
    "register_template",
]