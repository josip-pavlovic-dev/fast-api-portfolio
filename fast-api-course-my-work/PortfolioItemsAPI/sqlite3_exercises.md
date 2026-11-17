# SQLite3 vežbe — PortfolioItemsAPI

Ove vežbe su vezane za bazu PortfolioItemsAPI i njegove tri tabele: `users`, `categories` i `items`. Radićeš direktno nad `PortfolioItemsAPI/data/portfolioitemsapp.db`.

Promene koje napraviš ostaju sačuvane u toj bazi.

> Baza se ne kreira unapred. Komanda `sqlite3` će je napraviti kada je prvi put otvoriš.
> Ako `PortfolioItemsAPI/data/` direktorijum ne postoji, prvo ga napravi.
> Ove vežbe kreiraju tabele direktno kroz SQLite, bez korišćenja ORM-a ili drugih alata.
> Nemoj pokretati `main.py` samo radi njihovog kreiranja.

## 1. Otvori bazu za ovaj projekat

Komandu pokreni iz **root-a repozitorijuma**:

```bash
mkdir -p fast-api-course-my-work/PortfolioItemsAPI/data
sqlite3 fast-api-course-my-work/PortfolioItemsAPI/data/portfolioitemsapp.db
```

U SQLite prompt-u proveri putanju:

```sql
.databases
```

Treba da prikazuje `fast-api-course-my-work/PortfolioItemsAPI/data/portfolioitemsapp.db`.

Podešavanja prikaza i uključivanje provere stranih ključeva važe za trenutnu SQLite konekciju:

```sql
.headers on
.mode table
PRAGMA foreign_keys = ON; # Uključi proveru stranih ključeva za trenutnu konekciju
PRAGMA foreign_keys; # Proveri da li je provera stranih ključeva uključena
```

Poslednji upit treba da vrati `1`. SQLite strane ključeve po podrazumevanom
ne sprovodi, pa ih treba uključiti za svaku novu konekciju. Ovo je važno jer bez uključene provere stranih ključeva, SQLite neće sprečiti unos nevalidnih referenci u kolone koje imaju FOREIGN KEY ograničenje.

---

## 2. Kreiraj početnu šemu

Ova DDL šema odgovara početnim ORM modelima u `models.py`. Pokreni je samo pri prvom radu sa praznom bazom. Ako tabele već postoje, prvo ih pregledaj sa `.schema` umesto da pokušavaš ponovo da ih kreiraš.

```sql
CREATE TABLE users (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR NOT NULL UNIQUE
);

CREATE TABLE categories (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE
);

CREATE TABLE items (
    id INTEGER NOT NULL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    price NUMERIC(10, 2) NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'draft'
        CONSTRAINT item_status CHECK (status IN ('draft', 'published')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    owner_id INTEGER NOT NULL REFERENCES users (id),
    category_id INTEGER NOT NULL REFERENCES categories (id)
);

CREATE INDEX ix_users_id ON users (id);
CREATE INDEX ix_categories_id ON categories (id);
CREATE INDEX ix_items_id ON items (id);
```

Pregledaj kreirane tabele i kolone:

```sql
.tables
.schema users
.schema categories
.schema items
PRAGMA table_info(items);
```

---

## 3. Dodaj korisnike i kategorije

Dodaj dva korisnika i dve kategorije. Email i ime korisnika kao i ime kategorije moraju biti različiti jer su jedinstveni. Ovaj primer unesi jednom; ako si ga već koristio, izaberi druge email adrese i nazive kategorija, pa ih koristi i u upitima za dodavanje stavki:

```sql
INSERT INTO users (name, email)
VALUES
    ('Ana Example', 'ana@example.test'),
    ('Marko Example', 'marko@example.test');

INSERT INTO categories (name)
VALUES
    ('Web development'),
    ('Data projects');
```

Prikaži ih sortirane po ID-u:

```sql
SELECT id, name, email
FROM users
ORDER BY id;

SELECT id, name
FROM categories
ORDER BY id;
```

Zapiši ID-jeve koje su dobili. ID se automatski dodeljuje i ne treba
pretpostaviti da je uvek `1`.

---

## 4. Dodaj portfolio stavke

Za probne stavke pronađi `owner_id` i `category_id` po email-u i imenu kategorije. Tako ne moraš da pretpostavljaš njihove ID vrednosti.

Prvi red izostavlja `status`, pa će baza postaviti `draft`. Drugi eksplicitno postavlja `published`:

```sql
INSERT INTO items (title, description, price, owner_id, category_id)
VALUES (
    'Portfolio landing page',
    'Prvi SQLite unos',
    125.50,
    (SELECT id FROM users WHERE email = 'ana@example.test'),
    (SELECT id FROM categories WHERE name = 'Web development')
);

INSERT INTO items (title, description, price, status, owner_id, category_id)
VALUES (
    'Data dashboard',
    NULL,
    89.99,
    'published',
    (SELECT id FROM users WHERE email = 'marko@example.test'),
    (SELECT id FROM categories WHERE name = 'Data projects')
);
```

Pregledaj stavke i njihove datume:

```sql
SELECT id, title, description, price, status, created_at, updated_at
FROM items
ORDER BY id;
```

---

## 5. Vežbaj `SELECT` i `WHERE`

1. Prikaži samo nazive i cene:

   ```sql
   SELECT title, price FROM items;
   ```

2. Pronađi sve objavljene stavke:

   ```sql
   SELECT id, title, status
   FROM items
   WHERE status = 'published';
   ```

3. Pronađi stavke bez opisa. Za `NULL` se koristi `IS NULL`, ne `= NULL`:

   ```sql
   SELECT id, title
   FROM items
   WHERE description IS NULL;
   ```

4. Prebroj stavke po statusu:

   ```sql
   SELECT status, COUNT(*) AS item_count
   FROM items
   GROUP BY status;
   ```

5. Prikaži stavke zajedno sa vlasnikom i kategorijom:

   ```sql
   SELECT
       items.id,
       items.title,
       users.name AS owner,
       categories.name AS category
   FROM items
   JOIN users ON users.id = items.owner_id
   JOIN categories ON categories.id = items.category_id
   ORDER BY items.id;
   ```

---

## 6. Vežbaj `UPDATE`

Najpre pronađi ID stavke koju želiš da ažuriraš. Zatim zameni `ID_STAVKE` stvarnim brojem iz rezultata:

```sql
UPDATE items
SET status = 'published',
    updated_at = CURRENT_TIMESTAMP
WHERE id = ID_STAVKE;
```

Odmah pročitaj izmenjeni red:

```sql
SELECT id, title, status, updated_at
FROM items
WHERE id = ID_STAVKE;

SELECT changes();
```

Kod direktnog `sqlite3 UPDATE`, `updated_at` se ne osvežava automatski. `onupdate=func.now()` iz modela se primenjuje kroz SQLAlchemy, što znači da će se `updated_at` automatski osvežavati pri svakoj izmeni kroz ORM. Međutim, to nije ugrađeni SQLite trigger, zato ga u ovom SQL upitu postavljamo ručno.

---

## 7. Vežbaj `DELETE`

Izaberi ID jedne od probnih stavki i zameni `ID_STAVKE` stvarnom vrednošću:

```sql
DELETE FROM items
WHERE id = ID_STAVKE;

SELECT changes();

SELECT id, title
FROM items
WHERE id = ID_STAVKE;
```

`changes()` treba da prijavi `1`, a završni `SELECT` da ne vrati red.
Brisanje stavke ne briše njenog korisnika ni kategoriju.

---

## 8. Razmisli i odgovori

1. Zašto se u `INSERT` navode imena kolona?

2. Šta se dešava ako `status` izostavimo iz `INSERT`-a?

3. Zašto se `NULL` proverava pomoću `IS NULL`?

4. Zašto su `JOIN` potrebni da bi se uz stavku prikazali vlasnik i kategorija?

5. Zašto je `UPDATE` ili `DELETE` bez preciznog `WHERE` uslova rizičan?

6. Zašto se `updated_at` u ovom direktnom SQL primeru postavlja ručno?

7. Šta ograničavaju `UNIQUE`, `NOT NULL`, `CHECK` i strani ključevi?

---

## Napomena o vrednostima i kasnijem ORM radu

`price` je definisana kao `NUMERIC(10, 2)`, ali SQLite ne garantuje istu fiksnu decimalnu preciznost kao neke druge baze.

Status dozvoljava samo dve vrednosti: `draft` i `published`. Strani ključevi povezuju stavke sa postojećim korisnikom i kategorijom, pod uslovom da je `PRAGMA foreign_keys` uključen.

Ove vežbe prave početnu šemu direktno u ciljnoj PortfolioItemsAPI bazi. Kasnije, kada se aplikacija pokrene iz `fast-api-course-my-work`, relativni URL `sqlite:///./PortfolioItemsAPI/data/portfolioitemsapp.db` pokazuje na isti fajl. `create_all()` može da napravi tabele koje nedostaju, ali ne menja postojeće tabele; za promene šeme ćemo kasnije učiti migracije.
