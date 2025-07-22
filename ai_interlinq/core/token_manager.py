"""
Token Management System for AI-Interlinq
Handles token generation, validation, and lifecycle management.
"""

import secrets
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class TokenStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class Token:
    """Represents a communication token."""
    token_id: str
    value: str
    created_at: float
    expires_at: float
    status: TokenStatus
    session_id: str


class TokenManager:
    """Manages token lifecycle for AI communication."""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize TokenManager.
        
        Args:
            default_ttl: Default token time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self._tokens: Dict[str, Token] = {}
        self._session_tokens: Dict[str, str] = {}
    
    def generate_token(self, session_id: str, ttl: Optional[int] = None) -> str:
        """
        Generate a new secure token for a session.
        
        Args:
            session_id: Unique session identifier
            ttl: Token time-to-live in seconds
            
        Returns:
            Generated token string
        """
        ttl = ttl or self.default_ttl
        token_value = secrets.token_urlsafe(32)
        token_id = secrets.token_hex(16)
        
        now = time.time()
        expires_at = now + ttl
        
        token = Token(
            token_id=token_id,
            value=token_value,
            created_at=now,
            expires_at=expires_at,
            status=TokenStatus.ACTIVE,
            session_id=session_id
        )
        
        self._tokens[token_id] = token
        self._session_tokens[session_id] = token_id
        
        return token_value
    
    def validate_token(self, token_value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a token and return session ID if valid.
        
        Args:
            token_value: Token to validate
            
        Returns:
            Tuple of (is_valid, session_id)
        """
        for token in self._tokens.values():
            if token.value == token_value:
                if self._is_token_valid(token):
                    return True, token.session_id
                else:
                    return False, None
        
        return False, None
    
    def revoke_token(self, session_id: str) -> bool:
        """
        Revoke a token for a session.
        
        Args:
            session_id: Session to revoke token for
            
        Returns:
            True if token was revoked, False if not found
        """
        token_id = self._session_tokens.get(session_id)
        if token_id and token_id in self._tokens:
            self._tokens[token_id].status = TokenStatus.REVOKED
            return True
        return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        Remove expired tokens from storage.
        
        Returns:
            Number of tokens cleaned up
        """
        now = time.time()
        expired_tokens = []
        
        for token_id, token in self._tokens.items():
            if token.expires_at < now:
                token.status = TokenStatus.EXPIRED
                expired_tokens.append(token_id)
        
        for token_id in expired_tokens:
            token = self._tokens[token_id]
            del self._session_tokens[token.session_id]
            del self._tokens[token_id]
        
        return len(expired_tokens)
    
    def _is_token_valid(self, token: Token) -> bool:
        """Check if a token is currently valid."""
        now = time.time()
        return (
            token.status == TokenStatus.ACTIVE and 
            token.expires_at > now
        )
    
    def get_token_info(self, session_id: str) -> Optional[Dict]:
        """Get token information for a session."""
        token_id = self._session_tokens.get(session_id)
        if token_id and token_id in self._tokens:
            token = self._tokens[token_id]
            return {
                "token_id": token.token_id,
                "created_at": token.created_at,
                "expires_at": token.expires_at,
                "status": token.status.value,
                "session_id": token.session_id
            }
        return None
