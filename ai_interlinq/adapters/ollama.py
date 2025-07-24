# File: /ai_interlinq/adapters/ollama.py
# Directory: /ai_interlinq/adapters

"""
Ollama local LLM adapter for AI-Interlinq framework.
Provides integration with local Ollama models including Llama, Mistral, CodeLlama, etc.
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
class OllamaModel:
    """Ollama model information."""
    name: str
    modified_at: str
    size: int
    digest: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class OllamaResponse:
    """Ollama API response structure."""
    model: str
    created_at: str
    response: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None

class OllamaAdapter:
    """
    Ollama local LLM integration adapter.
    
    Features:
    - Multiple local model support (Llama, Mistral, CodeLlama, etc.)
    - Model management (pull, delete, list)
    - Streaming responses
    - Context preservation
    - Custom model parameters
    - Embeddings generation
    - Model fine-tuning support
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        timeout: int = 300,
        keep_alive: str = "5m"
    ):
        """
        Initialize Ollama adapter.
        
        Args:
            base_url: Ollama server URL
            model: Default model to use
            timeout: Request timeout in seconds
            keep_alive: How long to keep model in memory
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.keep_alive = keep_alive
        
        # HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={"Content-Type": "application/json"}
        )
        
        # Available models cache
        self.available_models: Dict[str, OllamaModel] = {}
        self._models_last_updated = 0
        
        # Conversation contexts
        self.contexts: Dict[str, List[int]] = {}
        
        # Model parameters
        self.default_parameters = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "num_ctx": 2048,
            "num_predict": -1,
            "stop": []
        }
        
        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens_processed": 0,
            "total_generation_time": 0.0,
            "model_loads": 0,
            "errors": 0
        }
        
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[OllamaResponse, AsyncGenerator[Dict[str, Any], None]]:
        """
        Send message to Ollama model.
        
        Args:
            message: User message
            conversation_id: Conversation identifier for context
            model: Model to use (overrides default)
            system_prompt: System prompt for behavior
            stream: Enable streaming response
            **kwargs: Additional parameters
            
        Returns:
            Ollama response or streaming generator
        """
        try:
            model_name = model or self.model
            
            # Build prompt with system context
            prompt = message
            if system_prompt:
                prompt = f"System: {system_prompt}\nUser: {message}"
                
            # Build request payload
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": stream,
                "keep_alive": self.keep_alive
            }
            
            # Add context if available
            if conversation_id and conversation_id in self.contexts:
                payload["context"] = self.contexts[conversation_id]
                
            # Add model parameters
            options = self.default_parameters.copy()
            options.update(kwargs.get("options", {}))
            payload["options"] = options
            
            if stream:
                return self._stream_response(payload, conversation_id)
            else:
                return await self._send_request(payload, conversation_id)
                
        except Exception as e:
            logger.error(f"Ollama message send failed: {e}")
            self.usage_stats["errors"] += 1
            raise
            
    async def generate_embeddings(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            model: Model to use for embeddings
            
        Returns:
            List of embedding values
        """
        model_name = model or f"{self.model}:embedding"
        
        payload = {
            "model": model_name,
            "prompt": text
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            return data["embedding"]
            
        except Exception as e:
            logger.error(f"Ollama embeddings failed: {e}")
            raise
            
    async def list_models(self, refresh: bool = False) -> List[OllamaModel]:
        """
        List available models.
        
        Args:
            refresh: Force refresh from server
            
        Returns:
            List of available models
        """
        current_time = time.time()
        
        # Use cache if recent and not forced refresh
        if not refresh and (current_time - self._models_last_updated) < 60:
            return list(self.available_models.values())
            
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            for model_data in data.get("models", []):
                model = OllamaModel(
                    name=model_data["name"],
                    modified_at=model_data["modified_at"],
                    size=model_data["size"],
                    digest=model_data["digest"],
                    details=model_data.get("details")
                )
                models.append(model)
                self.available_models[model.name] = model
                
            self._models_last_updated = current_time
            return models
            
        except Exception as e:
            logger.error(f"Ollama list models failed: {e}")
            raise
            
    async def pull_model(
        self,
        model_name: str,
        stream: bool = True
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        Pull/download a model.
        
        Args:
            model_name: Name of model to pull
            stream: Stream download progress
            
        Returns:
            Pull status or streaming progress
        """
        payload = {
            "name": model_name,
            "stream": stream
        }
        
        try:
            if stream:
                return self._stream_pull_progress(payload)
            else:
                response = await self.client.post(
                    f"{self.base_url}/api/pull",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Ollama pull model failed: {e}")
            raise
            
    async def delete_model(self, model_name: str) -> Dict[str, Any]:
        """
        Delete a model.
        
        Args:
            model_name: Name of model to delete
            
        Returns:
            Deletion status
        """
        payload = {"name": model_name}
        
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/delete",
                json=payload
            )
            response.raise_for_status()
            
            # Remove from cache
            if model_name in self.available_models:
                del self.available_models[model_name]
                
            return {"status": "success", "message": f"Model {model_name} deleted"}
            
        except Exception as e:
            logger.error(f"Ollama delete model failed: {e}")
            raise
            
    async def show_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get detailed model information.
        
        Args:
            model_name: Name of model
            
        Returns:
            Model information
        """
        payload = {"name": model_name}
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/show",
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Ollama show model failed: {e}")
            raise
            
    async def copy_model(self, source: str, destination: str) -> Dict[str, Any]:
        """
        Copy a model.
        
        Args:
            source: Source model name
            destination: Destination model name
            
        Returns:
            Copy status
        """
        payload = {
            "source": source,
            "destination": destination
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/copy",
                json=payload
            )
            response.raise_for_status()
            return {"status": "success", "message": f"Model copied from {source} to {destination}"}
            
        except Exception as e:
            logger.error(f"Ollama copy model failed: {e}")
            raise
            
    async def _send_request(
        self,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> OllamaResponse:
        """Send API request to Ollama."""
        self.usage_stats["total_requests"] += 1
        start_time = time.time()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            ollama_response = OllamaResponse(
                model=data["model"],
                created_at=data["created_at"],
                response=data["response"],
                done=data["done"],
                context=data.get("context"),
                total_duration=data.get("total_duration"),
                load_duration=data.get("load_duration"),
                prompt_eval_count=data.get("prompt_eval_count"),
                prompt_eval_duration=data.get("prompt_eval_duration"),
                eval_count=data.get("eval_count"),
                eval_duration=data.get("eval_duration")
            )
            
            # Update usage stats
            generation_time = time.time() - start_time
            self.usage_stats["total_generation_time"] += generation_time
            
            if ollama_response.eval_count:
                self.usage_stats["total_tokens_processed"] += ollama_response.eval_count
                
            # Store context for conversation
            if conversation_id and ollama_response.context:
                self.contexts[conversation_id] = ollama_response.context
                
            return ollama_response
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Ollama API request failed: {e}")
            raise
            
    async def _stream_response(
        self,
        payload: Dict[str, Any],
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream response from Ollama."""
        self.usage_stats["total_requests"] += 1
        start_time = time.time()
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()
                
                full_response = ""
                context = None
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            
                            if "response" in data:
                                chunk = data["response"]
                                full_response += chunk
                                
                                yield {
                                    "type": "content_delta",
                                    "content": chunk,
                                    "full_content": full_response,
                                    "done": data.get("done", False)
                                }
                                
                            if data.get("done"):
                                context = data.get("context")
                                
                                yield {
                                    "type": "completion",
                                    "full_content": full_response,
                                    "context": context,
                                    "total_duration": data.get("total_duration"),
                                    "eval_count": data.get("eval_count")
                                }
                                
                        except json.JSONDecodeError:
                            continue
                            
                # Update stats and context
                generation_time = time.time() - start_time
                self.usage_stats["total_generation_time"] += generation_time
                
                if conversation_id and context:
                    self.contexts[conversation_id] = context
                    
        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise
            
    async def _stream_pull_progress(
        self,
        payload: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream model pull progress."""
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/pull",
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            yield data
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Ollama pull streaming failed: {e}")
            raise
            
    def clear_context(self, conversation_id: str):
        """Clear conversation context."""
        if conversation_id in self.contexts:
            del self.contexts[conversation_id]
            
    def get_context(self, conversation_id: str) -> Optional[List[int]]:
        """Get conversation context."""
        return self.contexts.get(conversation_id)
        
    def set_model_parameters(self, **parameters):
        """Set default model parameters."""
        self.default_parameters.update(parameters)
        
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        stats = self.usage_stats.copy()
        if stats["total_requests"] > 0:
            stats["avg_generation_time"] = stats["total_generation_time"] / stats["total_requests"]
        else:
            stats["avg_generation_time"] = 0.0
        return stats
        
    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama server health."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return {"status": "healthy", "server": "ollama", "url": self.base_url}
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}
            
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
