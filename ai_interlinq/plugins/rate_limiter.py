# ai_interlinq/plugins/rate_limiter.py
"""Rate limiting plugin for AI-Interlinq."""

import asyncio
import time
from typing import Dict, Optional
from dataclasses import dataclass
from collections import deque

from ..utils.logging import get_logger


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_second: float = 10.0
    burst_size: int = 20
    window_size: int = 60  # seconds


class TokenBucket:
    """Token bucket for rate limiting."""
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket."""
        now = time.time()
        
        # Add tokens based on elapsed time
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
        
        # Check if we have enough tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def time_until_available(self, tokens: int = 1) -> float:
        """Time until specified tokens will be available."""
        if self.tokens >= tokens:
            return 0.0
        
        needed_tokens = tokens - self.tokens
        return needed_tokens / self.rate


class SlidingWindow:
    """Sliding window rate limiter."""
    
    def __init__(self, limit: int, window_size: int):
        self.limit = limit
        self.window_size = window_size
        self.requests = deque()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed."""
        now = time.time()
        
        # Remove old requests outside the window
        while self.requests and self.requests[0] <= now - self.window_size:
            self.requests.popleft()
        
        # Check if we're under the limit
        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True
        
        return False
    
    def time_until_available(self) -> float:
        """Time until next request is allowed."""
        if len(self.requests) < self.limit:
            return 0.0
        
        oldest_request = self.requests[0]
        return oldest_request + self.window_size - time.time()


class RateLimiter:
    """Rate limiter for AI-Interlinq messages."""
    
    def __init__(self):
        self.logger = get_logger("rate_limiter")
        
        # Per-agent rate limiters
        self._agent_limiters: Dict[str, TokenBucket] = {}
        self._agent_configs: Dict[str, RateLimitConfig] = {}
        
        # Global rate limiter
        self._global_limiter: Optional[TokenBucket] = None
        self._global_config: Optional[RateLimitConfig] = None
        
        # Sliding window limiters for burst protection
        self._sliding_windows: Dict[str, SlidingWindow] = {}
    
    def set_global_rate_limit(self, config: RateLimitConfig) -> None:
        """Set global rate limit."""
        self._global_config = config
        self._global_limiter = TokenBucket(
            rate=config.requests_per_second,
            capacity=config.burst_size
        )
        self.logger.info(f"Set global rate limit: {config.requests_per_second} req/s")
    
    def set_agent_rate_limit(self, agent_id: str, config: RateLimitConfig) -> None:
        """Set rate limit for specific agent."""
        self._agent_configs[agent_id] = config
        self._agent_limiters[agent_id] = TokenBucket(
            rate=config.requests_per_second,
            capacity=config.burst_size
        )
        
        # Set up sliding window for burst protection
        self._sliding_windows[agent_id] = SlidingWindow(
            limit=int(config.requests_per_second * config.window_size),
            window_size=config.window_size
        )
        
        self.logger.info(f"Set rate limit for {agent_id}: {config.requests_per_second} req/s")
    
    async def check_rate_limit(self, agent_id: str, tokens: int = 1) -> bool:
        """Check if request is within rate limits."""
        # Check global rate limit first
        if self._global_limiter and not self._global_limiter.consume(tokens):
            self.logger.warning(f"Global rate limit exceeded for {agent_id}")
            return False
        
        # Check agent-specific rate limit
        if agent_id in self._agent_limiters:
            limiter = self._agent_limiters[agent_id]
            if not limiter.consume(tokens):
                self.logger.warning(f"Rate limit exceeded for agent {agent_id}")
                return False
            
            # Check sliding window for burst protection
            if agent_id in self._sliding_windows:
                window = self._sliding_windows[agent_id]
                if not window.is_allowed():
                    self.logger.warning(f"Burst limit exceeded for agent {agent_id}")
                    return False
        
        return True
    
    async def wait_for_availability(self, agent_id: str, tokens: int = 1) -> float:
        """Wait until request is allowed and return wait time."""
        wait_time = 0.0
        
        # Check global limiter
        if self._global_limiter:
            global_wait = self._global_limiter.time_until_available(tokens)
            wait_time = max(wait_time, global_wait)
        
        # Check agent limiter
        if agent_id in self._agent_limiters:
            limiter = self._agent_limiters[agent_id]
            agent_wait = limiter.time_until_available(tokens)
            wait_time = max(wait_time, agent_wait)
            
            # Check sliding window
            if agent_id in self._sliding_windows:
                window = self._sliding_windows[agent_id]
                window_wait = window.time_until_available()
                wait_time = max(wait_time, window_wait)
        
        if wait_time > 0:
            self.logger.debug(f"Waiting {wait_time:.2f}s for rate limit availability")
            await asyncio.sleep(wait_time)
        
        return wait_time
    
    def get_rate_limit_status(self, agent_id: str) -> Dict[str, float]:
        """Get current rate limit status for an agent."""
        status = {}
        
        if self._global_limiter:
            status["global_tokens"] = self._global_limiter.tokens
            status["global_capacity"] = self._global_limiter.capacity
        
        if agent_id in self._agent_limiters:
            limiter = self._agent_limiters[agent_id]
            status["agent_tokens"] = limiter.tokens
            status["agent_capacity"] = limiter.capacity
            
            if agent_id in self._sliding_windows:
                window = self._sliding_windows[agent_id]
                status["window_requests"] = len(window.requests)
                status["window_limit"] = window.limit
        
        return status
    
    def reset_agent_limits(self, agent_id: str) -> None:
        """Reset rate limits for an agent."""
        if agent_id in self._agent_limiters:
            config = self._agent_configs[agent_id]
            self._agent_limiters[agent_id] = TokenBucket(
                rate=config.requests_per_second,
                capacity=config.burst_size
            )
            
            self._sliding_windows[agent_id] = SlidingWindow(
                limit=int(config.requests_per_second * config.window_size),
                window_size=config.window_size
            )
            
            self.logger.info(f"Reset rate limits for agent {agent_id}")
    
    def remove_agent_limits(self, agent_id: str) -> None:
        """Remove rate limits for an agent."""
        self._agent_limiters.pop(agent_id, None)
        self._agent_configs.pop(agent_id, None)
        self._sliding_windows.pop(agent_id, None)
        
        self.logger.info(f"Removed rate limits for agent {agent_id}")
