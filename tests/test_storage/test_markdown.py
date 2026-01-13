"""Tests for markdown storage."""

from cveasy.storage import MarkdownStorage
from cveasy.models.skill import Skill


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
