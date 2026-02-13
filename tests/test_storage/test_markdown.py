"""Tests for markdown storage."""

import pytest
from cveasy.models.skill import Skill
from cveasy.models.job import Job
from cveasy.models.bio import Bio


def test_save_and_load_skill(storage, sample_skill):
    """Test saving and loading a skill."""
    filepath = storage.save_skill(sample_skill)

    assert filepath.exists()

    loaded_skill = storage.load_skill("Python")

    assert loaded_skill is not None
    assert loaded_skill.name == sample_skill.name
    assert loaded_skill.category == sample_skill.category


def test_list_skills(storage, sample_skill):
    """Test listing skills."""
    storage.save_skill(sample_skill)

    skills = storage.list_skills()

    assert len(skills) == 1
    assert skills[0].name == "Python"


def test_save_and_load_education(storage, sample_education):
    """Test saving and loading an education."""
    filepath = storage.save_education(sample_education)

    assert filepath.exists()

    loaded_education = storage.load_education("Bachelor of Science in Computer Science")

    assert loaded_education is not None
    assert loaded_education.name == sample_education.name
    assert loaded_education.organization == sample_education.organization
    assert loaded_education.degree == sample_education.degree


def test_list_educations(storage, sample_education):
    """Test listing educations."""
    storage.save_education(sample_education)

    educations = storage.list_educations()

    assert len(educations) == 1
    assert educations[0].name == "Bachelor of Science in Computer Science"


def test_save_and_load_experience(storage, sample_experience):
    """Test saving and loading an experience."""
    filepath = storage.save_experience(sample_experience)

    assert filepath.exists()

    loaded_experience = storage.load_experience("Senior Software Engineer")

    assert loaded_experience is not None
    assert loaded_experience.title == sample_experience.title
    assert loaded_experience.organization == sample_experience.organization


def test_list_experiences(storage, sample_experience):
    """Test listing experiences."""
    storage.save_experience(sample_experience)

    experiences = storage.list_experiences()

    assert len(experiences) == 1
    assert experiences[0].title == "Senior Software Engineer"


def test_save_and_load_story(storage, sample_story):
    """Test saving and loading a story."""
    filepath = storage.save_story(sample_story)

    assert filepath.exists()

    loaded_story = storage.load_story("Led Migration to Microservices")

    assert loaded_story is not None
    assert loaded_story.title == sample_story.title
    assert loaded_story.context == sample_story.context


def test_list_stories(storage, sample_story):
    """Test listing stories."""
    storage.save_story(sample_story)

    stories = storage.list_stories()

    assert len(stories) == 1
    assert stories[0].title == "Led Migration to Microservices"


def test_save_and_load_link(storage, sample_link):
    """Test saving and loading a link."""
    filepath = storage.save_link(sample_link)

    assert filepath.exists()

    loaded_link = storage.load_link("LinkedIn")

    assert loaded_link is not None
    assert loaded_link.name == sample_link.name
    assert loaded_link.url == sample_link.url


def test_list_links(storage, sample_link):
    """Test listing links."""
    storage.save_link(sample_link)

    links = storage.list_links()

    assert len(links) == 1
    assert links[0].name == "LinkedIn"


def test_save_and_load_project(storage, sample_project):
    """Test saving and loading a project."""
    filepath = storage.save_project(sample_project)

    assert filepath.exists()

    loaded_project = storage.load_project("E-commerce Platform")

    assert loaded_project is not None
    assert loaded_project.name == sample_project.name
    assert loaded_project.description == sample_project.description


def test_list_projects(storage, sample_project):
    """Test listing projects."""
    storage.save_project(sample_project)

    projects = storage.list_projects()

    assert len(projects) == 1
    assert projects[0].name == "E-commerce Platform"


def test_save_and_load_job(storage, sample_job):
    """Test saving and loading a job."""
    application_id = "test-application-20240101"
    filepath = storage.save_job(sample_job, application_id)

    assert filepath.exists()

    loaded_job = storage.load_job(application_id)

    assert loaded_job is not None
    assert loaded_job.name == sample_job.name
    assert loaded_job.title == sample_job.title


def test_list_applications(storage, sample_job):
    """Test listing applications."""
    application_id1 = "test-app-1-20240101"
    application_id2 = "test-app-2-20240102"

    storage.save_job(sample_job, application_id1)
    storage.save_job(sample_job, application_id2)

    applications = storage.list_applications()

    assert len(applications) == 2
    assert application_id1 in applications
    assert application_id2 in applications


def test_save_and_load_bio(storage):
    """Test saving and loading a bio."""
    bio = Bio(name="John Doe", location="San Francisco, CA")
    filepath = storage.save_bio(bio)

    assert filepath.exists()

    loaded_bio = storage.load_bio()

    assert loaded_bio is not None
    assert loaded_bio.name == "John Doe"
    assert loaded_bio.location == "San Francisco, CA"


def test_load_bio_not_found(storage):
    """Test loading bio when file doesn't exist."""
    loaded_bio = storage.load_bio()
    assert loaded_bio is None


def test_save_resume_with_application_id(storage):
    """Test saving resume with application ID."""
    content = "# Resume\n\nThis is a resume with enough content to pass the minimum length validation check."
    application_id = "test-app-20240101"

    filepath = storage.save_resume(content, application_id=application_id)

    assert filepath.exists()
    assert filepath.name == "resume.md"
    assert application_id in str(filepath.parent)

    # Verify content
    loaded_content = storage.load_resume(application_id=application_id)
    assert loaded_content == content


def test_save_resume_general(storage):
    """Test saving general resume without application ID."""
    content = "# General Resume\n\nThis is a general resume with enough content to pass minimum length validation."

    filepath = storage.save_resume(content)

    assert filepath.exists()
    assert filepath.name.startswith("resume-")
    assert filepath.name.endswith(".md")

    # Verify content
    loaded_content = storage.load_resume()
    assert loaded_content == content


def test_load_resume_by_date(storage):
    """Test loading resume by date."""
    content = "# Resume\n\nContent here with enough text to pass the minimum length validation check."
    date = "20240101"

    storage.save_resume(content)

    # Manually create a resume with specific date
    resume_dir = storage.base_path / "resume"
    resume_dir.mkdir(exist_ok=True)
    resume_file = resume_dir / f"resume-{date}.md"
    resume_file.write_text(content)

    loaded_content = storage.load_resume(date=date)
    assert loaded_content == content


def test_load_resume_not_found(storage):
    """Test loading resume when it doesn't exist."""
    loaded_content = storage.load_resume(application_id="nonexistent")
    assert loaded_content is None


def test_save_and_load_check_report(storage):
    """Test saving and loading check report."""
    report_content = "# Check Report\n\nThis is a check report with enough content to pass minimum validation."
    application_id = "test-app-20240101"

    filepath = storage.save_check_report(report_content, application_id)

    assert filepath.exists()
    assert filepath.name == "check-report.md"

    loaded_report = storage.load_check_report(application_id)
    assert loaded_report == report_content


def test_load_check_report_not_found(storage):
    """Test loading check report when it doesn't exist."""
    loaded_report = storage.load_check_report("nonexistent")
    assert loaded_report is None


def test_save_cover_letter(storage):
    """Test saving cover letter to application directory."""
    cover_letter_content = "# Cover Letter\n\nThis is a cover letter with enough content to pass minimum length validation."
    application_id = "test-app-20240101"

    filepath = storage.save_cover_letter(cover_letter_content, application_id)

    assert filepath.exists()
    assert filepath.name == "cover-letter.md"
    assert application_id in str(filepath)

    # Verify content was saved correctly
    with open(filepath, "r", encoding="utf-8") as f:
        assert f.read() == cover_letter_content


def test_load_cover_letter(storage):
    """Test loading cover letter from application directory."""
    cover_letter_content = "# Cover Letter\n\nThis is a cover letter with enough content to pass minimum length validation."
    application_id = "test-app-20240101"

    storage.save_cover_letter(cover_letter_content, application_id)

    loaded_cover_letter = storage.load_cover_letter(application_id)
    assert loaded_cover_letter == cover_letter_content


def test_load_cover_letter_not_found(storage):
    """Test loading cover letter when it doesn't exist."""
    loaded_cover_letter = storage.load_cover_letter("nonexistent")
    assert loaded_cover_letter is None


def test_load_skill_not_found(storage):
    """Test loading skill when it doesn't exist."""
    loaded_skill = storage.load_skill("Nonexistent Skill")
    assert loaded_skill is None


def test_load_experience_not_found(storage):
    """Test loading experience when it doesn't exist."""
    loaded_experience = storage.load_experience("Nonexistent Experience")
    assert loaded_experience is None


def test_load_story_not_found(storage):
    """Test loading story when it doesn't exist."""
    loaded_story = storage.load_story("Nonexistent Story")
    assert loaded_story is None


def test_load_link_not_found(storage):
    """Test loading link when it doesn't exist."""
    loaded_link = storage.load_link("Nonexistent Link")
    assert loaded_link is None


def test_load_project_not_found(storage):
    """Test loading project when it doesn't exist."""
    loaded_project = storage.load_project("Nonexistent Project")
    assert loaded_project is None


def test_load_job_not_found(storage):
    """Test loading job when it doesn't exist."""
    loaded_job = storage.load_job("nonexistent-app")
    assert loaded_job is None


def test_load_education_not_found(storage):
    """Test loading education when it doesn't exist."""
    loaded_education = storage.load_education("Nonexistent Education")
    assert loaded_education is None


def test_list_skills_empty(storage):
    """Test listing skills when none exist."""
    skills = storage.list_skills()
    assert skills == []


def test_list_experiences_empty(storage):
    """Test listing experiences when none exist."""
    experiences = storage.list_experiences()
    assert experiences == []


def test_list_stories_empty(storage):
    """Test listing stories when none exist."""
    stories = storage.list_stories()
    assert stories == []


def test_list_links_empty(storage):
    """Test listing links when none exist."""
    links = storage.list_links()
    assert links == []


def test_list_projects_empty(storage):
    """Test listing projects when none exist."""
    projects = storage.list_projects()
    assert projects == []


def test_list_applications_empty(storage):
    """Test listing applications when none exist."""
    applications = storage.list_applications()
    assert applications == []


def test_list_educations_empty(storage):
    """Test listing educations when none exist."""
    educations = storage.list_educations()
    assert educations == []


def test_save_resume_empty_content(storage):
    """Test saving resume with empty content raises StorageError."""
    from cveasy.exceptions import StorageError

    content = ""
    application_id = "test-app-20240101"

    with pytest.raises(StorageError, match="Generated resume is empty"):
        storage.save_resume(content, application_id=application_id)


def test_save_check_report_empty_content(storage):
    """Test saving check report with empty content raises StorageError."""
    from cveasy.exceptions import StorageError

    content = ""
    application_id = "test-app-20240101"

    with pytest.raises(StorageError, match="Generated check report is empty"):
        storage.save_check_report(content, application_id)


def test_list_applications_filters_invalid_dirs(storage):
    """Test list_applications only returns directories with job-description.md."""
    application_id1 = "valid-app-20240101"
    application_id2 = "invalid-app-20240102"

    # Create valid application
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python",
        pay="$150k",
        content="Job description",
    )
    storage.save_job(job, application_id1)

    # Create directory without job-description.md
    (storage.base_path / "applications" / application_id2).mkdir(parents=True)

    applications = storage.list_applications()

    assert application_id1 in applications
    assert application_id2 not in applications


# Error handling tests


def test_save_skill_io_error(storage, sample_skill, monkeypatch):
    """Test that save_skill raises StorageError on IOError."""
    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save skill"):
        storage.save_skill(sample_skill)


def test_list_skills_io_error(storage, sample_skill, monkeypatch):
    """Test that list_skills raises StorageError on IOError."""
    storage.save_skill(sample_skill)

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load skill"):
        storage.list_skills()


def test_load_skill_backward_compatibility_by_search(storage, sample_skill):
    """Test loading skill by searching all files when slug doesn't match."""
    # Save skill with slug
    storage.save_skill(sample_skill)

    # Manually create a file with old naming (without hash) but correct name in frontmatter
    skills_dir = storage.base_path / "skills"
    old_file = skills_dir / "python.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_skill.content,
        **sample_skill.to_frontmatter_dict()
    )
    with open(old_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    # Should still be able to load by name
    loaded = storage.load_skill("Python")
    assert loaded is not None
    assert loaded.name == "Python"


def test_load_skill_name_mismatch_searches_all_files(storage, sample_skill):
    """Test that load_skill searches all files when name doesn't match."""
    # Save skill
    storage.save_skill(sample_skill)

    # Create a file with wrong slug but correct name in frontmatter
    skills_dir = storage.base_path / "skills"
    wrong_file = skills_dir / "wrong-slug.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_skill.content,
        **sample_skill.to_frontmatter_dict()
    )
    with open(wrong_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    # Should find it by searching all files
    loaded = storage.load_skill("Python")
    assert loaded is not None
    assert loaded.name == "Python"


def test_load_experience_backward_compatibility(storage, sample_experience):
    """Test loading experience by searching all files."""
    storage.save_experience(sample_experience)

    # Create old-style file
    experiences_dir = storage.base_path / "experiences"
    old_file = experiences_dir / "senior-software-engineer.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_experience.content,
        **sample_experience.to_frontmatter_dict()
    )
    with open(old_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    loaded = storage.load_experience("Senior Software Engineer")
    assert loaded is not None
    assert loaded.title == "Senior Software Engineer"


def test_list_experiences_io_error(storage, sample_experience, monkeypatch):
    """Test that list_experiences raises StorageError on IOError."""
    storage.save_experience(sample_experience)

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load experience"):
        storage.list_experiences()


def test_load_story_backward_compatibility(storage, sample_story):
    """Test loading story by searching all files."""
    storage.save_story(sample_story)

    # Create old-style file
    stories_dir = storage.base_path / "stories"
    old_file = stories_dir / "led-migration-to-microservices.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_story.content,
        **sample_story.to_frontmatter_dict()
    )
    with open(old_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    loaded = storage.load_story("Led Migration to Microservices")
    assert loaded is not None
    assert loaded.title == "Led Migration to Microservices"


def test_list_stories_io_error(storage, sample_story, monkeypatch):
    """Test that list_stories raises StorageError on IOError."""
    storage.save_story(sample_story)

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load story"):
        storage.list_stories()


def test_load_link_backward_compatibility(storage, sample_link):
    """Test loading link by searching all files."""
    storage.save_link(sample_link)

    # Create old-style file
    links_dir = storage.base_path / "links"
    old_file = links_dir / "linkedin.md"
    import frontmatter
    post = frontmatter.Post(
        content="",
        **sample_link.to_frontmatter_dict()
    )
    with open(old_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    loaded = storage.load_link("LinkedIn")
    assert loaded is not None
    assert loaded.name == "LinkedIn"


def test_list_links_io_error(storage, sample_link, monkeypatch):
    """Test that list_links raises StorageError on IOError."""
    storage.save_link(sample_link)

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load link"):
        storage.list_links()


def test_load_project_backward_compatibility(storage, sample_project):
    """Test loading project by searching all files."""
    storage.save_project(sample_project)

    # Create old-style file
    projects_dir = storage.base_path / "projects"
    old_file = projects_dir / "e-commerce-platform.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_project.content,
        **sample_project.to_frontmatter_dict()
    )
    with open(old_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    loaded = storage.load_project("E-commerce Platform")
    assert loaded is not None
    assert loaded.name == "E-commerce Platform"


def test_list_projects_io_error(storage, sample_project, monkeypatch):
    """Test that list_projects raises StorageError on IOError."""
    storage.save_project(sample_project)

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load project"):
        storage.list_projects()


def test_load_education_backward_compatibility(storage, sample_education):
    """Test loading education by searching all files."""
    storage.save_education(sample_education)

    # Create old-style file
    education_dir = storage.base_path / "education"
    old_file = education_dir / "bachelor-of-science-in-computer-science.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_education.content,
        **sample_education.to_frontmatter_dict()
    )
    with open(old_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    loaded = storage.load_education("Bachelor of Science in Computer Science")
    assert loaded is not None
    assert loaded.name == "Bachelor of Science in Computer Science"


def test_list_educations_io_error(storage, sample_education, monkeypatch):
    """Test that list_educations raises StorageError on IOError."""
    storage.save_education(sample_education)

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load education"):
        storage.list_educations()


def test_save_experience_io_error(storage, sample_experience, monkeypatch):
    """Test that save_experience raises StorageError on IOError."""
    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save experience"):
        storage.save_experience(sample_experience)


def test_save_story_io_error(storage, sample_story, monkeypatch):
    """Test that save_story raises StorageError on IOError."""
    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save story"):
        storage.save_story(sample_story)


def test_save_link_io_error(storage, sample_link, monkeypatch):
    """Test that save_link raises StorageError on IOError."""
    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save link"):
        storage.save_link(sample_link)


def test_save_project_io_error(storage, sample_project, monkeypatch):
    """Test that save_project raises StorageError on IOError."""
    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save project"):
        storage.save_project(sample_project)


def test_save_education_io_error(storage, sample_education, monkeypatch):
    """Test that save_education raises StorageError on IOError."""
    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save education"):
        storage.save_education(sample_education)


def test_save_job_io_error(storage, sample_job, monkeypatch):
    """Test that save_job raises StorageError on IOError."""
    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save job"):
        storage.save_job(sample_job, "test-app-20240101")


def test_load_job_io_error(storage, sample_job, monkeypatch):
    """Test that load_job raises StorageError on IOError."""
    application_id = "test-app-20240101"
    storage.save_job(sample_job, application_id)

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load job"):
        storage.load_job(application_id)


def test_save_bio_io_error(storage, monkeypatch):
    """Test that save_bio raises StorageError on IOError."""
    bio = Bio(name="John Doe", location="San Francisco, CA")

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save bio"):
        storage.save_bio(bio)


def test_load_bio_io_error(storage, monkeypatch):
    """Test that load_bio raises StorageError on IOError."""
    bio = Bio(name="John Doe", location="San Francisco, CA")
    storage.save_bio(bio)

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load bio"):
        storage.load_bio()


def test_save_resume_io_error(storage, monkeypatch):
    """Test that save_resume raises StorageError on IOError."""
    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save resume"):
        storage.save_resume(
            "# Resume\n\nThis is a resume with enough content to pass the minimum length validation check.",
            application_id="test-app-20240101",
        )


def test_load_resume_io_error(storage, monkeypatch):
    """Test that load_resume raises StorageError on IOError."""
    storage.save_resume(
        "# Resume\n\nThis is a resume with enough content to pass the minimum length validation check.",
        application_id="test-app-20240101",
    )

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load resume"):
        storage.load_resume(application_id="test-app-20240101")


def test_save_check_report_io_error(storage, monkeypatch):
    """Test that save_check_report raises StorageError on IOError."""
    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save check report"):
        storage.save_check_report(
            "# Check Report\n\nThis is a check report with enough content to pass minimum validation.",
            "test-app-20240101",
        )


def test_load_check_report_io_error(storage, monkeypatch):
    """Test that load_check_report raises StorageError on IOError."""
    storage.save_check_report(
        "# Check Report\n\nThis is a check report with enough content to pass minimum validation.",
        "test-app-20240101",
    )

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load check report"):
        storage.load_check_report("test-app-20240101")


def test_save_cover_letter_io_error(storage, monkeypatch):
    """Test that save_cover_letter raises StorageError on IOError."""
    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to save cover letter"):
        storage.save_cover_letter(
            "# Cover Letter\n\nThis is a cover letter with enough content to pass minimum length validation.",
            "test-app-20240101",
        )


def test_load_cover_letter_io_error(storage, monkeypatch):
    """Test that load_cover_letter raises StorageError on IOError."""
    storage.save_cover_letter(
        "# Cover Letter\n\nThis is a cover letter with enough content to pass minimum length validation.",
        "test-app-20240101",
    )

    def mock_open(*args, **kwargs):
        raise IOError("Permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    from cveasy.exceptions import StorageError
    with pytest.raises(StorageError, match="Failed to load cover letter"):
        storage.load_cover_letter("test-app-20240101")


def test_load_resume_no_resume_dir(storage):
    """Test loading resume when resume directory doesn't exist."""
    loaded = storage.load_resume()
    assert loaded is None


def test_load_resume_no_resumes_in_dir(storage):
    """Test loading resume when no resume files exist."""
    resume_dir = storage.base_path / "resume"
    resume_dir.mkdir(exist_ok=True)

    loaded = storage.load_resume()
    assert loaded is None


def test_load_skill_with_io_error_in_search(storage, sample_skill):
    """Test load_skill handles IOError gracefully when searching files."""
    # Create a file that will cause IOError when reading
    skills_dir = storage.base_path / "skills"
    bad_file = skills_dir / "bad-file.md"
    bad_file.write_text("invalid content")

    # Save a valid skill
    storage.save_skill(sample_skill)

    # Should still be able to load the valid skill
    loaded = storage.load_skill("Python")
    assert loaded is not None
    assert loaded.name == "Python"


def test_load_skill_name_mismatch_searches_all(storage, sample_skill):
    """Test load_skill searches all files when name doesn't match after loading."""
    # Save skill with slug
    storage.save_skill(sample_skill)

    # Create a file with wrong slug but correct name in frontmatter
    skills_dir = storage.base_path / "skills"
    wrong_file = skills_dir / "wrong-slug-abc123.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_skill.content,
        **sample_skill.to_frontmatter_dict()
    )
    with open(wrong_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    # Create another file with different name to test search
    other_skill = Skill(name="JavaScript", category="Language")
    storage.save_skill(other_skill)

    # Should find Python by searching all files
    loaded = storage.load_skill("Python")
    assert loaded is not None
    assert loaded.name == "Python"


def test_load_experience_name_mismatch_searches_all(storage, sample_experience):
    """Test load_experience searches all files when title doesn't match."""
    # Save experience
    storage.save_experience(sample_experience)

    # Create file with wrong slug but correct title
    experiences_dir = storage.base_path / "experiences"
    wrong_file = experiences_dir / "wrong-title-abc123.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_experience.content,
        **sample_experience.to_frontmatter_dict()
    )
    with open(wrong_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    loaded = storage.load_experience("Senior Software Engineer")
    assert loaded is not None
    assert loaded.title == "Senior Software Engineer"


def test_load_story_name_mismatch_searches_all(storage, sample_story):
    """Test load_story searches all files when title doesn't match."""
    storage.save_story(sample_story)

    # Create file with wrong slug but correct title
    stories_dir = storage.base_path / "stories"
    wrong_file = stories_dir / "wrong-title-abc123.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_story.content,
        **sample_story.to_frontmatter_dict()
    )
    with open(wrong_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    loaded = storage.load_story("Led Migration to Microservices")
    assert loaded is not None
    assert loaded.title == "Led Migration to Microservices"


def test_load_link_name_mismatch_searches_all(storage, sample_link):
    """Test load_link searches all files when name doesn't match."""
    storage.save_link(sample_link)

    # Create file with wrong slug but correct name
    links_dir = storage.base_path / "links"
    wrong_file = links_dir / "wrong-name-abc123.md"
    import frontmatter
    post = frontmatter.Post(
        content="",
        **sample_link.to_frontmatter_dict()
    )
    with open(wrong_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    loaded = storage.load_link("LinkedIn")
    assert loaded is not None
    assert loaded.name == "LinkedIn"


def test_load_project_name_mismatch_searches_all(storage, sample_project):
    """Test load_project searches all files when name doesn't match."""
    storage.save_project(sample_project)

    # Create file with wrong slug but correct name
    projects_dir = storage.base_path / "projects"
    wrong_file = projects_dir / "wrong-name-abc123.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_project.content,
        **sample_project.to_frontmatter_dict()
    )
    with open(wrong_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    loaded = storage.load_project("E-commerce Platform")
    assert loaded is not None
    assert loaded.name == "E-commerce Platform"


def test_load_education_name_mismatch_searches_all(storage, sample_education):
    """Test load_education searches all files when name doesn't match."""
    storage.save_education(sample_education)

    # Create file with wrong slug but correct name
    education_dir = storage.base_path / "education"
    wrong_file = education_dir / "wrong-name-abc123.md"
    import frontmatter
    post = frontmatter.Post(
        content=sample_education.content,
        **sample_education.to_frontmatter_dict()
    )
    with open(wrong_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    loaded = storage.load_education("Bachelor of Science in Computer Science")
    assert loaded is not None
    assert loaded.name == "Bachelor of Science in Computer Science"
