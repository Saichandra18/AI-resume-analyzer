import re

KEYWORD_ALIASES = {
    "ai": {
        "ai",
        "artificial intelligence",
    },
    "artificial intelligence": {
        "ai",
        "artificial intelligence",
    },

    "ml": {
        "ml",
        "machine learning",
    },
    "machine learning": {
        "ml",
        "machine learning",
    },

    "llm": {
        "llm",
        "llms",
        "large language model",
        "large language models",
    },
    "llms": {
        "llm",
        "llms",
        "large language model",
        "large language models",
    },
    "large language model": {
        "llm",
        "llms",
        "large language model",
        "large language models",
    },
    "large language models": {
        "llm",
        "llms",
        "large language model",
        "large language models",
    },

    "rag": {
        "rag",
        "retrieval augmented generation",
        "retrieval-augmented generation",
    },
    "retrieval augmented generation": {
        "rag",
        "retrieval augmented generation",
        "retrieval-augmented generation",
    },

    "ci cd": {
        "ci cd",
        "ci/cd",
        "continuous integration continuous delivery",
        "continuous integration and continuous delivery",
    },

    "genai": {
        "genai",
        "generative ai",
    },

    "generative ai": {
        "genai",
        "generative ai",
    },

    "neural network": {
        "neural network",
        "neural networks",
    },

    "neural networks": {
        "neural network",
        "neural networks",
    },
}

def normalize_keyword(keyword):
    """Normalize a keyword for comparison."""

    if not keyword:
        return ""

    keyword = keyword.strip().lower()

    keyword = re.sub(r"[^a-z0-9\s]", " ", keyword)

    return keyword.strip()


def extract_resume_keywords(resume_data):
    """Build searchable keywords from structured and raw resume data."""

    if not resume_data:
        return set()

    keywords = set()
    text_parts = []

    # Skills
    skills = resume_data.get("skills", [])

    if isinstance(skills, str):
        text_parts.append(skills)

    elif isinstance(skills, list):
        text_parts.extend(
            item for item in skills
            if isinstance(item, str)
        )

    # Education
    education = resume_data.get("education", {})

    # Legacy dictionary-based education structure.
    if isinstance(education, dict):
        degrees = education.get("degrees", [])

        if isinstance(degrees, str):
            text_parts.append(degrees)

        elif isinstance(degrees, list):
            text_parts.extend(
                item for item in degrees
                if isinstance(item, str)
            )

    # Current structured education-list format.
    elif isinstance(education, list):
        for education_item in education:
            if not isinstance(education_item, dict):
                continue

            for field in (
                "degree",
                "degree_name",
                "qualification",
                "name",
            ):
                value = education_item.get(field)

                if isinstance(value, str):
                    text_parts.append(value)

    # Experience
    experience = resume_data.get("experience", [])

    # Current structured experience-list format.
    if isinstance(experience, list):
        for experience_item in experience:
            if not isinstance(experience_item, dict):
                continue

            for field in (
                "job_title",
                "company",
                "location",
                "description",
                "summary",
                "responsibilities",
                "achievements",
                "dates",
            ):
                value = experience_item.get(field)

                if isinstance(value, str):
                    text_parts.append(value)

                elif isinstance(value, list):
                    text_parts.extend(
                        item for item in value
                        if isinstance(item, str)
                    )

    # Legacy dictionary-based experience structure.
    elif isinstance(experience, dict):
        for value in experience.values():
            if isinstance(value, str):
                text_parts.append(value)

            elif isinstance(value, list):
                text_parts.extend(
                    item for item in value
                    if isinstance(item, str)
                )

    # Projects
    projects = resume_data.get("projects", [])

    if isinstance(projects, list):
        for project in projects:
            if isinstance(project, dict):
                for value in project.values():
                    if isinstance(value, str):
                        text_parts.append(value)

                    elif isinstance(value, list):
                        text_parts.extend(
                            item for item in value
                            if isinstance(item, str)
                        )

            elif isinstance(project, str):
                text_parts.append(project)

    # Certifications
    certifications = resume_data.get("certifications", [])

    if isinstance(certifications, str):
        text_parts.append(certifications)

    elif isinstance(certifications, list):
        text_parts.extend(
            item for item in certifications
            if isinstance(item, str)
        )

    # Summary / profile / raw text fields
    for field in (
        "summary",
        "professional_summary",
        "profile",
        "objective",
        "raw_text",
        "text",
    ):
        value = resume_data.get(field)

        if isinstance(value, str):
            text_parts.append(value)

    # Build searchable keywords.
    #
    # We preserve BOTH:
    #   - individual words
    #   - normalized multi-word phrases
    #
    # Example:
    #   "Machine Learning"
    # becomes:
    #   "machine"
    #   "learning"
    #   "machine learning"
    #
    # "CI/CD"
    # becomes:
    #   "ci"
    #   "cd"
    #   "ci cd"
    for text in text_parts:
        if not isinstance(text, str):
            continue

        normalized = normalize_keyword(text)

        if not normalized:
            continue

        # Preserve the complete normalized phrase.
        keywords.add(normalized)

        # Also preserve individual tokens.
        keywords.update(
            token
            for token in normalized.split()
            if token
        )

    return keywords

def match_keywords(resume_data, job_keywords):
    """Compare job keywords against structured and raw resume data."""

    job_keywords = job_keywords or []
    resume_data = resume_data or {}

    resume_keywords = extract_resume_keywords(resume_data)

    raw_text = resume_data.get("raw_text", "")

    normalized_raw_text = normalize_keyword(raw_text)

    matched = []
    missing = []

    matched_normalized = set()
    missing_normalized = set()

    for keyword in job_keywords:
        normalized_keyword = normalize_keyword(keyword)

        if not normalized_keyword:
            continue

        aliases = KEYWORD_ALIASES.get(
            normalized_keyword,
            {normalized_keyword},
        )

        is_match = False

        for alias in aliases:
            normalized_alias = normalize_keyword(alias)

            # Check structured resume keywords.
            if normalized_alias in resume_keywords:
                is_match = True
                break

            # Check the actual resume text.
            if normalized_alias and normalized_alias in normalized_raw_text:
                is_match = True
                break

        if is_match:
            if normalized_keyword not in matched_normalized:
                matched.append(keyword)
                matched_normalized.add(normalized_keyword)

        else:
            if normalized_keyword not in missing_normalized:
                missing.append(keyword)
                missing_normalized.add(normalized_keyword)

    return {
        "matched": matched,
        "missing": missing,
    }