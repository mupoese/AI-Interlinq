# File: /ai_interlinq/adapters/deepseek.py
# Directory: /ai_interlinq/adapters

"""
DeepSeek AI adapter for AI-Interlinq framework.
Provides integration with DeepSeek models optimized for coding and reasoning.
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
class DeepSeekMessage:
    """DeepSeek message structure."""
    role: str  # "system", "user", "assistant"
    content: str

@dataclass
class DeepSeekResponse:
    """DeepSeek API response structure."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

class DeepSeekAdapter:
    """
    DeepSeek AI integration adapter.
    
    Features:
    - DeepSeek Coder and Chat models
    - Code generation and analysis
    - Reasoning capabilities
    - Streaming responses
    - Function calling support
    - Conversation management
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-coder",
        max_tokens: int = 4096,
        temperature: float = 0.3,
        base_url: str = "https://api.deepseek.com/v1",
        timeout: int = 60
    ):
        """
        Initialize DeepSeek adapter.
        
        Args:
            api_key: DeepSeek API key
            model: DeepSeek model to use
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
            "deepseek-coder": {
                "max_tokens": 4096,
                "context_window": 16384,
                "coding": True,
                "reasoning": True,
                "languages": ["python", "javascript", "java", "c++", "go", "rust", "sql"]
            },
            "deepseek-chat": {
                "max_tokens": 4096,
                "context_window": 32768,
                "coding": True,
                "reasoning": True,
                "general_chat": True
            },
            "deepseek-math": {
                "max_tokens": 4096,
                "context_window": 16384,
                "mathematics": True,
                "reasoning": True,
                "problem_solving": True
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
        self.conversations: Dict[str, List[DeepSeekMessage]] = {}
        
        # Code analysis cache
        self.code_analysis_cache: Dict[str, Dict[str, Any]] = {}
        
        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens_prompt": 0,
            "total_tokens_completion": 0,
            "code_generations": 0,
            "code_analyses": 0,
            "errors": 0
        }
        
    async def send_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[DeepSeekResponse, AsyncGenerator[Dict[str, Any], None]]:
        """
        Send message to DeepSeek.
        
        Args:
            message: User message
            conversation_id: Conversation identifier for context
            system_prompt: System prompt for behavior
            stream: Enable streaming response
            **kwargs: Additional parameters
            
        Returns:
            DeepSeek response or streaming generator
        """
        try:
            # Prepare messages
            messages = self._prepare_messages(message, conversation_id, system_prompt)
            
            # Build request payload
            payload = {
                "model": self.model,
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "stream": stream
            }
            
            # Additional parameters
            for param in ["top_p", "frequency_penalty", "presence_penalty", "stop"]:
                if param in kwargs:
                    payload[param] = kwargs[param]
                    
            if stream:
                return self._stream_response(payload, conversation_id)
            else:
                return await self._send_request(payload, conversation_id)
                
        except Exception as e:
            logger.error(f"DeepSeek message send failed: {e}")
            self.usage_stats["errors"] += 1
            raise
            
    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        conversation_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate code using DeepSeek Coder.
        
        Args:
            prompt: Code generation prompt
            language: Programming language
            conversation_id: Conversation identifier
            **kwargs: Additional parameters
            
        Returns:
            Generated code and metadata
        """
        # Use coder model if not already
        original_model = self.model
        if "coder" not in self.model:
            self.model = "deepseek-coder"
            
        try:
            # Build coding-specific system prompt
            system_prompt = f"""You are an expert {language} programmer. Generate clean, efficient, and well-documented code.
Focus on:
1. Code quality and best practices
2. Clear variable names and structure
3. Appropriate comments and documentation
4. Error handling where applicable
5. Performance optimization

Language: {language}"""
            
            # Enhanced prompt for code generation
            enhanced_prompt = f"""Generate {language} code for the following requirement:

{prompt}

Please provide:
1. Complete, runnable code
2. Brief explanation of the approach
3. Any dependencies or setup required
4. Example usage if applicable"""
            
            response = await self.send_message(
                message=enhanced_prompt,
                conversation_id=conversation_id,
                system_prompt=system_prompt,
                **kwargs
            )
            
            self.usage_stats["code_generations"] += 1
            
            # Extract code from response
            content = response.choices[0]["message"]["content"]
            code_blocks = self._extract_code_blocks(content)
            
            return {
                "response": response,
                "code_blocks": code_blocks,
                "language": language,
                "explanation": content,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        finally:
            # Restore original model
            self.model = original_model
            
    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze code for issues, improvements, and optimization.
        
        Args:
            code: Code to analyze
            language: Programming language
            analysis_type: Type of analysis ("security", "performance", "style", "comprehensive")
            
        Returns:
            Code analysis results
        """
        # Check cache first
        cache_key = f"{hash(code)}_{language}_{analysis_type}"
        if cache_key in self.code_analysis_cache:
            return self.code_analysis_cache[cache_key]
            
        # Use coder model
        original_model = self.model
        if "coder" not in self.model:
            self.model = "deepseek-coder"
            
        try:
            analysis_prompts = {
                "security": "Analyze this code for security vulnerabilities, potential exploits, and security best practices.",
                "performance": "Analyze this code for performance issues, bottlenecks, and optimization opportunities.",
                "style": "Analyze this code for style issues, code quality, and adherence to best practices.",
                "comprehensive": "Provide a comprehensive analysis including security, performance, style, and general code quality."
            }
            
            system_prompt = f"""You are an expert code reviewer and static analysis tool for {language}.
Provide detailed analysis in the following format:

1. **Issues Found**: List any problems with severity levels
2. **Improvements**: Suggest specific improvements
3. **Security**: Security considerations and vulnerabilities
4. **Performance**: Performance implications and optimizations
5. **Best Practices**: Code quality and style recommendations
6. **Score**: Overall code quality score (1-10)

Be specific, actionable, and provide code examples where helpful."""

            prompt = f"""{analysis_prompts[analysis_type]}

```{language}
{code}
```

Please analyze this code according to the criteria above."""

            response = await self.generate_response(prompt, system_prompt=system_prompt)
            
            # Cache the result
            result = {
                "analysis": response,
                "timestamp": time.time(),
                "language": language,
                "analysis_type": analysis_type
            }
            self.code_analysis_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Code analysis error: {e}")
            return {
                "error": str(e),
                "timestamp": time.time(),
                "language": language,
                "analysis_type": analysis_type
            }
        finally:
            # Restore original model
            self.model = original_model
