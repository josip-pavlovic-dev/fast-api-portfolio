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
- `db/session.py` definiše sinhronu SQLAlchemy `Session` dependency funkciju.
- Izdvojeni demonstracioni model sa svih šest planiranih tabela u
  `models1.py` i FastAPI CRUD primer u `main1.py`. Oni ne menjaju postojeći
  `models.py` i `main.py`.
- ERD dijagram, SQLite vežbe za ovu bazu, dnevnik rada i detaljne beleške.

---

### Još nije implementirano

- Pydantic modeli i CRUD router-i za osnovnu aplikaciju u `schemas.py` i
  `api/routes/`.
- Pydantic šeme i CRUD router-i za osnovnu aplikaciju u `schemas.py` i
  `api/routes/`; postojeći `main.py` ih još ne koristi.
- SQLite foreign-key enforcement za osnovni `db/database.py` engine.
- Testovi i Alembic migracije.

`main1.py` je nastavna referentna verzija: sadrži pun CRUD za `items`, kao i
kreiranje i listanje gradova, korisnika, kategorija i tagova potrebnih za
testiranje veza. Njeni request i response modeli su privremeno definisani u
istom fajlu; kasnije ih možeš premestiti u `schemas.py`, a endpoint-e u
`api/routes/`. Za razliku od osnovnog engine-a, demonstracioni engine uključuje
SQLite foreign-key enforcement. Endpoint-i su sinhroni jer koriste sinhroni
SQLAlchemy `Session`. `Base1` ima odvojene metadata podatke kako bi ovaj model
mogao da se uvozi bez sudara sa imenima tabela iz `models.py`.

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

Predloženi, normalizovani ciljni dijagram je u
[ERD_PortfolioItemsAPI.drawio](./ERD_PortfolioItemsAPI.drawio). Dodaci
`cities`, `tags` i `item_tags` prikazani su kao planirana šema za učenje i
još nisu implementirani u `models.py` niti kreirani u bazi.

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
│   └── session.py                 # sinhroni get_db dependency
├── notes/
│   ├── dan_01.md                  # nullable, datetime, Decimal, Enum
│   └── dan_02.md                  # SQLite indeksi i rowid
├── progress/
│   ├── 2026-11-16.md              # dnevna retrospektiva
│   └── 2026-11-17.md              # plan modelovanja i normalizacije
├── __init__.py
├── main.py                        # FastAPI aplikacija i create_all()
├── main1.py                       # demonstracioni endpoint-i i API šeme
├── models.py                      # SQLAlchemy modeli
├── models1.py                     # ciljna normalizovana šema sa 6 tabela
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

Osnovna aplikacija koristi postojeći DB URL:

```text
sqlite:///./PortfolioItemsAPI/data/portfolioitemsapp.db
```

Zato aplikaciju treba pokrenuti iz direktorijuma `fast-api-course-my-work`, kako bi URL pokazao na očekivani fajl:

```bash
cd fast-api-course-my-work
../.venv/bin/uvicorn PortfolioItemsAPI.main:app --reload
```

Demonstraciona verzija koristi odvojenu bazu `PortfolioItemsAPI/data/portfolioitemsapp1.db`, jer `create_all()` ne migrira već postojeće tabele. Pokretaj je na isti način:

```bash
cd fast-api-course-my-work
../.venv/bin/uvicorn PortfolioItemsAPI.main1:app --reload
```

Prvi start kreira demonstracionu bazu i njene tabele. Nju takođe ne treba commit-ovati.

---

## Beleške i materijali

- [Dnevnik rada za 2026-11-16](./progress/2026-11-16.md)
- [Plan modelovanja i normalizacije za 2026-11-17](./progress/2026-11-17.md)
- [Detaljne beleške za prvi dan](./notes/dan_01.md)
- [SQLite indeksi i rowid — beleške za drugi dan](./notes/dan_02.md)
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
