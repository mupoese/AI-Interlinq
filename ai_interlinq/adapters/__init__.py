
# File: /ai_interlinq/adapters/__init__.py
# Directory: /ai_interlinq/adapters

"""
AI platform adapters for AI-Interlinq communication framework.
"""

from .anthropic import AnthropicAdapter
from .openai import OpenAIAdapter
from .ollama import OllamaAdapter
from .deepseek import DeepSeekAdapter
from .gemini import GeminiAdapter
from .grok import GrokAdapter
from .huggingface import HuggingFaceAdapter

__all__ = [
    "AnthropicAdapter",
    "OpenAIAdapter", 
    "OllamaAdapter",
    "DeepSeekAdapter",
    "GeminiAdapter",
    "GrokAdapter",
    "HuggingFaceAdapter"
]
