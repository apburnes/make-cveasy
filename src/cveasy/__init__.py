"""CVEasy - CLI tool to manage resume data and generate customized resumes."""

# Ensure spaCy model is available on import
def _ensure_spacy_model():
    """Ensure en_core_web_sm model is available."""
    try:
        import spacy
        import spacy.util

        model_name = "en_core_web_sm"
        if not spacy.util.is_package(model_name):
            # Model not found, try to download it
            import subprocess
            import sys
            import logging

            logger = logging.getLogger(__name__)
            logger.info(f"Downloading spaCy model '{model_name}'...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "spacy", "download", model_name],
                    check=True,
                    timeout=300,
                    capture_output=True,
                    text=True
                )
                logger.info(f"✓ Successfully downloaded spaCy model '{model_name}'")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                logger.warning(
                    f"Failed to download spaCy model '{model_name}'. "
                    f"Please run: python -m spacy download {model_name}"
                )
    except ImportError:
        # spaCy not installed yet, will be handled when it's actually needed
        pass

# Try to ensure model is available (non-blocking)
try:
    _ensure_spacy_model()
except Exception:
    # Don't fail import if model download fails
    pass

__version__ = "0.5.0"
