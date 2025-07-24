# ai_interlinq/utils/serializer.py

"""
Message Serializer for AI-Interlinq
Advanced serialization utilities with multiple format support.
"""

import json
import pickle
import msgpack
import base64
import gzip
from typing import Dict, Any, Optional, Union, List
from dataclasses import asdict
from enum import Enum

from ..core.communication_protocol import Message


class SerializationFormat(Enum):
    """Supported serialization formats."""
    JSON = "json"
    MSGPACK = "msgpack"
    PICKLE = "pickle"
    BINARY = "binary"


class CompressionType(Enum):
    """Supported compression types."""
    NONE = "none"
    GZIP = "gzip"


class MessageSerializer:
    """Advanced message serializer with multiple format support."""
    
    def __init__(self, default_format: SerializationFormat = SerializationFormat.JSON):
        """
        Initialize message serializer.
        
        Args:
            default_format: Default serialization format
        """
        self.default_format = default_format
        self._serializers = {
            SerializationFormat.JSON: self._serialize_json,
            SerializationFormat.MSGPACK: self._serialize_msgpack,
            SerializationFormat.PICKLE: self._serialize_pickle,
            SerializationFormat.BINARY: self._serialize_binary
        }
        self._deserializers = {
            SerializationFormat.JSON: self._deserialize_json,
            SerializationFormat.MSGPACK: self._deserialize_msgpack,
            SerializationFormat.PICKLE: self._deserialize_pickle,
            SerializationFormat.BINARY: self._deserialize_binary
        }
    
    def serialize(
        self,
        message: Message,
        format: Optional[SerializationFormat] = None,
        compress: CompressionType = CompressionType.NONE,
        **kwargs
    ) -> bytes:
        """
        Serialize a message to bytes.
        
        Args:
            message: Message to serialize
            format: Serialization format
            compress: Compression type
            **kwargs: Additional serialization options
            
        Returns:
            Serialized message as bytes
        """
        format = format or self.default_format
        
        # Get serializer
        serializer = self._serializers.get(format)
        if not serializer:
            raise ValueError(f"Unsupported serialization format: {format}")
        
        # Serialize message
        data = serializer(message, **kwargs)
        
        # Apply compression if requested
        if compress == CompressionType.GZIP:
            data = gzip.compress(data)
        
        return data
    
    def deserialize(
        self,
        data: bytes,
        format: Optional[SerializationFormat] = None,
        compressed: CompressionType = CompressionType.NONE
    ) -> Message:
        """
        Deserialize bytes to a message.
        
        Args:
            data: Serialized message data
            format: Serialization format
            compressed: Compression type used
            
        Returns:
            Deserialized Message object
        """
        format = format or self.default_format
        
        # Decompress if needed
        if compressed == CompressionType.GZIP:
            data = gzip.decompress(data)
        
        # Get deserializer
        deserializer = self._deserializers.get(format)
        if not deserializer:
            raise ValueError(f"Unsupported serialization format: {format}")
        
        return deserializer(data)
    
    def _serialize_json(self, message: Message, indent: Optional[int] = None) -> bytes:
        """Serialize message to JSON."""
        message_dict = {
            "header": {
                **asdict(message.header),
                "message_type": message.header.message_type.value,
                "priority": message.header.priority.value
            },
            "payload": asdict(message.payload),
            "signature": message.signature
        }
        
        json_str = json.dumps(message_dict, indent=indent, separators=(',', ':'))
        return json_str.encode('utf-8')
    
    def _deserialize_json(self, data: bytes) -> Message:
        """Deserialize JSON to message."""
        from ..utils.parser import MessageParser
        
        parser = MessageParser()
        json_str = data.decode('utf-8')
        result = parser.parse_message(json_str)
        
        if not result.success:
            raise ValueError(f"Failed to deserialize JSON message: {result.error}")
        
        return result.message
    
    def _serialize_msgpack(self, message: Message) -> bytes:
        """Serialize message to MessagePack."""
        try:
            import msgpack
        except ImportError:
            raise ImportError("msgpack-python is required for MessagePack serialization")
        
        message_dict = {
            "header": {
                **asdict(message.header),
                "message_type": message.header.message_type.value,
                "priority": message.header.priority.value
            },
            "payload": asdict(message.payload),
            "signature": message.signature
        }
        
        return msgpack.packb(message_dict, use_bin_type=True)
    
    def _deserialize_msgpack(self, data: bytes) -> Message:
        """Deserialize MessagePack to message."""
        try:
            import msgpack
        except ImportError:
            raise ImportError("msgpack-python is required for MessagePack deserialization")
        
        from ..utils.parser import MessageParser
        
        message_dict = msgpack.unpackb(data, raw=False)
        parser = MessageParser()
        result = parser.parse_message(message_dict)
        
        if not result.success:
            raise ValueError(f"Failed to deserialize MessagePack message: {result.error}")
        
        return result.message
    
    def _serialize_pickle(self, message: Message) -> bytes:
        """Serialize message to Pickle."""
        return pickle.dumps(message)
    
    def _deserialize_pickle(self, data: bytes) -> Message:
        """Deserialize Pickle to message."""
        return pickle.loads(data)
    
    def _serialize_binary(self, message: Message) -> bytes:
        """Serialize message to custom binary format."""
        # Custom binary format for high performance
        json_data = self._serialize_json(message)
        header = len(json_data).to_bytes(4, byteorder='big')
        return header + json_data
    
    def _deserialize_binary(self, data: bytes) -> Message:
        """Deserialize custom binary format to message."""
        if len(data) < 4:
            raise ValueError("Invalid binary message format")
        
        length = int.from_bytes(data[:4], byteorder='big')
        json_data = data[4:4+length]
        
        return self._deserialize_json(json_data)
    
    def serialize_batch(
        self,
        messages: List[Message],
        format: Optional[SerializationFormat] = None,
        compress: CompressionType = CompressionType.NONE
    ) -> bytes:
        """Serialize multiple messages in batch."""
        format = format or self.default_format
        
        # Serialize each message
        serialized_messages = []
        for message in messages:
            serialized = self.serialize(message, format, CompressionType.NONE)
            serialized_messages.append(serialized)
        
        # Create batch format
        batch_data = {
            "format": format.value,
            "count": len(messages),
            "messages": [base64.b64encode(msg).decode('ascii') for msg in serialized_messages]
        }
        
        batch_json = json.dumps(batch_data).encode('utf-8')
        
        # Apply compression
        if compress == CompressionType.GZIP:
            batch_json = gzip.compress(batch_json)
        
        return batch_json
    
    def deserialize_batch(
        self,
        data: bytes,
        compressed: CompressionType = CompressionType.NONE
    ) -> List[Message]:
        """Deserialize batch of messages."""
        # Decompress if needed
        if compressed == CompressionType.GZIP:
            data = gzip.decompress(data)
        
        # Parse batch format
        batch_data = json.loads(data.decode('utf-8'))
        format = SerializationFormat(batch_data["format"])
        
        # Deserialize each message
        messages = []
        for encoded_msg in batch_data["messages"]:
            msg_data = base64.b64decode(encoded_msg.encode('ascii'))
            message = self.deserialize(msg_data, format, CompressionType.NONE)
            messages.append(message)
        
        return messages
    
    def get_serialization_stats(self, message: Message) -> Dict[str, Any]:
        """Get serialization statistics for different formats."""
        stats = {}
        
        for format in SerializationFormat:
            try:
                serialized = self.serialize(message, format)
                compressed = self.serialize(message, format, CompressionType.GZIP)
                
                stats[format.value] = {
                    "size": len(serialized),
                    "compressed_size": len(compressed),
                    "compression_ratio": len(serialized) / len(compressed) if compressed else 1.0
                }
            except Exception as e:
                stats[format.value] = {"error": str(e)}
        
        return stats
    
    def optimize_for_size(self, message: Message) -> bytes:
        """Serialize with optimal settings for minimum size."""
        # Try different formats and return the smallest
        best_size = float('inf')
        best_data = None
        
        for format in SerializationFormat:
            try:
                data = self.serialize(message, format, CompressionType.GZIP)
                if len(data) < best_size:
                    best_size = len(data)
                    best_data = data
            except Exception:
                continue
        
        return best_data or self.serialize(message, SerializationFormat.JSON, CompressionType.GZIP)
    
    def optimize_for_speed(self, message: Message) -> bytes:
        """Serialize with optimal settings for speed."""
        # Binary format is typically fastest
        return self.serialize(message, SerializationFormat.BINARY, CompressionType.NONE)
