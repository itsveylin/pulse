
import sqlite3
from datetime import datetime
from database import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def add_goal(
    user_id,
    goal,
    priority="medium",
    deadline=None,
    goal_type="general"
):
    """Save a new student goal."""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO goals (
            user_id,
            goal,
            status,
            created_at,
            priority,
            deadline,
            goal_type,
            progress,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(user_id),
        goal,
        "active",
        now,
        priority,
        deadline,
        goal_type,
        0,
        now
    ))

    goal_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return goal_id


def get_goals(user_id):
    """Retrieve active goals belonging to a student."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, goal, priority
        FROM goals
        WHERE user_id = ?
        AND status = 'active'
    """, (str(user_id),))

    goals = cursor.fetchall()
    conn.close()

    return goals


def get_goal_details(user_id):
    """Retrieve complete goal information."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            goal,
            priority,
            deadline,
            goal_type,
            progress,
            status
        FROM goals
        WHERE user_id = ?
    """, (str(user_id),))

    goals = cursor.fetchall()
    conn.close()

    return goals


def complete_goal(goal_id, user_id=None):
    """Mark a goal as completed."""

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_id is None:
        cursor.execute("""
            UPDATE goals
            SET status = 'completed',
                progress = 100,
                updated_at = ?
            WHERE id = ?
        """, (now, goal_id))
    else:
        cursor.execute("""
            UPDATE goals
            SET status = 'completed',
                progress = 100,
                updated_at = ?
            WHERE id = ?
            AND user_id = ?
        """, (now, goal_id, str(user_id)))

    conn.commit()
    conn.close()


def update_progress(goal_id, user_id, progress):
    """Update goal completion percentage."""

    progress = max(0, min(100, int(progress)))

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status = "completed" if progress == 100 else "active"

    cursor.execute("""
        UPDATE goals
        SET progress = ?,
            status = ?,
            updated_at = ?
        WHERE id = ?
        AND user_id = ?
    """, (
        progress,
        status,
        now,
        goal_id,
        str(user_id)
    ))

    conn.commit()
    conn.close()


def delete_goal(goal_id, user_id=None):
    """Delete a goal."""

    conn = get_connection()
    cursor = conn.cursor()

    if user_id is None:
        cursor.execute("""
            DELETE FROM goals
            WHERE id = ?
        """, (goal_id,))
    else:
        cursor.execute("""
            DELETE FROM goals
            WHERE id = ?
            AND user_id = ?
        """, (goal_id, str(user_id)))

    conn.commit()
    conn.close()


def get_completed_goals(user_id):
    """Retrieve completed goals belonging to a student."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, goal, priority
        FROM goals
        WHERE user_id = ?
        AND status = 'completed'
    """, (str(user_id),))

    goals = cursor.fetchall()
    conn.close()

    return goals
