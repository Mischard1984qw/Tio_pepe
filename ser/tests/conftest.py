"""Test configuration and fixtures for Tío Pepe system tests."""

import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

@pytest.fixture
def test_config():
    """Provide test configuration settings."""
    return {
        'test_data_dir': str(project_root / 'tests' / 'test_data'),
        'log_level': 'DEBUG',
        'mock_api_responses': True
    }

@pytest.fixture
def mock_task_data():
    """Provide mock task data for testing."""
    return {
        'task_id': 'test-123',
        'task_type': 'test',
        'priority': 1,
        'data': {'test_key': 'test_value'}
    }

@pytest.fixture
def mock_agent_config():
    """Provide mock agent configuration for testing."""
    return {
        'agent_id': 'test-agent',
        'agent_type': 'test',
        'capabilities': ['test_capability'],
        'config': {'test_param': 'test_value'}
    }

@pytest.fixture
def cleanup_test_data():
    """Clean up test data after tests."""
    yield
    test_data_dir = project_root / 'tests' / 'test_data'
    if test_data_dir.exists():
        for file in test_data_dir.glob('*'):
            if file.is_file():
                file.unlink()