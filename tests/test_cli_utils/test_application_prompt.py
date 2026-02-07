"""Tests for application selection prompt."""

from unittest.mock import patch

from cveasy.cli_utils.application_prompt import (
    GENERAL_RESUME_CHOICE,
    GENERAL_RESUME_LABEL,
    prompt_select_application,
)
from cveasy.models.job import Job


def test_prompt_select_application_no_applications(temp_dir, storage):
    """Test that helper returns None and does not call pick when no applications exist."""
    with patch("cveasy.cli_utils.application_prompt.pick") as mock_pick:
        result = prompt_select_application(temp_dir)

    assert result is None
    mock_pick.assert_not_called()


def test_prompt_select_application_no_applications_prints_message(temp_dir, storage, capsys):
    """Test that helper prints helpful message when no applications exist."""
    # Ensure we reach the "no applications" branch (test runner often has non-TTY stdout)
    with patch("cveasy.cli_utils.application_prompt.sys.stdout.isatty", return_value=True):
        prompt_select_application(temp_dir)
    captured = capsys.readouterr()
    assert "No job applications found" in captured.err
    assert "cveasy add job" in captured.err


def test_prompt_select_application_non_tty_returns_none(temp_dir, storage):
    """Test that helper returns None when stdout is not a TTY."""
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python",
        pay="$150k",
        content="Job description",
    )
    storage.save_job(job, "test-app-20240101")

    with patch("cveasy.cli_utils.application_prompt.sys") as mock_sys:
        mock_sys.stdout.isatty.return_value = False
        with patch("cveasy.cli_utils.application_prompt.pick") as mock_pick:
            result = prompt_select_application(temp_dir)

    assert result is None
    mock_pick.assert_not_called()


def test_prompt_select_application_non_tty_prints_message(temp_dir, storage, capsys):
    """Test that helper prints message when not a TTY."""
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python",
        pay="$150k",
        content="Job description",
    )
    storage.save_job(job, "test-app-20240101")

    # Patch only isatty so stderr is still real and capsys captures the message
    with patch("cveasy.cli_utils.application_prompt.sys.stdout.isatty", return_value=False):
        prompt_select_application(temp_dir)

    captured = capsys.readouterr()
    assert "Use --application when not running interactively" in captured.err


def test_prompt_select_application_with_applications_returns_selected(temp_dir, storage):
    """Test that helper returns selected application ID when user picks one."""
    application_id = "software-engineer-20240101"
    job = Job(
        name="Software Engineer at Acme",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python",
        pay="$150k",
        content="Job description",
    )
    storage.save_job(job, application_id)

    # pick returns (selected_display_string, index)
    with patch("cveasy.cli_utils.application_prompt.sys") as mock_sys:
        mock_sys.stdout.isatty.return_value = True
        with patch("cveasy.cli_utils.application_prompt.pick") as mock_pick:
            mock_pick.return_value = (f"Software Engineer at Acme ({application_id})", 0)
            result = prompt_select_application(temp_dir)

    assert result == application_id
    mock_pick.assert_called_once()
    call_args = mock_pick.call_args
    assert "Select job application" in call_args[0][1]
    assert len(call_args[0][0]) == 1
    assert application_id in call_args[0][0][0]
    assert "Software Engineer at Acme" in call_args[0][0][0]


def test_prompt_select_application_display_includes_job_name(temp_dir, storage):
    """Test that pick is called with display strings that include job names."""
    application_id = "my-job-20240101"
    job = Job(
        name="Backend Developer",
        title="Backend Developer",
        location="NYC",
        requirements="Go",
        pay="$120k",
        content="Description",
    )
    storage.save_job(job, application_id)

    with patch("cveasy.cli_utils.application_prompt.sys") as mock_sys:
        mock_sys.stdout.isatty.return_value = True
        with patch("cveasy.cli_utils.application_prompt.pick") as mock_pick:
            mock_pick.return_value = (f"Backend Developer ({application_id})", 0)
            prompt_select_application(temp_dir)

    options = mock_pick.call_args[0][0]
    assert len(options) == 1
    assert options[0] == f"Backend Developer ({application_id})"


def test_prompt_select_application_include_general_first_option_returns_sentinel(temp_dir, storage):
    """Test that with include_general=True, selecting first option returns GENERAL_RESUME_CHOICE."""
    application_id = "test-app-20240101"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python",
        pay="$150k",
        content="Job description",
    )
    storage.save_job(job, application_id)

    with patch("cveasy.cli_utils.application_prompt.sys.stdout.isatty", return_value=True):
        with patch("cveasy.cli_utils.application_prompt.pick") as mock_pick:
            mock_pick.return_value = (GENERAL_RESUME_LABEL, 0)
            result = prompt_select_application(temp_dir, include_general=True)

    assert result == GENERAL_RESUME_CHOICE
    options = mock_pick.call_args[0][0]
    assert options[0] == GENERAL_RESUME_LABEL
    assert len(options) == 2  # General + one job app


def test_prompt_select_application_include_general_no_apps_returns_sentinel(temp_dir, storage):
    """Test that with include_general=True and no applications, selecting returns GENERAL_RESUME_CHOICE."""
    with patch("cveasy.cli_utils.application_prompt.sys.stdout.isatty", return_value=True):
        with patch("cveasy.cli_utils.application_prompt.pick") as mock_pick:
            mock_pick.return_value = (GENERAL_RESUME_LABEL, 0)
            result = prompt_select_application(temp_dir, include_general=True)

    assert result == GENERAL_RESUME_CHOICE
    options = mock_pick.call_args[0][0]
    assert len(options) == 1
    assert options[0] == GENERAL_RESUME_LABEL


def test_prompt_select_application_include_general_false_no_apps_returns_none(temp_dir, storage):
    """Test that with include_general=False and no applications, still returns None."""
    with patch("cveasy.cli_utils.application_prompt.pick") as mock_pick:
        result = prompt_select_application(temp_dir, include_general=False)

    assert result is None
    mock_pick.assert_not_called()
