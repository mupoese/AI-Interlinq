
"""
Message Handler for AI-Interlinq
Manages message processing, routing, and delivery.
"""

import asyncio
import time
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, deque
import logging

from .communication_protocol import Message, MessageType, Priority
from .token_manager import TokenManager
from .encryption import EncryptionHandler


@dataclass
class MessageQueue:
    """Message queue for different priority levels."""
    critical: deque = None
    high: deque = None
    normal: deque = None
    low: deque = None
    
    def __post_init__(self):
        if self.critical is None:
            self.critical = deque()
        if self.high is None:
            self.high = deque()
        if self.normal is None:
            self.normal = deque()
        if self.low is None:
            self.low = deque()


class MessageHandler:
    """Handles message processing, queuing, and delivery."""
    
    def __init__(
        self,
        agent_id: str,
        token_manager: TokenManager,
        encryption_handler: EncryptionHandler
    ):
        """
        Initialize message handler.
        
        Args:
            agent_id: ID of this AI agent
            token_manager: Token manager instance
            encryption_handler: Encryption handler instance
        """
        self.agent_id = agent_id
        self.token_manager = token_manager
        self.encryption_handler = encryption_handler
        
        # Message queues by session
        self._message_queues: Dict[str, MessageQueue] = defaultdict(MessageQueue)
        
        # Message handlers by command
        self._command_handlers: Dict[str, Callable] = {}
        
        # Response tracking
        self._pending_responses: Dict[str, asyncio.Future] = {}
        
        # Statistics
        self._stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_processed": 0,
            "errors": 0
        }
        
        # Setup logging
        self.logger = logging.getLogger(f"MessageHandler-{agent_id}")
    
    def register_command_handler(self, command: str, handler: Callable) -> None:
        """
        Register a handler function for a specific command.
        
        Args:
            command: Command name
            handler: Handler function
        """
        self._command_handlers[command] = handler
    
    async def send_message(
        self,
        message: Message,
        encrypt: bool = True
    ) -> bool:
        """
        Send a message to another AI agent.
        
        Args:
            message: Message to send
            encrypt: Whether to encrypt the message
            
        Returns:
            True if message was sent successfully
        """
        try:
            # Validate token for the session
            if hasattr(message.header, 'session_id'):
                token_info = self.token_manager.get_token_info(message.header.session_id)
                if not token_info:
                    self.logger.error(f"Invalid session token for {message.header.session_id}")
                    return False
            
            # Serialize message
            from .communication_protocol import CommunicationProtocol
            protocol = CommunicationProtocol(self.agent_id)
            serialized = protocol.serialize_message(message)
            
            # Encrypt if requested
            if encrypt:
                success, encrypted_data = self.encryption_handler.encrypt_message(serialized)
                if not success:
                    self.logger.error(f"Failed to encrypt message: {encrypted_data}")
                    return False
                message_data = encrypted_data
            else:
                message_data = serialized
            
            # TODO: Implement actual network transmission
            # For now, we'll simulate successful transmission
            await asyncio.sleep(0.001)  # Simulate network delay
            
            self._stats["messages_sent"] += 1
            self.logger.debug(f"Message sent: {message.header.message_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            self._stats["errors"] += 1
            return False
    
    async def receive_message(self, message_data: str, encrypted: bool = True) -> bool:
        """
        Receive and process a message from another AI agent.
        
        Args:
            message_data: Raw message data
            encrypted: Whether the message is encrypted
            
        Returns:
            True if message was processed successfully
        """
        try:
            # Decrypt if needed
            if encrypted:
                success, decrypted_data = self.encryption_handler.decrypt_message(message_data)
                if not success:
                    self.logger.error(f"Failed to decrypt message: {decrypted_data}")
                    return False
                serialized_message = decrypted_data
            else:
                serialized_message = message_data
            
            # Deserialize message
            from .communication_protocol import CommunicationProtocol
            protocol = CommunicationProtocol(self.agent_id)
            message = protocol.deserialize_message(serialized_message)
            
            if not message:
                self.logger.error("Failed to deserialize message")
                return False
            
            # Validate message
            is_valid, error_msg = protocol.validate_message(message)
            if not is_valid:
                self.logger.error(f"Invalid message: {error_msg}")
                return False
            
            # Queue message for processing
            await self._queue_message(message)
            
            self._stats["messages_received"] += 1
            self.logger.debug(f"Message received: {message.header.message_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to receive message: {str(e)}")
            self._stats["errors"] += 1
            return False
    
    async def _queue_message(self, message: Message) -> None:
        """Queue a message based on its priority."""
        session_id = message.header.session_id
        queue = self._message_queues[session_id]
        
        if message.header.priority == Priority.CRITICAL:
            queue.critical.append(message)
        elif message.header.priority == Priority.HIGH:
            queue.high.append(message)
        elif message.header.priority == Priority.NORMAL:
            queue.normal.append(message)
        else:
            queue.low.append(message)
    
    async def process_messages(self, session_id: str, max_messages: int = 10) -> int:
        """
        Process queued messages for a session.
        
        Args:
            session_id: Session to process messages for
            max_messages: Maximum number of messages to process
            
        Returns:
            Number of messages processed
        """
        if session_id not in self._message_queues:
            return 0
        
        queue = self._message_queues[session_id]
        processed = 0
        
        # Process messages in priority order
        for priority_queue in [queue.critical, queue.high, queue.normal, queue.low]:
            while priority_queue and processed < max_messages:
                message = priority_queue.popleft()
                await self._process_single_message(message)
                processed += 1
                self._stats["messages_processed"] += 1
        
        return processed
    
    async def _process_single_message(self, message: Message) -> None:
        """Process a single message."""
        try:
            command = message.payload.command
            
            # Handle response messages
            if message.header.message_type == MessageType.RESPONSE:
                original_id = message.payload.data.get("original_message_id")
                if original_id in self._pending_responses:
                    future = self._pending_responses.pop(original_id)
                    if not future.done():
                        future.set_result(message)
                return
            
            # Handle command messages
            if command in self._command_handlers:
                handler = self._command_handlers[command]
                await handler(message)
            else:
                self.logger.warning(f"No handler for command: {command}")
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
    
    async def send_request_and_wait_response(
        self,
        message: Message,
        timeout: float = 30.0
    ) -> Optional[Message]:
        """
        Send a request message and wait for response.
        
        Args:
            message: Request message to send
            timeout: Timeout in seconds
            
        Returns:
            Response message or None if timeout
        """
        # Create future for response
        future = asyncio.Future()
        self._pending_responses[message.header.message_id] = future
        
        try:
            # Send message
            success = await self.send_message(message)
            if not success:
                return None
            
            # Wait for response
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout waiting for response to {message.header.message_id}")
            self._pending_responses.pop(message.header.message_id, None)
            return None
        except Exception as e:
            self.logger.error(f"Error waiting for response: {str(e)}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get handler statistics."""
        return {
            **self._stats,
            "pending_responses": len(self._pending_responses),
            "queued_messages": sum(
                len(q.critical) + len(q.high) + len(q.normal) + len(q.low)
                for q in self._message_queues.values()
            )
        }
    
    def clear_session_queue(self, session_id: str) -> None:
        """Clear all queued messages for a session."""
        if session_id in self._message_queues:
            del self._message_queues[session_id]
