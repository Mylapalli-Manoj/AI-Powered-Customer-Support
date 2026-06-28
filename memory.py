"""
memory.py
---------
Handles SQLite-based memory for storing and retrieving customer
conversation history.

Task 7: Implement SQLite-based memory to store and retrieve
customer conversation history.
"""

import sqlite3
from datetime import datetime

DB_PATH = "memory.db"


def init_db():
    """Creates the conversations table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            query TEXT NOT NULL,
            intent TEXT,
            response TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_interaction(customer_name: str, query: str, intent: str, response: str):
    """Saves one customer interaction into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO conversations (customer_name, query, intent, response, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (customer_name, query, intent, response, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_history(customer_name: str, limit: int = 5) -> str:
    """
    Retrieves the most recent past interactions for a given customer.
    Returns a formatted string summary, or an empty string if none found.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT query, intent, response, timestamp FROM conversations
        WHERE customer_name = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (customer_name, limit)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return ""

    history_lines = []
    for query, intent, response, timestamp in rows:
        history_lines.append(
            f"- On {timestamp}, customer asked: \"{query}\" "
            f"(Category: {intent}). We replied: \"{response}\""
        )

    return "\n".join(history_lines)