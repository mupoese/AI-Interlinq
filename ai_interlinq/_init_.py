# ai_interlinq/__init__.py
"""
AI-Interlinq: Ultra-Fast AI-to-AI Communication Library
A high-performance token-based communication system for AI models and agents.
"""

__version__ = "2.0.0"
__author__ = "mupoese"
__license__ = "GPL-2.0"

# Core components
from .core.token_manager import TokenManager
from .core.encryption import EncryptionHandler
from .core.communication_protocol import EnhancedCommunicationProtocol as CommunicationProtocol
from .core.message_handler import UltraFastMessageHandler as MessageHandler

# Transport layers
from .transport import BaseTransport, WebSocketTransport, TCPTransport, RedisTransport

# Middleware
from .middleware import AuthMiddleware, RateLimiterMiddleware, MetricsMiddleware

# Utilities
from .utils.performance import PerformanceMonitor

__all__ = [
    # Core
    "TokenManager",
    "EncryptionHandler", 
    "CommunicationProtocol",
    "MessageHandler",
    
    # Transport
    "BaseTransport",
    "WebSocketTransport", 
    "TCPTransport",
    "RedisTransport",
    
    # Middleware
    "AuthMiddleware",
    "RateLimiterMiddleware", 
    "MetricsMiddleware",
    
    # Utils
    "PerformanceMonitor"
]
