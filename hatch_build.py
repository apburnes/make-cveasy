"""Custom build hook for hatchling to validate spaCy model availability."""

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)


class CustomBuildHook(BuildHookInterface):
    """Custom build hook to ensure spaCy model is available during build."""

    def initialize(self, version, build_data):
        """
        Called before build. Validates that the en_core_web_sm model is available.

        Args:
            version: Package version
            build_data: Build data dictionary
        """
        # Configure logging if not already configured
        if not logging.root.handlers:
            logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

        model_name = "en_core_web_sm"

        try:
            import spacy
            import spacy.util

            # Check if model is available
            if spacy.util.is_package(model_name):
                logger.info(f"✓ spaCy model '{model_name}' is available")
                return

            # Model not found, try to download it
            logger.warning(
                f"spaCy model '{model_name}' not found. Attempting to download..."
            )
            # Use subprocess.run with timeout and capture output for better error reporting
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "spacy", "download", model_name],
                    check=True,
                    timeout=300,  # 5 minute timeout
                    capture_output=True,
                    text=True
                )
            except subprocess.TimeoutExpired:
                error_msg = f"Download of spaCy model '{model_name}' timed out after 5 minutes"
                logger.warning(error_msg)
                return  # Don't fail the build
            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to download spaCy model '{model_name}': {e.stderr if e.stderr else str(e)}"
                logger.warning(error_msg)
                return  # Don't fail the build

            logger.info(f"✓ Successfully downloaded spaCy model '{model_name}'")

        except ImportError:
            # spaCy not installed - this is okay during build, it will be installed
            # as a dependency when the package is installed
            logger.warning(
                "spaCy is not installed during build. "
                "This is expected if building in a minimal environment. "
                "The model will be downloaded at runtime if needed."
            )
        except subprocess.CalledProcessError as e:
            # Download failed - log warning but don't fail the build
            logger.warning(
                f"Failed to download spaCy model '{model_name}' during build: {e}. "
                "The model will be downloaded at runtime if needed."
            )
        except Exception as e:
            # Any other error - log but don't fail the build
            logger.warning(
                f"Unexpected error while checking spaCy model '{model_name}': {e}. "
                "The model will be downloaded at runtime if needed."
            )
