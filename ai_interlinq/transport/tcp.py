# ai_interlinq/transport/tcp.py
"""TCP transport implementation."""

import asyncio
import json
import logging
from typing import Optional, Tuple

from .base import BaseTransport, TransportConfig, TransportError
from ..utils.logging import get_logger


class TCPTransport(BaseTransport):
    """TCP-based transport implementation."""
    
    def __init__(self, config: TransportConfig):
        super().__init__(config)
        self.logger = get_logger("tcp_transport")
        self._server: Optional[asyncio.Server] = None
    
    async def start_server(self) -> None:
        """Start TCP server."""
        try:
            self._server = await asyncio.start_server(
                self._handle_client,
                self.config.host,
                self.config.port
            )
            self._is_running = True
            self.logger.info(f"TCP server started on {self.config.host}:{self.config.port}")
            
            # Start serving
            async with self._server:
                await self._server.serve_forever()
                
        except Exception as e:
            self.logger.error(f"Failed to start TCP server: {e}")
            raise TransportError(f"TCP server start failed: {e}")
    
    async def stop_server(self) -> None:
        """Stop TCP server."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._is_running = False
            self.logger.info("TCP server stopped")
    
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle incoming client connection."""
        client_addr = writer.get_extra_info('peername')
        self.logger.debug(f"New connection from {client_addr}")
        
        try:
            while True:
                # Read message length first (4 bytes)
                length_data = await reader.readexactly(4)
                message_length = int.from_bytes(length_data, 'big')
                
                # Read the actual message
                message_data = await reader.readexactly(message_length)
                message = message_data.decode('utf-8')
                
                # Handle the message
                await self.handle_incoming_message(message, str(client_addr))
                
        except asyncio.IncompleteReadError:
            self.logger.debug(f"Client {client_addr} disconnected")
        except Exception as e:
            self.logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def send_message(self, target: str, message: str) -> bool:
        """Send message via TCP."""
        try:
            host, port = self._parse_target(target)
            
            reader, writer = await asyncio.open_connection(host, port)
            
            # Send message length first
            message_bytes = message.encode('utf-8')
            length_bytes = len(message_bytes).to_bytes(4, 'big')
            
            writer.write(length_bytes)
            writer.write(message_bytes)
            await writer.drain()
            
            writer.close()
            await writer.wait_closed()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message to {target}: {e}")
            return False
    
    async def connect_to_peer(self, target: str) -> bool:
        """Connect to a peer (TCP doesn't maintain persistent connections)."""
        # TCP transport doesn't maintain persistent connections
        # Connection is established per message
        return True
    
    async def disconnect_from_peer(self, target: str) -> bool:
        """Disconnect from a peer."""
        # No persistent connections to disconnect
        return True
    
    def _parse_target(self, target: str) -> Tuple[str, int]:
        """Parse target string into host and port."""
        if ':' in target:
            host, port_str = target.rsplit(':', 1)
            return host, int(port_str)
        else:
            return target, self.config.port
