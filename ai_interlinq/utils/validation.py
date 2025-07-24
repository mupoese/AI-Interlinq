### ai_interlinq/utils/validation.py

"""Validation utilities for AI-Interlinq."""

import re
from typing import Any, Dict, List, Tuple, Optional
from ..exceptions import ValidationError


class Validator:
    """General purpose validator."""
    
    @staticmethod
    def validate_agent_id(agent_id: str) -> bool:
        """Validate agent ID format."""
        if not agent_id:
            return False
        
        # Agent ID should be alphanumeric with underscores/hyphens
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, agent_id)) and len(agent_id) <= 64
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """Validate session ID format."""
        if not session_id:
            return False
        
        # Session ID should be alphanumeric with underscores/hyphens
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, session_id)) and len(session_id) <= 128
    
    @staticmethod
    def validate_message_size(data: bytes, max_size: int = 1024 * 1024) -> bool:
        """Validate message size."""
        return len(data) <= max_size
    
    @staticmethod
    def validate_token_format(token: str) -> bool:
        """Validate token format."""
        if not token:
            return False
        
        # Token should be base64-like characters
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, token)) and 32 <= len(token) <= 256
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            raise ValidationError("Input must be a string")
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_payload(payload: Dict[str, Any], max_depth: int = 10) -> bool:
        """Validate payload structure and depth."""
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                return False
            
            if isinstance(obj, dict):
                return all(check_depth(v, current_depth + 1) for v in obj.values())
            elif isinstance(obj, list):
                return all(check_depth(item, current_depth + 1) for item in obj)
            
            return True
        
        return check_depth(payload)


def validate_message_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate message data."""
    validator = Validator()
    
    # Check required fields
    required_fields = ['command', 'data']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate command
    command = data.get('command', '')
    if not isinstance(command, str) or not command.strip():
        return False, "Command must be a non-empty string"
    
    if len(command) > 64:
        return False, "Command too long (max 64 characters)"
    
    # Validate data payload
    payload = data.get('data', {})
    if not isinstance(payload, dict):
        return False, "Data must be a dictionary"
    
    if not validator.validate_payload(payload):
        return False, "Data structure too deep or invalid"
    
    return True, None
