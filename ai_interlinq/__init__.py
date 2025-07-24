# ai_interlinq/__init__.py (Updated)
"""
AI-Interlinq: Fast AI-to-AI Communication Library
A high-performance token-based communication system for AI models and agents.

File: ai_interlinq/__init__.py
Directory: ai_interlinq/
"""

__version__ = "0.1.0"
__author__ = "mupoese"
__license__ = "GPL-2.0"

# Core components
from .core.token_manager import TokenManager, TokenType, TokenStatus
from .core.encryption import EncryptionHandler
from .core.communication_protocol import (
    CommunicationProtocol, MessageType, Priority, Message, 
    MessageHeader, MessagePayload
)
from .core.message_handler import MessageHandler, MessageQueue
from .core.memory_system import AdvancedMemorySystem, MemorySnapshot, ConversationContext
from .core.connection_manager import ConnectionManager, ConnectionStatus, ConnectionInfo
from .core.session_manager import SessionManager, SessionStatus, SessionInfo

# Utils
from .utils.performance import PerformanceMonitor, PerformanceMetric
from .utils.parser import MessageParser, ParseResult
from .utils.serializer import MessageSerializer, SerializationFormat, CompressionType
from .utils.validation import Validator, validate_message_data
from .utils.logging import setup_logging, get_logger

# Transport layer
from .transport.base import BaseTransport, TransportConfig, TransportError
from .transport.websocket import WebSocketTransport
from .transport.tcp import TCPTransport
from .transport.redis import RedisTransport, RedisConfig

# Middleware
from .middleware.auth import AuthMiddleware, AuthLevel, AuthContext
from .middleware.compression import CompressionMiddleware, CompressionConfig
from .middleware.metrics import MetricsCollector, MetricType
from .middleware.rate_limiter import RateLimiterMiddleware

# Plugins
from .plugins.load_balancer import LoadBalancer, LoadBalancingStrategy, BackendAgent
from .plugins.rate_limiter import RateLimiter, RateLimitConfig, TokenBucket
from .plugins.metrics import MetricsCollector as PluginMetricsCollector

# CLI
from .cli.main import cli_main
from .cli.benchmark import BenchmarkSuite, BenchmarkConfig
from .cli.monitor import SystemMonitor, MonitorConfig

# Configuration
from .config import Config, SecurityConfig, PerformanceConfig, LoggingConfig

# Exceptions
from .exceptions import (
    AIInterlinqError, AuthenticationError, EncryptionError, TokenError,
    MessageError, ProtocolError, ConnectionError, TimeoutError,
    ValidationError, ConfigurationError
)

# Version info
from .version import __version__, get_version

__all__ = [
    # Core
    "TokenManager", "TokenType", "TokenStatus",
    "EncryptionHandler",
    "CommunicationProtocol", "MessageType", "Priority", "Message", 
    "MessageHeader", "MessagePayload",
    "MessageHandler", "MessageQueue", 
    "AdvancedMemorySystem", "MemorySnapshot", "ConversationContext",
    "ConnectionManager", "ConnectionStatus", "ConnectionInfo",
    "SessionManager", "SessionStatus", "SessionInfo",
    
    # Utils
    "PerformanceMonitor", "PerformanceMetric",
    "MessageParser", "ParseResult",
    "MessageSerializer", "SerializationFormat", "CompressionType",
    "Validator", "validate_message_data",
    "setup_logging", "get_logger",
    
    # Transport
    "BaseTransport", "TransportConfig", "TransportError",
    "WebSocketTransport", "TCPTransport", 
    "RedisTransport", "RedisConfig",
    
    # Middleware
    "AuthMiddleware", "AuthLevel", "AuthContext",
    "CompressionMiddleware", "CompressionConfig", 
    "MetricsCollector", "MetricType",
    "RateLimiterMiddleware",
    
    # Plugins
    "LoadBalancer", "LoadBalancingStrategy", "BackendAgent",
    "RateLimiter", "RateLimitConfig", "TokenBucket",
    "PluginMetricsCollector",
    
    # CLI
    "cli_main", "BenchmarkSuite", "BenchmarkConfig", 
    "SystemMonitor", "MonitorConfig",
    
    # Configuration
    "Config", "SecurityConfig", "PerformanceConfig", "LoggingConfig",
    
    # Exceptions
    "AIInterlinqError", "AuthenticationError", "EncryptionError", 
    "TokenError", "MessageError", "ProtocolError", "ConnectionError",
    "TimeoutError", "ValidationError", "ConfigurationError",
    
    # Version
    "__version__", "get_version"
]

# Quick start helper
def create_agent(agent_id: str, 
                shared_key: str, 
                ttl: int = 3600,
                transport_type: str = "websocket",
                host: str = "localhost", 
                port: int = 8765) -> dict:
    """
    Quick start helper to create a complete AI agent setup.
    
    Args:
        agent_id: Unique agent identifier
        shared_key: Shared encryption key
        ttl: Token time-to-live in seconds
        transport_type: Transport type ("websocket", "tcp", "redis")
        host: Host address
        port: Port number
        
    Returns:
        Dictionary with configured agent components
    """
    
    # Core components
    token_manager = TokenManager(default_ttl=ttl)
    encryption = EncryptionHandler(shared_key)
    protocol = CommunicationProtocol(agent_id)
    message_handler = MessageHandler(agent_id, token_manager, encryption)
    memory_system = AdvancedMemorySystem(agent_id)
    
    # Transport configuration
    transport_config = TransportConfig(host=host, port=port)
    
    if transport_type.lower() == "websocket":
        transport = WebSocketTransport(transport_config)
    elif transport_type.lower() == "tcp":
        transport = TCPTransport(transport_config)
    elif transport_type.lower() == "redis":
        redis_config = RedisConfig(host=host, port=port)
        transport = RedisTransport(redis_config)
    else:
        raise ValueError(f"Unsupported transport type: {transport_type}")
    
    # Connection and session management
    connection_manager = ConnectionManager(transport, agent_id)
    session_manager = SessionManager()
    
    # Performance monitoring
    performance_monitor = PerformanceMonitor()
    
    return {
        "agent_id": agent_id,
        "token_manager": token_manager,
        "encryption": encryption,
        "protocol": protocol, 
        "message_handler": message_handler,
        "memory_system": memory_system,
        "transport": transport,
        "connection_manager": connection_manager,
        "session_manager": session_manager,
        "performance_monitor": performance_monitor
    }


# Convenience function for simple communication
async def send_message(sender_agent: dict, 
                      recipient_id: str,
                      command: str,
                      data: dict,
                      session_id: str = None,
                      priority: Priority = Priority.NORMAL) -> bool:
    """
    Convenience function to send a message between agents.
    
    Args:
        sender_agent: Sender agent components (from create_agent())
        recipient_id: Recipient agent ID
        command: Command to send
        data: Message data
        session_id: Session ID (auto-generated if None)
        priority: Message priority
        
    Returns:
        True if message sent successfully
    """
    
    if session_id is None:
        session_id = f"auto_session_{int(time.time())}"
        
    # Generate token if needed
    token = sender_agent["token_manager"].generate_token(session_id)
    
    # Create message
    message = sender_agent["protocol"].create_message(
        recipient_id=recipient_id,
        message_type=MessageType.REQUEST,
        command=command,
        data=data,
        session_id=session_id,
        priority=priority
    )
    
    # Send message
    return await sender_agent["message_handler"].send_message(message)


# Auto-discovery and setup
def discover_agents(network_range: str = "localhost", 
                   port_range: tuple = (8765, 8775)) -> List[str]:
    """
    Auto-discover AI-Interlinq agents on the network.
    
    Args:
        network_range: Network range to scan
        port_range: Port range to check
        
    Returns:
        List of discovered agent endpoints
    """
    # This would implement actual network discovery
    # For now, return a placeholder
    return [f"{network_range}:{port}" for port in range(port_range[0], port_range[1] + 1)]


# Configuration helpers
def load_config_from_env() -> Config:
    """Load configuration from environment variables."""
    return Config.from_environment()


def load_config_from_file(file_path: str) -> Config:
    """Load configuration from JSON file."""
    return Config.from_file(file_path)
