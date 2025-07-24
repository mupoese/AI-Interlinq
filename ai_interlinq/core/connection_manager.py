# ai_interlinq/core/connection_manager.py
"""Connection management for AI-Interlinq."""

import asyncio
import time
from typing import Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass

from ..transport.base import BaseTransport
from ..utils.logging import get_logger
from ..exceptions import ConnectionError


class ConnectionStatus(Enum):
    """Connection status enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class ConnectionInfo:
    """Information about a connection."""
    agent_id: str
    address: str
    status: ConnectionStatus
    connected_at: Optional[float] = None
    last_seen: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3


class ConnectionManager:
    """Manages connections to other AI agents."""
    
    def __init__(self, transport: BaseTransport, agent_id: str):
        self.transport = transport
        self.agent_id = agent_id
        self.logger = get_logger("connection_manager")
        
        # Connection tracking
        self._connections: Dict[str, ConnectionInfo] = {}
        self._heartbeat_interval = 30.0  # seconds
        self._heartbeat_timeout = 60.0   # seconds
        self._is_running = False
        
        # Tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the connection manager."""
        self._is_running = True
        
        # Start background tasks
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        self.logger.info("Connection manager started")
    
    async def stop(self):
        """Stop the connection manager."""
        self._is_running = False
        
        # Cancel background tasks
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect all peers
        for agent_id in list(self._connections.keys()):
            await self.disconnect_from_agent(agent_id)
        
        self.logger.info("Connection manager stopped")
    
    async def connect_to_agent(self, agent_id: str, address: str) -> bool:
        """Connect to another AI agent."""
        if agent_id in self._connections:
            conn = self._connections[agent_id]
            if conn.status == ConnectionStatus.CONNECTED:
                return True
        
        # Create connection info
        conn_info = ConnectionInfo(
            agent_id=agent_id,
            address=address,
            status=ConnectionStatus.CONNECTING
        )
        self._connections[agent_id] = conn_info
        
        try:
            # Attempt connection
            success = await self.transport.connect_to_peer(address)
            
            if success:
                conn_info.status = ConnectionStatus.CONNECTED
                conn_info.connected_at = time.time()
                conn_info.last_seen = time.time()
                conn_info.retry_count = 0
                
                self.logger.info(f"Connected to agent {agent_id} at {address}")
                return True
            else:
                conn_info.status = ConnectionStatus.ERROR
                self.logger.error(f"Failed to connect to agent {agent_id}")
                return False
                
        except Exception as e:
            conn_info.status = ConnectionStatus.ERROR
            self.logger.error(f"Exception connecting to agent {agent_id}: {e}")
            return False
    
    async def disconnect_from_agent(self, agent_id: str) -> bool:
        """Disconnect from an AI agent."""
        if agent_id not in self._connections:
            return True
        
        conn_info = self._connections[agent_id]
        
        try:
            success = await self.transport.disconnect_from_peer(conn_info.address)
            conn_info.status = ConnectionStatus.DISCONNECTED
            
            self.logger.info(f"Disconnected from agent {agent_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Exception disconnecting from agent {agent_id}: {e}")
            return False
    
    async def send_heartbeat(self, agent_id: str) -> bool:
        """Send heartbeat to an agent."""
        if agent_id not in self._connections:
            return False
        
        conn_info = self._connections[agent_id]
        if conn_info.status != ConnectionStatus.CONNECTED:
            return False
        
        try:
            # Create heartbeat message
            from ..core.communication_protocol import CommunicationProtocol, MessageType
            protocol = CommunicationProtocol(self.agent_id)
            
            heartbeat = protocol.create_heartbeat(f"heartbeat_{agent_id}")
            message_str = protocol.serialize_message(heartbeat)
            
            # Send heartbeat
            success = await self.transport.send_message(conn_info.address, message_str)
            
            if success:
                conn_info.last_seen = time.time()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to send heartbeat to {agent_id}: {e}")
            return False
    
    def update_last_seen(self, agent_id: str):
        """Update last seen timestamp for an agent."""
        if agent_id in self._connections:
            self._connections[agent_id].last_seen = time.time()
    
    def get_connection_status(self, agent_id: str) -> Optional[ConnectionStatus]:
        """Get connection status for an agent."""
        if agent_id in self._connections:
            return self._connections[agent_id].status
        return None
    
    def get_connected_agents(self) -> List[str]:
        """Get list of connected agent IDs."""
        return [
            agent_id for agent_id, conn in self._connections.items()
            if conn.status == ConnectionStatus.CONNECTED
        ]
    
    def get_connection_info(self, agent_id: str) -> Optional[ConnectionInfo]:
        """Get detailed connection information."""
        return self._connections.get(agent_id)
    
    async def _heartbeat_loop(self):
        """Background heartbeat loop."""
        while self._is_running:
            try:
                # Send heartbeats to all connected agents
                for agent_id, conn in self._connections.items():
                    if conn.status == ConnectionStatus.CONNECTED:
                        await self.send_heartbeat(agent_id)
                
                await asyncio.sleep(self._heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(1)
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._is_running:
            try:
                current_time = time.time()
                
                # Check for timed out connections
                for agent_id, conn in list(self._connections.items()):
                    if conn.status == ConnectionStatus.CONNECTED:
                        if conn.last_seen and \
                           current_time - conn.last_seen > self._heartbeat_timeout:
                            
                            self.logger.warning(f"Agent {agent_id} timed out, attempting reconnect")
                            conn.status = ConnectionStatus.RECONNECTING
                            
                            # Attempt reconnection
                            if conn.retry_count < conn.max_retries:
                                conn.retry_count += 1
                                success = await self.connect_to_agent(agent_id, conn.address)
                                
                                if not success:
                                    self.logger.error(f"Reconnection failed for {agent_id} "
                                                    f"(attempt {conn.retry_count}/{conn.max_retries})")
                            else:
                                self.logger.error(f"Max retries exceeded for {agent_id}, marking as error")
                                conn.status = ConnectionStatus.ERROR
                
                await asyncio.sleep(10)  # Cleanup every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(1)
