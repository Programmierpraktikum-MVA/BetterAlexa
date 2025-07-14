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
        return api_key
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
        cursor.execute(
            "SELECT encrypted_value, salt FROM sensitive_data WHERE user_id=? AND key=?", (user_id, key)
        )
        row = cursor.fetchone()

        if row:
            encrypted_value_db, salt_db = row
            try:
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

# ----- User Settings Management -----

def is_real_setting(key: str) -> bool:
    real_keys = {"speed"}
    return key.lower() in real_keys

def set_user_setting(user_id: str, key: str, value) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        if is_real_setting(key):
            try:
                real_value = float(value)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Wert für '{key}' muss eine Zahl sein.")
            cursor.execute("""
                INSERT INTO user_settings_real (user_id, key, value)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, key) DO UPDATE SET value=excluded.value
            """, (user_id, key, real_value))
        else:
            cursor.execute("""
                INSERT INTO user_settings_text (user_id, key, value)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, key) DO UPDATE SET value=excluded.value
            """, (user_id, key, str(value)))
        conn.commit()
    finally:
        conn.close()

def get_user_setting(user_id: str, key: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        if is_real_setting(key):
            cursor.execute("""
                SELECT value FROM user_settings_real WHERE user_id=? AND key=?
            """, (user_id, key))
            row = cursor.fetchone()
            if not row:
                return None
            return float(row[0])
        else:
            cursor.execute("""
                SELECT value FROM user_settings_text WHERE user_id=? AND key=?
            """, (user_id, key))
            row = cursor.fetchone()
            if not row:
                return None
            return row[0]
    finally:
        conn.close()

# ----- Zoom Link Management -----

def set_zoom_link(user_id: str, zoom_link: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users SET zoom_link = ? WHERE user_id = ?
        """, (zoom_link, user_id))
        conn.commit()
    finally:
        conn.close()

def get_zoom_link(user_id: str) -> str | None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT zoom_link FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
        return None
    finally:
        conn.close()

def get_user_id_by_meeting_id(meeting_id: str) -> str:
    """
    Return the `user_id` that is associated with a given Zoom `meeting_id`.

    The lookup scans the `zoom_link` column of the `users` table and searches
    for any link that contains the exact meeting ID.  Assumes one-to-one
    mapping between a meeting and a user.

    Raises
    ------
    fastapi.HTTPException
        404 – no user has a Zoom link with that meeting ID
    """
    if not meeting_id:
        raise HTTPException(status_code=400, detail="Meeting-ID muss angegeben werden")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT user_id FROM users WHERE zoom_link LIKE ?",
            (f"%{meeting_id}%",),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Meeting-ID nicht verknüpft")
        return str(row[0])
    finally:
        conn.close()
