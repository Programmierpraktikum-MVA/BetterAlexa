from .database_wrapper import create_user, set_sensitive_data, get_sensitive_data

# User anlegen
create_user("test", "abc123")

# Daten speichern
set_sensitive_data("test", "foo", "bar", "abc123")

# Daten abrufen
wert = get_sensitive_data("test", "foo", "abc123")
print("Gespeicherter Wert:", wert)

