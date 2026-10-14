# AI Resume Analyzer

An AI-powered web application that analyzes resumes against job descriptions, provides ATS-style compatibility insights, identifies skill gaps, recommends improvements, and generates job-description-optimized resumes.

## Current Status

**Phase 24 — Provider Testing, Configuration, Documentation & Regression (Validated)**

Completed capabilities include:

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
- LLM provider abstraction and runtime switching
- OpenAI-compatible, local, and Anthropic provider support
- Embedding provider abstraction


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

Current scoring weights:

| Category | Weight |
|---|---:|
| Skills | 50% |
| Experience | 20% |
| Qualifications | 15% |
| Keywords | 15% |
| **Total** | **100%** |

The analyzer also identifies matching skills, missing skills, matching keywords, resume strengths, resume weaknesses, and improvement opportunities.

### Resume Improvement

Recommendations can address:

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

### Job-Description-Optimized Resume Generation

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

## Retrieval-Augmented Generation (RAG)

The application includes RAG support for knowledge-grounded resume optimization.

RAG components include:

- Document loading and parsing
- Document cleaning and chunking
- Embedding support
- In-memory vector storage
- Retrieval services
- Job-description-aware retrieval
- Resume-aware retrieval
- Knowledge-base persistence
- Grounding validation
- RAG optimization orchestration

RAG can be enabled or disabled through configuration.

The built-in local embedding provider generates deterministic SHA-256-based vectors. It does not call an external embedding API. Changing `RAG_EMBEDDING_MODEL` does not change the local embedding algorithm.

Only the local embedding provider is registered by default. Other embedding providers must be registered and implemented separately.

## Professional Resume Templates

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

## Web Application

The Flask application provides:

- Resume upload
- Job description submission
- ATS analysis
- Resume rewriting
- Optimized resume generation
- Resume download
- Validation results
- Generation progress and state
- Template selection
- Error handling
- Responsive UI

## Technology Stack

### Backend

- Python
- Flask
- Waitress
- PyPDF
- python-docx
- ReportLab
- Pillow

### AI and NLP

- LLM-based resume rewriting
- ATS matching
- Retrieval-Augmented Generation
- Embeddings
- Knowledge retrieval
- Multiple LLM provider support

### Frontend

- HTML
- CSS
- JavaScript

### Testing

- pytest

### Configuration

- python-dotenv
- Environment variables

## Project Structure

Simplified project structure:

```text
AI Resume Analyzer/
├── app/
│   ├── ai/
│   ├── rag/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── ...
├── data/
├── frontend/
├── generated_rag/
├── generated_resumes/
├── tests/
├── uploads/
├── .env.example
├── .gitignore
├── app.py
├── config.py
├── requirements.txt
├── run.py
├── wsgi.py
└── README.md
```

Generated files and user uploads should be excluded from version control through `.gitignore`.

## Prerequisites

Recommended environment:

- Python 3.14+
- pip
- Git

An OpenAI API key is required only for functionality that uses the configured OpenAI provider. Other providers have their own configuration requirements.

Never commit API keys or other secrets to source control.

## Installation

### 1. Clone the repository

```powershell
git clone <repository-url>
cd "AI Resume Analyzer"
```

Replace `<repository-url>` with your repository URL.

### 2. Create a virtual environment

```powershell
python -m venv venv
```

Activate it in Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell execution policy prevents activation, use the appropriate environment activation method for your system.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
## Running in Development

Start the Flask application using the development entry point:

```powershell
python run.py
```

Use the development server only for local development.

## Running in Production

The project provides a WSGI entry point in `wsgi.py`, which exposes the application through `create_app()`.

Start the application using Waitress:

```powershell
python -m waitress --listen=127.0.0.1:5000 --max-request-body-size=5242880 wsgi:app
```

The application will be available at `http://127.0.0.1:5000`. The configured request body limit is 5 MB.

For a real deployment, configure network binding for the hosting environment and use an appropriate network security layer or reverse proxy where required.

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Serves the web application |
| `/api/resume/upload` | POST | Uploads and processes a resume |
| `/api/job-description` | POST | Analyzes a job description |
| `/api/analyze` | POST | Analyzes resume compatibility |
| `/api/resume/rewrite` | POST | Performs AI-assisted resume rewriting |
| `/api/resume/generate` | POST | Generates an optimized resume in DOCX and PDF formats |
| `/api/resume/download` | GET | Downloads a generated document using the `filename` query parameter |

Request formats, validation requirements, and response details are defined by the corresponding Flask route handlers.

## Environment Configuration

Create a `.env` file in the project root. Use `.env.example` as the configuration template.

Do not commit `.env` or real credentials.

### Production Requirements

- Configure the application using the project's supported production configuration.
- Set a strong, randomly generated `SECRET_KEY`.
- Keep `FLASK_DEBUG=false` in production.
- Never commit `.env` or real API credentials.

The application must be configured according to its production startup requirements before deployment.

### LLM Provider Configuration

Configure the LLM provider through environment variables:

```dotenv
LLM_PROVIDER=openai
LLM_MODEL=
LLM_API_KEY=
LLM_BASE_URL=
```

Built-in provider identifiers:

| Provider | `LLM_PROVIDER` value | Configuration requirements |
|---|---|---|
| OpenAI | `openai` | API key and model |
| OpenAI-compatible API | `openai_compatible` | API key, model, and base URL |
| Local LLM server | `local` | Model and base URL; API key is optional |
| Anthropic | `anthropic` | API key and model |

Registered custom providers can also be selected through the provider registry, provided their constructors and configuration requirements are satisfied.

### Legacy OpenAI Configuration

The application retains compatibility with these environment variables:

```dotenv
OPENAI_API_KEY=
OPENAI_MODEL=
```

When `LLM_PROVIDER` is unset, the default provider is `openai`.

The legacy `OPENAI_API_KEY` and `OPENAI_MODEL` values are used as fallbacks when the corresponding generic `LLM_API_KEY` and `LLM_MODEL` values are absent or empty.

`LLM_BASE_URL` is used for providers that require a custom endpoint.

Keep API keys secret and never commit credentials to source control.

### RAG Configuration

Enable RAG:

```dotenv
RAG_ENABLED=true
```

Disable RAG:

```dotenv
RAG_ENABLED=false
```

Embedding configuration:

```dotenv
RAG_EMBEDDING_PROVIDER=local
RAG_EMBEDDING_MODEL=default
RAG_EMBEDDING_DIMENSION=384
```

Boolean values for `RAG_ENABLED` must use a supported true value (`1`, `true`, `yes`, `on`) or false value (`0`, `false`, `no`, `off`). Invalid values raise a configuration error.

The local embedding provider uses deterministic SHA-256-based vectors. The model setting is forwarded to registered providers that implement model selection, but it does not change the local provider's algorithm.

Only the local embedding provider is registered by default.

Optional persisted knowledge index:

```dotenv
RAG_KNOWLEDGE_INDEX_PATH=
```

RAG functionality is designed to remain compatible with RAG disabled.

## Security

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

## Testing

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

The project has undergone regression, integration, UI, RAG, ATS, template, security, and end-to-end testing.

- Historical Phase 23 regression baseline: **2,168 passed, 0 failed**
- Phase 24 full regression: **2,174 passed, 0 failed**

The reported Phase 24 regression validated the application and test changes. The final README-only updates are documentation changes and do not alter application behavior.

## Production Smoke Testing

Start Waitress using:

```powershell
python -m waitress --listen=127.0.0.1:5000 --max-request-body-size=5242880 wsgi:app
```

Verify the application in another PowerShell window:

```powershell
(Invoke-WebRequest http://127.0.0.1:5000/ -UseBasicParsing).StatusCode
```

Expected status code:

```text
200
```

Invalid API requests should return appropriate validation responses, such as `400`, depending on the endpoint and request.

Inspect security headers:

```powershell
$response = Invoke-WebRequest http://127.0.0.1:5000/ -UseBasicParsing
$response.Headers
```

## Deployment Checklist

Before deploying:

- [ ] Install dependencies from `requirements.txt`
- [ ] Configure production environment variables
- [ ] Set a strong production `SECRET_KEY`
- [ ] Configure the required LLM provider credentials
- [ ] Set the appropriate production Flask configuration
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

## Important Production Notes

### API Credentials

Never place API credentials directly in Python source code.

Use environment variables:

```dotenv
OPENAI_API_KEY=
```

If an API credential is accidentally exposed, revoke or rotate it immediately.

### Debug Mode

Never enable Flask debug mode in production:

```dotenv
FLASK_DEBUG=false
```

### Secret Key

Production requires a strong, randomly generated secret key:

```dotenv
SECRET_KEY=<strong-random-secret>
```

Do not use the development fallback secret in production.

### Uploaded Files

Uploaded resumes contain potentially sensitive user information.

Production deployments should implement appropriate:

- Access controls
- File retention policies
- Storage controls
- Logging policies
- Data protection practices

## Application Workflow

The overall workflow is:

```text
Resume
  |
  v
Resume Parsing
  |
  v
Resume Structuring
  |
  v
Job Description Analysis
  |
  v
ATS Matching
  |
  +----> Strengths
  +----> Weaknesses
  +----> Missing Skills
  +----> Missing Keywords
  |
  v
Tailoring Plan
  |
  v
AI Rewriting
  |
  v
Content Selection
  |
  v
Content Prioritization
  |
  v
Length Control
  |
  v
Section Ordering
  |
  v
Final Validation
  |
  v
Template Rendering
  |
  v
DOCX / PDF
```

When RAG is enabled, knowledge retrieval and grounding can be incorporated into the optimization workflow.

## Project Validation Milestones

The project has progressed through development phases covering:

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
- LLM provider expansion
- Embedding provider abstraction
- Provider configuration and documentation

Phase 24 completed provider configuration hardening, embedding-provider validation, documentation updates, and full regression testing.

## License

Add the project's applicable license here before public distribution.

## Disclaimer

The ATS score and recommendations are automated analysis tools intended to assist with resume improvement.

They should not be treated as guarantees of interview selection, employment, or recruiter decisions.