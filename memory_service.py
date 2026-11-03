
import sqlite3
from pathlib import Path

# Database is created automatically alongside this file
DB_PATH = Path(__file__).resolve().parent / "pulse_memory.db"

# Number of recent messages to send to Groq as context
MAX_CONTEXT_MESSAGES = 20


def get_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create the memory table if it doesn't exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_messages
            ON messages (user_id, id)
        """)


def add_message(user_id, role, content):
    """Save a user's message permanently."""
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO messages (user_id, role, content)
            VALUES (?, ?, ?)
        """, (str(user_id), role, content))


def get_memory(user_id, limit=MAX_CONTEXT_MESSAGES):
    """Retrieve the most recent messages for a specific user."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT role, content
            FROM messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (str(user_id), limit)).fetchall()

    # Reverse so messages appear in chronological order
    return [
        {"role": row["role"], "content": row["content"]}
        for row in reversed(rows)
    ]


def clear_memory(user_id):
    """Delete all stored conversation history for a user."""
    with get_connection() as conn:
        conn.execute("""
            DELETE FROM messages
            WHERE user_id = ?
        """, (str(user_id),))


# Initialize database when this module loads
initialize_database()
