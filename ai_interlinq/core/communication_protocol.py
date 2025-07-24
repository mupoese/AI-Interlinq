"""
Enhanced Communication Protocol for AI-Interlinq
Adds compression, batching, streaming, and advanced features.
"""

import json
import time
import zlib
import hashlib
from typing import Dict, Any, Optional, List, Union, Iterator
from enum import Enum
from dataclasses import dataclass, asdict, field
import asyncio
from collections import deque


class MessageType(Enum):
    """Enhanced message types."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    HANDSHAKE = "handshake"
    BATCH = "batch"
    STREAM_START = "stream_start"
    STREAM_DATA = "stream_data"
    STREAM_END = "stream_end"
    ACK = "acknowledgment"


class Priority(Enum):
    """Enhanced priority levels with numeric values for easier comparison."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    REALTIME = 5  # New highest priority for real-time communication


class CompressionType(Enum):
    """Compression algorithms."""
    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"


class MessageFlags(Enum):
    """Message processing flags."""
    COMPRESS = "compress"
    ENCRYPT = "encrypt"
    ACKNOWLEDGE = "acknowledge"
    PERSIST = "persist"
    BROADCAST = "broadcast"
    ORDERED = "ordered"


@dataclass
class MessageHeader:
    """Enhanced message header with additional metadata."""
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: str
    timestamp: float
    priority: Priority
    session_id: str
    protocol_version: str = "2.0"
    
    # Enhanced fields
    sequence_number: Optional[int] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: Optional[int] = None  # Time to live in seconds
    compression: CompressionType = CompressionType.NONE
    flags: List[MessageFlags] = field(default_factory=list)
    checksum: Optional[str] = None
    
    # Routing and load balancing
    routing_key: Optional[str] = None
    load_balance_group: Optional[str] = None
    
    # Performance tracking
    created_at: float = field(default_factory=time.time)
    processing_deadline: Optional[float] = None


@dataclass
class MessagePayload:
    """Enhanced message payload with streaming support."""
    command: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
    # Streaming support
    stream_id: Optional[str] = None
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None
    is_final_chunk: bool = False
    
    # Large data handling
    data_refs: Optional[List[str]] = None  # References to external data
    compressed_size: Optional[int] = None
    original_size: Optional[int] = None


@dataclass
class BatchMessage:
    """Container for batch messages."""
    batch_id: str
    messages: List['Message']
    batch_size: int
    compression: CompressionType = CompressionType.ZLIB
    created_at: float = field(default_factory=time.time)


@dataclass
class Message:
    """Enhanced message structure."""
    header: MessageHeader
    payload: MessagePayload
    signature: Optional[str] = None
    
    # Performance tracking
    processing_start: Optional[float] = None
    processing_end: Optional[float] = None
    hop_count: int = 0
    route_history: List[str] = field(default_factory=list)


class StreamManager:
    """Manages message streams for large data transfers."""
    
    def __init__(self):
        self._active_streams: Dict[str, Dict] = {}
        self._stream_buffers: Dict[str, List[Message]] = {}
        self._stream_timeouts: Dict[str, float] = {}
    
    def start_stream(self, stream_id: str, total_chunks: int, timeout: float = 300.0) -> None:
        """Start a new message stream."""
        self._active_streams[stream_id] = {
            "total_chunks": total_chunks,
            "received_chunks": 0,
            "started_at": time.time(),
            "timeout": timeout
        }
        self._stream_buffers[stream_id] = [None] * total_chunks
        self._stream_timeouts[stream_id] = time.time() + timeout
    
    def add_chunk(self, message: Message) -> Optional[List[Message]]:
        """
        Add a chunk to a stream. Returns complete message list when stream is complete.
        """
        stream_id = message.payload.stream_id
        chunk_index = message.payload.chunk_index
        
        if stream_id not in self._active_streams:
            return None
        
        # Add chunk to buffer
        self._stream_buffers[stream_id][chunk_index] = message
        self._active_streams[stream_id]["received_chunks"] += 1
        
        # Check if stream is complete
        stream_info = self._active_streams[stream_id]
        if stream_info["received_chunks"] == stream_info["total_chunks"]:
            # Stream complete
            complete_messages = self._stream_buffers[stream_id]
            self._cleanup_stream(stream_id)
            return complete_messages
        
        return None
    
    def cleanup_expired_streams(self) -> List[str]:
        """Clean up expired streams and return their IDs."""
        now = time.time()
        expired_streams = []
        
        for stream_id, timeout in self._stream_timeouts.items():
            if now > timeout:
                expired_streams.append(stream_id)
        
        for stream_id in expired_streams:
            self._cleanup_stream(stream_id)
        
        return expired_streams
    
    def _cleanup_stream(self, stream_id: str) -> None:
        """Clean up stream data."""
        self._active_streams.pop(stream_id, None)
        self._stream_buffers.pop(stream_id, None)
        self._stream_timeouts.pop(stream_id, None)


class EnhancedCommunicationProtocol:
    """Enhanced communication protocol with advanced features."""
    
    PROTOCOL_VERSION = "2.0"
    MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_BATCH_SIZE = 1000
    COMPRESSION_THRESHOLD = 1024  # Compress messages larger than 1KB
    
    def __init__(self, agent_id: str, enable_compression: bool = True):
        """
        Initialize enhanced communication protocol.
        
        Args:
            agent_id: Unique identifier for this AI agent
            enable_compression: Enable automatic compression
        """
        self.agent_id = agent_id
        self.enable_compression = enable_compression
        self._message_counter = 0
        self._sequence_counter = 0
        self._stream_manager = StreamManager()
        
        # Performance tracking
        self._message_stats = {
            "messages_created": 0,
            "messages_serialized": 0,
            "messages_compressed": 0,
            "bytes_saved": 0,
            "compression_ratio": 0.0
        }
    
    def create_message(
        self,
        recipient_id: str,
        message_type: MessageType,
        command: str,
        data: Dict[str, Any],
        session_id: str,
        priority: Priority = Priority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Message:
        """
        Create an enhanced message with additional features.
        
        Additional kwargs:
        - correlation_id: For request-response correlation
        - reply_to: For directing responses
        - ttl: Time to live in seconds
        - flags: List of MessageFlags
        - routing_key: For advanced routing
        - processing_deadline: Deadline for processing
        """
        self._message_counter += 1
        self._sequence_counter += 1
        
        message_id = f"{self.agent_id}_{self._message_counter}_{int(time.time() * 1000)}"
        
        # Auto-enable compression for large messages
        should_compress = (
            self.enable_compression and 
            len(json.dumps(data, separators=(',', ':')).encode()) > self.COMPRESSION_THRESHOLD
        )
        
        flags = kwargs.get('flags', [])
        if should_compress and MessageFlags.COMPRESS not in flags:
            flags.append(MessageFlags.COMPRESS)
        
        header = MessageHeader(
            message_id=message_id,
            message_type=message_type,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            timestamp=time.time(),
            priority=priority,
            session_id=session_id,
            protocol_version=self.PROTOCOL_VERSION,
            sequence_number=self._sequence_counter,
            correlation_id=kwargs.get('correlation_id'),
            reply_to=kwargs.get('reply_to'),
            ttl=kwargs.get('ttl'),
            compression=CompressionType.ZLIB if should_compress else CompressionType.NONE,
            flags=flags,
            routing_key=kwargs.get('routing_key'),
            processing_deadline=kwargs.get('processing_deadline')
        )
        
        payload = MessagePayload(
            command=command,
            data=data,
            metadata=metadata
        )
        
        message = Message(header=header, payload=payload)
        self._message_stats["messages_created"] += 1
        
        return message
    
    def create_batch_message(
        self,
        messages: List[Message],
        batch_id: Optional[str] = None,
        compression: CompressionType = CompressionType.ZLIB
    ) -> Message:
        """Create a batch message containing multiple messages."""
        if len(messages) > self.MAX_BATCH_SIZE:
            raise ValueError(f"Batch size {len(messages)} exceeds maximum {self.MAX_BATCH_SIZE}")
        
        batch_id = batch_id or f"batch_{self.agent_id}_{int(time.time() * 1000)}"
        
        batch = BatchMessage(
            batch_id=batch_id,
            messages=messages,
            batch_size=len(messages),
            compression=compression
        )
        
        # Create container message
        return self.create_message(
            recipient_id="*",  # Broadcast or will be overridden
            message_type=MessageType.BATCH,
            command="batch_messages",
            data={"batch": asdict(batch)},
            session_id="batch_session",
            flags=[MessageFlags.COMPRESS] if compression != CompressionType.NONE else []
        )
    
    def create_stream_messages(
        self,
        recipient_id: str,
        command: str,
        large_data: Any,
        session_id: str,
        chunk_size: int = 64 * 1024,  # 64KB chunks
        **kwargs
    ) -> List[Message]:
        """
        Create a stream of messages for large data transfer.
        
        Args:
            recipient_id: Target agent
            command: Command for the data
            large_data: Large data to stream
            session_id: Session ID
            chunk_size: Size of each chunk in bytes
            
        Returns:
            List of stream messages
        """
        # Serialize data
        serialized_data = json.dumps(large_data, separators=(',', ':'))
        data_bytes = serialized_data.encode('utf-8')
        
        # Calculate chunks
        total_size = len(data_bytes)
        chunks = []
        chunk_count = (total_size + chunk_size - 1) // chunk_size
        
        stream_id = f"stream_{self.agent_id}_{int(time.time() * 1000)}"
        
        for i in range(chunk_count):
            start_idx = i * chunk_size
            end_idx = min(start_idx + chunk_size, total_size)
            chunk_data = data_bytes[start_idx:end_idx]
            
            # Create chunk message
            chunk_message = self.create_message(
                recipient_id=recipient_id,
                message_type=MessageType.STREAM_DATA,
                command=command,
                data={
                    "chunk_data": chunk_data.decode('utf-8', errors='ignore'),
                    "original_size": total_size
                },
                session_id=session_id,
                **kwargs
            )
            
            # Set stream metadata
            chunk_message.payload.stream_id = stream_id
            chunk_message.payload.chunk_index = i
            chunk_message.payload.total_chunks = chunk_count
            chunk_message.payload.is_final_chunk = (i == chunk_count - 1)
            chunk_message.payload.original_size = total_size
            chunk_message.payload.compressed_size = len(chunk_data)
            
            chunks.append(chunk_message)
        
        return chunks
    
    def serialize_message(self, message: Message) -> str:
        """Enhanced serialization with compression support."""
        # Convert message to dictionary
        message_dict = self._message_to_dict(message)
        
        # Calculate checksum before compression
        message_json = json.dumps(message_dict, separators=(',', ':'))
        message_dict["header"]["checksum"] = hashlib.sha256(message_json.encode()).hexdigest()[:16]
        
        # Serialize again with checksum
        serialized = json.dumps(message_dict, separators=(',', ':'))
        
        # Apply compression if enabled
        if message.header.compression != CompressionType.NONE:
            compressed = self._compress_data(serialized, message.header.compression)
            self._message_stats["messages_compressed"] += 1
            self._message_stats["bytes_saved"] += len(serialized) - len(compressed)
            
            # Wrap compressed data
            compressed_wrapper = {
                "compressed": True,
                "compression": message.header.compression.value,
                "original_size": len(serialized),
                "data": compressed
            }
            serialized = json.dumps(compressed_wrapper, separators=(',', ':'))
        
        self._message_stats["messages_serialized"] += 1
        return serialized
    
    def deserialize_message(self, message_json: str) -> Optional[Message]:
        """Enhanced deserialization with decompression support."""
        try:
            data = json.loads(message_json)
            
            # Handle compressed messages
            if isinstance(data, dict) and data.get("compressed"):
                compression_type = CompressionType(data["compression"])
                compressed_data = data["data"]
                
                # Decompress
                decompressed = self._decompress_data(compressed_data, compression_type)
                data = json.loads(decompressed)
            
            # Verify checksum
            header_data = data["header"]
            expected_checksum = header_data.pop("checksum", None)
            
            if expected_checksum:
                # Recalculate checksum
                temp_json = json.dumps(data, separators=(',', ':'))
                actual_checksum = hashlib.sha256(temp_json.encode()).hexdigest()[:16]
                
                if actual_checksum != expected_checksum:
                    raise ValueError("Message checksum mismatch")
            
            # Reconstruct message
            return self._dict_to_message(data)
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return None
    
    def _message_to_dict(self, message: Message) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            "header": {
                **asdict(message.header),
                "message_type": message.header.message_type.value,
                "priority": message.header.priority.value,
                "compression": message.header.compression.value,
                "flags": [flag.value for flag in message.header.flags]
            },
            "payload": asdict(message.payload),
            "signature": message.signature,
            "processing_start": message.processing_start,
            "processing_end": message.processing_end,
            "hop_count": message.hop_count,
            "route_history": message.route_history
        }
    
    def _dict_to_message(self, data: Dict[str, Any]) -> Message:
        """Convert dictionary to message object."""
        header_data = data["header"]
        header = MessageHeader(
            message_id=header_data["message_id"],
            message_type=MessageType(header_data["message_type"]),
            sender_id=header_data["sender_id"],
            recipient_id=header_data["recipient_id"],
            timestamp=header_data["timestamp"],
            priority=Priority(header_data["priority"]),
            session_id=header_data["session_id"],
            protocol_version=header_data.get("protocol_version", "2.0"),
            sequence_number=header_data.get("sequence_number"),
            correlation_id=header_data.get("correlation_id"),
            reply_to=header_data.get("reply_to"),
            ttl=header_data.get("ttl"),
            compression=CompressionType(header_data.get("compression", "none")),
            flags=[MessageFlags(flag) for flag in header_data.get("flags", [])],
            routing_key=header_data.get("routing_key"),
            load_balance_group=header_data.get("load_balance_group"),
            created_at=header_data.get("created_at", time.time()),
            processing_deadline=header_data.get("processing_deadline")
        )
        
        payload_data = data["payload"]
        payload = MessagePayload(
            command=payload_data["command"],
            data=payload_data["data"],
            metadata=payload_data.get("metadata"),
            stream_id=payload_data.get("stream_id"),
            chunk_index=payload_data.get("chunk_index"),
            total_chunks=payload_data.get("total_chunks"),
            is_final_chunk=payload_data.get("is_final_chunk", False),
            data_refs=payload_data.get("data_refs"),
            compressed_size=payload_data.get("compressed_size"),
            original_size=payload_data.get("original_size")
        )
        
        return Message(
            header=header,
            payload=payload,
            signature=data.get("signature"),
            processing_start=data.get("processing_start"),
            processing_end=data.get("processing_end"),
            hop_count=data.get("hop_count", 0),
            route_history=data.get("route_history", [])
        )
    
    def _compress_data(self, data: str, compression_type: CompressionType) -> str:
        """Compress data using specified algorithm."""
        data_bytes = data.encode('utf-8')
        
        if compression_type == CompressionType.ZLIB:
            compressed = zlib.compress(data_bytes, level=6)
        else:
            compressed = data_bytes
        
        # Return base64 encoded compressed data
        import base64
        return base64.b64encode(compressed).decode('ascii')
    
    def _decompress_data(self, compressed_data: str, compression_type: CompressionType) -> str:
        """Decompress data using specified algorithm."""
        import base64
        compressed_bytes = base64.b64decode(compressed_data.encode('ascii'))
        
        if compression_type == CompressionType.ZLIB:
            decompressed = zlib.decompress(compressed_bytes)
        else:
            decompressed = compressed_bytes
        
        return decompressed.decode('utf-8')
    
    def validate_message(self, message: Message) -> tuple[bool, str]:
        """Enhanced message validation."""
        # Check protocol version
        if message.header.protocol_version != self.PROTOCOL_VERSION:
            return False, f"Unsupported protocol version: {message.header.protocol_version}"
        
        # Check message size
        serialized = self.serialize_message(message)
        if len(serialized.encode()) > self.MAX_MESSAGE_SIZE:
            return False, "Message exceeds maximum size"
        
        # Check TTL
        if message.header.ttl:
            age = time.time() - message.header.timestamp
            if age > message.header.ttl:
                return False, "Message TTL expired"
        
        # Check processing deadline
        if message.header.processing_deadline:
            if time.time() > message.header.processing_deadline:
                return False, "Processing deadline exceeded"
        
        # Check required fields
        required_fields = [
            message.header.message_id,
            message.header.sender_id,
            message.header.recipient_id,
            message.payload.command
        ]
        
        if not all(required_fields):
            return False, "Missing required fields"
        
        return True, "Valid"
    
    def create_error_response(
        self,
        original_message: Message,
        error_code: str,
        error_description: str,
        include_original: bool = False
    ) -> Message:
        """Create an enhanced error response message."""
        error_data = {
            "error_code": error_code,
            "error_description": error_description,
            "original_message_id": original_message.header.message_id,
            "timestamp": time.time()
        }
        
        if include_original:
            error_data["original_message"] = self._message_to_dict(original_message)
        
        return self.create_message(
            recipient_id=original_message.header.sender_id,
            message_type=MessageType.ERROR,
            command="error",
            data=error_data,
            session_id=original_message.header.session_id,
            priority=original_message.header.priority,
            correlation_id=original_message.header.message_id,
            reply_to=original_message.header.reply_to
        )
    
    def create_acknowledgment(self, original_message: Message) -> Message:
        """Create an acknowledgment message."""
        return self.create_message(
            recipient_id=original_message.header.sender_id,
            message_type=MessageType.ACK,
            command="acknowledge",
            data={
                "acknowledged_message_id": original_message.header.message_id,
                "acknowledged_at": time.time()
            },
            session_id=original_message.header.session_id,
            priority=Priority.LOW,
            correlation_id=original_message.header.message_id
        )
    
    def create_heartbeat(self, session_id: str, include_stats: bool = False) -> Message:
        """Create an enhanced heartbeat message."""
        data = {
            "timestamp": time.time(),
            "agent_id": self.agent_id,
            "sequence": self._sequence_counter
        }
        
        if include_stats:
            data["stats"] = self.get_protocol_stats()
        
        return self.create_message(
            recipient_id="*",  # Broadcast
            message_type=MessageType.HEARTBEAT,
            command="ping",
            data=data,
            session_id=session_id,
            priority=Priority.LOW,
            ttl=60  # Heartbeats expire after 1 minute
        )
    
    def process_stream_message(self, message: Message) -> Optional[List[Message]]:
        """Process a stream message and return complete data when ready."""
        if message.header.message_type == MessageType.STREAM_START:
            stream_id = message.payload.stream_id
            total_chunks = message.payload.total_chunks
            self._stream_manager.start_stream(stream_id, total_chunks)
            return None
        
        elif message.header.message_type == MessageType.STREAM_DATA:
            return self._stream_manager.add_chunk(message)
        
        return None
    
    def cleanup_expired_streams(self) -> List[str]:
        """Clean up expired streams."""
        return self._stream_manager.cleanup_expired_streams()
    
    def get_protocol_stats(self) -> Dict[str, Any]:
        """Get protocol performance statistics."""
        stats = dict(self._message_stats)
        
        if stats["messages_compressed"] > 0:
            stats["compression_ratio"] = stats["bytes_saved"] / (stats["bytes_saved"] + sum(
                len(self.serialize_message(Message(
                    MessageHeader("", MessageType.REQUEST, "", "", 0, Priority.NORMAL, ""),
                    MessagePayload("", {})
                )).encode()) for _ in range(stats["messages_compressed"])
            )) if stats["messages_compressed"] > 0 else 0
        
        stats["active_streams"] = len(self._stream_manager._active_streams)
        stats["protocol_version"] = self.PROTOCOL_VERSION
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset protocol statistics."""
        self._message_stats = {
            "messages_created": 0,
            "messages_serialized": 0,
            "messages_compressed": 0,
            "bytes_saved": 0,
            "compression_ratio": 0.0
        }
