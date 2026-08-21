import re


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "have",
    "has",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "with",
    "will",
    "you",
    "your",
}


GENERIC_WORDS = {
    "candidate",
    "should",
    "experience",
    "working",
    "teams",
    "ensure",
    "good",
    "quality",
    "provide",
    "support",
    "various",
    "projects",
    "position",
    "based",
    "minimum",
    "years",
    "year",
    "required",
    "role",
    "responsibilities",
    "responsibility",
    "including",
    "ability",
    "strong",
    "professional",
    "development",
    "develop",
    "develops",
    "applications",
    "application",
    "systems",
    "tools",
    "services",
    "use",
    "using",
    "need",
    "needs",
    "must",
    "able",
    "also",
    "part",
    "our",
    "job",
    "description",
    "project",
    "projects",
    "time",
    "full",
    "education",
    "educational",
    "qualification",
    "qualifications",
    "summary",
    "day",
    "typical",
    "involve",
    "involves",
    "ensure",
    "ensuring",
    "various",
    "aspects",
    "functionality",
    "roles",
    "continuously",
    "existing",
    "efficiency",
    "multiple",
    "contribute",
    "key",
    "decisions",
    "problems",
    "immediate",
    "team",
    "across",
    "facilitate",
    "knowledge",
    "sharing",
    "sessions",
    "capabilities",
    "monitor",
    "progress",
    "alignment",
    "goals",
    "technical",
    "design",
    "build",
    "maintain",
    "work",
    "manage",
    "management",
    "well",
    "workflows",
    "automate",
    "testing",
    "safe",
    "efficient",
    "security",
    "compliance",
    "ethical",
    "governance",
    "stay",
    "updated",
    "advances",
    "need",
    "additional",
    "candidate",
    "position",
    "office",
}


MULTI_WORD_KEYWORDS = {
    "data analyst",
    "data scientist",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "generative ai",
    "generative artificial intelligence",
    "natural language processing",
    "computer vision",
    "neural networks",
    "neural network",
    "retrieval augmented generation",
    "large language model",
    "large language models",
    "prompt engineering",
    "model evaluation",
    "model deployment",
    "model validation",
    "model monitoring",
    "performance optimization",
    "data pipelines",
    "data pipeline",
    "software engineering",
    "cloud infrastructure",
    "cloud services",
    "continuous integration",
    "continuous deployment",
    "ci cd",
    "machine learning operations",
    "machine learning operations",
    "llm operations",
    "llmops",
    "power bi",
}


TECHNICAL_TERMS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "cpp",
    "csharp",
    "sql",
    "r",
    "go",
    "rust",
    "scala",
    "kotlin",
    "swift",
    "pandas",
    "numpy",
    "scipy",
    "tensorflow",
    "pytorch",
    "keras",
    "scikit",
    "sklearn",
    "opencv",
    "spark",
    "hadoop",
    "airflow",
    "docker",
    "kubernetes",
    "jenkins",
    "git",
    "github",
    "gitlab",
    "aws",
    "azure",
    "gcp",
    "linux",
    "flask",
    "django",
    "fastapi",
    "react",
    "node",
    "nodejs",
    "langchain",
    "huggingface",
    "hugging",
    "transformers",
    "openai",
    "llm",
    "llms",
    "rag",
    "ragas",
    "llmops",
    "mlops",
    "genai",
    "ai",
    "ml",
    "ci",
    "cd",
    "powerbi",
    "tableau",
}


def _normalize_text(text):
    """Normalize text while preserving technical phrases."""

    text = text.lower()

    text = text.replace("-", " ")

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    return re.sub(r"\s+", " ", text).strip()


def extract_job_keywords(job_description):
    """Extract meaningful ATS keywords from a job description."""

    if not job_description:
        return []

    text = _normalize_text(job_description)

    keywords = []

    # Detect multi-word concepts first.
    for phrase in sorted(
        MULTI_WORD_KEYWORDS,
        key=len,
        reverse=True,
    ):
        if phrase in text and phrase not in keywords:
            keywords.append(phrase)

    # Detect meaningful technical terms.
    words = text.split()

    for word in words:
        if not word:
            continue

        if word in STOP_WORDS:
            continue

        if word in GENERIC_WORDS:
            continue

        if word.isdigit():
            continue

        if word in TECHNICAL_TERMS and word not in keywords:
            keywords.append(word)

    return keywords