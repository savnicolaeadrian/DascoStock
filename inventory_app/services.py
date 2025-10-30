"""Logica de business pentru aplicatia de gestiune."""
from __future__ import annotations

from typing import List, Optional

from . import repository
from .database import initialize_database


def setup_database() -> None:
    """Creeaza tabelele necesare daca nu exista deja."""
    initialize_database()


def add_item(
    name: str,
    unit: str,
    quantity: float = 0,
    minimum_quantity: float = 0,
    category: Optional[str] = None,
    price: Optional[float] = None,
) -> int:
    """Adauga un nou produs in inventar."""
    if repository.item_exists(name):
        raise ValueError("Exista deja un produs cu acest nume")
    return repository.create_item(name, category, unit, quantity, minimum_quantity, price)


def receive_stock(item_id: int, quantity: float, note: Optional[str] = None) -> None:
    """Inregistreaza o intrare de marfa."""
    if quantity <= 0:
        raise ValueError("Cantitatea trebuie sa fie pozitiva")
    repository.update_quantity(item_id, quantity, reason="receptie", note=note)


def consume_stock(item_id: int, quantity: float, note: Optional[str] = None) -> None:
    """Inregistreaza consumul de stoc pentru productie sau vanzare."""
    if quantity <= 0:
        raise ValueError("Cantitatea trebuie sa fie pozitiva")
    repository.update_quantity(item_id, -quantity, reason="consum", note=note)


def adjust_stock(item_id: int, change: float, reason: str, note: Optional[str] = None) -> None:
    """Ajusteaza stocul manual, pentru pierderi sau corectii."""
    if change == 0:
        raise ValueError("Modificarea trebuie sa fie diferita de zero")
    repository.update_quantity(item_id, change, reason=reason, note=note)


def update_minimum(item_id: int, minimum_quantity: float) -> None:
    """Actualizeaza pragul de reaprovizionare."""
    if minimum_quantity < 0:
        raise ValueError("Pragul minim nu poate fi negativ")
    repository.set_minimum_quantity(item_id, minimum_quantity)


def remove_item(item_id: int) -> None:
    """Sterge un produs."""
    repository.delete_item(item_id)


def list_items(low_stock_only: bool = False, category: Optional[str] = None) -> List[dict]:
    """Returneaza lista produselor."""
    return repository.fetch_items(low_stock_only=low_stock_only, category=category)


def get_item(item_id: int) -> dict:
    """Returneaza produsul sau ridica exceptie daca nu exista."""
    item = repository.fetch_item_by_id(item_id)
    if item is None:
        raise ValueError("Produsul specificat nu exista")
    return item


def history(item_id: Optional[int] = None, limit: Optional[int] = None) -> List[dict]:
    """Returneaza istoricul ajustarilor."""
    return repository.fetch_adjustments(item_id=item_id, limit=limit)
