from database import db_path, db_connect

conn = db_connect()

print("Database path:", db_path)

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("Tables found:", tables)

conn.close()