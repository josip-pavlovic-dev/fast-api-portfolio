# 01 Uvod u baze i relacioni model

## Zasto uopste baza podataka

Do sada si radio CRUD nad listama u memoriji.
To je odlican prvi korak, ali ima ogranicenja:

- podaci nestaju kada se aplikacija ugasi
- nema pouzdanosti pri vecem broju korisnika
- tesko je traziti i filtrirati podatke efikasno
- nema jasnih pravila integriteta podataka

Baza podataka resava bas te probleme.

## Sta je DBMS

DBMS je sistem koji cuva, organizuje i vraca podatke.
Primeri:

- SQLite
- PostgreSQL
- MySQL

U ovoj fazi pocinjemo sa SQLite, jer je lak za lokalni razvoj.

## Relaciona baza u jednoj slici

Relacione baze rade sa tabelama.
Tabela ima redove i kolone.

- red = jedan zapis (jedan konkretan objekat)
- kolona = jedno svojstvo objekta

Primer tabela users:

- id
- username
- email
- created_at

## Kljucni pojmovi

## Primarni kljuc (Primary Key)

Primary key je jedinstveni identifikator reda.
Najcesce je to kolona id.

Pravila:

- ne sme biti NULL
- mora biti jedinstven

## Strani kljuc (Foreign Key)

Foreign key povezuje dve tabele.

Primer:

- tabela orders ima user_id
- user_id pokazuje na users.id

To pravi relaciju: jedan korisnik ima vise porudzbina.

## Integritet podataka

Baza cuva pravila:

- ne mozes uneti vrednost pogresnog tipa
- ne mozes uneti dupli jedinstveni podatak ako postoji UNIQUE
- ne mozes obrisati roditeljski red bez pravila za povezane redove (zavisi od on delete pravila)

## Tipovi relacija

## 1:1

Jedan korisnik ima jedan profil, i profil pripada jednom korisniku.

## 1:N

Jedan korisnik ima vise postova.
Svaki post pripada jednom korisniku.

## N:M

Student moze slusati vise kurseva, kurs ima vise studenata.
To se resava pomocnom tabelom.

## SQL jezik na visokom nivou

SQL ima vise kategorija komandi:

- DDL (schema): CREATE, ALTER, DROP
- DML (podaci): INSERT, UPDATE, DELETE
- DQL (upiti): SELECT
- DCL/TCL (kontrola): GRANT, COMMIT, ROLLBACK

Za pocetak su najvazniji CREATE, INSERT, SELECT, UPDATE, DELETE.

## Mentalni model za FastAPI

Kada imas endpoint POST /items:

1. stize request
2. validira se ulaz kroz Pydantic schema
3. kreira se ORM model
4. upisuje se u bazu kroz SQLAlchemy session
5. vraca se response schema

Tvoj dosadasnji CRUD ostaje isti po ideji.
Menja se mesto gde podaci zive i nacin pristupa podacima.

## Najcesce greske pocetnika

- mesanje models.py i schemas.py
- preskakanje validacija i oslanjanje samo na bazu
- zaboravljanje commit i refresh
- koriscenje jedne globalne DB sesije za sve zahteve

## Mini recnik

- schema (DB schema): struktura tabela i odnosa
- schema (Pydantic schema): oblik request/response podataka
- migration: verzionisanje promena baze kroz vreme
- transaction: grupa operacija koje uspevaju zajedno ili se vracaju nazad

## Brza provera razumevanja

1. Zasto lista u memoriji nije dovoljna za ozbiljniju aplikaciju?
2. Sta je razlika izmedju primary key i foreign key?
3. Kako bi opisao relaciju 1:N na primeru users i posts?
4. Zasto je transaction vazna?

## Zadaci

1. Nacrtaj 3 tabele za mini app: users, categories, items.
2. Obelezi primary i foreign kljuceve.
3. Opisi dve situacije gde integrity pravila sprecavaju bug.

## Zakljucak

Ulazis u sledeci veliki korak: od API endpoint logike ka pravom data sloju.
Ako savladas relacije i integritet, SQLAlchemy ce ti biti mnogo laksi.
