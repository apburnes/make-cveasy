"""Analysis tools for resume quality checks.

Lazily imported to avoid loading spaCy (~133MB) until actually needed.
"""

import importlib

__all__ = ["KeywordMatcher", "SkillsMatcher", "ResumeChecker"]

_MODULE_MAP = {
    "KeywordMatcher": "cveasy.analysis.matcher",
    "SkillsMatcher": "cveasy.analysis.matcher",
    "ResumeChecker": "cveasy.analysis.checker",
}


def __getattr__(name: str):
    if name in _MODULE_MAP:
        module = importlib.import_module(_MODULE_MAP[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
