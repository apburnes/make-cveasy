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
            (final_path / subdir).mkdir(exist_ok=True)

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

## Usage

### Adding Data

```bash
cveasy add bio --name "Your Name" --location "City, State"
cveasy add skill --name "Python"
cveasy add experience --name "Software Engineer"
cveasy add story --name "Led Migration"
cveasy add link --name "LinkedIn" --description "Professional profile" --url "https://linkedin.com/in/username"
cveasy add project --name "E-commerce Platform" --description "Full-stack application"
cveasy add education --name "Bachelor of Science in Computer Science" --organization "University Name" --degree "Bachelor of Science"
cveasy add job --name "Software Engineer Position" --url "https://example.com/job"
```

### Generating Resumes

```bash
# General resume
cveasy generate

# Customized for a job application
cveasy generate --application software-engineer-20240115

# Update based on check report
cveasy generate --application software-engineer-20240115 --update
```

### Checking Resume Quality

```bash
cveasy check software-engineer-20240115
```

### Exporting Resumes

```bash
cveasy export applications/software-engineer-20240115/resume.md --format pdf
cveasy export resume/resume-20240115.md --format docx
```

## Configuration

Create a `.env` file in this directory with your AI API keys:

```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
CVEASY_AI_PROVIDER=openai
```

For more information, visit: https://github.com/yourusername/cveasy
"""
        readme_path = final_path / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")

        # Create .env.example
        env_example_content = """# AI Provider Configuration
# Set CVEASY_AI_PROVIDER to: openai, anthropic, or openrouter
# This is REQUIRED - the tool will not work without it

CVEASY_AI_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
# OpenAI model to use (optional, defaults to gpt-4)
# Common models: gpt-4, gpt-4-turbo, gpt-3.5-turbo, gpt-4o, etc.
OPENAI_MODEL=gpt-4

# Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# Anthropic model to use (optional, defaults to claude-3-haiku-20240307)
# Common models: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
ANTHROPIC_MODEL=claude-3-haiku-20240307
# Maximum tokens for Anthropic responses (optional, defaults to 8192)
# Note: Older models (claude-3-opus, claude-3-sonnet, claude-3-haiku) typically support up to 4096 tokens
# Newer models (claude-3-5-sonnet) support up to 8192 tokens
ANTHROPIC_MAX_TOKENS=8192

# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
# OpenRouter model to use (optional, defaults to openai/gpt-4)
# Format: provider/model-name (e.g., openai/gpt-4, anthropic/claude-3-opus, etc.)
OPENROUTER_MODEL=openai/gpt-4
"""
        env_example_path = final_path / ".env.example"
        env_example_path.write_text(env_example_content, encoding="utf-8")

        # Create bio.md file
        bio_content = frontmatter.Post(content="", name="", location="")
        bio_path = final_path / "bio.md"
        with open(bio_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(bio_content))

        return final_path
