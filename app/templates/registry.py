"""Registry for resume template configurations."""

from app.templates.config import (
    DEFAULT_TEMPLATE_CONFIG,
    TemplateConfig,
)


_TEMPLATE_REGISTRY = {
    DEFAULT_TEMPLATE_CONFIG.name: DEFAULT_TEMPLATE_CONFIG,
}


ATS_CLEAN_TEMPLATE = TemplateConfig(
    name="ats_clean",
    display_name="ATS Clean",
    font_name="Arial",
    body_font_size=10,
    heading_font_size=12,
    name_font_size=18,
    contact_font_size=9,
    item_title_font_size=10.5,
    secondary_font_size=9,
    top_margin=0.55,
    bottom_margin=0.55,
    left_margin=0.65,
    right_margin=0.65,
    section_space_before=8,
    section_space_after=3,
    body_space_after=3,
    line_spacing=1.0,
    name_alignment="center",
    contact_alignment="center",
    heading_bold=True,
    name_bold=True,
    use_bullets=True,
    single_column=True,
    ats_safe=True,
)




_TEMPLATE_REGISTRY[ATS_CLEAN_TEMPLATE.name] = ATS_CLEAN_TEMPLATE

MODERN_TEMPLATE = TemplateConfig(
    name="modern",
    display_name="Modern Professional",
    font_name="Aptos",
    body_font_size=10,
    heading_font_size=13,
    name_font_size=20,
    contact_font_size=9,
    item_title_font_size=11,
    secondary_font_size=9,
    top_margin=0.60,
    bottom_margin=0.60,
    left_margin=0.70,
    right_margin=0.70,
    section_space_before=9,
    section_space_after=4,
    body_space_after=3,
    line_spacing=1.05,
    name_alignment="left",
    contact_alignment="left",
    heading_bold=True,
    name_bold=True,
    use_bullets=True,
    single_column=True,
    ats_safe=True,
)

_TEMPLATE_REGISTRY[MODERN_TEMPLATE.name] = MODERN_TEMPLATE

_TEMPLATE_REGISTRY["modern_professional"] = MODERN_TEMPLATE

TECHNICAL_TEMPLATE = TemplateConfig(
    name="technical",
    display_name="Compact Technical",
    font_name="Arial",
    body_font_size=9.5,
    heading_font_size=11.5,
    name_font_size=17,
    contact_font_size=8.5,
    item_title_font_size=10,
    secondary_font_size=8.5,
    top_margin=0.45,
    bottom_margin=0.45,
    left_margin=0.55,
    right_margin=0.55,
    section_space_before=6,
    section_space_after=2,
    body_space_after=2,
    line_spacing=1.0,
    name_alignment="left",
    contact_alignment="left",
    heading_bold=True,
    name_bold=True,
    use_bullets=True,
    single_column=True,
    ats_safe=True,
)

_TEMPLATE_REGISTRY[TECHNICAL_TEMPLATE.name] = TECHNICAL_TEMPLATE

_TEMPLATE_REGISTRY["compact_technical"] = TECHNICAL_TEMPLATE

def get_template(name="default"):
    """Return a registered template configuration by name."""

    if not isinstance(name, str):
        raise TypeError("Template name must be a string.")

    template = _TEMPLATE_REGISTRY.get(name)

    if template is None:
        raise ValueError(f"Unknown resume template: {name}")

    return template


def list_templates():
    """Return the names of all registered templates."""

    return list(_TEMPLATE_REGISTRY.keys())


def register_template(template):
    """Register a resume template configuration."""

    if not isinstance(template, TemplateConfig):
        raise TypeError(
            "template must be a TemplateConfig instance."
        )

    if template.name in _TEMPLATE_REGISTRY:
        raise ValueError(
            f"Template already registered: {template.name}"
        )

    _TEMPLATE_REGISTRY[template.name] = template