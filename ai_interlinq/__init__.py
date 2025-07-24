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
from .transport.redis import RedisTransport

# Middleware imports
from .middleware.auth import AuthMiddleware
from .middleware.compression import CompressionMiddleware
from .middleware.metrics import MetricsMiddleware
from .middleware.rate_limiter import RateLimiterMiddleware

# Adapter imports
from .adapters.anthropic import AnthropicAdapter
from .adapters.openai import OpenAIAdapter
from .adapters.ollama import OllamaAdapter
from .adapters.deepseek import DeepSeekAdapter
from .adapters.gemini import GeminiAdapter
from .adapters.grok import GrokAdapter
from .adapters.huggingface import HuggingFaceAdapter

# Utility imports
from .utils.performance import PerformanceMonitor
from .utils.serializer import MessageSerializer

# CLI imports
from .cli.benchmark import BenchmarkCLI
from .cli.monitor import MonitorCLI

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
    "RedisTransport",
    
    # Middleware
    "AuthMiddleware",
    "CompressionMiddleware",
    "MetricsMiddleware",
    "RateLimiterMiddleware",
    
    # Adapters
    "AnthropicAdapter",
    "OpenAIAdapter",
    "OllamaAdapter",
    "DeepSeekAdapter", 
    "GeminiAdapter",
    "GrokAdapter",
    "HuggingFaceAdapter",
    
    # Utils
    "PerformanceMonitor",
    "MessageSerializer",
    
    # CLI
    "BenchmarkCLI",
    "MonitorCLI"
]
