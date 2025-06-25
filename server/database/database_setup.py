import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "key_value_store.db")

def create_tables(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensitive_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        key TEXT NOT NULL,
        encrypted_value TEXT NOT NULL,
        salt TEXT NOT NULL,
        UNIQUE(user_id, key)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_id_mapping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        betteralexa_user_id TEXT UNIQUE NOT NULL,
        tutoraI_user_id TEXT UNIQUE NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        api_key TEXT UNIQUE NOT NULL
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Datenbanktabellen erstellt (falls nicht vorhanden).")
