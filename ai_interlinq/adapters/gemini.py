# File: /ai_interlinq/adapters/gemini.py
# Directory: /ai_interlinq/adapters

"""
Google Gemini adapter for AI-Interlinq framework.
Provides integration with Gemini models including vision and multimodal capabilities.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from dataclasses import dataclass
import logging
import httpx
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

@dataclass
class GeminiContent:
    """Gemini content structure for multimodal inputs."""
    role: str  # "user", "model"
    parts: List[Dict[str, Any]]

@dataclass
class GeminiResponse:
    """Gemini API response structure."""
    candidates: List[Dict[str, Any]]
    usage_metadata: Optional[Dict[str, Any]] = None
    prompt_feedback: Optional[Dict[str, Any]] = None

class GeminiAdapter:
    """
    Google Gemini integration adapter.
    
    Features:
    - Gemini Pro and Pro Vision models
    - Multimodal capabilities (text, images, video)
    - Function calling and tool use
    - Streaming responses
    - Safety settings configuration
    - Conversation management
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-pro",
        max_tokens: int = 8192,
        temperature: float = 0.7,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout: int = 60
    ):
        """
        Initialize Gemini adapter.
        
        Args:
            api_key: Google AI API key
            model: Gemini model to use
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
            "gemini-1.5-pro": {
                "max_tokens": 8192,
                "context_window": 2097152,  # 2M tokens
                "vision": True,
                "function_calling": True,
                "multimodal": True,
                "video": True
            },
            "gemini-1.5-flash": {
                "max_tokens": 8192,
                "context_window": 1048576,  # 1M tokens
                "vision": True,
                "function_calling": True,
                "multimodal": True,
                "video": True
            },
            "gemini-pro": {
                "max_tokens": 2048,
                "context_window": 32768,
                "vision": False,
                "function_calling": True,
                "multimodal": False,
                "video": False
            },
            "gemini-pro-vision": {
                "max_tokens": 2048,
                "context_window": 16384,
                "vision": True,
                "function_calling": False,
                "multimodal": True,
                "video": False
            }
        }
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Generation configuration
        self.generation_config = {
            "temperature": self.temperature,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": self.max_tokens,
            "stopSequences": []
        }
        
        # HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={"Content-Type": "application/json"}
        )
        
        # Conversation history
        self.conversations: Dict[str, List[GeminiContent]] = {}
        
        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens_input": 0,
            "total_tokens_output": 0,
            "multimodal_requests": 0,
            "function_calls": 0,
            "errors": 0
        }
        
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_instruction: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[GeminiResponse, AsyncGenerator[Dict[str, Any], None]]:
        """
        Send message to Gemini.
        
        Args:
            message: User message
            conversation_id: Conversation identifier for context
            system_instruction: System instruction for behavior
            tools: Available tools/functions
            stream: Enable streaming response
            **kwargs: Additional parameters
            
        Returns:
            Gemini response or streaming generator
        """
        try:
            # Prepare contents
            contents = self._prepare_contents(message, conversation_id)
            
            # Build request payload
            payload = {
                "contents": [self._content_to_dict(content) for content in contents],
                "generationConfig": self._build_generation_config(**kwargs),
                "safetySettings": self.safety_settings
            }
            
            # Add system instruction if provided
            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }
                
            # Add tools if provided
            if tools:
                payload["tools"] = tools
                
            if stream:
                return self._stream_response(payload, conversation_id)
            else:
                return await self._send_request(payload, conversation_id)
                
        except Exception as e:
            logger.error(f"Gemini message send failed: {e}")
            self.usage_stats["errors"] += 1
            raise
            
    async def send_multimodal_message(
        self,
        text: str,
        media_items: List[Dict[str, Any]],
        conversation_id: Optional[str] = None,
        **kwargs
    ) -> GeminiResponse:
        """
        Send multimodal message with images/video.
        
        Args:
            text: Text message
            media_items: List of media items (images, video)
            conversation_id: Conversation identifier
            **kwargs: Additional parameters
            
        Returns:
            Gemini response
        """
        self.usage_stats["multimodal_requests"] += 1
        
        # Build multimodal parts
        parts = [{"text": text}]
        
        for media_item in media_items:
            if media_item.get("type") == "image":
                if "base64" in media_item:
                    parts.append({
                        "inlineData": {
                            "mimeType": media_item.get("mime_type", "image/jpeg"),
                            "data": media_item["base64"]
                        }
                    })
                elif "url" in media_item:
                    # Download and encode image
                    try:
                        image_data = await self._download_and_encode_image(media_item["url"])
                        parts.append({
                            "inlineData": {
                                "mimeType": media_item.get("mime_type", "image/jpeg"),
                                "data": image_data
                            }
                        })
                    except Exception as e:
                        logger.warning(f"Failed to download image from {media_item['url']}: {e}")
                        
            elif media_item.get("type") == "video":
                if "base64" in media_item:
                    parts.append({
                        "inlineData": {
                            "mimeType": media_item.get("mime_type", "video/mp4"),
                            "data": media_item["base64"]
                        }
                    })
                    
        # Create content with multimodal parts
        contents = self._get_conversation_history(conversation_id)
        contents.append(GeminiContent(role="user", parts=parts))
        
        # Build payload
        payload = {
            "contents": [self._content_to_dict(content) for content in contents],
            "generationConfig": self._build_generation_config(**kwargs),
            "safetySettings": self.safety_settings
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
        Call function using Gemini's function calling.
        
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
        
        # Check for function calls in response
        function_calls = []
        if response.candidates:
            candidate = response.candidates[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            
            for part in parts:
                if "functionCall" in part:
                    function_calls.append(part["functionCall"])
                    
        if not function_calls:
            return {"response": response, "function_calls": []}
            
        self.usage_stats["function_calls"] += len(function_calls)
        
        # Execute function calls if auto_execute is enabled
        function_results = []
        if auto_execute:
            for function_call in function_calls:
                try:
                    result = await self._execute_function_call(function_call)
                    function_results.append(result)
                except Exception as e:
                    logger.error(f"Function execution failed: {e}")
                    function_results.append({"error": str(e)})
                    
        return {
            "response": response,
            "function_calls": function_calls,
            "function_results": function_results
        }
        
    async def count_tokens(
        self,
        text: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
            model: Model to use for counting
            
        Returns:
            Token count information
        """
        model_name = model or self.model
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": text}]
                }
            ]
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/models/{model_name}:countTokens?key={self.api_key}",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Token counting failed: {e}")
            raise
            
    async def _send_request(
        self,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> GeminiResponse:
        """Send API request to Gemini."""
        self.usage_stats["total_requests"] += 1
        
        try:
            response = await self.client.post(
                f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            gemini_response = GeminiResponse(
                candidates=data.get("candidates", []),
                usage_metadata=data.get("usageMetadata"),
                prompt_feedback=data.get("promptFeedback")
            )
            
            # Update usage stats
            if gemini_response.usage_metadata:
                usage = gemini_response.usage_metadata
                self.usage_stats["total_tokens_input"] += usage.get("promptTokenCount", 0)
                self.usage_stats["total_tokens_output"] += usage.get("candidatesTokenCount", 0)
                
            # Update conversation history
            if conversation_id and gemini_response.candidates:
                candidate = gemini_response.candidates[0]
                if "content" in candidate:
                    self._update_conversation_history(conversation_id, candidate["content"])
                    
            return gemini_response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            raise
            
    async def _stream_response(
        self,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream response from Gemini."""
        self.usage_stats["total_requests"] += 1
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/models/{self.model}:streamGenerateContent?key={self.api_key}",
                json=payload
            ) as response:
                response.raise_for_status()
                
                full_content = ""
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            # Remove any potential prefix
                            line_data = line.strip()
                            if line_data.startswith("data: "):
                                line_data = line_data[6:]
                                
                            data = json.loads(line_data)
                            
                            if "candidates" in data and data["candidates"]:
                                candidate = data["candidates"][0]
                                content = candidate.get("content", {})
                                parts = content.get("parts", [])
                                
                                for part in parts:
                                    if "text" in part:
                                        text = part["text"]
                                        full_content += text
                                        
                                        yield {
                                            "type": "content_delta",
                                            "text": text,
                                            "full_content": full_content
                                        }
                                        
                                if candidate.get("finishReason"):
                                    yield {
                                        "type": "completion",
                                        "finish_reason": candidate["finishReason"],
                                        "full_content": full_content
                                    }
                                    
                        except json.JSONDecodeError as e:
                            logger.debug(f"JSON decode error: {e}")
                            continue
                            
                # Update conversation history
                if conversation_id and full_content:
                    content_obj = {
                        "role": "model",
                        "parts": [{"text": full_content}]
                    }
                    self._update_conversation_history(conversation_id, content_obj)
                    
        except Exception as e:
            logger.error(f"Gemini streaming failed: {e}")
            raise
            
    def _prepare_contents(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> List[GeminiContent]:
        """Prepare contents for API request."""
        contents = self._get_conversation_history(conversation_id)
        contents.append(GeminiContent(
            role="user",
            parts=[{"text": message}]
        ))
        return contents
        
    def _get_conversation_history(self, conversation_id: Optional[str]) -> List[GeminiContent]:
        """Get conversation history."""
        if not conversation_id:
            return []
            
        return self.conversations.get(conversation_id, []).copy()
        
    def _update_conversation_history(self, conversation_id: str, content: Dict[str, Any]):
        """Update conversation history."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            
        # Convert content to GeminiContent
        gemini_content = GeminiContent(
            role=content["role"],
            parts=content["parts"]
        )
        
        self.conversations[conversation_id].append(gemini_content)
        
        # Limit conversation history
        max_contents = 20
        if len(self.conversations[conversation_id]) > max_contents:
            self.conversations[conversation_id] = self.conversations[conversation_id][-max_contents:]
            
    def _content_to_dict(self, content: GeminiContent) -> Dict[str, Any]:
        """Convert GeminiContent to dictionary."""
        return {
            "role": content.role,
            "parts": content.parts
        }
        
    def _build_generation_config(self, **kwargs) -> Dict[str, Any]:
        """Build generation configuration."""
        config = self.generation_config.copy()
        
        # Update with provided parameters
        for key, value in kwargs.items():
            if key == "temperature":
                config["temperature"] = value
            elif key == "max_tokens":
                config["maxOutputTokens"] = value
            elif key == "top_p":
                config["topP"] = value
            elif key == "top_k":
                config["topK"] = value
            elif key == "stop":
                config["stopSequences"] = value if isinstance(value, list) else [value]
                
        return config
        
    async def _download_and_encode_image(self, url: str) -> str:
        """Download image from URL and encode as base64."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            image_data = response.content
            return base64.b64encode(image_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            raise
            
    async def _execute_function_call(self, function_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute function call (placeholder for function registry integration)."""
        return {
            "function_name": function_call.get("name"),
            "result": "Function execution not implemented",
            "status": "pending"
        }
        
    def set_safety_settings(self, settings: List[Dict[str, Any]]):
        """Set safety settings."""
        self.safety_settings = settings
        
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
