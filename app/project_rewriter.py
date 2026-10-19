import json

from app.ai import create_llm_provider
from app.ai.providers import LLMProvider
from app.rewrite_models import build_rewrite_output
from app.rewrite_validator import validate_rewrite


import re



def _group_project_lines(projects):
    """Group flat extracted project lines into title-and-bullet blocks."""
    if not isinstance(projects, list):
        return projects

    grouped = []
    current = None

    bullet_pattern = re.compile(
        r"^\s*(?:\u2022|\uf0b7|[-\u2013\u2014]|â€¢|ï‚·|â€“|â€”)\s*"
    )

    corrupted_bullet_pattern = re.compile(r"^\s*(?:\?|\*\s*)\s*")

    def save_current():
        if current is None:
            return

        title = current["title"]
        bullets = current["bullets"]

        text = title
        if bullets:
            text += "\n" + "\n".join(
                f"\u2022 {bullet}" for bullet in bullets
            )

        grouped.append(text)

    def join_continuation(previous, line):
        """Join a wrapped line without introducing a false word boundary."""
        previous = previous.rstrip()

        if previous.endswith("-"):
            return previous[:-1] + line.lstrip()

        return previous + " " + line.lstrip()

    for item in projects:
        if not isinstance(item, str):
            # Preserve existing structured inputs.
            if current is not None:
                save_current()
                current = None

            grouped.append(item)
            continue

        line = item.strip()
        if not line:
            continue

        bullet_match = bullet_pattern.match(line)

        # Recognize common corrupted bullet markers from PDF extraction.
        corrupted_match = None
        if not bullet_match:
            corrupted_match = corrupted_bullet_pattern.match(line)

        is_bullet = bool(bullet_match) or bool(corrupted_match)

        if is_bullet:
            if bullet_match:
                content = line[bullet_match.end():].strip()
            else:
                content = line[corrupted_match.end():].strip()

            if not content:
                continue

            if current is None:
                current = {"title": content, "bullets": []}
            else:
                current["bullets"].append(content)

            continue

        # A wrapped bullet can continue with an uppercase word.
        # Join it when the previous bullet appears incomplete.
        if current is not None and current["bullets"]:
            previous = current["bullets"][-1]
            previous_stripped = previous.rstrip()

            ends_in_hyphen = previous_stripped.endswith("-")
            ends_in_separator = previous_stripped.endswith(
                (",", ":", ";", "—", "–")
            )
            lacks_sentence_ending = not previous_stripped.endswith(
                (".", "!", "?", "。", "！", "？")
            )

            starts_like_continuation = (
                line[0].islower()
                or line.lower().startswith(
                    (
                        "and ",
                        "or ",
                        "with ",
                        "for ",
                        "to ",
                        "of ",
                        "in ",
                        "using ",
                        "including ",
                        "such as ",
                        "compatibility",
                    )
                )
            )

            if (
                ends_in_hyphen
                or ends_in_separator
                or (
                    lacks_sentence_ending
                    and starts_like_continuation
                )
            ):
                current["bullets"][-1] = join_continuation(
                    previous, line
                )
                continue

        # Otherwise, treat the line as a new project title.
        save_current()
        current = {"title": line, "bullets": []}

    save_current()
    return grouped

def rewrite_projects(
    projects,
    resume_text,
    resume_data=None,
    tailoring_plan=None,
    job_description="",
    client: LLMProvider | None = None,
):
    """Rewrite existing resume project content using AI."""

    if not projects:
        return build_rewrite_output()

    projects = _group_project_lines(projects)

    client = client or create_llm_provider()

    prompt = f"""
Rewrite the following existing resume project content.

PROJECTS:
{projects}

ORIGINAL RESUME:
{resume_text}

STRUCTURED RESUME DATA:
{resume_data or {}}

PHASE 9 TAILORING PLAN:
{tailoring_plan or {}}

TARGET JOB DESCRIPTION:
{job_description or "(empty)"}

RULES:

- Preserve the original meaning.
- Preserve all factual information.
- Do not invent project functionality.
- Do not invent technologies or skills.
- Do not invent achievements.
- Do not invent metrics or numbers.
- Do not invent users, customers, performance results, or scale.
- Use job-description terminology only when supported by the
  original resume.
- Improve clarity, professionalism, and impact.
- Do not exaggerate the project.
- Do not change the actual scope of the project.
- Treat each input block as exactly one project.
- Never combine content from different projects.
- Preserve the original project title.
- Return the title on the first line of each rewritten project.
- Put each project bullet on a separate line.
- Preserve all factual details from that project's original bullets.

Return one rewritten item for each original project item.

Each item must contain:

{{
    "original": "original project text",
    "rewritten": "improved project text",
    "changes": [
        "brief description of the change"
    ]
}}

Return only JSON-compatible data.
"""

    response = client.generate(prompt)

    try:
        parsed_response = json.loads(response)
    except (TypeError, json.JSONDecodeError):
        return {
            "projects": [],
            "validation": {
                "meaning_preserved": False,
                "unsupported_claims": [],
                "grounding_status": "needs_review",
            },
        }

    if not isinstance(parsed_response, list):
        return {
            "projects": [],
            "validation": {
                "meaning_preserved": False,
                "unsupported_claims": [],
                "grounding_status": "needs_review",
            },
        }

    validated_projects = []
    all_unsupported_claims = []
    all_grounded = True

    for item in parsed_response:
        if not isinstance(item, dict):
            all_grounded = False
            all_unsupported_claims.append(
                "Invalid rewritten project item."
            )
            continue

        original = item.get("original", "")
        rewritten = item.get("rewritten", "")

        validation = validate_rewrite(
            original,
            rewritten,
            evidence_text=resume_text,
        )

        item["validation"] = validation

        validated_projects.append(item)

        all_unsupported_claims.extend(
            validation["unsupported_claims"]
        )

        if validation["grounding_status"] != "grounded":
            all_grounded = False

    return {
        "projects": validated_projects,
        "validation": {
            "meaning_preserved": (
                all_grounded
                and bool(validated_projects)
            ),
            "unsupported_claims": all_unsupported_claims,
            "grounding_status": (
                "grounded"
                if all_grounded and validated_projects
                else "needs_review"
            ),
        },
    }