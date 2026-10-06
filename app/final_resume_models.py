"""Data models for the final JD-optimized resume."""

from copy import deepcopy


DEFAULT_SECTION_ORDER = [
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
]


class FinalResumeMetadata:
    """Metadata controlling final resume generation."""

    def __init__(
        self,
        target_pages=1,
        optimization_enabled=True,
        target_job_title=None,
    ):
        if not isinstance(target_pages, int) or target_pages < 1:
            raise ValueError(
                "target_pages must be a positive integer."
            )

        self.target_pages = target_pages
        self.optimization_enabled = bool(
            optimization_enabled
        )
        self.target_job_title = target_job_title

    def to_dict(self):
        """Return metadata as a dictionary."""

        return {
            "target_pages": self.target_pages,
            "optimization_enabled": self.optimization_enabled,
            "target_job_title": self.target_job_title,
        }

    @classmethod
    def from_dict(cls, data=None):
        """Create metadata from a dictionary."""

        data = data or {}

        return cls(
            target_pages=data.get("target_pages", 1),
            optimization_enabled=data.get(
                "optimization_enabled",
                True,
            ),
            target_job_title=data.get(
                "target_job_title"
            ),
        )


class FinalResume:
    """Canonical representation of the final resume."""

    def __init__(
        self,
        personal_info=None,
        summary="",
        skills=None,
        experience=None,
        projects=None,
        education=None,
        certifications=None,
        section_order=None,
        metadata=None,
    ):
        self.personal_info = deepcopy(
            personal_info or {}
        )
        self.summary = summary or ""
        self.skills = deepcopy(skills or [])
        self.experience = deepcopy(experience or [])
        self.projects = deepcopy(projects or [])
        self.education = deepcopy(education or [])
        self.certifications = deepcopy(
            certifications or []
        )

        self.section_order = list(
            section_order or DEFAULT_SECTION_ORDER
        )

        self.metadata = (
            metadata
            if isinstance(
                metadata,
                FinalResumeMetadata,
            )
            else FinalResumeMetadata.from_dict(metadata)
        )

        self._validate_section_order()

    def _validate_section_order(self):
        """Validate that section ordering is supported."""

        valid_sections = set(
            DEFAULT_SECTION_ORDER
        )

        if len(self.section_order) != len(
            set(self.section_order)
        ):
            raise ValueError(
                "section_order cannot contain duplicates."
            )

        unknown_sections = set(
            self.section_order
        ) - valid_sections

        if unknown_sections:
            raise ValueError(
                "Unknown resume sections: "
                + ", ".join(
                    sorted(unknown_sections)
                )
            )

    def to_dict(self):
        """Return a serialized representation."""

        return {
            "personal_info": deepcopy(
                self.personal_info
            ),
            "summary": self.summary,
            "skills": deepcopy(self.skills),
            "experience": deepcopy(self.experience),
            "projects": deepcopy(self.projects),
            "education": deepcopy(self.education),
            "certifications": deepcopy(
                self.certifications
            ),
            "section_order": list(
                self.section_order
            ),
            "metadata": self.metadata.to_dict(),
        }

    @classmethod
    def from_dict(cls, data=None):
        """Create a FinalResume from a dictionary."""

        data = data or {}

        return cls(
            personal_info=data.get(
                "personal_info",
                {},
            ),
            summary=data.get(
                "summary",
                "",
            ),
            skills=data.get(
                "skills",
                [],
            ),
            experience=data.get(
                "experience",
                [],
            ),
            projects=data.get(
                "projects",
                [],
            ),
            education=data.get(
                "education",
                [],
            ),
            certifications=data.get(
                "certifications",
                [],
            ),
            section_order=data.get(
                "section_order",
                DEFAULT_SECTION_ORDER,
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )


def build_final_resume(
    personal_info=None,
    summary="",
    skills=None,
    experience=None,
    projects=None,
    education=None,
    certifications=None,
    section_order=None,
    metadata=None,
):
    """Build a canonical final resume."""

    return FinalResume(
        personal_info=personal_info,
        summary=summary,
        skills=skills,
        experience=experience,
        projects=projects,
        education=education,
        certifications=certifications,
        section_order=section_order,
        metadata=metadata,
    )