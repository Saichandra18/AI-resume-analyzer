from app.job_description_processor import clean_job_description
from app.job_skill_extractor import extract_required_skills
from app.qualification_extractor import extract_required_qualifications
from app.experience_requirement_extractor import (
    extract_experience_requirement,
)
from app.job_keyword_extractor import extract_job_keywords


def analyze_job_description(job_description):
    """Analyze a job description and return structured data."""

    if not job_description:
        return {
            "cleaned_text": "",
            "required_skills": [],
            "qualifications": [],
            "experience": None,
            "keywords": [],
        }

    cleaned_text = clean_job_description(job_description)

    return {
        "cleaned_text": cleaned_text,
        "required_skills": extract_required_skills(cleaned_text),
        "qualifications": extract_required_qualifications(cleaned_text),
        "experience": extract_experience_requirement(cleaned_text),
        "keywords": extract_job_keywords(cleaned_text),
    }