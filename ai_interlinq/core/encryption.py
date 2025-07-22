"""
Encryption Handler for AI-Interlinq
Provides secure encryption/decryption for AI communication.
"""

import hashlib
import secrets
from typing import Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class EncryptionHandler:
    """Handles encryption and decryption for AI communications."""
    
    def __init__(self, shared_key: Optional[str] = None):
        """
        Initialize encryption handler.
        
        Args:
            shared_key: Optional shared key for encryption
        """
        self._shared_key = shared_key
        self._fernet = None
        
        if shared_key:
            self._setup_encryption(shared_key)
    
    def _setup_encryption(self, shared_key: str) -> None:
        """Setup Fernet encryption with the shared key."""
        # Derive a proper key from the shared key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'ai_interlinq_salt',  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(shared_key.encode()))
        self._fernet = Fernet(key)
    
    def generate_shared_key(self) -> str:
        """Generate a new shared key for encryption."""
        return secrets.token_urlsafe(32)
    
    def set_shared_key(self, shared_key: str) -> None:
        """Set the shared encryption key."""
        self._shared_key = shared_key
        self._setup_encryption(shared_key)
    
    def encrypt_message(self, message: str) -> Tuple[bool, str]:
        """
        Encrypt a message using the shared key.
        
        Args:
            message: Plain text message to encrypt
            
        Returns:
            Tuple of (success, encrypted_message_or_error)
        """
        if not self._fernet:
            return False, "No encryption key set"
        
        try:
            encrypted = self._fernet.encrypt(message.encode())
            return True, base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            return False, f"Encryption failed: {str(e)}"
    
    def decrypt_message(self, encrypted_message: str) -> Tuple[bool, str]:
        """
        Decrypt a message using the shared key.
        
        Args:
            encrypted_message: Encrypted message to decrypt
            
        Returns:
            Tuple of (success, decrypted_message_or_error)
        """
        if not self._fernet:
            return False, "No encryption key set"
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_message.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return True, decrypted.decode()
        except Exception as e:
            return False, f"Decryption failed: {str(e)}"
    
    def generate_message_hash(self, message: str) -> str:
        """Generate a hash for message integrity verification."""
        return hashlib.sha256(message.encode()).hexdigest()
    
    def verify_message_hash(self, message: str, expected_hash: str) -> bool:
        """Verify message integrity using hash."""
        actual_hash = self.generate_message_hash(message)
        return actual_hash == expected_hash
    
    def create_secure_session_key(self, session_id: str) -> str:
        """Create a unique session key based on session ID and shared key."""
        if not self._shared_key:
            return secrets.token_urlsafe(32)
        
        combined = f"{self._shared_key}:{session_id}"
        return hashlib.sha256(combined.encode()).hexdigest()
