# ai_interlinq/core/communication_protocol.py

"""
Communication Protocol for AI-Interlinq
Defines the standard protocol for AI-to-AI communication.
"""

import json
import time
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, asdict


class MessageType(Enum):
    """Types of messages in the protocol."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    HANDSHAKE = "handshake"


class Priority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MessageHeader:
    """Standard message header."""
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: str
    timestamp: float
    priority: Priority
    session_id: str
    protocol_version: str = "1.0"


@dataclass
class MessagePayload:
    """Message payload structure."""
    command: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Message:
    """Complete message structure."""
    header: MessageHeader
    payload: MessagePayload
    signature: Optional[str] = None


class CommunicationProtocol:
    """Handles AI communication protocol operations."""
    
    PROTOCOL_VERSION = "1.0"
    MAX_MESSAGE_SIZE = 1024 * 1024  # 1MB
    
    def __init__(self, agent_id: str):
        """
        Initialize communication protocol.
        
        Args:
            agent_id: Unique identifier for this AI agent
        """
        self.agent_id = agent_id
        self._message_counter = 0
    
    def create_message(
        self,
        recipient_id: str,
        message_type: MessageType,
        command: str,
        data: Dict[str, Any],
        session_id: str,
        priority: Priority = Priority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Create a new message according to the protocol.
        
        Args:
            recipient_id: ID of the receiving AI agent
            message_type: Type of message
            command: Command or action to perform
            data: Message data
            session_id: Communication session ID
            priority: Message priority
            metadata: Optional metadata
            
        Returns:
            Formatted message
        """
        self._message_counter += 1
        message_id = f"{self.agent_id}_{self._message_counter}_{int(time.time())}"
        
        header = MessageHeader(
            message_id=message_id,
            message_type=message_type,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            timestamp=time.time(),
            priority=priority,
            session_id=session_id,
            protocol_version=self.PROTOCOL_VERSION
        )
        
        payload = MessagePayload(
            command=command,
            data=data,
            metadata=metadata
        )
        
        return Message(header=header, payload=payload)
    
    def serialize_message(self, message: Message) -> str:
        """
        Serialize a message to JSON string.
        
        Args:
            message: Message to serialize
            
        Returns:
            JSON string representation
        """
        message_dict = {
            "header": {
                **asdict(message.header),
                "message_type": message.header.message_type.value,
                "priority": message.header.priority.value
            },
            "payload": asdict(message.payload),
            "signature": message.signature
        }
        return json.dumps(message_dict, separators=(',', ':'))
    
    def deserialize_message(self, message_json: str) -> Optional[Message]:
        """
        Deserialize a JSON string to a message.
        
        Args:
            message_json: JSON string to deserialize
            
        Returns:
            Message object or None if invalid
        """
        try:
            data = json.loads(message_json)
            
            header_data = data["header"]
            header = MessageHeader(
                message_id=header_data["message_id"],
                message_type=MessageType(header_data["message_type"]),
                sender_id=header_data["sender_id"],
                recipient_id=header_data["recipient_id"],
                timestamp=header_data["timestamp"],
                priority=Priority(header_data["priority"]),
                session_id=header_data["session_id"],
                protocol_version=header_data.get("protocol_version", "1.0")
            )
            
            payload_data = data["payload"]
            payload = MessagePayload(
                command=payload_data["command"],
                data=payload_data["data"],
                metadata=payload_data.get("metadata")
            )
            
            return Message(
                header=header,
                payload=payload,
                signature=data.get("signature")
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return None
    
    def validate_message(self, message: Message) -> Tuple[bool, str]:
        """
        Validate a message according to protocol rules.
        
        Args:
            message: Message to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check protocol version
        if message.header.protocol_version != self.PROTOCOL_VERSION:
            return False, f"Unsupported protocol version: {message.header.protocol_version}"
        
        # Check message size
        serialized = self.serialize_message(message)
        if len(serialized.encode()) > self.MAX_MESSAGE_SIZE:
            return False, "Message exceeds maximum size"
        
        # Check required fields
        if not message.header.message_id:
            return False, "Missing message ID"
        
        if not message.header.sender_id:
            return False, "Missing sender ID"
        
        if not message.header.recipient_id:
            return False, "Missing recipient ID"
        
        if not message.payload.command:
            return False, "Missing command"
        
        return True, "Valid"
    
    def create_error_response(
        self,
        original_message: Message,
        error_code: str,
        error_description: str
    ) -> Message:
        """Create an error response message."""
        return self.create_message(
            recipient_id=original_message.header.sender_id,
            message_type=MessageType.ERROR,
            command="error",
            data={
                "error_code": error_code,
                "error_description": error_description,
                "original_message_id": original_message.header.message_id
            },
            session_id=original_message.header.session_id,
            priority=original_message.header.priority
        )
    
    def create_heartbeat(self, session_id: str) -> Message:
        """Create a heartbeat message."""
        return self.create_message(
            recipient_id="*",  # Broadcast
            message_type=MessageType.HEARTBEAT,
            command="ping",
            data={"timestamp": time.time()},
            session_id=session_id,
            priority=Priority.LOW
        )
