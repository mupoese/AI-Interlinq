# ai_interlinq/transport/websocket.py
"""WebSocket transport implementation."""

import asyncio
import json
import websockets
from typing import Dict, Optional, Set
from websockets.server import WebSocketServerProtocol

from .base import BaseTransport, TransportConfig, TransportError
from ..utils.logging import get_logger


class WebSocketTransport(BaseTransport):
    """WebSocket-based transport implementation."""
    
    def __init__(self, config: TransportConfig):
        super().__init__(config)
        self.logger = get_logger("websocket_transport")
        self._clients: Dict[str, WebSocketServerProtocol] = {}
        self._server: Optional[websockets.WebSocketServer] = None
    
    async def start_server(self) -> None:
        """Start WebSocket server."""
        try:
            self._server = await websockets.serve(
                self._handle_client,
                self.config.host,
                self.config.port
            )
            self._is_running = True
            self.logger.info(f"WebSocket server started on {self.config.host}:{self.config.port}")
            
            # Keep server running
            await self._server.wait_closed()
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
            raise TransportError(f"WebSocket server start failed: {e}")
    
    async def stop_server(self) -> None:
        """Stop WebSocket server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._is_running = False
            self.logger.info("WebSocket server stopped")
    
    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket client connection."""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self._clients[client_id] = websocket
        self.logger.debug(f"WebSocket client connected: {client_id}")
        
        try:
            async for message in websocket:
                await self.handle_incoming_message(message, client_id)
        except websockets.exceptions.ConnectionClosed:
            self.logger.debug(f"WebSocket client disconnected: {client_id}")
        except Exception as e:
            self.logger.error(f"Error handling WebSocket client {client_id}: {e}")
        finally:
            self._clients.pop(client_id, None)
    
    async def send_message(self, target: str, message: str) -> bool:
        """Send message via WebSocket."""
        try:
            if target in self._clients:
                websocket = self._clients[target]
                await websocket.send(message)
                return True
            else:
                # Try to connect to target
                uri = f"ws://{target}"
                async with websockets.connect(uri) as websocket:
                    await websocket.send(message)
                    return True
        except Exception as e:
            self.logger.error(f"Failed to send WebSocket message to {target}: {e}")
            return False
    
    async def connect_to_peer(self, target: str) -> bool:
        """Connect to WebSocket peer."""
        try:
            uri = f"ws://{target}"
            websocket = await websockets.connect(uri)
            self._clients[target] = websocket
            
            # Start listening for messages from this peer
            asyncio.create_task(self._listen_to_peer(websocket, target))
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket peer {target}: {e}")
            return False
    
    async def disconnect_from_peer(self, target: str) -> bool:
        """Disconnect from WebSocket peer."""
        if target in self._clients:
            websocket = self._clients.pop(target)
            await websocket.close()
            return True
        return False
    
    async def _listen_to_peer(self, websocket: WebSocketServerProtocol, peer_id: str):
        """Listen for messages from a connected peer."""
        try:
            async for message in websocket:
                await self.handle_incoming_message(message, peer_id)
        except websockets.exceptions.ConnectionClosed:
            self.logger.debug(f"Peer {peer_id} disconnected")
            self._clients.pop(peer_id, None)
        except Exception as e:
            self.logger.error(f"Error listening to peer {peer_id}: {e}")
