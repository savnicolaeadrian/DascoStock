"""Interfata din linia de comanda pentru gestiunea stocului."""
from __future__ import annotations

import argparse
import sys
from typing import Iterable, List, Optional

from . import services


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dascostock",
        description="Aplicatie simpla pentru gestiunea stocului unui restaurant.",
    )
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="initializeaza baza de date inainte de executarea comenzii",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add-item", help="adauga un produs nou")
    add_parser.add_argument("name", help="numele produsului")
    add_parser.add_argument("unit", help="unitatea de masura (ex. kg, litri, bucati)")
    add_parser.add_argument("--quantity", type=float, default=0.0, help="stocul initial")
    add_parser.add_argument("--minimum", type=float, default=0.0, help="pragul minim")
    add_parser.add_argument("--category", help="categoria produsului")
    add_parser.add_argument("--price", type=float, help="pretul unitar")

    list_parser = subparsers.add_parser("list", help="afiseaza produsele din inventar")
    list_parser.add_argument(
        "--low-stock",
        action="store_true",
        help="afiseaza doar produsele cu stoc sub pragul minim",
    )
    list_parser.add_argument("--category", help="filtrare dupa categorie")

    receive_parser = subparsers.add_parser("receive", help="inregistreaza o receptie")
    receive_parser.add_argument("item_id", type=int, help="ID-ul produsului")
    receive_parser.add_argument("quantity", type=float, help="cantitatea receptionata")
    receive_parser.add_argument("--note", help="observatii")

    consume_parser = subparsers.add_parser("consume", help="inregistreaza un consum")
    consume_parser.add_argument("item_id", type=int, help="ID-ul produsului")
    consume_parser.add_argument("quantity", type=float, help="cantitatea consumata")
    consume_parser.add_argument("--note", help="observatii")

    adjust_parser = subparsers.add_parser(
        "adjust", help="ajusteaza manual stocul (pierderi, inventar etc.)"
    )
    adjust_parser.add_argument("item_id", type=int, help="ID-ul produsului")
    adjust_parser.add_argument("change", type=float, help="valoarea ajustarii, poate fi negativa")
    adjust_parser.add_argument("reason", help="motivul ajustarii")
    adjust_parser.add_argument("--note", help="observatii suplimentare")

    minimum_parser = subparsers.add_parser(
        "set-minimum", help="stabileste pragul minim pentru un produs"
    )
    minimum_parser.add_argument("item_id", type=int, help="ID-ul produsului")
    minimum_parser.add_argument("minimum", type=float, help="pragul minim dorit")

    delete_parser = subparsers.add_parser("remove", help="sterge un produs")
    delete_parser.add_argument("item_id", type=int, help="ID-ul produsului")

    history_parser = subparsers.add_parser("history", help="afiseaza istoricul ajustarilor")
    history_parser.add_argument("--item-id", type=int, help="limiteaza istoricul la un produs")
    history_parser.add_argument("--limit", type=int, help="numarul maxim de inregistrari")

    return parser


def format_table(rows: Iterable[dict], headers: List[str]) -> str:
    """Construieste un tabel ASCII simplu."""
    rows = list(rows)
    if not rows:
        return "<niciun rezultat>"

    columns = {header: [str(header)] for header in headers}
    for row in rows:
        for header in headers:
            columns[header].append(str(row.get(header, "")))

    widths = {header: max(len(value) for value in values) for header, values in columns.items()}
    lines = []
    header_line = " | ".join(header.ljust(widths[header]) for header in headers)
    separator = "-+-".join("-" * widths[header] for header in headers)
    lines.append(header_line)
    lines.append(separator)

    for row in rows:
        line = " | ".join(str(row.get(header, "")).ljust(widths[header]) for header in headers)
        lines.append(line)
    return "\n".join(lines)


def handle_add_item(args: argparse.Namespace) -> None:
    item_id = services.add_item(
        name=args.name,
        unit=args.unit,
        quantity=args.quantity,
        minimum_quantity=args.minimum,
        category=args.category,
        price=args.price,
    )
    print(f"Produs creat cu ID {item_id}")


def handle_list(args: argparse.Namespace) -> None:
    items = services.list_items(low_stock_only=args.low_stock, category=args.category)
    headers = ["id", "name", "category", "unit", "quantity", "minimum_quantity", "price"]
    print(format_table(items, headers))


def handle_receive(args: argparse.Namespace) -> None:
    services.receive_stock(args.item_id, args.quantity, note=args.note)
    print("Receptie inregistrata cu succes")


def handle_consume(args: argparse.Namespace) -> None:
    services.consume_stock(args.item_id, args.quantity, note=args.note)
    print("Consum inregistrat cu succes")


def handle_adjust(args: argparse.Namespace) -> None:
    services.adjust_stock(args.item_id, args.change, reason=args.reason, note=args.note)
    print("Ajustare salvata")


def handle_minimum(args: argparse.Namespace) -> None:
    services.update_minimum(args.item_id, args.minimum)
    print("Pragul minim a fost actualizat")


def handle_remove(args: argparse.Namespace) -> None:
    services.remove_item(args.item_id)
    print("Produsul a fost sters")


def handle_history(args: argparse.Namespace) -> None:
    rows = services.history(item_id=args.item_id, limit=args.limit)
    headers = ["id", "name", "change", "reason", "note", "created_at"]
    print(format_table(rows, headers))


def dispatch(args: argparse.Namespace) -> None:
    if args.command == "add-item":
        handle_add_item(args)
    elif args.command == "list":
        handle_list(args)
    elif args.command == "receive":
        handle_receive(args)
    elif args.command == "consume":
        handle_consume(args)
    elif args.command == "adjust":
        handle_adjust(args)
    elif args.command == "set-minimum":
        handle_minimum(args)
    elif args.command == "remove":
        handle_remove(args)
    elif args.command == "history":
        handle_history(args)
    else:
        raise ValueError(f"Comanda necunoscuta: {args.command}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    services.setup_database()
    if args.init_db:
        print("Baza de date este pregatita.")

    try:
        dispatch(args)
        return 0
    except ValueError as exc:
        print(f"Eroare: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - entry point CLI
    sys.exit(main())
