import sqlite3


def connect_db():
    conn = sqlite3.connect("pulse.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        joined_at TEXT,
        favorite_subject TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        goal TEXT,
        status TEXT,
        created_at TEXT,
        priority TEXT
    )
    """)

    conn.commit()
    conn.close()