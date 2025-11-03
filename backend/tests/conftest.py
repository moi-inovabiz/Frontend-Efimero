"""
Pytest configuration and shared fixtures for the test suite.
"""

import pytest
import sys
import os
from pathlib import Path

# Add the app directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

# Import all fixtures to make them available globally
from tests.fixtures.mock_data import *
from tests.fixtures.service_mocks import *
from tests.fixtures.training_data import *


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "firebase: mark test as requiring Firebase"
    )


@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment configuration."""
    return {
        "testing": True,
        "debug": True,
        "mock_external_services": True,
        "log_level": "DEBUG"
    }


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Configure logging for tests."""
    import logging
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise during tests
        format='%(levelname)s - %(name)s - %(message)s'
    )


@pytest.fixture
def clean_environment():
    """Ensure clean test environment between tests."""
    # Clear any cached modules or singletons
    yield
    # Cleanup after test
    pass


# Async test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Common test data combinations
@pytest.fixture(params=["desktop_power_user", "mobile_casual_user", "elderly_user"])
def varied_user_context(request, mock_user_contexts):
    """Parametrized fixture providing different user contexts."""
    return mock_user_contexts[request.param]


@pytest.fixture(params=["minimal_context", "extreme_resolution", "invalid_data"])
def edge_case_context(request, mock_edge_case_contexts):
    """Parametrized fixture providing edge case contexts."""
    return mock_edge_case_contexts[request.param]


# Helper fixtures for test setup
@pytest.fixture
def temp_model_directory(tmp_path):
    """Create temporary directory for model files."""
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    return model_dir


@pytest.fixture
def sample_model_files(temp_model_directory):
    """Create sample model files for testing."""
    # Create dummy model files
    (temp_model_directory / "classifier.joblib").touch()
    (temp_model_directory / "regressor.joblib").touch()
    (temp_model_directory / "feature_scaler.pkl").touch()
    
    return {
        "classifier": temp_model_directory / "classifier.joblib",
        "regressor": temp_model_directory / "regressor.joblib", 
        "scaler": temp_model_directory / "feature_scaler.pkl"
    }