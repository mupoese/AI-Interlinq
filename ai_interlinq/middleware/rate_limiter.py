# File: /ai_interlinq/middleware/rate_limiter.py
# Directory: /ai_interlinq/middleware

"""
Rate limiter middleware for AI-Interlinq framework.
Provides token bucket rate limiting with burst support and adaptive throttling.
"""

import time
import asyncio
import threading
from typing import Dict, Any, Optional, Callable, Union, List
from dataclasses import dataclass
from collections import defaultdict, deque
from datetime import datetime, timedelta
from enum import Enum
import logging
import hashlib

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"

@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""
    max_requests: int
    time_window: int  # seconds
    burst_size: Optional[int] = None
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    
@dataclass
class RateLimitResult:
    """Result of rate limiting check."""
    allowed: bool
    remaining_requests: int
    reset_time: datetime
    retry_after: Optional[int] = None
    
class TokenBucket:
    """Token bucket implementation for rate limiting."""
    
    def __init__(self, max_tokens: int, refill_rate: float, burst_size: Optional[int] = None):
        """
        Initialize token bucket.
        
        Args:
            max_tokens: Maximum tokens in bucket
            refill_rate: Tokens added per second
            burst_size: Maximum burst size (defaults to max_tokens)
        """
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.burst_size = burst_size or max_tokens
        self.tokens = float(max_tokens)
        self.last_refill = time.time()
        self.lock = threading.Lock()
        
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed successfully
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
            
    def get_available_tokens(self) -> int:
        """Get number of available tokens."""
        with self.lock:
            self._refill()
            return int(self.tokens)
            
    def time_until_tokens(self, required_tokens: int) -> float:
        """Calculate time until required tokens are available."""
        with self.lock:
            self._refill()
            
            if self.tokens >= required_tokens:
                return 0.0
                
            tokens_needed = required_tokens - self.tokens
            return tokens_needed / self.refill_rate
            
    def _refill(self):
        """Refill bucket based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        if elapsed > 0:
            tokens_to_add = elapsed * self.refill_rate
            self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
            self.last_refill = now

class SlidingWindowLimiter:
    """Sliding window rate limiter."""
    
    def __init__(self, max_requests: int, window_size: int):
        """
        Initialize sliding window limiter.
        
        Args:
            max_requests: Maximum requests in window
            window_size: Window size in seconds
        """
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = deque()
        self.lock = threading.Lock()
        
    def is_allowed(self) -> bool:
        """Check if request is allowed."""
        with self.lock:
            now = time.time()
            window_start = now - self.window_size
            
            # Remove old requests
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
                
            # Check if under limit
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
                
            return False
            
    def get_remaining_requests(self) -> int:
        """Get remaining requests in current window."""
        with self.lock:
            now = time.time()
            window_start = now - self.window_size
            
            # Remove old requests
            while self.requests and self.requests[0] < window_start:
                self.requests.popleft()
                
            return max(0, self.max_requests - len(self.requests))

class RateLimiterMiddleware:
    """
    Advanced rate limiting middleware with multiple strategies.
    
    Features:
    - Multiple rate limiting strategies
    - Per-user and global rate limits
    - Burst handling
    - Adaptive throttling
    - Detailed metrics and monitoring
    """
    
    def __init__(
        self,
        global_rule: Optional[RateLimitRule] = None,
        user_rules: Optional[Dict[str, RateLimitRule]] = None,
        default_user_rule: Optional[RateLimitRule] = None,
        enable_adaptive: bool = False
    ):
        """
        Initialize rate limiter middleware.
        
        Args:
            global_rule: Global rate limiting rule
            user_rules: Per-user rate limiting rules
            default_user_rule: Default rule for users without specific rules
            enable_adaptive: Enable adaptive rate limiting
        """
        self.global_rule = global_rule
        self.user_rules = user_rules or {}
        self.default_user_rule = default_user_rule or RateLimitRule(
            max_requests=100,
            time_window=60,
            burst_size=10
        )
        self.enable_adaptive = enable_adaptive
        
        # Rate limiters storage
        self.global_limiter = None
        self.user_limiters: Dict[str, Union[TokenBucket, SlidingWindowLimiter]] = {}
        
        # Initialize global limiter
        if self.global_rule:
            self.global_limiter = self._create_limiter(self.global_rule)
            
        # Adaptive throttling state
        self.adaptive_state = {
            "error_rate": 0.0,
            "avg_response_time": 0.0,
            "throttle_factor": 1.0,
            "last_adjustment": time.time()
        }
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "adaptive_adjustments": 0
        }
        
        # Request history for adaptive limiting
        self.request_history = deque(maxlen=1000)
        self.lock = threading.RLock()
        
    def check_rate_limit(
        self,
        user_id: Optional[str] = None,
        request_weight: int = 1
    ) -> RateLimitResult:
        """
        Check if request is within rate limits.
        
        Args:
            user_id: User identifier for per-user limits
            request_weight: Weight of the request (default 1)
            
        Returns:
            RateLimitResult with limit check details
        """
        with self.lock:
            now = datetime.utcnow()
            self.metrics["total_requests"] += 1
            
            # Check global rate limit first
            if self.global_limiter and not self._check_limiter(self.global_limiter, request_weight):
                self.metrics["blocked_requests"] += 1
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=now + timedelta(seconds=60),
                    retry_after=60
                )
                
            # Check user-specific rate limit
            if user_id:
                user_limiter = self._get_user_limiter(user_id)
                if not self._check_limiter(user_limiter, request_weight):
                    self.metrics["blocked_requests"] += 1
                    return RateLimitResult(
                        allowed=False,
                        remaining_requests=0,
                        reset_time=now + timedelta(seconds=60),
                        retry_after=60
                    )
                    
            # Apply adaptive throttling
            if self.enable_adaptive:
                throttle_factor = self._get_adaptive_throttle_factor()
                if throttle_factor < 1.0:
                    # Probabilistic throttling
                    import random
                    if random.random() > throttle_factor:
                        self.metrics["blocked_requests"] += 1
                        return RateLimitResult(
                            allowed=False,
                            remaining_requests=0,
                            reset_time=now + timedelta(seconds=30),
                            retry_after=30
                        )
                        
            # Request allowed
            self.metrics["allowed_requests"] += 1
            self.request_history.append({
                "timestamp": time.time(),
                "user_id": user_id,
                "weight": request_weight
            })
            
            return RateLimitResult(
                allowed=True,
                remaining_requests=self._get_remaining_requests(user_id),
                reset_time=now + timedelta(seconds=60)
            )
            
    async def middleware_handler(
        self,
        message: Dict[str, Any],
        next_handler: Callable
    ) -> Dict[str, Any]:
        """
        Middleware handler for rate limiting.
        
        Args:
            message: Message to process
            next_handler: Next middleware in chain
            
        Returns:
            Processed message or rate limit error
        """
        # Extract user information
        user_id = None
        if "auth_context" in message:
            user_id = message["auth_context"].get("user_id")
        elif "user_id" in message:
            user_id = message["user_id"]
            
        # Determine request weight
        request_weight = message.get("weight", 1)
        message_size = len(str(message))
        if message_size > 10000:  # Large messages get higher weight
            request_weight *= 2
            
        # Check rate limits
        limit_result = self.check_rate_limit(user_id, request_weight)
        
        if not limit_result.allowed:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return {
                "error": "Rate limit exceeded",
                "code": "RATE_LIMIT_EXCEEDED",
                "remaining_requests": limit_result.remaining_requests,
                "reset_time": limit_result.reset_time.isoformat(),
                "retry_after": limit_result.retry_after,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        # Process request
        start_time = time.time()
        try:
            response = await next_handler(message)
            processing_time = time.time() - start_time
            
            # Update adaptive state on success
            if self.enable_adaptive:
                self._update_adaptive_state(processing_time, success=True)
                
            # Add rate limit headers to response
            if isinstance(response, dict):
                response["rate_limit"] = {
                    "remaining": limit_result.remaining_requests,
                    "reset_time": limit_result.reset_time.isoformat()
                }
                
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Update adaptive state on error
            if self.enable_adaptive:
                self._update_adaptive_state(processing_time, success=False)
                
            # Re-raise exception
            raise
            
    def add_user_rule(self, user_id: str, rule: RateLimitRule):
        """Add or update user-specific rate limiting rule."""
        with self.lock:
            self.user_rules[user_id] = rule
            # Remove existing limiter to force recreation with new rule
            if user_id in self.user_limiters:
                del self.user_limiters[user_id]
                
    def remove_user_rule(self, user_id: str):
        """Remove user-specific rate limiting rule."""
        with self.lock:
            if user_id in self.user_rules:
                del self.user_rules[user_id]
            if user_id in self.user_limiters:
                del self.user_limiters[user_id]
                
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get rate limiting statistics for a user."""
        user_requests = [
            req for req in self.request_history
            if req.get("user_id") == user_id
        ]
        
        recent_requests = [
            req for req in user_requests
            if time.time() - req["timestamp"] < 300  # Last 5 minutes
        ]
        
        return {
            "user_id": user_id,
            "total_requests": len(user_requests),
            "recent_requests": len(recent_requests),
            "remaining_requests": self._get_remaining_requests(user_id),
            "has_custom_rule": user_id in self.user_rules
        }
        
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global rate limiting statistics."""
        recent_requests = [
            req for req in self.request_history
            if time.time() - req["timestamp"] < 300  # Last 5 minutes
        ]
        
        stats = self.metrics.copy()
        stats.update({
            "recent_requests": len(recent_requests),
            "adaptive_state": self.adaptive_state.copy(),
            "active_users": len(set(req.get("user_id") for req in recent_requests if req.get("user_id")))
        })
        
        return stats
        
    def _create_limiter(
        self,
        rule: RateLimitRule
    ) -> Union[TokenBucket, SlidingWindowLimiter]:
        """Create rate limiter based on strategy."""
        if rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return TokenBucket(
                max_tokens=rule.max_requests,
                refill_rate=rule.max_requests / rule.time_window,
                burst_size=rule.burst_size
            )
        elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return SlidingWindowLimiter(
                max_requests=rule.max_requests,
                window_size=rule.time_window
            )
        else:
            # Default to token bucket
            return TokenBucket(
                max_tokens=rule.max_requests,
                refill_rate=rule.max_requests / rule.time_window,
                burst_size=rule.burst_size
            )
            
    def _get_user_limiter(
        self,
        user_id: str
    ) -> Union[TokenBucket, SlidingWindowLimiter]:
        """Get or create user-specific rate limiter."""
        if user_id not in self.user_limiters:
            rule = self.user_rules.get(user_id, self.default_user_rule)
            self.user_limiters[user_id] = self._create_limiter(rule)
            
        return self.user_limiters[user_id]
        
    def _check_limiter(
        self,
        limiter: Union[TokenBucket, SlidingWindowLimiter],
        weight: int
    ) -> bool:
        """Check if request is allowed by limiter."""
        if isinstance(limiter, TokenBucket):
            return limiter.consume(weight)
        elif isinstance(limiter, SlidingWindowLimiter):
            # For sliding window, ignore weight and just check if allowed
            return limiter.is_allowed()
        return False
        
    def _get_remaining_requests(self, user_id: Optional[str]) -> int:
        """Get remaining requests for user."""
        if user_id:
            limiter = self._get_user_limiter(user_id)
            if isinstance(limiter, TokenBucket):
                return limiter.get_available_tokens()
            elif isinstance(limiter, SlidingWindowLimiter):
                return limiter.get_remaining_requests()
                
        if self.global_limiter:
            if isinstance(self.global_limiter, TokenBucket):
                return self.global_limiter.get_available_tokens()
            elif isinstance(self.global_limiter, SlidingWindowLimiter):
                return self.global_limiter.get_remaining_requests()
                
        return 100  # Default fallback
        
    def _get_adaptive_throttle_factor(self) -> float:
        """Calculate adaptive throttling factor."""
        state = self.adaptive_state
        
        # Base throttle factor
        throttle_factor = state["throttle_factor"]
        
        # Adjust based on error rate
        if state["error_rate"] > 0.1:  # > 10% error rate
            throttle_factor *= 0.8
        elif state["error_rate"] < 0.01:  # < 1% error rate
            throttle_factor = min(1.0, throttle_factor * 1.1)
            
        # Adjust based on response time
        if state["avg_response_time"] > 2.0:  # > 2 seconds
            throttle_factor *= 0.9
        elif state["avg_response_time"] < 0.5:  # < 0.5 seconds
            throttle_factor = min(1.0, throttle_factor * 1.05)
            
        # Update state
        state["throttle_factor"] = max(0.1, min(1.0, throttle_factor))
        
        return state["throttle_factor"]
        
    def _update_adaptive_state(self, processing_time: float, success: bool):
        """Update adaptive throttling state."""
        state = self.adaptive_state
        now = time.time()
        
        # Update response time (exponential moving average)
        alpha = 0.1
        state["avg_response_time"] = (
            alpha * processing_time + 
            (1 - alpha) * state["avg_response_time"]
        )
        
        # Update error rate
        if success:
            state["error_rate"] = (1 - alpha) * state["error_rate"]
        else:
            state["error_rate"] = alpha + (1 - alpha) * state["error_rate"]
            
        # Adjust throttle factor periodically
        if now - state["last_adjustment"] > 30:  # Every 30 seconds
            old_factor = state["throttle_factor"]
            new_factor = self._get_adaptive_throttle_factor()
            
            if abs(new_factor - old_factor) > 0.05:
                self.metrics["adaptive_adjustments"] += 1
                logger.info(f"Adaptive throttle factor adjusted: {old_factor:.2f} -> {new_factor:.2f}")
                
            state["last_adjustment"] = now
