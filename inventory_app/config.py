"""Configurarea principalelor cai pentru aplicatia de gestiune."""
from __future__ import annotations

import os
from pathlib import Path


DATA_DIR = Path(os.environ.get("DASCOSTOCK_DATA_DIR", Path.home() / ".dascostock"))
"""Directorul folosit pentru a stoca datele persistente."""

DB_PATH = Path(os.environ.get("DASCOSTOCK_DB_PATH", DATA_DIR / "inventory.db"))
"""Calea catre baza de date SQLite in care este stocat inventarul."""


def ensure_data_dir() -> None:
    """Creeaza directorul de date daca nu exista deja."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
