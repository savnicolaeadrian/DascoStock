"""Operatiuni CRUD de nivel inferior pentru inventar."""
from __future__ import annotations

from typing import List, Optional

from .database import current_timestamp, get_connection


def create_item(
    name: str,
    category: Optional[str],
    unit: str,
    quantity: float,
    minimum_quantity: float,
    price: Optional[float],
) -> int:
    """Creeaza un produs si returneaza ID-ul acestuia."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO inventory (name, category, unit, quantity, minimum_quantity, price, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, category, unit, quantity, minimum_quantity, price, current_timestamp()),
        )
        connection.commit()
        return cursor.lastrowid


def update_quantity(item_id: int, change: float, reason: str, note: Optional[str]) -> None:
    """Modifica stocul unui produs si inregistreaza ajustarea."""
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT quantity FROM inventory WHERE id = ?",
            (item_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError("Produsul specificat nu exista")

        new_quantity = row["quantity"] + change
        if new_quantity < 0:
            raise ValueError("Nu exista suficient stoc pentru aceasta operatiune")

        connection.execute(
            """
            UPDATE inventory
               SET quantity = ?,
                   last_updated = ?
             WHERE id = ?
            """,
            (new_quantity, current_timestamp(), item_id),
        )
        connection.execute(
            """
            INSERT INTO adjustments (item_id, change, reason, note, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (item_id, change, reason, note, current_timestamp()),
        )
        connection.commit()


def set_minimum_quantity(item_id: int, minimum_quantity: float) -> None:
    """Seteaza pragul minim pentru un produs."""
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE inventory SET minimum_quantity = ?, last_updated = ? WHERE id = ?",
            (minimum_quantity, current_timestamp(), item_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("Produsul specificat nu exista")
        connection.commit()


def delete_item(item_id: int) -> None:
    """Sterge un produs si ajustarile sale."""
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        if cursor.rowcount == 0:
            raise ValueError("Produsul specificat nu exista")
        connection.execute("DELETE FROM adjustments WHERE item_id = ?", (item_id,))
        connection.commit()


def fetch_items(low_stock_only: bool = False, category: Optional[str] = None) -> List[dict]:
    """Returneaza produsele, optional doar cele cu stoc scazut."""
    query = "SELECT * FROM inventory"
    filters: List[str] = []
    params: List[object] = []

    if low_stock_only:
        filters.append("quantity <= minimum_quantity")
    if category:
        filters.append("category = ?")
        params.append(category)

    if filters:
        query += " WHERE " + " AND ".join(filters)
    query += " ORDER BY name COLLATE NOCASE"

    with get_connection() as connection:
        cursor = connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def fetch_adjustments(item_id: Optional[int] = None, limit: Optional[int] = None) -> List[dict]:
    """Returneaza istoricul ajustarilor."""
    query = (
        "SELECT adjustments.*, inventory.name "
        "FROM adjustments JOIN inventory ON adjustments.item_id = inventory.id"
    )
    params: List[object] = []
    if item_id is not None:
        query += " WHERE item_id = ?"
        params.append(item_id)

    query += " ORDER BY created_at DESC"
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    with get_connection() as connection:
        cursor = connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def item_exists(name: str) -> bool:
    """Verifica existenta unui produs dupa nume."""
    with get_connection() as connection:
        cursor = connection.execute("SELECT 1 FROM inventory WHERE name = ?", (name,))
        return cursor.fetchone() is not None


def fetch_item_by_id(item_id: int) -> Optional[dict]:
    """Returneaza detaliile produsului, daca exista."""
    with get_connection() as connection:
        cursor = connection.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
