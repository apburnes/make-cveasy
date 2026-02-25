"""Interactive prompt for selecting a job application."""

import sys
from pathlib import Path
from typing import Optional

from pick import pick

from cveasy.services import ApplicationService

# Sentinel returned when user selects "General resume (not job-specific)" in the picker.
GENERAL_RESUME_CHOICE = "__general__"

GENERAL_RESUME_LABEL = "General resume (not job-specific)"


def prompt_select_application(project_path: Path, include_general: bool = False) -> Optional[str]:
    """
    Prompt the user to select a job application from a list (arrow-key selection).

    Only runs when stdout is a TTY. When include_general is False, at least one
    application must exist; otherwise prints a helpful message and returns None.
    When include_general is True, the list always includes "General resume" so
    the prompt can run even with zero applications.

    Args:
        project_path: Path to the project directory.
        include_general: If True, prepend "General resume (not job-specific)" as
            first option; selecting it returns GENERAL_RESUME_CHOICE.

    Returns:
        The selected application ID, GENERAL_RESUME_CHOICE if general was chosen,
        or None if no selection (non-TTY, or no apps when include_general is False).
    """
    if not sys.stdout.isatty():
        print("Use --application when not running interactively.", file=sys.stderr)
        return None

    app_service = ApplicationService(project_path)
    application_ids = app_service.list_applications()

    if not include_general and not application_ids:
        print(
            "No job applications found. Add one with: cveasy add job --name <name>",
            file=sys.stderr,
        )
        return None

    options = []
    if include_general:
        options.append(GENERAL_RESUME_LABEL)
    for app_id in application_ids:
        job = app_service.storage.load_job(app_id)
        label = job.name if job else app_id
        options.append(f"{label} ({app_id})")

    selected_display, index = pick(
        options,
        "Select job application:",
        indicator="=>",
    )
    if include_general and index == 0:
        return GENERAL_RESUME_CHOICE
    if include_general:
        return application_ids[index - 1]
    return application_ids[index]
