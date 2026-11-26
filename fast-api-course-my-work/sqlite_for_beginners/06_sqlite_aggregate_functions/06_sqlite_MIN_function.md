# 06 — SQLite `MIN()` funkcija

## Cilj lekcije

`MIN()` pronalazi najmanju vrednost izraza među redovima koji ulaze u agregaciju. Bez `GROUP BY` vraća jedan minimum za ceo ulazni skup; uz `GROUP BY` računa minimum zasebno za svaku grupu.

U ovoj lekciji koristimo trajanje numera iz Chinook tabele `tracks`. Transkript koristi podupit da pronađe numeru sa najkraćim trajanjem. Pored tog primera, obrađujemo `NULL`, prazne skupove, izjednačene minimume, tekstualni redosled i kolacije, mešane SQLite tipove i razliku između agregatnog `MIN()` i skalarnog `min()`.

Prethodno: [SQLite `MAX()`](./05_sqlite_MAX_function.md). Povezane lekcije: [uvod u agregatne funkcije](./01_introduction_to_sqlite_aggregate_functions.md), [`AVG()`](./02_sqlite_AVG_function.md), [`GROUP BY`](./08_sqlite_GROUP_BY_clause.md) i [`HAVING`](./09_sqlite_HAVING_clause.md).

## Osnovna sintaksa agregatne funkcije

```text
MIN([DISTINCT] izraz)
```

- `MIN(izraz)` vraća najmanju nenultu vrednost izraza.
- `MIN(DISTINCT izraz)` prvo razmatra različite nenulte vrednosti. Kod minimuma `DISTINCT` ne menja rezultat: ponavljanje najmanje vrednosti ne može je učiniti manjom.
- Funkcija ignoriše `NULL`; ako nema nijedne nenulte vrednosti, rezultat je `NULL`.

`MIN()` ne računa prosek niti proverava kvalitet podataka. Vraća vrednost koja bi se pojavila prva pri sortiranju istog izraza uzlazno, koristeći odgovarajuća SQLite pravila poređenja. Tip rezultata je tip izabrane vrednosti.

## Najkraća numera

Transkript koristi podupit u `WHERE` uslovu: unutrašnji upit izračuna najmanje trajanje, a spoljašnji vrati numeru ili numere sa tim trajanjem:

```sql
SELECT
    TrackId,
    Name,
    AlbumId,
    Milliseconds
FROM tracks
WHERE Milliseconds = (
    SELECT MIN(Milliseconds)
    FROM tracks
)
ORDER BY TrackId;
```

U trenutnoj Chinook kopiji rezultat je:

| TrackId | Name                     | AlbumId | Milliseconds |
| ------: | ------------------------ | ------: | -----------: |
|    2461 | É Uma Partida De Futebol |     200 |         1071 |

Unutrašnji upit vraća skalarno najmanje trajanje, `1071`. Spoljašnji upit zatim pronalazi redove čiji `Milliseconds` odgovara toj vrednosti. Ako više numera deli najmanje trajanje, upit će vratiti sve njih.

### Pretvaranje milisekundi u minute

Jedan minut ima 60.000 milisekundi. Sledeći upit prikazuje razliku između celobrojnih i decimalnih minuta:

```sql
SELECT
    MIN(Milliseconds) AS shortest_milliseconds,
    MIN(Milliseconds) / 60000 AS whole_minutes,
    MIN(Milliseconds) / 60000.0 AS exact_minutes,
    ROUND(MIN(Milliseconds) / 60000.0, 4) AS rounded_minutes
FROM tracks;
```

U trenutnoj kopiji rezultat je `1071 | 0 | 0.01785 | 0.0179`. Kada su oba operanda celobrojna, SQLite celobrojnim deljenjem skraćuje decimalni deo: `1071 / 60000` daje `0`. Za decimalne minute koristi `60000.0`. `ROUND()` zaokružuje broj, ali ne garantuje završne nule u prikazu.

## Minimum po grupi

`GROUP BY` omogućava da se najkraće trajanje izračuna posebno za svaki album:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    MIN(Milliseconds) AS shortest_milliseconds,
    ROUND(MIN(Milliseconds) / 60000.0, 3) AS shortest_minutes
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;
```

Prvi redovi u trenutnoj kopiji:

| AlbumId | track_count | shortest_milliseconds | shortest_minutes |
| ------: | ----------: | --------------------: | ---------------: |
|       1 |          10 |                199836 |            3.331 |
|       2 |           1 |                342562 |            5.709 |
|       3 |           3 |                230619 |            3.844 |
|       4 |           8 |                215196 |            3.587 |
|       5 |          15 |                215875 |            3.598 |

`ORDER BY AlbumId` obezbeđuje predvidljiv redosled grupa. Bez `ORDER BY`, SQL ne garantuje redosled izlaznih redova.

## `MIN()` vraća vrednost, ne automatski ceo red

Agregat `MIN(Milliseconds)` vraća najmanje trajanje; ne vraća automatski `TrackId`, naziv numere ili druge kolone iz reda. Podupit iz transkripta rešava to tako što izračuna minimum, pa spoljašnji upit pronađe odgovarajuće redove.

Isto možeš zapisati pomoću CTE-a:

```sql
WITH shortest_duration AS (
    SELECT MIN(Milliseconds) AS milliseconds
    FROM tracks
)
SELECT
    t.TrackId,
    t.Name,
    t.AlbumId,
    t.Milliseconds
FROM tracks AS t
JOIN shortest_duration AS s
    ON t.Milliseconds = s.milliseconds
ORDER BY t.TrackId;
```

Ako želiš sve najkraće numere po albumu, prvo izračunaj minimum za svaki album, a zatim rezultat spoji nazad sa `tracks`:

```sql
WITH album_minima AS (
    SELECT
        AlbumId,
        MIN(Milliseconds) AS shortest_milliseconds
    FROM tracks
    GROUP BY AlbumId
)
SELECT
    t.AlbumId,
    t.TrackId,
    t.Name,
    t.Milliseconds
FROM tracks AS t
JOIN album_minima AS m
    ON m.AlbumId = t.AlbumId
   AND m.shortest_milliseconds = t.Milliseconds
ORDER BY t.AlbumId, t.TrackId;
```

Spajanje po albumu i minimumu vraća sve numere koje dele minimum u svojoj grupi.

SQLite ima posebno ponašanje za neagregirane kolone u upitu poput `SELECT Name, MIN(Milliseconds) FROM tracks`, ali izbor reda nije pouzdan kada postoji nerešen minimum i takav upit nije prenosiv na druge baze. Za čitljiv i prenosiv rezultat izračunaj minimum pa ga spoji sa tabelom.

## `NULL`, prazan skup i grupe bez vrednosti

`MIN()` ignoriše `NULL`. Među vrednostima `10`, `20` i `NULL`, minimum je `10`; `NULL` se ne tretira kao nula niti kao vrednost manja od ostalih.

Ako agregatni upit bez `GROUP BY` nema ulazne redove ili su sve vrednosti `NULL`, upit i dalje vraća jedan rezultatni red, ali je minimum `NULL`:

```sql
WITH empty(value) AS (
    SELECT 1
    WHERE 0
),
all_null(value) AS (
    VALUES (NULL), (NULL)
)
SELECT
    'empty' AS input_case,
    COUNT(*) AS input_rows,
    MIN(value) AS minimum
FROM empty
UNION ALL
SELECT
    'all NULL',
    COUNT(*),
    MIN(value)
FROM all_null;
```

Rezultat je `empty | 0 | NULL` i `all NULL | 2 | NULL`. `COUNT(*)` pomaže da razlikuješ prazan skup od skupa koji ima redove, ali nema poznate vrednosti.

U obrascu za pronalaženje reda, ako unutrašnji `MIN()` vrati `NULL`, uslov poput `Milliseconds = (SELECT MIN(...))` ne postaje tačan ni za jedan red: poređenje sa `NULL` daje nepoznatu vrednost, pa spoljašnji upit ne vraća redove.

Sa `GROUP BY`:

- Prazan ulaz ne sadrži grupe, pa upit vraća nula redova.
- Postojeća grupa u kojoj su sve vrednosti `NULL` i dalje se vraća, ali je `MIN()` za tu grupu `NULL`.

Ako poslovno pravilo nalaže da odsustvo vrednosti treba prikazati kao nulu, možeš eksplicitno koristiti `COALESCE(MIN(value), 0)`. Nemoj to raditi automatski: nepoznata vrednost i stvarna nula mogu imati različito značenje.

## Duplikati i `DISTINCT`

Ponavljanje iste vrednosti ne utiče na minimum:

```sql
WITH sample(value) AS (
    VALUES (5), (1), (1), (NULL)
)
SELECT
    MIN(value) AS minimum_all,
    MIN(DISTINCT value) AS minimum_distinct
FROM sample;
```

Oba izraza vraćaju `1`. Za razliku od `AVG()` ili `SUM()`, kod kojih duplikati mogu promeniti rezultat, duplikati ne mogu promeniti najmanju vrednost. `DISTINCT` je dozvoljen, ali je za `MIN()` obično suvišan.

## Tekst, kolacija i SQLite tipovi

Za tekstualne vrednosti `MIN()` koristi redosled poređenja izraza, uključujući kolaciju. Podrazumevana `BINARY` kolacija razlikuje velika i mala slova. Kolaciju možeš navesti eksplicitno:

```sql
WITH sample(value) AS (
    VALUES ('a'), ('B'), (NULL)
)
SELECT
    MIN(value) AS binary_minimum,
    MIN(value COLLATE NOCASE) AS nocase_minimum
FROM sample;
```

Rezultat je `B | a`: `BINARY` poređenje bira veliko slovo `B` pre malog `a`, dok se uz `NOCASE` porede kao `b` i `a`, pa je `a` minimum. Ugrađeni SQLite `NOCASE` tretira ASCII velika i mala slova kao jednaka; nije potpuno Unicode case-folding pravilo. Ako se vrednosti smatraju jednakim prema kolaciji, nemoj pretpostaviti koje će izvorno pisanje `MIN()` vratiti.

SQLite koristi storage klase za poređenje. U svom redosledu poređenja numeričke vrednosti dolaze pre tekstualnih, a tekst se poredi prema kolaciji:

```sql
WITH sample(value) AS (
    VALUES (100), ('9'), ('10'), (NULL)
)
SELECT
    MIN(value) AS minimum_value,
    typeof(MIN(value)) AS result_type
FROM sample;
```

Rezultat je `100 | integer`: numerička vrednost dolazi pre tekstualnih vrednosti prema SQLite redosledu tipova. `MIN()` ne pretvara tekst `'9'` ili `'10'` u brojeve, pa nije validacija da kolona sadrži dosledne numeričke podatke. Za minimum broja, obezbedi da vrednosti budu numeričkog tipa.

Datumi u SQLite-u često su sačuvani kao tekst. `MIN(date_text)` može pronaći najraniji datum ako su vrednosti u istom vremenski sortirljivom formatu, na primer `YYYY-MM-DD`. Različiti formati ili tekstualno zapisane vremenske zone ne moraju se poređati hronološki; normalizuj podatke pre poređenja. U Chinook kopiji najraniji račun ima `InvoiceDate` `2009-01-01 00:00:00`.

## Agregatni `MIN()` i skalarni `min()`

SQLite koristi isto ime za agregatnu i skalarnu funkciju, ali im se argumenti i značenje razlikuju:

```sql
SELECT min(10, 20, 5) AS scalar_minimum;
```

Skalarni `min()` sa dva ili više argumenata poredi vrednosti navedene u jednom pozivu i vraća `5`. Ako je neki argument `NULL`, skalarni poziv vraća `NULL`:

```sql
SELECT min(10, NULL, 5) AS scalar_minimum;
```

Agregatni `MIN(value)` obrađuje vrednost izraza kroz redove i ignoriše `NULL` vrednosti:

```sql
WITH sample(value) AS (
    VALUES (10), (NULL), (5)
)
SELECT MIN(value) AS aggregate_minimum
FROM sample;
```

Rezultat je `5`. U agregatnom obliku navodi se jedan izraz; u skalarnom obliku `min(a, b, ...)` poredi se više argumenata jednog reda. Nemoj mešati njihova pravila za `NULL`.

## `WHERE`, `GROUP BY` i `HAVING`

`WHERE` uklanja ulazne redove pre izračunavanja minimuma. `HAVING` odbacuje grupe nakon što se agregat izračuna:

```sql
SELECT
    AlbumId,
    MIN(Milliseconds) AS shortest_milliseconds
FROM tracks
WHERE Milliseconds >= 60000
GROUP BY AlbumId
HAVING MIN(Milliseconds) < 180000
ORDER BY shortest_milliseconds, AlbumId;
```

- `WHERE Milliseconds >= 60000` ograničava numere koje ulaze u računanje.
- `GROUP BY AlbumId` formira grupu za svaki album.
- `MIN(Milliseconds)` pronalazi najkraću od preostalih numera u grupi.
- `HAVING` zadržava albume čiji minimum iznosi manje od 180000 milisekundi.

Uslov nad agregatom, kao što je `MIN(Milliseconds) < 180000`, pripada klauzuli `HAVING`, a ne `WHERE`.

## Veza sa SQLAlchemy 2.0

SQLAlchemy `func.min()` generiše SQL agregat `MIN()`. Primer pretpostavlja ORM model `Track`:

```python
from sqlalchemy import func, select

statement = (
    select(
        Track.album_id,
        func.min(Track.milliseconds).label("shortest_milliseconds"),
    )
    .group_by(Track.album_id)
    .order_by(Track.album_id)
)
```

`label()` daje ime izrazu u rezultatu; ne kreira kolonu u tabeli. `NULL`, tipovi i redosled poređenja i dalje zavise od podataka i dijalekta baze.

## Česte greške

- **Očekuješ da `MIN()` vrati ceo red:** agregat vraća samo vrednost; za povezane kolone koristi podupit ili spajanje.
- **Pretpostaviš da postoji samo jedan red sa minimumom:** više redova mogu deliti istu minimalnu vrednost.
- **Tretiraš `NULL` kao nulu:** `NULL` se ignoriše; bez nenultih vrednosti rezultat je `NULL`.
- **Koristiš celobrojno deljenje za kratka trajanja:** `1071 / 60000` daje `0`; koristi `60000.0` za decimalne minute.
- **Koristiš `MIN(DISTINCT X)` da ukloniš problematične duplikate:** `DISTINCT` ne menja minimum i ne rešava kvalitet podataka.
- **Pretpostaviš da se tekstualne vrednosti porede kao brojevi:** SQLite poredi storage klase i tekst prema kolaciji.
- **Pretpostaviš da je tekstualni minimum hronološki najraniji datum:** to važi samo za dosledan, sortirljiv format.
- **Mešaš agregatni i skalarni oblik:** `MIN(column)` agregira redove, a `min(a, b, ...)` poredi argumente jednog reda.
- **Koristiš `WHERE` za agregatni uslov:** upotrebi `HAVING`.
- **Osloniš se na redosled grupa bez `ORDER BY`:** dodaj eksplicitno sortiranje.

## Vežbe

1. Pronađi najkraće trajanje numere u milisekundama.
2. Pronađi `TrackId`, naziv i album numere koja ima najmanje trajanje.
3. Uporedi `MIN(Milliseconds) / 60000` i `MIN(Milliseconds) / 60000.0`; objasni zašto prvi izraz daje `0`.
4. Izračunaj najkraće trajanje po albumu pomoću `GROUP BY`.
5. Napravi primer sa dve numere istog minimalnog trajanja i vrati obe pomoću podupita.
6. Uporedi `MIN(value)` i `MIN(DISTINCT value)` nad `(5), (1), (1), (NULL)`.
7. Uporedi agregatni `MIN(value)` sa skalarnim `min(10, 20, 5)` i `min(10, NULL, 5)`.
8. Proveri minimum tekstualnih vrednosti uz podrazumevanu kolaciju i uz `COLLATE NOCASE`.
9. Ispitaj `MIN()` nad mešavinom broja `100` i tekstualnih vrednosti `'9'` i `'10'`.
10. Pronađi najraniji datum računa i proveri da li su datumi sačuvani u doslednom formatu.
11. Dodaj `HAVING MIN(Milliseconds) < 180000` na grupisani upit i objasni razliku u odnosu na `WHERE`.

## Provera razumevanja

1. Koju vrednost vraća agregatni `MIN(X)`?
2. Kako `MIN()` postupa sa `NULL` vrednostima?
3. Šta vraća agregatni upit bez `GROUP BY` ako nema redova?
4. Zašto `MIN(DISTINCT X)` obično daje isti rezultat kao `MIN(X)`?
5. Kako možeš dobiti sve redove koji dele minimalnu vrednost?
6. Zašto je `MIN(Milliseconds) / 60000` jednak `0` za najkraću numeru u ovoj kopiji?
7. Kako kolacija utiče na minimum tekstualne vrednosti?
8. Zašto `MIN()` nad mešavinom broja i teksta ne mora da vrati najmanji broj?
9. Koja je razlika između agregatnog `MIN(column)` i skalarnog `min(a, b)`?
10. Zašto se uslov nad grupnim minimumom piše u `HAVING` klauzuli?

## Izvori za dalje čitanje

- [SQLite: Aggregate Functions — `min(X)`](https://www.sqlite.org/lang_aggfunc.html#minunc)
- [SQLite: Core Functions — scalar `min(X,Y,...)`](https://www.sqlite.org/lang_corefunc.html#min_scalar)
- [SQLite: Datatypes and comparison rules](https://www.sqlite.org/datatype3.html#sort_order)
- [SQLite: SELECT — GROUP BY, HAVING i obrada upita](https://www.sqlite.org/lang_select.html)
