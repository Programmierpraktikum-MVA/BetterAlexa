import base64
import json
import sqlite3
from cryptography.fernet import Fernet

# Key ableiten (z.B. aus user_id, als Bytes-Padding)
def generate_key(user_id: str) -> bytes:
    # Einfachheit: user_id auf 32 Zeichen auffüllen/truncaten und base64 kodieren
    raw_key = (user_id * 32)[:32].encode()  
    return base64.urlsafe_b64encode(raw_key)

def encrypt(user_id: str, plaintext: str) -> str:
    key = generate_key(user_id)
    f = Fernet(key)
    encrypted = f.encrypt(plaintext.encode())
    return encrypted.decode()

def decrypt(user_id: str, ciphertext: str) -> str:
    key = generate_key(user_id)
    f = Fernet(key)
    decrypted = f.decrypt(ciphertext.encode())
    return decrypted.decode()

# Speichert Daten pro user_id und key (key ist der Name z.B. 'spotify_api_key')
def encrypt_and_store(user_id: str, data: dict, conn: sqlite3.Connection, cursor: sqlite3.Cursor):
    for key, value in data.items():
        encrypted_value = encrypt(user_id, value)
        cursor.execute("""
            INSERT INTO sensitive_data (user_id, key, encrypted_value) 
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, key) DO UPDATE SET encrypted_value=excluded.encrypted_value
        """, (user_id, key, encrypted_value))
    conn.commit()

def retrieve_and_decrypt(user_id: str, key: str, conn: sqlite3.Connection, cursor: sqlite3.Cursor) -> str:
    cursor.execute("""
        SELECT encrypted_value FROM sensitive_data WHERE user_id=? AND key=?
    """, (user_id, key))
    row = cursor.fetchone()
    if not row:
        raise ValueError("No data found")
    encrypted_value = row[0]
    return decrypt(user_id, encrypted_value)
