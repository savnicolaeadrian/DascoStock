"""Functionalitati comune pentru lucrul cu baza de date."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

from .config import DB_PATH, ensure_data_dir


SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT,
        unit TEXT NOT NULL,
        quantity REAL NOT NULL DEFAULT 0,
        minimum_quantity REAL NOT NULL DEFAULT 0,
        price REAL,
        last_updated TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS adjustments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        change REAL NOT NULL,
        reason TEXT NOT NULL,
        note TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(item_id) REFERENCES inventory(id) ON DELETE CASCADE
    );
    """,
]


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Returneaza o conexiune catre baza de date."""
    ensure_data_dir()
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.row_factory = sqlite3.Row
        yield connection
    finally:
        connection.close()


def initialize_database() -> None:
    """Initializeaza baza de date cu tabelele necesare."""
    with get_connection() as connection:
        for statement in SCHEMA:
            connection.execute(statement)
        connection.commit()


def current_timestamp() -> str:
    """Returneaza timestamp-ul ISO folosit la auditarea modificarilor."""
    return datetime.utcnow().replace(microsecond=0).isoformat()
