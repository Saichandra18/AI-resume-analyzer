"""Configuration models for professional resume templates."""


class TemplateConfig:
    """Visual configuration for a resume template."""

    def __init__(
        self,
        name="default",
        display_name="Default",
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
    ):
        """Initialize template configuration."""

        self.name = name
        self.display_name = display_name

        self.font_name = font_name

        self.body_font_size = body_font_size
        self.heading_font_size = heading_font_size
        self.name_font_size = name_font_size
        self.contact_font_size = contact_font_size
        self.item_title_font_size = item_title_font_size
        self.secondary_font_size = secondary_font_size

        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.left_margin = left_margin
        self.right_margin = right_margin

        self.section_space_before = section_space_before
        self.section_space_after = section_space_after
        self.body_space_after = body_space_after

        self.line_spacing = line_spacing

        self.name_alignment = name_alignment
        self.contact_alignment = contact_alignment

        self.heading_bold = heading_bold
        self.name_bold = name_bold
        self.use_bullets = use_bullets
        self.single_column = single_column
        self.ats_safe = ats_safe

    def to_dict(self):
        """Return the configuration as a dictionary."""

        return {
            "name": self.name,
            "display_name": self.display_name,
            "font_name": self.font_name,
            "body_font_size": self.body_font_size,
            "heading_font_size": self.heading_font_size,
            "name_font_size": self.name_font_size,
            "contact_font_size": self.contact_font_size,
            "item_title_font_size": (
                self.item_title_font_size
            ),
            "secondary_font_size": (
                self.secondary_font_size
            ),
            "top_margin": self.top_margin,
            "bottom_margin": self.bottom_margin,
            "left_margin": self.left_margin,
            "right_margin": self.right_margin,
            "section_space_before": (
                self.section_space_before
            ),
            "section_space_after": (
                self.section_space_after
            ),
            "body_space_after": self.body_space_after,
            "line_spacing": self.line_spacing,
            "name_alignment": self.name_alignment,
            "contact_alignment": (
                self.contact_alignment
            ),
            "heading_bold": self.heading_bold,
            "name_bold": self.name_bold,
            "use_bullets": self.use_bullets,
            "single_column": self.single_column,
            "ats_safe": self.ats_safe,
        }

    @classmethod
    def from_dict(cls, data=None):
        """Create a configuration from a dictionary."""

        data = data or {}

        return cls(
            name=data.get("name", "default"),
            display_name=data.get(
                "display_name",
                "Default",
            ),
            font_name=data.get(
                "font_name",
                "Arial",
            ),
            body_font_size=data.get(
                "body_font_size",
                10,
            ),
            heading_font_size=data.get(
                "heading_font_size",
                12,
            ),
            name_font_size=data.get(
                "name_font_size",
                18,
            ),
            contact_font_size=data.get(
                "contact_font_size",
                9,
            ),
            item_title_font_size=data.get(
                "item_title_font_size",
                10.5,
            ),
            secondary_font_size=data.get(
                "secondary_font_size",
                9,
            ),
            top_margin=data.get(
                "top_margin",
                0.55,
            ),
            bottom_margin=data.get(
                "bottom_margin",
                0.55,
            ),
            left_margin=data.get(
                "left_margin",
                0.65,
            ),
            right_margin=data.get(
                "right_margin",
                0.65,
            ),
            section_space_before=data.get(
                "section_space_before",
                8,
            ),
            section_space_after=data.get(
                "section_space_after",
                3,
            ),
            body_space_after=data.get(
                "body_space_after",
                3,
            ),
            line_spacing=data.get(
                "line_spacing",
                1.0,
            ),
            name_alignment=data.get(
                "name_alignment",
                "center",
            ),
            contact_alignment=data.get(
                "contact_alignment",
                "center",
            ),
            heading_bold=data.get(
                "heading_bold",
                True,
            ),
            name_bold=data.get(
                "name_bold",
                True,
            ),
            use_bullets=data.get(
                "use_bullets",
                True,
            ),
            single_column=data.get(
                "single_column",
                True,
            ),
            ats_safe=data.get(
                "ats_safe",
                True,
            ),
        )


DEFAULT_TEMPLATE_CONFIG = TemplateConfig()
