"""Encryption utilities for handling sensitive data in Tío Pepe system."""

from typing import Any, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os
from pathlib import Path

class EncryptionManager:
    """Manager class for handling data encryption and decryption."""

    def __init__(self):
        self.key_path = Path(__file__).parent.parent / 'config' / 'encryption_key'
        self._initialize_key()
        self.fernet = Fernet(self.load_key())

    def _initialize_key(self) -> None:
        """Initialize encryption key if it doesn't exist."""
        if not self.key_path.exists():
            key = Fernet.generate_key()
            self.key_path.parent.mkdir(exist_ok=True)
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)

    def load_key(self) -> bytes:
        """Load the encryption key."""
        with open(self.key_path, 'rb') as key_file:
            return key_file.read()

    def encrypt_data(self, data: Union[str, bytes]) -> str:
        """Encrypt data using Fernet symmetric encryption."""
        if isinstance(data, str):
            data = data.encode()
        return self.fernet.encrypt(data).decode()

    def decrypt_data(self, encrypted_data: Union[str, bytes]) -> str:
        """Decrypt Fernet-encrypted data."""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.fernet.decrypt(encrypted_data).decode()

    def generate_key_from_password(self, password: str, salt: bytes = None) -> bytes:
        """Generate encryption key from password using PBKDF2."""
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def hash_sensitive_data(self, data: str) -> str:
        """Create a one-way hash of sensitive data."""
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data.encode())
        return base64.b64encode(digest.finalize()).decode()

    def encrypt_file(self, file_path: Union[str, Path], output_path: Union[str, Path] = None) -> Path:
        """Encrypt a file using Fernet encryption."""
        file_path = Path(file_path)
        if output_path is None:
            output_path = file_path.parent / f"{file_path.name}.encrypted"
        else:
            output_path = Path(output_path)

        with open(file_path, 'rb') as f:
            data = f.read()

        encrypted_data = self.fernet.encrypt(data)

        with open(output_path, 'wb') as f:
            f.write(encrypted_data)

        return output_path

    def decrypt_file(self, file_path: Union[str, Path], output_path: Union[str, Path] = None) -> Path:
        """Decrypt a Fernet-encrypted file."""
        file_path = Path(file_path)
        if output_path is None:
            output_path = file_path.parent / file_path.name.replace('.encrypted', '')
        else:
            output_path = Path(output_path)

        with open(file_path, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = self.fernet.decrypt(encrypted_data)

        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

        return output_path