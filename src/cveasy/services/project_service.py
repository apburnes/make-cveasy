"""Service for project initialization."""

import subprocess
from pathlib import Path
from typing import Optional
import frontmatter

from cveasy.exceptions import ProjectError, ValidationError


class ProjectService:
    """Service for initializing CVEasy projects."""

    def initialize_project(self, name: str, project_path: Optional[Path] = None) -> Path:
        """
        Initialize a new CVEasy project.

        Args:
            name: Name of the project directory.
            project_path: Optional base path. If None, uses current working directory.

        Returns:
            Path to the created project directory.

        Raises:
            ValidationError: If project path is invalid.
            ProjectError: If project initialization fails.
        """
        if project_path:
            # If project_path is specified, use that as the project path
            final_path = Path(project_path).resolve()
            if final_path.exists() and not final_path.is_dir():
                raise ValidationError(f"{final_path} exists but is not a directory.")
        else:
            # Otherwise, create directory with the specified name in current working directory
            final_path = Path.cwd() / name

        if final_path.exists():
            raise ValidationError(f"Directory {final_path} already exists.")

        # Create directory
        try:
            final_path.mkdir(parents=True, exist_ok=False)
        except OSError as e:
            raise ProjectError(f"Could not create directory {final_path}: {e}") from e

        # Initialize git
        try:
            subprocess.run(
                ["git", "init"], cwd=final_path, check=True, capture_output=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git not found or failed - not critical, continue
            pass

        # Create .gitignore file
        gitignore_content = """# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
        gitignore_path = final_path / ".gitignore"
        gitignore_path.write_text(gitignore_content, encoding="utf-8")

        # Create subdirectories
        subdirs = [
            "skills",
            "experiences",
            "stories",
            "links",
            "projects",
            "applications",
            "resume",
            "education",
        ]
        for subdir in subdirs:
            subdir_path = final_path / subdir
            subdir_path.mkdir(exist_ok=True)
            # Create .keep file to ensure directory is tracked by git
            (subdir_path / ".keep").touch()

        # Create README.md
        readme_content = """# CVEasy Resume Project

This project is managed using CVEasy, a CLI tool for managing resume data and generating customized resumes.

## Directory Structure

- `bio.md` - Your name and location
- `skills/` - Your skills and competencies
- `experiences/` - Work experience and positions
- `stories/` - Success stories and achievements
- `links/` - Professional links (LinkedIn, GitHub, etc.)
- `projects/` - Personal and professional projects
- `applications/` - Job applications with customized resumes
- `resume/` - General resume files
- `education/` - Educational background and credentials

## Getting Started

### 1. Configure AI Provider

You can configure your AI provider in two ways:

**Option A: Use the interactive config command (recommended):**

```bash
cveasy config
```

This will prompt you through setting up:
- `CVEASY_AI_PROVIDER` - AI provider (openai, anthropic, or openrouter)
- `CVEASY_API_KEY` - Your API key
- `CVEASY_MODEL` - Model name (optional, with provider-specific defaults)
- `CVEASY_MAX_TOKENS` - Maximum tokens (default: 8192)
- `CVEASY_SPACY_MODEL` - spaCy language model (default: en_core_web_sm)

**Option B: Manual configuration:**

The `cveasy init` command created a `.env.example` file. Copy it to `.env` and edit it:

```bash
cp .env.example .env
# Edit .env with your API keys
```

**Required configuration:**
- `CVEASY_AI_PROVIDER` - Must be set to one of: `openai`, `anthropic`, or `openrouter`
- `CVEASY_API_KEY` - Your API key for the selected provider

**Optional configuration:**
- `CVEASY_MODEL` - Model to use (provider-specific defaults: OpenAI: `gpt-4`, Anthropic: `claude-3-haiku-20240307`, OpenRouter: `openai/gpt-4`)
- `CVEASY_MAX_TOKENS` - Maximum tokens for responses (default: `8192`)
- `CVEASY_SPACY_MODEL` - spaCy language model for keyword and skills matching (default: `en_core_web_sm`)

See the [Configuration](#configuration) section below for detailed information.

### 2. Install spaCy Language Model

The spaCy language model is required for keyword and skills matching in the `cveasy check` command. Download the default model:

```bash
# Download the default spaCy model (en_core_web_sm)
python -m spacy download en_core_web_sm
```

**Note:** If you want to use a different model (e.g., `en_core_web_md` for semantic similarity), download it and set `CVEASY_SPACY_MODEL` in your `.env` file. Common options:
- `en_core_web_sm` - Small model (default, ~12MB, no word vectors)
- `en_core_web_md` - Medium model (~40MB, includes word vectors for semantic similarity)
- `en_core_web_lg` - Large model (~560MB, best quality word vectors)

### 3. Add Your Resume Data

You can add data manually or import from an existing resume:

**Option A: Import from existing resume (recommended for quick start)**

```bash
# Import from PDF or DOCX - automatically extracts skills, experiences, projects, stories, education, and links
cveasy import -f path/to/your/resume.pdf
# or
cveasy import -f path/to/your/resume.docx
```

**Option B: Add data manually**

```bash
# Add bio information
cveasy add bio --name "Your Name" --location "City, State"

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

# Add job applications (with automatic job description scraping)
cveasy add job --name "Software Engineer Position" --url "https://example.com/job"
```

### 4. Generate Resumes

```bash
# General resume (uses all your data)
cveasy generate

# Customized for a specific job application
cveasy generate --application software-engineer-20240115

# Update resume based on check report feedback
cveasy generate --application software-engineer-20240115 --update
```

### 5. Check Resume Quality

Analyze how well your resume matches a job description:

```bash
cveasy check --application software-engineer-20240115
```

This command:
- Automatically generates a resume if one doesn't exist for the application
- Performs keyword and skills matching
- Uses LLM to compare your resume against the job description
- Generates a detailed check report saved to `applications/{app-id}/check-report.md`

### 5. Generate Cover Letter

Create a personalized cover letter for a job application:

```bash
cveasy cover-letter --application software-engineer-20240115

# With optional reason for interest
cveasy cover-letter --application software-engineer-20240115 --reason "I'm excited about the company's mission"
```

### 6. Export Resume

Export your resume to PDF or Word format:

```bash
# Export application resume to PDF (default format)
cveasy export --application software-engineer-20240115 --format pdf

# Export application resume to Word
cveasy export --application software-engineer-20240115 --format docx --output resume.docx

# Export a specific resume file
cveasy export --file applications/software-engineer-20240115/resume.md --format pdf

# Export general resume
cveasy export --file resume/resume-20240115.md --format docx
```

## Commands

### `cveasy config`

Configure CVEasy environment variables interactively.

```bash
cveasy config
cveasy config --project /path/to/project
```

**What it does:**
- Prompts you through setting up `CVEASY_AI_PROVIDER`, `CVEASY_API_KEY`, `CVEASY_MODEL`, `CVEASY_MAX_TOKENS`, and `CVEASY_SPACY_MODEL`
- Saves configuration to `.env` file in your project root
- Preserves existing variables and comments in `.env` file

### `cveasy add`

Add resume data entries. All subcommands support the `--project <path>` flag.

#### `cveasy add bio`
Add or update your bio information (name and location).
```bash
cveasy add bio --name "Your Name" [--location "City, State"]
```

#### `cveasy add skill`
Add a new skill entry.
```bash
cveasy add skill --name "Python"
```
After creation, edit the file to add category, years of experience, proficiency level, and description.

#### `cveasy add experience`
Add a new work experience entry.
```bash
cveasy add experience --name "Senior Software Engineer"
```
After creation, edit the file to add organization, dates, location, and description.

#### `cveasy add story`
Add a new success story or achievement.
```bash
cveasy add story --name "Led Migration to Microservices"
```
After creation, edit the file to add context, outcome, and detailed description.

#### `cveasy add link`
Add a professional link (LinkedIn, GitHub, portfolio, etc.).
```bash
cveasy add link --name "LinkedIn" --description "Professional profile" --url "https://linkedin.com/in/username"
```

#### `cveasy add project`
Add a new project entry.
```bash
cveasy add project --name "E-commerce Platform" --description "Full-stack application" [--link "https://github.com/user/project"]
```

#### `cveasy add education`
Add a new education entry.
```bash
cveasy add education --name "Bachelor of Science in Computer Science" --organization "University Name" --degree "Bachelor of Science" [--start_date "2018-09-01"] [--end_date "2022-05-15"]
```

#### `cveasy add job`
Add a new job application. Automatically scrapes job description from URL.
```bash
cveasy add job --name "Software Engineer Position" --url "https://example.com/job"
```

### `cveasy import`

Import resume data from PDF or DOCX files. Uses AI to automatically extract and parse skills, experiences, projects, stories, education, links, and bio from your existing resume.

```bash
cveasy import -f resume.pdf
cveasy import --file resume.docx
cveasy import -f /path/to/resume.pdf --project /path/to/project
```

**What it does:**
- Extracts text from PDF or DOCX files
- Uses AI to parse and structure the resume content
- Automatically creates: bio, skills, experiences, projects, stories, education entries, and links
- Skips any entries that already exist (won't overwrite)
- Displays import statistics and token usage

### `cveasy generate`

Generate resumes using AI.

```bash
# General resume (uses all your data)
cveasy generate

# Customized for a job application
cveasy generate --application software-engineer-20240115

# Update based on check report
cveasy generate --application software-engineer-20240115 --update
```

### `cveasy check`

Check resume quality against job description.

```bash
cveasy check --application software-engineer-20240115
```

**What it does:**
- Automatically generates a resume if one doesn't exist for the application
- Performs keyword matching analysis
- Performs skills matching analysis
- Uses LLM to compare your resume against the job description
- Generates a detailed check report saved to `applications/{app-id}/check-report.md`
- Displays token usage statistics

### `cveasy cover-letter`

Generate personalized cover letters for job applications using AI.

```bash
# Generate cover letter for a job application
cveasy cover-letter --application software-engineer-20240115

# Generate cover letter with a reason for interest
cveasy cover-letter --application software-engineer-20240115 --reason "I'm excited about the company's mission"
```

**What it does:**
- Generates a personalized cover letter based on your skills, stories, experience, education, and projects
- Tailors the cover letter to the specific job application
- Incorporates optional reason for interest if provided
- Ensures the cover letter is no more than 500 words
- Saves cover letter to `applications/{app-id}/cover-letter.md`
- Displays token usage statistics

### `cveasy export`

Export resume to PDF or Word document.

```bash
# Export application resume to PDF (default format)
cveasy export --application software-engineer-20240115 --format pdf

# Export application resume to Word
cveasy export --application software-engineer-20240115 --format docx --output resume.docx

# Export a specific resume file
cveasy export --file applications/software-engineer-20240115/resume.md --format pdf

# Export general resume
cveasy export --file resume/resume-20240115.md --format docx
```

## Configuration

### Option 1: Interactive Configuration (Recommended)

Use the `cveasy config` command to configure your environment variables interactively:

```bash
cveasy config
```

This will prompt you through setting up all required configuration.

### Option 2: Manual Configuration

### Step 1: Copy Environment File

```bash
cp .env.example .env
```

### Step 2: Configure AI Provider

Edit the `.env` file and set the required variables:

**Required:**
- `CVEASY_AI_PROVIDER` - Must be set to one of: `openai`, `anthropic`, or `openrouter`
- `CVEASY_API_KEY` - Your API key for the selected provider

**Optional:**
- `CVEASY_MODEL` - Model to use (provider-specific defaults)
  - OpenAI default: `gpt-4` (common: `gpt-4`, `gpt-4-turbo`, `gpt-4o`, `gpt-3.5-turbo`)
  - Anthropic default: `claude-3-haiku-20240307` (common: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`)
  - OpenRouter default: `openai/gpt-4` (format: `provider/model-name`, e.g., `openai/gpt-4`, `anthropic/claude-3-opus`)
- `CVEASY_MAX_TOKENS` - Maximum tokens for responses (default: `8192`)
- `CVEASY_SPACY_MODEL` - spaCy language model for keyword and skills matching (default: `en_core_web_sm`)
  - Must be downloaded before use: `python -m spacy download <model-name>`
  - Common options: `en_core_web_sm` (default), `en_core_web_md`, `en_core_web_lg`

### Example `.env` File

```env
# AI Provider Configuration (REQUIRED)
CVEASY_AI_PROVIDER=openai

# Unified API Configuration
CVEASY_API_KEY=sk-your-key-here

# Model Configuration (optional)
CVEASY_MODEL=gpt-4

# Maximum tokens (optional, defaults to 8192)
CVEASY_MAX_TOKENS=8192

# spaCy Model Configuration (optional, defaults to en_core_web_sm)
# Required for keyword and skills matching. Download with: python -m spacy download en_core_web_sm
CVEASY_SPACY_MODEL=en_core_web_sm
```

**Important:** The `.env` file is already in `.gitignore` and will not be committed to version control. Never commit your API keys.

**Privacy Note:** If you do not want your job applications to be tracked in git history (so others cannot see which jobs you have applied to), add `applications/` to your `.gitignore` file.

## Complete Workflow Example

```bash
# 1. Initialize project (already done)
# cveasy init -n my-resume
# cd my-resume

# 2. Configure API keys
cp .env.example .env
# Edit .env with your API keys

# 3. Import existing resume or add data manually
cveasy import -f ~/Documents/resume.pdf

# 4. Add a new job application
cveasy add job --name "Senior Software Engineer at TechCorp" --url "https://techcorp.com/jobs/senior-engineer"

# 5. Generate customized resume
cveasy generate --application senior-software-engineer-at-techcorp-20240115

# 6. Check resume quality
cveasy check --application senior-software-engineer-at-techcorp-20240115

# 7. Review check report and improve resume
cveasy generate --application senior-software-engineer-at-techcorp-20240115 --update

# 8. Generate cover letter
cveasy cover-letter --application senior-software-engineer-at-techcorp-20240115

# 9. Export final resume
cveasy export --application senior-software-engineer-at-techcorp-20240115 --format pdf
```

For more information, visit: https://github.com/apburnes/make-cveasy
"""
        readme_path = final_path / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")

        # Create .env.example
        env_example_content = """# AI Provider Configuration
# Set CVEASY_AI_PROVIDER to: openai, anthropic, or openrouter
# This is REQUIRED - the tool will not work without it

CVEASY_AI_PROVIDER=openai

# Unified API Configuration
# CVEASY_API_KEY is used for all providers (OpenAI, Anthropic, OpenRouter)
CVEASY_API_KEY=your_api_key_here

# Model Configuration (optional)
# Default models by provider:
#   OpenAI: gpt-4
#   Anthropic: claude-3-haiku-20240307
#   OpenRouter: openai/gpt-4
# Common OpenAI models: gpt-4, gpt-4-turbo, gpt-4o, gpt-3.5-turbo
# Common Anthropic models: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
# OpenRouter format: provider/model-name (e.g., openai/gpt-4, anthropic/claude-3-opus)
CVEASY_MODEL=gpt-4

# Maximum tokens for responses (optional, defaults to 8192)
# Note: Model limits vary (claude-3-5-sonnet supports 8192, older models typically 4096)
CVEASY_MAX_TOKENS=8192

# spaCy Model Configuration (optional, defaults to en_core_web_sm)
# Required for keyword and skills matching. Download with: python -m spacy download en_core_web_sm
# Other options: en_core_web_md, en_core_web_lg (larger models with word vectors)
CVEASY_SPACY_MODEL=en_core_web_sm
"""
        env_example_path = final_path / ".env.example"
        env_example_path.write_text(env_example_content, encoding="utf-8")

        # Create bio.md file
        bio_content = frontmatter.Post(content="", name="", location="")
        bio_path = final_path / "bio.md"
        with open(bio_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(bio_content))

        return final_path
