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

# Install the CLI in development mode
uv pip install -e .
```

**Note:** `uv sync` automatically creates a virtual environment if one doesn't exist. You can also explicitly create one with `uv venv` first.

### Using pip

```bash
pip install -e .
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

### `cveasy export`
Export resume to PDF or Word.

```bash
cveasy export <resume-file> [--format pdf|docx] [--output <path>]
```

## Configuration

All commands support a `--project <path>` flag to specify the project directory if you're not running from within it.

## Environment Variables

Set these in your `.env` file:

- `CVEASY_AI_PROVIDER`: AI provider to use (`openai`, `anthropic`, or `openrouter`)
- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `OPENROUTER_API_KEY`: Your OpenRouter API key

## Development

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
