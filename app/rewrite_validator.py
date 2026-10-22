import re


def _normalize_text(text):
    """Normalize text for simple comparison."""
    if not text:
        return ""

    return re.sub(r"\s+", " ", str(text).strip().lower())


def _extract_numbers(text):
    """Extract numeric values and percentages from text."""
    return set(
        re.findall(
            r"\b\d+(?:\.\d+)?%|\b\d+(?:\.\d+)?\b",
            str(text or ""),
        )
    )


def _extract_technical_terms(text):
    """Extract common technical terms from text."""

    technical_terms = {
        "python",
        "java",
        "javascript",
        "typescript",
        "c",
        "c++",
        "c#",
        "sql",
        "html",
        "css",
        "flask",
        "django",
        "fastapi",
        "react",
        "angular",
        "vue",
        "node.js",
        "nodejs",
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "pandas",
        "numpy",
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "git",
        "github",
        "mongodb",
        "mysql",
        "postgresql",
        "postgres",
        "pyspark",
        "xgboost",
        "lightgbm",
        "catboost",
        "langchain",
        "llamaindex",
        "llama-index",
        "hugging face",
        "transformers",
        "openai",
        "ollama",
        "mlflow",
        "airflow",
        "spark",
        "hadoop",
        "scipy",
        "matplotlib",
        "seaborn",
        "streamlit",
        "gradio",
        "jupyter",
        "rest api",
        "graphql",
        "redis",
        "elasticsearch",
        "firebase",
        "supabase",
        "gitlab",
        "bitbucket",
        "jenkins",
        "github actions",
        "terraform",
        "pipeline",
        "pipelines",
        "deployment",
        "deployments",
        "production environment",
        "production environments",
    }

    normalized = _normalize_text(text)

    return {
        term
        for term in technical_terms
        if re.search(
            rf"(?<!\w){re.escape(term)}(?!\w)",
            normalized,
        )
    }


def _extract_dynamic_technical_terms(text):
    """Extract likely technical terms not covered by the known dictionary."""
    raw_text = str(text or "")
    normalized = _normalize_text(raw_text)

    terms = set()

    # Detect version-like / compound technical names:
    # e.g. vector-db, node.js, model_v2, api2
    terms.update(
        re.findall(
            r"\b[a-z][a-z0-9]*(?:[._][a-z0-9]+)+\b"
            r"|\b[a-z]+[0-9][a-z0-9]*\b",
            normalized,
        )
    )

    # Detect CamelCase / PascalCase technical names:
    # e.g. VectorDBX, FastAPI, LangChainX
    camel_case_terms = re.findall(
        r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+\b",
        raw_text,
    )

    terms.update(_normalize_text(term) for term in camel_case_terms)

    stop_words = {
        "version1",
        "section1",
        "project1",
        "experience1",
    }

    return {
        term
        for term in terms
        if term not in stop_words
    }
def _extract_all_technical_terms(text):
    """Extract known and dynamically detected technical terms."""

    return (
        _extract_technical_terms(text)
        | _extract_dynamic_technical_terms(text)
    )

def _detect_unsupported_claim_strengthening(
    original, rewritten, evidence_text=""
):
    """Detect stronger performance claims not supported by original or evidence."""
    original_text = _normalize_text(original)
    rewritten_text = _normalize_text(rewritten)
    evidence_text = _normalize_text(evidence_text)

    strengthening_terms = {
        "exceeded",
        "outperformed",
        "surpassed",
        "maximized",
        "optimized",
        "improved",
        "increased",
        "reduced",
        "accelerated",
        "achieved",
        "delivered",
        "led",
        "drove",
        "maintained",
        "implemented",
        "managed",
        "deployed",
        "automated",
        "designed",
        "architected",
    }
    strengthening_phrases = {
        "consistently met",
        "consistently achieved",
        "successfully delivered",
        "reliably achieved",
        "reliably maintained",
        "consistently maintained",
        "effectively improved",
    }

    original_strength_terms = {
        term
        for term in strengthening_terms
        if re.search(rf"\b{re.escape(term)}\b", original_text)
    }

    rewritten_strength_terms = {
        term
        for term in strengthening_terms
        if re.search(rf"\b{re.escape(term)}\b", rewritten_text)
    }

    evidence_strength_terms = {
        term
        for term in strengthening_terms
        if re.search(rf"\b{re.escape(term)}\b", evidence_text)
    }

    new_strength_terms = (
        rewritten_strength_terms
        - original_strength_terms
        - evidence_strength_terms
    )
    original_strength_phrases = {
        phrase
        for phrase in strengthening_phrases
        if phrase in original_text
    }

    rewritten_strength_phrases = {
        phrase
        for phrase in strengthening_phrases
        if phrase in rewritten_text
    }

    evidence_strength_phrases = {
        phrase
        for phrase in strengthening_phrases
        if phrase in evidence_text
    }

    new_strength_phrases = (
        rewritten_strength_phrases
        - original_strength_phrases
        - evidence_strength_phrases
    )

    return sorted(
        list(new_strength_terms) + list(new_strength_phrases)
    )

    
def validate_rewrite(original, rewritten, evidence_text=""):
    """Validate a rewritten resume item against its original text."""

    original_text = _normalize_text(original)
    rewritten_text = _normalize_text(rewritten)
    evidence = _normalize_text(evidence_text)

    if not original_text or not rewritten_text:
        return {
            "meaning_preserved": False,
            "unsupported_claims": [
                "Original or rewritten text is empty."
            ],
            "grounding_status": "needs_review",
        }

    unsupported_claims = []

    new_strength_terms = _detect_unsupported_claim_strengthening(
        original_text,
        rewritten_text,
        evidence_text,
    )
    for term in new_strength_terms:
        unsupported_claims.append(
            f"Unsupported claim strengthening detected: {term}"
        )

    # ---------------------------------------------------------
    # Numeric claim validation
    # ---------------------------------------------------------

    original_numbers = _extract_numbers(original_text)
    rewritten_numbers = _extract_numbers(rewritten_text)
    evidence_numbers = _extract_numbers(evidence)

    new_numbers = (
        rewritten_numbers
        - original_numbers
        - evidence_numbers
    )

    for number in sorted(new_numbers):
        unsupported_claims.append(
            f"New numeric claim detected: {number}"
        )

    # ---------------------------------------------------------
    # Technical term validation
    # ---------------------------------------------------------

    original_terms = _extract_all_technical_terms(
        original
    )

    rewritten_terms = _extract_all_technical_terms(
        rewritten
    )

    evidence_terms = _extract_all_technical_terms(
        evidence_text
    )

    new_terms = (
        rewritten_terms
        - original_terms
        - evidence_terms
    )

    for term in sorted(new_terms):
        unsupported_claims.append(
            f"New technical term detected: {term}"
        )

    # ---------------------------------------------------------
    # Final validation result
    # ---------------------------------------------------------

    if unsupported_claims:
        return {
            "meaning_preserved": False,
            "unsupported_claims": unsupported_claims,
            "grounding_status": "needs_review",
        }

    return {
        "meaning_preserved": True,
        "unsupported_claims": [],
        "grounding_status": "grounded",
    }