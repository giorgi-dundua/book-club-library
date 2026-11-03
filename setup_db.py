import sqlite3
from database import db_path

connection = sqlite3.connect(db_path)

with open("schema.sql", "r", encoding="utf-8") as file:
    schema = file.read()

connection.executescript(schema)
connection.commit()

print("Database tables created successfully!")

tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("Tables found:", tables)

connection.close()