# 03: `SELECT`, filtriranje i JOIN

## SELECT bira podatke

`SELECT` čita podatke iz jedne ili više tabela. Osnovni oblik je:

```sql
SELECT kolona_a, kolona_b
FROM ime_tabele;
```

Primer:

```sql
SELECT name, fullname
FROM user_account;
```

Ovo vraća samo dve izabrane kolone za sve redove iz `user_account`. `SELECT *` vraća sve kolone:

```sql
SELECT * FROM user_account;
```

`*` je korisno za brz pregled, ali u aplikacionim upitima je često bolje navesti kolone koje su stvarno potrebne. Tako je namera jasnija, a rezultat ne zavisi od svake buduće kolone koja bude dodata u tabelu.

`SELECT` ne menja redove. On pravi rezultat upita.

## `WHERE` filtrira redove

`WHERE` zadržava samo redove koji zadovoljavaju uslov:

```sql
SELECT name, fullname
FROM user_account
WHERE name = 'sandy';
```

Česti operatori poređenja:

```sql
=       -- jednako
<>      -- nije jednako
>       -- veće od
>=      -- veće ili jednako
<       -- manje od
<=      -- manje ili jednako
```

Primer sa više uslova:

```sql
SELECT id, name
FROM user_account
WHERE id > 1 AND name <> 'patrick';
```

`AND` zahteva da oba uslova važe; `OR` zahteva da važi bar jedan. Kada izraz postane složen, koristi zagrade da jasno prikažeš redosled:

```sql
SELECT name
FROM user_account
WHERE (name = 'sandy' OR name = 'patrick')
  AND id > 1;
```

## `NULL` se proverava posebnim operatorom

SQL `NULL` nije obična tekstualna vrednost i poređenje `= NULL` nije ispravan test. Koristi:

```sql
SELECT name
FROM user_account
WHERE fullname IS NULL;
```

Za prisutnu vrednost koristi `IS NOT NULL`:

```sql
SELECT name
FROM user_account
WHERE fullname IS NOT NULL;
```

Razlikuj:

- `NULL`: vrednost nije prisutna;
- `''`: prisutan je prazan tekst;
- `'NULL'`: prisutan je tekst koji se sastoji od slova `NULL`.

## `IN` i `LIKE`

`IN` proverava da li je vrednost jednaka jednom od navedenih kandidata:

```sql
SELECT name
FROM user_account
WHERE name IN ('sandy', 'patrick');
```

`LIKE` poredi tekst po obrascu. U uobičajenoj SQL sintaksi:

- `%` odgovara nula ili više znakova;
- `_` odgovara tačno jednom znaku.

```sql
SELECT name
FROM user_account
WHERE name LIKE 's%';
```

Ovo traži imena koja počinju sa `s`. Osetljivost na velika/mala slova zavisi od baze i kolacije; SQLite, PostgreSQL i MySQL mogu se ponašati različito.

U aplikacionom kodu vrednosti i dalje treba slati kao bind parametre, a ne spajati ih u SQL tekst. Primer SQLAlchemy `text()` oblika:

```python
statement = text("SELECT name FROM user_account WHERE name = :name")
connection.execute(statement, {"name": user_input})
```

## `ORDER BY` sortira rezultat

Bez `ORDER BY` baza ne garantuje redosled redova. Za predvidljivo sortiranje navedi kolonu:

```sql
SELECT id, name
FROM user_account
ORDER BY name ASC;
```

`ASC` znači uzlazno i podrazumevano je; `DESC` znači silazno:

```sql
SELECT id, name
FROM user_account
ORDER BY id DESC;
```

Može se sortirati po više kolona:

```sql
SELECT id, name
FROM user_account
ORDER BY name ASC, id DESC;
```

Ako redove treba razlikovati kad je `name` isti, dodaj jedinstveniju tie-break kolonu kao `id`.

## JOIN povezuje redove iz povezanih tabela

Pretpostavimo da postoji `address.user_id` strani ključ koji referencira `user_account.id`. Koristimo JOIN da bismo dobili korisnika zajedno sa njegovom adresom:

```sql
SELECT u.name, a.email_address
FROM user_account AS u
JOIN address AS a ON a.user_id = u.id;
```

- `u` i `a` su alias-i tabela koji skraćuju pisanje.
- `ON a.user_id = u.id` kaže koji redovi su povezani.
- `JOIN` bez dodatne reči znači `INNER JOIN`: vraćaju se samo parovi koji imaju poklapanje.

Strani ključ u `CREATE TABLE` i uslov u `JOIN ... ON` su povezani pojmovi, ali nisu ista naredba: FK je pravilo šeme; ON je pravilo za spajanje redova konkretnog upita.

### Zašto je ON uslov važan?

Ovo nije ekvivalentan JOIN:

```sql
SELECT u.name, a.email_address
FROM user_account AS u, address AS a;
```

Bez uslova povezivanja dobija se kartezijanski proizvod: svaki korisnik se uparuje sa svakom adresom. Ako prva tabela ima `m` redova, a druga `n`, rezultat može imati `m × n` kombinacija. Za povezane tabele obično je potreban `JOIN ... ON`.

### `LEFT JOIN`

`LEFT JOIN` (odnosno `LEFT OUTER JOIN`) zadržava sve redove leve tabele. Ako korisnik nema adresu, korisnik se i dalje vraća, a kolone iz `address` imaju `NULL`:

```sql
SELECT u.name, a.email_address
FROM user_account AS u
LEFT JOIN address AS a ON a.user_id = u.id;
```

Ovo je korisno kada želimo da prikažemo sve korisnike, uključujući one koji još nemaju adresu. Standardni `JOIN`/`INNER JOIN` bi takve korisnike izostavio.

## Kako se ovo preslikava u SQLAlchemy?

```python
select(User.name).where(User.name == "sandy").order_by(User.id)
```

približno odgovara:

```sql
SELECT user_account.name
FROM user_account
WHERE user_account.name = ?
ORDER BY user_account.id;
```

SQLAlchemy koristi `User.name` kao mapirani class-level atribut, iz kog zna kolonu i tabelu. String vrednost se šalje kao bind parametar. JOIN oblik:

```python
select(User.name, Address.email_address).join_from(User, Address)
```

može da zaključi ON uslov iz FK metadata-e kada postoji jedna jasna veza. I dalje treba razumeti koji SQL JOIN želimo i kakav će skup redova vratiti.

## SQLite napomena

Primeri u ovom modulu koriste SQLite-kompatibilan SQL. Osnovni `SELECT`, `WHERE`, `ORDER BY` i JOIN oblici su široko prenosivi, ali postoje razlike među bazama u tipovima, string kolacijama, datumskoj sintaksi, placeholder-ima i podršci za određene operatore.
