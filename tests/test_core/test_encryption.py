# tests/test_core/test_encryption.py
"""Tests for EncryptionHandler."""

import pytest
from ai_interlinq.core.encryption import EncryptionHandler


class TestEncryptionHandler:
    
    def test_encryption_decryption_roundtrip(self):
        """Test encryption/decryption roundtrip."""
        handler = EncryptionHandler("test_key_123")
        
        original_message = "This is a test message for encryption"
        
        # Encrypt
        success, encrypted = handler.encrypt_message(original_message)
        assert success is True
        assert encrypted != original_message
        
        # Decrypt
        success, decrypted = handler.decrypt_message(encrypted)
        assert success is True
        assert decrypted == original_message
    
    def test_encryption_without_key(self):
        """Test encryption without setting a key."""
        handler = EncryptionHandler()
        
        success, error = handler.encrypt_message("test message")
        assert success is False
        assert "No encryption key set" in error
    
    def test_decryption_without_key(self):
        """Test decryption without setting a key."""
        handler = EncryptionHandler()
        
        success, error = handler.decrypt_message("fake_encrypted_data")
        assert success is False
        assert "No encryption key set" in error
    
    def test_set_shared_key(self):
        """Test setting shared key after initialization."""
        handler = EncryptionHandler()
        handler.set_shared_key("new_test_key")
        
        message = "Test message"
        success, encrypted = handler.encrypt_message(message)
        assert success is True
        
        success, decrypted = handler.decrypt_message(encrypted)
        assert success is True
        assert decrypted == message
    
    def test_generate_shared_key(self):
        """Test shared key generation."""
        handler = EncryptionHandler()
        
        key = handler.generate_shared_key()
        assert key is not None
        assert len(key) > 0
        assert isinstance(key, str)
    
    def test_message_hash(self):
        """Test message hash generation and verification."""
        handler = EncryptionHandler()
        
        message = "Test message for hashing"
        hash1 = handler.generate_message_hash(message)
        hash2 = handler.generate_message_hash(message)
        
        # Same message should produce same hash
        assert hash1 == hash2
        
        # Hash verification should work
        is_valid = handler.verify_message_hash(message, hash1)
        assert is_valid is True
        
        # Different message should produce different hash
        different_hash = handler.generate_message_hash("Different message")
        assert hash1 != different_hash
    
    def test_create_secure_session_key(self):
        """Test secure session key creation."""
        handler = EncryptionHandler("master_key")
        
        session_key1 = handler.create_secure_session_key("session1")
        session_key2 = handler.create_secure_session_key("session2")
        
        # Different sessions should have different keys
        assert session_key1 != session_key2
        
        # Same session should produce same key
        session_key1_again = handler.create_secure_session_key("session1")
        assert session_key1 == session_key1_again
