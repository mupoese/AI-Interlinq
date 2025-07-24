"""
WebSocket Transport Implementation for AI-Interlinq
High-performance WebSocket transport with auto-reconnection and load balancing.

File: ai_interlinq/transport/websocket.py
"""

import asyncio
import json
import time
import logging
from typing import Optional, Dict, Any
import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from .base import BaseTransport, TransportConfig, ConnectionState


class WebSocketTransport(BaseTransport):
    """WebSocket transport implementation with advanced features."""
    
    def __init__(self, config: TransportConfig, headers: Optional[Dict[str, str]] = None):
        """
        Initialize WebSocket transport.
        
        Args:
            config: Transport configuration
            headers: Optional WebSocket headers
        """
        super().__init__(config)
        self.headers = headers or {}
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.logger = logging.getLogger(f"WebSocketTransport-{config.endpoint}")
        
        # Connection management
        self._reconnect_task: Optional[asyncio.Task] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        # Message queues
        self._send_queue: asyncio.Queue = asyncio.Queue()
        self._receive_queue: asyncio.Queue = asyncio.Queue()
        
        # Connection tracking
        self._last_ping: float = 0.0
        self._connection_start: float = 0.0
    
    async def connect(self) -> bool:
        """Establish WebSocket connection with retries."""
        if self.state in [ConnectionState.CONNECTED, ConnectionState.CONNECTING]:
            return True
        
        await self._notify_connection_handlers(ConnectionState.CONNECTING)
        
        retry_count = 0
        while retry_count < self.config.max_retries:
            try:
                self.logger.info(f"Attempting to connect to {self.config.endpoint}")
                
                # Establish WebSocket connection
                self.websocket = await websockets.connect(
                    self.config.endpoint,
                    extra_headers=self.headers,
                    timeout=self.config.timeout,
                    max_size=self.config.max_message_size,
                    compression="deflate" if self.config.compression_enabled else None
                )
                
                self._connection_start = time.time()
                await self._notify_connection_handlers(ConnectionState.CONNECTED)
                
                # Start background tasks
                self._receive_task = asyncio.create_task(self._receive_loop())
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                
                self.logger.info("WebSocket connection established")
                return True
                
            except Exception as e:
                retry_count += 1
                self.logger.error(f"Connection attempt {retry_count} failed: {e}")
                
                if retry_count < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay * retry_count)
                else:
                    await self._notify_connection_handlers(ConnectionState.FAILED)
                    await self._notify_error_handlers(e)
        
        return False
    
    async def disconnect(self) -> bool:
        """Close WebSocket connection gracefully."""
        if self.state == ConnectionState.DISCONNECTED:
            return True
        
        await self._notify_connection_handlers(ConnectionState.CLOSING)
        
        try:
            # Cancel background tasks
            if self._receive_task and not self._receive_task.done():
                self._receive_task.cancel()
            
            if self._heartbeat_task and not self._heartbeat_task.done():
                self._heartbeat_task.cancel()
            
            if self._reconnect_task and not self._reconnect_task.done():
                self._reconnect_task.cancel()
            
            # Close WebSocket connection
            if self.websocket and not self.websocket.closed:
                await self.websocket.close()
            
            await self._notify_connection_handlers(ConnectionState.DISCONNECTED)
            self.logger.info("WebSocket connection closed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
            await self._notify_error_handlers(e)
            return False
    
    async def send_message(self, message: bytes, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Send message through WebSocket."""
        if not await self.is_connected():
            return False
        
        try:
            # Prepare message with metadata
            message_data = {
                "payload": message.decode('utf-8') if isinstance(message, bytes) else message,
                "metadata": metadata or {},
                "timestamp": time.time()
            }
            
            # Send message
            await self.websocket.send(json.dumps(message_data))
            
            # Update statistics
            self._stats["messages_sent"] += 1
            self._stats["bytes_sent"] += len(json.dumps(message_data).encode())
            self._stats["last_activity"] = time.time()
            
            return True
            
        except (ConnectionClosedError, ConnectionClosedOK) as e:
            self.logger.warning("Connection closed during send, attempting reconnect")
            await self._handle_connection_loss()
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            await self._notify_error_handlers(e)
            return False
    
    async def receive_message(self) -> Optional[tuple[bytes, Dict[str, Any]]]:
        """Receive message from WebSocket."""
        try:
            # Get message from receive queue (populated by receive loop)
            message_data = await asyncio.wait_for(self._receive_queue.get(), timeout=0.1)
            
            payload = message_data.get("payload", "").encode('utf-8')
            metadata = message_data.get("metadata", {})
            
            # Update statistics
            self._stats["messages_received"] += 1
            self._stats["bytes_received"] += len(payload)
            self._stats["last_activity"] = time.time()
            
            return payload, metadata
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            await self._notify_error_handlers(e)
            return None
    
    async def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return (
            self.state == ConnectionState.CONNECTED and 
            self.websocket is not None and 
            not self.websocket.closed
        )
    
    async def _receive_loop(self):
        """Background task to receive WebSocket messages."""
        while await self.is_connected():
            try:
                # Receive message with timeout
                raw_message = await asyncio.wait_for(
                    self.websocket.recv(), 
                    timeout=self.config.timeout
                )
                
                # Parse message
                try:
                    message_data = json.loads(raw_message)
                except json.JSONDecodeError:
                    # Handle raw text messages
                    message_data = {
                        "payload": raw_message,
                        "metadata": {},
                        "timestamp": time.time()
                    }
                
                # Add to receive queue
                await self._receive_queue.put(message_data)
                
                # Notify message handlers
                payload = message_data.get("payload", "").encode('utf-8')
                metadata = message_data.get("metadata", {})
                await self._notify_message_handlers(payload, metadata)
                
            except asyncio.TimeoutError:
                continue  # Normal timeout, continue receiving
                
            except (ConnectionClosedError, ConnectionClosedOK):
                self.logger.warning("Connection closed during receive")
                await self._handle_connection_loss()
                break
                
            except Exception as e:
                self.logger.error(f"Error in receive loop: {e}")
                await self._notify_error_handlers(e)
                await asyncio.sleep(1)  # Brief pause before retrying
    
    async def _heartbeat_loop(self):
        """Background task to send periodic heartbeats."""
        while await self.is_connected():
            try:
                # Send ping
                if self.websocket and not self.websocket.closed:
                    pong_waiter = await self.websocket.ping()
                    self._last_ping = time.time()
                    
                    # Wait for pong with timeout
                    try:
                        await asyncio.wait_for(pong_waiter, timeout=10.0)
                        latency = time.time() - self._last_ping
                        self.logger.debug(f"Ping successful, latency: {latency:.3f}s")
                    except asyncio.TimeoutError:
                        self.logger.warning("Ping timeout, connection may be stale")
                        await self._handle_connection_loss()
                        break
                
                # Wait for next heartbeat interval
                await asyncio.sleep(self.config.keepalive_interval)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                await self._notify_error_handlers(e)
                await asyncio.sleep(5)  # Brief pause before retrying
    
    async def _handle_connection_loss(self):
        """Handle connection loss and attempt reconnection."""
        if self.state == ConnectionState.RECONNECTING:
            return  # Already reconnecting
        
        await self._notify_connection_handlers(ConnectionState.RECONNECTING)
        
        # Start reconnection task if not already running
        if not self._reconnect_task or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self._reconnect_loop())
    
    async def _reconnect_loop(self):
        """Background task to handle automatic reconnection."""
        reconnect_attempts = 0
        max_reconnect_attempts = self.config.max_retries * 2  # More attempts for reconnection
        
        while reconnect_attempts < max_reconnect_attempts:
            try:
                self.logger.info(f"Reconnection attempt {reconnect_attempts + 1}")
                
                # Close existing connection
                if self.websocket and not self.websocket.closed:
                    await self.websocket.close()
                
                # Attempt to reconnect
                if await self.connect():
                    self.logger.info("Reconnection successful")
                    return
                
                reconnect_attempts += 1
                
                # Exponential backoff
                backoff_delay = min(self.config.retry_delay * (2 ** reconnect_attempts), 60)
                await asyncio.sleep(backoff_delay)
                
            except Exception as e:
                self.logger.error(f"Reconnection attempt failed: {e}")
                reconnect_attempts += 1
                await asyncio.sleep(self.config.retry_delay)
        
        # All reconnection attempts failed
        self.logger.error("All reconnection attempts failed")
        await self._notify_connection_handlers(ConnectionState.FAILED)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get detailed connection information."""
        info = {
            "endpoint": self.config.endpoint,
            "state": self.state.value,
            "connected_duration": time.time() - self._connection_start if self._connection_start else 0,
            "last_ping": self._last_ping,
            "websocket_state": None
        }
        
        if self.websocket:
            info["websocket_state"] = {
                "closed": self.websocket.closed,
                "close_code": getattr(self.websocket, 'close_code', None),
                "close_reason": getattr(self.websocket, 'close_reason', None)
            }
        
        return info


class WebSocketServer:
    """WebSocket server for accepting AI agent connections."""
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 8765,
                 max_connections: int = 100):
        """
        Initialize WebSocket server.
        
        Args:
            host: Server host address
            port: Server port
            max_connections: Maximum concurrent connections
        """
        self.host = host
        self.port = port
        self.max_connections = max_connections
        
        self.server: Optional[websockets.WebSocketServer] = None
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.logger = logging.getLogger(f"WebSocketServer-{host}:{port}")
        
        # Message broadcasting
        self._message_handlers: List[Callable] = []
        self._connection_handlers: List[Callable] = []
    
    async def start(self) -> bool:
        """Start the WebSocket server."""
        try:
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port,
                max_size=10 * 1024 * 1024,  # 10MB max message size
                compression="deflate"
            )
            
            self.logger.info(f"WebSocket server started on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the WebSocket server."""
        try:
            if self.server:
                self.server.close()
                await self.server.wait_closed()
            
            # Close all client connections
            for client_id, websocket in self.clients.items():
                if not websocket.closed:
                    await websocket.close()
            
            self.clients.clear()
            self.logger.info("WebSocket server stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")
            return False
    
    async def _handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle individual client connections."""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}_{int(time.time())}"
        
        if len(self.clients) >= self.max_connections:
            self.logger.warning(f"Max connections reached, rejecting {client_id}")
            await websocket.close(code=1013, reason="Server full")
            return
        
        self.clients[client_id] = websocket
        self.logger.info(f"Client {client_id} connected")
        
        # Notify connection handlers
        for handler in self._connection_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(client_id, "connected")
                else:
                    handler(client_id, "connected")
            except Exception as e:
                self.logger.error(f"Error in connection handler: {e}")
        
        try:
            async for message in websocket:
                try:
                    # Parse message
                    message_data = json.loads(message) if isinstance(message, str) else message
                    
                    # Notify message handlers
                    for handler in self._message_handlers:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(client_id, message_data)
                            else:
                                handler(client_id, message_data)
                        except Exception as e:
                            self.logger.error(f"Error in message handler: {e}")
                
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON from {client_id}: {message}")
                except Exception as e:
                    self.logger.error(f"Error processing message from {client_id}: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            self.logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up client
            self.clients.pop(client_id, None)
            
            # Notify connection handlers
            for handler in self._connection_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(client_id, "disconnected")
                    else:
                        handler(client_id, "disconnected")
                except Exception as e:
                    self.logger.error(f"Error in disconnection handler: {e}")
    
    async def broadcast_message(self, message: Dict[str, Any], exclude_client: Optional[str] = None):
        """Broadcast message to all connected clients."""
        if not self.clients:
            return
        
        message_json = json.dumps(message)
        disconnected_clients = []
        
        for client_id, websocket in self.clients.items():
            if client_id == exclude_client:
                continue
            
            try:
                if not websocket.closed:
                    await websocket.send(message_json)
                else:
                    disconnected_clients.append(client_id)
            except Exception as e:
                self.logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.clients.pop(client_id, None)
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific client."""
        if client_id not in self.clients:
            return False
        
        websocket = self.clients[client_id]
        
        try:
            if not websocket.closed:
                await websocket.send(json.dumps(message))
                return True
            else:
                self.clients.pop(client_id, None)
                return False
        except Exception as e:
            self.logger.error(f"Error sending to {client_id}: {e}")
            self.clients.pop(client_id, None)
            return False
    
    def add_message_handler(self, handler: Callable[[str, Dict[str, Any]], None]):
        """Add message handler for incoming messages."""
        self._message_handlers.append(handler)
    
    def add_connection_handler(self, handler: Callable[[str, str], None]):
        """Add connection handler for client connect/disconnect events."""
        self._connection_handlers.append(handler)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            "host": self.host,
            "port": self.port,
            "active_connections": len(self.clients),
            "max_connections": self.max_connections,
            "server_running": self.server is not None,
            "clients": list(self.clients.keys())
        }
