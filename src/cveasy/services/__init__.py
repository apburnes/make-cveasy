"""Service layer for CVEasy business logic.

Services are lazily imported to avoid pulling in heavy dependencies (e.g., spaCy via
CheckService -> analysis -> matcher) when only lightweight services are needed.
"""

import importlib

__all__ = [
    "ResumeService",
    "ApplicationService",
    "DataService",
    "ImportService",
    "ExportService",
    "CheckService",
    "ProjectService",
    "CoverLetterService",
]

_MODULE_MAP = {
    "ResumeService": "cveasy.services.resume_service",
    "ApplicationService": "cveasy.services.application_service",
    "DataService": "cveasy.services.data_service",
    "ImportService": "cveasy.services.import_service",
    "ExportService": "cveasy.services.export_service",
    "CheckService": "cveasy.services.check_service",
    "ProjectService": "cveasy.services.project_service",
    "CoverLetterService": "cveasy.services.cover_letter_service",
}


def __getattr__(name: str):
    if name in _MODULE_MAP:
        module = importlib.import_module(_MODULE_MAP[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
