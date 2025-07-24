# File: /ai_interlinq/adapters/grok.py
# Directory: /ai_interlinq/adapters

"""
xAI Grok adapter for AI-Interlinq framework.
Provides integration with Grok models with real-time capabilities.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from dataclasses import dataclass
import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class GrokMessage:
    """Grok message structure."""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: Optional[str] = None

@dataclass
class GrokResponse:
    """Grok API response structure."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    system_fingerprint: Optional[str] = None

class GrokAdapter:
    """
    xAI Grok integration adapter.
    
    Features:
    - Grok-1 and Grok-1.5 models
    - Real-time information access
    - Witty and humorous responses
    - Function calling support
    - Streaming responses
    - Context-aware conversations
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "grok-beta",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        base_url: str = "https://api.x.ai/v1",
        timeout: int = 60
    ):
        """
        Initialize Grok adapter.
        
        Args:
            api_key: xAI API key
            model: Grok model to use
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0.0-2.0)
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Available models with capabilities
        self.available_models = {
            "grok-beta": {
                "max_tokens": 4096,
                "context_window": 131072,  # 131K tokens
                "real_time": True,
                "function_calling": True,
                "humor": True,
                "knowledge_cutoff": "real-time"
            },
            "grok-vision-beta": {
                "max_tokens": 4096,
                "context_window": 131072,
                "real_time": True,
                "function_calling": True,
                "vision": True,
                "humor": True,
                "knowledge_cutoff": "real-time"
            }
        }
        
        # HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        # Conversation history
        self.conversations: Dict[str, List[GrokMessage]] = {}
        
        # Real-time context
        self.real_time_enabled = True
        self.context_sources = ["web", "news", "social"]
        
        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens_prompt": 0,
            "total_tokens_completion": 0,
            "real_time_queries": 0,
            "function_calls": 0,
            "errors": 0
        }
        
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        enable_real_time: bool = True,
        functions: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[GrokResponse, AsyncGenerator[Dict[str, Any], None]]:
        """
        Send message to Grok.
        
        Args:
            message: User message
            conversation_id: Conversation identifier for context
            system_prompt: System prompt for behavior
            enable_real_time: Enable real-time information access
            functions: Available functions
            stream: Enable streaming response
            **kwargs: Additional parameters
            
        Returns:
            Grok response or streaming generator
        """
        try:
            # Prepare messages
            messages = self._prepare_messages(message, conversation_id, system_prompt)
            
            # Build request payload
            payload = {
                "model": self.model,
                "messages": [self._message_to_dict(msg) for msg in messages],
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "stream": stream
            }
            
            # Add real-time context if enabled
            if enable_real_time and self.real_time_enabled:
                payload["real_time"] = True
                payload["context_sources"] = self.context_sources
                self.usage_stats["real_time_queries"] += 1
                
            # Add functions if provided
            if functions:
                payload["functions"] = functions
                payload["function_call"] = kwargs.get("function_call", "auto")
                
            # Additional parameters
            for param in ["top_p", "frequency_penalty", "presence_penalty", "stop"]:
                if param in kwargs:
                    payload[param] = kwargs[param]
                    
            if stream:
                return self._stream_response(payload, conversation_id)
            else:
                return await self._send_request(payload, conversation_id)
                
        except Exception as e:
            logger.error(f"Grok message send failed: {e}")
            self.usage_stats["errors"] += 1
            raise
            
    async def ask_with_humor(
        self,
        question: str,
        humor_level: str = "medium",
        conversation_id: Optional[str] = None
    ) -> GrokResponse:
        """
        Ask question with Grok's characteristic humor.
        
        Args:
            question: Question to ask
            humor_level: Level of humor ("low", "medium", "high", "maximum")
            conversation_id: Conversation identifier
            
        Returns:
            Humorous Grok response
        """
        humor_prompts = {
            "low": "Respond with subtle wit and mild humor.",
            "medium": "Respond with your characteristic wit and humor, but keep it appropriate.",
            "high": "Respond with maximum wit, humor, and sarcasm while being helpful.",
            "maximum": "Go full Grok mode - maximum wit, humor, and playful sarcasm while still being accurate."
        }
        
        system_prompt = f"""You are Grok, xAI's witty and humorous AI assistant. {humor_prompts.get(humor_level, humor_prompts['medium'])}

Key traits:
- Witty and clever responses
- Appropriate use of humor and sarcasm
- Direct and honest communication
- Real-time knowledge when needed
- Helpful despite the humor

Maintain accuracy while being entertaining."""

        return await self.send_message(
            message=question,
            conversation_id=conversation_id,
            system_prompt=system_prompt,
            enable_real_time=True
        )
        
    async def get_real_time_info(
        self,
        query: str,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get real-time information on a topic.
        
        Args:
            query: Information query
            sources: Specific sources to search
            
        Returns:
            Real-time information response
        """
        sources = sources or self.context_sources
        
        system_prompt = """You are Grok with access to real-time information. Provide current, accurate information about the query. 

Focus on:
1. Latest developments and current status
2. Recent news and updates
3. Current statistics and data
4. Real-time context and implications

Be concise but comprehensive."""

        enhanced_query = f"""Provide current, real-time information about: {query}

Please include:
- Latest developments
- Current status/statistics
- Recent news if relevant
- Real-time context

Sources to check: {', '.join(sources)}"""

        response = await self.send_message(
            message=enhanced_query,
            system_prompt=system_prompt,
            enable_real_time=True
        )
        
        return {
            "query": query,
            "response": response,
            "sources_used": sources,
            "timestamp": datetime.utcnow().isoformat(),
            "real_time": True
        }
        
    async def analyze_with_personality(
        self,
        content: str,
        analysis_type: str = "general",
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze content with Grok's unique personality and perspective.
        
        Args:
            content: Content to analyze
            analysis_type: Type of analysis
            conversation_id: Conversation identifier
            
        Returns:
            Analysis with Grok's perspective
        """
        analysis_prompts = {
            "general": "Provide a witty and insightful general analysis.",
            "critical": "Give a critical analysis with your characteristic sharp wit.",
            "humorous": "Analyze this with maximum humor while maintaining accuracy.",
            "philosophical": "Provide a philosophical analysis with wit and depth."
        }
        
        system_prompt = f"""You are Grok, providing analysis with your unique perspective. {analysis_prompts.get(analysis_type, analysis_prompts['general'])}

Your analysis should be:
- Insightful and accurate
- Witty and engaging
- Direct and honest
- Thought-provoking
- Balanced between humor and substance"""

        analysis_request = f"""Analyze the following content:

{content}

Provide your analysis with your characteristic wit, insight, and honesty."""

        response = await self.send_message(
            message=analysis_request,
            conversation_id=conversation_id,
            system_prompt=system_prompt,
            enable_real_time=True
        )
        
        return {
            "content": content,
            "analysis_type": analysis_type,
            "response": response,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    async def _send_request(
        self,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> GrokResponse:
        """Send API request to Grok."""
        self.usage_stats["total_requests"] += 1
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            grok_response = GrokResponse(
                id=data["id"],
                object=data["object"],
                created=data["created"],
                model=data["model"],
                choices=data["choices"],
                usage=data["usage"],
                system_fingerprint=data.get("system_fingerprint")
            )
            
            # Update usage stats
            usage = data["usage"]
            self.usage_stats["total_tokens_prompt"] += usage["prompt_tokens"]
            self.usage_stats["total_tokens_completion"] += usage["completion_tokens"]
            
            # Update conversation history
            if conversation_id and grok_response.choices:
                assistant_message = grok_response.choices[0]["message"]["content"]
                self._update_conversation_history(conversation_id, assistant_message)
                
            return grok_response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Grok API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Grok API request failed: {e}")
            raise
            
    async def _stream_response(
        self,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream response from Grok."""
        self.usage_stats["total_requests"] += 1
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                
                full_content = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str.strip() == "[DONE]":
                            break
                            
                        try:
                            data = json.loads(data_str)
                            
                            if "choices" in data and data["choices"]:
                                choice = data["choices"][0]
                                delta = choice.get("delta", {})
                                
                                if "content" in delta and delta["content"]:
                                    content = delta["content"]
                                    full_content += content
                                    
                                    yield {
                                        "type": "content_delta",
                                        "content": content,
                                        "full_content": full_content
                                    }
                                    
                        except json.JSONDecodeError:
                            continue
                            
                # Update conversation history
                if conversation_id and full_content:
                    self._update_conversation_history(conversation_id, full_content)
                    
        except Exception as e:
            logger.error(f"Grok streaming failed: {e}")
            raise
            
    def _prepare_messages(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> List[GrokMessage]:
        """Prepare messages for API request."""
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append(GrokMessage(role="system", content=system_prompt))
            
        # Add conversation history
        if conversation_id and conversation_id in self.conversations:
            messages.extend(self.conversations[conversation_id])
            
        # Add user message
        messages.append(GrokMessage(
            role="user", 
            content=message,
            timestamp=datetime.utcnow().isoformat()
        ))
        
        return messages
        
    def _update_conversation_history(self, conversation_id: str, assistant_message: str):
        """Update conversation history."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            
        self.conversations[conversation_id].append(GrokMessage(
            role="assistant",
            content=assistant_message,
            timestamp=datetime.utcnow().isoformat()
        ))
        
        # Limit conversation history
        max_messages = 30
        if len(self.conversations[conversation_id]) > max_messages:
            self.conversations[conversation_id] = self.conversations[conversation_id][-max_messages:]
            
    def _message_to_dict(self, message: GrokMessage) -> Dict[str, Any]:
        """Convert GrokMessage to dictionary."""
        msg_dict = {
            "role": message.role,
            "content": message.content
        }
        if message.timestamp:
            msg_dict["timestamp"] = message.timestamp
        return msg_dict
        
    def set_real_time_sources(self, sources: List[str]):
        """Set real-time information sources."""
        self.context_sources = sources
        
    def enable_real_time(self, enabled: bool = True):
        """Enable or disable real-time information access."""
        self.real_time_enabled = enabled
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get current model information."""
        return self.available_models.get(self.model, {})
        
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return self.usage_stats.copy()
        
    def clear_conversation(self, conversation_id: str):
        """Clear conversation history."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
