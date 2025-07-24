# File: /ai_interlinq/adapters/anthropic.py
# Directory: /ai_interlinq/adapters

"""
Anthropic Claude adapter for AI-Interlinq framework.
Provides integration with Claude models including streaming support.
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
class ClaudeMessage:
    """Claude message structure."""
    role: str  # "user", "assistant", "system"
    content: Union[str, List[Dict[str, Any]]]
    
@dataclass
class ClaudeResponse:
    """Claude API response structure."""
    id: str
    content: List[Dict[str, Any]]
    model: str
    role: str
    stop_reason: Optional[str]
    stop_sequence: Optional[str]
    usage: Dict[str, int]
    
class AnthropicAdapter:
    """
    Anthropic Claude integration adapter.
    
    Features:
    - Multiple Claude model support (Claude-3, Claude-3.5 Sonnet, Haiku, Opus)
    - Streaming responses
    - Vision capabilities
    - Function calling support
    - Conversation history management
    - Rate limit handling
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        base_url: str = "https://api.anthropic.com",
        timeout: int = 60
    ):
        """
        Initialize Anthropic adapter.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0.0-1.0)
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
            "claude-3-5-sonnet-20241022": {
                "max_tokens": 200000,
                "context_window": 200000,
                "vision": True,
                "function_calling": True,
                "multimodal": True
            },
            "claude-3-opus-20240229": {
                "max_tokens": 200000,
                "context_window": 200000,
                "vision": True,
                "function_calling": True,
                "multimodal": True
            },
            "claude-3-sonnet-20240229": {
                "max_tokens": 200000,
                "context_window": 200000,
                "vision": True,
                "function_calling": True,
                "multimodal": True
            },
            "claude-3-haiku-20240307": {
                "max_tokens": 200000,
                "context_window": 200000,
                "vision": True,
                "function_calling": True,
                "multimodal": True
            }
        }
        
        # HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "x-api-key": self.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
        )
        
        # Conversation history
        self.conversations: Dict[str, List[ClaudeMessage]] = {}
        
        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "total_cost": 0.0,
            "errors": 0
        }
        
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ClaudeResponse, AsyncGenerator[Dict[str, Any], None]]:
        """
        Send message to Claude.
        
        Args:
            message: User message
            conversation_id: Conversation identifier for context
            system_prompt: System prompt for behavior
            tools: Available tools/functions
            stream: Enable streaming response
            **kwargs: Additional parameters
            
        Returns:
            Claude response or streaming generator
        """
        try:
            # Prepare messages
            messages = self._prepare_messages(message, conversation_id, system_prompt)
            
            # Build request payload
            payload = {
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
                "temperature": kwargs.get("temperature", self.temperature)
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt
                
            # Add tools if provided
            if tools:
                payload["tools"] = tools
                
            # Add streaming if requested
            if stream:
                payload["stream"] = True
                return self._stream_response(payload, conversation_id)
            else:
                return await self._send_request(payload, conversation_id)
                
        except Exception as e:
            logger.error(f"Claude message send failed: {e}")
            self.usage_stats["errors"] += 1
            raise
            
    async def send_multimodal_message(
        self,
        text: str,
        images: List[Dict[str, Any]],
        conversation_id: Optional[str] = None,
        **kwargs
    ) -> ClaudeResponse:
        """
        Send multimodal message with images.
        
        Args:
            text: Text message
            images: List of image data dictionaries
            conversation_id: Conversation identifier
            **kwargs: Additional parameters
            
        Returns:
            Claude response
        """
        # Build multimodal content
        content = [{"type": "text", "text": text}]
        
        for image in images:
            if "base64" in image:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image.get("media_type", "image/jpeg"),
                        "data": image["base64"]
                    }
                })
            elif "url" in image:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "url", 
                        "url": image["url"]
                    }
                })
                
        # Create message with multimodal content
        messages = self._get_conversation_history(conversation_id)
        messages.append(ClaudeMessage(role="user", content=content))
        
        # Build payload
        payload = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": kwargs.get("temperature", self.temperature)
        }
        
        return await self._send_request(payload, conversation_id)
        
    async def call_function(
        self,
        message: str,
        tools: List[Dict[str, Any]],
        conversation_id: Optional[str] = None,
        auto_execute: bool = False
    ) -> Dict[str, Any]:
        """
        Call function using Claude's tool use capability.
        
        Args:
            message: User message that may trigger function calls
            tools: Available tools/functions
            conversation_id: Conversation identifier
            auto_execute: Auto-execute function calls
            
        Returns:
            Function call results
        """
        response = await self.send_message(
            message=message,
            conversation_id=conversation_id,
            tools=tools
        )
        
        # Check for tool use in response
        tool_calls = []
        for content_block in response.content:
            if content_block.get("type") == "tool_use":
                tool_calls.append(content_block)
                
        if not tool_calls:
            return {"response": response, "tool_calls": []}
            
        # Execute tool calls if auto_execute is enabled
        tool_results = []
        if auto_execute:
            for tool_call in tool_calls:
                try:
                    # This would need to be implemented based on your function registry
                    result = await self._execute_tool_call(tool_call)
                    tool_results.append(result)
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    tool_results.append({"error": str(e)})
                    
        return {
            "response": response,
            "tool_calls": tool_calls,
            "tool_results": tool_results
        }
        
    async def _send_request(
        self,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> ClaudeResponse:
        """Send API request to Claude."""
        self.usage_stats["total_requests"] += 1
        
        try:
            response = await self.client.post(
                f"{self.base_url}/v1/messages",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            claude_response = ClaudeResponse(
                id=data["id"],
                content=data["content"],
                model=data["model"],
                role=data["role"],
                stop_reason=data.get("stop_reason"),
                stop_sequence=data.get("stop_sequence"),
                usage=data["usage"]
            )
            
            # Update usage stats
            self.usage_stats["total_tokens_input"] += data["usage"]["input_tokens"]
            self.usage_stats["total_tokens_output"] += data["usage"]["output_tokens"]
            
            # Update conversation history
            if conversation_id:
                self._update_conversation_history(
                    conversation_id,
                    claude_response.content[0]["text"] if claude_response.content else ""
                )
                
            return claude_response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Claude API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Claude API request failed: {e}")
            raise
            
    async def _stream_response(
        self,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream response from Claude."""
        self.usage_stats["total_requests"] += 1
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/v1/messages",
                json=payload
            ) as response:
                response.raise_for_status()
                
                full_response = ""
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        if data_str.strip() == "[DONE]":
                            break
                            
                        try:
                            data = json.loads(data_str)
                            
                            if data["type"] == "content_block_delta":
                                delta = data["delta"]
                                if delta.get("type") == "text_delta":
                                    text = delta.get("text", "")
                                    full_response += text
                                    
                                    yield {
                                        "type": "content_delta",
                                        "text": text,
                                        "full_text": full_response
                                    }
                                    
                            elif data["type"] == "message_delta":
                                if "usage" in data:
                                    usage = data["usage"]
                                    self.usage_stats["total_tokens_output"] += usage.get("output_tokens", 0)
                                    
                                yield {
                                    "type": "usage_update",
                                    "usage": data.get("usage", {})
                                }
                                
                        except json.JSONDecodeError:
                            continue
                            
                # Update conversation history
                if conversation_id and full_response:
                    self._update_conversation_history(conversation_id, full_response)
                    
        except Exception as e:
            logger.error(f"Claude streaming failed: {e}")
            raise
            
    def _prepare_messages(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> List[ClaudeMessage]:
        """Prepare messages for API request."""
        messages = self._get_conversation_history(conversation_id)
        messages.append(ClaudeMessage(role="user", content=message))
        return messages
        
    def _get_conversation_history(self, conversation_id: Optional[str]) -> List[ClaudeMessage]:
        """Get conversation history."""
        if not conversation_id:
            return []
            
        return self.conversations.get(conversation_id, []).copy()
        
    def _update_conversation_history(self, conversation_id: str, assistant_message: str):
        """Update conversation history."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            
        self.conversations[conversation_id].append(
            ClaudeMessage(role="assistant", content=assistant_message)
        )
        
        # Limit conversation history to prevent context overflow
        max_messages = 20
        if len(self.conversations[conversation_id]) > max_messages:
            self.conversations[conversation_id] = self.conversations[conversation_id][-max_messages:]
            
    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool call (placeholder for function registry integration)."""
        # This would integrate with a function registry system
        return {
            "tool_call_id": tool_call["id"],
            "result": "Tool execution not implemented",
            "status": "pending"
        }
        
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
            
    def list_conversations(self) -> List[str]:
        """List active conversation IDs."""
        return list(self.conversations.keys())
        
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
