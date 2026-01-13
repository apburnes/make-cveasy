"""Tests for markdown storage."""

from cveasy.storage import MarkdownStorage
from cveasy.models.skill import Skill
from cveasy.models.education import Education


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
