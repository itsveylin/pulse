
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "pulse.db"


def check_database():

    if not DB_PATH.exists():
        print("Database file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n========== PULSE DATABASE CHECK ==========\n")

    # Check tables
    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """)

    tables = cursor.fetchall()

    print("TABLES FOUND:")

    for table in tables:
        print(f"- {table[0]}")

    # Check columns in each table
    for (table_name,) in tables:

        print(f"\nCOLUMNS IN {table_name}:")

        cursor.execute(
            f"PRAGMA table_info({table_name})"
        )

        columns = cursor.fetchall()

        for column in columns:
            print(
                f"  {column[1]} | {column[2]}"
            )

    # Check existing goals
    print("\n========== EXISTING GOALS ==========\n")

    cursor.execute("""
        SELECT id, user_id, goal, status,
               priority, deadline, goal_type, progress
        FROM goals
    """)

    goals = cursor.fetchall()

    if goals:
        for goal in goals:
            print(f"ID: {goal[0]}")
            print(f"User ID: {goal[1]}")
            print(f"Goal: {goal[2]}")
            print(f"Status: {goal[3]}")
            print(f"Priority: {goal[4]}")
            print(f"Deadline: {goal[5]}")
            print(f"Type: {goal[6]}")
            print(f"Progress: {goal[7]}%")
            print("-" * 35)
    else:
        print("No goals found.")

    conn.close()

    print("\nDatabase check completed.")


if __name__ == "__main__":
    check_database()
