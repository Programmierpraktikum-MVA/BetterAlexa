import sqlite3
import os
from fastapi import HTTPException
from .secure_store import encrypt_with_password, decrypt_with_password

DB_PATH = os.path.join(os.path.dirname(__file__), "key_value_store.db")

def authenticate_user(api_key: str) -> str:
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

def set_sensitive_data(user_id: str, key: str, value: str, password: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
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
        cursor.execute("""
            SELECT encrypted_value, salt FROM sensitive_data WHERE user_id=? AND key=?
        """, (user_id, key))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Daten nicht gefunden")
        encrypted_value, salt = row
        return decrypt_with_password(password, encrypted_value, salt)
    finally:
        conn.close()
