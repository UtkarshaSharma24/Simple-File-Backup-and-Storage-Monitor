"""database.py - SQLite helper functions for the backup history."""

import sqlite3
from datetime import datetime

DB_NAME = "backup_history.db"


def get_connection(db_path=DB_NAME):
    return sqlite3.connect(db_path)


def create_table(db_path=DB_NAME):
    """Create the history table if it does not exist."""
    conn = get_connection(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS backups (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            action        TEXT NOT NULL,      -- 'Backup' or 'Restore'
            file_name     TEXT NOT NULL,
            item_type     TEXT,               -- 'File' or 'Folder'
            source_path   TEXT,
            backup_path   TEXT,
            backup_date   TEXT NOT NULL,
            backup_time   TEXT NOT NULL,
            status        TEXT NOT NULL,      -- 'Success' or 'Failed'
            message       TEXT,
            size_bytes    INTEGER DEFAULT 0   -- size of the backup copy
        )
        """
    )
    # Old database file without size_bytes? Add the column.
    columns = [row[1] for row in conn.execute("PRAGMA table_info(backups)")]
    if "size_bytes" not in columns:
        conn.execute("ALTER TABLE backups ADD COLUMN size_bytes INTEGER DEFAULT 0")
    conn.commit()
    conn.close()


def add_record(action, file_name, item_type, source_path, backup_path,
               status, message="", db_path=DB_NAME, size_bytes=0):
    """Insert one row. Date and time are stored separately."""
    now = datetime.now()
    conn = get_connection(db_path)
    conn.execute(
        """
        INSERT INTO backups
        (action, file_name, item_type, source_path, backup_path,
         backup_date, backup_time, status, message, size_bytes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (action, file_name, item_type, source_path, backup_path,
         now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), status, message,
         size_bytes),
    )
    conn.commit()
    conn.close()


def get_history(db_path=DB_NAME):
    """Return all rows (newest first) as a list of dictionaries."""
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM backups ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_successful_backups(db_path=DB_NAME):
    """Return only successful backups (these can be restored)."""
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM backups WHERE action = 'Backup' AND status = 'Success' "
        "ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
