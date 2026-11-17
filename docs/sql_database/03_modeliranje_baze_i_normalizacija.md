# 03 Modeliranje baze i normalizacija

## Zašto modeliranje dolazi pre koda

Najskuplja greška nije pogrešan endpoint.
Najskuplja greška je loš model podataka.

Ako je schema loša:

- endpointi će biti komplikovani
- performanse će padati
- podaci će biti nekonzistentni

Zato prvo model, pa tek onda implementacija.

---

## Koraci modeliranja

1. Identifikuj entitete (npr. User, Item, Category, Order).
2. Definisi atribute po entitetu.
3. Odredi kljuceve i jedinstvenost.
4. Definisi relacije i cardinality.
5. Proveri normalizaciju.
6. Razmisli o upitima koje ćeš najčešće raditi.

---

## Primer mini domena: portfolio items

Entiteti:

- users
- items
- categories

Predlog:

- user ima više items
- category ima više items
- item pripada jednom user-u i jednoj category

## Primer schema razmišljanja

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
- status (CHECK constraint ili ENUM)
- owner_id (FK -> users.id)
- category_id (FK -> categories.id)
- created_at
- updated_at

---

## Normalizacija ukratko

Cilj normalizacije je smanjenje dupliranja i anomalija pri izmeni.

---

## 1NF

Svaka kolona treba da sadrži atomsku vrednost.
Nema liste vrednosti u jednoj celiji.

Loše: `tags` kolona sa "python,fastapi,sql"
Bolje: posebna `item_tags` tabela.

---

## 2NF

Ako imas slozen PK, ne-key kolone moraju zavisiti od celog kljuca.
(U praksi je češće bitno kod spojnih tabela.)

---

## 3NF

Ne-key kolone ne treba da zavise od drugih ne-key kolona.

Primer problema:

- users tabela ima city_id i city_name
- city_name zavisi od city_id, ne direktno od users PK

Rešenje:

- posebna cities tabela
- users.city_id FK

---

## Denormalizacija

Nekad namerno dupliraš podatke zbog performansi. Ali to radi tek kad imaš dokaz da je potrebno, ne na početku projekta.

---

## Ograničenja (constraints)

- NOT NULL: obavezno polje
- UNIQUE: jedinstvena vrednost
- CHECK: pravilo vrednosti
- FK: referencijalni integritet

Primer CHECK:

```sql
price REAL NOT NULL CHECK (price >= 0)
```

---

## Soft delete vs hard delete

Hard delete:

- red se fizički briše i više se ne može vratiti

Soft delete:

- red ostaje, ali ima npr. `is_deleted = 1` ili `deleted_at`

Za audit i povrat podataka, soft delete je često bolji, ali traži disciplinu u svim upitima (npr. dodavanje `WHERE is_deleted = 0`).

---

## Audit kolone

Preporuka za realne app:

- created_at
- updated_at
- optional: created_by, updated_by

---

## Praksa za budući models.py

Pre nego napises ORM klase, odgovori:

1. Koji su required atributi?
2. Koja polja moraju biti jedinstvena?
3. Gde treba FK?
4. Šta radimo pri brisanju parent reda?
5. Da li je soft delete potreban sada ili kasnije?

---

## Česte greške pri modeliranju

- prerano ubacivanje previše tabela bez realne potrebe
- kasno dodavanje UNIQUE pravila
- izbegavanje FK i oslanjanje na „dogovor“ u kodu
- nema timestamp kolona od starta

---

## Zadaci

1. Nacrtaj ERD model za `users`, `items`, `categories`.
2. Definiši 5 `constraints` koje smatraš obaveznim.
3. Napiši gde bi koristio soft delete, a gde hard delete.
4. Predloži jedan indeks na `items` i obrazloži zašto.

---

## Zaključak

Dobar model podataka je pola backend posla. U sledećoj lekciji prelazimo na SQLite praksu, transakcije i indekse.
