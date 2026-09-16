# 03 Modeliranje baze i normalizacija

## Zasto modeliranje dolazi pre koda

Najskuplja greska nije pogresan endpoint.
Najskuplja greska je los model podataka.

Ako je schema losa:

- endpointi ce biti komplikovani
- performanse ce padati
- podaci ce biti nekonzistentni

Zato prvo model, pa tek onda implementation.

## Koraci modeliranja

1. Identifikuj entitete (npr. User, Item, Category, Order).
2. Definisi atribute po entitetu.
3. Odredi kljuceve i jedinstvenost.
4. Definisi relacije i cardinality.
5. Proveri normalizaciju.
6. Razmisli o upitima koje ces najcesce raditi.

## Primer mini domena: portfolio items

Entiteti:

- users
- items
- categories

Predlog:

- user ima vise items
- category ima vise items
- item pripada jednom user i jednoj category

## Primer schema razmisljanja

Tabela users:

- id (PK)
- username (UNIQUE)
- email (UNIQUE)
- created_at

Tabela categories:

- id (PK)
- name (UNIQUE)

Tabela items:

- id (PK)
- title
- description
- price
- owner_id (FK -> users.id)
- category_id (FK -> categories.id)
- created_at
- updated_at

## Normalizacija ukratko

Cilj normalizacije je smanjenje dupliranja i anomalija pri izmeni.

## 1NF

Svaka kolona treba da sadrzi atomsku vrednost.
Nema liste vrednosti u jednoj celiji.

Lose: tags kolona sa "python,fastapi,sql"
Bolje: posebna item_tags tabela.

## 2NF

Ako imas slozen PK, ne-key kolone moraju zavisiti od celog kljuca.
(U praksi je cesce bitno kod spojnih tabela.)

## 3NF

Ne-key kolone ne treba da zavise od drugih ne-key kolona.

Primer problema:

- users tabela ima city_id i city_name
- city_name zavisi od city_id, ne direktno od users PK

Resenje:

- posebna cities tabela
- users.city_id FK

## Denormalizacija

Nekad namerno dupliras podatke zbog performansi.
Ali to radi tek kad imas dokaz da je potrebno,
ne na pocetku projekta.

## Ogranicenja (constraints)

- NOT NULL: obavezno polje
- UNIQUE: jedinstvena vrednost
- CHECK: pravilo vrednosti
- FK: referencijalni integritet

Primer CHECK:

```sql
price REAL NOT NULL CHECK (price >= 0)
```

## Soft delete vs hard delete

Hard delete:

- red se fizicki brise

Soft delete:

- red ostaje, ali ima npr. is_deleted = 1 ili deleted_at

Za audit i povrat podataka, soft delete je cesto bolji,
ali trazi disciplinu u svim upitima.

## Audit kolone

Preporuka za realne app:

- created_at
- updated_at
- optional: created_by, updated_by

## Praksa za buduci models.py

Pre nego napises ORM klase, odgovori:

1. Koji su required atributi?
2. Koja polja moraju biti jedinstvena?
3. Gde treba FK?
4. Sta radimo pri brisanju parent reda?
5. Da li je soft delete potreban sada ili kasnije?

## Ceste greske pri modeliranju

- prerano ubacivanje previse tabela bez realne potrebe
- kasno dodavanje UNIQUE pravila
- izbegavanje FK i oslanjanje na "dogovor" u kodu
- nema timestamp kolona od starta

## Zadaci

1. Nacrtaj ER model za users, items, categories.
2. Definisi 5 constraints koje smatras obaveznim.
3. Napisi gde bi koristio soft delete, a gde hard delete.
4. Predlozi jedan indeks na items i obrazlozi zasto.

## Zakljucak

Dobar model podataka je pola backend posla.
U sledecoj lekciji prelazimo na SQLite praksu, transakcije i indekse.
