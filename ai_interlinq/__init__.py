# File: /ai_interlinq/__init__.py
# Directory: /ai_interlinq

"""
AI-Interlinq: Advanced AI-to-AI Communication Framework
========================================================

Ultra-fast, secure, token-based communication system for AI agents.
"""

__version__ = "1.0.0"
__author__ = "mupoese"
__email__ = "contact@ai-interlinq.com"

# Core imports
from .core.token_manager import TokenManager
from .core.encryption import EncryptionHandler
from .core.communication_protocol import CommunicationProtocol
from .core.message_handler import MessageHandler
from .core.memory_system import MemorySystem

# Transport imports
from .transport.base import BaseTransport
from .transport.websocket import WebSocketTransport
from .transport.tcp import TCPTransport

# Optional redis import
try:
    from .transport.redis import RedisTransport
    _redis_available = True
except (ImportError, TypeError):
    RedisTransport = None
    _redis_available = False

# Middleware imports
from .middleware.auth import AuthMiddleware
from .middleware.compression import CompressionMiddleware
from .middleware.metrics import MetricsMiddleware
from .middleware.rate_limiter import RateLimiterMiddleware

# Adapter imports removed - not connected to core LAW-001 system

# Utility imports
from .utils.performance import PerformanceMonitor
from .utils.serializer import MessageSerializer

# CLI imports
from .cli.benchmark import BenchmarkSuite
from .cli.monitor import SystemMonitor

__all__ = [
    # Core
    "TokenManager",
    "EncryptionHandler", 
    "CommunicationProtocol",
    "MessageHandler",
    "MemorySystem",
    
    # Transport
    "BaseTransport",
    "WebSocketTransport",
    "TCPTransport", 
    
    # Middleware
    "AuthMiddleware",
    "CompressionMiddleware",
    "MetricsMiddleware",
    "RateLimiterMiddleware",
    
    # Adapters removed - not connected to core LAW-001 system
    
    # Utils
    "PerformanceMonitor",
    "MessageSerializer",
    
    # CLI
    "BenchmarkSuite",
    "SystemMonitor"
]

# Add RedisTransport if available
if _redis_available:
    __all__.append("RedisTransport")
