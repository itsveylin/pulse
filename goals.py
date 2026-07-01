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


def complete_goal(goal_id):

    conn = sqlite3.connect("pulse.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE goals
        SET status = 'completed'
        WHERE id = ?
    """, (goal_id,))

    conn.commit()
    conn.close()


def delete_goal(goal_id):

    conn = sqlite3.connect("pulse.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM goals
        WHERE id = ?
    """, (goal_id,))

    conn.commit()
    conn.close()


def get_completed_goals(user_id):

    conn = sqlite3.connect("pulse.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, goal, priority
        FROM goals
        WHERE user_id = ?
        AND status = 'completed'
    """, (user_id,))

    goals = cursor.fetchall()

    conn.close()

    return goals