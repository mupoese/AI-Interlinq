# ai_interlinq/utils/serializer.py
"""Message serialization utilities for AI-Interlinq."""

import json
import pickle
import msgpack
from typing import Dict, Any, Optional, Union
from dataclasses import asdict

from ..core.communication_protocol import Message
from ..utils.logging import get_logger


class SerializationError(Exception):
    """Serialization error."""
    pass


class MessageSerializer:
    """Serializes AI-Interlinq messages in various formats."""
    
    def __init__(self):
        self.logger = get_logger("message_serializer")
    
    def to_json(self, message: Message, compact: bool = False) -> str:
        """Serialize message to JSON."""
        try:
            message_dict = {
                "header": {
                    **asdict(message.header),
                    "message_type": message.header.message_type.value,
                    "priority": message.header.priority.value
                },
                "payload": asdict(message.payload),
                "signature": message.signature
            }
            
            if compact:
                return json.dumps(message_dict, separators=(',', ':'))
            else:
                return json.dumps(message_dict, indent=2)
                
        except Exception as e:
            self.logger.error(f"JSON serialization error: {e}")
            raise SerializationError(f"JSON serialization failed: {e}")
    
    def to_msgpack(self, message: Message) -> bytes:
        """Serialize message to MessagePack binary format."""
        try:
            message_dict = {
                "header": {
                    **asdict(message.header),
                    "message_type": message.header.message_type.value,
                    "priority": message.header.priority.value
                },
                "payload": asdict(message.payload),
                "signature": message.signature
            }
            
            return msgpack.packb(message_dict)
            
        except Exception as e:
            self.logger.error(f"MessagePack serialization error: {e}")
            raise SerializationError(f"MessagePack serialization failed: {e}")
    
    def to_compact_string(self, message: Message) -> str:
        """Serialize to compact string format."""
        try:
            data_json = json.dumps(message.payload.data, separators=(',', ':'))
            
            compact = f"{message.header.message_type.value}|" \
                     f"{message.header.sender_id}|" \
                     f"{message.header.recipient_id}|" \
                     f"{message.payload.command}|" \
                     f"{data_json}"
            
            return compact
            
        except Exception as e:
            self.logger.error(f"Compact serialization error: {e}")
            raise SerializationError(f"Compact serialization failed: {e}")
    
    def to_binary(self, message: Message) -> bytes:
        """Serialize message to binary format using pickle."""
        try:
            return pickle.dumps(message)
        except Exception as e:
            self.logger.error(f"Binary serialization error: {e}")
            raise SerializationError(f"Binary serialization failed: {e}")
    
    def from_json(self, json_str: str) -> Message:
        """Deserialize message from JSON."""
        from .parser import MessageParser
        parser = MessageParser()
        message = parser.parse_json_message(json_str)
        
        if not message:
            raise SerializationError("Failed to deserialize JSON message")
        
        return message
    
    def from_msgpack(self, data: bytes) -> Message:
        """Deserialize message from MessagePack."""
        try:
            message_dict = msgpack.unpackb(data, raw=False)
            from .parser import MessageParser
            parser = MessageParser()
            return parser._dict_to_message(message_dict)
            
        except Exception as e:
            self.logger.error(f"MessagePack deserialization error: {e}")
            raise SerializationError(f"MessagePack deserialization failed: {e}")
    
    def from_compact_string(self, compact_str: str) -> Message:
        """Deserialize from compact string format."""
        from .parser import MessageParser
        parser = MessageParser()
        message = parser.parse_compact_message(compact_str)
        
        if not message:
            raise SerializationError("Failed to deserialize compact message")
        
        return message
    
    def from_binary(self, data: bytes) -> Message:
        """Deserialize message from binary format."""
        try:
            return pickle.loads(data)
        except Exception as e:
            self.logger.error(f"Binary deserialization error: {e}")
            raise SerializationError(f"Binary deserialization failed: {e}")
    
    def get_serialized_size(self, message: Message, format: str = "json") -> int:
        """Get serialized size of message in bytes."""
        try:
            if format == "json":
                return len(self.to_json(message, compact=True).encode('utf-8'))
            elif format == "msgpack":
                return len(self.to_msgpack(message))
            elif format == "compact":
                return len(self.to_compact_string(message).encode('utf-8'))
            elif format == "binary":
                return len(self.to_binary(message))
            else:
                raise ValueError(f"Unknown format: {format}")
                
        except Exception as e:
            self.logger.error(f"Size calculation error: {e}")
            return 0
