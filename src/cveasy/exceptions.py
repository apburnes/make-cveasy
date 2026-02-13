"""Custom exception hierarchy for CVEasy."""


# Base exception
class CVEasyError(Exception):
    """Base exception for all CVEasy errors."""

    pass


# Domain-specific exceptions
class ProjectError(CVEasyError):
    """Project-related errors."""

    pass


class ValidationError(CVEasyError):
    """Data validation errors."""

    pass


class StorageError(CVEasyError):
    """Storage operation errors."""

    pass


class AIProviderError(CVEasyError):
    """AI provider errors."""

    pass


class ResumeGenerationError(CVEasyError):
    """Resume generation errors."""

    pass


class DataImportError(CVEasyError):
    """Data import operation errors (e.g., resume parsing, scraping)."""

    pass


class ExportError(CVEasyError):
    """Export operation errors."""

    pass


class NotFoundError(CVEasyError):
    """Resource not found errors."""

    pass
