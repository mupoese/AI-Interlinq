# File: /ai_interlinq/middleware/auth.py
# Directory: /ai_interlinq/middleware

"""
Authentication middleware for AI-Interlinq framework.
Provides JWT-based authentication with role management and session handling.
"""

import jwt
import time
import hashlib
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class AuthRole(Enum):
    """Authentication roles for AI agents."""
    ADMIN = "admin"
    AGENT = "agent" 
    OBSERVER = "observer"
    SYSTEM = "system"

@dataclass
class AuthToken:
    """Authentication token structure."""
    user_id: str
    role: AuthRole
    permissions: List[str]
    issued_at: datetime
    expires_at: datetime
    session_id: str
    agent_type: Optional[str] = None
    
class AuthMiddleware:
    """
    JWT-based authentication middleware with role management.
    
    Features:
    - JWT token generation and validation
    - Role-based access control
    - Session management
    - Token refresh mechanisms
    - AI agent identification
    """
    
    def __init__(
        self,
        secret_key: str,
        token_expiry: int = 3600,
        refresh_threshold: int = 300,
        max_sessions_per_user: int = 5
    ):
        """
        Initialize authentication middleware.
        
        Args:
            secret_key: JWT signing secret
            token_expiry: Token expiry time in seconds
            refresh_threshold: Auto-refresh threshold in seconds
            max_sessions_per_user: Maximum concurrent sessions
        """
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self.refresh_threshold = refresh_threshold
        self.max_sessions = max_sessions_per_user
        
        # Active sessions tracking
        self.active_sessions: Dict[str, AuthToken] = {}
        self.user_sessions: Dict[str, List[str]] = {}
        
        # Role permissions mapping
        self.role_permissions = {
            AuthRole.ADMIN: ["*"],  # All permissions
            AuthRole.AGENT: ["communicate", "process", "learn"],
            AuthRole.OBSERVER: ["read", "monitor"],
            AuthRole.SYSTEM: ["system", "manage", "configure"]
        }
        
    def generate_token(
        self,
        user_id: str,
        role: AuthRole,
        agent_type: Optional[str] = None,
        custom_permissions: Optional[List[str]] = None
    ) -> str:
        """
        Generate JWT authentication token.
        
        Args:
            user_id: Unique user identifier
            role: User role
            agent_type: Type of AI agent
            custom_permissions: Additional permissions
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=self.token_expiry)
        session_id = self._generate_session_id(user_id)
        
        # Get permissions based on role
        permissions = self.role_permissions.get(role, []).copy()
        if custom_permissions:
            permissions.extend(custom_permissions)
            
        # Create token data
        token_data = AuthToken(
            user_id=user_id,
            role=role,
            permissions=permissions,
            issued_at=now,
            expires_at=expires_at,
            session_id=session_id,
            agent_type=agent_type
        )
        
        # JWT payload
        payload = {
            "user_id": user_id,
            "role": role.value,
            "permissions": permissions,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "session_id": session_id,
            "agent_type": agent_type
        }
        
        # Generate JWT
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # Store session
        self._store_session(token_data)
        
        logger.info(f"Generated token for user {user_id} with role {role.value}")
        return token
        
    def validate_token(self, token: str) -> Optional[AuthToken]:
        """
        Validate JWT token and return auth data.
        
        Args:
            token: JWT token string
            
        Returns:
            AuthToken if valid, None otherwise
        """
        try:
            # Decode JWT
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Check if session exists
            session_id = payload.get("session_id")
            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not found")
                return None
                
            auth_token = self.active_sessions[session_id]
            
            # Check expiry
            if datetime.utcnow() > auth_token.expires_at:
                self._remove_session(session_id)
                logger.info(f"Token expired for session {session_id}")
                return None
                
            return auth_token
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
            
    def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh authentication token if within threshold.
        
        Args:
            token: Current JWT token
            
        Returns:
            New token if refreshed, None otherwise
        """
        auth_token = self.validate_token(token)
        if not auth_token:
            return None
            
        # Check if within refresh threshold
        time_to_expiry = (auth_token.expires_at - datetime.utcnow()).total_seconds()
        if time_to_expiry > self.refresh_threshold:
            return None
            
        # Generate new token
        new_token = self.generate_token(
            user_id=auth_token.user_id,
            role=auth_token.role,
            agent_type=auth_token.agent_type,
            custom_permissions=auth_token.permissions
        )
        
        # Remove old session
        self._remove_session(auth_token.session_id)
        
        logger.info(f"Refreshed token for user {auth_token.user_id}")
        return new_token
        
    def check_permission(self, token: str, required_permission: str) -> bool:
        """
        Check if token has required permission.
        
        Args:
            token: JWT token
            required_permission: Permission to check
            
        Returns:
            True if permission granted
        """
        auth_token = self.validate_token(token)
        if not auth_token:
            return False
            
        # Admin has all permissions
        if "*" in auth_token.permissions:
            return True
            
        return required_permission in auth_token.permissions
        
    def revoke_token(self, token: str) -> bool:
        """
        Revoke authentication token.
        
        Args:
            token: JWT token to revoke
            
        Returns:
            True if revoked successfully
        """
        auth_token = self.validate_token(token)
        if not auth_token:
            return False
            
        self._remove_session(auth_token.session_id)
        logger.info(f"Revoked token for user {auth_token.user_id}")
        return True
        
    def revoke_user_sessions(self, user_id: str) -> int:
        """
        Revoke all sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of sessions revoked
        """
        if user_id not in self.user_sessions:
            return 0
            
        sessions = self.user_sessions[user_id].copy()
        revoked_count = 0
        
        for session_id in sessions:
            if session_id in self.active_sessions:
                self._remove_session(session_id)
                revoked_count += 1
                
        logger.info(f"Revoked {revoked_count} sessions for user {user_id}")
        return revoked_count
        
    def get_active_sessions(self, user_id: Optional[str] = None) -> Dict[str, AuthToken]:
        """
        Get active sessions.
        
        Args:
            user_id: Filter by user ID
            
        Returns:
            Dictionary of active sessions
        """
        if user_id:
            user_session_ids = self.user_sessions.get(user_id, [])
            return {
                sid: token for sid, token in self.active_sessions.items()
                if sid in user_session_ids
            }
        return self.active_sessions.copy()
        
    async def middleware_handler(self, message: Dict[str, Any], next_handler: Callable) -> Dict[str, Any]:
        """
        Middleware handler for message processing.
        
        Args:
            message: Incoming message
            next_handler: Next middleware in chain
            
        Returns:
            Processed message
        """
        # Extract token from message
        token = message.get("auth_token")
        if not token:
            return {
                "error": "Authentication required",
                "code": "AUTH_REQUIRED",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        # Validate token
        auth_token = self.validate_token(token)
        if not auth_token:
            return {
                "error": "Invalid or expired token", 
                "code": "AUTH_INVALID",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        # Add auth context to message
        message["auth_context"] = {
            "user_id": auth_token.user_id,
            "role": auth_token.role.value,
            "permissions": auth_token.permissions,
            "session_id": auth_token.session_id,
            "agent_type": auth_token.agent_type
        }
        
        # Check auto-refresh
        time_to_expiry = (auth_token.expires_at - datetime.utcnow()).total_seconds()
        if time_to_expiry <= self.refresh_threshold:
            new_token = self.refresh_token(token)
            if new_token:
                message["new_auth_token"] = new_token
                
        # Continue to next handler
        return await next_handler(message)
        
    def _generate_session_id(self, user_id: str) -> str:
        """Generate unique session ID."""
        timestamp = str(int(time.time() * 1000))
        data = f"{user_id}:{timestamp}:{self.secret_key}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
        
    def _store_session(self, auth_token: AuthToken):
        """Store active session."""
        # Limit sessions per user
        if auth_token.user_id in self.user_sessions:
            user_sessions = self.user_sessions[auth_token.user_id]
            if len(user_sessions) >= self.max_sessions:
                # Remove oldest session
                oldest_session = user_sessions.pop(0)
                if oldest_session in self.active_sessions:
                    del self.active_sessions[oldest_session]
        else:
            self.user_sessions[auth_token.user_id] = []
            
        # Store session
        self.active_sessions[auth_token.session_id] = auth_token
        self.user_sessions[auth_token.user_id].append(auth_token.session_id)
        
    def _remove_session(self, session_id: str):
        """Remove session from storage."""
        if session_id in self.active_sessions:
            auth_token = self.active_sessions[session_id]
            del self.active_sessions[session_id]
            
            # Remove from user sessions
            if auth_token.user_id in self.user_sessions:
                user_sessions = self.user_sessions[auth_token.user_id]
                if session_id in user_sessions:
                    user_sessions.remove(session_id)
                    
                # Clean up empty user session list
                if not user_sessions:
                    del self.user_sessions[auth_token.user_id]
                    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        now = datetime.utcnow()
        expired_sessions = []
        
        for session_id, auth_token in self.active_sessions.items():
            if now > auth_token.expires_at:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            self._remove_session(session_id)
            
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
    async def start_cleanup_task(self, cleanup_interval: int = 300):
        """Start background cleanup task."""
        while True:
            await asyncio.sleep(cleanup_interval)
            self.cleanup_expired_sessions()
