# CVEasy

CLI tool for managing resume data and generating customized resumes for job applications using AI.

## Features

- **Project-based structure**: Manage all your resume data in a single Git-friendly project
- **Relationship tracking**: Link skills and stories to experiences via frontmatter metadata
- **AI-powered generation**: Generate customized resumes using OpenAI, Anthropic, or OpenRouter
- **Job application management**: Track multiple job applications with custom resumes
- **Quality checks**: Keyword and skills matching with LLM comparison for resume optimization
- **Iterative improvement**: Update resumes based on check reports
- **Export capabilities**: Export resumes to PDF or Word documents
- **Resume import**: Import resume data from existing PDF or DOCX files using AI parsing
- **Job description scraping**: Automatically extract job details from URLs

## Installation

### Using UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone or navigate to the project
cd resume-ops

# Create virtual environment (optional - uv sync will create one automatically)
uv venv

# Install dependencies and create virtual environment if needed
uv sync

## Install dev dependencies
uv sync --extra dev

# Install the CLI in development mode
uv pip install -e .

## or
uv pip install -r pyproject.toml

# Install dev dependencies (pytest, etc.) for development
uv sync --extra dev

# Download spaCy language model (required for keyword and skills matching)
## With UV
uv run python -m spacy download en_core_web_sm

## With python
python -m spacy download en_core_web_sm
```

**Note:** `uv sync` automatically creates a virtual environment if one doesn't exist. You can also explicitly create one with `uv venv` first.

### Using pip

```bash
pip install -e .

# Install dev dependencies (pytest, etc.) for development
pip install -e ".[dev]"

# Download spaCy language model (required for keyword and skills matching)
python -m spacy download en_core_web_sm
```

## Quick Start

### 1. Initialize a Project

```bash
cveasy init -n my-resume
cd my-resume
```

### 2. Configure AI Provider

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Add Your Resume Data

You can add data manually or import from an existing resume:

**Option A: Import from existing resume (recommended for quick start)**
```bash
# Import from PDF or DOCX - automatically extracts skills, experiences, projects, stories, and education
cveasy import -f path/to/your/resume.pdf
# or
cveasy import -f path/to/your/resume.docx
```

**Option B: Add data manually**
```bash
# Add skills
cveasy add skill --name "Python"
cveasy add skill --name "AWS"

# Add experiences
cveasy add experience --name "Senior Software Engineer"

# Add stories
cveasy add story --name "Led Migration to Microservices"

# Add links
cveasy add link --name "LinkedIn" --description "Professional profile" --url "https://linkedin.com/in/username"

# Add projects
cveasy add project --name "E-commerce Platform" --description "Full-stack application" --link "https://github.com/user/project"

# Add education
cveasy add education --name "Bachelor of Science in Computer Science" --organization "University Name" --degree "Bachelor of Science" --start_date "2018-09-01" --end_date "2022-05-15"

# Add job applications
cveasy add job --name "Software Engineer Position" --url "https://example.com/job"
```

### 4. Generate Resumes

```bash
# General resume
cveasy generate

# Customized for a job application
cveasy generate --application software-engineer-20240115
```

### 5. Check Resume Quality

```bash
cveasy check software-engineer-20240115
```

### 6. Improve Resume

```bash
# Update resume based on check report
cveasy generate --application software-engineer-20240115 --update
```

### 7. Export Resume

```bash
# Export to PDF (default)
cveasy export applications/software-engineer-20240115/resume.md --format pdf

# Export to Word
cveasy export applications/software-engineer-20240115/resume.md --format docx --output resume.docx
```

## Project Structure

```
my-resume/
├── skills/              # Your skills and competencies
├── experiences/         # Work experience and positions
├── stories/            # Success stories and achievements
├── links/              # Professional links (LinkedIn, GitHub, etc.)
├── projects/           # Personal and professional projects
├── education/          # Educational background and credentials
├── applications/       # Job applications with customized resumes
│   └── {app-id}/
│       ├── job-description.md
│       ├── resume.md
│       └── check-report.md
└── resume/             # General resume files
    └── resume-{date}.md
```

## Commands

### `cveasy init`
Initialize a new CVEasy project.

```bash
cveasy init -n <project-name>
```

### `cveasy add`
Add resume data entries.

```bash
cveasy add skill --name <name>
cveasy add experience --name <name>
cveasy add story --name <name>
cveasy add link --name <name> --description <desc> --url <url>
cveasy add project --name <name> --description <desc> [--link <url>]
cveasy add education --name <name> [--start_date <date>] [--end_date <date>] [--degree <degree>] [--certificate <cert>] [--organization <org>]
cveasy add job --name <name> [--url <url>]
```

### `cveasy generate`
Generate resumes using AI.

```bash
# General resume
cveasy generate

# Customized for job application
cveasy generate --application <app-id>

# Update based on check report
cveasy generate --application <app-id> --update
```

### `cveasy check`
Check resume quality against job description.

```bash
cveasy check <application-id>
```

### `cveasy import`
Import resume data from PDF or DOCX files. Uses AI to automatically extract and parse skills, experiences, projects, stories, and education from your existing resume.

```bash
cveasy import -f <path-to-resume> [--project <path>]
```

The command will:
- Extract text from PDF or DOCX files
- Use AI to parse and structure the resume content
- Automatically create skills, experiences, projects, stories, and education
- Skip any entries that already exist (won't overwrite)

Examples:
```bash
cveasy import -f resume.pdf
cveasy import --file resume.docx
```

### `cveasy export`
Export resume to PDF or Word.

```bash
cveasy export <resume-file> [--format pdf|docx] [--output <path>]
```

## Configuration

All commands support a `--project <path>` flag to specify the project directory if you're not running from within it.

## Environment Variables

Set these in your `.env` file:

### Required

- `CVEASY_AI_PROVIDER`: AI provider to use (`openai`, `anthropic`, or `openrouter`) - **REQUIRED**

### Provider API Keys

- `OPENAI_API_KEY`: Your OpenAI API key (required if using OpenAI provider)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (required if using Anthropic provider)
- `OPENROUTER_API_KEY`: Your OpenRouter API key (required if using OpenRouter provider)

### Model Configuration (Optional)

- `OPENAI_MODEL`: OpenAI model to use (default: `gpt-4`)
  - Common options: `gpt-4`, `gpt-4-turbo`, `gpt-4o`, `gpt-3.5-turbo`
- `ANTHROPIC_MODEL`: Anthropic model to use (default: `claude-3-haiku-20240307`)
  - Common options: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`
- `ANTHROPIC_MAX_TOKENS`: Maximum tokens for Anthropic responses (default: `8192`)
  - Note: Older models typically support up to 4096 tokens, newer models support up to 8192
- `OPENROUTER_MODEL`: OpenRouter model to use (default: `openai/gpt-4`)
  - Format: `provider/model-name` (e.g., `openai/gpt-4`, `anthropic/claude-3-opus`)

## Development

### Installing Dev Dependencies

To run tests and use development tools, install the dev dependencies:

**Using UV:**
```bash
uv sync --extra dev
```

**Using pip:**
```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Coverage

```bash
pytest --cov=src/cveasy --cov-report=html
```

## License

MIT
