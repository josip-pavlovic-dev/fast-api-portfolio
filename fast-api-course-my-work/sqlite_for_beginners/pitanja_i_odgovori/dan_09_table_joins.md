# Dan 09 — SQLite JOIN: `LEFT`, `INNER`, `CROSS` i `SELF`

> **Važna napomena:** naziv „Dan 09“ je oznaka dokumenta, a ne očekivanje da se sav materijal uradi za jedan dan. Ovaj vodič prati vežbe iz cele oblasti 05, odnosno sve četiri lekcije o spajanju tabela. Slobodno ga rasporedi u više sesija; nastavi kada razumeš trenutnu temu, ne prema kalendaru.

## Cilj oblasti

U ovoj oblasti učiš kako se redovi iz tabela kombinuju i kako izbor vrste spoja menja rezultat:

- `LEFT JOIN` čuva sve redove leve tabele, čak i kada ne postoji poklapanje;
- `INNER JOIN` vraća samo redove koji zadovoljavaju uslov povezivanja;
- `CROSS JOIN` pravi sve moguće kombinacije redova dve tabele;
- `SELF JOIN` koristi istu tabelu u više uloga, na primer zaposleni i rukovodilac.

Ovaj vodič povezuje teoriju i proverene SQL primere:

- [teorija oblasti 05](../05_table_joins/)
- [SQL vežbe oblasti 05](../playground/sql/05_table_joins/)
- [Playground uputstvo](../playground/README.md)
- [plan učenja](../plan_ucenja/sta_je_vazno.md)
- prethodni vodič za [SQLite operatore](./dan_08_some_sqlite_operators.md)

Svaka SQL skripta je samo za čitanje. Prvo pokušaj zadatak samostalno, pa pokreni odgovarajući `-- @block` ili ceo fajl i uporedi rezultat.

## 1. Bezbedan način rada

### Koristi Chinook kopiju samo za čitanje

Vežbe koriste `artists`, `albums`, `tracks`, `media_types` i `employees` iz lokalne Chinook kopije. Ne izvršavaj ih nad bazom FastAPI aplikacije. U SQLite CLI-ju, iz root-a repozitorijuma, otvori kopiju u read-only režimu:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Zatim učitaj jednu skriptu, na primer:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/05_table_joins/01_sqlite_LEFT_join.sql
```

Otvoriće se query-only konekcija. U SQLTools-u izaberi `ChinookPractice` i proveri da pokazuje na `playground/databases/chinook_practice.db`. Svaka skripta sadrži `-- @block` oznake kako bi mogao da izvršiš samo jedan deo.

### Očekivani rezultati zavise od podataka

Brojevi u nastavku provereni su nad priloženom Chinook kopijom. Ako su se podaci promenili, broj redova može biti drugačiji, iako pravila spajanja ostaju ista.

| Provera u Chinook bazi                                                                         | Očekivani rezultat |
| ---------------------------------------------------------------------------------------------- | -----------------: |
| `artists LEFT JOIN albums` — ukupan broj izlaznih redova                                       |                418 |
| Različiti izvođači očuvani u `LEFT JOIN` rezultatu                                             |                275 |
| Različiti povezani albumi                                                                      |                347 |
| Izvođači bez albuma, pronađeni preko `IS NULL`                                                 |                 71 |
| `LEFT JOIN` sa uslovom `al.Title LIKE 'A%'` u `ON` — redovi / izvođači / NULL-prošireni redovi |    282 / 275 / 250 |
| Isti uslov u `WHERE` — redovi / izvođači                                                       |            32 / 25 |
| `tracks INNER JOIN albums` — redovi / različite numere / albumi                                |  3503 / 3503 / 347 |
| Numere bez albuma u trenutnoj kopiji                                                           |                  0 |
| Numere sa albuma `Greatest Hits`                                                               |                 57 |
| `INNER JOIN` rezultat kada je naslov albuma `LIKE 'A%'`                                        |                369 |
| `albums CROSS JOIN media_types`                                                                |     347 × 5 = 1735 |
| Zaposleni / parovi zaposleni–rukovodilac / bez rukovodioca                                     |          8 / 7 / 1 |

Ovi brojevi su provere konkretnih podataka, ne definicije SQL ponašanja. Posebno, isti broj redova za `INNER JOIN` i `LEFT JOIN` nad `tracks` i `albums` važi zato što u ovoj kopiji svaka numera ima album.

---

## 2. Rešenja i objašnjenja vežbi

## Lekcija 01 — `LEFT JOIN`

Teorija: [01_sqlite_LEFT_join.md](../05_table_joins/01_sqlite_LEFT_join.md); radni fajl: [01_sqlite_LEFT_join.sql](../playground/sql/05_table_joins/01_sqlite_LEFT_join.sql)

### Vežba 1 — Prikaži izvođače i njihove albume

```sql
SELECT
    ar.ArtistId,
    ar.Name AS ArtistName,
    al.AlbumId,
    al.Title AS AlbumTitle
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
ORDER BY ar.ArtistId, al.AlbumId
LIMIT 15;
```

`ON` povezuje izvođača sa njegovim albumima preko `ArtistId`. Pošto je `artists` leva tabela, svaki izvođač se sačuva. Izvođač bez albuma dobija `NULL` vrednosti za kolone iz `albums`.

`LIMIT 15` prikazuje samo deo rezultata; ne menja način spajanja i ne znači da ukupno postoji samo 15 parova.

### Vežba 1.1 — Prebroj redove, izvođače, albume i nepoklopljene izvođače

```sql
SELECT
    COUNT(*) AS joined_rows,
    COUNT(DISTINCT ar.ArtistId) AS artists_preserved,
    COUNT(DISTINCT al.AlbumId) AS matched_albums,
    SUM(al.AlbumId IS NULL) AS artists_without_album
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId;
```

Očekivani rezultat u priloženoj kopiji:

| joined_rows | artists_preserved | matched_albums | artists_without_album |
| ----------: | ----------------: | -------------: | --------------------: |
|         418 |               275 |            347 |                    71 |

Brojevi nemaju isto značenje:

- `COUNT(*)` broji svaki izlazni red. Izvođač sa više albuma pravi više redova, a izvođač bez albuma i dalje pravi jedan NULL-prošireni red.
- `COUNT(DISTINCT ar.ArtistId)` broji svakog izvođača jednom.
- `COUNT(DISTINCT al.AlbumId)` broji povezane albume i zanemaruje `NULL`.
- `SUM(al.AlbumId IS NULL)` sabira redove u kojima nema albuma. SQLite izrazi uslova vraćaju `1` za tačno, `0` za netačno.

### Vežba 2 — Pronađi izvođače bez albuma

```sql
SELECT ar.ArtistId, ar.Name
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
WHERE al.AlbumId IS NULL
ORDER BY ar.ArtistId;
```

`LEFT JOIN` najpre sačuva sve izvođače. Za nepoklopljene redove `al.AlbumId` je `NULL`, pa ga `WHERE` uslov pronađe. U trenutnoj kopiji upit vraća 71 izvođača.

Proveravaj nullable ključ sa desne strane koji se inače ne bi očekivao kao `NULL` u stvarnom albumu, najčešće primarni ključ. Ako bi proveravao kolonu koja sme da bude `NULL`, ne bi mogao pouzdano da razlikuješ „nema povezanog reda“ od „povezani red ima NULL u toj koloni“.

### Vežba 3 — Uslov za album u `ON`-u

```sql
SELECT
    COUNT(*) AS result_rows,
    COUNT(DISTINCT ar.ArtistId) AS artists_preserved,
    SUM(al.AlbumId IS NULL) AS null_extended_rows
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
   AND al.Title LIKE 'A%';
```

Rezultat je 282 redova, sa svih 275 izvođača i 250 NULL-proširenih redova. Uslov u `ON`-u ograničava koje albume upariti, ali ne odbacuje izvođače sa leve strane kada odgovarajući album ne postoji. Jedan izvođač može imati više albuma koji ispunjavaju filter, zato `COUNT(*)` može biti veći od broja izvođača.

### Vežba 3.1 — Isti uslov u `WHERE`-u

```sql
SELECT
    COUNT(*) AS result_rows,
    COUNT(DISTINCT ar.ArtistId) AS artists_with_matching_album
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
WHERE al.Title LIKE 'A%';
```

Ovaj upit vraća 32 reda i 25 izvođača. `WHERE` se primenjuje nakon spajanja; kod nepoklopljenog izvođača `al.Title` je `NULL`, a `NULL LIKE 'A%'` nije tačno. Zato se takvi redovi uklanjaju.

Za `LEFT JOIN`, uslov za desnu tabelu u `ON`-u i isti uslov u `WHERE`-u nisu zamenljivi. Kod `INNER JOIN` oba oblika filtera daju isti broj redova za odgovarajući uslov, jer nepoklopljeni redovi već ne ulaze u rezultat.

### Vežba 4 — `COUNT(*)` naspram `COUNT(al.AlbumId)`

```sql
SELECT
    COUNT(*) AS all_joined_rows,
    COUNT(al.AlbumId) AS matched_album_rows,
    COUNT(*) - COUNT(al.AlbumId) AS unmatched_left_rows
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId;
```

U ovoj kopiji dobijamo `418`, `347` i `71`. `COUNT(*)` broji NULL-proširene redove, a `COUNT(al.AlbumId)` ignoriše `NULL` i broji samo poklopljene albume.

### Ivični slučaj — `NULL` ključ se ne poklapa sa `NULL` ključem

```sql
WITH sample_artist(ArtistId) AS (
    VALUES (1), (NULL)
),
sample_album(ArtistId) AS (
    VALUES (1), (NULL)
)
SELECT a.ArtistId, al.ArtistId AS album_artist_id
FROM sample_artist AS a
LEFT JOIN sample_album AS al
    ON al.ArtistId = a.ArtistId
ORDER BY a.ArtistId;
```

Vrednost `1` se poklapa sa `1`, ali `NULL = NULL` nije `TRUE`. Red sa `NULL` na levoj strani se ipak čuva zbog `LEFT JOIN`-a, a desna kolona ostaje `NULL`. Isti prikaz `NULL` zato može označavati nepoklopljen desni red ili vrednost `NULL` u stvarnom povezanom redu; za proveru poklapanja koristi se pouzdan, neprazan ključ desne tabele.

### Kratki odgovori za `LEFT JOIN`

1. **Koja je uloga `ON`-a?** Definiše uslov povezivanja redova, npr. `al.ArtistId = ar.ArtistId`.
2. **Šta se dešava ako izvođač nema album?** Izvođač se zadržava, a kolone albuma dobijaju `NULL`.
3. **Da li `ORDER BY` filtrira izvođače bez albuma?** Ne. Sortira rezultate. Za izdvajanje nepoklopljenih redova koristi `WHERE al.AlbumId IS NULL`.
4. **Zašto se neki izvođači ponavljaju?** Svaki album daje poseban red; to su različiti parovi izvođač–album.
5. **Zašto filter u `ON`-u nije isto što i filter u `WHERE`-u?** `ON` određuje poklapanja; `WHERE` zatim odbacuje redove koji ne ispunjavaju filter.
6. **Da li `LEFT JOIN` čuva nepoklopljene redove desne tabele?** Ne. Čuva redove leve tabele; za čuvanje druge strane promeni redosled tabela ili upotrebi drugi join.

## Lekcija 02 — `INNER JOIN`

Teorija: [02_sqlite_INNER_join.md](../05_table_joins/02_sqlite_INNER_join.md); radni fajl: [02_sqlite_INNER_join.sql](../playground/sql/05_table_joins/02_sqlite_INNER_join.sql)

### Vežba 1 — Spoji numere i albume

```sql
SELECT
    t.TrackId,
    t.Name AS TrackName,
    a.AlbumId,
    a.Title AS AlbumTitle
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
ORDER BY t.TrackId
LIMIT 10;
```

`t` i `a` su alias-i tabela. `ON a.AlbumId = t.AlbumId` povezuje strani ključ numere sa primarnim ključem albuma. `ORDER BY t.TrackId` daje predvidiv redosled, a `LIMIT 10` ograničava samo prikaz.

`JOIN` bez reči `INNER` podrazumeva unutrašnji spoj u SQLite-u:

```sql
FROM tracks AS t
JOIN albums AS a
    ON a.AlbumId = t.AlbumId
```

### Vežba 2 — Prebroj rezultate i različite ključeve

```sql
SELECT
    COUNT(*) AS joined_rows,
    COUNT(DISTINCT t.TrackId) AS distinct_tracks,
    COUNT(DISTINCT a.AlbumId) AS albums_in_result
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId;
```

Očekivano: `3503 | 3503 | 347`. Svaka numera u ovoj kopiji ima poklopljeni album, a album može imati više numera.

Nemoj zaključiti da je broj redova spajanja uvek jednak broju redova prve tabele. Rezultat zavisi od uslova i kardinalnosti: jedan red može imati nula, jedno ili više poklapanja. Kod ovog ključa album je jedinstven, pa se jedna numera poklapa sa najviše jednim albumom.

### Vežba 3 — Naslov albuma koji se ponavlja

```sql
SELECT
    a.AlbumId,
    a.Title AS AlbumTitle,
    COUNT(*) AS track_count
FROM albums AS a
INNER JOIN tracks AS t
    ON t.AlbumId = a.AlbumId
WHERE a.Title = 'Greatest Hits'
GROUP BY a.AlbumId, a.Title;
```

U trenutnoj kopiji `Greatest Hits` ima 57 numera. Rezultat spajanja zato ponavlja naslov 57 puta, po jednom za svaku numeru. To nisu duplikati istog reda numere.

Ako je cilj jedinstvena lista albuma koji imaju numere, izaberi albumov identitet i primeni `DISTINCT`:

```sql
SELECT DISTINCT
    a.AlbumId,
    a.Title
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
ORDER BY a.AlbumId;
```

`DISTINCT` menja oblik rezultata, ne podatke u tabeli. Ne koristi ga samo da bi sakrio ponovljen naslov, jer više različitih redova numera može ispravno pripadati istom albumu.

### Vežba 5 — Poređenje sa `LEFT JOIN`-om

```sql
SELECT COUNT(*) AS inner_join_rows
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId;

SELECT COUNT(*) AS left_join_rows
FROM tracks AS t
LEFT JOIN albums AS a
    ON a.AlbumId = t.AlbumId;
```

Oba broja su 3503 u ovoj bazi zato što sve numere imaju poklapanje. Da pronađeš numere bez albuma, koristi `LEFT JOIN` i proveri desni ključ:

```sql
SELECT t.TrackId, t.Name
FROM tracks AS t
LEFT JOIN albums AS a
    ON a.AlbumId = t.AlbumId
WHERE a.AlbumId IS NULL;
```

U trenutnoj kopiji nema takvih redova. U drugoj bazi rezultat može da se razlikuje. Jednaki brojevi na ovom uzorku ne čine `INNER JOIN` i `LEFT JOIN` semantički zamenljivim.

### Vežba 6 — Filter u `ON`-u i `WHERE`-u

```sql
SELECT COUNT(*) AS matching_tracks
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
   AND a.Title LIKE 'A%';
```

Isti filter se može napisati kao:

```sql
SELECT COUNT(*) AS matching_tracks
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
WHERE a.Title LIKE 'A%';
```

Oba upita vraćaju 369 u ovoj kopiji. Kod `INNER JOIN`-a filter ograničava redove koji ulaze u rezultat; redovi bez poklapanja ionako se izostavljaju.

### Ivični slučaj — poređenje sa `NULL`

```sql
WITH left_values(id) AS (
    VALUES (1), (NULL)
),
right_values(id) AS (
    VALUES (1), (NULL)
)
SELECT l.id AS left_id, r.id AS right_id
FROM left_values AS l
INNER JOIN right_values AS r
    ON l.id = r.id;
```

Rezultat sadrži samo `(1, 1)`. SQL tro-vrednosna logika znači da `NULL = NULL` daje `UNKNOWN`, ne `TRUE`, pa taj par ne ispunjava uslov spoja.

### SQLAlchemy 2.0

Metoda `.join()` pravi unutrašnji spoj. Primer pretpostavlja modele `Track` i `Album` sa prikazanim atributima:

```python
from sqlalchemy import select

statement = (
    select(
        Track.track_id,
        Track.name,
        Album.album_id,
        Album.title,
    )
    .select_from(Track)
    .join(Album, Album.album_id == Track.album_id)
    .order_by(Track.track_id)
)
```

### Kratki odgovori za `INNER JOIN`

1. **Koji redovi ulaze u rezultat?** Samo kombinacije koje zadovolje uslov iz `ON`-a.
2. **Da li spojene kolone moraju imati isto ime?** Ne. Moraju da izražavaju namernu relaciju; ovde su to `tracks.AlbumId` i `albums.AlbumId`.
3. **Zašto se naslov albuma ponavlja?** Jedan album može imati više numera, pa svaki par daje zaseban red.
4. **Šta radi `DISTINCT`?** Uklanja ponovljene izlazne redove po izabranim kolonama; ne menja tabele.
5. **Zašto `NULL` join ključ ne daje poklapanje pomoću `=`?** Poređenje je `UNKNOWN`, a join zadržava samo uslove koji su `TRUE`.
6. **Da li `COUNT(*)` nad spajanjem mora biti broj redova leve tabele?** Ne. Broj zavisi od nula, jednog ili više poklapanja za svaki red.

## Lekcija 03 — `CROSS JOIN`

Teorija: [03_sqlite_CROSS_join.md](../05_table_joins/03_sqlite_CROSS_join.md); radni fajl: [03_sqlite_CROSS_join.sql](../playground/sql/05_table_joins/03_sqlite_CROSS_join.sql)

### Vežba 1 — Kombinuj sve albume sa svim tipovima medija

```sql
SELECT
    a.AlbumId,
    a.Title AS AlbumTitle,
    a.ArtistId,
    m.MediaTypeId,
    m.Name AS MediaTypeName
FROM albums AS a
CROSS JOIN media_types AS m
ORDER BY a.AlbumId, m.MediaTypeId
LIMIT 10;
```

Ovaj upit pravi svaki mogući par; ne proverava da li je album stvarno dostupan u određenom tipu medija. Prvi album se zato pojavljuje pet puta, jednom uz svaki red iz `media_types`.

### Vežba 2 — Izračunaj proizvod

```sql
SELECT
    (SELECT COUNT(*) FROM albums) AS album_count,
    (SELECT COUNT(*) FROM media_types) AS media_type_count,
    (SELECT COUNT(*) FROM albums CROSS JOIN media_types) AS combinations;
```

Očekivano: `347 | 5 | 1735`. Opšte pravilo je:

```text
broj_redova_prve_tabele × broj_redova_druge_tabele
```

Ako jedna strana ima nula redova, proizvod ima nula redova. To se proverava i sa praznom `common table expression` (CTE):

```sql
WITH empty_media_types(MediaTypeId, Name) AS (
    SELECT MediaTypeId, Name
    FROM media_types
    WHERE 0
)
SELECT COUNT(*) AS combinations
FROM albums AS a
CROSS JOIN empty_media_types AS m;
```

Rezultat je `0`.

### Vežba 3 — Izaberi potrebne kolone

```sql
SELECT
    a.AlbumId AS AlbumId,
    a.Title AS AlbumTitle,
    m.MediaTypeId AS MediaTypeId,
    m.Name AS MediaTypeName
FROM albums AS a
CROSS JOIN media_types AS m
ORDER BY a.AlbumId, m.MediaTypeId;
```

`SELECT *` može biti zgodan za kratko istraživanje, ali nad širim tabelama vraća nepotrebne kolone i može sadržati istoimene kolone. Eksplicitno biranje kolona i alias-i čine rezultat jasnijim.

Bez `ORDER BY` redosled nije garantovan. U ovom primeru `AlbumId` i `MediaTypeId` zajedno daju predvidiv redosled kombinacija.

### Ivični slučaj — proceni veličinu rezultata

Četiri reda ukrštena sa tri reda daju 12 kombinacija. Međutim, 5.000 redova ukrštenih sa 3.000 redova daju 15.000.000 redova. Pre pokretanja velikog `CROSS JOIN`-a proveri da li su sve kombinacije zaista potrebne; slučajno izostavljen join uslov često uzrokuje neočekivano veliki rezultat.

SQLite prihvata i zapis `CROSS JOIN ... ON uslov`, ali tada uslov filtrira kombinacije i rezultat više nije puni Dekartov proizvod. Ako želiš da povežeš redove prema uslovu, `INNER JOIN ... ON` jasnije izražava nameru.

### Kratki odgovori za `CROSS JOIN`

1. **Šta je Dekartov proizvod?** Skup svih parova u kojima se svaki red prve tabele kombinuje sa svakim redom druge.
2. **Koliko redova daju tabele sa 6 i 4 reda?** 24.
3. **Šta ako je jedna tabela prazna?** Rezultat je prazan, odnosno 0 redova.
4. **Da li kolone moraju biti povezane ili istog imena?** Ne. `CROSS JOIN` ne zahteva uslov poklapanja.
5. **Da li kombinacija dokazuje stvarnu vezu u podacima?** Ne. Ona je samo generisan par.
6. **Zašto računamo očekivanu veličinu?** Rezultat može da naraste do miliona redova ili više i optereti bazu.

## Lekcija 04 — `SELF JOIN`

Teorija: [04_sqlite_SELF_join.md](../05_table_joins/04_sqlite_SELF_join.md); radni fajl: [04_sqlite_SELF_join.sql](../playground/sql/05_table_joins/04_sqlite_SELF_join.sql)

`SELF JOIN` nije poseban SQL operator. To je obrazac u kom se ista tabela koristi kao dve reference sa različitim alias-ima. U ovom primeru `e` je zaposleni, a `m` njegov rukovodilac.

### Vežba 1 — Prikaži zaposlene uz rukovodioce

```sql
SELECT
    m.EmployeeId AS ManagerId,
    m.FirstName || ' ' || m.LastName AS Manager,
    e.EmployeeId AS DirectReportId,
    e.FirstName || ' ' || e.LastName AS DirectReport,
    e.Title AS DirectReportTitle
FROM employees AS e
INNER JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo
ORDER BY
    m.LastName,
    m.FirstName,
    e.LastName,
    e.FirstName;
```

Ključ je smer uslova: `e.ReportsTo` čuva ID rukovodioca, a `m.EmployeeId` je njegov red. Zato se piše `m.EmployeeId = e.ReportsTo`.

Očekivani parovi u ovoj kopiji:

| Manager          | DirectReport     |
| ---------------- | ---------------- |
| Andrew Adams     | Nancy Edwards    |
| Andrew Adams     | Michael Mitchell |
| Nancy Edwards    | Jane Peacock     |
| Nancy Edwards    | Margaret Park    |
| Nancy Edwards    | Steve Johnson    |
| Michael Mitchell | Laura Callahan   |
| Michael Mitchell | Robert King      |

### Vežbe 2–3 — `INNER JOIN` izostavlja koren, `LEFT JOIN` ga čuva

```sql
SELECT COUNT(*) AS employees
FROM employees;

SELECT COUNT(*) AS manager_report_pairs
FROM employees AS e
INNER JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo;
```

Dobijamo 8 zaposlenih, ali samo 7 parova. Andrew Adams nema rukovodioca, pa je `ReportsTo` vrednost `NULL` i unutrašnji spoj ga izostavlja.

Ako želiš da prikažeš sve zaposlene, koristi `LEFT JOIN` i zadrži `e` na levoj strani:

```sql
SELECT
    e.EmployeeId,
    e.FirstName || ' ' || e.LastName AS Employee,
    m.FirstName || ' ' || m.LastName AS Manager
FROM employees AS e
LEFT JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo
ORDER BY e.EmployeeId;
```

Očekivano je 8 redova; za Andrewa je `Manager` `NULL`. Da pronađeš samo zaposlene bez rukovodioca:

```sql
SELECT e.EmployeeId, e.FirstName, e.LastName
FROM employees AS e
LEFT JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo
WHERE m.EmployeeId IS NULL;
```

### Vežba 4 — Prikaži titule obeju uloga

```sql
SELECT
    m.Title AS ManagerTitle,
    m.FirstName || ' ' || m.LastName AS Manager,
    e.Title AS EmployeeTitle,
    e.FirstName || ' ' || e.LastName AS Employee
FROM employees AS e
INNER JOIN employees AS m
    ON m.EmployeeId = e.ReportsTo
ORDER BY Manager, Employee;
```

Alias-i kolona razlikuju slične vrednosti iz iste tabele. Alias tabele (`e`, `m`) razdvaja uloge u join uslovu, dok alias kolone (`Manager`, `Employee`) daje čitljive nazive izlaznim kolonama.

### Vežba 5 — Stariji implicitni oblik

```sql
SELECT
    m.FirstName || ' ' || m.LastName AS Manager,
    e.FirstName || ' ' || e.LastName AS DirectReport
FROM employees AS e, employees AS m
WHERE m.EmployeeId = e.ReportsTo;
```

U ovom primeru uslov u `WHERE`-u daje rezultat unutrašnjeg spajanja, ali se ne preporučuje kao stil za nove upite. Eksplicitni `JOIN ... ON` jasnije odvaja uslov povezivanja od dodatnih filtera.

### Granica `SELF JOIN`-a

Ovaj upit prikazuje samo neposrednog rukovodioca. Za ceo lanac hijerarhije kroz proizvoljan broj nivoa potreban je rekurzivni CTE, a ne samo jedan self join. Self join može da poredi i druge redove iste tabele; tada pažljivo definiši da li rezultat treba da izostavi poređenje reda sa samim sobom ili obrnute parove.

### Kratki odgovori za `SELF JOIN`

1. **Da li je `SELF JOIN` poseban operator?** Ne. To je ista tabela navedena više puta uz različite alias-e i običan join operator.
2. **Šta predstavljaju `e` i `m`?** `e` je zaposleni, `m` rukovodilac.
3. **Zašto je uslov `m.EmployeeId = e.ReportsTo`?** Vrednost `ReportsTo` zaposlenog upućuje na `EmployeeId` rukovodioca.
4. **Zašto `INNER JOIN` vraća 7, a ne 8 redova?** Zaposleni sa `ReportsTo IS NULL` nema poklapanje i izostavlja se.
5. **Kako `LEFT JOIN` menja rezultat?** Ako je `e` leva strana, čuva svih 8 zaposlenih i daje `NULL` za rukovodioca koji ne postoji.
6. **Da li jedan self join prikazuje celu hijerarhiju?** Ne, samo direktnu vezu između dva nivoa.
7. **Zašto je `JOIN ... ON` poželjniji od implicitnog oblika?** Jasnije odvaja uslov povezivanja od uslova filtriranja.

## 3. Kratka provera razumevanja

1. **Koja je osnovna razlika između `INNER JOIN` i `LEFT JOIN`?** `INNER` odbacuje nepoklopljene redove; `LEFT` čuva sve redove leve tabele i popunjava desne kolone sa `NULL`.
2. **Koji deo upita definiše poklapanje?** `ON`.
3. **Da li `ORDER BY` može da pronađe redove bez albuma?** Ne. Koristi `WHERE desni_ključ IS NULL` posle `LEFT JOIN`-a.
4. **Zašto uslov desne tabele u `WHERE`-u može poništiti svrhu `LEFT JOIN`-a?** Uklanja NULL-proširene redove koji ne zadovoljavaju filter.
5. **Zašto se broj redova spajanja razlikuje od broja redova jedne tabele?** Svaki red može imati nula, jedno ili više poklapanja.
6. **Da li ponovljen naziv albuma nužno znači dupliranu numeru?** Ne. Više numera može pripadati istom albumu.
7. **Koliko kombinacija daje `CROSS JOIN` sa 12 i 8 redova?** 96.
8. **Šta vraća `CROSS JOIN` kada je jedna tabela prazna?** Nula redova.
9. **Da li `CROSS JOIN` dokazuje da su upareni redovi povezani u modelu podataka?** Ne, on generiše sve parove.
10. **Zašto self join koristi alias-e?** Da bi se razlikovale uloge iste tabele, kao što su zaposleni i rukovodilac.
11. **Koji uslov povezuje zaposlenog sa rukovodiocem u Chinook primeru?** `m.EmployeeId = e.ReportsTo`.
12. **Kako `NULL = NULL` utiče na običan join uslov?** Daje `UNKNOWN`, ne `TRUE`, pa ne stvara poklapanje.
13. **Da li rezultat ima garantovan redosled bez `ORDER BY`?** Ne.
14. **Zašto proveravamo broj redova pre velikog `CROSS JOIN`-a?** Proizvod redova može brzo postati ogroman i obično nije željeni rezultat ako je uslov povezivanja izostao.

## 4. Šta je prioritet prema planu učenja?

Najvažnije je da umeš da izabereš join prema željenom rezultatu i objasniš ulogu svakog dela upita:

- `ON` opisuje vezu između redova; `WHERE` filtrira rezultat.
- `INNER JOIN` koristi kada su potrebna samo poklapanja.
- `LEFT JOIN` koristi kada treba sačuvati sve redove leve tabele, uključujući one bez para.
- `CROSS JOIN` koristi namerno za sve kombinacije i unapred proceni veličinu rezultata.
- `SELF JOIN` koristi sa jasnim alias-ima kada različite uloge potiču iz iste tabele.
- Za nepoklopljene redove posle `LEFT JOIN`-a proveravaj pouzdan ključ desne strane sa `IS NULL`.
- Nemoj zaključivati da su redovi duplikati samo zato što se neka vrednost ponavlja. Proveri granularnost rezultata i ključeve.
- Dodaj `ORDER BY` kada ti je potreban stabilan prikaz.

Praktični SQL obrasci važe i u drugim relacionim bazama, ali proveri sintaksu i podršku konkretne baze. SQLAlchemy ne uklanja razlike u ponašanju između baza.

### Predlog rasporeda rada

Ovo je samo predlog, ne obavezan rok:

1. `LEFT JOIN` i izdvajanje nepoklopljenih redova.
2. `INNER JOIN`, ključevi i kardinalnost.
3. `CROSS JOIN` i procena broja kombinacija.
4. `SELF JOIN`, hijerarhije i završna provera razumevanja.

Pređi na sledeći deo kada možeš da predvidiš koje redove će spoj vratiti i da objasniš zašto.
