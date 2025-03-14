#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Encryption utilities for Persian Life Manager Application
"""

import os
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        """Initialize the encryption service"""
        # Try to load existing key or generate a new one
        self._encryption_key = self._load_or_generate_key()
        self._fernet = Fernet(self._encryption_key)
    
    def _load_or_generate_key(self):
        """Load existing encryption key or generate a new one
        
        Returns:
            bytes: The encryption key
        """
        key_path = os.path.join(os.path.expanduser("~"), '.persian_life_manager', '.encryption_key')
        
        try:
            # Check if key file exists
            if os.path.exists(key_path):
                with open(key_path, 'rb') as key_file:
                    key = key_file.read()
                    logger.info("Loaded existing encryption key")
                    return key
            
            # Generate a new key
            logger.info("Generating new encryption key")
            key = Fernet.generate_key()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(key_path), exist_ok=True)
            
            # Save the key
            with open(key_path, 'wb') as key_file:
                key_file.write(key)
                
            # Set secure permissions
            os.chmod(key_path, 0o600)  # Only owner can read/write
            
            return key
        except Exception as e:
            logger.error(f"Error handling encryption key: {str(e)}")
            # Fallback to a derived key if file operations fail
            return self._derive_key_from_machine()
    
    def _derive_key_from_machine(self):
        """Derive an encryption key from machine-specific information
        
        Returns:
            bytes: The derived encryption key
        """
        try:
            # Try to get some machine-specific data
            # Note: This is not ideal for security but serves as a fallback
            machine_id = ""
            
            # Try to read /etc/machine-id on Linux
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id", "r") as f:
                    machine_id = f.read().strip()
            
            # If that fails, use hostname
            if not machine_id:
                import socket
                machine_id = socket.gethostname()
            
            # If we still don't have an ID, use a fixed salt
            if not machine_id:
                machine_id = "PersianLifeManagerDefaultSalt"
            
            # Derive a key using PBKDF2
            salt = b"PersianLifeManagerSalt"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
            return key
        except Exception as e:
            logger.error(f"Error deriving encryption key: {str(e)}")
            # Final fallback to a fixed key (not secure, but better than crashing)
            return base64.urlsafe_b64encode(b"PersianLifeManagerFallbackEncryptionKey===")
    
    def encrypt(self, data):
        """Encrypt data
        
        Args:
            data (str): The data to encrypt
            
        Returns:
            bytes: The encrypted data
        """
        if not data:
            return b""
            
        try:
            return self._fernet.encrypt(data.encode())
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return b""
    
    def decrypt(self, encrypted_data):
        """Decrypt data
        
        Args:
            encrypted_data (bytes): The data to decrypt
            
        Returns:
            str: The decrypted data
        """
        if not encrypted_data:
            return ""
            
        try:
            return self._fernet.decrypt(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return ""
    
    def encrypt_password(self, password, master_password):
        """Encrypt a password with a user's master password
        
        Args:
            password (str): The password to encrypt
            master_password (str): The master password to use for encryption
            
        Returns:
            bytes: The encrypted password
        """
        try:
            # Derive a key from the master password
            salt = b"PersianLifeManagerPasswordSalt"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
            
            # Create a Fernet cipher with the derived key
            cipher = Fernet(key)
            
            # Encrypt the password
            return cipher.encrypt(password.encode())
        except Exception as e:
            logger.error(f"Password encryption error: {str(e)}")
            return b""
    
    def decrypt_password(self, encrypted_password, master_password):
        """Decrypt a password with a user's master password
        
        Args:
            encrypted_password (bytes): The encrypted password
            master_password (str): The master password used for encryption
            
        Returns:
            str: The decrypted password
        """
        try:
            # Derive the same key from the master password
            salt = b"PersianLifeManagerPasswordSalt"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
            
            # Create a Fernet cipher with the derived key
            cipher = Fernet(key)
            
            # Decrypt the password
            return cipher.decrypt(encrypted_password).decode()
        except Exception as e:
            logger.error(f"Password decryption error: {str(e)}")
            return ""
