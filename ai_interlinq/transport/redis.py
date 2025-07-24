# ai_interlinq/transport/redis.py
"""Redis pub/sub transport implementation."""

import asyncio
import json
import aioredis
from typing import Optional

from .base import BaseTransport, TransportConfig, TransportError
from ..utils.logging import get_logger


class RedisConfig(TransportConfig):
    """Redis-specific configuration."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    channel_prefix: str = "ai_interlinq"


class RedisTransport(BaseTransport):
    """Redis pub/sub based transport implementation."""
    
    def __init__(self, config: RedisConfig):
        super().__init__(config)
        self.config: RedisConfig = config
        self.logger = get_logger("redis_transport")
        self._redis: Optional[aioredis.Redis] = None
        self._pubsub: Optional[aioredis.client.PubSub] = None
        self._agent_id: Optional[str] = None
    
    def set_agent_id(self, agent_id: str):
        """Set the agent ID for this transport."""
        self._agent_id = agent_id
    
    async def start_server(self) -> None:
        """Start Redis connection and subscribe to channels."""
        try:
            # Connect to Redis
            self._redis = aioredis.from_url(
                f"redis://{self.config.host}:{self.config.port}/{self.config.db}",
                password=self.config.password,
                decode_responses=True
            )
            
            # Create pubsub instance
            self._pubsub = self._redis.pubsub()
            
            if self._agent_id:
                # Subscribe to agent-specific channel
                channel = f"{self.config.channel_prefix}:{self._agent_id}"
                await self._pubsub.subscribe(channel)
                self.logger.info(f"Subscribed to Redis channel: {channel}")
            
            # Subscribe to broadcast channel
            broadcast_channel = f"{self.config.channel_prefix}:broadcast"
            await self._pubsub.subscribe(broadcast_channel)
            
            self._is_running = True
            self.logger.info("Redis transport started")
            
            # Start message listener
            await self._listen_for_messages()
            
        except Exception as e:
            self.logger.error(f"Failed to start Redis transport: {e}")
            raise TransportError(f"Redis transport start failed: {e}")
    
    async def stop_server(self) -> None:
        """Stop Redis transport."""
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
        
        if self._redis:
            await self._redis.close()
        
        self._is_running = False
        self.logger.info("Redis transport stopped")
    
    async def _listen_for_messages(self):
        """Listen for incoming Redis messages."""
        async for message in self._pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    sender = data.get('sender', 'unknown')
                    content = data.get('content', '')
                    
                    await self.handle_incoming_message(content, sender)
                    
                except Exception as e:
                    self.logger.error(f"Error processing Redis message: {e}")
    
    async def send_message(self, target: str, message: str) -> bool:
        """Send message via Redis pub/sub."""
        try:
            if not self._redis:
                return False
            
            channel = f"{self.config.channel_prefix}:{target}"
            data = {
                'sender': self._agent_id or 'unknown',
                'content': message,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            await self._redis.publish(channel, json.dumps(data))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Redis message to {target}: {e}")
            return False
    
    async def connect_to_peer(self, target: str) -> bool:
        """Connect to peer (Redis doesn't require explicit connections)."""
        # Redis pub/sub doesn't require explicit peer connections
        return True
    
    async def disconnect_from_peer(self, target: str) -> bool:
        """Disconnect from peer."""
        # Redis pub/sub doesn't maintain peer connections
        return True
