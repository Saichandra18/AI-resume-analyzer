from app.ai import create_llm_provider
from app.ai.providers import LLMProvider
from app.experience_rewriter import rewrite_experience
from app.full_rewrite_validator import validate_full_rewrite
from app.project_rewriter import rewrite_projects
from app.skills_rewriter import rewrite_skills
from app.summary_rewriter import rewrite_summary


def rewrite_resume(
    resume_text,
    resume_data=None,
    tailoring_plan=None,
    job_description="",
    experience=None,
    projects=None,
    skills=None,
    client: LLMProvider | None = None,
):
    """Rewrite supported resume sections and validate the result."""

    resume_data = resume_data or {}
    tailoring_plan = tailoring_plan or {}
    client = client or create_llm_provider()

    experience_result = rewrite_experience(
        experience=experience or [],
        resume_text=resume_text,
        resume_data=resume_data,
        tailoring_plan=tailoring_plan,
        job_description=job_description,
        client=client,
    )

    print("\n[DEBUG] Project input count:", len(projects or []))
    print("[DEBUG] Project input items:", repr(projects))
    print(
        "[DEBUG] Experience input type:",
        type(experience).__name__,
    )
    print("[DEBUG] Experience input:", repr(experience))

    print("\n[DEBUG] Project input count:", len(projects or []))
    print("[DEBUG] Project input items:", repr(projects))
    print(
        "[DEBUG] Experience input type:",
        type(experience).__name__,
    )
    print("[DEBUG] Experience input:", repr(experience))

    projects_result = rewrite_projects(
        projects=projects or [],
        resume_text=resume_text,
        resume_data=resume_data,
        tailoring_plan=tailoring_plan,
        job_description=job_description,
        client=client,
    )

    summary_result = rewrite_summary(
        resume_text=resume_text,
        resume_data=resume_data,
        tailoring_plan=tailoring_plan,
        job_description=job_description,
        client=client,
    )

    skills_result = rewrite_skills(
        skills=skills or [],
        resume_text=resume_text,
        resume_data=resume_data,
        tailoring_plan=tailoring_plan,
        job_description=job_description,
        client=client,
    )

    validation = validate_full_rewrite(
        summary=summary_result.get("summary"),
        experience=experience_result.get("experience"),
        projects=projects_result.get("projects"),
        skills=skills_result.get("skills"),
    )

    return {
        "summary": summary_result.get("summary", {}),
        "experience": experience_result.get("experience", []),
        "projects": projects_result.get("projects", []),
        "skills": skills_result.get("skills", {}),
        "validation": validation,
    }
