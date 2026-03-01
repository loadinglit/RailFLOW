"""
RailFLOW — SQLite Database Layer.

Single local database for auth, users, and complaints.
Zero cloud dependency. Data persists permanently.
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "railflow.db"


def get_db() -> sqlite3.Connection:
    """Get a SQLite connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they don't exist. Called once on startup."""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = get_db()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role        TEXT NOT NULL DEFAULT 'passenger',
            language_pref TEXT NOT NULL DEFAULT 'en',
            phone       TEXT,
            address     TEXT,
            origin      TEXT,
            destination TEXT,
            line        TEXT,
            usual_train TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS complaints (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ref         TEXT UNIQUE NOT NULL,
            user_id     TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            severity    TEXT NOT NULL DEFAULT 'medium',
            status      TEXT NOT NULL DEFAULT 'filed',
            complaint_text TEXT,
            user_message TEXT,
            authority   TEXT,
            officer_note TEXT,
            date_filed  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_complaints_user ON complaints(user_id);
        CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
        CREATE INDEX IF NOT EXISTS idx_complaints_ref ON complaints(ref);
    """)

    conn.commit()

    # Safe migration: add new columns to existing DBs
    for table, col_def in [
        ("users", "phone TEXT"),
        ("users", "address TEXT"),
        ("complaints", "from_station TEXT"),
        ("complaints", "to_station TEXT"),
    ]:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
            conn.commit()
        except Exception:
            pass  # Column already exists

    conn.close()
    print(f"[db] SQLite initialized at {DB_PATH}")