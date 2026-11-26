# 05 — SQLite `MAX()` funkcija

## Cilj lekcije

`MAX()` pronalazi najveću vrednost izraza među redovima koji ulaze u agregaciju. Bez `GROUP BY` vraća jedan maksimum za ceo ulazni skup; uz `GROUP BY` računa maksimum zasebno za svaku grupu.

U ovoj lekciji koristićemo trajanje numera iz tabele `tracks`. Pored osnovnog primera iz transkripta, obradićemo `NULL`, prazne skupove, tekstualna poređenja i kolacije, ponovljene maksimumе, pronalaženje reda koji sadrži maksimum i razliku između agregatne funkcije i istoimene skalarne funkcije.

Prethodno: [SQLite `SUM()`](./04_sqlite_SUM_function.md). Povezane lekcije: [uvod u agregatne funkcije](./01_introduction_to_sqlite_aggregate_functions.md), [`MIN()`](./06_sqlite_MIN_function.md), [`GROUP BY`](./08_sqlite_GROUP_BY_clause.md) i [`HAVING`](./09_sqlite_HAVING_clause.md).

## Osnovna sintaksa agregatne funkcije

```text
MAX([DISTINCT] izraz)
```

- `MAX(izraz)` vraća najveću nenultu vrednost izraza.
- `MAX(DISTINCT izraz)` prvo razmatra različite nenulte vrednosti. Kod maksimuma `DISTINCT` ne menja rezultat: ponavljanje najveće vrednosti ne može povećati maksimum.
- Funkcija ignoriše `NULL`; ako nema nijedne nenulte vrednosti, rezultat je `NULL`.

`MAX()` ne sabira i ne računa prosek; samo pronalazi ekstremnu vrednost prema SQLite pravilima poređenja. Tip rezultata je tip vrednosti koja je izabrana kao maksimum.

## Najduža numera

Transkript pronalazi najveće trajanje u koloni `Milliseconds` i deli ga sa `60000` da bi dobio minute:

```sql
SELECT
    MAX(Milliseconds) AS longest_milliseconds,
    MAX(Milliseconds) / 60000 AS whole_minutes,
    MAX(Milliseconds) / 60000.0 AS exact_minutes,
    ROUND(MAX(Milliseconds) / 60000.0, 2) AS rounded_minutes
FROM tracks;
```

U trenutnoj Chinook kopiji rezultat je približno:

| longest_milliseconds | whole_minutes | exact_minutes | rounded_minutes |
| -------------------: | ------------: | ------------: | --------------: |
|              5286953 |            88 | 88.1158833333 |           88.12 |

Transkriptov rezultat `88` odgovara izrazu `MAX(Milliseconds) / 60000`: obe vrednosti su celi brojevi, pa SQLite-ovo celobrojno deljenje odbacuje decimalni deo. Za preciznije minute koristi `60000.0`. `ROUND(..., 2)` zaokružuje broj, ali ne garantuje da će prikaz uvek imati završne nule.

Maksimum sam po sebi vraća trajanje, ne podatke o numeri. U trenutnoj kopiji najduža numera je:

| TrackId | Name                   | AlbumId | Milliseconds |
| ------: | ---------------------- | ------: | -----------: |
|    2820 | Occupation / Precipice |     227 |      5286953 |

## Maksimum po grupi

Uz `GROUP BY`, `MAX()` računa najduže trajanje zasebno za svaki album:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    MAX(Milliseconds) AS longest_milliseconds,
    ROUND(MAX(Milliseconds) / 60000.0, 2) AS longest_minutes
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;
```

Prvi redovi u trenutnoj kopiji:

| AlbumId | track_count | longest_milliseconds | longest_minutes |
| ------: | ----------: | -------------------: | --------------: |
|       1 |          10 |               343719 |            5.73 |
|       2 |           1 |               342562 |            5.71 |
|       3 |           3 |               375418 |            6.26 |
|       4 |           8 |               369319 |            6.16 |
|       5 |          15 |               381231 |            6.35 |

`ORDER BY AlbumId` obezbeđuje predvidljiv redosled izlaznih grupa. Bez `ORDER BY`, SQL ne garantuje redosled redova.

## `MAX()` ne vraća automatski red koji sadrži maksimum

Izraz `MAX(Milliseconds)` vraća samo vrednost maksimuma. Ako ti trebaju naziv numere, ID ili druga polja tog reda, pronađi redove čija vrednost odgovara maksimumu:

```sql
SELECT
    TrackId,
    Name,
    AlbumId,
    Milliseconds
FROM tracks
WHERE Milliseconds = (
    SELECT MAX(Milliseconds)
    FROM tracks
)
ORDER BY TrackId;
```

Ovaj oblik vraća sve redove koji dele najveće trajanje. U trenutnoj bazi postoji jedan takav red; u drugom skupu podataka mogu postojati izjednačeni maksimumi.

Mali primer pokazuje da se vraćaju svi redovi sa istom maksimalnom vrednošću:

```sql
WITH sample(track_id, duration) AS (
    VALUES (1, 5), (2, 9), (3, 9)
)
SELECT track_id, duration
FROM sample
WHERE duration = (SELECT MAX(duration) FROM sample)
ORDER BY track_id;
```

Rezultat sadrži redove `2 | 9` i `3 | 9`.

Za sve najduže numere po albumu izračunaj maksimum za svaki album pa ga spoji nazad sa tabelom:

```sql
WITH album_maxima AS (
    SELECT
        AlbumId,
        MAX(Milliseconds) AS longest_milliseconds
    FROM tracks
    GROUP BY AlbumId
)
SELECT
    t.AlbumId,
    t.TrackId,
    t.Name,
    t.Milliseconds
FROM tracks AS t
JOIN album_maxima AS m
    ON m.AlbumId = t.AlbumId
   AND m.longest_milliseconds = t.Milliseconds
ORDER BY t.AlbumId, t.TrackId;
```

Ako više numera u jednom albumu ima isto najduže trajanje, upit zadržava sve te numere.

Nemoj se oslanjati na negrupisane kolone pored agregata, na primer `SELECT Name, MAX(Milliseconds) FROM tracks`. SQLite ima posebno ponašanje za neagregirane kolone uz jedan ugrađeni `MIN()` ili `MAX()`, ali kod izjednačenih maksimuma izbor reda nije pouzdan, a takav upit nije prenosiv na druge baze. Eksplicitno pronađi maksimum pa spoji tabelu kao u primerima iznad.

## `NULL`, prazan skup i grupe bez vrednosti

`MAX()` ignoriše `NULL` argumente. Ako među vrednostima `10`, `20` i `NULL` tražiš maksimum, rezultat je `20`; `NULL` se ne tretira ni kao nula ni kao vrednost veća od ostalih.

Ako nema ulaznih redova ili su sve vrednosti `NULL`, agregatni upit bez `GROUP BY` i dalje vraća jedan rezultatni red, ali je maksimum `NULL`:

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
    MAX(value) AS maximum
FROM empty
UNION ALL
SELECT
    'all NULL',
    COUNT(*),
    MAX(value)
FROM all_null;
```

Rezultat je `empty | 0 | NULL` i `all NULL | 2 | NULL`. `COUNT(*)` pomaže da razlikuješ prazan skup od skupa koji sadrži redove bez vrednosti.

Sa `GROUP BY` postoje dve dodatne mogućnosti:

- Ako ulaz nema nijedan red, nema grupa i upit vraća nula redova.
- Ako grupa postoji, ali su sve njene vrednosti za maksimum `NULL`, red grupe postoji, a `MAX()` za nju vraća `NULL`.

Kada poslovno pravilo nalaže da odsustvo vrednosti treba prikazati kao nulu, možeš to eksplicitno uraditi sa `COALESCE(MAX(value), 0)`. Nemoj to raditi automatski: `NULL` može značiti „nema poznate vrednosti“, što nije isto što i maksimum nula.

## Duplikati i `DISTINCT`

Ponovljene vrednosti ne utiču na najveću vrednost:

```sql
WITH sample(value) AS (
    VALUES (1), (1), (5), (NULL)
)
SELECT
    MAX(value) AS maximum_all,
    MAX(DISTINCT value) AS maximum_distinct
FROM sample;
```

Oba izraza vraćaju `5`. Za razliku od `AVG()` ili `SUM()`, kod kojih duplikati mogu promeniti rezultat, uklanjanje duplikata ne može promeniti najveću vrednost. `DISTINCT` je dozvoljen, ali je u ovom slučaju suvišan.

## Tekst, kolacija i SQLite tipovi

Za tekstualne vrednosti `MAX()` koristi redosled poređenja izraza, uključujući kolaciju. Podrazumevana `BINARY` kolacija razlikuje velika i mala slova. Kolaciju možeš navesti eksplicitno:

```sql
WITH sample(value) AS (
    VALUES ('a'), ('B'), (NULL)
)
SELECT
    MAX(value) AS binary_maximum,
    MAX(value COLLATE NOCASE) AS nocase_maximum
FROM sample;
```

Rezultat je `a | B`: podrazumevana `BINARY` kolacija bira malo slovo `a` kao veće od velikog `B`, dok se uz `NOCASE` vrednosti porede kao da su `a` i `b`, pa je `B` maksimum. Ugrađeni SQLite `NOCASE` tretira ASCII velika i mala slova kao jednaka; nije potpuno Unicode case-folding pravilo. Ako se dve vrednosti smatraju jednakim prema kolaciji, nemoj pretpostaviti koje će izvorno pisanje `MAX()` vratiti.

SQLite vrednosti imaju storage klase. Kada `MAX()` poredi mešavinu numeričkog i tekstualnog sadržaja, ne pretvara svaki tekst u broj kao što to mogu numerički agregati. U SQLite redosledu poređenja tekstualne vrednosti dolaze posle numeričkih, a tekst se zatim poredi prema kolaciji:

```sql
WITH sample(value) AS (
    VALUES (100), ('9'), ('10'), (NULL)
)
SELECT
    MAX(value) AS maximum_value,
    typeof(MAX(value)) AS result_type
FROM sample;
```

U SQLite-u rezultat je tekstualna vrednost `'9'`, a `result_type` je `text`: tekstualne vrednosti se porede posle broja `100`, a po podrazumevanoj tekstualnoj kolaciji `'9'` dolazi posle `'10'`. Zato `MAX()` nije provera da li je kolona ispravno tipizirana. Za brojčani maksimum obezbedi dosledne numeričke vrednosti.

Datumi u SQLite-u često su sačuvani kao tekst. `MAX(date_text)` može pronaći najkasniji datum ako su sve vrednosti u istom, vremenski sortirljivom formatu, na primer `YYYY-MM-DD`. Različiti formati ili vremenske zone kao tekst ne moraju se poređati hronološki; normalizuj vrednosti pre poređenja.

## Agregatni `MAX()` i skalarni `max()`

SQLite koristi isto ime za agregatnu i skalarnu funkciju, ali im se argumenti i značenje razlikuju:

```sql
SELECT max(10, 20, 5) AS scalar_maximum;
```

Skalarni `max()` sa dva ili više argumenata poredi vrednosti navedene u jednom pozivu i vraća `20`. Ako je neki argument `NULL`, skalarni poziv vraća `NULL`:

```sql
SELECT max(10, NULL, 5) AS scalar_maximum;
```

Nasuprot tome, agregatni `MAX(value)` obrađuje vrednost izraza kroz redove i ignoriše `NULL` vrednosti. U agregatnom obliku navodi se jedan izraz:

```sql
SELECT MAX(Milliseconds)
FROM tracks;
```

Dakle, `MAX(column)` u upitu nad tabelom je agregat, dok je `max(value1, value2, ...)` skalarna funkcija. Nemoj mešati njihova pravila za `NULL`.

## `WHERE`, `GROUP BY` i `HAVING`

`WHERE` uklanja ulazne redove pre izračunavanja maksimuma. `HAVING` odbacuje grupe nakon što se agregat izračuna:

```sql
SELECT
    AlbumId,
    MAX(Milliseconds) AS longest_milliseconds
FROM tracks
WHERE Milliseconds >= 60000
GROUP BY AlbumId
HAVING MAX(Milliseconds) > 300000
ORDER BY longest_milliseconds DESC, AlbumId;
```

- `WHERE Milliseconds >= 60000` ograničava numere koje ulaze u računanje.
- `GROUP BY AlbumId` pravi po jednu grupu za svaki album.
- `MAX(Milliseconds)` računa najdužu od preostalih numera u grupi.
- `HAVING` zadržava albume čiji maksimum prelazi 300000 milisekundi.

Uslov nad agregatom, kao što je `MAX(Milliseconds) > 300000`, pripada klauzuli `HAVING`, a ne `WHERE`.

## Veza sa SQLAlchemy 2.0

SQLAlchemy `func.max()` generiše SQL agregat `MAX()`. Primer pretpostavlja ORM model `Track`:

```python
from sqlalchemy import func, select

statement = (
    select(
        Track.album_id,
        func.max(Track.milliseconds).label("longest_milliseconds"),
    )
    .group_by(Track.album_id)
    .order_by(Track.album_id)
)
```

`label()` daje ime izrazu u rezultatu; ne kreira kolonu u tabeli. `NULL`, tipovi i redosled poređenja i dalje zavise od podataka i dijalekta baze.

## Česte greške

- **Tretiraš `MAX()` kao numeričku konverziju:** mešane tekstualne i numeričke storage klase mogu dati maksimum koji nije najveći broj.
- **Očekuješ da maksimum vrati ceo red:** agregat vraća vrednost; za povezane kolone pronađi redove podupitom ili spajanjem.
- **Pretpostaviš da postoji samo jedan red sa maksimumom:** više redova mogu deliti istu maksimalnu vrednost.
- **Pretpostaviš da se `NULL` računa kao nula:** `NULL` se ignoriše; bez nenultih vrednosti rezultat je `NULL`.
- **Koristiš celobrojno deljenje za minute:** `5286953 / 60000` daje `88`; koristi `60000.0` za decimalne minute.
- **Mešaš agregatni i skalarni oblik:** `MAX(column)` agregira redove, dok `max(a, b, ...)` poredi argumente jednog reda.
- **Dodaješ `DISTINCT` bez razloga:** ponovljene vrednosti ne menjaju maksimum.
- **Zaboravljaš kolaciju teksta:** poređenje stringova može biti osetljivo na velika i mala slova.
- **Koristiš `WHERE` za agregatni uslov:** upotrebi `HAVING`.
- **Oslanjaš se na redosled grupa bez `ORDER BY`:** dodaj eksplicitno sortiranje.

## Vežbe

1. Pronađi najveće trajanje numere u milisekundama.
2. Prikaži isto trajanje kao cele minute i decimalne minute; objasni razliku.
3. Pronađi naziv i ID numere koja ima najveće trajanje. Razmotri kako bi upit postupio kada bi više numera delilo maksimum.
4. Izračunaj najduže trajanje po albumu pomoću `GROUP BY`.
5. Pronađi sve najduže numere po albumu tako što ćeš maksimum po albumu spojiti nazad sa tabelom `tracks`.
6. Uporedi `MAX(value)` i `MAX(DISTINCT value)` nad `(1), (1), (5), (NULL)`.
7. Uporedi rezultat agregatnog `MAX(value)` sa skalarnim `max(10, 20, 5)` i `max(10, NULL, 5)`.
8. Proveri tekstualni maksimum uz podrazumevanu kolaciju i uz `COLLATE NOCASE`.
9. Ispitaj rezultat maksimuma za skup koji sadrži i broj `100` i tekstualne vrednosti `'9'` i `'10'`.
10. Dodaj `HAVING MAX(Milliseconds) > 300000` na grupisani upit i objasni razliku u odnosu na `WHERE`.

## Provera razumevanja

1. Koju vrednost vraća agregatni `MAX(X)`?
2. Kako `MAX()` postupa sa `NULL` vrednostima?
3. Šta vraća agregatni upit bez `GROUP BY` ako nema ulaznih redova?
4. Zašto `MAX(DISTINCT X)` obično daje isti rezultat kao `MAX(X)`?
5. Da li `MAX(X)` vraća i ostale kolone reda u kojem se nalazi maksimum?
6. Kako možeš dobiti sve redove koji dele maksimalnu vrednost?
7. Kako kolacija utiče na maksimum tekstualne vrednosti?
8. Zašto maksimum tekstualne vrednosti `'9'` može biti veći od `'10'`?
9. Koja je razlika između agregatnog `MAX(column)` i skalarnog `max(a, b)`?
10. Zašto se za agregatni uslov koristi `HAVING`, a ne `WHERE`?

## Izvori za dalje čitanje

- [SQLite: Aggregate Functions — `max(X)`](https://www.sqlite.org/lang_aggfunc.html#maxunc)
- [SQLite: Core Functions — scalar `max(X,Y,...)`](https://www.sqlite.org/lang_corefunc.html#max_scalar)
- [SQLite: Datatypes and comparison rules](https://www.sqlite.org/datatype3.html#sort_order)
- [SQLite: SELECT — GROUP BY, HAVING i obrada upita](https://www.sqlite.org/lang_select.html)
