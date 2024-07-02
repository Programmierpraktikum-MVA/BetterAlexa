import sqlite3
'''
# Connect to the SQLite database
conn = sqlite3.connect('key_value_store.db')
c = conn.cursor()

# Create table
c.execute(''CREATE TABLE IF NOT EXISTS store
             (key TEXT PRIMARY KEY, value TEXT))
'''
# Function to write to the store
def write_to_store(key, value, conn, c):
    with conn:
        c.execute("REPLACE INTO store (key, value) VALUES (?, ?)", (key, value))

# Function to read from the store
def read_from_store(key, c):
    c.execute("SELECT value FROM store WHERE key=?", (key,))
    result = c.fetchone()
    return result[0] if result else None


# Function to delete from the store
def delete_from_store(key, conn, c):
    with conn:
        c.execute("DELETE FROM store WHERE key=?", (key,))

'''
# Write to the store
write_to_store('key1', 'value1')

# Read from the store
print(read_from_store('key1'))  # Output: value1

# Update the store
write_to_store('key1', 'updated_value1')
#print(read_from_store('key1'))  # Output: updated_value1

# Delete from the store
delete_from_store('key1')
#print(read_from_store('key1'))  # Output: None

# Close the connection
conn.close()
'''