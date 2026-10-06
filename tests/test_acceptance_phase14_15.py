from copy import deepcopy

from app.resume_generation_service import generate_optimized_resume_documents


def test_phase14_acceptance_full_resume_generation(tmp_path):
    resume_data = {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+91 9876543210",
            "location": "Bengaluru, India",
        },
        "summary": (
            "AI/ML Engineer with experience in Python, SQL, "
            "Machine Learning, Generative AI, and RAG."
        ),
        "skills": [
            "Python",
            "SQL",
            "Machine Learning",
            "Generative AI",
            "RAG",
            "Flask",
        ],
        "experience": {
            "section": [
                "Data Analyst",
                "ABC Technologies",
                "2021 - Present",
            ],
            "job_titles": ["Data Analyst"],
            "years": ["2021 - Present"],
        },
        "projects": [
            "AI Resume Analyzer",
            "Built an AI-powered resume analysis and optimization platform.",
        ],
        "education": {
            "degrees": ["Bachelor of Technology in Computer Science"],
            "years": ["2020", "2024"],
        },
    }

    resume_text = """
    John Doe
    john.doe@example.com | +91 9876543210 | Bengaluru, India

    PROFESSIONAL SUMMARY
    AI/ML Engineer with experience in Python, SQL, Machine Learning,
    Generative AI, and RAG.

    SKILLS
    Python, SQL, Machine Learning, Generative AI, RAG, Flask

    EXPERIENCE
    Data Analyst
    ABC Technologies
    2021 - Present

    PROJECTS
    AI Resume Analyzer
    Built an AI-powered resume analysis and optimization platform.

    EDUCATION
    Bachelor of Technology in Computer Science
    University of Technology
    """

    job_description = """
    We are looking for an AI/ML Engineer with skills in Python, SQL,
    Machine Learning, Generative AI, RAG, and Flask.
    """

    original_data = deepcopy(resume_data)

    docx_path = tmp_path / "accepted_resume.docx"
    pdf_path = tmp_path / "accepted_resume.pdf"

    result = generate_optimized_resume_documents(
        resume_text=resume_text,
        resume_data=resume_data,
        job_description=job_description,
        docx_output_path=str(docx_path),
        pdf_output_path=str(pdf_path),
        template="ats_clean",
    )

    assert result is not None

    assert docx_path.exists()
    assert docx_path.stat().st_size > 0

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0

    # Generation must not mutate the caller's input.
    assert resume_data == original_data