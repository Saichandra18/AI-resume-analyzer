def build_rewrite_prompt(
    resume_text,
    resume_data=None,
    tailoring_plan=None,
    job_description="",
):
    """Build a strict prompt for AI-based resume rewriting."""

    resume_data = resume_data or {}
    tailoring_plan = tailoring_plan or {}

    return f"""
You are an AI resume content rewriting assistant.

Your task is to improve the candidate's existing resume content
based on a job description and a Phase 9 tailoring plan.

IMPORTANT RULES:

1. Preserve all factual information from the original resume.
2. Preserve the original meaning of every rewritten statement.
3. Never invent skills, technologies, responsibilities, achievements,
   qualifications, employment history, projects, or metrics.
4. Never assume that a requirement in the job description is something
   the candidate has experience with.
5. Only use skills, technologies, responsibilities, and achievements
   that are supported by the original resume.
6. Improve clarity, professionalism, specificity, and readability.
7. Incorporate relevant job-description keywords only when they are
   genuinely supported by the candidate's existing resume.
8. Do not fabricate numbers, percentages, performance improvements,
   team sizes, dates, or other measurable results.
9. Do not add responsibilities that are not supported by the resume.
10. Do not remove important factual information merely to make the
    resume shorter.
11. Do not change the candidate's seniority or level of experience.
12. Do not create experience that the candidate does not have.
13. The Phase 9 tailoring plan identifies what should be improved.
    It does NOT provide permission to invent information.
14. Return only structured JSON-compatible data.
15. For every rewritten item, retain the original text so that the
    result can be compared and validated.

ORIGINAL RESUME:
----------------
{resume_text or "(empty)"}

STRUCTURED RESUME DATA:
-----------------------
{resume_data}

PHASE 9 TAILORING PLAN:
-----------------------
{tailoring_plan}

TARGET JOB DESCRIPTION:
-----------------------
{job_description or "(empty)"}

TASK:

Rewrite the following resume content where appropriate:

- Professional summary
- Work experience descriptions
- Project descriptions
- Skills descriptions

REWRITING QUALITY GUIDELINES:

1. Make meaningful improvements rather than only replacing words with
   synonyms.

2. For experience and project bullets, prefer a clear professional
   structure such as:
   action + work performed + relevant method/technology + outcome,
   but include an outcome only when the original resume explicitly
   supports that outcome.

3. Use precise, professional action verbs that accurately describe the
   candidate's actual contribution.

4. Do not make a contribution sound more senior, successful, impactful,
   or measurable than the original evidence supports.

5. Remove unnecessary repetition, filler words, and awkward phrasing.

6. Preserve useful technical terminology and surface relevant
   job-description terminology when it is already supported by the
   resume.

7. Keep bullets concise and resume-ready. Prefer one clear idea per
   bullet.

8. When the original bullet is already strong and clear, make only
   minimal changes rather than rewriting it unnecessarily.

9. Do not add metrics, percentages, performance improvements,
   leadership claims, business outcomes, scale, or achievements unless
   they are explicitly supported by the resume.

10. Never turn a participation or support statement into a leadership
    or ownership claim unless the original resume supports that level
    of responsibility.

11. Never turn an activity into a proven outcome merely because the
    wording sounds more professional.

12. Do not introduce implied performance or consistency claims such as
    "consistently met", "successfully delivered", "reliably achieved",
    "effectively improved", or similar language unless the original
    resume explicitly supports that level of performance.

For each rewritten item:

- Keep the original meaning.
- Improve clarity, specificity, professionalism, and conciseness.
- Make the rewrite meaningfully better when there is a genuine
  opportunity to improve it.
- Align wording with relevant parts of the job description only when
  supported by the original resume.
- Do not introduce unsupported information.

The output must contain these top-level sections:

summary
experience
projects
skills
validation

The validation section must include:

- meaning_preserved
- unsupported_claims
- grounding_status

The "unsupported_claims" field must contain any claims that cannot
be directly supported by the original resume.

The "grounding_status" should be:

- "grounded" when all rewritten content is supported
- "needs_review" when potentially unsupported claims are detected

Do not output explanations outside the structured result.
""".strip()