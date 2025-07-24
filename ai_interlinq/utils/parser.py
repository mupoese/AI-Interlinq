# ai_interlinq/utils/parser.py
"""Message parsing utilities for AI-Interlinq."""

import json
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import asdict

from ..core.communication_protocol import Message, MessageHeader, MessagePayload, MessageType, Priority
from ..exceptions import ValidationError
from ..utils.logging import get_logger


class MessageParser:
    """Parses and validates AI-Interlinq messages."""
    
    def __init__(self):
        self.logger = get_logger("message_parser")
    
    def parse_json_message(self, json_str: str) -> Optional[Message]:
        """Parse JSON string into Message object."""
        try:
            data = json.loads(json_str)
            return self._dict_to_message(data)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Message parsing error: {e}")
            return None
    
    def parse_compact_message(self, compact_str: str) -> Optional[Message]:
        """Parse compact message format: TYPE|SENDER|RECIPIENT|COMMAND|DATA"""
        try:
            parts = compact_str.split('|', 4)
            if len(parts) != 5:
                return None
            
            msg_type, sender, recipient, command, data_str = parts
            
            # Parse data as JSON
            data = json.loads(data_str) if data_str else {}
            
            # Create message components
            header = MessageHeader(
                message_id=f"{sender}_{hash(compact_str)}",
                message_type=MessageType(msg_type.lower()),
                sender_id=sender,
                recipient_id=recipient,
                timestamp=0.0,  # Will be set by protocol
                priority=Priority.NORMAL,
                session_id="compact_session"
            )
            
            payload = MessagePayload(
                command=command,
                data=data
            )
            
            return Message(header=header, payload=payload)
            
        except Exception as e:
            self.logger.error(f"Compact message parsing error: {e}")
            return None
    
    def _dict_to_message(self, data: Dict[str, Any]) -> Message:
        """Convert dictionary to Message object."""
        header_data = data["header"]
        payload_data = data["payload"]
        
        header = MessageHeader(
            message_id=header_data["message_id"],
            message_type=MessageType(header_data["message_type"]),
            sender_id=header_data["sender_id"],
            recipient_id=header_data["recipient_id"],
            timestamp=header_data["timestamp"],
            priority=Priority(header_data["priority"]),
            session_id=header_data["session_id"],
            protocol_version=header_data.get("protocol_version", "1.0")
        )
        
        payload = MessagePayload(
            command=payload_data["command"],
            data=payload_data["data"],
            metadata=payload_data.get("metadata")
        )
        
        return Message(
            header=header,
            payload=payload,
            signature=data.get("signature")
        )
    
    def extract_commands(self, text: str) -> List[str]:
        """Extract command patterns from text."""
        # Pattern for command extraction: @command or /command
        command_pattern = r'[@/](\w+)'
        matches = re.findall(command_pattern, text)
        return matches
    
    def parse_key_value_pairs(self, text: str) -> Dict[str, str]:
        """Parse key=value pairs from text."""
        # Pattern for key=value pairs
        kv_pattern = r'(\w+)=(["\']?)([^"\'\\n]*)\2'
        matches = re.findall(kv_pattern, text)
        return {key: value for key, _, value in matches}
    
    def validate_message_format(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate message format against schema."""
        required_header_fields = [
            "message_id", "message_type", "sender_id", 
            "recipient_id", "timestamp", "priority", "session_id"
        ]
        
        required_payload_fields = ["command", "data"]
        
        # Check header
        if "header" not in data:
            return False, "Missing header"
        
        header = data["header"]
        for field in required_header_fields:
            if field not in header:
                return False, f"Missing header field: {field}"
        
        # Check payload
        if "payload" not in data:
            return False, "Missing payload"
        
        payload = data["payload"]
        for field in required_payload_fields:
            if field not in payload:
                return False, f"Missing payload field: {field}"
        
        # Validate enums
        try:
            MessageType(header["message_type"])
            Priority(header["priority"])
        except ValueError as e:
            return False, f"Invalid enum value: {e}"
        
        return True, "Valid"
