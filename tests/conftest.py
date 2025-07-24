### tests/conftest.py

"""Pytest configuration and fixtures."""

import pytest
import asyncio
from ai_interlinq import TokenManager, EncryptionHandler, CommunicationProtocol, MessageHandler
from ai_interlinq.config import Config, SecurityConfig, PerformanceConfig


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Create test configuration."""
    return Config(
        security=SecurityConfig(
            default_encryption_key="test_key_123",
            token_ttl=300,  # 5 minutes for tests
            require_encryption=True
        ),
        performance=PerformanceConfig(
            max_message_size=1024,  # 1KB for tests
            message_queue_size=100,
            connection_timeout=5
        )
    )


@pytest.fixture
def token_manager():
    """Create token manager for testing."""
    return TokenManager(default_ttl=300)


@pytest.fixture
def encryption_handler():
    """Create encryption handler for testing."""
    return EncryptionHandler("test_encryption_key")


@pytest.fixture
def communication_protocol():
    """Create communication protocol for testing."""
    return CommunicationProtocol("test_agent")


@pytest.fixture
async def message_handler(token_manager, encryption_handler):
    """Create message handler for testing."""
    return MessageHandler("test_agent", token_manager, encryption_handler)


@pytest.fixture
def sample_message_data():
    """Sample message data for testing."""
    return {
        "command": "test_command",
        "data": {
            "key1": "value1",
            "key2": 42,
            "key3": [1, 2, 3]
        },
        "metadata": {
            "test": True
        }
    }
