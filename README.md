# AI Resume Analyzer

An AI-powered web application that analyzes resumes against job descriptions, provides ATS-style compatibility insights, identifies skill gaps, recommends improvements, and generates job-description-optimized resumes.

## Current Status

**Phase 18 — Production Readiness & Deployment**

Completed and validated:

- Resume parsing and structuring
- Job description analysis
- ATS scoring and matching
- Skill-gap analysis
- Resume improvement recommendations
- AI-powered resume rewriting
- Job-description-optimized resume generation
- RAG-based knowledge grounding
- Professional resume templates
- DOCX and PDF resume rendering
- ATS validation
- Responsive web UI
- End-to-end testing
- Production security hardening
- Production WSGI deployment with Waitress

Latest full regression baseline:

**1956 tests passed, 0 failed**

---

## Features

### Resume Analysis

- PDF and DOCX resume parsing
- Resume text extraction
- Structured resume information extraction
- Skills extraction
- Education extraction
- Experience extraction
- Project extraction
- Resume quality analysis
- Content quality analysis

### Job Description Analysis

- Job description parsing
- Required skill extraction
- Qualification analysis
- Experience requirement analysis
- Keyword extraction
- Job-specific matching

### ATS Analysis

The ATS scoring engine evaluates resume compatibility using:

- Skills
- Experience
- Qualifications
- Keywords

The current scoring configuration uses:

- Skills: 50%
- Experience: 20%
- Qualifications: 15%
- Keywords: 15%

The analyzer also identifies:

- Matching skills
- Missing skills
- Matching keywords
- Resume strengths
- Resume weaknesses
- Improvement opportunities

### Resume Improvement

The application can generate recommendations based on ATS gaps, including:

- Missing skills
- Missing keywords
- Experience improvements
- Qualification improvements
- Content-quality improvements

### AI Resume Rewriting

The application supports AI-assisted rewriting of:

- Professional summary
- Experience
- Projects
- Skills
- Other supported resume content

The rewriting pipeline validates generated content before incorporating it into the final resume.

### JD-Optimized Resume Generation

The application can generate a resume optimized for a target job description.

The generation pipeline includes:

1. Resume analysis
2. Job description analysis
3. ATS matching
4. Tailoring plan
5. AI rewriting
6. Content normalization
7. Content selection
8. Content prioritization
9. Length control
10. Section ordering
11. Final resume construction
12. Final validation
13. DOCX/PDF rendering

### RAG

The application includes Retrieval-Augmented Generation support for knowledge-grounded resume optimization.

RAG components include:

- Document loading
- Document parsing
- Document cleaning
- Document chunking
- Embedding support
- In-memory vector storage
- Retrieval services
- JD-aware retrieval
- Resume-aware retrieval
- Knowledge-base persistence
- Grounding validation
- RAG optimization orchestration

RAG can be enabled or disabled through configuration.

### Professional Resume Templates

Supported functionality includes:

- Template architecture
- ATS-safe templates
- Modern professional formatting
- Compact technical formatting
- Template configuration
- Section formatting
- DOCX rendering
- PDF rendering
- Page optimization
- Template selection
- Visual validation

### Web Application

The Flask application provides:

- Resume upload
- Job description submission
- ATS analysis
- Resume rewriting
- Optimized resume generation
- Resume download
- Validation results
- Generation progress/state
- Template selection
- Error handling
- Responsive UI

---

# Technology Stack

## Backend

- Python
- Flask
- Waitress
- PyPDF
- python-docx
- ReportLab
- Pillow

## AI / NLP

- LLM-based resume rewriting
- ATS matching
- RAG
- Embeddings
- Knowledge retrieval

## Frontend

- HTML
- CSS
- JavaScript

## Testing

- pytest

## Configuration

- python-dotenv
- Environment variables

---

# Project Structure

A simplified project structure:

```text
AI Resume Analyzer/
│
├── app/
│   ├── ai/
│   ├── rag/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── ...
│
├── data/
├── frontend/
├── generated_rag/
├── generated_resumes/
├── tests/
├── uploads/
│
├── .env
├── .env.example
├── .gitignore
├── app.py
├── config.py
├── requirements.txt
├── run.py
├── wsgi.py
└── README.md
```

Generated files and user uploads are excluded from version control through `.gitignore`.

---

# Prerequisites

Recommended environment:

- Python 3.14+
- pip
- Git

An OpenAI API key is required only for functionality that uses the configured OpenAI provider.

Do not commit API keys or other secrets to source control.

---

# Installation

## 1. Clone the repository

```bash
git clone <repository-url>
cd "AI Resume Analyzer"
```

## 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell execution policy prevents activation, use the appropriate environment activation method for your system.

## 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# Environment Configuration

Create a `.env` file in the project root.

Example:

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6-luna

SECRET_KEY=

FLASK_ENV=development

RAG_ENABLED=false
RAG_EMBEDDING_PROVIDER=local
RAG_EMBEDDING_MODEL=default
RAG_EMBEDDING_DIMENSION=384

# Optional
# RAG_KNOWLEDGE_INDEX_PATH=

FLASK_DEBUG=false
```

The repository contains `.env.example` as a configuration template.

## Production Requirements

When:

```text
FLASK_ENV=production
```

a `SECRET_KEY` must be supplied.

The application intentionally refuses to start if production mode is enabled without a secret key.

For production:

```text
FLASK_DEBUG=false
```

Never commit the real `.env` file or API credentials.

---

# Running in Development

For local development, start the Flask application using the project's development entry point:

```powershell
python run.py
```

Use the development server only for local development.

---

# Running in Production

The project provides a WSGI entry point:

```text
wsgi.py
```

It exposes:

```python
app = create_app()
```

The production server uses Waitress.

Start the application with:

```powershell
python -m waitress --listen=127.0.0.1:5000 --max-request-body-size=5242880 wsgi:app
```

The application will be available at:

```text
http://127.0.0.1:5000
```

The configured request body limit is 5 MB.

For a real deployment, bind the server according to the hosting environment and place the application behind the appropriate network security layer/reverse proxy when required.

---

# API Endpoints

## Home

```text
GET /
```

Returns the web application.

## Resume Upload

```text
POST /api/resume/upload
```

Uploads and processes a supported resume document.

## Job Description

```text
POST /api/job-description
```

Analyzes a submitted job description.

## ATS Analysis

```text
POST /api/analyze
```

Analyzes resume compatibility against a job description.

## Resume Rewrite

```text
POST /api/resume/rewrite
```

Generates supported AI-assisted resume content.

## Resume Generation

```text
POST /api/resume/generate
```

Generates a job-description-optimized resume.

## Resume Download

```text
GET /api/resume/download
```

Downloads the generated resume.

---

# ATS Scoring

The ATS score currently uses the following weighting:

| Category | Weight |
|---|---:|
| Skills | 50% |
| Experience | 20% |
| Qualifications | 15% |
| Keywords | 15% |
| **Total** | **100%** |

The score is accompanied by detailed matching information rather than being treated as a standalone hiring decision.

---

# RAG Configuration

RAG is controlled through environment variables.

Enable RAG:

```text
RAG_ENABLED=true
```

Disable RAG:

```text
RAG_ENABLED=false
```

Embedding configuration:

```text
RAG_EMBEDDING_PROVIDER=local
RAG_EMBEDDING_MODEL=default
RAG_EMBEDDING_DIMENSION=384
```

Optional persisted knowledge index:

```text
RAG_KNOWLEDGE_INDEX_PATH=
```

RAG functionality is designed to remain compatible with RAG disabled.

---

# Security

Production hardening includes:

- Secure filename handling
- UUID-based temporary upload filenames
- Temporary upload cleanup
- File extension validation
- Request validation
- JSON body validation
- Request size limits
- Generic error responses
- Server-side exception logging
- Production secret-key enforcement
- Debug mode disabled in production
- Download path validation
- Security response headers

Security headers include:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

Unexpected server exceptions are logged while preventing internal traceback details from being exposed to clients.

---

# Testing

The project uses pytest.

Run the complete test suite:

```powershell
python -m pytest
```

Run a specific test file:

```powershell
python -m pytest tests/test_resume_parser.py -v
```

Run tests matching a keyword:

```powershell
python -m pytest tests -k "rag" -v
```

## Production Validation

The project has undergone extensive regression, integration, UI, RAG, ATS, template, security, and end-to-end testing.

Latest full regression baseline:

```text
1956 passed, 0 failed


Latest production smoke-test validation:

6 passed, 0 failed

The production smoke-test suite validates production configuration,
secret-key enforcement, application creation, root endpoint availability,
API validation, and traceback protection.
```

---

# Production Smoke Testing

When Waitress is running:

```powershell
python -m waitress --listen=127.0.0.1:5000 --max-request-body-size=5242880 wsgi:app
```

Verify the application:

```powershell
Invoke-WebRequest `
    http://127.0.0.1:5000/ `
    -UseBasicParsing |
    Select-Object StatusCode
```

Expected:

```text
200
```

Invalid API requests should return appropriate validation responses such as:

```text
400
```

Security headers can be inspected with:

```powershell
$response = Invoke-WebRequest `
    http://127.0.0.1:5000/ `
    -UseBasicParsing

$response.Headers
```

---

# Deployment Checklist

Before deploying:

- [ ] Install dependencies from `requirements.txt`
- [ ] Configure production environment variables
- [ ] Set a strong production `SECRET_KEY`
- [ ] Configure the required LLM provider credentials
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=false`
- [ ] Verify RAG configuration
- [ ] Confirm generated files are not committed
- [ ] Confirm `.env` is not committed
- [ ] Run the complete pytest suite
- [ ] Start the application through Waitress
- [ ] Verify the home page
- [ ] Verify API validation
- [ ] Verify security headers
- [ ] Verify resume upload
- [ ] Verify resume generation
- [ ] Verify document download
- [ ] Review application logs

---

# Important Production Notes

## API Credentials

Never place API credentials directly in Python source code.

Use environment variables:

```text
OPENAI_API_KEY=
```

If an API credential is accidentally exposed, revoke or rotate it immediately.

## Debug Mode

Never enable Flask debug mode in production:

```text
FLASK_DEBUG=false
```

## Secret Key

Production requires:

```text
SECRET_KEY=<strong-random-secret>
```

Do not use the development fallback secret in production.

## Uploaded Files

Uploaded resumes contain potentially sensitive user information.

Production deployments should therefore use appropriate:

- Access controls
- File retention policies
- Storage controls
- Logging policies
- Data protection practices

---

# Application Workflow

The overall workflow is:

```text
Resume
   │
   ▼
Resume Parsing
   │
   ▼
Resume Structuring
   │
   ▼
Job Description Analysis
   │
   ▼
ATS Matching
   │
   ├──► Strengths
   ├──► Weaknesses
   ├──► Missing Skills
   └──► Missing Keywords
            │
            ▼
     Tailoring Plan
            │
            ▼
      AI Rewriting
            │
            ▼
     Content Selection
            │
            ▼
     Content Prioritization
            │
            ▼
       Length Control
            │
            ▼
      Section Ordering
            │
            ▼
      Final Validation
            │
            ▼
    Template Rendering
            │
            ▼
       DOCX / PDF
```

When RAG is enabled, knowledge retrieval and grounding can be incorporated into the optimization workflow.

---

# Project Validation Milestones

The project has progressed through multiple development phases covering:

- Foundation and Flask architecture
- Resume parsing
- Resume structuring
- Job description analysis
- ATS matching
- Recommendations
- Resume tailoring
- AI rewriting
- Optimized resume generation
- RAG
- Finalization
- Professional templates
- ATS validation
- UI implementation
- End-to-end testing
- Production hardening
- Deployment validation

The current development effort is focused on completing production-readiness and deployment documentation.

---

# License

Add the project's applicable license here before public distribution.

---

# Disclaimer

The ATS score and recommendations are automated analysis tools intended to assist with resume improvement.

They should not be treated as guarantees of interview selection, employment, or recruiter decisions.