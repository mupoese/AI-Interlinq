# File: /ai_interlinq/adapters/openai.py
# Directory: /ai_interlinq/adapters

"""
OpenAI GPT adapter for AI-Interlinq framework.
Provides integration with OpenAI models including GPT-4, GPT-3.5, and function calling.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncGenerator, Union, Callable
from dataclasses import dataclass
import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class OpenAIMessage:
    """OpenAI message structure."""
    role: str  # "system", "user", "assistant", "function", "tool"
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

@dataclass
class OpenAIResponse:
    """OpenAI API response structure."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    system_fingerprint: Optional[str] = None

class OpenAIAdapter:
    """
    OpenAI GPT integration adapter.
    
    Features:
    - Multiple GPT model support (GPT-4, GPT-4 Turbo, GPT-3.5 Turbo)
    - Function calling and tool use
    - Streaming responses
    - Vision capabilities (GPT-4V)
    - Fine-tuned model support
    - Conversation management
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        base_url: str = "https://api.openai.com/v1",
        organization: Optional[str] = None,
        timeout: int = 60
    ):
        """
        Initialize OpenAI adapter.
        
        Args:
            api_key: OpenAI API key
            model: GPT model to use
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0.0-2.0)
            base_url: API base URL
            organization: OpenAI organization ID
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.base_url = base_url.rstrip('/')
        self.organization = organization
        self.timeout = timeout
        
        # Available models with capabilities
        self.available_models = {
            "gpt-4-turbo-preview": {
                "max_tokens": 4096,
                "context_window": 128000,
                "function_calling": True,
                "vision": False,
                "knowledge_cutoff": "2024-04"
            },
            "gpt-4-vision-preview": {
                "max_tokens": 4096,
                "context_window": 128000,
                "function_calling": True,
                "vision": True,
                "knowledge_cutoff": "2024-04"
            },
            "gpt-4": {
                "max_tokens": 4096,
                "context_window": 8192,
                "function_calling": True,
                "vision": False,
                "knowledge_cutoff": "2023-09"
            },
            "gpt-4-32k": {
                "max_tokens": 4096,
                "context_window": 32768,
                "function_calling": True,
                "vision": False,
                "knowledge_cutoff": "2023-09"
            },
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "context_window": 16385,
                "function_calling": True,
                "vision": False,
                "knowledge_cutoff": "2023-09"
            }
        }
        
        # Build headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
            
        # HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=headers
        )
        
        # Conversation history
        self.conversations: Dict[str, List[OpenAIMessage]] = {}
        
        # Function registry
        self.functions: Dict[str, Dict[str, Any]] = {}
        
        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens_prompt": 0,
            "total_tokens_completion": 0,
            "total_cost": 0.0,
            "function_calls": 0,
            "errors": 0
        }
        
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[OpenAIResponse, AsyncGenerator[Dict[str, Any], None]]:
        """
        Send message to OpenAI GPT.
        
        Args:
            message: User message
            conversation_id: Conversation identifier for context
            system_prompt: System prompt for behavior
            functions: Available functions (deprecated, use tools)
            tools: Available tools/functions
            stream: Enable streaming response
            **kwargs: Additional parameters
            
        Returns:
            OpenAI response or streaming generator
        """
        try:
            # Prepare messages
            messages = self._prepare_messages(message, conversation_id, system_prompt)
            
            # Build request payload
            payload = {
                "model": self.model,
                "messages": [self._message_to_dict(msg) for msg in messages],
                "temperature": kwargs.get("temperature", self.temperature),
                "stream": stream
            }
            
            # Add max_tokens if specified
            if self.max_tokens or kwargs.get("max_tokens"):
                payload["max_tokens"] = kwargs.get("max_tokens", self.max_tokens)
                
            # Add functions or tools
            if functions:
                payload["functions"] = functions
                payload["function_call"] = kwargs.get("function_call", "auto")
            elif tools:
                payload["tools"] = tools
                payload["tool_choice"] = kwargs.get("tool_choice", "auto")
                
            # Additional parameters
            for param in ["top_p", "frequency_penalty", "presence_penalty", "stop"]:
                if param in kwargs:
                    payload[param] = kwargs[param]
                    
            if stream:
                return self._stream_response(payload, conversation_id)
            else:
                return await self._send_request(payload, conversation_id)
                
        except Exception as e:
            logger.error(f"OpenAI message send failed: {e}")
            self.usage_stats["errors"] += 1
            raise
            
    async def send_vision_message(
        self,
        text: str,
        images: List[Union[str, Dict[str, Any]]],
        conversation_id: Optional[str] = None,
        detail: str = "auto",
        **kwargs
    ) -> OpenAIResponse:
        """
        Send message with vision capabilities.
        
        Args:
            text: Text message
            images: List of image URLs or base64 data
            conversation_id: Conversation identifier
            detail: Vision detail level ("low", "high", "auto")
            **kwargs: Additional parameters
            
        Returns:
            OpenAI response
        """
        if "vision" not in self.model:
            # Use vision model
            original_model = self.model
            self.model = "gpt-4-vision-preview"
            
        try:
            # Build vision content
            content = [{"type": "text", "text": text}]
            
            for image in images:
                if isinstance(image, str):
                    # URL or base64 string
                    if image.startswith(("http://", "https://")):
                        image_content = {
                            "type": "image_url",
                            "image_url": {"url": image, "detail": detail}
                        }
                    else:
                        # Assume base64
                        image_content = {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image}", "detail": detail}
                        }
                else:
                    # Dictionary with url or base64
                    if "url" in image:
                        image_content = {
                            "type": "image_url",
                            "image_url": {"url": image["url"], "detail": detail}
                        }
                    elif "base64" in image:
                        media_type = image.get("media_type", "image/jpeg")
                        image_content = {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image['base64']}",
                                "detail": detail
                            }
                        }
                        
                content.append(image_content)
                
            # Create message with vision content
            messages = self._get_conversation_history(conversation_id)
            messages.append(OpenAIMessage(role="user", content=content))
            
            # Send request
            payload = {
                "model": self.model,
                "messages": [self._message_to_dict(msg) for msg in messages],
                "temperature": kwargs.get("temperature", self.temperature)
            }
            
            if self.max_tokens:
                payload["max_tokens"] = self.max_tokens
                
            return await self._send_request(payload, conversation_id)
            
        finally:
            # Restore original model if changed
            if "vision" not in self.model and "original_model" in locals():
                self.model = original_model
                
    async def call_function(
        self,
        message: str,
        functions: List[Dict[str, Any]],
        conversation_id: Optional[str] = None,
        auto_execute: bool = False
    ) -> Dict[str, Any]:
        """
        Call function using OpenAI function calling.
        
        Args:
            message: User message that may trigger function calls
            functions: Available functions
            conversation_id: Conversation identifier
            auto_execute: Auto-execute function calls
            
        Returns:
            Function call results
        """
        # Convert functions to tools format
        tools = [{"type": "function", "function": func} for func in functions]
        
        response = await self.send_message(
            message=message,
            conversation_id=conversation_id,
            tools=tools
        )
        
        # Check for tool calls in response
        choice = response.choices[0]
        message_obj = choice["message"]
        tool_calls = message_obj.get("tool_calls", [])
        
        if not tool_calls:
            return {"response": response, "tool_calls": []}
            
        self.usage_stats["function_calls"] += len(tool_calls)
        
        # Execute tool calls if auto_execute is enabled
        tool_results = []
        if auto_execute:
            for tool_call in tool_calls:
                try:
                    result = await self._execute_tool_call(tool_call)
                    tool_results.append(result)
                    
                    # Add tool result to conversation
                    if conversation_id:
                        self._add_tool_result_to_conversation(
                            conversation_id, tool_call, result
                        )
                        
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
    ) -> OpenAIResponse:
        """Send API request to OpenAI."""
        self.usage_stats["total_requests"] += 1
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            openai_response = OpenAIResponse(
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
            if conversation_id and openai_response.choices:
                assistant_message = openai_response.choices[0]["message"]
                self._update_conversation_history(conversation_id, assistant_message)
                
            return openai_response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            raise
            
    async def _stream_response(
        self,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream response from OpenAI."""
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
                        data_str = line[6:]  # Remove "data: " prefix
                        
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
                                        "full_content": full_content,
                                        "choice_index": choice.get("index", 0)
                                    }
                                    
                                if choice.get("finish_reason"):
                                    yield {
                                        "type": "completion",
                                        "finish_reason": choice["finish_reason"],
                                        "full_content": full_content
                                    }
                                    
                        except json.JSONDecodeError:
                            continue
                            
                # Update conversation history
                if conversation_id and full_content:
                    assistant_message = {"role": "assistant", "content": full_content}
                    self._update_conversation_history(conversation_id, assistant_message)
                    
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise
            
    def _prepare_messages(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> List[OpenAIMessage]:
        """Prepare messages for API request."""
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append(OpenAIMessage(role="system", content=system_prompt))
            
        # Add conversation history
        messages.extend(self._get_conversation_history(conversation_id))
        
        # Add user message
        messages.append(OpenAIMessage(role="user", content=message))
        
        return messages
        
    def _get_conversation_history(self, conversation_id: Optional[str]) -> List[OpenAIMessage]:
        """Get conversation history."""
        if not conversation_id:
            return []
            
        return self.conversations.get(conversation_id, []).copy()
        
    def _update_conversation_history(self, conversation_id: str, assistant_message: Dict[str, Any]):
        """Update conversation history."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            
        # Add user message if not already added
        # Add assistant message
        self.conversations[conversation_id].append(
            OpenAIMessage(
                role=assistant_message["role"],
                content=assistant_message.get("content"),
                function_call=assistant_message.get("function_call"),
                tool_calls=assistant_message.get("tool_calls")
            )
        )
        
        # Limit conversation history
        max_messages = 30
        if len(self.conversations[conversation_id]) > max_messages:
            # Keep system message if present, then trim
            system_messages = [msg for msg in self.conversations[conversation_id] if msg.role == "system"]
            other_messages = [msg for msg in self.conversations[conversation_id] if msg.role != "system"]
            
            trimmed_messages = system_messages + other_messages[-(max_messages - len(system_messages)):]
            self.conversations[conversation_id] = trimmed_messages
            
    def _message_to_dict(self, message: OpenAIMessage) -> Dict[str, Any]:
        """Convert OpenAIMessage to dictionary."""
        msg_dict = {"role": message.role}
        
        if message.content is not None:
            msg_dict["content"] = message.content
        if message.name is not None:
            msg_dict["name"] = message.name
        if message.function_call is not None:
            msg_dict["function_call"] = message.function_call
        if message.tool_calls is not None:
            msg_dict["tool_calls"] = message.tool_calls
        if message.tool_call_id is not None:
            msg_dict["tool_call_id"] = message.tool_call_id
            
        return msg_dict
        
    def _add_tool_result_to_conversation(
        self,
        conversation_id: str,
        tool_call: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """Add tool result to conversation."""
        if conversation_id not in self.conversations:
            return
            
        # Add tool result message
        self.conversations[conversation_id].append(
            OpenAIMessage(
                role="tool",
                content=json.dumps(result),
                tool_call_id=tool_call["id"]
            )
        )
        
    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool call (placeholder for function registry integration)."""
        function_name = tool_call["function"]["name"]
        
        if function_name in self.functions:
            # Execute registered function
            func_info = self.functions[function_name]
            # This would call the actual function
            return {"result": f"Function {function_name} executed", "status": "success"}
        else:
            return {"error": f"Function {function_name} not found", "status": "error"}
            
    def register_function(self, name: str, function: Callable, schema: Dict[str, Any]):
        """Register a function for tool calling."""
        self.functions[name] = {
            "function": function,
            "schema": schema
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
