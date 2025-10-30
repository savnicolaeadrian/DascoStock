# DascoStock

Aplicatie din linia de comanda pentru gestiunea stocului unui restaurant. 
Instrumentul foloseste o baza de date SQLite salvata implicit in `~/.dascostock/inventory.db` si
permite administrarea produselor, receptiilor si consumurilor direct din terminal.

## Instalare si configurare

Aplicatia necesita Python 3.9 sau mai nou. Pentru rulare nu sunt necesare dependinte externe.
Clonati depozitul si rulati comenzile din radacina proiectului. Baza de date este initializata
automat la prima executie, insa puteti folosi flag-ul optional `--init-db` pentru a afisa un mesaj
explicit ca baza de date este pregatita:

```bash
python -m inventory_app.cli --init-db add-item "Faina 000" kg --quantity 25 --minimum 10 --category "Depozit" --price 4.5
```

Locatia fisierului SQLite poate fi personalizata prin variabila de mediu `DASCOSTOCK_DB_PATH`.
Alternativ, variabila `DASCOSTOCK_DATA_DIR` modifica directorul in care se stocheaza fisierele
aplicatiei.

## Utilizare

Comenzile principale disponibile sunt:

- `add-item` – adauga un produs nou.
- `list` – afiseaza inventarul curent, optional doar produsele cu stoc sub prag.
- `receive` – inregistreaza o receptie de marfa.
- `consume` – scade stocul in urma consumului.
- `adjust` – ajusteaza manual stocul pentru pierderi sau corectii.
- `set-minimum` – actualizeaza pragul minim al unui produs.
- `remove` – sterge un produs din inventar.
- `history` – afiseaza istoricul ajustarilor.

Afisarea tabelelor foloseste o prezentare text simpla, facilitand exportul catre alte instrumente.

### Exemple

Adaugarea unui nou produs:

```bash
python -m inventory_app.cli --init-db add-item "Mozzarella" kg --quantity 5 --minimum 2 --category "Lactate" --price 32
```

Inregistrarea unui consum:

```bash
python -m inventory_app.cli consume 1 0.5 --note "Pizza Margherita"
```

Verificarea produselor cu stoc minim:

```bash
python -m inventory_app.cli list --low-stock
```

Consultarea istoricului ajustarilor pentru un produs:

```bash
python -m inventory_app.cli history --item-id 1 --limit 5
```

## Structura proiectului

- `inventory_app/config.py` – configurarea cailor si directorului de date.
- `inventory_app/database.py` – gestionarea conexiunilor si schema bazei de date.
- `inventory_app/repository.py` – operatiuni CRUD de nivel jos pentru tabele.
- `inventory_app/services.py` – logica de business si validari de nivel inalt.
- `inventory_app/cli.py` – interfata din linia de comanda.

Aplicatia poate fi extinsa usor pentru a integra rapoarte suplimentare sau pentru a expune o API web.
