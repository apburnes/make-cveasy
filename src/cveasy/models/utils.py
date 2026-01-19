"""Utility functions for models."""

import secrets
from slugify import slugify


def generate_slug(name: str) -> str:
    """
    Generate a URL-safe slug from a name.

    The slug is lowercase, uses hyphens to separate spaces, and includes
    a 6-character random hash at the end.

    Args:
        name: The name to generate a slug from

    Returns:
        A slug string in the format: lowercase-name-with-hyphens-{6-char-hash}

    Example:
        >>> slug = generate_slug("Python Programming")
        >>> # Returns something like: "python-programming-a1b2c3"
    """
    # Convert to lowercase and replace spaces with hyphens
    base_slug = slugify(name, lowercase=True)

    # Generate a 6-character random hash
    hash_suffix = secrets.token_hex(3)

    # Combine base slug with hash
    return f"{base_slug}-{hash_suffix}"
