# File: /ai_interlinq/adapters/huggingface.py
# Directory: /ai_interlinq/adapters

"""
HuggingFace adapter for AI-Interlinq framework.
Provides integration with HuggingFace models via Inference API and custom endpoints.
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
class HuggingFaceModel:
    """HuggingFace model information."""
    model_id: str
    task: str
    endpoint_url: Optional[str] = None
    is_custom: bool = False

@dataclass
class HuggingFaceResponse:
    """HuggingFace API response structure."""
    generated_text: Optional[str] = None
    embeddings: Optional[List[float]] = None
    labels: Optional[List[str]] = None
    scores: Optional[List[float]] = None
    raw_response: Optional[Dict[str, Any]] = None

class HuggingFaceAdapter:
    """
    HuggingFace integration adapter.
    
    Features:
    - Multiple model support via Inference API
    - Custom endpoint integration
    - Text generation, classification, embeddings
    - Vision models support
    - Streaming responses
    - Model switching and management
    """
    
    def __init__(
        self,
        api_token: str,
        model_id: str = "microsoft/DialoGPT-large",
        base_url: str = "https://api-inference.huggingface.co/models",
        timeout: int = 60,
        custom_endpoint: Optional[str] = None
    ):
        """
        Initialize HuggingFace adapter.
        
        Args:
            api_token: HuggingFace API token
            model_id: Model identifier
            base_url: Inference API base URL
            timeout: Request timeout in seconds
            custom_endpoint: Custom endpoint URL if using dedicated inference
        """
        self.api_token = api_token
        self.model_id = model_id
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.custom_endpoint = custom_endpoint
        
        # Common model categories and their capabilities
        self.model_categories = {
            "text-generation": {
                "task": "text-generation",
                "examples": ["gpt2", "microsoft/DialoGPT-large", "EleutherAI/gpt-j-6B"],
                "supports_streaming": True,
                "supports_chat": True
            },
            "text-classification": {
                "task": "text-classification",
                "examples": ["cardiffnlp/twitter-roberta-base-sentiment-latest"],
                "supports_streaming": False,
                "supports_chat": False
            },
            "feature-extraction": {
                "task": "feature-extraction",
                "examples": ["sentence-transformers/all-MiniLM-L6-v2"],
                "supports_streaming": False,
                "supports_chat": False
            },
            "question-answering": {
                "task": "question-answering",
                "examples": ["deepset/roberta-base-squad2"],
                "supports_streaming": False,
                "supports_chat": True
            },
            "image-classification": {
                "task": "image-classification",
                "examples": ["google/vit-base-patch16-224"],
                "supports_streaming": False,
                "supports_chat": False
            },
            "text-to-image": {
                "task": "text-to-image",
                "examples": ["runwayml/stable-diffusion-v1-5"],
                "supports_streaming": False,
                "supports_chat": False
            }
        }
        
        # HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
        )
        
        # Active models and endpoints
        self.active_models: Dict[str, HuggingFaceModel] = {}
        self.model_cache: Dict[str, Dict[str, Any]] = {}
        
        # Conversation history for chat models
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
        
        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "text_generations": 0,
            "embeddings_generated": 0,
            "classifications": 0,
            "custom_endpoint_calls": 0,
            "errors": 0
        }
        
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        model_id: Optional[str] = None,
        max_length: int = 100,
        temperature: float = 0.7,
        **kwargs
    ) -> HuggingFaceResponse:
        """
        Send message to HuggingFace model.
        
        Args:
            message: Input message
            conversation_id: Conversation identifier for context
            model_id: Model to use (overrides default)
            max_length: Maximum response length
            temperature: Response randomness
            **kwargs: Additional parameters
            
        Returns:
            HuggingFace response
        """
        try:
            model = model_id or self.model_id
            
            # Prepare input with conversation context
            input_text = self._prepare_input(message, conversation_id)
            
            # Build parameters
            parameters = {
                "max_length": max_length,
                "temperature": temperature,
                "do_sample": True,
                "return_full_text": False
            }
            parameters.update(kwargs)
            
            # Send request
            response = await self._send_generation_request(
                model=model,
                inputs=input_text,
                parameters=parameters
            )
            
            # Update conversation history
            if conversation_id and response.generated_text:
                self._update_conversation_history(conversation_id, message, response.generated_text)
                
            return response
            
        except Exception as e:
            logger.error(f"HuggingFace message send failed: {e}")
            self.usage_stats["errors"] += 1
            raise
            
    async def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        model_id: Optional[str] = None,
        normalize: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Text or list of texts to embed
            model_id: Model to use for embeddings
            normalize: Normalize embeddings
            
        Returns:
            List of embedding vectors
        """
        model = model_id or "sentence-transformers/all-MiniLM-L6-v2"
        
        if isinstance(texts, str):
            texts = [texts]
            
        try:
            response = await self._send_request(
                model=model,
                inputs=texts,
                task="feature-extraction"
            )
            
            self.usage_stats["embeddings_generated"] += len(texts)
            
            embeddings = response if isinstance(response, list) else [response]
            
            # Normalize if requested
            if normalize:
                embeddings = self._normalize_embeddings(embeddings)
                
            return embeddings
            
        except Exception as e:
            logger.error(f"HuggingFace embeddings failed: {e}")
            raise
            
    async def classify_text(
        self,
        text: str,
        model_id: Optional[str] = None,
        return_all_scores: bool = False
    ) -> Dict[str, Any]:
        """
        Classify text using classification model.
        
        Args:
            text: Text to classify
            model_id: Model to use for classification
            return_all_scores: Return scores for all labels
            
        Returns:
            Classification results
        """
        model = model_id or "cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        try:
            response = await self._send_request(
                model=model,
                inputs=text,
                task="text-classification"
            )
            
            self.usage_stats["classifications"] += 1
            
            # Parse classification response
            if isinstance(response, list) and response:
                classifications = response[0] if isinstance(response[0], list) else response
                
                result = {
                    "predictions": classifications,
                    "top_prediction": max(classifications, key=lambda x: x["score"]) if classifications else None
                }
                
                if not return_all_scores and result["top_prediction"]:
                    result["label"] = result["top_prediction"]["label"]
                    result["score"] = result["top_prediction"]["score"]
                    
                return result
            else:
                return {"predictions": [], "top_prediction": None}
                
        except Exception as e:
            logger.error(f"HuggingFace classification failed: {e}")
            raise
            
    async def answer_question(
        self,
        question: str,
        context: str,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer question based on context.
        
        Args:
            question: Question to answer
            context: Context containing the answer
            model_id: Model to use for QA
            
        Returns:
            Answer with confidence score
        """
        model = model_id or "deepset/roberta-base-squad2"
        
        try:
            response = await self._send_request(
                model=model,
                inputs={
                    "question": question,
                    "context": context
                },
                task="question-answering"
            )
            
            return {
                "answer": response.get("answer", ""),
                "score": response.get("score", 0.0),
                "start": response.get("start", 0),
                "end": response.get("end", 0),
                "question": question,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"HuggingFace QA failed: {e}")
            raise
            
    async def generate_image(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """
        Generate image from text prompt.
        
        Args:
            prompt: Text prompt for image generation
            model_id: Model to use for generation
            **kwargs: Additional parameters
            
        Returns:
            Generated image as bytes
        """
        model = model_id or "runwayml/stable-diffusion-v1-5"
        
        try:
            # Image generation returns binary data
            response = await self._send_raw_request(
                model=model,
                inputs=prompt,
                task="text-to-image",
                **kwargs
            )
            
            return response
            
        except Exception as e:
            logger.error(f"HuggingFace image generation failed: {e}")
            raise
            
    async def use_custom_endpoint(
        self,
        endpoint_url: str,
        inputs: Any,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use custom inference endpoint.
        
        Args:
            endpoint_url: Custom endpoint URL
            inputs: Input data
            parameters: Optional parameters
            
        Returns:
            Endpoint response
        """
        try:
            payload = {"inputs": inputs}
            if parameters:
                payload["parameters"] = parameters
                
            response = await self.client.post(
                endpoint_url,
                json=payload
            )
            response.raise_for_status()
            
            self.usage_stats["custom_endpoint_calls"] += 1
            return response.json()
            
        except Exception as e:
            logger.error(f"Custom endpoint call failed: {e}")
            raise
            
    async def _send_generation_request(
        self,
        model: str,
        inputs: str,
        parameters: Dict[str, Any]
    ) -> HuggingFaceResponse:
        """Send text generation request."""
        payload = {
            "inputs": inputs,
            "parameters": parameters
        }
        
        response_data = await self._send_request(model, payload, "text-generation")
        
        self.usage_stats["text_generations"] += 1
        
        # Parse generation response
        if isinstance(response_data, list) and response_data:
            generated_text = response_data[0].get("generated_text", "")
        else:
            generated_text = response_data.get("generated_text", "") if response_data else ""
            
        return HuggingFaceResponse(
            generated_text=generated_text,
            raw_response=response_data
        )
        
    async def _send_request(
        self,
        model: str,
        inputs: Any,
        task: str,
        **kwargs
    ) -> Any:
        """Send request to HuggingFace Inference API."""
        self.usage_stats["total_requests"] += 1
        
        # Use custom endpoint if available
        if self.custom_endpoint:
            return await self.use_custom_endpoint(
                self.custom_endpoint,
                inputs,
                kwargs.get("parameters")
            )
            
        # Build URL
        url = f"{self.base_url}/{model}"
        
        # Prepare payload
        if isinstance(inputs, dict):
            payload = inputs
        else:
            payload = {"inputs": inputs}
            
        if kwargs:
            payload.update(kwargs)
            
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                # Model is loading, wait and retry
                logger.info(f"Model {model} is loading, waiting...")
                await asyncio.sleep(10)
                return await self._send_request(model, inputs, task, **kwargs)
            else:
                logger.error(f"HuggingFace API HTTP error: {e.response.status_code} - {e.response.text}")
                raise
                
        except Exception as e:
            logger.error(f"HuggingFace API request failed: {e}")
            raise
            
    async def _send_raw_request(
        self,
        model: str,
        inputs: Any,
        task: str,
        **kwargs
    ) -> bytes:
        """Send request expecting binary response."""
        self.usage_stats["total_requests"] += 1
        
        url = f"{self.base_url}/{model}"
        payload = {"inputs": inputs}
        payload.update(kwargs)
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            logger.error(f"HuggingFace raw request failed: {e}")
            raise
            
    def _prepare_input(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """Prepare input with conversation context."""
        if not conversation_id or conversation_id not in self.conversations:
            return message
            
        # Build conversation context
        context_messages = self.conversations[conversation_id]
        context = ""
        
        for msg in context_messages[-5:]:  # Last 5 messages
            context += f"{msg['role']}: {msg['content']}\n"
            
        return f"{context}user: {message}\nassistant:"
        
    def _update_conversation_history(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str
    ):
        """Update conversation history."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            
        # Add user message
        self.conversations[conversation_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Add assistant message
        self.conversations[conversation_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Limit conversation history
        max_messages = 20
        if len(self.conversations[conversation_id]) > max_messages:
            self.conversations[conversation_id] = self.conversations[conversation_id][-max_messages:]
            
    def _normalize_embeddings(self, embeddings: List[List[float]]) -> List[List[float]]:
        """Normalize embedding vectors."""
        import math
        
        normalized = []
        for embedding in embeddings:
            # Calculate L2 norm
            norm = math.sqrt(sum(x * x for x in embedding))
            if norm > 0:
                normalized.append([x / norm for x in embedding])
            else:
                normalized.append(embedding)
                
        return normalized
        
    def switch_model(self, model_id: str):
        """Switch to different model."""
        self.model_id = model_id
        
    def add_custom_model(
        self,
        model_id: str,
        endpoint_url: str,
        task: str
    ):
        """Add custom model endpoint."""
        self.active_models[model_id] = HuggingFaceModel(
            model_id=model_id,
            task=task,
            endpoint_url=endpoint_url,
            is_custom=True
        )
        
    def get_model_info(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get model information."""
        model = model_id or self.model_id
        
        # Check if it's a known model category
        for category, info in self.model_categories.items():
            if any(example in model for example in info["examples"]):
                return {
                    "model_id": model,
                    "category": category,
                    **info
                }
                
        return {
            "model_id": model,
            "category": "unknown",
            "task": "unknown"
        }
        
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
