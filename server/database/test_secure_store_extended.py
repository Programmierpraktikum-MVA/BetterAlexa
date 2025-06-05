import unittest
import sqlite3
from secure_store import encrypt_and_store, retrieve_and_decrypt

DB_PATH = "key_value_store.db"

class TestSecureStore(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM sensitive_data")
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_encrypt_decrypt(self):
        user_id = "user1"
        key = "spotify_api_key"
        value = "secret_token_123"
        encrypt_and_store(user_id, {key: value}, self.conn, self.cursor)
        decrypted = retrieve_and_decrypt(user_id, key, self.conn, self.cursor)
        self.assertEqual(decrypted, value)

    def test_update_value(self):
        user_id = "user1"
        key = "spotify_api_key"
        value1 = "token_old"
        value2 = "token_new"
        encrypt_and_store(user_id, {key: value1}, self.conn, self.cursor)
        encrypt_and_store(user_id, {key: value2}, self.conn, self.cursor)
        decrypted = retrieve_and_decrypt(user_id, key, self.conn, self.cursor)
        self.assertEqual(decrypted, value2)

    def test_multiple_users(self):
        key = "discord_username"
        encrypt_and_store("user1", {key: "UserOne#1234"}, self.conn, self.cursor)
        encrypt_and_store("user2", {key: "discord_username"}, self.conn, self.cursor)
        decrypted1 = retrieve_and_decrypt("user1", key, self.conn, self.cursor)
        decrypted2 = retrieve_and_decrypt("user2", key, self.conn, self.cursor)
        self.assertEqual(decrypted1, "UserOne#1234")
        self.assertEqual(decrypted2, "discord_username")

if __name__ == '__main__':
    unittest.main()
