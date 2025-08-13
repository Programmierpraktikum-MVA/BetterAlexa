# Database Setup Guide

This guide explains how to set up and initialize the SQLite database used by this project.

---

## Overview

The project uses an **SQLite** database (`key_value_store.db`) to store:

- **Encrypted sensitive data** (per user)
- **User accounts** with hashed passwords and API keys
- **User settings** (separated into text and numeric/real values)
- **Zoom links** (unencrypted, per user)

Main files in this folder:

- `database_setup.py` – Creates and initializes the database schema.
- `database_wrapper.py` – Functions for reading/writing data (including encryption logic).
- `secure_store.py` – Handles password-based encryption/decryption of sensitive data.
- `key_value_store.db` – The SQLite database file (created after setup).

---

## Requirements

You need:

- **Python** ≥ 3.9
- **pip** (Python package manager)
- Required Python packages:
  
  ```bash
  pip install fastapi uvicorn cryptography

## Creating / Initializing the Database
- If the database file does not exist, you can create it by running:
    python database_setup.py
This will:
1. Create key_value_store.db in the database folder.
2. Create the following tables:
    sensitive_data – Stores encrypted values per user.
    user_id_mapping – Links BetterAlexa user IDs to TutorAI user IDs.
    users – Stores user credentials, API keys, and the zoom_link column.
    user_settings_text – Stores text-based settings.
    user_settings_real – Stores numeric settings (e.g., speed).
3. Add the zoom_link column to users if it doesn’t exist.
Important: Run this once on the server before starting the application.

## Sensitive Data
- Sensitive values are stored encrypted in the sensitive_data table.
- Encryption/Decryption is done in secure_store.py using the provided password at request time.
- Without the correct password, the encrypted values cannot be read, even with DB access.

## Accessing the Database in the Application
The FastAPI service interacts with the database only via database_wrapper.py:
- Set sensitive data:
    set_sensitive_data(user_id, key, value, password)
- Get sensitive data:
    get_sensitive_data(user_id, key, password)
- Set user setting (text or real):
    set_user_setting(user_id, "language", "en")
- Get user setting:
    get_user_setting(user_id, "language")
- Set/Get zoom link:
    set_zoom_link(user_id, "https://zoom.us/j/123456789")
    get_zoom_link(user_id)

## Security Notes
- Never commit key_value_store.db to public version control if it contains real data.
- Always back up the database before making structural changes.
- Keep user passwords hashed and API keys secret (handled automatically in code).

## Troubleshooting
- Error: no such table → Run python database_setup.py again to create tables.
- Encryption error → Ensure you are using the same password that was used to encrypt the value.
- Database not found → Make sure you are running the command from the database folder or that DB_PATH is correct in the scripts.