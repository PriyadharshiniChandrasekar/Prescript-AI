"""
database.py
------------
Handles SQLite database connection, schema creation and all DB helper
functions used by the Flask app (app.py).

Tables:
    users          -> stores login/registration details
    prescriptions  -> stores each medicine a user is tracking
    intake_logs    -> stores taken/skipped/missed history for reminders
    chat_history   -> stores AI Assistant (Aura) chat messages
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "prescriptai.db")


def get_connection():
    """Return a new SQLite connection with rows accessible as dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they do not already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            medicine_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            times TEXT NOT NULL,          -- JSON list e.g. ["08:00","20:00"]
            start_date TEXT NOT NULL,
            end_date TEXT,
            notes TEXT,
            ai_summary TEXT,              -- AI generated analysis (Groq)
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS intake_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,       -- YYYY-MM-DD
            scheduled_time TEXT NOT NULL, -- HH:MM
            status TEXT NOT NULL,         -- taken / skipped / missed / pending
            logged_at TEXT,
            FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,           -- user / assistant
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


if __name__ == "__main__":
    init_db()
    print(f"Database initialised at {DB_PATH}")
