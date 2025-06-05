import sqlite3
from secure_store import encrypt, decrypt  # your encryption functions


def test_encryption_decryption():
    user_id = "user123"
    plaintext = "my_secret_data"

    encrypted = encrypt(user_id, plaintext)
    print("Encrypted:", encrypted)

    decrypted = decrypt(user_id, encrypted)
    print("Decrypted:", decrypted)

    assert decrypted == plaintext, "Decryption failed!"

def test_database_storage():
    db_path = "key_value_store.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Setup table if not exists (adjust if your DB schema is different)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensitive_data (
        user_id TEXT NOT NULL,
        key TEXT NOT NULL,
        encrypted_value TEXT NOT NULL,
        PRIMARY KEY (user_id, key)
    )
    ''')
    conn.commit()

    user_id = "user123"
    key = "spotify_api_key"
    value = "super_secret_spotify_token"

    # Encrypt value
    encrypted_value = encrypt(user_id, value)

    # Insert or update
    cursor.execute("""
        INSERT INTO sensitive_data (user_id, key, encrypted_value) VALUES (?, ?, ?)
        ON CONFLICT(user_id, key) DO UPDATE SET encrypted_value=excluded.encrypted_value
    """, (user_id, key, encrypted_value))
    conn.commit()

    # Retrieve from DB
    cursor.execute("SELECT encrypted_value FROM sensitive_data WHERE user_id=? AND key=?", (user_id, key))
    row = cursor.fetchone()
    if row:
        decrypted_value = decrypt(user_id, row[0])
        print("Decrypted value from DB:", decrypted_value)
    else:
        print("No data found")

    conn.close()

if __name__ == "__main__":
    test_encryption_decryption()
    test_database_storage()
