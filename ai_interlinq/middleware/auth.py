# ai_interlinq/middleware/auth.py
"""
Authentication Middleware for AI-Interlinq
Provides comprehensive authentication and authorization for AI agents.

File: ai_interlinq/middleware/auth.py
Directory: ai_interlinq/middleware/
"""

import asyncio
import time
import hashlib
import hmac
from typing import Dict, List, Optional, Set, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

from ..core.token_manager import TokenManager, TokenType
from ..core.communication_protocol import Message, MessageType
from ..exceptions import AuthenticationError, ValidationError
from ..utils.logging import get_logger


class AuthLevel(Enum):
    """Authentication levels."""
    NONE = 0
    BASIC = 1
    ELEVATED = 2
    ADMIN = 3


class AuthAction(Enum):
    """Authentication actions."""
    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"
    RATE_LIMIT = "rate_limit"


@dataclass
class AuthContext:
    """Authentication context for requests."""
    agent_id: str
    session_id: str
    token: Optional[str] = None
    permissions: Set[str] = field(default_factory=set)
    auth_level: AuthLevel = AuthLevel.NONE
    metadata: Dict[str, Any] = field(default_factory=dict)
    authenticated_at: float = 0.0
    last_activity: float = 0.0
    request_count: int = 0


@dataclass
class AuthRule:
    """Authentication rule definition."""
    name: str
    pattern: str  # Command pattern or regex
    required_level: AuthLevel
    required_permissions: Set[str] = field(default_factory=set)
    rate_limit: Optional[int] = None  # requests per minute
    allowed_agents: Optional[Set[str]] = None
    denied_agents: Optional[Set[str]] = None
    time_restrictions: Optional[Dict[str, Any]] = None


class AuthMiddleware:
    """Advanced authentication middleware with comprehensive security features."""
    
    def __init__(self, 
                 token_manager: TokenManager,
                 default_auth_level: AuthLevel = AuthLevel.BASIC,
                 enable_rate_limiting: bool = True,
                 enable_audit_logging: bool = True):
        """
        Initialize authentication middleware.
        
        Args:
            token_manager: Token manager instance
            default_auth_level: Default authentication level required
            enable_rate_limiting: Enable rate limiting features
            enable_audit_logging: Enable audit logging
        """
        self.token_manager = token_manager
        self.default_auth_level = default_auth_level
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_audit_logging = enable_audit_logging
        
        self.logger = get_logger("auth_middleware")
        
        # Authentication state
        self._auth_contexts: Dict[str, AuthContext] = {}
        self._auth_rules: List[AuthRule] = []
        self._trusted_agents: Set[str] = set()
        self._blocked_agents: Set[str] = set()
        
        # Rate limiting
        self._rate_limits: Dict[str, List[float]] = {}
        
        # Audit logging
        self._audit_log: List[Dict[str, Any]] = []
        
        # Setup default rules
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default authentication rules."""
        # Admin commands require admin level
        self.add_auth_rule(AuthRule(
            name="admin_commands",
            pattern="admin_.*",
            required_level=AuthLevel.ADMIN,
            required_permissions={"admin"}
        ))
        
        # System commands require elevated access
        self.add_auth_rule(AuthRule(
            name="system_commands", 
            pattern="system_.*",
            required_level=AuthLevel.ELEVATED,
            required_permissions={"system"}
        ))
        
        # High-frequency commands have rate limits
        self.add_auth_rule(AuthRule(
            name="high_frequency_commands",
            pattern="(query|search|process)_.*",
            required_level=AuthLevel.BASIC,
            rate_limit=60  # 60 requests per minute
        ))
    
    async def authenticate_message(self, message: Message) -> AuthContext:
        """
        Authenticate an incoming message.
        
        Args:
            message: Message to authenticate
            
        Returns:
            Authentication context
            
        Raises:
            AuthenticationError: If authentication fails
        """
        agent_id = message.header.sender_id
        session_id = message.header.session_id
        
        # Check if agent is blocked
        if agent_id in self._blocked_agents:
            await self._audit_log_event("auth_blocked_agent", {
                "agent_id": agent_id,
                "reason": "Agent is blocked"
            })
            raise AuthenticationError(f"Agent {agent_id} is blocked")
        
        # Get or create auth context
        context_key = f"{agent_id}:{session_id}"
        if context_key not in self._auth_contexts:
            self._auth_contexts[context_key] = AuthContext(
                agent_id=agent_id,
                session_id=session_id
            )
        
        context = self._auth_contexts[context_key]
        context.last_activity = time.time()
        context.request_count += 1
        
        # Extract token from message metadata
        token = None
        if message.payload.metadata:
            token = message.payload.metadata.get("auth_token")
        
        # Validate token if present
        if token:
            is_valid, validated_session, token_info = self.token_manager.validate_token(token)
            
            if is_valid and validated_session == session_id:
                context.token = token
                context.auth_level = self._get_auth_level_from_token(token_info)
                context.permissions = set(token_info.get("permissions", []))
                context.authenticated_at = time.time()
                
                await self._audit_log_event("auth_token_validated", {
                    "agent_id": agent_id,
                    "session_id": session_id,
                    "auth_level": context.auth_level.name
                })
            else:
                await self._audit_log_event("auth_token_invalid", {
                    "agent_id": agent_id,
                    "session_id": session_id,
                    "token_hash": hashlib.sha256(token.encode()).hexdigest()[:16]
                })
                raise AuthenticationError("Invalid or expired token")
        
        # Check if agent is trusted (bypass some checks)
        if agent_id in self._trusted_agents:
            context.auth_level = max(context.auth_level, AuthLevel.ELEVATED)
            context.permissions.add("trusted")
        
        # Apply authentication rules
        await self._apply_auth_rules(message, context)
        
        return context
    
    def _get_auth_level_from_token(self, token_info: Dict[str, Any]) -> AuthLevel:
        """Determine authentication level from token info."""
        permissions = set(token_info.get("permissions", []))
        
        if "admin" in permissions:
            return AuthLevel.ADMIN
        elif "elevated" in permissions or "system" in permissions:
            return AuthLevel.ELEVATED
        elif permissions:
            return AuthLevel.BASIC
        else:
            return AuthLevel.NONE
    
    async def _apply_auth_rules(self, message: Message, context: AuthContext):
        """Apply authentication rules to message and context."""
        import re
        
        command = message.payload.command
        
        for rule in self._auth_rules:
            # Check if rule pattern matches command
            if re.match(rule.pattern, command):
                # Check authentication level
                if context.auth_level.value < rule.required_level.value:
                    await self._audit_log_event("auth_insufficient_level", {
                        "agent_id": context.agent_id,
                        "command": command,
                        "required_level": rule.required_level.name,
                        "current_level": context.auth_level.name
                    })
                    raise AuthenticationError(
                        f"Command {command} requires {rule.required_level.name} authentication"
                    )
                
                # Check permissions
                if rule.required_permissions and not rule.required_permissions.issubset(context.permissions):
                    missing_perms = rule.required_permissions - context.permissions
                    await self._audit_log_event("auth_insufficient_permissions", {
                        "agent_id": context.agent_id,
                        "command": command,
                        "missing_permissions": list(missing_perms)
                    })
                    raise AuthenticationError(
                        f"Command {command} requires permissions: {missing_perms}"
                    )
                
                # Check agent restrictions
                if rule.allowed_agents and context.agent_id not in rule.allowed_agents:
                    raise AuthenticationError(f"Agent {context.agent_id} not allowed for command {command}")
                
                if rule.denied_agents and context.agent_id in rule.denied_agents:
                    raise AuthenticationError(f"Agent {context.agent_id} denied for command {command}")
                
                # Check rate limits
                if rule.rate_limit and self.enable_rate_limiting:
                    if not await self._check_rate_limit(context.agent_id, rule.rate_limit):
                        await self._audit_log_event("auth_rate_limited", {
                            "agent_id": context.agent_id,
                            "command": command,
                            "rate_limit": rule.rate_limit
                        })
                        raise AuthenticationError(f"Rate limit exceeded for command {command}")
                
                # Check time restrictions
                if rule.time_restrictions:
                    if not self._check_time_restrictions(rule.time_restrictions):
                        raise AuthenticationError(f"Command {command} not allowed at this time")
    
    async def _check_rate_limit(self, agent_id: str, limit: int) -> bool:
        """Check if agent is within rate limit."""
        now = time.time()
        window = 60  # 1 minute window
        
        if agent_id not in self._rate_limits:
            self._rate_limits[agent_id] = []
        
        # Clean old entries
        self._rate_limits[agent_id] = [
            timestamp for timestamp in self._rate_limits[agent_id]
            if now - timestamp < window
        ]
        
        # Check limit
        if len(self._rate_limits[agent_id]) >= limit:
            return False
        
        # Add current request
        self._rate_limits[agent_id].append(now)
        return True
    
    def _check_time_restrictions(self, restrictions: Dict[str, Any]) -> bool:
        """Check if current time is within allowed restrictions."""
        # Implementation for time-based restrictions
        # Could include business hours, maintenance windows, etc.
        return True  # Simplified for now
    
    async def authorize_action(self, 
                             context: AuthContext, 
                             action: str, 
                             resource: Optional[str] = None) -> bool:
        """
        Authorize a specific action for an authenticated context.
        
        Args:
            context: Authentication context
            action: Action to authorize
            resource: Optional resource being accessed
            
        Returns:
            True if authorized, False otherwise
        """
        # Check basic authentication
        if context.auth_level == AuthLevel.NONE:
            return False
        
        # Admin can do everything
        if context.auth_level == AuthLevel.ADMIN:
            return True
        
        # Check specific permissions
        permission_required = f"{action}:{resource}" if resource else action
        
        if permission_required in context.permissions:
            return True
        
        # Check wildcard permissions
        wildcard_permission = f"{action}:*"
        if wildcard_permission in context.permissions:
            return True
        
        await self._audit_log_event("auth_action_denied", {
            "agent_id": context.agent_id,
            "action": action,
            "resource": resource,
            "permissions": list(context.permissions)
        })
        
        return False
    
    def add_auth_rule(self, rule: AuthRule):
        """Add an authentication rule."""
        self._auth_rules.append(rule)
        self.logger.info(f"Added auth rule: {rule.name}")
    
    def remove_auth_rule(self, rule_name: str) -> bool:
        """Remove an authentication rule by name."""
        original_len = len(self._auth_rules)
        self._auth_rules = [rule for rule in self._auth_rules if rule.name != rule_name]
        
        if len(self._auth_rules) < original_len:
            self.logger.info(f"Removed auth rule: {rule_name}")
            return True
        return False
    
    def add_trusted_agent(self, agent_id: str):
        """Add an agent to the trusted list."""
        self._trusted_agents.add(agent_id)
        self.logger.info(f"Added trusted agent: {agent_id}")
    
    def remove_trusted_agent(self, agent_id: str):
        """Remove an agent from the trusted list."""
        self._trusted_agents.discard(agent_id)
        self.logger.info(f"Removed trusted agent: {agent_id}")
    
    def block_agent(self, agent_id: str, reason: str = "Manual block"):
        """Block an agent from authentication."""
        self._blocked_agents.add(agent_id)
        asyncio.create_task(self._audit_log_event("agent_blocked", {
            "agent_id": agent_id,
            "reason": reason
        }))
        self.logger.warning(f"Blocked agent {agent_id}: {reason}")
    
    def unblock_agent(self, agent_id: str):
        """Unblock a previously blocked agent."""
        self._blocked_agents.discard(agent_id)
        asyncio.create_task(self._audit_log_event("agent_unblocked", {
            "agent_id": agent_id
        }))
        self.logger.info(f"Unblocked agent: {agent_id}")
    
    def get_auth_context(self, agent_id: str, session_id: str) -> Optional[AuthContext]:
        """Get authentication context for agent/session."""
        context_key = f"{agent_id}:{session_id}"
        return self._auth_contexts.get(context_key)
    
    def cleanup_expired_contexts(self, max_age: int = 3600) -> int:
        """Clean up expired authentication contexts."""
        now = time.time()
        expired_keys = []
        
        for key, context in self._auth_contexts.items():
            if now - context.last_activity > max_age:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._auth_contexts[key]
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired auth contexts")
        
        return len(expired_keys)
    
    async def _audit_log_event(self, event_type: str, details: Dict[str, Any]):
        """Log an audit event."""
        if not self.enable_audit_logging:
            return
        
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details
        }
        
        self._audit_log.append(event)
        
        # Keep only recent events (last 10000)
        if len(self._audit_log) > 10000:
            self._audit_log = self._audit_log[-10000:]
        
        # Log to system logger for external monitoring
        self.logger.info(f"AUTH_AUDIT: {event_type} - {details}")
    
    def get_audit_log(self, 
                     event_type: Optional[str] = None, 
                     agent_id: Optional[str] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit log entries with optional filtering."""
        events = self._audit_log
        
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        if agent_id:
            events = [e for e in events if e["details"].get("agent_id") == agent_id]
        
        return events[-limit:]
    
    def get_auth_statistics(self) -> Dict[str, Any]:
        """Get authentication statistics."""
        now = time.time()
        active_contexts = sum(
            1 for context in self._auth_contexts.values()
            if now - context.last_activity < 300  # Active in last 5 minutes
        )
        
        return {
            "total_contexts": len(self._auth_contexts),
            "active_contexts": active_contexts,
            "auth_rules": len(self._auth_rules),
            "trusted_agents": len(self._trusted_agents),
            "blocked_agents": len(self._blocked_agents),
            "audit_events": len(self._audit_log),
            "rate_limited_agents": len(self._rate_limits)
        }
