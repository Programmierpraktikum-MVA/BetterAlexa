import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Leitet einen 32-Byte Schlüssel aus Passwort + Salt mittels PBKDF2 ab.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)

def encrypt_with_password(password: str, plaintext: str) -> (str, str):  # type: ignore
    """
    Verschlüsselt plaintext mit Schlüssel aus password + zufälligem Salt.
    Gibt Tuple (encrypted_string, base64_salt) zurück.
    """
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(plaintext.encode())
    return encrypted.decode(), base64.b64encode(salt).decode()

def decrypt_with_password(password: str, encrypted_text: str, salt_b64: str) -> str:
    """
    Entschlüsselt encrypted_text mit Schlüssel aus password + Salt.
    Salt wird als Base64 erwartet.
    """
    salt = base64.b64decode(salt_b64)
    key = derive_key(password, salt)
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_text.encode())
    return decrypted.decode()
