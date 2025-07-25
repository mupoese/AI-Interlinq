# ai_interlinq/transport/__init__.py
"""Transport layer implementations."""

from .base import BaseTransport, TransportConfig, TransportError
from .tcp import TCPTransport
from .websocket import WebSocketTransport

# Optional redis import to avoid aioredis compatibility issues
try:
    from .redis import RedisTransport, RedisConfig
    _redis_available = True
except (ImportError, TypeError):
    RedisTransport = None
    RedisConfig = None
    _redis_available = False

__all__ = [
    "BaseTransport",
    "TransportConfig", 
    "TransportError",
    "TCPTransport",
    "WebSocketTransport"
]

if _redis_available:
    __all__.extend(["RedisTransport", "RedisConfig"])
