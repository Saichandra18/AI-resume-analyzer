from app.job_description_analyzer import analyze_job_description
from app.skill_matcher import match_skills
from app.experience_matcher import match_experience
from app.qualification_matcher import match_qualifications
from app.keyword_matcher import match_keywords
from app.score_engine import calculate_ats_score


def _extract_resume_degrees(resume_education):
    """
    Extract degree values from supported resume education structures.

    Supported formats:

    1. Legacy dictionary:
        {
            "degrees": ["B.Tech", "M.Tech"]
        }

    2. Structured education list:
        [
            {
                "degree": "B.Tech",
                "institution": "Example University",
                "year": "2024"
            }
        ]
    """

    if not resume_education:
        return []

    # Legacy dictionary-based structure.
    if isinstance(resume_education, dict):
        degrees = resume_education.get("degrees", [])

        if isinstance(degrees, str):
            return [degrees]

        if isinstance(degrees, list):
            return degrees

        return []

    # Current structured resume contract.
    if isinstance(resume_education, list):
        degrees = []

        for education in resume_education:
            if not isinstance(education, dict):
                continue

            degree = (
                education.get("degree")
                or education.get("degree_name")
                or education.get("qualification")
                or education.get("name")
            )

            if isinstance(degree, str):
                degrees.append(degree)

        return degrees

    return []


def analyze_resume_against_job(resume_data, job_description):
    """Analyze a structured resume against a job description."""

    if not resume_data:
        resume_data = {}

    job_analysis = analyze_job_description(job_description)

    skill_result = match_skills(
        resume_data.get("skills", []),
        job_analysis.get("required_skills", []),
    )

    experience_result = match_experience(
        resume_data.get("experience", {}),
        job_analysis.get("experience"),
    )

    education = resume_data.get("education", [])
    resume_degrees = _extract_resume_degrees(education)

    qualification_result = match_qualifications(
        resume_degrees,
        job_analysis.get("qualifications", []),
    )

    keyword_result = match_keywords(
        resume_data,
        job_analysis.get("keywords", []),
    )

    score_result = calculate_ats_score(
        skill_result,
        experience_result,
        qualification_result,
        keyword_result,
    )

    return {
        "ats_score": score_result["ats_score"],
        "skills": skill_result,
        "experience": experience_result,
        "qualifications": qualification_result,
        "keywords": keyword_result,
        "component_scores": score_result["component_scores"],
        "weights": score_result["weights"],
    }