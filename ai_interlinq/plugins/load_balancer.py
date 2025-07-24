# ai_interlinq/plugins/load_balancer.py
"""Load balancing plugin for AI-Interlinq."""

import random
import time
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass

from ..utils.logging import get_logger


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_RANDOM = "weighted_random"
    HEALTH_BASED = "health_based"


@dataclass
class BackendAgent:
    """Information about a backend agent."""
    agent_id: str
    address: str
    weight: float = 1.0
    active_connections: int = 0
    last_response_time: float = 0.0
    health_score: float = 1.0
    is_healthy: bool = True


class LoadBalancer:
    """Load balancer for distributing messages across multiple AI agents."""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.logger = get_logger("load_balancer")
        
        # Backend management
        self._backends: Dict[str, BackendAgent] = {}
        self._round_robin_index = 0
        
        # Health checking
        self._health_check_interval = 30.0
        self._unhealthy_threshold = 3
    
    def add_backend(
        self, 
        agent_id: str, 
        address: str, 
        weight: float = 1.0
    ) -> None:
        """Add a backend agent."""
        backend = BackendAgent(
            agent_id=agent_id,
            address=address,
            weight=weight
        )
        
        self._backends[agent_id] = backend
        self.logger.info(f"Added backend {agent_id} at {address} with weight {weight}")
    
    def remove_backend(self, agent_id: str) -> bool:
        """Remove a backend agent."""
        if agent_id in self._backends:
            del self._backends[agent_id]
            self.logger.info(f"Removed backend {agent_id}")
            return True
        return False
    
    def select_backend(self, exclude: Optional[List[str]] = None) -> Optional[BackendAgent]:
        """Select a backend agent based on the load balancing strategy."""
        exclude = exclude or []
        available_backends = [
            backend for backend in self._backends.values()
            if backend.is_healthy and backend.agent_id not in exclude
        ]
        
        if not available_backends:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(available_backends)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return random.choice(available_backends)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return min(available_backends, key=lambda b: b.active_connections)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_RANDOM:
            return self._weighted_random_select(available_backends)
        elif self.strategy == LoadBalancingStrategy.HEALTH_BASED:
            return self._health_based_select(available_backends)
        
        return available_backends[0]
    
    def _round_robin_select(self, backends: List[BackendAgent]) -> BackendAgent:
        """Round-robin selection."""
        if not backends:
            raise ValueError("No backends available")
        
        backend = backends[self._round_robin_index % len(backends)]
        self._round_robin_index = (self._round_robin_index + 1) % len(backends)
        return backend
    
    def _weighted_random_select(self, backends: List[BackendAgent]) -> BackendAgent:
        """Weighted random selection."""
        weights = [backend.weight for backend in backends]
        return random.choices(backends, weights=weights)[0]
    
    def _health_based_select(self, backends: List[BackendAgent]) -> BackendAgent:
        """Health-based selection (higher health score = higher probability)."""
        weights = [backend.health_score for backend in backends]
        return random.choices(backends, weights=weights)[0]
    
    def update_backend_stats(
        self, 
        agent_id: str, 
        response_time: float, 
        success: bool
    ) -> None:
        """Update backend statistics."""
        if agent_id not in self._backends:
            return
        
        backend = self._backends[agent_id]
        backend.last_response_time = response_time
        
        # Update health score based on success/failure
        if success:
            backend.health_score = min(1.0, backend.health_score + 0.1)
        else:
            backend.health_score = max(0.0, backend.health_score - 0.2)
        
        # Mark as unhealthy if health score is too low
        backend.is_healthy = backend.health_score > 0.3
    
    def increment_connections(self, agent_id: str) -> None:
        """Increment active connection count."""
        if agent_id in self._backends:
            self._backends[agent_id].active_connections += 1
    
    def decrement_connections(self, agent_id: str) -> None:
        """Decrement active connection count."""
        if agent_id in self._backends:
            backend = self._backends[agent_id]
            backend.active_connections = max(0, backend.active_connections - 1)
    
    def get_backend_stats(self) -> Dict[str, Dict]:
        """Get statistics for all backends."""
        return {
            agent_id: {
                "address": backend.address,
                "weight": backend.weight,
                "active_connections": backend.active_connections,
                "last_response_time": backend.last_response_time,
                "health_score": backend.health_score,
                "is_healthy": backend.is_healthy
            }
            for agent_id, backend in self._backends.items()
        }
    
    def get_healthy_backends(self) -> List[str]:
        """Get list of healthy backend IDs."""
        return [
            agent_id for agent_id, backend in self._backends.items()
            if backend.is_healthy
        ]
