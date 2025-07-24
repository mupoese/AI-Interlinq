# ai_interlinq/__init__.py

"""
AI-Interlinq: Fast AI-to-AI Communication Library
A high-performance token-based communication system for AI models and agents.
"""

__version__ = "0.1.0"
__author__ = "mupoese"
__license__ = "GPL-2.0"

from .core.token_manager import TokenManager
from .core.encryption import EncryptionHandler
from .core.communication_protocol import CommunicationProtocol, MessageType, Priority, Message
from .core.message_handler import MessageHandler
from .core.memory_system import AdvancedMemorySystem, MemorySnapshot
from .utils.performance import PerformanceMonitor
from .utils.parser import MessageParser, ParseResult
from .utils.serializer import MessageSerializer, SerializationFormat

__all__ = [
    "TokenManager",
    "EncryptionHandler", 
    "CommunicationProtocol",
    "MessageHandler",
    "AdvancedMemorySystem",
    "MemorySnapshot",
    "PerformanceMonitor",
    "MessageParser",
    "ParseResult",
    "MessageSerializer",
    "SerializationFormat",
    "MessageType",
    "Priority",
    "Message"
]
