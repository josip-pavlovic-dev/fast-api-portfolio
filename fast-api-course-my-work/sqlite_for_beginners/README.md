# SQLite for Beginners

Ovaj folder sadrži nastavne beleške i vežbe za kurs SQLite for Beginners. Materijali su na srpskoj latinici, prilagođeni radu u VS Code-u i dopunjeni savremenim napomenama tamo gde je to važno za ispravno korišćenje SQLite-a.

Cilj je da izgradiš čvrste osnove SQL-a i relacionih baza, a zatim ih povežeš sa SQLAlchemy 2.0 i FastAPI-jem.

## Preporučeni redosled

Prođi oblasti ovim redosledom:

1. [00 — Uvod](./00_intro/README.md)
2. [01 — Osnovne SQLite komande](./01_some_basic_sql_commands/README.md)
3. [02 — Čitanje i manipulisanje podacima](./02_retriving_data_and_manipulating_data/README.md)

Svaka oblast ima svoj README sa kratkim pregledom i linkovima ka lekcijama. Svaka lekcija sadrži teoriju i vežbe na kraju.

## Plan učenja

Za dnevni raspored od četiri sata pogledaj [plan učenja po danima](./plan_ucenja/README.md).

## Vežbanje u VS Code-u

Koristi folder [`playground/`](./playground/) za svoje `.sql` fajlove i ostale rezultate vežbanja. Možeš da ih organizuješ po lekcijama, na primer `01_select.sql`, `04_order_by.sql` ili `06_where.sql`.

Za pripremu baza, predloženu strukturu fajlova i postupak rada sa vežbama pogledaj [README za playground](./playground/README.md).

Iz root-a repozitorijuma možeš otvoriti nastavnu Chinook bazu u SQLite CLI-ju:

```bash
sqlite3 fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db
```

U SQLite shell-u pokreni svoju SQL datoteku pomoću `.read` komande, na primer:

```sql
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/06_filtering_data_with_where_clause.sql
```

Možeš koristiti i SQLite ekstenziju u VS Code-u. Za vežbe koje menjaju ili brišu podatke, prvo napravi kopiju baze u `playground/` i radi nad kopijom, ne nad originalnim `chinook.db`. SQLite datoteke i njihove WAL/journal prateće datoteke u `playground/` isključene su iz Git-a; tvoje `.sql` vežbe ostaju verzionisane.

## Materijali

- [`chinook/chinook.db`](./chinook/chinook.db) — primer baze korišćen u lekcijama.
- [`chinook/ERD.drawio`](./chinook/ERD.drawio) — uređivi dijagram tabela i veza.
- [`chinook/db_schema.jpg`](./chinook/db_schema.jpg) — izvorna slika šeme.
- [`transcripts/`](./transcripts/) — transkripti koji služe kao izvor za nastavne beleške.
- [`playground/`](./playground/) — prostor za tvoje upite i rezultate vežbanja.

Trenutno su pripremljene oblasti 00, 01 i 02. Nastavak kursa može se dodati kao nove oblasti kada budeš spreman.
