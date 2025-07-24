"""
Enhanced Token Management System for AI-Interlinq
Adds advanced security features and performance improvements.
"""

import secrets
import time
import hashlib
import hmac
from typing import Dict, Optional, Tuple, Set, List
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import defaultdict


class TokenStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"
    SUSPENDED = "suspended"


class TokenType(Enum):
    SESSION = "session"
    REFRESH = "refresh"
    API = "api"
    TEMPORARY = "temporary"


@dataclass
class Token:
    """Enhanced token with additional security features."""
    token_id: str
    value: str
    created_at: float
    expires_at: float
    status: TokenStatus
    session_id: str
    token_type: TokenType = TokenType.SESSION
    permissions: Set[str] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)
    last_used: float = 0.0
    use_count: int = 0
    max_uses: Optional[int] = None
    origin_agent: Optional[str] = None


class TokenManager:
    """Enhanced token manager with advanced security and performance features."""
    
    def __init__(self, 
                 default_ttl: int = 3600,
                 max_tokens_per_session: int = 10,
                 enable_rate_limiting: bool = True,
                 enable_token_refresh: bool = True):
        """
        Initialize enhanced TokenManager.
        
        Args:
            default_ttl: Default token time-to-live in seconds
            max_tokens_per_session: Maximum tokens per session
            enable_rate_limiting: Enable rate limiting features
            enable_token_refresh: Enable token refresh mechanism
        """
        self.default_ttl = default_ttl
        self.max_tokens_per_session = max_tokens_per_session
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_token_refresh = enable_token_refresh
        
        # Thread-safe token storage
        self._lock = threading.RLock()
        self._tokens: Dict[str, Token] = {}
        self._session_tokens: Dict[str, List[str]] = defaultdict(list)
        self._value_to_id: Dict[str, str] = {}
        
        # Rate limiting
        self._token_usage: Dict[str, List[float]] = defaultdict(list)
        self._blocked_sessions: Set[str] = set()
        
        # Security features
        self._failed_attempts: Dict[str, int] = defaultdict(int)
        self._security_events: List[Dict] = []
        
        # Performance optimization
        self._token_cache: Dict[str, Tuple[bool, Optional[str]]] = {}
        self._cache_ttl = 60  # Cache validation results for 60 seconds
    
    def generate_token(self, 
                      session_id: str, 
                      ttl: Optional[int] = None,
                      token_type: TokenType = TokenType.SESSION,
                      permissions: Optional[Set[str]] = None,
                      max_uses: Optional[int] = None,
                      origin_agent: Optional[str] = None) -> str:
        """
        Generate a new secure token with enhanced features.
        
        Args:
            session_id: Unique session identifier
            ttl: Token time-to-live in seconds
            token_type: Type of token to generate
            permissions: Set of permissions for this token
            max_uses: Maximum number of uses (None for unlimited)
            origin_agent: Agent that requested this token
            
        Returns:
            Generated token string
        """
        with self._lock:
            # Check session limits
            if len(self._session_tokens[session_id]) >= self.max_tokens_per_session:
                # Clean up expired tokens first
                self._cleanup_session_tokens(session_id)
                
                if len(self._session_tokens[session_id]) >= self.max_tokens_per_session:
                    raise ValueError(f"Maximum tokens per session ({self.max_tokens_per_session}) exceeded")
            
            # Check if session is blocked
            if session_id in self._blocked_sessions:
                raise ValueError(f"Session {session_id} is blocked due to security violations")
            
            ttl = ttl or self.default_ttl
            
            # Generate cryptographically secure token
            token_value = self._generate_secure_token()
            token_id = secrets.token_hex(16)
            
            now = time.time()
            expires_at = now + ttl
            
            token = Token(
                token_id=token_id,
                value=token_value,
                created_at=now,
                expires_at=expires_at,
                status=TokenStatus.ACTIVE,
                session_id=session_id,
                token_type=token_type,
                permissions=permissions or set(),
                max_uses=max_uses,
                origin_agent=origin_agent,
                last_used=now
            )
            
            # Store token
            self._tokens[token_id] = token
            self._session_tokens[session_id].append(token_id)
            self._value_to_id[token_value] = token_id
            
            # Log security event
            self._log_security_event("token_generated", {
                "session_id": session_id,
                "token_id": token_id,
                "token_type": token_type.value,
                "origin_agent": origin_agent
            })
            
            return token_value
    
    def _generate_secure_token(self) -> str:
        """Generate a cryptographically secure token with additional entropy."""
        # Use multiple sources of entropy
        entropy_sources = [
            secrets.token_bytes(32),
            str(time.time_ns()).encode(),
            secrets.randbits(256).to_bytes(32, 'big')
        ]
        
        combined_entropy = b''.join(entropy_sources)
        
        # Use SHA-256 to create final token
        token_hash = hashlib.sha256(combined_entropy).digest()
        return secrets.token_urlsafe(len(token_hash))[:43]  # Standard token length
    
    def validate_token(self, 
                      token_value: str, 
                      required_permissions: Optional[Set[str]] = None,
                      origin_agent: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Enhanced token validation with permission checking.
        
        Args:
            token_value: Token to validate
            required_permissions: Required permissions for this operation
            origin_agent: Agent making the request
            
        Returns:
            Tuple of (is_valid, session_id, token_info)
        """
        # Check cache first for performance
        cache_key = f"{token_value}:{required_permissions}:{origin_agent}"
        if cache_key in self._token_cache:
            cached_result, cache_time = self._token_cache[cache_key]
            if time.time() - cache_time < self._cache_ttl:
                if cached_result[0]:  # If valid, return full info
                    return self._get_full_validation_result(token_value, required_permissions)
                return cached_result[0], cached_result[1], None
        
        with self._lock:
            token_id = self._value_to_id.get(token_value)
            if not token_id or token_id not in self._tokens:
                self._record_failed_attempt(token_value, "token_not_found")
                result = (False, None, None)
                self._token_cache[cache_key] = (result[:2], time.time())
                return result
            
            token = self._tokens[token_id]
            
            # Check token validity
            if not self._is_token_valid(token):
                self._record_failed_attempt(token_value, "token_invalid")
                result = (False, None, None)
                self._token_cache[cache_key] = (result[:2], time.time())
                return result
            
            # Check usage limits
            if token.max_uses and token.use_count >= token.max_uses:
                token.status = TokenStatus.EXPIRED
                result = (False, None, None)
                self._token_cache[cache_key] = (result[:2], time.time())
                return result
            
            # Check permissions
            if required_permissions and not required_permissions.issubset(token.permissions):
                self._record_failed_attempt(token_value, "insufficient_permissions")
                result = (False, None, None)
                self._token_cache[cache_key] = (result[:2], time.time())
                return result
            
            # Rate limiting check
            if self.enable_rate_limiting and self._is_rate_limited(token.session_id):
                self._record_failed_attempt(token_value, "rate_limited")
                result = (False, None, None)
                self._token_cache[cache_key] = (result[:2], time.time())
                return result
            
            # Update token usage
            token.last_used = time.time()
            token.use_count += 1
            
            # Record usage for rate limiting
            if self.enable_rate_limiting:
                self._token_usage[token.session_id].append(time.time())
            
            token_info = {
                "token_id": token.token_id,
                "token_type": token.token_type.value,
                "permissions": list(token.permissions),
                "use_count": token.use_count,
                "max_uses": token.max_uses,
                "last_used": token.last_used,
                "expires_at": token.expires_at
            }
            
            result = (True, token.session_id, token_info)
            self._token_cache[cache_key] = (result[:2], time.time())
            return result
    
    def _get_full_validation_result(self, token_value: str, required_permissions: Optional[Set[str]]) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Get full validation result bypassing cache."""
        token_id = self._value_to_id.get(token_value)
        if token_id and token_id in self._tokens:
            token = self._tokens[token_id]
            token_info = {
                "token_id": token.token_id,
                "token_type": token.token_type.value,
                "permissions": list(token.permissions),
                "use_count": token.use_count,
                "max_uses": token.max_uses,
                "last_used": token.last_used,
                "expires_at": token.expires_at
            }
            return True, token.session_id, token_info
        return False, None, None
    
    def refresh_token(self, old_token_value: str) -> Optional[str]:
        """
        Refresh a token with a new value and extended expiry.
        
        Args:
            old_token_value: Current token to refresh
            
        Returns:
            New token value or None if refresh failed
        """
        if not self.enable_token_refresh:
            return None
        
        with self._lock:
            token_id = self._value_to_id.get(old_token_value)
            if not token_id or token_id not in self._tokens:
                return None
            
            token = self._tokens[token_id]
            
            # Only refresh if token is still valid or recently expired
            if token.status not in [TokenStatus.ACTIVE, TokenStatus.EXPIRED]:
                return None
            
            # Generate new token value
            new_token_value = self._generate_secure_token()
            
            # Update token
            old_value = token.value
            token.value = new_token_value
            token.expires_at = time.time() + self.default_ttl
            token.status = TokenStatus.ACTIVE
            token.last_used = time.time()
            
            # Update mappings
            del self._value_to_id[old_value]
            self._value_to_id[new_token_value] = token_id
            
            # Clear cache
            self._token_cache.clear()
            
            # Log security event
            self._log_security_event("token_refreshed", {
                "session_id": token.session_id,
                "token_id": token_id,
                "old_value_hash": hashlib.sha256(old_value.encode()).hexdigest()[:16]
            })
            
            return new_token_value
    
    def _is_rate_limited(self, session_id: str) -> bool:
        """Check if a session is rate limited."""
        if not self.enable_rate_limiting:
            return False
        
        now = time.time()
        window = 60  # 1 minute window
        max_requests = 100  # Max requests per minute
        
        # Clean old entries
        usage_times = self._token_usage[session_id]
        self._token_usage[session_id] = [t for t in usage_times if now - t < window]
        
        return len(self._token_usage[session_id]) >= max_requests
    
    def _cleanup_session_tokens(self, session_id: str) -> None:
        """Clean up expired tokens for a specific session."""
        now = time.time()
        expired_tokens = []
        
        for token_id in self._session_tokens[session_id]:
            if token_id in self._tokens:
                token = self._tokens[token_id]
                if token.expires_at < now or token.status in [TokenStatus.EXPIRED, TokenStatus.REVOKED]:
                    expired_tokens.append(token_id)
        
        for token_id in expired_tokens:
            self._remove_token(token_id)
    
    def _remove_token(self, token_id: str) -> None:
        """Remove a token from all storage structures."""
        if token_id in self._tokens:
            token = self._tokens[token_id]
            
            # Remove from value mapping
            if token.value in self._value_to_id:
                del self._value_to_id[token.value]
            
            # Remove from session tokens
            if token.session_id in self._session_tokens:
                self._session_tokens[token.session_id] = [
                    tid for tid in self._session_tokens[token.session_id] 
                    if tid != token_id
                ]
            
            # Remove from main storage
            del self._tokens[token_id]
    
    def _record_failed_attempt(self, identifier: str, reason: str) -> None:
        """Record a failed authentication attempt."""
        self._failed_attempts[identifier] += 1
        
        # Block after too many failures
        if self._failed_attempts[identifier] > 5:
            # If it's a session ID, block it
            if identifier in self._session_tokens:
                self._blocked_sessions.add(identifier)
        
        self._log_security_event("authentication_failed", {
            "identifier": identifier,
            "reason": reason,
            "attempt_count": self._failed_attempts[identifier]
        })
    
    def _log_security_event(self, event_type: str, details: Dict) -> None:
        """Log a security event."""
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details
        }
        
        self._security_events.append(event)
        
        # Keep only recent events (last 1000)
        if len(self._security_events) > 1000:
            self._security_events = self._security_events[-1000:]
    
    def get_security_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get recent security events."""
        events = self._security_events
        
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        return events[-limit:]
    
    def get_session_statistics(self, session_id: str) -> Dict:
        """Get detailed statistics for a session."""
        with self._lock:
            session_tokens = [
                self._tokens[tid] for tid in self._session_tokens.get(session_id, [])
                if tid in self._tokens
            ]
            
            if not session_tokens:
                return {"session_id": session_id, "active_tokens": 0}
            
            total_uses = sum(token.use_count for token in session_tokens)
            active_tokens = sum(1 for token in session_tokens if token.status == TokenStatus.ACTIVE)
            
            return {
                "session_id": session_id,
                "total_tokens": len(session_tokens),
                "active_tokens": active_tokens,
                "total_uses": total_uses,
                "last_activity": max(token.last_used for token in session_tokens),
                "is_rate_limited": self._is_rate_limited(session_id),
                "is_blocked": session_id in self._blocked_sessions
            }
    
    def cleanup_expired_tokens(self) -> int:
        """Enhanced cleanup with better performance."""
        with self._lock:
            now = time.time()
            expired_token_ids = []
            
            # Find expired tokens
            for token_id, token in self._tokens.items():
                if (token.expires_at < now or 
                    token.status in [TokenStatus.EXPIRED, TokenStatus.REVOKED] or
                    (token.max_uses and token.use_count >= token.max_uses)):
                    expired_token_ids.append(token_id)
            
            # Remove expired tokens
            for token_id in expired_token_ids:
                self._remove_token(token_id)
            
            # Clear cache
            self._token_cache.clear()
            
            # Clean up usage tracking
            cutoff_time = now - 3600  # Keep 1 hour of usage data
            for session_id in list(self._token_usage.keys()):
                self._token_usage[session_id] = [
                    t for t in self._token_usage[session_id] 
                    if t > cutoff_time
                ]
                if not self._token_usage[session_id]:
                    del self._token_usage[session_id]
            
            return len(expired_token_ids)
    
    def _is_token_valid(self, token: Token) -> bool:
        """Enhanced token validity check."""
        now = time.time()
        return (
            token.status == TokenStatus.ACTIVE and 
            token.expires_at > now and
            (not token.max_uses or token.use_count < token.max_uses)
        )
