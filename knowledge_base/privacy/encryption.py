#!/usr/bin/env python3
"""
Encryption Module for Knowledge Base System.

This module provides end-to-end encryption capabilities including:
1. Content encryption/decryption
2. Key management
3. Encrypted storage adapters
"""

import os
import json
import base64
import hashlib
import logging
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

# Import cryptography libraries
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key,
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

@dataclass
class EncryptionResult:
    """Result of an encryption operation."""
    ciphertext: bytes
    key_id: str
    algorithm: str
    metadata: Dict[str, Any]
    created_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'ciphertext': base64.b64encode(self.ciphertext).decode('utf-8'),
            'key_id': self.key_id,
            'algorithm': self.algorithm,
            'metadata': self.metadata,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptionResult':
        """Create from dictionary representation."""
        return cls(
            ciphertext=base64.b64decode(data['ciphertext']),
            key_id=data['key_id'],
            algorithm=data['algorithm'],
            metadata=data['metadata'],
            created_at=data['created_at']
        )


@dataclass
class EncryptionKey:
    """Represents an encryption key with metadata."""
    key_id: str
    key_data: bytes
    key_type: str
    algorithm: str
    created_at: str
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self, include_key_data: bool = False) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Args:
            include_key_data: Whether to include the actual key data
            
        Returns:
            Dictionary representation
        """
        result = {
            'key_id': self.key_id,
            'key_type': self.key_type,
            'algorithm': self.algorithm,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'metadata': self.metadata or {}
        }
        
        if include_key_data:
            result['key_data'] = base64.b64encode(self.key_data).decode('utf-8')
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptionKey':
        """Create from dictionary representation."""
        return cls(
            key_id=data['key_id'],
            key_data=base64.b64decode(data['key_data']) if 'key_data' in data else b'',
            key_type=data['key_type'],
            algorithm=data['algorithm'],
            created_at=data['created_at'],
            expires_at=data.get('expires_at'),
            metadata=data.get('metadata', {})
        )


class KeyManager:
    """
    Manages encryption keys for the system.
    
    This class handles:
    1. Key generation and storage
    2. Key retrieval and rotation
    3. Secure key management
    """
    
    def __init__(self, key_storage_path: str = None):
        """
        Initialize the key manager.
        
        Args:
            key_storage_path: Path to store encryption keys
        """
        # Set up storage location
        self.key_storage_path = key_storage_path
        if key_storage_path:
            self.key_storage_dir = Path(key_storage_path)
            self.key_storage_dir.mkdir(parents=True, exist_ok=True)
        else:
            # Default storage in user home directory
            self.key_storage_dir = Path.home() / ".kb_encryption" / "keys"
            self.key_storage_dir.mkdir(parents=True, exist_ok=True)
            
        # In-memory key cache
        self.key_cache: Dict[str, EncryptionKey] = {}
        
        # Master key used to protect content keys
        self.master_key: Optional[EncryptionKey] = None
        
        # Initialize master key
        self._initialize_master_key()
    
    def _initialize_master_key(self) -> None:
        """Initialize or load the master key."""
        master_key_path = self.key_storage_dir / "master_key.json"
        
        if master_key_path.exists():
            # Load existing master key
            try:
                with open(master_key_path, 'r') as f:
                    master_key_data = json.load(f)
                    
                self.master_key = EncryptionKey.from_dict(master_key_data)
                logger.info("Loaded existing master key")
                
            except Exception as e:
                logger.error(f"Error loading master key: {e}")
                self._generate_master_key()
        else:
            # Generate new master key
            self._generate_master_key()
    
    def _generate_master_key(self) -> None:
        """Generate a new master key."""
        # Generate a secure random key
        key_data = Fernet.generate_key()
        
        # Create master key with metadata
        self.master_key = EncryptionKey(
            key_id="master",
            key_data=key_data,
            key_type="symmetric",
            algorithm="Fernet",
            created_at=datetime.now().isoformat(),
            metadata={"purpose": "master_key", "version": "1.0"}
        )
        
        # Save the master key
        self._save_master_key()
        logger.info("Generated new master key")
    
    def _save_master_key(self) -> None:
        """Save the master key securely."""
        if not self.master_key:
            return
            
        master_key_path = self.key_storage_dir / "master_key.json"
        
        # Save to file
        try:
            with open(master_key_path, 'w') as f:
                json.dump(self.master_key.to_dict(include_key_data=True), f)
            
            # Set restricted permissions
            os.chmod(master_key_path, 0o600)  # Owner read/write only
            
        except Exception as e:
            logger.error(f"Error saving master key: {e}")
            raise RuntimeError(f"Failed to save master key: {e}")
    
    def generate_content_key(self, key_type: str = "symmetric", 
                           algorithm: str = "AES-GCM") -> EncryptionKey:
        """
        Generate a new content encryption key.
        
        Args:
            key_type: Type of key ("symmetric" or "asymmetric")
            algorithm: Encryption algorithm
            
        Returns:
            New encryption key
        """
        # Generate key ID
        key_id = f"content-{secrets.token_hex(8)}"
        
        key_data: bytes
        
        # Generate appropriate key based on type
        if key_type == "symmetric":
            if algorithm == "AES-GCM":
                # Generate 256-bit key for AES-GCM
                key_data = os.urandom(32)  # 256 bits
            elif algorithm == "Fernet":
                key_data = Fernet.generate_key()
            else:
                raise ValueError(f"Unsupported symmetric algorithm: {algorithm}")
                
        elif key_type == "asymmetric":
            if algorithm == "RSA":
                # Generate RSA key pair
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                # Serialize private key to PEM format
                key_data = private_key.private_bytes(
                    encoding=Encoding.PEM,
                    format=PrivateFormat.PKCS8,
                    encryption_algorithm=NoEncryption()
                )
            else:
                raise ValueError(f"Unsupported asymmetric algorithm: {algorithm}")
        else:
            raise ValueError(f"Unsupported key type: {key_type}")
        
        # Create key with metadata
        content_key = EncryptionKey(
            key_id=key_id,
            key_data=key_data,
            key_type=key_type,
            algorithm=algorithm,
            created_at=datetime.now().isoformat(),
            metadata={"purpose": "content_encryption"}
        )
        
        # Encrypt and save the key
        self._encrypt_and_save_key(content_key)
        
        # Add to cache
        self.key_cache[key_id] = content_key
        
        return content_key
    
    def _encrypt_and_save_key(self, key: EncryptionKey) -> None:
        """
        Encrypt a content key with the master key and save it.
        
        Args:
            key: Encryption key to encrypt and save
        """
        if not self.master_key:
            raise RuntimeError("Master key not initialized")
        
        # Create Fernet cipher with master key
        fernet = Fernet(self.master_key.key_data)
        
        # Encrypt the key data with master key
        encrypted_key_data = fernet.encrypt(key.key_data)
        
        # Create serializable key data (without the actual key)
        key_dict = key.to_dict(include_key_data=False)
        
        # Add encrypted key data
        key_dict['encrypted_key_data'] = base64.b64encode(encrypted_key_data).decode('utf-8')
        
        # Save to file
        key_path = self.key_storage_dir / f"{key.key_id}.json"
        with open(key_path, 'w') as f:
            json.dump(key_dict, f)
        
        # Set restricted permissions
        os.chmod(key_path, 0o600)  # Owner read/write only
    
    def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """
        Get an encryption key by ID.
        
        Args:
            key_id: ID of the key to retrieve
            
        Returns:
            Encryption key or None if not found
        """
        # Check cache first
        if key_id in self.key_cache:
            return self.key_cache[key_id]
        
        # Check if it's the master key
        if key_id == "master" and self.master_key:
            return self.master_key
        
        # Try to load from storage
        key_path = self.key_storage_dir / f"{key_id}.json"
        if not key_path.exists():
            return None
        
        try:
            # Load encrypted key data
            with open(key_path, 'r') as f:
                key_dict = json.load(f)
            
            # If there's no encrypted data
            if 'encrypted_key_data' not in key_dict:
                return None
            
            # Decrypt the key data with master key
            encrypted_key_data = base64.b64decode(key_dict['encrypted_key_data'])
            
            if not self.master_key:
                raise RuntimeError("Master key not available for decryption")
                
            fernet = Fernet(self.master_key.key_data)
            decrypted_key_data = fernet.decrypt(encrypted_key_data)
            
            # Create key object
            key = EncryptionKey(
                key_id=key_dict['key_id'],
                key_data=decrypted_key_data,
                key_type=key_dict['key_type'],
                algorithm=key_dict['algorithm'],
                created_at=key_dict['created_at'],
                expires_at=key_dict.get('expires_at'),
                metadata=key_dict.get('metadata', {})
            )
            
            # Add to cache
            self.key_cache[key_id] = key
            
            return key
            
        except Exception as e:
            logger.error(f"Error retrieving key {key_id}: {e}")
            return None
    
    def list_keys(self, include_metadata: bool = True) -> List[Dict[str, Any]]:
        """
        List all available keys (without sensitive data).
        
        Args:
            include_metadata: Whether to include key metadata
            
        Returns:
            List of key information dictionaries
        """
        keys = []
        
        # Add master key
        if self.master_key:
            keys.append(self.master_key.to_dict(include_key_data=False))
        
        # Add content keys from storage directory
        for key_file in self.key_storage_dir.glob("content-*.json"):
            try:
                with open(key_file, 'r') as f:
                    key_dict = json.load(f)
                
                # Remove encrypted key data
                if 'encrypted_key_data' in key_dict:
                    del key_dict['encrypted_key_data']
                
                # Remove metadata if not requested
                if not include_metadata and 'metadata' in key_dict:
                    del key_dict['metadata']
                
                keys.append(key_dict)
                
            except Exception as e:
                logger.error(f"Error reading key file {key_file}: {e}")
        
        return keys
    
    def rotate_master_key(self) -> None:
        """
        Rotate the master key and re-encrypt all content keys.
        
        This creates a new master key and re-encrypts all content keys with it.
        """
        # Remember old master key
        old_master_key = self.master_key
        
        # Generate new master key
        self._generate_master_key()
        
        # Get all content keys
        content_keys = []
        for key_file in self.key_storage_dir.glob("content-*.json"):
            key_id = key_file.stem
            
            # Skip already cached keys
            if key_id in self.key_cache:
                content_keys.append(self.key_cache[key_id])
                continue
                
            # Load and decrypt with old master key
            try:
                with open(key_file, 'r') as f:
                    key_dict = json.load(f)
                
                if 'encrypted_key_data' not in key_dict:
                    continue
                    
                encrypted_key_data = base64.b64decode(key_dict['encrypted_key_data'])
                
                if not old_master_key:
                    logger.error(f"Cannot decrypt key {key_id} without old master key")
                    continue
                    
                fernet = Fernet(old_master_key.key_data)
                decrypted_key_data = fernet.decrypt(encrypted_key_data)
                
                key = EncryptionKey(
                    key_id=key_dict['key_id'],
                    key_data=decrypted_key_data,
                    key_type=key_dict['key_type'],
                    algorithm=key_dict['algorithm'],
                    created_at=key_dict['created_at'],
                    expires_at=key_dict.get('expires_at'),
                    metadata=key_dict.get('metadata', {})
                )
                
                content_keys.append(key)
                
            except Exception as e:
                logger.error(f"Error rotating key {key_id}: {e}")
        
        # Re-encrypt all content keys with new master key
        for key in content_keys:
            self._encrypt_and_save_key(key)


class ContentEncryptionManager:
    """
    Manages encryption and decryption of content.
    
    This class provides:
    1. Content encryption using AES-GCM
    2. Content decryption with key lookup
    3. Search-friendly encryption methods
    """
    
    def __init__(self, key_manager: KeyManager):
        """
        Initialize the content encryption manager.
        
        Args:
            key_manager: Key manager instance
        """
        self.key_manager = key_manager
    
    def encrypt_content(self, content: Union[str, bytes], 
                       key_id: Optional[str] = None) -> EncryptionResult:
        """
        Encrypt content with AES-GCM.
        
        Args:
            content: Content to encrypt
            key_id: Key ID to use (generates new key if None)
            
        Returns:
            Encryption result
        """
        # Convert string to bytes if needed
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        
        # Get or generate key
        key = None
        if key_id:
            key = self.key_manager.get_key(key_id)
            
        # If no key provided or key not found, generate a new one
        if not key:
            key = self.key_manager.generate_content_key(
                key_type="symmetric", 
                algorithm="AES-GCM"
            )
            key_id = key.key_id
        
        # Encrypt the content
        if key.algorithm == "AES-GCM":
            # Generate a random nonce
            nonce = os.urandom(12)  # 96 bits as recommended for AES-GCM
            
            # Create AES-GCM cipher
            cipher = AESGCM(key.key_data)
            
            # Use empty associated data
            associated_data = b""
            
            # Encrypt the content
            ciphertext = cipher.encrypt(nonce, content_bytes, associated_data)
            
            # Prepend nonce to ciphertext for later decryption
            full_ciphertext = nonce + ciphertext
            
            return EncryptionResult(
                ciphertext=full_ciphertext,
                key_id=key.key_id,
                algorithm="AES-GCM",
                metadata={"content_type": "application/octet-stream"},
                created_at=datetime.now().isoformat()
            )
        elif key.algorithm == "Fernet":
            # Create Fernet cipher
            f = Fernet(key.key_data)
            
            # Encrypt the content
            ciphertext = f.encrypt(content_bytes)
            
            return EncryptionResult(
                ciphertext=ciphertext,
                key_id=key.key_id,
                algorithm="Fernet",
                metadata={"content_type": "application/octet-stream"},
                created_at=datetime.now().isoformat()
            )
        else:
            raise ValueError(f"Unsupported encryption algorithm: {key.algorithm}")
    
    def decrypt_content(self, encrypted_result: EncryptionResult) -> bytes:
        """
        Decrypt content using the appropriate key.
        
        Args:
            encrypted_result: Encryption result to decrypt
            
        Returns:
            Decrypted content as bytes
            
        Raises:
            ValueError: If key not found or decryption fails
        """
        # Get the encryption key
        key = self.key_manager.get_key(encrypted_result.key_id)
        if not key:
            raise ValueError(f"Encryption key not found: {encrypted_result.key_id}")
        
        # Decrypt based on algorithm
        if encrypted_result.algorithm == "AES-GCM":
            # Extract nonce (first 12 bytes)
            nonce = encrypted_result.ciphertext[:12]
            
            # Extract actual ciphertext
            ciphertext = encrypted_result.ciphertext[12:]
            
            # Create cipher
            cipher = AESGCM(key.key_data)
            
            # Decrypt
            try:
                plaintext = cipher.decrypt(nonce, ciphertext, b"")
                return plaintext
            except Exception as e:
                raise ValueError(f"Decryption failed: {e}")
                
        elif encrypted_result.algorithm == "Fernet":
            # Create cipher
            f = Fernet(key.key_data)
            
            # Decrypt
            try:
                plaintext = f.decrypt(encrypted_result.ciphertext)
                return plaintext
            except Exception as e:
                raise ValueError(f"Decryption failed: {e}")
                
        else:
            raise ValueError(f"Unsupported encryption algorithm: {encrypted_result.algorithm}")
    
    def encrypt_searchable_content(self, content: Dict[str, Any], 
                                  searchable_fields: List[str],
                                  key_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Encrypt content while keeping specified fields searchable.
        
        Args:
            content: Content dictionary to encrypt
            searchable_fields: Fields to keep searchable
            key_id: Key ID to use
            
        Returns:
            Dictionary with encrypted content and searchable fields
        """
        # Create a copy of the content dict
        result = {}
        
        # Split content into searchable and non-searchable parts
        searchable_content = {}
        non_searchable_content = {}
        
        for field, value in content.items():
            if field in searchable_fields:
                searchable_content[field] = value
            else:
                non_searchable_content[field] = value
        
        # Encrypt non-searchable content
        if non_searchable_content:
            encrypted_result = self.encrypt_content(
                json.dumps(non_searchable_content).encode('utf-8'),
                key_id
            )
            
            result["_encrypted"] = encrypted_result.to_dict()
            
        # Add searchable content as-is
        result.update(searchable_content)
        
        # Add metadata
        result["_metadata"] = {
            "has_encrypted_data": bool(non_searchable_content),
            "searchable_fields": searchable_fields,
            "encryption_type": "partial" if searchable_content else "full",
            "created_at": datetime.now().isoformat()
        }
        
        return result
    
    def decrypt_searchable_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt content that was encrypted with encrypt_searchable_content.
        
        Args:
            content: Dictionary with encrypted content
            
        Returns:
            Fully decrypted content dictionary
        """
        # Create result dict with searchable fields
        result = {}
        
        # Copy searchable fields
        for field, value in content.items():
            if field not in ["_encrypted", "_metadata"]:
                result[field] = value
        
        # Decrypt non-searchable content
        if "_encrypted" in content:
            encrypted_result = EncryptionResult.from_dict(content["_encrypted"])
            decrypted_bytes = self.decrypt_content(encrypted_result)
            decrypted_content = json.loads(decrypted_bytes.decode('utf-8'))
            
            # Add decrypted fields
            result.update(decrypted_content)
        
        return result


class EncryptedStorageAdapter:
    """
    Adapter for transparently encrypting data before storage.
    
    This class provides:
    1. Transparent encryption for storage operations
    2. File-level and content-level encryption
    3. Metadata protection
    """
    
    def __init__(self, encryption_manager: ContentEncryptionManager,
                base_storage_dir: str):
        """
        Initialize the encrypted storage adapter.
        
        Args:
            encryption_manager: Content encryption manager
            base_storage_dir: Base directory for storage
        """
        self.encryption_manager = encryption_manager
        self.base_storage_dir = Path(base_storage_dir)
        
        # Create directory if it doesn't exist
        self.base_storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Directory for storing encryption metadata
        self.metadata_dir = self.base_storage_dir / ".encryption"
        self.metadata_dir.mkdir(exist_ok=True)
    
    def save_encrypted_file(self, 
                          content: Union[str, bytes], 
                          filepath: Union[str, Path],
                          key_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Save content to a file with encryption.
        
        Args:
            content: Content to encrypt and save
            filepath: Path to save the file
            key_id: Key ID to use for encryption
            
        Returns:
            Dictionary with encryption metadata
        """
        # Convert string content to bytes if needed
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        
        # Get full file path
        if isinstance(filepath, str):
            filepath = Path(filepath)
            
        # Make path relative to base storage directory
        if not filepath.is_absolute():
            filepath = self.base_storage_dir / filepath
            
        # Make sure target directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Encrypt the content
        encrypted_result = self.encryption_manager.encrypt_content(
            content_bytes, 
            key_id
        )
        
        # Save encrypted content to file
        with open(filepath, 'wb') as f:
            f.write(encrypted_result.ciphertext)
        
        # Save encryption metadata
        relative_path = filepath.relative_to(self.base_storage_dir)
        meta_filepath = self.metadata_dir / f"{relative_path}.meta.json"
        
        # Create metadata directory
        meta_filepath.parent.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "filepath": str(relative_path),
            "key_id": encrypted_result.key_id,
            "algorithm": encrypted_result.algorithm,
            "created_at": encrypted_result.created_at
        }
        
        # Save metadata
        with open(meta_filepath, 'w') as f:
            json.dump(metadata, f)
            
        return metadata
    
    def read_encrypted_file(self, filepath: Union[str, Path]) -> bytes:
        """
        Read and decrypt an encrypted file.
        
        Args:
            filepath: Path to the encrypted file
            
        Returns:
            Decrypted content as bytes
            
        Raises:
            FileNotFoundError: If file or metadata not found
            ValueError: If decryption fails
        """
        # Get full file path
        if isinstance(filepath, str):
            filepath = Path(filepath)
            
        # Make path relative to base storage directory
        if not filepath.is_absolute():
            filepath = self.base_storage_dir / filepath
            
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
            
        # Get metadata file path
        relative_path = filepath.relative_to(self.base_storage_dir)
        meta_filepath = self.metadata_dir / f"{relative_path}.meta.json"
        
        if not meta_filepath.exists():
            raise FileNotFoundError(f"Encryption metadata not found for: {filepath}")
            
        # Read metadata
        with open(meta_filepath, 'r') as f:
            metadata = json.load(f)
            
        # Read encrypted content
        with open(filepath, 'rb') as f:
            encrypted_content = f.read()
            
        # Create encryption result
        encrypted_result = EncryptionResult(
            ciphertext=encrypted_content,
            key_id=metadata['key_id'],
            algorithm=metadata['algorithm'],
            metadata={},
            created_at=metadata['created_at']
        )
        
        # Decrypt the content
        return self.encryption_manager.decrypt_content(encrypted_result)
    
    def save_encrypted_json(self, 
                          data: Dict[str, Any], 
                          filepath: Union[str, Path],
                          searchable_fields: Optional[List[str]] = None,
                          key_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Save a JSON dictionary with encryption.
        
        Args:
            data: Dictionary to encrypt and save
            filepath: Path to save the file
            searchable_fields: Fields to keep searchable (None for full encryption)
            key_id: Key ID to use for encryption
            
        Returns:
            Dictionary with encryption metadata
        """
        # Process searchable fields
        if searchable_fields:
            # Encrypt with searchable fields preserved
            encrypted_data = self.encryption_manager.encrypt_searchable_content(
                data, searchable_fields, key_id
            )
            json_content = json.dumps(encrypted_data)
        else:
            # Encrypt entire content
            json_content = json.dumps(data)
            encrypted_data = {
                "_metadata": {
                    "has_encrypted_data": True,
                    "searchable_fields": [],
                    "encryption_type": "full",
                    "created_at": datetime.now().isoformat()
                }
            }
            
        # Save the file with appropriate extension
        if isinstance(filepath, str):
            filepath_str = filepath
        else:
            filepath_str = str(filepath)
            
        if not filepath_str.endswith('.json'):
            filepath_str += '.json'
            
        # Save the encrypted content
        metadata = self.save_encrypted_file(json_content, filepath_str, key_id)
        
        # Add searchable information to metadata
        metadata["searchable_fields"] = searchable_fields or []
        metadata["encryption_type"] = "partial" if searchable_fields else "full"
        
        return metadata
    
    def read_encrypted_json(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Read and decrypt an encrypted JSON file.
        
        Args:
            filepath: Path to the encrypted JSON file
            
        Returns:
            Decrypted JSON dictionary
            
        Raises:
            FileNotFoundError: If file or metadata not found
            ValueError: If decryption fails or content is not valid JSON
        """
        # Make sure file has .json extension
        if isinstance(filepath, str):
            filepath_str = filepath
        else:
            filepath_str = str(filepath)
            
        if not filepath_str.endswith('.json'):
            filepath_str += '.json'
            
        # Read and decrypt the file
        decrypted_content = self.read_encrypted_file(filepath_str)
        
        try:
            # Parse JSON content
            json_data = json.loads(decrypted_content.decode('utf-8'))
            
            # Check if this is partially encrypted content
            if isinstance(json_data, dict) and "_encrypted" in json_data:
                # Decrypt the partial content
                return self.encryption_manager.decrypt_searchable_content(json_data)
            else:
                # Return regular JSON
                return json_data
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON content: {e}")


# Initialize with default key manager for standalone usage
def get_default_encryption_manager() -> ContentEncryptionManager:
    """
    Get a default encryption manager instance.
    
    Returns:
        ContentEncryptionManager instance
    """
    key_manager = KeyManager()
    return ContentEncryptionManager(key_manager) 