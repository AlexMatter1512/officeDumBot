import dotenv
import os
import sqlite3
import logging

log = logging.getLogger("dumb")
dotenv.load_dotenv()
DB_FILE_PATH = os.getenv("DB_FILE_PATH", "./mbarometro.db")
# Ensure the directory exists
os.makedirs(os.path.dirname(DB_FILE_PATH), exist_ok=True)


def _init_db():
    """Initialize the database with required tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS mbarometro (
        user TEXT PRIMARY KEY,
        value INTEGER NOT NULL DEFAULT 0
    )
    """
    )
    conn.commit()
    conn.close()


def increment(user: str, amount: int = 1):
    """
    Increment the value stored in the database by a specified amount.
    Args:
        user (str): The user to increment the value for.
        amount (int, optional): The amount to increment the value by. Defaults to 1.
    Returns:
        tuple: (user_value, total_value) - The new user value and total across all users.
    """
    try:
        _init_db()
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()

        # Insert or update the user's value
        cursor.execute(
            "INSERT INTO mbarometro (user, value) VALUES (?, ?) "
            "ON CONFLICT(user) DO UPDATE SET value = value + ?",
            (user, amount, amount),
        )
        conn.commit()

        # Get the user's new value
        cursor.execute("SELECT value FROM mbarometro WHERE user = ?", (user,))
        user_value = cursor.fetchone()[0]

        # Get the total value
        cursor.execute("SELECT SUM(value) FROM mbarometro")
        total = cursor.fetchone()[0] or 0

        conn.close()
        return user_value, total

    except Exception as e:
        log.error(e)
        return 0, 0


def get_all():
    """Retrieve all users and their values from the database as a list of dictionaries."""
    try:
        _init_db()
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user, value FROM mbarometro ORDER BY value DESC")
        rows = cursor.fetchall()
        conn.close()
        return [{"user": row[0], "value": row[1]} for row in rows]
    except Exception as e:
        log.error(e)
        return []

# Uncomment and modify to use SQLite
# def get_value(user: str = None) -> str:
#     """Retrieve the value from the database."""
#     try:
#         _init_db()
#         conn = sqlite3.connect(DB_FILE_PATH)
#         cursor = conn.cursor()
#
#         if user:
#             cursor.execute("SELECT value FROM mbarometro WHERE user = ?", (user,))
#             result = cursor.fetchone()
#             conn.close()
#             return result[0] if result else 0
#         else:
#             cursor.execute("SELECT user, value FROM mbarometro")
#             result = dict(cursor.fetchall())
#             conn.close()
#             return result
#     except Exception as e:
#         log.error(e)
#         return 0
