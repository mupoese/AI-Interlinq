# ai_interlinq/utils/parser.py

"""
Message Parser for AI-Interlinq
Advanced parsing utilities for AI communication messages.
"""

import json
import re
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime

from ..core.communication_protocol import Message, MessageType, Priority


@dataclass
class ParseResult:
    """Result of message parsing operation."""
    success: bool
    message: Optional[Message] = None
    error: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class MessageParser:
    """Advanced message parser with validation and error handling."""
    
    def __init__(self):
        """Initialize message parser."""
        self._validation_rules = {}
        self._custom_parsers = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default validation rules."""
        self._validation_rules = {
            'message_id': {
                'required': True,
                'type': str,
                'pattern': r'^[a-zA-Z0-9_\-]+$',
                'max_length': 128
            },
            'sender_id': {
                'required': True,
                'type': str,
                'min_length': 1,
                'max_length': 64
            },
            'recipient_id': {
                'required': True,
                'type': str,
                'min_length': 1,
                'max_length': 64
            },
            'command': {
                'required': True,
                'type': str,
                'min_length': 1,
                'max_length': 32
            },
            'session_id': {
                'required': True,
                'type': str,
                'pattern': r'^[a-zA-Z0-9_\-]+$'
            }
        }
    
    def parse_message(self, raw_data: Union[str, bytes, Dict]) -> ParseResult:
        """
        Parse raw message data into a Message object.
        
        Args:
            raw_data: Raw message data (JSON string, bytes, or dict)
            
        Returns:
            ParseResult with success status and parsed message or error
        """
        try:
            # Handle different input types
            if isinstance(raw_data, bytes):
                raw_data = raw_data.decode('utf-8')
            
            if isinstance(raw_data, str):
                data = json.loads(raw_data)
            elif isinstance(raw_data, dict):
                data = raw_data
            else:
                return ParseResult(
                    success=False,
                    error=f"Unsupported data type: {type(raw_data)}"
                )
            
            # Validate structure
            validation_result = self._validate_structure(data)
            if not validation_result.success:
                return validation_result
            
            # Parse message components
            message = self._parse_message_components(data)
            if not message:
                return ParseResult(
                    success=False,
                    error="Failed to parse message components"
                )
            
            return ParseResult(
                success=True,
                message=message,
                warnings=validation_result.warnings
            )
            
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error=f"Invalid JSON: {str(e)}"
            )
        except Exception as e:
            return ParseResult(
                success=False,
                error=f"Parse error: {str(e)}"
            )
    
    def _validate_structure(self, data: Dict[str, Any]) -> ParseResult:
        """Validate message structure."""
        warnings = []
        
        # Check required top-level fields
        required_fields = ['header', 'payload']
        for field in required_fields:
            if field not in data:
                return ParseResult(
                    success=False,
                    error=f"Missing required field: {field}"
                )
        
        # Validate header fields
        header = data['header']
        for field, rules in self._validation_rules.items():
            if field in ['command']:  # Skip payload fields
                continue
                
            if rules.get('required', False) and field not in header:
                return ParseResult(
                    success=False,
                    error=f"Missing required header field: {field}"
                )
            
            if field in header:
                value = header[field]
                validation_error = self._validate_field(field, value, rules)
                if validation_error:
                    return ParseResult(success=False, error=validation_error)
        
        # Validate payload
        payload = data['payload']
        if 'command' not in payload:
            return ParseResult(
                success=False,
                error="Missing required payload field: command"
            )
        
        command_rules = self._validation_rules.get('command', {})
        validation_error = self._validate_field('command', payload['command'], command_rules)
        if validation_error:
            return ParseResult(success=False, error=validation_error)
        
        # Check for deprecated fields
        deprecated_fields = ['legacy_field', 'old_format']
        for field in deprecated_fields:
            if field in header or field in payload:
                warnings.append(f"Deprecated field found: {field}")
        
        return ParseResult(success=True, warnings=warnings)
    
    def _validate_field(self, field_name: str, value: Any, rules: Dict[str, Any]) -> Optional[str]:
        """Validate a single field against rules."""
        # Type validation
        expected_type = rules.get('type')
        if expected_type and not isinstance(value, expected_type):
            return f"Field {field_name} must be of type {expected_type.__name__}"
        
        # String validations
        if isinstance(value, str):
            min_length = rules.get('min_length')
            if min_length and len(value) < min_length:
                return f"Field {field_name} must be at least {min_length} characters"
            
            max_length = rules.get('max_length')
            if max_length and len(value) > max_length:
                return f"Field {field_name} must be at most {max_length} characters"
            
            pattern = rules.get('pattern')
            if pattern and not re.match(pattern, value):
                return f"Field {field_name} does not match required pattern"
        
        return None
    
    def _parse_message_components(self, data: Dict[str, Any]) -> Optional[Message]:
        """Parse message components into Message object."""
        try:
            from ..core.communication_protocol import MessageHeader, MessagePayload
            
            header_data = data['header']
            payload_data = data['payload']
            
            # Parse header
            header = MessageHeader(
                message_id=header_data['message_id'],
                message_type=MessageType(header_data['message_type']),
                sender_id=header_data['sender_id'],
                recipient_id=header_data['recipient_id'],
                timestamp=header_data['timestamp'],
                priority=Priority(header_data['priority']),
                session_id=header_data['session_id'],
                protocol_version=header_data.get('protocol_version', '1.0')
            )
            
            # Parse payload
            payload = MessagePayload(
                command=payload_data['command'],
                data=payload_data.get('data', {}),
                metadata=payload_data.get('metadata')
            )
            
            return Message(
                header=header,
                payload=payload,
                signature=data.get('signature')
            )
            
        except (KeyError, ValueError, TypeError) as e:
            return None
    
    def register_custom_parser(self, message_type: str, parser_func):
        """Register a custom parser for specific message types."""
        self._custom_parsers[message_type] = parser_func
    
    def add_validation_rule(self, field: str, rules: Dict[str, Any]):
        """Add custom validation rule for a field."""
        self._validation_rules[field] = rules
    
    def parse_batch(self, raw_messages: List[Union[str, Dict]]) -> List[ParseResult]:
        """Parse multiple messages in batch."""
        results = []
        for raw_message in raw_messages:
            result = self.parse_message(raw_message)
            results.append(result)
        return results
    
    def extract_metadata(self, message: Message) -> Dict[str, Any]:
        """Extract useful metadata from a message."""
        return {
            'message_age': datetime.now().timestamp() - message.header.timestamp,
            'message_size': len(str(message)),
            'has_metadata': message.payload.metadata is not None,
            'data_keys': list(message.payload.data.keys()) if message.payload.data else [],
            'priority_level': message.header.priority.name,
            'message_type': message.header.message_type.name
        }
