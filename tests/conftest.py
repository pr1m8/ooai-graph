"""Pytest configuration and fixtures.

This module configures pytest for the test suite and provides
global fixtures and configuration.
"""

import sys
from pathlib import Path

import pytest

# Load environment variables from .env file for testing
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from {env_file}")
except ImportError:
    print("⚠️ python-dotenv not available, skipping .env loading")

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory.

    Returns:
        Path: Path to project root
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Return the test data directory.

    Args:
        project_root: Project root fixture

    Returns:
        Path: Path to test data directory
    """
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(exist_ok=True, parents=True)
    return data_dir


@pytest.fixture(autouse=True)
def reset_model_cache():
    """Reset the model cache before each test.

    This ensures tests are isolated and don't share cached data.
    """
    from ooai.core.models import DynamicBaseModel

    # Clear cache before each test
    DynamicBaseModel.clear_cache()
    yield
    # Clear cache after each test as well
    DynamicBaseModel.clear_cache()


# =============================================================================
# Test Infrastructure Integration
# =============================================================================


@pytest.fixture(scope="session")
def golden_manager():
    """Provide a configured GoldenFileManager instance.

    Returns:
        GoldenFileManager: Configured manager for golden files
    """
    from tests.utils.golden_utils import GoldenFileManager

    return GoldenFileManager()


@pytest.fixture(scope="session")
def test_manager():
    """Provide a configured TestManager instance.

    Returns:
        TestManager: Configured manager for test execution
    """
    from tests.utils.test_manager import TestManager

    return TestManager()


@pytest.fixture
def model_fixtures():
    """Provide ModelFixtures for creating test models.

    Returns:
        ModelFixtures: Class with factory methods for test models
    """
    from tests.utils.model_fixtures import ModelFixtures

    return ModelFixtures


@pytest.fixture
def test_helpers():
    """Provide test helper functions.

    Returns:
        module: test_helpers module with utility functions
    """
    from tests.utils import test_helpers

    return test_helpers


# =============================================================================
# Golden File Testing Integration
# =============================================================================


def pytest_addoption(parser):
    """Add custom command line options for golden file testing."""
    # Check if option already exists (from pytest-golden)
    try:
        parser.addoption(
            "--update-goldens",
            action="store_true",
            default=False,
            help="Update golden files when tests fail",
        )
    except ValueError:
        pass  # Option already exists from pytest-golden
    parser.addoption(
        "--golden-diff",
        action="store_true",
        default=False,
        help="Show differences when golden file tests fail",
    )
    parser.addoption(
        "--golden-backup",
        action="store_true",
        default=False,
        help="Backup golden files before updating",
    )


def pytest_configure(config):
    """Configure pytest with custom markers and golden file settings."""
    # Register our custom markers
    config.addinivalue_line("markers", "golden: mark test as using golden files")
    config.addinivalue_line(
        "markers", "regen_golden: mark test to regenerate golden files"
    )

    # Configure golden file behavior based on command line options
    if config.getoption("--update-goldens"):
        # Set environment variable that our golden utils can check
        import os

        os.environ["UPDATE_GOLDEN_FILES"] = "true"

    if config.getoption("--golden-backup"):
        import os

        os.environ["BACKUP_GOLDEN_FILES"] = "true"


@pytest.fixture
def golden_file_config(request):
    """Provide golden file configuration based on pytest options.

    Args:
        request: pytest request object

    Returns:
        dict: Configuration for golden file operations
    """
    config = {
        "update_golden": request.config.getoption("--update-goldens"),
        "show_diff": request.config.getoption("--golden-diff"),
        "backup_files": request.config.getoption("--golden-backup"),
    }
    return config


# =============================================================================
# Test Data and Model Factories
# =============================================================================


@pytest.fixture
def simple_models(model_fixtures):
    """Provide simple test models.

    Args:
        model_fixtures: ModelFixtures instance

    Returns:
        dict: Dictionary of simple test models
    """
    return model_fixtures.create_simple_models()


@pytest.fixture
def hierarchical_models(model_fixtures):
    """Provide hierarchical test models.

    Args:
        model_fixtures: ModelFixtures instance

    Returns:
        dict: Dictionary of hierarchical test models
    """
    return model_fixtures.create_hierarchical_models()


@pytest.fixture
def conflicting_models(model_fixtures):
    """Provide models with field conflicts.

    Args:
        model_fixtures: ModelFixtures instance

    Returns:
        dict: Dictionary of models with conflicts
    """
    return model_fixtures.create_conflicting_models()


@pytest.fixture
def validated_models(model_fixtures):
    """Provide models with validation.

    Args:
        model_fixtures: ModelFixtures instance

    Returns:
        dict: Dictionary of validated test models
    """
    return model_fixtures.create_validated_models()


# =============================================================================
# Test Environment Setup
# =============================================================================


@pytest.fixture(autouse=True, scope="session")
def setup_test_environment():
    """Set up the test environment once per session."""
    # Ensure test directories exist
    test_dirs = [
        "tests/models/goldens",
        "tests/engines/goldens",
        "tests/utils",
        "tests/data",
    ]

    base_path = Path(__file__).parent
    for test_dir in test_dirs:
        (base_path / test_dir).mkdir(parents=True, exist_ok=True)


    # Cleanup can be added here if needed
