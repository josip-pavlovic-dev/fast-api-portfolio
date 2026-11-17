# PortfolioItemsAPI

Edukativni mini-projekat za postepeno učenje SQL-a, SQLite-a, SQLAlchemy-ja 2.0, Pydantic-a 2 i FastAPI-ja. Rad počinje direktnim SQL vežbama, a zatim se nastavlja modelima, API validacijom, CRUD rutama, testovima i migracijama.

## Trenutno stanje

### Već postoji

- SQLAlchemy 2.0 `Base`, engine i session factory.
- ORM modeli za `users`, `categories` i `items`.
- Status stavke kao enum `draft`/`published`, sa DB `CHECK` ograničenjem i
  podrazumevanom vrednošću `draft`.
- Timestamp kolone `created_at` i `updated_at`.
- FastAPI aplikacija u `main.py`, koja poziva `Base.metadata.create_all()`
  pri uvozu.
- ERD dijagram, SQLite vežbe za ovu bazu, dnevnik rada i detaljne beleške.

---

### Još nije implementirano

- Pydantic modeli u `schemas.py`.
- CRUD endpoint-i i router-i u `api/routes/`.
- DB session dependency za FastAPI.
- Posebna konfiguracija SQLite foreign-key enforcement-a.
- Testovi i Alembic migracije.

---

## Model baze

ORM modeli su u [models.py](./models.py):

| Tabela       | Kolone i ograničenja                                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `users`      | `id` primarni ključ; `name` obavezan; `email` obavezan i jedinstven                                                      |
| `categories` | `id` primarni ključ; `name` obavezan i jedinstven                                                                        |
| `items`      | `id`, obavezan `title`, opcioni `description`, obavezna cena `Numeric(10, 2)`, obavezan status, datumi i strani ključevi |

`items.owner_id` referencira `users.id`, a `items.category_id` referencira `categories.id`. Oba strana ključa su obavezna. Trenutni modeli deklarišu FK kolone, ali još nemaju ORM `relationship()` atribute.

`ItemStatus` definiše `draft` i `published`. ORM je podešen da čuva enum `.value` tekst (`draft`/`published`) i da napravi `CHECK` ograničenje.

`created_at` i `updated_at` dobijaju DB podrazumevanu vrednost preko `func.now()`; `onupdate=func.now()` važi za SQLAlchemy izmene, ne za direktan SQLite `UPDATE`.

SQLite po podrazumevanom podešavanju ne sprovodi strane ključeve. Oni su deklarisani u modelu, ali `db/database.py` još ne uključuje eksplicitno izvršavanje `PRAGMA foreign_keys=ON` nakon uspostavljanja konekcije.

Detaljan dijagram je u [ERD_PortfolioItemsAPI.drawio](./ERD_PortfolioItemsAPI.drawio).

---

## Struktura projekta

```text
PortfolioItemsAPI/
├── api/
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       ├── users.py               # prazan kostur
│       ├── categories.py          # prazan kostur
│       └── items.py               # prazan kostur
├── core/
│   ├── __init__.py
│   └── config.py                  # prazan kostur konfiguracije
├── data/                          # predviđeno za lokalnu SQLite bazu
├── db/
│   ├── __init__.py
│   ├── base.py                    # DeclarativeBase
│   ├── database.py                # engine, URL i SessionLocal
│   └── session.py                 # prazan kostur
├── notes/
│   └── dan_01.md                  # nullable, datetime, Decimal, Enum
├── progress/
│   └── 2026-11-16.md              # dnevna retrospektiva
├── __init__.py
├── main.py                        # FastAPI aplikacija i create_all()
├── models.py                      # SQLAlchemy modeli
├── schemas.py                     # prazan kostur Pydantic šema
├── ERD_PortfolioItemsAPI.drawio
├── sqlite3_exercises.md
└── README.md
```

`data/` je namenjen lokalnim bazama i ne treba commit-ovati razvojni `.db` fajl. U ovom projektu baza se kreira tek kada pratiš SQLite vežbe ili pokreneš aplikaciju.

---

## SQLite vežbe

- [SQLite vežbe za PortfolioItemsAPI](./sqlite3_exercises.md) rade direktno nad `PortfolioItemsAPI/data/portfolioitemsapp.db`. Uključuju kreiranje početne šeme, rad sa `users`, `categories` i `items`, i CRUD upite.
- [SQLite vežbe za Project 3](../Project_3/sqlite3_exercises.md) koriste zasebno postojeću `Project_3/data/todosapp3.db`. Obe baze su odvojene.

SQLite fajl se kreira tek kada ga otvoriš komandom iz vežbi ili kada aplikacija pokuša da se poveže. SQLite ne pravi nedostajuće roditeljske direktorijume.

---

## Pokretanje aplikacije

`main.py` poziva `create_all()` pri uvozu. To može kreirati nedostajuću bazu i tabele, zato aplikaciju pokreni tek kada želiš taj efekat. `create_all()` ne menja šemu postojećih tabela. Za kasnije izmene biće potrebne migracije.

DB URL je relativan:

```text
sqlite:///./PortfolioItemsAPI/data/portfolioitemsapp.db
```

Zato aplikaciju treba pokrenuti iz direktorijuma `fast-api-course-my-work`, kako bi URL pokazao na očekivani fajl:

```bash
cd fast-api-course-my-work
../.venv/bin/uvicorn PortfolioItemsAPI.main:app --reload
```

Trenutno aplikacija još nema CRUD endpoint-e.

---

## Beleške i materijali

- [Dnevnik rada za 2026-11-16](./progress/2026-11-16.md)
- [Detaljne beleške za prvi dan](./notes/dan_01.md)
- [SQLite terminal vežbe za PortfolioItemsAPI](./sqlite3_exercises.md)
- [SQLAlchemy ERD](./ERD_PortfolioItemsAPI.drawio)
- [SQL Database kursni materijali](../../docs/sql_database/README.md)
- [Uvod u SQL upite](../../docs/stage_2/01_setup_database/04_queries_introduction/04_queries_introduction_detaljno.md)
- [SQLite terminal materijal za TodoApp](../../docs/stage_2/01_setup_database/05_sqlite3_setting_up_Todos/05_sqlite3_setting_up_Todos_detaljno.md)
- [Plan vežbi i mini-projekta](../../docs/sql_database/09_plan_vezbe_i_mini_projekat.md)

---

## Plan rada

1. Vežbati SQL upite nad odgovarajućim bazama kroz dva odvojena dokumenta.
2. Razumeti veze, transakcije i ograničenja pre API implementacije.
3. Završiti SQLite/SQLAlchemy konfiguraciju, uključujući DB session dependency i sprovođenje stranih ključeva.
4. Dodati Pydantic ulazne/izlazne šeme i FastAPI CRUD rute.
5. Dodati testove i zatim Alembic migracije.

Dok se uči početna šema, razvojnu bazu možeš svesno ponovo kreirati ako nema podataka koje treba sačuvati. Kada se uvedu migracije ili važni podaci, promene šeme treba raditi kontrolisanim migracijama, a ne brisanjem baze.
