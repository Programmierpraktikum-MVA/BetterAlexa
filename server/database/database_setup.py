# database_setup.py
import sqlite3

def create_tables(db_path='key_value_store.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensitive_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        key TEXT NOT NULL,
        encrypted_value BLOB NOT NULL,
        UNIQUE(user_id, key)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_id_mapping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        betteralexa_user_id TEXT NOT NULL,
        tutoraI_user_id TEXT NOT NULL,
        UNIQUE(betteralexa_user_id, tutoraI_user_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("Datenbank-Tabellen erstellt (falls nicht vorhanden).")

if __name__ == "__main__":
    create_tables()
