# 09 Plan vezbe i mini projekat

## Cilj plana

Da teoriju odmah pretvoris u stabilnu praksu.

## Faza 1: Cisto SQL razmisljanje

Ishod:

- samostalno pises osnovne SELECT/WHERE/JOIN upite
- razumes relacije i constraints

Zadaci:

1. Napisi 10 SQL upita nad users/items/categories.
2. Uradi 3 agregacije sa GROUP BY.
3. Dodaj 2 indeksa i objasni zasto.

## Faza 2: SQLAlchemy skelet

Ishod:

- imas ispravan database.py, models.py, schemas.py

Zadaci:

1. Definisi 3 ORM modela sa FK relacijama.
2. Uspostavi session dependency po request-u.
3. Napravi create_all za lokalni start.

## Faza 3: Endpoint implementacija

Ishod:

- kompletan CRUD preko baze

Zadaci:

1. POST /items
2. GET /items
3. GET /items/{id}
4. PUT /items/{id}
5. PATCH /items/{id}
6. DELETE /items/{id}

## Faza 4: Test pokrivenost

Ishod:

- endpointi imaju osnovnu sigurnosnu mrezu

Minimalni testovi:

1. create success + invalid payload
2. get by id found + not found
3. put success + not found
4. patch success
5. delete success + not found

## Faza 5: Migracije

Ishod:

- schema promene su verzionisane

Zadaci:

1. Uvedi Alembic.
2. Napravi inicijalnu migraciju.
3. Dodaj novu kolonu kroz drugu migraciju.

## Predlog mini projekta

Tema: Portfolio Items API

Tabele:

- users
- categories
- items

Obavezna polja items:

- title
- description
- price
- status (draft/published)
- owner_id
- category_id
- created_at
- updated_at

## Definition of done

- CRUD endpointi rade nad SQLite bazom
- status kodovi i greske su dosledni
- postoji bar 10 testova
- migracije prolaze napred i nazad
- dokumentovan API i data model

## Kako da znas da si spreman za sledeci nivo

Spreman si za PostgreSQL i napredniji auth sloj kada:

- bez pomoci kreiras novi model + migraciju + CRUD
- brzo lociras gresku izmedju schema/model/route sloja
- razumes koji indeks i zasto treba za odredjeni query

## Zavrsna poruka

Ovo je trenutak gde prelazis iz "znam FastAPI endpoint" u
"znam da gradim backend koji cuva i stiti podatke".
To je veliki i vazan skok.
