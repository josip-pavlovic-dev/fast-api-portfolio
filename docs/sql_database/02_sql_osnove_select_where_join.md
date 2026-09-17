# 02 SQL osnove: SELECT, WHERE, JOIN

## Uvod

SQL je jezik kojim pričaš sa bazom.
Ako je API spolja, SQL je unutra.

U FastAPI projektu SQL znanje je korisno i kada koristiš ORM,
zato što ORM ipak generiše SQL ispod haube.

## Kreiranje primera tabela

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
```

## INSERT

```sql
INSERT INTO users (username, email)
VALUES ('ana', 'ana@example.com');

INSERT INTO items (title, price, owner_id)
VALUES ('Miska tastatura', 49.99, 1);
```

## SELECT osnova

```sql
SELECT * FROM users;
```

Bolja praksa je birati samo potrebne kolone:

```sql
SELECT id, username FROM users;
```

## WHERE filtriranje

```sql
SELECT id, title, price
FROM items
WHERE price > 20;
```

Kombinovanje uslova:

```sql
SELECT id, title
FROM items
WHERE price >= 10 AND price <= 100;
```

## ORDER BY i LIMIT

```sql
SELECT id, title, price
FROM items
ORDER BY price DESC
LIMIT 5;
```

Korisno za paginaciju i prikaz najnovijih/najskupljih podataka.

## UPDATE

```sql
UPDATE items
SET price = 59.99
WHERE id = 1;
```

Bez WHERE možeš nehotice promeniti sve redove.
To je jedna od najopasnijih početničkih grešaka.

## DELETE

```sql
DELETE FROM items
WHERE id = 1;
```

Isto pravilo: bez WHERE brišeš sve redove.

## JOIN

JOIN spaja podatke iz više tabela.

### INNER JOIN

Vraća samo redove koji imaju poklapanje u obe tabele.

```sql
SELECT i.id, i.title, u.username
FROM items i
INNER JOIN users u ON i.owner_id = u.id;
```

### LEFT JOIN

Vraća sve redove iz leve tabele i poklapanja iz desne.

```sql
SELECT u.id, u.username, i.title
FROM users u
LEFT JOIN items i ON i.owner_id = u.id;
```

Ako korisnik nema item, i.title je NULL.

## Agregacije

### COUNT

```sql
SELECT COUNT(*) AS total_users FROM users;
```

### GROUP BY

```sql
SELECT owner_id, COUNT(*) AS total_items
FROM items
GROUP BY owner_id;
```

### HAVING

```sql
SELECT owner_id, COUNT(*) AS total_items
FROM items
GROUP BY owner_id
HAVING COUNT(*) >= 2;
```

## NULL i tri-vrednosna logika

U SQL svetu NULL znači nepoznato.

- price = NULL nije ispravno.
- koristi se IS NULL ili IS NOT NULL.

```sql
SELECT * FROM items WHERE price IS NULL;
```

## Bezbednost: SQL Injection

Nikada ne spajaj korisnički input direktno u SQL string.

Loše:

```python
query = f"SELECT * FROM users WHERE username = '{username}'"
```

Bolje: parametrizovani upiti (SQLAlchemy ovo radi umesto tebe kada koristis ORM/Core API pravilno).

## Kako se ovo mapira na tvoj CRUD nivo

- GET /items -> SELECT
- GET /items/{id} -> SELECT ... WHERE id = ...
- POST /items -> INSERT
- PUT /items/{id} -> UPDATE ... WHERE id = ...
- DELETE /items/{id} -> DELETE ... WHERE id = ...

## Zadaci

1. Napiši upit koji vraća 10 najnovijih items.

```sql
SELECT * FROM items
ORDER BY created_at DESC
LIMIT 10;
```
2. Napiši upit koji vraća sve users i broj njihovih items.

```sql
SELECT u.id, u.username, COUNT(i.id) AS total_items
FROM users u
LEFT JOIN items i ON i.owner_id = u.id
GROUP BY u.id, u.username;
```
3. Napiši upit koji vraća items sa cenom između 100 i 500 sortirano rastuće.

```sql
SELECT * FROM items
WHERE price BETWEEN 100 AND 500
ORDER BY price ASC;
```
4. Napiši primer UPDATE sa dva polja i sigurnim WHERE.

```sql
UPDATE items
SET price = 199.99, title = 'Updated Title'
WHERE id = 1;
```

## Zaključak

Ako razumeš SELECT/WHERE/JOIN, već imaš bazu za SQLAlchemy ORM.
ORM će ti skratiti kod, ali SQL logika ostaje ista.
