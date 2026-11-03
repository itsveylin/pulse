
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "pulse.db"


def connect_db():
    """Initialize database and safely migrate existing tables."""

    conn = sqlite3.connect(DB_PATH)
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

    # Check existing columns before migration
    cursor.execute("PRAGMA table_info(goals)")
    existing_columns = {
        column[1] for column in cursor.fetchall()
    }

    migrations = {
        "deadline": "TEXT",
        "goal_type": "TEXT DEFAULT 'general'",
        "progress": "INTEGER DEFAULT 0",
        "updated_at": "TEXT"
    }

    for column, definition in migrations.items():
        if column not in existing_columns:
            cursor.execute(
                f"ALTER TABLE goals ADD COLUMN {column} {definition}"
            )

    conn.commit()
    conn.close()
