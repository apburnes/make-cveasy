# make-cveasy

Managing your resume in a single document and making endless copies to customize it for each job application is painful. Instead of juggling multiple versions, `cveasy` lets you maintain a single source of truth for your experiences and skills, then automatically generate and optimize customized resumes for any job application using git version control, keyword matching, and AI.

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
- **Token usage tracking**: Monitor AI API usage with detailed token metrics

## Installation

### Installing the CLI Tool

First, install the CVEasy CLI tool on your system:

#### Using UV (Recommended)

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd make-cveasy-cli

# Install dependencies and CLI in development mode
uv sync --extra dev
uv pip install -e .

# If downloading the spaCy model fails, you may need:
uv pip install -U pip setuptools wheel
```

**Note:** `uv sync` automatically creates a virtual environment if one doesn't exist. You can also explicitly create one with `uv venv` first.

#### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd make-cveasy-cli

# Install CLI and dependencies
pip install -e ".[dev]"
```

### Verifying Installation

After installation, verify the CLI is working:

```bash
cveasy --help
```

## Quick Start

### 1. Initialize a Project

Create a new CVEasy project:

```bash
## Generate you resume repository
cveasy init -n my-resume

## Navigate to the root of your resume repository
cd my-resume
```

This creates a project directory with organized subdirectories for skills, experiences, stories, links, projects, education, applications, and resume files. See [Project Structure](#project-structure) for details.

### 2. Configure AI Provider

Configure your AI provider using the interactive command:

```bash
cveasy config
```

Or manually: copy `.env.example` to `.env` and edit it with your API keys. See [Configuration](#configuration) for details.

### 3. Add Your Resume Data

Import from an existing resume (recommended):

```bash
cveasy import -f path/to/your/resume.pdf
```

Or add data manually using `cveasy add` commands. See [Commands](#commands) for all available options.

### 4. Generate and Optimize Resumes

```bash
# General resume (uses all your data)
cveasy generate

# Customized for a job application
cveasy generate --application software-engineer-20260125

# Check resume quality against job description
cveasy check --application software-engineer-20260125

# Update resume based on check report
cveasy generate --application software-engineer-20260125 --update

# Export to PDF or Word
cveasy export --application software-engineer-20260125 --format pdf
```

See [Commands](#commands) for detailed options and usage.

## Project Structure

```
my-resume/
├── bio.md                 # Your name and location
├── skills/                # Your skills and competencies
│   └── python-{hash}.md
├── experiences/           # Work experience and positions
│   └── senior-software-engineer-{hash}.md
├── stories/              # Success stories and achievements
│   └── led-migration-to-microservices-{hash}.md
├── links/                # Professional links (LinkedIn, GitHub, etc.)
│   └── linkedin-{hash}.md
├── projects/             # Personal and professional projects
│   └── e-commerce-platform-{hash}.md
├── education/            # Educational background and credentials
│   └── bachelor-of-science-in-computer-science-{hash}.md
├── applications/         # Job applications with customized resumes
│   └── software-engineer-20260125/
│       ├── job-description.md
│       ├── resume.md
│       └── check-report.md
├── resume/               # General resume files
│   └── resume-20260125.md
├── .env                  # Your API keys (not in git)
├── .env.example          # Example configuration
└── README.md             # Project documentation
```

### File Naming and Slugs

All resume data files (skills, experiences, stories, links, projects, education) are named using a **slug** attribute. The slug is a URL-safe string that:

- Converts the name/title to lowercase
- Replaces spaces with hyphens
- Appends a 6-character random hexadecimal hash at the end

For example:
- A skill named "Python Programming" might be saved as `python-programming-a1b2c3.md`
- An experience titled "Senior Software Engineer" might be saved as `senior-software-engineer-d4e5f6.md`

The slug is automatically generated when you create a new entry and is stored in the frontmatter of each markdown file. This ensures:
- **Unique filenames**: Even if two entries have similar names, they'll have different file names
- **URL-safe**: Slugs are safe to use in URLs and file systems
- **Backward compatibility**: Existing files without slugs will still load correctly, and slugs will be generated automatically

**Note**: The `bio.md` file uses a fixed filename and doesn't follow the slug naming pattern, though it still has a slug attribute stored in its frontmatter.

## Commands

### `cveasy config`

Configure CVEasy environment variables interactively.

**Options:**
- `--project <path>`: Project directory path (optional)

**Examples:**
```bash
cveasy config
cveasy config --project /path/to/project
```

Prompts you through setting up environment variables and saves them to `.env` in your project root.

### `cveasy init`

Initialize a new CVEasy project.

**Options:**
- `-n, --name <name>`: Name of the project directory (default: `my-cveasy-resume`)
- `--project <path>`: Path where to create the project directory (optional)

**Examples:**
```bash
cveasy init
cveasy init -n my-resume
cveasy init --name professional-resume
cveasy init -n my-resume --project /path/to/projects
```

Creates a project directory with required subdirectories, initializes a git repository, and sets up configuration files.

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

**Required flags:**
- `--name`: Link name
- `--description`: Link description
- `--url`: Link URL

#### `cveasy add project`

Add a new project entry.

```bash
cveasy add project --name "E-commerce Platform" --description "Full-stack application" [--link "https://github.com/user/project"]
```

**Required flags:**
- `--name`: Project name
- `--description`: Project description

**Optional flags:**
- `--link`: Project URL

#### `cveasy add education`

Add a new education entry.

```bash
cveasy add education --name "Bachelor of Science in Computer Science" [--organization "University Name"] [--degree "Bachelor of Science"] [--start_date "2018-09-01"] [--end_date "2022-05-15"] [--certificate "Certificate Name"]
```

**Required flags:**
- `--name`: Education name/title

**Optional flags:**
- `--organization`: School/institution name
- `--degree`: Degree type
- `--start_date`: Start date (YYYY-MM-DD)
- `--end_date`: End date (YYYY-MM-DD) or "Present"
- `--certificate`: Certificate name

#### `cveasy add job`

Add a new job application.

```bash
cveasy add job --name "Software Engineer Position" [--url "https://example.com/job"]
```

**Required flags:**
- `--name`: Job application name

**Optional flags:**
- `--url`: URL to scrape job description from

If `--url` is provided, the command automatically scrapes the job description from the URL. Otherwise, it creates an empty `job-description.md` file for manual entry.

The application ID is automatically generated as `{slugified-name}-{date}` (e.g., `software-engineer-20260125`).

### `cveasy generate`

Generate resumes using AI.

**Options:**
- `-a, --application <app-id>`: Application ID to generate customized resume for (optional)
- `-u, --update`: Update resume based on check report (requires `--application`)
- `-p, --project <path>`: Project directory path (optional)

**Examples:**
```bash
# Generate general resume from all available data
cveasy generate

# Generate customized resume for a job application
cveasy generate --application software-engineer-20260125
cveasy generate -a software-engineer-20260125

# Update resume based on check report recommendations
cveasy generate --application software-engineer-20260125 --update
cveasy generate -a software-engineer-20260125 -u
```

General resumes are saved to `resume/resume-{date}.md`, application resumes to `applications/{app-id}/resume.md`. All commands display token usage statistics.

### `cveasy cover-letter`

Generate personalized cover letters for job applications using AI.

**Options:**
- `-a, --application <app-id>`: Application ID to generate cover letter for (required)
- `-r, --reason <text>`: Optional reason for interest in the job application
- `-p, --project <path>`: Project directory path (optional)

**Examples:**
```bash
# Generate cover letter for a job application
cveasy cover-letter --application software-engineer-20260125
cveasy cover-letter -a software-engineer-20260125

# Generate cover letter with a reason for interest
cveasy cover-letter --application software-engineer-20260125 --reason "I'm excited about the company's mission"
cveasy cover-letter -a software-engineer-20260125 -r "I'm excited about the company's mission"
```

Generates a personalized cover letter (max 500 words) tailored to the job application and saves it to `applications/{app-id}/cover-letter.md`.

### `cveasy check`

Check resume quality against job description.

**Options:**
- `-a, --application <app-id>`: Application ID to run resume check for (required)
- `--project <path>`: Project directory path (optional)

**Examples:**
```bash
cveasy check --application software-engineer-20260125
cveasy check -a software-engineer-20260125
```

Automatically generates a resume if needed, performs keyword and skills matching, uses LLM to compare against the job description, and saves a detailed report to `applications/{app-id}/check-report.md`.

**Tip:** After reviewing the check report, run `cveasy generate --application <app-id> --update` to improve your resume.

### `cveasy import`

Import resume data from PDF or DOCX files. Uses AI to automatically extract and parse skills, experiences, projects, stories, education, links, and bio from your existing resume.

**Options:**
- `-f, --file <path>`: Path to PDF or DOCX resume file (required)
- `--project <path>`: Project directory path (optional)

**Examples:**
```bash
cveasy import -f resume.pdf
cveasy import --file resume.docx
cveasy import -f /path/to/resume.pdf --project /path/to/project
```

Extracts and parses resume content from PDF or DOCX files using AI, automatically creating bio, skills, experiences, projects, stories, education, and links. Skips existing entries to avoid overwriting.

### `cveasy export`

Export resume to PDF or Word document.

**Options:**
- `-a, --application <app-id>`: Application ID to export resume for
- `-f, --file <path>`: Path to resume markdown file
- `--format <format>`: Export format: `pdf` or `docx` (default: `pdf`)
- `--output <path>`: Output file path (optional, defaults to same location as source)
- `--project <path>`: Project directory path (optional)

**Important:** You must specify exactly one source: either `--application` or `--file`.

**Examples:**
```bash
# Export application resume to PDF (default)
cveasy export --application software-engineer-20260125

# Export application resume to Word
cveasy export --application software-engineer-20260125 --format docx --output resume.docx

# Export specific resume file
cveasy export --file applications/software-engineer-20260125/resume.md --format pdf

# Export general resume
cveasy export --file resume/resume-20260125.md --format docx
```

## Configuration

### Project Path

All commands support a `--project <path>` flag to specify the project directory if you're not running from within it. If not specified, CVEasy automatically searches for the project root by looking for:
- A `.git` directory with expected CVEasy subdirectories
- Required subdirectories (`skills`, `experiences`, `stories`, `links`, `projects`, `applications`)

The search starts from the current working directory and walks up the directory tree.

### Environment Variables

Configuration is managed through a `.env` file in your project root. You can configure it using the `cveasy config` command (recommended) or by manually editing the `.env` file.

CVEasy automatically loads the `.env` file from:
1. The project root directory
2. Any parent directory (searches up the directory tree)
3. The current working directory (fallback)

#### Required Configuration

**`CVEASY_AI_PROVIDER`** (required)
- AI provider to use: `openai`, `anthropic`, or `openrouter`
- Must be set for the CLI to work

**`CVEASY_API_KEY`** (required)
- Your API key for the selected provider
- Used for all providers (OpenAI, Anthropic, OpenRouter)

#### Optional Configuration

**`CVEASY_MODEL`** (optional)
- Model to use (provider-specific defaults)
- **OpenAI default**: `gpt-4`
  - Common options: `gpt-4`, `gpt-4-turbo`, `gpt-4o`, `gpt-3.5-turbo`
- **Anthropic default**: `claude-3-haiku-20240307`
  - Common options: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-3-sonnet-20240229`, `claude-3-haiku-20240307`
- **OpenRouter default**: `openai/gpt-4`
  - Format: `provider/model-name` (e.g., `openai/gpt-4`, `anthropic/claude-3-opus`)

**`CVEASY_MAX_TOKENS`** (optional)
- Maximum tokens for responses (default: `8192`)
- Note: Model limits vary (claude-3-5-sonnet supports 8192, older models typically 4096)

**Note:** The spaCy language model (`en_core_web_sm`) is automatically included and downloaded on first use. Required for the `cveasy check` command.

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
```

## Usage Examples

### Working with Multiple Projects

All commands support the `--project <path>` flag to work with projects from any directory:

```bash
cveasy add skill --name "Python" --project ~/resumes/tech-resume
cveasy generate --project ~/resumes/tech-resume
cveasy check --application engineer-20260125 --project ~/resumes/tech-resume
```

## Services (For Developers)

CVEasy is built with a service-oriented architecture. The following services handle different aspects of the application:

- **ResumeService**: Resume generation and management
  - `generate_general_resume()`: Generate resume from all available data
  - `generate_customized_resume()`: Generate resume customized for a job application
  - `update_resume_from_check_report()`: Update resume based on check report feedback

- **ApplicationService**: Job application management
  - `create_application()`: Create new job application with optional URL scraping
  - `scrape_job_description()`: Scrape job description from URL
  - `list_applications()`: List all job applications

- **DataService**: CRUD operations for resume data
  - `create_skill()`, `create_experience()`, `create_story()`, etc.
  - `create_or_update_bio()`: Manage bio information

- **ImportService**: Resume import from PDF/DOCX
  - `import_resume()`: Extract and parse resume from PDF or DOCX file

- **ExportService**: Resume export to PDF/Word
  - `export_application_resume()`: Export application resume
  - `export_file_resume()`: Export any resume markdown file

- **CheckService**: Resume quality checking
  - `check_resume()`: Perform comprehensive resume quality analysis

- **ProjectService**: Project initialization
  - `initialize_project()`: Create new CVEasy project structure

- **MeteringService**: Token usage tracking
  - Tracks AI API token usage across all operations

## Development

### Setting Up for Development

Follow the [Installation](#installation) instructions above. Development setup is the same as regular installation.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/cveasy --cov-report=html

# Run specific test file
pytest tests/test_commands/test_add.py

# Run with verbose output
pytest -v
```

### Code Quality

The project uses `ruff` for linting and formatting:

```bash
# Check code style
ruff check src/

# Format code
ruff format src/

# Check and fix
ruff check --fix src/
```

### Project Structure

```
make-cveasy-cli/
├── src/
│   └── cveasy/
│       ├── ai/              # AI provider implementations
│       ├── analysis/         # Resume analysis and checking
│       ├── commands/         # CLI command implementations
│       ├── models/           # Data models
│       ├── parsing/         # Resume parsing
│       ├── scraping/        # Web scraping utilities
│       ├── services/        # Business logic services
│       ├── storage/          # Data storage layer
│       ├── cli.py           # Main CLI entry point
│       └── config.py        # Configuration management
├── tests/                   # Test suite
├── example/                 # Example resume project
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

### Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `pytest`
4. Check code style: `ruff check src/`
5. Submit a pull request

## License

MIT
