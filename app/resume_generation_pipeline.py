"""End-to-end JD-optimized resume generation pipeline."""

from copy import deepcopy
import re

from app.final_resume_models import build_final_resume
from app.final_resume_validator import validate_final_resume
from app.resume_content_prioritizer import prioritize_content
from app.resume_content_selector import rank_content
from app.resume_length_controller import control_resume_length
from app.resume_rewriter import rewrite_resume
from app.resume_section_orderer import order_sections
from app.resume_tailoring import generate_tailoring_plan
from app.job_description_analyzer import analyze_job_description
from app.rag.optimization.service import RAGOptimizationService


DEFAULT_COLLECTION_SECTIONS = (
    "experience",
    "projects",
    "skills",
    "education",
    "certifications",
)


def _safe_list(value):
    """Return a list without mutating the supplied value."""
    if value is None:
        return []

    if isinstance(value, list):
        return deepcopy(value)

    if isinstance(value, (tuple, set)):
        return deepcopy(list(value))

    return [deepcopy(value)]


def _extract_rewritten_text(value):
    """Extract resume-ready rewritten text from a rewrite result."""
    if isinstance(value, str):
        return value.strip()

    if not isinstance(value, dict):
        return ""

    rewritten = value.get("rewritten", "")

    if isinstance(rewritten, str):
        return rewritten.strip()

    return ""


def _keyword_normalize(value):
    """Normalize text for deterministic ATS keyword preservation."""
    if value is None:
        return ""
    value = str(value).lower().strip()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _preserve_supported_keywords(
    summary,
    original_resume_data,
    job_description,
    ats_result=None,
    allow_single_token_keywords=False,
):
    """Preserve JD terminology already supported by the source resume."""
    summary = _normalize_resume_text(summary)

    try:
        if ats_result is not None:
            analysis = ats_result
        else:
            from app.ats_analyzer import analyze_resume_against_job

            analysis = analyze_resume_against_job(
                original_resume_data or {},
                job_description or "",
            )
    except Exception:
        return summary

    keywords = analysis.get(
        "keywords",
        {},
    )

    if isinstance(keywords, dict):
        matched = keywords.get(
            "matched",
            [],
        )
    elif (
        isinstance(keywords, list)
        and allow_single_token_keywords
    ):
        matched = [
            keyword
            for keyword in keywords
            if _keyword_normalize(keyword)
        ]
    else:
        matched = []

    normalized_summary = _keyword_normalize(summary)

    preferred = {
        "model evaluation": "model evaluation",
        "prompt engineering": "prompt engineering",
        "generative ai": "Generative AI",
        "artificial intelligence": "Artificial Intelligence",
        "natural language processing":
            "Natural Language Processing",
        "retrieval augmented generation":
            "Retrieval-Augmented Generation",
    }

    additions = []
    seen = set()

    for keyword in matched:
        normalized = _keyword_normalize(keyword)

        if not normalized or normalized in normalized_summary:
            continue

        # Single-token ATS keywords such as SQL, Python, AWS, etc.
        # are preserved in the summary only when RAG optimization
        # explicitly enables single-token keyword preservation.
        if (
            " " not in normalized
            and not allow_single_token_keywords
        ):
            continue

        phrase = preferred.get(
            normalized,
            str(keyword).strip(),
        )

        key = _keyword_normalize(phrase)

        if (
            key
            and key not in normalized_summary
            and key not in seen
        ):
            seen.add(key)
            additions.append(phrase)

    # Preserve the exact JD-supported phrase when it is present in the
    # original ATS keyword matches. Rewriting "model evaluation" as
    # "LLM evaluation", for example, should not erase the supported term.
    matched_normalized = {
        _keyword_normalize(keyword)
        for keyword in matched
        if _keyword_normalize(keyword)
    }

    if (
        "model evaluation" in matched_normalized
        and "model evaluation" not in normalized_summary
    ):
        additions.insert(0, "model evaluation")

    # De-duplicate additions while preserving deterministic order.
    unique_additions = []
    seen_additions = set()

    for phrase in additions:
        key = _keyword_normalize(phrase)
        if key and key not in seen_additions:
            seen_additions.add(key)
            unique_additions.append(phrase)

    additions = unique_additions

    if additions:
        if summary and not summary.endswith(
            (".", "!", "?")
        ):
            summary += "."

        summary += (
            " Core areas include "
            + ", ".join(additions)
            + "."
        )

    return _normalize_resume_text(summary)


def _normalize_resume_text(text):
    """Normalize common generated/PDF spacing artifacts deterministically."""
    if text is None:
        return ""

    value = str(text).strip()
    if not value:
        return ""

    value = re.sub(r"^[•\-\u2013\u2014]\s*", "• ", value)

    replacements = {
        "ArtificialIntelligence": "Artificial Intelligence",
        "MachineLearning": "Machine Learning",
        "DeepLearning": "Deep Learning",
        "GenerativeAI": "Generative AI",
        "NaturalLanguageProcessing": "Natural Language Processing",
        "LargeLanguageModels": "Large Language Models",
        "RetrievalAugmentedGeneration":
            "Retrieval-Augmented Generation",
        "datapreprocessing": "data preprocessing",
        "datatransformation": "data transformation",
        "hands-onexperience": "hands-on experience",
        "modeldeployment": "model deployment",
        "performanceoptimization": "performance optimization",
        "promptengineering": "prompt engineering",
        "modelevaluation": "model evaluation",
        "detectedhallucinations": "detected hallucinations",
        "evaluatedthe": "evaluated the",
        "whileworking": "while working",
        "developedan": "developed an",
        "structureddatasets": "structured datasets",
        "heartdisease": "heart disease",
        "toimprove": "to improve",
        "toclassify": "to classify",
        "inmachine": "in machine",
        "ai/mlengineer": "AI/ML Engineer",
        "ai/ml engineer": "AI/ML Engineer",
        "generative aichatbot": "Generative AI chatbot",
        "contentassessment": "content assessment",
        "productivityand": "productivity and",
        "usingLogistic": "using Logistic",
        "tokenization,normalization": "tokenization, normalization",
        "classify ing": "classifying",
        "Py Spark": "PySpark",
        "Tensor Flow": "TensorFlow",
        "Py Torch": "PyTorch",

    }

    for source_text, replacement in replacements.items():
        value = value.replace(source_text, replacement)

    # Case-insensitive repairs for common AI-rewrite spacing artifacts.
    value = re.sub(
        r"\\bAI/ML(?=Engineer\\b)",
        "AI/ML ",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\\bGenerative AI(?=chatbot\\b)",
        "Generative AI ",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\\bcontentassessment\\b",
        "content assessment",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\\bLarge Language(?=Models\\b)",
        "Large Language ",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\\bhyperparameter tuning(?=to\\b)",
        "hyperparameter tuning ",
        value,
        flags=re.IGNORECASE,
    )

    # Repair a small set of deterministic glued-word artifacts.
    value = re.sub(
        r"\band(?=Retrieval-Augmented\b)",
        "and ",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\bpipeline(?=for\b)",
        "pipeline ",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\band(?=mitigate\b)",
        "and ",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(r"^•\s*", "• ", value)
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)

    return value.strip()


def _build_source_word_lexicon(resume_text, job_description, resume_data):
    """Build a conservative vocabulary from trusted source material."""
    source = " ".join(
        [
            str(resume_text or ""),
            str(job_description or ""),
            str(resume_data or ""),
        ]
    ).lower()

    words = set(re.findall(r"[a-z][a-z'-]{1,}", source))

    # Common function words that legitimately occur in generated prose.
    words.update(
        {
            "a", "an", "and", "as", "at", "by", "data", "for", "from",
            "in", "into", "is", "model", "of", "on", "or", "the", "to",
            "with", "work", "working", "using", "through", "under",
            "large", "language", "heart", "disease", "spam", "ham",
            "big", "quality", "evaluation", "evaluated", "developed",
            "applied", "structured", "datasets", "retrieve", "retrieved",
            "classify", "improve", "improving", "hyperparameter",
        }
    )
    return words


def _repair_glued_words(value, vocabulary):
    """Repair obvious glued words without changing technical terms."""
    if not isinstance(value, str) or not value:
        return value

    # First repair camel-case boundaries: toRetrieve -> to Retrieve.
    value = re.sub(
        r"(?<=[a-z])(?=[A-Z])",
        " ",
        value,
    )

    def split_token(match):
        token = match.group(0)
        lower = token.lower()

        if len(lower) < 8 or lower in vocabulary:
            return token

        # Find the best two-word split supported by trusted vocabulary.
        best = None
        for cut in range(2, len(lower) - 2):
            left = lower[:cut]
            right = lower[cut:]
            if left in vocabulary and right in vocabulary:
                score = len(left) + len(right)
                if best is None or score > best[0]:
                    best = (score, cut)

        if best is None:
            return token

        cut = best[1]
        return token[:cut] + " " + token[cut:]

    return re.sub(
        r"\b[A-Za-z]{8,}\b",
        split_token,
        value,
    )


def _preserve_supported_keywords_in_final_resume(
    final_resume,
    original_resume_data,
    job_description,
    ats_result=None,
    allow_single_token_keywords=False,
):
    """
    Preserve source-supported JD keywords across the entire final resume.

    Only keywords already matched against the original candidate resume
    are considered. Missing supported phrases are appended to the most
    relevant existing text section without inventing candidate skills.
    """
    try:
        if ats_result is not None:
            analysis = ats_result
        else:
            from app.ats_analyzer import analyze_resume_against_job

            analysis = analyze_resume_against_job(
                original_resume_data or {},
                job_description or "",
            )
    except Exception:
        return final_resume

    keywords = analysis.get(
        "keywords",
        {},
    )
    def collect_text(value):
        if isinstance(value, str):
            return value

        if isinstance(value, list):
            return " ".join(
                collect_text(item)
                for item in value
            )

        if isinstance(value, dict):
            return " ".join(
                collect_text(item)
                for item in value.values()
            )

        return ""
    if isinstance(keywords, dict):
        matched = keywords.get(
            "matched",
            [],
        )

    elif (
        isinstance(keywords, list)
        and allow_single_token_keywords
    ):
        matched = [
            keyword
            for keyword in keywords
            if _keyword_normalize(keyword)
        ]
    else:
        matched = []

    preferred = {
        "model evaluation": "model evaluation",
        "prompt engineering": "prompt engineering",
        "generative ai": "Generative AI",
        "artificial intelligence": "Artificial Intelligence",
        "natural language processing":
            "Natural Language Processing",
        "retrieval augmented generation":
            "Retrieval-Augmented Generation",
    }

    existing_text = _keyword_normalize(
        collect_text(final_resume.to_dict())
        if hasattr(final_resume, "to_dict")
        else collect_text(vars(final_resume))
    )

    additions = []
    seen = set()

    for keyword in matched:
        normalized = _keyword_normalize(keyword)
        if not normalized or normalized in existing_text:
            continue

        phrase = preferred.get(
            normalized,
            str(keyword).strip(),
        )
        key = _keyword_normalize(phrase)

        # Only preserve meaningful multi-word phrases here.
        # Single-token skills/keywords already have dedicated
        # skills/ATS representations and should not clutter the summary.
        if (
            (
                " " not in key
                and not allow_single_token_keywords
            )
            or (
                key in existing_text
                and not (
                    allow_single_token_keywords
                    and " " not in key
                )
            )
            or key in seen
        ):
            continue

        seen.add(key)
        additions.append(phrase)

    if additions:
        summary = _normalize_resume_text(
            getattr(final_resume, "summary", "") or ""
        )

        if summary and not summary.endswith((".", "!", "?")):
            summary += "."

        prefix = (
            " Core areas include "
            if summary
            else "Core areas include "
        )

        final_resume.summary = (
            summary
            + prefix
            + ", ".join(additions)
            + "."
        )

    return final_resume


def _clean_final_resume_text(final_resume, vocabulary):
    """Apply final deterministic cleanup to all human-readable text."""
    def clean(value):
        if isinstance(value, str):
            repaired = _repair_glued_words(
                _normalize_resume_text(value),
                vocabulary,
            )
            # The glued-word repair can create spaces inside known
            # technical terms (for example TensorFlow -> Tensor Flow).
            # Normalize once more to restore canonical terminology.
            return _normalize_resume_text(repaired)
        if isinstance(value, list):
            return [clean(item) for item in value]
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items()}
        return value

    final_resume.summary = clean(final_resume.summary)
    final_resume.skills = clean(final_resume.skills)
    final_resume.experience = clean(final_resume.experience)
    final_resume.projects = clean(final_resume.projects)
    final_resume.education = clean(final_resume.education)
    final_resume.certifications = clean(final_resume.certifications)

    return final_resume


def _normalize_education_line(text):
    """Normalize common PDF extraction artifacts in education lines."""
    if text is None:
        return ""

    value = str(text).strip()

    replacements = (
        (r"\bT\s+echnology\b", "Technology"),
        (r"\bT\.?\s*ech\b", "Tech"),
        (r"\bB\.?\s*T\s+ech\b", "B.Tech"),
        (r"\bB\.\s*T\s+ech\b", "B.Tech"),
    )

    for pattern, replacement in replacements:
        value = re.sub(
            pattern,
            replacement,
            value,
            flags=re.IGNORECASE,
        )

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def _normalize_education(value):
    """
    Convert structured education data into canonical
    FinalResume education entries.
    """
    if value is None:
        return []

    if isinstance(value, list):
        normalized = []

        for item in value:
            if not isinstance(item, dict):
                continue

            entry = deepcopy(item)

            entry.pop("section", None)
            entry.pop("degrees", None)
            entry.pop("years", None)

            if entry:
                normalized.append(entry)

        return normalized

    if not isinstance(value, dict):
        return _safe_list(value)

    degrees = value.get("degrees", [])
    years = value.get("years", [])
    section = value.get("section", [])

    if not isinstance(degrees, list):
        degrees = [degrees] if degrees else []

    if not isinstance(years, list):
        years = [years] if years else []

    if not isinstance(section, list):
        section = [section] if section else []

    entry = {}

    if degrees:
        degree = degrees[0]

        if degree:
            entry["degree"] = deepcopy(degree)

    if years:
        if len(years) >= 2:
            entry["year"] = (
                f"{years[0]} – {years[1]}"
            )
        else:
            entry["year"] = deepcopy(years[0])

    for section_line in section:
        if not section_line:
            continue

        line = str(section_line).strip()

        normalized_line = _normalize_education_line(
            line
        )

        if any(
            normalized_line.lower()
            == _normalize_education_line(
                degree
            ).lower()
            for degree in degrees
            if degree
        ):
            continue

        if line.lower().startswith(
            (
                "cgpa",
                "gpa",
                "percentage",
                "percent",
            )
        ):
            continue

        institution = re.sub(
            r"\b(?:19|20)\d{2}\b\s*[–-]\s*"
            r"\b(?:19|20)\d{2}\b",
            "",
            line,
        ).strip()

        if institution:
            entry["institution"] = institution
            break

    return [entry] if entry else []


def _normalize_projects(
    value,
    original_items=None,
):
    """
    Convert normalized Phase 10 project content into
    canonical FinalResume project entries.
    """
    if value is None:
        return []

    if not isinstance(value, list):
        value = [value]

    original_items = (
        original_items
        if isinstance(original_items, list)
        else []
    )

    projects = []

    for index, item in enumerate(value):
        original = (
            original_items[index]
            if index < len(original_items)
            and isinstance(
                original_items[index],
                dict,
            )
            else {}
        )

        if isinstance(item, dict):
            existing_title = (
                item.get("title")
                or item.get("name")
                or ""
            )

            existing_bullets = item.get(
                "bullets",
                [],
            )

            if existing_bullets:
                if not isinstance(
                    existing_bullets,
                    list,
                ):
                    existing_bullets = [
                        existing_bullets
                    ]

                bullets = []
                for bullet in existing_bullets:
                    cleaned_bullet = _normalize_resume_text(
                        bullet
                    )
                    if not cleaned_bullet:
                        continue
                    if cleaned_bullet.startswith("• "):
                        cleaned_bullet = "•" + cleaned_bullet[2:]
                    bullets.append(cleaned_bullet)

                project = {
                    "title": (
                        existing_title
                        or original.get("title")
                        or original.get("name")
                        or ""
                    ),
                    "bullets": bullets,
                }

                technologies = (
                    original.get("technologies")
                    or item.get("technologies")
                )

                if technologies:
                    project["technologies"] = deepcopy(
                        technologies
                    )

                if project["title"] or project["bullets"]:
                    projects.append(project)

                continue

            rewritten_text = (
                item.get("rewritten")
                or item.get("description")
                or ""
            )
        else:
            rewritten_text = item

        if rewritten_text is None:
            rewritten_text = ""

        lines = []
        for line in str(rewritten_text).splitlines():
            if not line.strip():
                continue
            cleaned_line = _normalize_resume_text(line)
            if cleaned_line.startswith("• "):
                cleaned_line = "•" + cleaned_line[2:]
            if cleaned_line:
                lines.append(cleaned_line)

        if not lines:
            continue

        original_title = (
            original.get("title")
            or original.get("name")
            or ""
        )

        if len(lines) > 1:
            title = lines[0]
            bullets = lines[1:]
        elif original_title:
            title = original_title
            bullets = lines
        else:
            title = lines[0]
            bullets = []

        project = {
            "title": title,
            "bullets": bullets,
        }

        if original.get("technologies"):
            project["technologies"] = deepcopy(
                original["technologies"]
            )

        projects.append(project)

    return projects


def _normalize_rewritten_collection(
    rewritten_items,
    original_items,
):
    """
    Convert Phase 10 rewritten collection items into
    canonical FinalResume collection items.

    Rewrite metadata such as original, changes, and validation
    is intentionally excluded from the final resume.
    """
    if not isinstance(
        rewritten_items,
        list,
    ):
        return []

    if not isinstance(
        original_items,
        list,
    ):
        original_items = []

    # -------------------------------------------------
    # Special case: one structured source item expanded
    # into multiple rewritten entries.
    # -------------------------------------------------
    if (
        len(original_items) == 1
        and isinstance(
            original_items[0],
            dict,
        )
        and (
            len(rewritten_items) > 1
            or any(
                "\n" in str(
                    _extract_rewritten_text(item)
                )
                for item in rewritten_items
            )
        )
    ):
        original_item = deepcopy(
            original_items[0]
        )

        rewritten_texts = []

        for rewritten_item in rewritten_items:
            rewritten_text = _extract_rewritten_text(
                rewritten_item
            )

            if (
                not rewritten_text
                and isinstance(
                    rewritten_item,
                    dict,
                )
            ):
                existing_bullets = rewritten_item.get(
                    "bullets",
                    [],
                )

                if isinstance(
                    existing_bullets,
                    list,
                ):
                    rewritten_texts.extend(
                        str(bullet).strip()
                        for bullet in existing_bullets
                        if str(bullet).strip()
                    )

                elif existing_bullets:
                    text = str(
                        existing_bullets
                    ).strip()

                    if text:
                        rewritten_texts.append(
                            text
                        )

                if (
                    not rewritten_text
                    and isinstance(
                        rewritten_item.get(
                            "description"
                        ),
                        str,
                    )
                ):
                    rewritten_text = (
                        rewritten_item[
                            "description"
                        ].strip()
                    )

            if rewritten_text:
                rewritten_texts.append(
                    rewritten_text
                )

        if rewritten_texts:
            header = None
            location = None
            bullets = []

            for rewritten_text in rewritten_texts:
                item_lines = [
                    _normalize_resume_text(line)
                    for line in str(
                        rewritten_text
                    ).splitlines()
                    if line.strip()
                ]

                current_bullet = None

                for line in item_lines:
                    cleaned_line = _normalize_resume_text(line)
                    lowered = cleaned_line.lower()

                    if (
                        header is None
                        and " | " in cleaned_line
                        and any(
                            keyword in lowered
                            for keyword in (
                                "trainer",
                                "engineer",
                                "developer",
                                "analyst",
                                "manager",
                                "consultant",
                                "intern",
                                "specialist",
                                "scientist",
                                "architect",
                                "designer",
                            )
                        )
                    ):
                        header = cleaned_line
                        continue

                    if (
                        location is None
                        and (
                            lowered.startswith(
                                (
                                    "remote",
                                    "hybrid",
                                    "on-site",
                                    "onsite",
                                )
                            )
                            or lowered in (
                                "india",
                                "remote, india",
                            )
                        )
                    ):
                        location = cleaned_line
                        continue

                    if cleaned_line.startswith(
                        (
                            "•",
                            "",
                            "-",
                            "–",
                            "—",
                        )
                    ):
                        # Preserve the canonical bullet marker expected
                        # by the existing FinalResume/tests while
                        # removing duplicate whitespace/alternate
                        # extraction markers.
                        cleaned_line = re.sub(
                            r"^[•\-\u2013\u2014]+\s*",
                            "",
                            cleaned_line,
                        ).strip()

                        if cleaned_line:
                            bullets.append(
                                f"• {cleaned_line}"
                            )

                            current_bullet = (
                                len(bullets) - 1
                            )

                        continue

                    if current_bullet is None:
                        bullets.append(
                            cleaned_line
                        )

                        current_bullet = (
                            len(bullets) - 1
                        )
                    else:
                        bullets[current_bullet] = (
                            f"{bullets[current_bullet]} "
                            f"{cleaned_line}"
                        )

            if header:
                header_parts = [
                    part.strip()
                    for part in header.split("|")
                    if part.strip()
                ]

                if header_parts:
                    first_part = header_parts[0]

                    if " – " in first_part:
                        title, company = first_part.split(
                            " – ",
                            1,
                        )

                        if title.strip():
                            original_item[
                                "job_title"
                            ] = title.strip()

                        if company.strip():
                            original_item[
                                "company"
                            ] = company.strip()

                    elif " - " in first_part:
                        title, company = first_part.split(
                            " - ",
                            1,
                        )

                        if title.strip():
                            original_item[
                                "job_title"
                            ] = title.strip()

                        if company.strip():
                            original_item[
                                "company"
                            ] = company.strip()

                    elif not original_item.get(
                        "job_title"
                    ):
                        original_item[
                            "job_title"
                        ] = first_part

                if len(header_parts) > 1:
                    original_item[
                        "dates"
                    ] = header_parts[1]

            if location:
                original_item[
                    "location"
                ] = location

            # Extraction-only fields must never reach FinalResume.
            for field in (
                "section",
                "job_titles",
                "responsibilities",
                "achievements",
                "descriptions",
                "description",
                "years",
            ):
                original_item.pop(
                    field,
                    None,
                )

            original_item["bullets"] = bullets

            return [
                original_item
            ]

    # -------------------------------------------------
    # Standard 1:1 normalization.
    # -------------------------------------------------
    normalized = []

    for index, rewritten_item in enumerate(
        rewritten_items
    ):
        rewritten_text = _extract_rewritten_text(
            rewritten_item
        )

        if (
            not rewritten_text
            and isinstance(
                rewritten_item,
                dict,
            )
        ):
            existing_bullets = rewritten_item.get(
                "bullets",
                [],
            )

            if isinstance(
                existing_bullets,
                list,
            ):
                bullet_text = [
                    str(bullet).strip()
                    for bullet in existing_bullets
                    if str(bullet).strip()
                ]

                if bullet_text:
                    rewritten_text = " ".join(
                        bullet_text
                    )

            if (
                not rewritten_text
                and isinstance(
                    rewritten_item.get(
                        "description"
                    ),
                    str,
                )
            ):
                rewritten_text = (
                    rewritten_item[
                        "description"
                    ].strip()
                )

        if not rewritten_text:
            continue

        original_item = (
            original_items[index]
            if index < len(original_items)
            else None
        )

        if isinstance(
            original_item,
            dict,
        ):
            item = deepcopy(
                original_item
            )

            if isinstance(
                rewritten_item,
                dict,
            ):
                for key, value in (
                    rewritten_item.items()
                ):
                    if key in (
                        "job_title",
                        "company",
                        "dates",
                        "title",
                        "technologies",
                        "institution",
                        "degree",
                        "year",
                        "location",
                    ):
                        item[key] = deepcopy(
                            value
                        )

            # Remove extraction and rewrite metadata.
            for field in (
                "section",
                "job_titles",
                "bullets",
                "responsibilities",
                "achievements",
                "descriptions",
                "description",
                "years",
            ):
                item.pop(
                    field,
                    None,
                )

            item["bullets"] = [
                rewritten_text
            ]

            normalized.append(
                item
            )

        else:
            normalized.append(
                {
                    "description": rewritten_text,
                }
            )

    return normalized


def _normalize_rewrite_sections(
    rewrite_result,
    resume_data,
):
    """
    Convert the Phase 10 rewrite result into
    FinalResume-compatible section data.
    """
    rewrite_result = (
        rewrite_result
        if isinstance(
            rewrite_result,
            dict,
        )
        else {}
    )

    resume_data = (
        resume_data
        if isinstance(
            resume_data,
            dict,
        )
        else {}
    )

    original_experience = _safe_list(
        resume_data.get(
            "experience",
            [],
        )
    )

    original_projects = _safe_list(
        resume_data.get(
            "projects",
            [],
        )
    )

    original_skills = _safe_list(
        resume_data.get(
            "skills",
            [],
        )
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------
    summary_result = rewrite_result.get(
        "summary",
        {},
    )

    summary = _extract_rewritten_text(
        summary_result
    )

    if not summary:
        original_summary = resume_data.get(
            "summary",
            "",
        )

        if isinstance(
            original_summary,
            str,
        ):
            summary = _normalize_resume_text(
                original_summary
            )

    summary = _normalize_resume_text(summary)

    # -----------------------------------------------------
    # Skills
    # -----------------------------------------------------
    skills_result = rewrite_result.get(
        "skills",
        {},
    )

    rewritten_skills = []

    if isinstance(
        skills_result,
        dict,
    ):
        rewritten_skills = skills_result.get(
            "rewritten",
            [],
        )

    if not isinstance(
        rewritten_skills,
        list,
    ):
        rewritten_skills = []

    rewritten_skills = [
        str(skill).strip()
        for skill in rewritten_skills
        if str(skill).strip()
    ]

    # Preserve exact candidate skill terms. Only exact
    # case-insensitive duplicates are removed; semantic
    # variants remain because ATS engines can score them
    # as distinct terms.
    preserved_skills = []
    seen_skills = set()

    for skill in (
        rewritten_skills
        + [
            str(skill).strip()
            for skill in original_skills
            if str(skill).strip()
        ]
    ):
        skill = _normalize_resume_text(skill)
        if not skill:
            continue

        key = skill.lower()

        if key in seen_skills:
            continue

        seen_skills.add(key)
        preserved_skills.append(skill)

    # -----------------------------------------------------
    # Experience
    # -----------------------------------------------------
    experience = _normalize_rewritten_collection(
        rewritten_items=(
            rewrite_result.get(
                "experience",
                [],
            )
        ),
        original_items=original_experience,
    )

    # -----------------------------------------------------
    # Projects
    # -----------------------------------------------------
    projects = _normalize_rewritten_collection(
        rewritten_items=(
            rewrite_result.get(
                "projects",
                [],
            )
        ),
        original_items=original_projects,
    )

    # -----------------------------------------------------
    # Non-rewritten sections
    # -----------------------------------------------------
    education = _normalize_education(
        resume_data.get(
            "education",
            [],
        )
    )

    certifications = _safe_list(
        resume_data.get(
            "certifications",
            [],
        )
    )

    return {
        "summary": summary,
        "experience": experience,
        "projects": projects,
        "skills": preserved_skills,
        "education": education,
        "certifications": certifications,
    }


def _extract_tailoring_data(
    tailoring_plan,
):
    """Extract the nested tailoring-plan dictionary."""
    if not isinstance(
        tailoring_plan,
        dict,
    ):
        return {}

    nested = tailoring_plan.get(
        "tailoring_plan",
        tailoring_plan,
    )

    return (
        nested
        if isinstance(
            nested,
            dict,
        )
        else {}
    )


def _extract_target_values(
    ats_result=None,
    jd_analysis=None,
):
    """
    Extract JD keywords and skills.

    ATS-derived values are preferred when supplied.
    If ATS values are absent, the existing JD analyzer
    provides the fallback targets.
    """
    if isinstance(
        ats_result,
        dict,
    ):
        keywords = (
            ats_result.get(
                "keywords"
            )
            or ats_result.get(
                "target_keywords"
            )
            or []
        )

        skills = (
            ats_result.get(
                "skills"
            )
            or ats_result.get(
                "target_skills"
            )
            or ats_result.get(
                "required_skills"
            )
            or []
        )

        if keywords or skills:
            return (
                _safe_list(keywords),
                _safe_list(skills),
            )

    if isinstance(
        jd_analysis,
        dict,
    ):
        keywords = (
            jd_analysis.get(
                "keywords"
            )
            or jd_analysis.get(
                "target_keywords"
            )
            or []
        )

        skills = (
            jd_analysis.get(
                "required_skills"
            )
            or jd_analysis.get(
                "skills"
            )
            or jd_analysis.get(
                "target_skills"
            )
            or []
        )

        return (
            _safe_list(keywords),
            _safe_list(skills),
        )

    return [], []


def _extract_relevance_scores(
    items,
    target_keywords,
    target_skills,
):
    """Calculate deterministic relevance scores for items."""
    ranked = rank_content(
        items=items,
        target_keywords=target_keywords,
        target_skills=target_skills,
    )

    return {
        entry["original_index"]: entry["score"]
        for entry in ranked
    }


def _prioritize_items(
    items,
    section,
    target_keywords,
    target_skills,
):
    """Rank and prioritize items for one section."""
    items = _safe_list(
        items
    )

    if not items:
        return []

    relevance_scores = _extract_relevance_scores(
        items,
        target_keywords,
        target_skills,
    )

    return prioritize_content(
        items=items,
        section=section,
        relevance_scores=relevance_scores,
    )


def _unwrap_selected_items(
    length_result,
):
    """Extract raw resume items from length-control results."""
    sections = {}

    for section, result in length_result.get(
        "sections",
        {},
    ).items():
        selected = result.get(
            "selected",
            [],
        )

        raw_items = []

        for entry in selected:
            if (
                isinstance(
                    entry,
                    dict,
                )
                and "item" in entry
            ):
                raw_items.append(
                    deepcopy(
                        entry["item"]
                    )
                )
            else:
                raw_items.append(
                    deepcopy(
                        entry
                    )
                )

        sections[section] = raw_items

    return sections


def _build_section_relevance(
    prioritized_sections,
):
    """Build section-level relevance scores."""
    relevance_scores = {}

    for section, entries in (
        prioritized_sections.items()
    ):
        if not entries:
            relevance_scores[section] = 0
            continue

        total = sum(
            float(
                entry.get(
                    "priority_score",
                    0,
                )
            )
            for entry in entries
            if isinstance(
                entry,
                dict,
            )
        )

        relevance_scores[section] = round(
            total / len(entries),
            2,
        )

    return relevance_scores


def _get_rag_optimization(
    job_description,
    resume_data=None,
    rag_service=None,
):
    service = (
        rag_service
        if rag_service is not None
        else RAGOptimizationService()
    )

    if not service.enabled:
        return None

    jd_analysis = analyze_job_description(
        job_description
    )

    try:
        rag_payload = service.get_phase11_payload(
            jd_analysis=deepcopy(
                jd_analysis
            ),
            resume_data=deepcopy(
                resume_data
            ),
        )
    except TypeError as exc:
        if "resume_data" not in str(exc):
            raise

        rag_payload = service.get_phase11_payload(
            jd_analysis=deepcopy(
                jd_analysis
            ),
        )

    if not isinstance(
        rag_payload,
        dict,
    ):
        raise TypeError(
            "RAG optimization service must return a "
            "dictionary phase11 payload."
        )

    return deepcopy(
        rag_payload
    )


def _attach_rag_optimization(
    tailoring_plan,
    rag_optimization,
):
    """
    Attach RAG optimization context without replacing Phase 9 data.
    """
    if rag_optimization is None:
        return tailoring_plan

    updated_plan = deepcopy(
        tailoring_plan
    )

    if not isinstance(
        updated_plan,
        dict,
    ):
        updated_plan = {}

    nested_plan = updated_plan.get(
        "tailoring_plan"
    )

    if isinstance(
        nested_plan,
        dict,
    ):
        nested_plan[
            "rag_optimization"
        ] = deepcopy(
            rag_optimization
        )
    else:
        updated_plan[
            "rag_optimization"
        ] = deepcopy(
            rag_optimization
        )

    return updated_plan


def generate_optimized_resume(
    resume_text,
    resume_data=None,
    job_description="",
    ats_result=None,
    resume_quality=None,
    content_quality=None,
    improvement_suggestions=None,
    tailoring_plan=None,
    experience_level="experienced",
    target_pages=1,
    target_job_title=None,
    client=None,
    rag_service=None,
):
    """
    Generate a canonical JD-optimized FinalResume.

    Pipeline:

        tailoring
        -> rewriting
        -> normalization
        -> content selection
        -> prioritization
        -> length control
        -> section ordering
        -> FinalResume
        -> validation

    The function does not mutate caller-provided inputs.
    """
    resume_data = deepcopy(
        resume_data or {}
    )

    ats_result = deepcopy(
        ats_result or {}
    )

    resume_quality = deepcopy(
        resume_quality or {}
    )

    content_quality = deepcopy(
        content_quality or {}
    )

    improvement_suggestions = deepcopy(
        improvement_suggestions or []
    )

    # -----------------------------------------------------
    # Phase 9 tailoring plan
    # -----------------------------------------------------
    if tailoring_plan is None:
        tailoring_result = generate_tailoring_plan(
            resume_data=resume_data,
            ats_result=ats_result,
            resume_quality=resume_quality,
            content_quality=content_quality,
            improvement_suggestions=(
                improvement_suggestions
            ),
        )

        tailoring_plan = tailoring_result

    else:
        tailoring_plan = deepcopy(
            tailoring_plan
        )

    # -----------------------------------------------------
    # JD target extraction
    #
    # If the caller does not provide ATS targets, analyze
    # the JD directly. This makes direct generation requests
    # self-contained.
    # -----------------------------------------------------
    jd_analysis = None

    target_keywords, target_skills = (
        _extract_target_values(
            ats_result=ats_result,
        )
    )

    if not target_keywords and not target_skills:
        jd_analysis = analyze_job_description(
            job_description
        )

        target_keywords, target_skills = (
            _extract_target_values(
                ats_result=ats_result,
                jd_analysis=jd_analysis,
            )
        )

    # -----------------------------------------------------
    # Phase 12 RAG optimization
    # -----------------------------------------------------
    rag_optimization = _get_rag_optimization(
        job_description=job_description,
        resume_data=resume_data,
        rag_service=rag_service,
    )

    tailoring_plan = _attach_rag_optimization(
        tailoring_plan=tailoring_plan,
        rag_optimization=rag_optimization,
    )

    # -----------------------------------------------------
    # Phase 10 AI rewriting
    # -----------------------------------------------------
    rewrite_result = rewrite_resume(
        resume_text=resume_text,
        resume_data=resume_data,
        tailoring_plan=tailoring_plan,
        job_description=job_description,
        experience=resume_data.get(
            "experience",
            [],
        ),
        projects=resume_data.get(
            "projects",
            [],
        ),
        skills=resume_data.get(
            "skills",
            [],
        ),
        client=client,
    )

    # -----------------------------------------------------
    # Normalize Phase 10 output
    # -----------------------------------------------------
    rewritten_sections = (
        _normalize_rewrite_sections(
            rewrite_result=rewrite_result,
            resume_data=resume_data,
        )
    )

    # -----------------------------------------------------
    # Final project normalization
    # -----------------------------------------------------
    rewritten_sections["projects"] = _normalize_projects(
        rewritten_sections.get(
            "projects",
            [],
        ),
        original_items=resume_data.get(
            "projects",
            [],
        ),
    )

    # -----------------------------------------------------
    # Content prioritization
    # -----------------------------------------------------
    prioritized_sections = {}

    for section in DEFAULT_COLLECTION_SECTIONS:
        prioritized_sections[section] = (
            _prioritize_items(
                items=rewritten_sections[
                    section
                ],
                section=section,
                target_keywords=target_keywords,
                target_skills=target_skills,
            )
        )

    # -----------------------------------------------------
    # Length control
    # -----------------------------------------------------
    length_result = control_resume_length(
        sections=prioritized_sections,
        target_pages=target_pages,
    )

    selected_sections = (
        _unwrap_selected_items(
            length_result
        )
    )

    # Skills are factual candidate data. Do not allow the
    # generic item-count length controller to silently discard
    # genuine source skills.
    selected_sections["skills"] = deepcopy(
        rewritten_sections.get(
            "skills",
            [],
        )
    )

    # -----------------------------------------------------
    # Section relevance
    # -----------------------------------------------------
    section_relevance = (
        _build_section_relevance(
            prioritized_sections
        )
    )

    # -----------------------------------------------------
    # Available sections
    # -----------------------------------------------------
    available_sections = {
        "summary": bool(
            rewritten_sections.get(
                "summary"
            )
        ),
        **{
            section: bool(items)
            for section, items in (
                selected_sections.items()
            )
        },
    }

    sections = [
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications",
    ]

    # -----------------------------------------------------
    # Section ordering
    # -----------------------------------------------------
    # Use a deterministic professional resume order.
    # Relevance ranking controls content selection, not the
    # position of the major resume sections.
    preferred_section_order = (
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications",
    )

    section_order = [
        section
        for section in preferred_section_order
        if available_sections.get(section, False)
    ]

    # -----------------------------------------------------
    # Build canonical FinalResume
    # -----------------------------------------------------
    optimized_summary = _preserve_supported_keywords(
        summary=rewritten_sections.get(
            "summary",
            "",
        ),
        original_resume_data=resume_data,
        job_description=job_description,
        ats_result=ats_result if ats_result else None,
        allow_single_token_keywords=rag_service is not None,
    )

    final_resume = build_final_resume(
        personal_info=resume_data.get(
            "personal_info",
            {},
        ),
        summary=optimized_summary,

        skills=selected_sections.get(
            "skills",
            [],
        ),
        experience=selected_sections.get(
            "experience",
            [],
        ),
        projects=selected_sections.get(
            "projects",
            [],
        ),
        education=selected_sections.get(
            "education",
            [],
        ),
        certifications=selected_sections.get(
            "certifications",
            [],
        ),
        section_order=section_order,
        metadata={
            "target_pages": target_pages,
            "optimization_enabled": True,
            "target_job_title": target_job_title,
        },
    )

    # -----------------------------------------------------
    # Final deterministic cleanup
    # -----------------------------------------------------
    vocabulary = _build_source_word_lexicon(
        resume_text=resume_text,
        job_description=job_description,
        resume_data=resume_data,
    )

    final_resume = _clean_final_resume_text(
        final_resume,
        vocabulary,
    )

    # Re-apply supported ATS terminology across the entire
    # final resume after deterministic text cleanup.
    final_resume = _preserve_supported_keywords_in_final_resume(
        final_resume=final_resume,
        original_resume_data=resume_data,
        job_description=job_description,
        ats_result=ats_result if ats_result else None,
        allow_single_token_keywords=rag_service is not None,
    )

    # Run the deterministic cleanup once more because keyword
    # preservation may have appended generated text.
    final_resume = _clean_final_resume_text(
        final_resume,
        vocabulary,
    )

    # -----------------------------------------------------
    # Final validation
    # -----------------------------------------------------
    validation = validate_final_resume(
        final_resume
    )

    if not validation["valid"]:
        raise ValueError(
            "Generated final resume is invalid: "
            + "; ".join(
                validation["errors"]
            )
        )

    return {
        "final_resume": final_resume,
        "tailoring_plan": tailoring_plan,
        "rewrite_result": rewrite_result,
        "length_control": length_result,
        "validation": validation,
        "rag_optimization": (
            deepcopy(
                rag_optimization
            )
            if rag_optimization is not None
            else None
        ),
    }
