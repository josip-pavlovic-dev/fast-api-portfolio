# Pitanja i odgovori

## Pitanje 1

Kada koristimo `.schema` u SQLite terminalu, on prikazuje samo definiciju tabela i indeksa koji su trenutno sačuvani u bazi. Ako ne vidimo indekse za `users` i `categories`, moguće je da oni nisu kreirani ili da je došlo do greške prilikom izvršavanja `CREATE INDEX` komandi.

Da li je moguće da SQLite iz nekog razloga nije sačuvao te indekse za `users` i `categories`, ili je možda došlo do greške prilikom izvršavanja `CREATE INDEX` komandi? Kako mogu da proverim da li su ti indeksi zaista kreirani i sačuvani u bazi?

```sql
 CREATE INDEX ix_items_id ON items (id);
```

---

## Odgovor 1

U pravu si — indeksi za `users`, `categories` i `items` postoje. U SQLite terminalu sam proverio metapodatke baze u read-only režimu i našao:

```text
ix_users_id       ON users(id)
ix_categories_id  ON categories(id)
ix_items_id       ON items(id)
```

U početnom DDL-u u `sqlite3_exercises.md` tri `CREATE INDEX` naredbe su stavljene zajedno na kraju, pa je razumljivo da ih je lako povezati samo sa poslednjom tabelom. To što su navedene na kraju ne znači da sve pripadaju tabeli `items`: svaka naredba navodi svoju tabelu.

```sql
CREATE INDEX ix_users_id ON users (id);
CREATE INDEX ix_categories_id ON categories (id);
CREATE INDEX ix_items_id ON items (id);
```

`CREATE TABLE` kreira tabelu, a `CREATE INDEX` kreira poseban objekat baze. Zato SQLite alat obično prikazuje prvo definicije tabela, pa zatim definicije indeksa. Možeš ih pregledati ovako:

```sql
.schema
.indexes
.indexes users
.indexes categories
.indexes items

PRAGMA index_list('users');
PRAGMA index_list('categories');
PRAGMA index_list('items');
```

- `.schema` bez argumenta prikazuje DDL cele baze.
- `.schema items` ograničava prikaz na objekat povezan sa tabelom `items`, pa može prikazati samo njen indeks.
- `.indexes` prikazuje indekse; uz ime tabele prikazuje samo indekse te tabele.
- `PRAGMA index_list('users')` prikazuje indekse za konkretnu tabelu, uključujući poreklo indeksa.

Ako vidiš samo `ix_items_id`, prvo proveri da li si uneo `.schema items` ili `.indexes items`, da li je otvorena prava baza pomoću `.databases`, i da li je ceo izlaz terminala vidljiv.

---

### Šta je SQLite `rowid`?

U običnoj SQLite tabeli, svaki red ima interni ceo broj koji se zove `rowid`. SQLite koristi taj broj da organizuje i pronađe redove u svojoj datoteci baze. Pojednostavljeno, SQLite tabelu sa `rowid`-om možeš zamisliti kao strukturu gde je `rowid` ključ za pronalaženje reda.

Ako tabela nema svoj primarni ključ, `rowid` je i dalje prisutan u pozadini i može se čitati pomoću jednog od imena `rowid`, `_rowid_` ili `oid`, osim ako je kolona sa tim imenom zasenila pristup. On nije obična kolona navedena u `CREATE TABLE` definiciji.

Posebno važan slučaj je:

```sql
CREATE TABLE example (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
```

Kada je kolona **tačno tipa `INTEGER`** i definisana kao jednokolonski `PRIMARY KEY` u običnoj SQLite tabeli, `id` postaje alias za `rowid`. To ne važi za `WITHOUT ROWID` tabelu, a postoji i istorijski izuzetak za oblik `INTEGER PRIMARY KEY DESC` napisan kao definicija kolone.

To znači da `id` i interni `rowid` označavaju isti ključ reda. Primarni ključ zato omogućava brzo pronalaženje po `id`, bez potrebe za još jednim, posebnim indeksom samo radi te pretrage.

SQLite obično dodeljuje `rowid` novom redu kada `INTEGER PRIMARY KEY` kolona nije navedena u `INSERT`-u:

```sql
INSERT INTO example (title) VALUES ('Prvi red');
SELECT id, rowid, title FROM example;
```

Za ovu tabelu će `id` i `rowid` imati istu vrednost. To objašnjava zašto je ID primarnog ključa već efikasan za pretrage.

---

### Zašto se onda pojavljuje `CREATE INDEX ... ON ... (id)`?

U [models.py](../models.py) sva tri `id` polja imaju definisano `index=True` pored `primary_key=True`:

```python
mapped_column(Integer, primary_key=True, index=True)
```

`primary_key=True` označava primarni ključ. `index=True` dodatno traži od SQLAlchemy-ja da napravi indeks. Zato SQLAlchemy generiše imenovane indekse
kao što su `ix_users_id`, `ix_categories_id` i `ix_items_id`.

Za SQLite `INTEGER PRIMARY KEY` već koristi `rowid` mehanizam, pa je dodatni indeks nad istim `id` obično **suvišan**: zauzima prostor i zahteva ažuriranje pri promenama redova, a ne donosi korist za uobičajenu pretragu po primarnom ključu. Ipak, indeks je stvarno kreiran zato što je izričito naveden u DDL-u ili zatražen sa `index=True`.

U ovoj vežbi su indeksi uključeni da bi se naučilo kako se indeksi kreiraju i pregledaju, kao i da bi DDL odgovarao trenutnoj ORM deklaraciji. Kasnije, kada budete sređivali model, ima smisla razmotriti uklanjanje `index=True` sa `id` polja — primarni ključ je dovoljan za pretragu po ID-u.

---

### Važna napomena o automatskom dodeljivanju ID-a

`INTEGER PRIMARY KEY` dodeljuje `rowid` kada ga izostaviš pri unosu, ali SQLite ne obećava da će ID-jevi zauvek biti uzastopni ili da nikada neće biti ponovo upotrebljeni nakon brisanja redova.

`AUTOINCREMENT` menja pravilo tako da se određeni ranije korišćeni `rowid` ne koristi ponovo, ali obično nije potreban i ne znači da ID-jevi neće imati praznine.
Za većinu aplikacija `INTEGER PRIMARY KEY` je dovoljan.

---

### Ukratko

- `rowid` je interni ključ po kome SQLite organizuje redove u običnoj tabeli.
- `id INTEGER PRIMARY KEY` je alias za `rowid`.
- Zato SQLite već može efikasno da pronađe red po `id`.
- `index=True` pravi dodatni imenovani indeks, koji je za ovaj konkretan SQLite primarni ključ uglavnom suvišan.
- `.schema`, `.indexes` i `PRAGMA index_list(...)` pomažu da vidiš šta je zaista definisano u trenutno otvorenoj bazi.
