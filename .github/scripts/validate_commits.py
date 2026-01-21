#!/usr/bin/env python3
"""
Validate commit messages against Conventional Commits specification.

This script validates that all commit messages in a PR follow the
Conventional Commits format: type(scope): description

Valid types: feat, fix, docs, style, refactor, perf, test, chore, build, ci, deps
"""

import re
import sys
from typing import List, Tuple

# Valid commit types according to Conventional Commits
VALID_TYPES = {
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "chore",
    "build",
    "ci",
    "deps",
}

# Conventional Commits pattern:
# type(scope): description
# or
# type: description
#
# The scope is optional and must be in parentheses
# The description is required and must start with a space after the colon
CONVENTIONAL_COMMIT_PATTERN = re.compile(
    r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?:\s+(?P<description>.+)$"
)


def validate_commit_message(message: str) -> Tuple[bool, str]:
    """
    Validate a single commit message.

    Args:
        message: The commit message to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Remove leading/trailing whitespace
    message = message.strip()

    # Skip merge commits and empty messages
    if not message or message.startswith("Merge"):
        return True, ""

    # Check if message matches conventional commits pattern
    match = CONVENTIONAL_COMMIT_PATTERN.match(message)

    if not match:
        return False, (
            f"Commit message does not follow Conventional Commits format.\n"
            f"Expected format: type(scope): description\n"
            f"Example: feat(cli): add new command\n"
            f"Got: {message[:50]}"
        )

    commit_type = match.group("type")

    # Validate commit type
    if commit_type not in VALID_TYPES:
        return False, (
            f"Invalid commit type '{commit_type}'.\n"
            f"Valid types are: {', '.join(sorted(VALID_TYPES))}\n"
            f"Got: {message[:50]}"
        )

    # Validate description is not empty
    description = match.group("description")
    if not description or not description.strip():
        return False, (
            f"Commit message description is required.\n"
            f"Got: {message[:50]}"
        )

    return True, ""


def get_commit_messages(base_ref: str, head_ref: str) -> List[str]:
    """
    Get all commit messages between base and head refs.

    Args:
        base_ref: Base branch reference (e.g., main) or commit SHA
        head_ref: Head branch reference (e.g., feature-branch) or commit SHA

    Returns:
        List of commit messages
    """
    import subprocess

    try:
        # Fetch the base ref if it's a branch name (not a SHA)
        # SHAs are 40 characters, branch names are typically shorter
        if len(base_ref) < 40:
            try:
                subprocess.run(
                    ["git", "fetch", "origin", base_ref],
                    check=True,
                    capture_output=True,
                    timeout=30,
                )
                base_commit = f"origin/{base_ref}"
            except subprocess.CalledProcessError:
                # If fetch fails, use the ref as-is (might be a local branch)
                base_commit = base_ref
        else:
            # It's a SHA, use it directly
            base_commit = base_ref

        # Get commit messages between base and head
        # head_ref is typically a SHA in PR context
        result = subprocess.run(
            ["git", "log", f"{base_commit}..{head_ref}", "--pretty=format:%s"],
            check=True,
            capture_output=True,
            text=True,
        )

        messages = [msg for msg in result.stdout.strip().split("\n") if msg]
        return messages
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        print(f"Error getting commit messages: {error_msg}", file=sys.stderr)
        print(f"Base ref: {base_ref}, Head ref: {head_ref}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the validation script."""
    if len(sys.argv) < 3:
        print("Usage: validate_commits.py <base_ref> <head_ref>", file=sys.stderr)
        print("Example: validate_commits.py main feature-branch", file=sys.stderr)
        sys.exit(1)

    base_ref = sys.argv[1]
    head_ref = sys.argv[2]

    commit_messages = get_commit_messages(base_ref, head_ref)

    if not commit_messages:
        print("No commits found to validate.")
        sys.exit(0)

    errors = []
    for i, message in enumerate(commit_messages, 1):
        is_valid, error_msg = validate_commit_message(message)
        if not is_valid:
            errors.append(f"Commit {i}: {error_msg}")

    if errors:
        print("❌ Commit message validation failed:\n", file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
            print("", file=sys.stderr)
        print(
            "Please ensure all commit messages follow the Conventional Commits format:\n"
            "  type(scope): description\n\n"
            "Examples:\n"
            "  feat(cli): add new command\n"
            "  fix: resolve bug in parser\n"
            "  docs: update README\n"
            "  chore: update dependencies",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"✅ All {len(commit_messages)} commit message(s) are valid!")
    sys.exit(0)


if __name__ == "__main__":
    main()
