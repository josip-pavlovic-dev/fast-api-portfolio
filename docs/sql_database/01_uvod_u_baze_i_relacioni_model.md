# 01 Uvod u baze i relacioni model

## Zašto uopšte baza podataka

Do sada si radio `CRUD` nad listama u memoriji.
To je odličan prvi korak, ali ima ograničenja:

- podaci u memoriji nisu trajni
- podaci nestaju kada se aplikacija ugasi
- nema pouzdanosti pri većem broju korisnika
- teško je tražiti i filtrirati podatke efikasno
- nema jasnih pravila integriteta podataka

Baza podataka rešava baš te probleme.

---

## Šta je DBMS

`DBMS` je sistem koji čuva, organizuje i vraća podatke.
Primeri `DBMS` sistema:

- SQLite
- PostgreSQL
- MySQL

U ovoj fazi počinjemo sa SQLite, jer je lak za lokalni razvoj.

## Relaciona baza u jednoj slici

`Relacione baze` rade sa tabelama.
Tabela ima redove i kolone.

- red = jedan zapis (jedan konkretan objekat)
- kolona = jedno svojstvo objekta

Primer tabele `users`:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    updated_at TIMESTAMP,
    created_at TIMESTAMP
);
```

- `id` -> jedinstveni identifikator korisnika
- `username` -> korisničko ime
- `email` -> email adresa korisnika
- `updated_at` -> vreme poslednje izmene
- `created_at` -> vreme kreiranja korisnika

---

## Ključni pojmovi

- `Primary Key (PK)` -> jedinstveni identifikator reda u tabeli
- `Foreign Key (FK)` -> kolona koja povezuje red u jednoj tabeli sa redom u drugoj tabeli (referencira primarni ključ druge tabele)
- `Unique Key (UK)` -> kolona koja mora imati jedinstvene vrednosti u tabeli (ne sme biti duplikata)
- `Index` -> struktura koja ubrzava pretragu po jednoj ili više kolona
- `Check Constraint` -> pravilo koje ograničava vrednosti koje kolona može imati

---

## Primarni ključ (Primary Key)

`Primary key` je jedinstveni identifikator reda.
Najčešće je to kolona id.

Pravila za `primary key`:

- ne sme biti `NULL`
- mora biti jedinstven (`unique`)

---

## Strani ključ (Foreign Key)

`Foreign key` povezuje dve tabele.

Primer:

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Tabela `orders` ima `user_id` kolonu koja referencira `users.id` koji je primarni ključ tabele `users`

`user_id` pokazuje na `users.id` što pravi vezu između porudžbina i korisnika. Ovo je primer relacije 1:N, gde jedan korisnik može imati više porudžbina. Na taj način orders tabela zna kojem korisniku pripada svaka porudžbina. Pošto `user_id` referencira `users.id` koji je primarni ključ tabele `users` i koji ne može biti NULL i mora biti jedinstven, samim time i `user_id` ne može biti NULL i mora biti jedinstven u kontekstu te relacije. Zbog toga jedna porudžbina uvek pripada tačno jednom korisniku.

U praksi, ovo znači da baza garantuje integritet podataka i sprečava situacije gde bi porudžbina mogla biti vezana za nepostojećeg korisnika ili da jedna porudžbina pripada većem broju korisnika što nije logički moguće.

---

## Integritet podataka

Baza čuva pravila:

- ne možeš uneti vrednost pogrešnog tipa (`type mismatch`)
- ne možeš uneti dupli jedinstveni podatak ako postoji `UNIQUE`
- ne možeš obrisati roditeljski red bez pravila za povezane redove (zavisi od `ON DELETE` pravila)

---

## Tipovi relacija

### 1:1

Jedan korisnik ima jedan profil, i profil pripada jednom korisniku.

---

### 1:N

Jedan korisnik ima više postova.
Svaki post pripada jednom korisniku.

---

### N:M

Student može slušati više kurseva, kurs ima više studenata.

To se rešava pomoćnom tabelom koja sadrži strane ključeve ka obe tabele, čime se omogućava povezivanje više studenata sa više kurseva.

---

## SQL jezik na visokom nivou

SQL ima više kategorija komandi:

- DDL (schema): CREATE, ALTER, DROP
- DML (podaci): INSERT, UPDATE, DELETE
- DQL (upiti): SELECT
- DCL/TCL (kontrola): GRANT, COMMIT, ROLLBACK

Za početak su najvažniji CREATE, INSERT, SELECT, UPDATE, DELETE.

---

## Mentalni model za FastAPI

Kada imaš endpoint POST /items:

1. stiže request
2. validira se ulaz kroz Pydantic schema
3. kreira se ORM model
4. upisuje se u bazu kroz SQLAlchemy session
5. vraća se response schema

Tvoj dosadašnji CRUD ostaje isti po ideji.
Menja se mesto gde podaci žive i način pristupa podacima.

---

## Najčešće greške početnika

- mešanje models.py i schemas.py
- preskakanje validacija i oslanjanje samo na bazu
- zaboravljanje commit i refresh
- korišćenje jedne globalne DB sesije za sve zahteve

---

## Mini rečnik

- schema (DB schema): struktura tabela i odnosa
- schema (Pydantic schema): oblik request/response podataka
- migration: verzionisanje promena baze kroz vreme
- transaction: grupa operacija koje uspevaju zajedno ili se vraćaju nazad

---

## Brza provera razumevanja

1. Zašto lista u memoriji nije dovoljna za ozbiljniju aplikaciju?

- Lista u memoriji nije dovoljna jer se podaci gube kada aplikacija prestane da radi i nije lako deliti podatke između više instanci aplikacije.

2. Šta je razlika između primarnog (`Primary Key`) ključa i stranog (`Foreign Key`) ključa?

- Primarni ključ je jedinstveni identifikator reda u tabeli, dok strani ključ povezuje red u jednoj tabeli sa redom u drugoj tabeli (`Foreign Key`).

3. Kako bi opisao relaciju `1:N` na primeru `users` i `posts`?

- Jedan korisnik može imati više postova, dok svaki post pripada tačno jednom korisniku (`1:N` relacija).

4. Zašto je `transaction` važna?

- `Transaction` (transakcija) je važna jer omogućava da grupa operacija bude izvršena zajedno ili da se sve ponište u slučaju greške, čime se održava integritet podataka.

---

## Zadaci

1. Nacrataj 3 tabele za mini app: users, categories, items.

- `users` tabela: `id` (`Primary Key`), `name`, `email`
- `categories` tabela: `id` (`Primary Key`), `name`
- `items` tabela: `id` (`Primary Key`), `name`, `user_id` (`Foreign Key` ka `users.id`), `category_id` (`Foreign Key` ka `categories.id`)

2. Obeleži `primary` i `foreign` ključeve.

- `users.id` je `Primary Key`, pa ne može postojati dva korisnika sa istim `id`.
- `items.user_id` je `Foreign Key` ka `users.id`, pa ne može postojati `item` koji pripada nepostojećem korisniku.
- `items.category_id` je `Foreign Key` ka `categories.id`, pa ne može postojati `item` koji pripada nepostojećoj kategoriji.

3. Opiši dve situacije gde `integrity` pravila (`Primary Key` i `Foreign Key`) sprečavaju bug.

- Situacija 1: Pokušaj dodavanja korisnika sa već postojećim `id` će biti odbijen zbog `Primary Key` pravila, čime se sprečava duplikat i gubitak integriteta podataka.
- Situacija 2: Pokušaj dodavanja `item` koji pripada nepostojećem korisniku ili kategoriji će biti odbijen zbog `Foreign Key` pravila, čime se sprečava referencijalni integritet i potencijalni bugovi u aplikaciji.

---

## Zaključak

Ulaziš u sledeći veliki korak: od `API endpoint logike` ka pravom data sloju.
Ako savladaš `relacije` i `integritet`, SQLAlchemy će ti biti mnogo lakši.
