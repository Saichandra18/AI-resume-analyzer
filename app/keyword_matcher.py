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

    text_parts.extend(resume_data.get("skills", []))

    education = resume_data.get("education", {})
    text_parts.extend(education.get("degrees", []))

    experience = resume_data.get("experience", {})
    text_parts.extend(experience.get("section", []))
    text_parts.extend(experience.get("job_titles", []))

    text_parts.extend(resume_data.get("projects", []))
    text_parts.extend(resume_data.get("certifications", []))

    for text in text_parts:
        if not text:
            continue

        normalized_text = normalize_keyword(text)

        if not normalized_text:
            continue

        words = normalized_text.split()

        keywords.update(words)

        if len(words) > 1:
            keywords.add(normalized_text)

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