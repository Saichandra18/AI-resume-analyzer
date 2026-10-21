"""High-level service for generating JD-optimized resume documents."""

from pathlib import Path
from app.rendered_document_validator import (
    validate_final_documents,
)

from app.resume_document_renderer import render_final_resume
from app.page_fit import fit_pdf_to_pages
from app.resume_pdf_renderer import render_final_resume_pdf
from app.resume_generation_pipeline import generate_optimized_resume
from app.resume_optimization_evaluator import (
    evaluate_resume_optimization,
)


def _generate_resume(
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
    """Run the shared optimized-resume generation pipeline."""

    return generate_optimized_resume(
        resume_text=resume_text,
        resume_data=resume_data,
        job_description=job_description,
        ats_result=ats_result,
        resume_quality=resume_quality,
        content_quality=content_quality,
        improvement_suggestions=improvement_suggestions,
        tailoring_plan=tailoring_plan,
        experience_level=experience_level,
        target_pages=target_pages,
        target_job_title=target_job_title,
        client=client,
        rag_service=rag_service,
    )


def _evaluate_optimization(
    resume_data,
    final_resume,
    job_description,
):
    """Evaluate ATS impact of the optimized resume."""

    return evaluate_resume_optimization(
        original_resume_data=resume_data or {},
        optimized_resume=final_resume,
        job_description=job_description,
    )


def generate_optimized_resume_docx(
    resume_text,
    output_path,
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
    template="default",
):
    """
    Generate an optimized resume and render it as DOCX.

    Returns:
        dict containing the generation result, generated document
        path, and before-vs-after ATS evaluation.
    """

    output_path = Path(output_path)

    generation_result = _generate_resume(
        resume_text=resume_text,
        resume_data=resume_data,
        job_description=job_description,
        ats_result=ats_result,
        resume_quality=resume_quality,
        content_quality=content_quality,
        improvement_suggestions=improvement_suggestions,
        tailoring_plan=tailoring_plan,
        experience_level=experience_level,
        target_pages=target_pages,
        target_job_title=target_job_title,
        client=client,
        rag_service=rag_service,
    )

    final_resume = generation_result["final_resume"]

    document_path = render_final_resume(
        resume=final_resume,
        output_path=output_path,
        template=template,
    )

    ats_evaluation = _evaluate_optimization(
        resume_data=resume_data,
        final_resume=final_resume,
        job_description=job_description,
    )

    return {
        **generation_result,
        "document_path": document_path,
        "ats_evaluation": ats_evaluation,
    }


def generate_optimized_resume_pdf(
    resume_text,
    output_path,
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
    template="default",
):
    """
    Generate an optimized resume and render it as PDF.

    Returns:
        dict containing the generation result, generated PDF path,
        and before-vs-after ATS evaluation.
    """

    output_path = Path(output_path)

    generation_result = _generate_resume(
        resume_text=resume_text,
        resume_data=resume_data,
        job_description=job_description,
        ats_result=ats_result,
        resume_quality=resume_quality,
        content_quality=content_quality,
        improvement_suggestions=improvement_suggestions,
        tailoring_plan=tailoring_plan,
        experience_level=experience_level,
        target_pages=target_pages,
        target_job_title=target_job_title,
        client=client,
        rag_service=rag_service,
    )

    final_resume = generation_result["final_resume"]

    pdf_path = render_final_resume_pdf(
        resume=final_resume,
        output_path=output_path,
        template=template,
    )

    ats_evaluation = _evaluate_optimization(
        resume_data=resume_data,
        final_resume=final_resume,
        job_description=job_description,
    )

    return {
        **generation_result,
        "pdf_path": pdf_path,
        "ats_evaluation": ats_evaluation,
    }


def generate_optimized_resume_documents(
    resume_text,
    docx_output_path,
    pdf_output_path,
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
    template="default",
):
    """
    Generate an optimized resume in both DOCX and PDF.

    The optimization pipeline runs only once. The same validated
    FinalResume is rendered to both output formats.

    Returns:
        dict containing generation results, both generated paths,
        and before-vs-after ATS evaluation.
    """

    docx_output_path = Path(docx_output_path)
    pdf_output_path = Path(pdf_output_path)

    generation_result = _generate_resume(
        resume_text=resume_text,
        resume_data=resume_data,
        job_description=job_description,
        ats_result=ats_result,
        resume_quality=resume_quality,
        content_quality=content_quality,
        improvement_suggestions=improvement_suggestions,
        tailoring_plan=tailoring_plan,
        experience_level=experience_level,
        target_pages=target_pages,
        target_job_title=target_job_title,
        client=client,
        rag_service=rag_service,
    )

    final_resume = generation_result["final_resume"]

    # Render the PDF first and make it respect the page target (tighter
    # spacing, then dropping the lowest-priority bullet as a last resort).
    # The DOCX is rendered from the same, possibly trimmed, resume so both
    # documents always contain the same content.
    final_resume, pdf_path, page_fit = fit_pdf_to_pages(
        final_resume,
        pdf_output_path,
        target_pages,
        template=template,
        render=render_final_resume_pdf,
    )

    generation_result = {
        **generation_result,
        "final_resume": final_resume,
    }

    document_path = render_final_resume(
        resume=final_resume,
        output_path=docx_output_path,
        template=template,
    )

    ats_evaluation = _evaluate_optimization(
        resume_data=resume_data,
        final_resume=final_resume,
        job_description=job_description,
    )

    document_validation = validate_final_documents(
        docx_path=document_path,
        pdf_path=pdf_path,
        ats_comparison=ats_evaluation["comparison"],
        resume_text=resume_text,
        required_content=None,
        target_pages=target_pages,
    )

    return {
        **generation_result,
        "document_path": document_path,
        "pdf_path": pdf_path,
        "ats_evaluation": ats_evaluation,
        "document_validation": document_validation,
        "page_fit": page_fit,
    }

