from app.contact_extractor import extract_email, extract_phone
from app.education_extractor import (
    find_education_section,
    extract_degrees,
    extract_education_years,
)
from app.experience_extractor import (
    find_experience_section,
    extract_job_titles,
    extract_experience_years,
)
from app.name_extractor import extract_name
from app.project_extractor import find_project_section
from app.skill_extractor import extract_skills
from app.certification_extractor import find_certification_section


def structure_resume(text):
    """
    Convert raw resume text into structured resume data.
    """

    if not text:
        return {
            "raw_text": "",
            "personal_info": {
                "name": None,
                "email": None,
                "phone": None,
            },
            "skills": [],
            "education": {
                "section": [],
                "degrees": [],
                "years": [],
            },
            "experience": {
                "section": [],
                "job_titles": [],
                "years": [],
            },
            "projects": [],
            "certifications": [],
        }

    resume_data = {
        "raw_text": text,

        "personal_info": {
            "name": extract_name(text),
            "email": extract_email(text),
            "phone": extract_phone(text),
        },
        "skills": extract_skills(text),
        "education": {
            "section": find_education_section(text),
            "degrees": extract_degrees(text),
            "years": extract_education_years(text),
        },
        "experience": {
            "section": find_experience_section(text),
            "job_titles": extract_job_titles(text),
            "years": extract_experience_years(text),
        },
        "projects": find_project_section(text),
        "certifications": find_certification_section(text),
    }

    return resume_data
