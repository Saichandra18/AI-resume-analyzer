"""Build deterministic candidate context for RAG optimization."""

from copy import deepcopy


class ResumeContextBuilder:
    """Build grounded, deterministic context from resume data."""

    SECTION_FIELDS = (
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications",
    )

    def build(self, resume_data):
        """Build normalized candidate context from resume data."""

        if resume_data is None:
            return {
                "summary": "",
                "skills": [],
                "experience": [],
                "projects": [],
                "education": [],
                "certifications": [],
            }

        if not isinstance(resume_data, dict):
            raise TypeError(
                "resume_data must be a dictionary."
            )

        context = {}

        for field in self.SECTION_FIELDS:
            value = resume_data.get(field)

            if field == "summary":
                context[field] = self._normalize_text(
                    value
                )
            else:
                context[field] = self._normalize_collection(
                    value
                )

        return context

    @staticmethod
    def _normalize_text(value):
        """Normalize a scalar text value."""

        if value is None:
            return ""

        if isinstance(value, (list, tuple, set)):
            value = " ".join(
                str(item)
                for item in value
                if item is not None
            )

        return " ".join(
            str(value).split()
        ).strip()

    @classmethod
    def _normalize_collection(cls, value):
        """Normalize a resume collection without mutating input."""

        if value is None:
            return []

        if not isinstance(
            value,
            (list, tuple, set),
        ):
            value = [value]

        normalized = []

        for item in value:
            if isinstance(item, dict):
                normalized.append(
                    deepcopy(item)
                )
                continue

            text = cls._normalize_text(item)

            if text:
                normalized.append(text)

        return normalized

    def to_query_text(self, context):
        """Convert candidate context into deterministic query text."""

        if not isinstance(context, dict):
            raise TypeError(
                "context must be a dictionary."
            )

        parts = []

        summary = context.get(
            "summary",
            "",
        )

        if summary:
            parts.append(summary)

        for field in (
            "skills",
            "experience",
            "projects",
            "education",
            "certifications",
        ):
            values = context.get(
                field,
                [],
            )

            if not isinstance(
                values,
                (list, tuple),
            ):
                values = [values]

            for value in values:
                if isinstance(value, dict):
                    parts.extend(
                        self._flatten_dict_text(
                            value
                        )
                    )
                else:
                    text = self._normalize_text(
                        value
                    )

                    if text:
                        parts.append(text)

        return " ".join(parts).strip()

    @classmethod
    def _flatten_dict_text(cls, value):
        """Extract deterministic text from a structured resume item."""

        parts = []

        for key in sorted(value):
            item = value[key]

            if isinstance(
                item,
                (list, tuple, set),
            ):
                for entry in item:
                    text = cls._normalize_text(
                        entry
                    )

                    if text:
                        parts.append(text)

            elif isinstance(item, dict):
                parts.extend(
                    cls._flatten_dict_text(
                        item
                    )
                )

            else:
                text = cls._normalize_text(
                    item
                )

                if text:
                    parts.append(text)

        return parts