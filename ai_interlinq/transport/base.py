# ai_interlinq/transport/base.py
"""Base transport layer for AI-Interlinq communication."""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass

from ..core.communication_protocol import Message
from ..exceptions import ConnectionError, TransportError


@dataclass
class TransportConfig:
    """Base transport configuration."""
    host: str = "localhost"
    port: int = 8080
    timeout: float = 30.0
    max_connections: int = 100
    buffer_size: int = 8192


class TransportError(Exception):
    """Transport layer error."""
    pass


class BaseTransport(ABC):
    """Abstract base class for transport implementations."""
    
    def __init__(self, config: TransportConfig):
        self.config = config
        self._message_handler: Optional[Callable] = None
        self._connections: Dict[str, Any] = {}
        self._is_running = False
    
    def set_message_handler(self, handler: Callable[[Message, str], None]):
        """Set the message handler callback."""
        self._message_handler = handler
    
    @abstractmethod
    async def start_server(self) -> None:
        """Start the transport server."""
        pass
    
    @abstractmethod
    async def stop_server(self) -> None:
        """Stop the transport server."""
        pass
    
    @abstractmethod
    async def send_message(self, target: str, message: str) -> bool:
        """Send a message to a target."""
        pass
    
    @abstractmethod
    async def connect_to_peer(self, target: str) -> bool:
        """Connect to a peer."""
        pass
    
    @abstractmethod
    async def disconnect_from_peer(self, target: str) -> bool:
        """Disconnect from a peer."""
        pass
    
    async def handle_incoming_message(self, message: str, sender: str):
        """Handle incoming message."""
        if self._message_handler:
            # Parse message back to Message object
            from ..core.communication_protocol import CommunicationProtocol
            protocol = CommunicationProtocol("transport")
            msg_obj = protocol.deserialize_message(message)
            if msg_obj:
                await self._message_handler(msg_obj, sender)
