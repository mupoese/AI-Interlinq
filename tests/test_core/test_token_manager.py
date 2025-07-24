# tests/test_core/test_token_manager.py
"""Tests for TokenManager."""

import pytest
import time
import asyncio
from ai_interlinq.core.token_manager import TokenManager, TokenStatus


class TestTokenManager:
    
    def test_generate_token(self):
        """Test token generation."""
        manager = TokenManager(default_ttl=300)
        
        token = manager.generate_token("test_session")
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
    
    def test_validate_token(self):
        """Test token validation."""
        manager = TokenManager(default_ttl=300)
        
        token = manager.generate_token("test_session")
        is_valid, session_id = manager.validate_token(token)
        
        assert is_valid is True
        assert session_id == "test_session"
    
    def test_invalid_token(self):
        """Test validation of invalid token."""
        manager = TokenManager()
        
        is_valid, session_id = manager.validate_token("invalid_token")
        
        assert is_valid is False
        assert session_id is None
    
    def test_token_expiration(self):
        """Test token expiration."""
        manager = TokenManager(default_ttl=1)  # 1 second TTL
        
        token = manager.generate_token("test_session")
        
        # Token should be valid initially
        is_valid, _ = manager.validate_token(token)
        assert is_valid is True
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Token should be invalid after expiration
        is_valid, _ = manager.validate_token(token)
        assert is_valid is False
    
    def test_revoke_token(self):
        """Test token revocation."""
        manager = TokenManager()
        
        token = manager.generate_token("test_session")
        
        # Token should be valid initially
        is_valid, _ = manager.validate_token(token)
        assert is_valid is True
        
        # Revoke token
        success = manager.revoke_token("test_session")
        assert success is True
        
        # Token should be invalid after revocation
        is_valid, _ = manager.validate_token(token)
        assert is_valid is False
    
    def test_cleanup_expired_tokens(self):
        """Test cleanup of expired tokens."""
        manager = TokenManager(default_ttl=1)
        
        # Generate tokens
        token1 = manager.generate_token("session1")
        token2 = manager.generate_token("session2")
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Cleanup expired tokens
        cleaned_count = manager.cleanup_expired_tokens()
        
        assert cleaned_count == 2
        
        # Tokens should be invalid
        is_valid1, _ = manager.validate_token(token1)
        is_valid2, _ = manager.validate_token(token2)
        
        assert is_valid1 is False
        assert is_valid2 is False
    
    def test_get_token_info(self):
        """Test getting token information."""
        manager = TokenManager()
        
        token = manager.generate_token("test_session")
        token_info = manager.get_token_info("test_session")
        
        assert token_info is not None
        assert token_info["session_id"] == "test_session"
        assert token_info["status"] == TokenStatus.ACTIVE.value
        assert "created_at" in token_info
        assert "expires_at" in token_info
