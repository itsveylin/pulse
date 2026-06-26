import sqlite3
from datetime import datetime


def add_goal(user_id, goal, priority):

    conn = sqlite3.connect("pulse.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO goals (
        user_id,
        goal,
        status,
        created_at,
        priority
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        goal,
        "active",
        datetime.now().strftime("%Y-%m-%d"),
        priority
    ))

    conn.commit()
    conn.close()


def get_goals(user_id):

    conn = sqlite3.connect("pulse.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, goal, priority
    FROM goals
    WHERE user_id = ?
    AND status = 'active'
    """, (user_id,))

    goals = cursor.fetchall()

    conn.close()

    return goals