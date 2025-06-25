import sqlite3
import os
import hashlib
import binascii
import secrets
from fastapi import HTTPException
from .secure_store import encrypt_with_password, decrypt_with_password

DB_PATH = os.path.join(os.path.dirname(__file__), "key_value_store.db")

# ----- Password Hashing Helpers -----

def hash_password(password: str) -> str:
    """Generate a salted PBKDF2 SHA256 hash of the password."""
    salt = secrets.token_bytes(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return binascii.hexlify(salt + pwd_hash).decode()

def verify_password(stored_hash_hex: str, provided_password: str) -> bool:
    """Verify provided password against stored salted hash."""
    stored_hash = binascii.unhexlify(stored_hash_hex)
    salt = stored_hash[:16]
    stored_pwd_hash = stored_hash[16:]
    new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100000)
    return new_hash == stored_pwd_hash

# ----- API Key Generation -----

def generate_api_key() -> str:
    """Generate a secure random API key."""
    return secrets.token_hex(32)

# ----- User Management -----

def create_user(user_id: str, password: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        password_hash = hash_password(password)
        api_key = generate_api_key()
        cursor.execute(
            "INSERT INTO users (user_id, password_hash, api_key) VALUES (?, ?, ?)",
            (user_id, password_hash, api_key)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    finally:
        conn.close()

def login_user(user_id: str, password: str) -> str:
    """Validate username and password. Returns user_id if success."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="User not found")
        stored_hash = row[0]
        if not verify_password(stored_hash, password):
            raise HTTPException(status_code=401, detail="Incorrect password")
        return user_id
    finally:
        conn.close()

def authenticate_user(api_key: str) -> str:
    """Authenticate user by API key and return user_id."""
    if not api_key:
        raise HTTPException(status_code=401, detail="API-Key fehlt")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM users WHERE api_key = ?", (api_key,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Ungültiger API-Key")
        return str(row[0])
    finally:
        conn.close()

# ----- Sensitive Data Management -----

def set_sensitive_data(user_id: str, key: str, value: str, password: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Check if entry exists
        cursor.execute(
            "SELECT encrypted_value, salt FROM sensitive_data WHERE user_id=? AND key=?", (user_id, key)
        )
        row = cursor.fetchone()

        if row:
            encrypted_value_db, salt_db = row
            try:
                # Try decrypting to check password correctness
                _ = decrypt_with_password(password, encrypted_value_db, salt_db)
            except Exception:
                raise HTTPException(status_code=403, detail="Passwort stimmt nicht - Zugriff verweigert")

        encrypted_value, salt = encrypt_with_password(password, value)

        cursor.execute("""
            INSERT INTO sensitive_data (user_id, key, encrypted_value, salt)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, key) DO UPDATE SET
                encrypted_value=excluded.encrypted_value,
                salt=excluded.salt
        """, (user_id, key, encrypted_value, salt))
        conn.commit()
    finally:
        conn.close()

def get_sensitive_data(user_id: str, key: str, password: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT encrypted_value, salt FROM sensitive_data WHERE user_id=? AND key=?", (user_id, key)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Daten nicht gefunden")
        encrypted_value, salt = row
        return decrypt_with_password(password, encrypted_value, salt)
    finally:
        conn.close()
