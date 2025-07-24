"""
Base Transport Interface for AI-Interlinq
Defines the standard interface for all transport implementations.

File: ai_interlinq/transport/base.py
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum


class ConnectionState(Enum):
    """Connection states for transports."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"
    CLOSING = "closing"


@dataclass
class TransportConfig:
    """Configuration for transport layer."""
    endpoint: str
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    keepalive_interval: float = 30.0
    max_message_size: int = 10 * 1024 * 1024  # 10MB
    compression_enabled: bool = True
    encryption_enabled: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseTransport(ABC):
    """Abstract base class for all transport implementations."""
    
    def __init__(self, config: TransportConfig):
        """
        Initialize transport with configuration.
        
        Args:
            config: Transport configuration
        """
        self.config = config
        self.state = ConnectionState.DISCONNECTED
        self._message_handlers: List[Callable] = []
        self._error_handlers: List[Callable] = []
        self._connection_handlers: List[Callable] = []
        
        # Statistics
        self._stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
            "connection_count": 0,
            "error_count": 0,
            "last_activity": 0.0
        }
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the transport endpoint.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Close the transport connection.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def send_message(self, message: bytes, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send a message through the transport.
        
        Args:
            message: Message bytes to send
            metadata: Optional message metadata
            
        Returns:
            True if message sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def receive_message(self) -> Optional[tuple[bytes, Dict[str, Any]]]:
        """
        Receive a message from the transport.
        
        Returns:
            Tuple of (message_bytes, metadata) or None if no message
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if transport is currently connected.
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    def add_message_handler(self, handler: Callable[[bytes, Dict[str, Any]], None]) -> None:
        """Add a message handler callback."""
        self._message_handlers.append(handler)
    
    def add_error_handler(self, handler: Callable[[Exception], None]) -> None:
        """Add an error handler callback."""
        self._error_handlers.append(handler)
    
    def add_connection_handler(self, handler: Callable[[ConnectionState], None]) -> None:
        """Add a connection state change handler."""
        self._connection_handlers.append(handler)
    
    async def _notify_message_handlers(self, message: bytes, metadata: Dict[str, Any]) -> None:
        """Notify all message handlers."""
        for handler in self._message_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message, metadata)
                else:
                    handler(message, metadata)
            except Exception as e:
                await self._notify_error_handlers(e)
    
    async def _notify_error_handlers(self, error: Exception) -> None:
        """Notify all error handlers."""
        self._stats["error_count"] += 1
        for handler in self._error_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error)
                else:
                    handler(error)
            except Exception:
                pass  # Avoid infinite error loops
    
    async def _notify_connection_handlers(self, new_state: ConnectionState) -> None:
        """Notify all connection handlers."""
        old_state = self.state
        self.state = new_state
        
        if new_state == ConnectionState.CONNECTED:
            self._stats["connection_count"] += 1
        
        for handler in self._connection_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(new_state)
                else:
                    handler(new_state)
            except Exception as e:
                await self._notify_error_handlers(e)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get transport statistics."""
        return {
            **self._stats,
            "state": self.state.value,
            "endpoint": self.config.endpoint,
            "config": {
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries,
                "compression_enabled": self.config.compression_enabled,
                "encryption_enabled": self.config.encryption_enabled
            }
        }
    
    def reset_stats(self) -> None:
        """Reset transport statistics."""
        self._stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
            "connection_count": 0,
            "error_count": 0,
            "last_activity": 0.0
        }


class TransportManager:
    """Manages multiple transport connections."""
    
    def __init__(self):
        self.transports: Dict[str, BaseTransport] = {}
        self._default_transport: Optional[str] = None
    
    def add_transport(self, name: str, transport: BaseTransport, set_default: bool = False) -> None:
        """Add a transport to the manager."""
        self.transports[name] = transport
        
        if set_default or self._default_transport is None:
            self._default_transport = name
    
    def remove_transport(self, name: str) -> bool:
        """Remove a transport from the manager."""
        if name in self.transports:
            transport = self.transports.pop(name)
            if self._default_transport == name:
                self._default_transport = next(iter(self.transports.keys()), None)
            return True
        return False
    
    def get_transport(self, name: Optional[str] = None) -> Optional[BaseTransport]:
        """Get a transport by name or default."""
        if name:
            return self.transports.get(name)
        elif self._default_transport:
            return self.transports.get(self._default_transport)
        return None
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect all transports."""
        results = {}
        for name, transport in self.transports.items():
            try:
                results[name] = await transport.connect()
            except Exception as e:
                results[name] = False
        return results
    
    async def disconnect_all(self) -> Dict[str, bool]:
        """Disconnect all transports."""
        results = {}
        for name, transport in self.transports.items():
            try:
                results[name] = await transport.disconnect()
            except Exception as e:
                results[name] = False
        return results
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all transports."""
        return {name: transport.get_stats() for name, transport in self.transports.items()}
