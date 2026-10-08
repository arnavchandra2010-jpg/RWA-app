import os
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rwa.db")

conn = sqlite3.connect(DB_PATH)
conn.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, full_name TEXT, password_hash TEXT)"
)

username = input("Username: ").strip()
full_name = input("Full name: ").strip()
password = input("Password: ")

conn.execute(
    "INSERT INTO users (username, full_name, password_hash) VALUES (?, ?, ?)",
    (username, full_name, generate_password_hash(password)),
)
conn.commit()
conn.close()
print("RWA account created for", full_name)
