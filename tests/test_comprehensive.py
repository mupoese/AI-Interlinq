# tests/test_comprehensive.py

"""
Comprehensive tests for AI-Interlinq functionality
Tests all major components and their interactions.
"""

import pytest
import asyncio
import time
import json
from typing import Dict, Any

from ai_interlinq import (
    TokenManager, EncryptionHandler, CommunicationProtocol, MessageHandler,
    AdvancedMemorySystem, PerformanceMonitor, MessageSerializer, MessageParser
)
from ai_interlinq.core.communication_protocol import MessageType, Priority, Message


class TestTokenManager:
    """Test token management functionality."""
    
    def test_token_generation(self):
        """Test token generation."""
        manager = TokenManager(default_ttl=3600)
        session_id = "test_session"
        
        token = manager.generate_token(session_id)
        assert token is not None
        assert len(token) > 20  # Secure token should be reasonably long
        
        # Validate token
        is_valid, returned_session = manager.validate_token(token)
        assert is_valid is True
        assert returned_session == session_id
    
    def test_token_expiration(self):
        """Test token expiration."""
        manager = TokenManager(default_ttl=1)  # 1 second TTL
        session_id = "test_session"
        
        token = manager.generate_token(session_id)
        assert manager.validate_token(token)[0] is True
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Clean up expired tokens
        cleaned = manager.cleanup_expired_tokens()
        assert cleaned >= 1
        
        # Token should now be invalid
        is_valid, _ = manager.validate_token(token)
        assert is_valid is False
    
    def test_token_revocation(self):
        """Test token revocation."""
        manager = TokenManager()
        session_id = "test_session"
        
        token = manager.generate_token(session_id)
        assert manager.validate_token(token)[0] is True
        
        # Revoke token
        revoked = manager.revoke_token(session_id)
        assert revoked is True
        
        # Token should now be invalid
        is_valid, _ = manager.validate_token(token)
        assert is_valid is False


class TestEncryptionHandler:
    """Test encryption functionality."""
    
    def test_basic_encryption(self):
        """Test basic encryption and decryption."""
        handler = EncryptionHandler("test_shared_key")
        message = "Hello, encrypted world!"
        
        # Encrypt
        success, encrypted = handler.encrypt_message(message)
        assert success is True
        assert encrypted != message
        
        # Decrypt
        success, decrypted = handler.decrypt_message(encrypted)
        assert success is True
        assert decrypted == message
    
    def test_encryption_without_key(self):
        """Test encryption without key fails gracefully."""
        handler = EncryptionHandler()
        message = "Test message"
        
        success, error = handler.encrypt_message(message)
        assert success is False
        assert "No encryption key set" in error
    
    def test_key_generation(self):
        """Test shared key generation."""
        handler = EncryptionHandler()
        key = handler.generate_shared_key()
        
        assert key is not None
        assert len(key) > 20  # Should be a secure key
        
        # Use generated key
        handler.set_shared_key(key)
        
        message = "Test with generated key"
        success, encrypted = handler.encrypt_message(message)
        assert success is True
        
        success, decrypted = handler.decrypt_message(encrypted)
        assert success is True
        assert decrypted == message


class TestCommunicationProtocol:
    """Test communication protocol."""
    
    def test_message_creation(self):
        """Test message creation."""
        protocol = CommunicationProtocol("test_agent")
        
        message = protocol.create_message(
            recipient_id="target_agent",
            message_type=MessageType.REQUEST,
            command="test_command",
            data={"key": "value"},
            session_id="test_session"
        )
        
        assert message.header.sender_id == "test_agent"
        assert message.header.recipient_id == "target_agent"
        assert message.header.message_type == MessageType.REQUEST
        assert message.payload.command == "test_command"
        assert message.payload.data["key"] == "value"
    
    def test_message_serialization(self):
        """Test message serialization and deserialization."""
        protocol = CommunicationProtocol("test_agent")
        
        original_message = protocol.create_message(
            recipient_id="target_agent",
            message_type=MessageType.REQUEST,
            command="test_command",
            data={"key": "value", "number": 42},
            session_id="test_session"
        )
        
        # Serialize
        serialized = protocol.serialize_message(original_message)
        assert isinstance(serialized, str)
        
        # Deserialize
        deserialized = protocol.deserialize_message(serialized)
        assert deserialized is not None
        assert deserialized.header.sender_id == original_message.header.sender_id
        assert deserialized.payload.command == original_message.payload.command
        assert deserialized.payload.data == original_message.payload.data
    
    def test_message_validation(self):
        """Test message validation."""
        protocol = CommunicationProtocol("test_agent")
        
        # Valid message
        valid_message = protocol.create_message(
            recipient_id="target_agent",
            message_type=MessageType.REQUEST,
            command="test_command",
            data={"key": "value"},
            session_id="test_session"
        )
        
        is_valid, error = protocol.validate_message(valid_message)
        assert is_valid is True
        assert error == "Valid"
        
        # Invalid message (empty command)
        valid_message.payload.command = ""
        is_valid, error = protocol.validate_message(valid_message)
        assert is_valid is False
        assert "Missing command" in error


class TestMessageHandler:
    """Test message handling functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.token_manager = TokenManager()
        self.encryption = EncryptionHandler("test_key")
        self.handler = MessageHandler("test_agent", self.token_manager, self.encryption)
    
    def test_command_registration(self):
        """Test command handler registration."""
        handled_messages = []
        
        async def test_handler(message):
            handled_messages.append(message)
        
        self.handler.register_command_handler("test_command", test_handler)
        
        # Verify handler is registered
        assert "test_command" in self.handler._command_handlers
    
    @pytest.mark.asyncio
    async def test_message_processing(self):
        """Test message processing."""
        handled_messages = []
        
        async def test_handler(message):
            handled_messages.append(message)
        
        self.handler.register_command_handler("test_command", test_handler)
        
        # Create and process a message
        protocol = CommunicationProtocol("sender_agent")
        message = protocol.create_message(
            recipient_id="test_agent",
            message_type=MessageType.REQUEST,
            command="test_command",
            data={"test": "data"},
            session_id="test_session"
        )
        
        # Simulate receiving the message
        serialized = protocol.serialize_message(message)
        success, encrypted = self.encryption.encrypt_message(serialized)
        assert success is True
        
        await self.handler.receive_message(encrypted, encrypted=True)
        processed = await self.handler.process_messages("test_session")
        
        assert processed >= 1
        assert len(handled_messages) >= 1
        assert handled_messages[0].payload.command == "test_command"


class TestAdvancedMemorySystem:
    """Test advanced memory system."""
    
    def setup_method(self):
        """Setup for each test."""
        self.memory = AdvancedMemorySystem("test_agent", ":memory:")  # In-memory SQLite
    
    def test_snapshot_creation(self):
        """Test memory snapshot creation."""
        data = {"key": "value", "number": 42}
        tags = ["test", "snapshot"]
        
        snapshot_id = self.memory.create_snapshot(data, tags)
        assert snapshot_id is not None
        
        # Retrieve snapshot
        snapshot = self.memory.db.retrieve_snapshot(snapshot_id)
        assert snapshot is not None
        assert snapshot.data == data
        assert "test" in snapshot.tags
    
    def test_knowledge_injection(self):
        """Test knowledge injection and retrieval."""
        key = "test_knowledge"
        value = {"fact": "AI systems can learn and adapt", "confidence": 0.95}
        category = "general"
        
        # Inject knowledge
        success = self.memory.inject_knowledge(key, value, category)
        assert success is True
        
        # Retrieve knowledge
        retrieved = self.memory.retrieve_knowledge(key)
        assert retrieved == value
    
    def test_code_injection_security(self):
        """Test code injection security."""
        # Safe code should work
        safe_code = "len(context.get('data', []))"
        context = {"data": [1, 2, 3, 4, 5]}
        
        result = self.memory.process_code_injection(safe_code, context)
        assert result == 5
        
        # Unsafe code should be blocked
        unsafe_code = "import os; os.system('ls')"
        
        with pytest.raises(Exception):  # Should raise SecurityError
            self.memory.process_code_injection(unsafe_code, context)
    
    def test_memory_statistics(self):
        """Test memory statistics."""
        # Create some data
        self.memory.create_snapshot({"test": "data1"}, ["tag1"])
        self.memory.create_snapshot({"test": "data2
