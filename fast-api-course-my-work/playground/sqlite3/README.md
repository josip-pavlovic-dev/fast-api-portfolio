# SQLite3 playground

Ovaj folder je odvojeno mesto za vežbanje SQL naredbi direktno u `sqlite3`
terminalu. Nije povezan sa TodoApp-om, PortfolioItemsAPI-jem niti SQLAlchemy
modelima.

## Da li mogu da vežbam bez baze na disku?

Možeš da otvoriš privremenu SQLite bazu u memoriji:

```bash
sqlite3 :memory:
```

U njoj možeš da kreiraš tabele i radiš upite, ali se sve briše kada izađeš
iz SQLite shell-a. Sledeći put počinješ ispočetka.

Ovaj playground koristi drugu opciju: SQLite bazu u posebnoj datoteci
`sqlite_playground.db`. Tabele i potvrđeni podaci ostaju u toj datoteci i
posle zatvaranja terminala. Otvoriš li istu putanju ponovo, nastavljaš tamo
gde si stao.

---

## Otvaranje playground baze

Komandu pokreni iz root-a repozitorijuma:

```bash
sqlite3 fast-api-course-my-work/playground/sqlite3/sqlite_playground.db
```

Ovo otvara postojeću bazu ili pravi datoteku ako još ne postoji. U SQLite
shell-u uključi čitljiv prikaz i proveru stranih ključeva za tu konekciju:

```sql
.headers on
.mode table
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;
.databases
.tables
```

`PRAGMA foreign_keys` treba da vrati `1`. Podešavanje se odnosi na trenutnu
konekciju, pa ga ponovi svaki put kada otvoriš SQLite shell. Sama šema i
podaci se čuvaju u bazi; ovo podešavanje konekcije se ne pamti kao trajno
pravilo.

## Prvo pokretanje: napravi tabele i probne podatke

U SQLite shell-u, nakon što uključiš `foreign_keys`, pokreni:

```sql
.read fast-api-course-my-work/playground/sqlite3/schema.sql
.read fast-api-course-my-work/playground/sqlite3/seed.sql
```

Datoteka `schema.sql` pravi `user_account` i `address`. `seed.sql` dodaje
početne SpongeBob likove i njihove adrese. Obe skripte mogu ponovo da se
pokrenu: tabele se ne brišu, a isti početni korisnici i adrese se ne
dupliraju.

Proveri šta je kreirano i sačuvano:

```sql
.tables
.schema user_account
.schema address
SELECT id, name, fullname FROM user_account ORDER BY id;
SELECT id, email_address, user_id FROM address ORDER BY id;
```

Izađi iz shell-a:

```sql
.quit
```

Zatim ponovo pokreni `sqlite3` komandu iz prethodnog odeljka. Tabele i redovi
će i dalje biti tu.

## Primeri upita za rad

### `SELECT`: izaberi kolone i sortiraj

```sql
SELECT name, fullname
FROM user_account
ORDER BY name;
```

### `WHERE`: filtriraj redove

```sql
SELECT id, name
FROM user_account
WHERE name LIKE 's%';
```

### Proveri `NULL`

```sql
SELECT name
FROM user_account
WHERE fullname IS NULL;
```

Za `NULL` se koristi `IS NULL`, a ne `= NULL`.

### `JOIN`: prikaži korisnike i njihove adrese

```sql
SELECT
    user_account.name,
    address.email_address
FROM user_account
JOIN address ON address.user_id = user_account.id
ORDER BY user_account.name, address.email_address;
```

### `LEFT JOIN`: zadrži i korisnike bez adrese

```sql
SELECT
    user_account.name,
    address.email_address
FROM user_account
LEFT JOIN address ON address.user_id = user_account.id
ORDER BY user_account.name, address.email_address;
```

### `INSERT`: dodaj svoj korisnik

`name` je jedinstven, zato izaberi ime koje još ne postoji:

```sql
INSERT INTO user_account (name, fullname)
VALUES ('my_username', 'Moje puno ime');
```

ID i `created_at` baza postavlja automatski. Ako otvoriš shell ponovo,
korisnik će biti sačuvan.

### Pregledaj izmene pre zatvaranja

```sql
SELECT id, name, fullname, created_at
FROM user_account
ORDER BY id;
```

## Vežbe

Pokušaj da napišeš ove upite bez gledanja primera iznad:

1. Prikaži sve kolone svih korisnika.
2. Prikaži samo `id` i `name`, sortirano od najvećeg `id` ka najmanjem.
3. Pronađi korisnika po `name`.
4. Prikaži korisnike kojima je `fullname` nepoznat.
5. Prikaži sve adrese za jednog korisnika.
6. Prebroj koliko adresa ima svaki korisnik. Uključi i korisnike bez adresa.
7. Dodaj novu adresu koristeći korisnikov `id`.
8. Prikaži sve korisnike, uključujući one bez adrese, pomoću `LEFT JOIN`.
9. Izaberi jednu adresu po njenom `id` i promeni je pomoću `UPDATE`.
10. Obriši jednu probnu adresu pomoću `DELETE`; prvo proveri njen `id`.

Za izmene i brisanja uvek prvo proveri red koji nameravaš da promeniš:

```sql
SELECT * FROM address WHERE id = ID_ADRESE;
```

Zameni `ID_ADRESE` stvarnim brojem. Zatim koristi jednako precizan `WHERE`
uslov u `UPDATE` ili `DELETE`, da ne bi slučajno promenio više redova.

## Važno o čuvanju izmena i Git-u

SQLite shell podrazumevano potvrđuje svaki samostalni iskaz kada se završi.
Ako eksplicitno započneš transakciju sa `BEGIN`, promene postaju trajne tek
po `COMMIT`-u; `ROLLBACK` ih poništava. Nezavršena transakcija se ne čuva
samim zatvaranjem konekcije.

Lokalna datoteka `sqlite_playground.db` namerno je isključena iz Git-a. U njoj
možeš da menjaš i brišeš probne podatke bez uticaja na verzionisane SQL
skripte. `schema.sql` i `seed.sql` opisuju početno stanje, ali se ponovnim
pokretanjem tih skripti ne brišu tvoje tabele niti tvoji drugi podaci.

Playground je nezavisan od nastavne beleške o `CREATE TABLE`; možeš ga
koristiti paralelno sa
[lekcijom o tabelama i `CREATE TABLE`](../../teorija_sqlalchemy_2/priprema_za_kurs/basic_sql_SELECT_INSERT_CREATE_TABLE/01_tabele_i_create_table.md).
