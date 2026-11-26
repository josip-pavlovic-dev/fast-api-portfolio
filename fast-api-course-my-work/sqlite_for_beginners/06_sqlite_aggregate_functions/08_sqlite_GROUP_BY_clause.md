# 08 — SQLite `GROUP BY` klauzula

## Cilj lekcije

`GROUP BY` deli ulazne redove u grupe na osnovu jedne ili više vrednosti. Agregatne funkcije kao što su `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()` i `GROUP_CONCAT()` zatim računaju rezultat za svaku grupu.

Transkript koristi tabelu `tracks` i broji numere po albumu. U ovoj lekciji proširićemo taj primer: grupisaćemo po više kolona i izrazima, obradićemo `NULL`, prazne skupove, `WHERE` naspram `HAVING`, SQLite-ovo fleksibilno ponašanje sa negrupisanim kolonama i uticaj spajanja (`JOIN`).

Prethodno: [SQLite `GROUP_CONCAT()`](./07_sqlite_GROUP_CONCAT_function.md). Povezane lekcije: [uvod u agregatne funkcije](./01_introduction_to_sqlite_aggregate_functions.md), [`COUNT()`](./03_sqlite_COUNT_function.md), [`SUM()`](./04_sqlite_SUM_function.md), [`AVG()`](./02_sqlite_AVG_function.md) i [`HAVING`](./09_sqlite_HAVING_clause.md).

## Osnovna sintaksa

```text
SELECT
    grupni_izraz_1,
    grupni_izraz_2,
    agregatna_funkcija(izraz) AS rezultat
FROM tabela
WHERE uslov_za_ulazne_redove
GROUP BY grupni_izraz_1, grupni_izraz_2
HAVING uslov_za_grupe
ORDER BY izlazni_izraz;
```

`WHERE`, `HAVING` i `ORDER BY` su opcioni. `GROUP BY` se koristi kada želiš jedan rezultatni red po grupi; nije obavezan deo svakog `SELECT` upita.

Uobičajeni konceptualni redosled je:

1. `FROM` i `JOIN` određuju ulazne redove.
2. `WHERE` uklanja ulazne redove koji ne ispunjavaju uslov.
3. `GROUP BY` deli preostale redove u grupe.
4. Agregati izračunavaju rezultate za svaku grupu.
5. `HAVING` uklanja grupe koje ne ispunjavaju grupni uslov.
6. `SELECT` određuje izlazne kolone, a `ORDER BY` uređuje rezultat.

Ovo je logički model za razumevanje upita; SQLite može fizički optimizovati izvršavanje.

## Primer iz transkripta: broj numera po albumu

Transkript prikazuje `AlbumId` i broj numera u svakom albumu:

```sql
SELECT
    AlbumId,
    COUNT(TrackId) AS track_count
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;
```

- `GROUP BY AlbumId` pravi jednu grupu za svaki različiti `AlbumId`.
- `COUNT(TrackId)` broji ID-jeve numera unutar svake grupe.
- `ORDER BY AlbumId` sortira rezultat, jer grupisanje samo po sebi ne garantuje redosled.

U priloženoj Chinook kopiji prva tri rezultata su:

| AlbumId | track_count |
| ------: | ----------: |
|       1 |          10 |
|       2 |           1 |
|       3 |           3 |

Upit vraća 347 grupa albuma. U ovoj tabeli `TrackId` je primarni ključ i ne može biti `NULL`, pa bi `COUNT(*)` dao isti broj. Ako bi kolona za brojanje mogla biti `NULL`, `COUNT(kolona)` bi izostavio takve redove; `COUNT(*)` bi ih uključio.

## Kako se formiraju grupe

SQLite izračunava vrednosti grupnih izraza za svaki ulazni red. Redovi sa jednakim vrednostima svih izraza pripadaju istoj grupi. Svaki ulazni red pripada jednoj grupi, a izlazni agregatni upit vraća po jedan rezultatni red za svaku postojeću grupu koja nije uklonjena klauzulom `HAVING`.

### Grupisanje po više kolona

Kada navedeš više izraza, grupa je određena njihovom kombinacijom, odnosno torkom vrednosti:

```sql
SELECT
    BillingCountry,
    BillingCity,
    COUNT(*) AS invoice_count
FROM invoices
GROUP BY BillingCountry, BillingCity
ORDER BY BillingCountry, BillingCity;
```

Grupa predstavlja par `(BillingCountry, BillingCity)`, a ne zasebnu grupu za svaku državu pa zasebno još jednu za svaki grad. U Chinook kopiji prvi parovi su Argentina–Buenos Aires, Australia–Sidney i Austria–Vienne; svaki par ima svoj broj računa.

Redosled izraza u `GROUP BY` obično ne menja koje kombinacije postoje, ali treba uskladiti izabrane kolone i sortiranje tako da rezultat bude razumljiv:

```text
GROUP BY BillingCountry, BillingCity
ORDER BY BillingCountry, BillingCity
```

### Grupisanje po izrazu

Grupišući izraz ne mora biti samo naziv kolone. Možeš grupisati, na primer, po godini i mesecu iz datuma računa:

```sql
SELECT
    substr(InvoiceDate, 1, 7) AS invoice_month,
    COUNT(*) AS invoice_count,
    ROUND(SUM(Total), 2) AS revenue
FROM invoices
GROUP BY substr(InvoiceDate, 1, 7)
ORDER BY invoice_month;
```

U Chinook kopiji prvi meseci su `2009-01` sa 6 računa i `2009-02` sa 7 računa. `substr()` ovde se oslanja na format datuma `YYYY-MM-DD ...`; za drugačije ili neujednačene formate prvo normalizuj vrednosti ili koristi odgovarajuće SQLite date/time izraze.

Radi jasnoće ponovi izraz u `GROUP BY`, umesto da se oslanjaš na poziciju kolone kao što je `GROUP BY 1`. Numeričke pozicije su osetljive na promene redosleda `SELECT` liste.

## Agregati se izračunavaju za svaku grupu

Možeš koristiti više agregata u istom upitu:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    MIN(Milliseconds) AS shortest_milliseconds,
    MAX(Milliseconds) AS longest_milliseconds,
    ROUND(AVG(Milliseconds), 2) AS average_milliseconds,
    SUM(Milliseconds) AS total_milliseconds
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;
```

Svaki agregat obrađuje redove iz iste grupe, ali ima svoja pravila za `NULL`, tipove, duplikate i prazan ulaz. Na primer, `COUNT(*)` broji sve redove, dok `COUNT(Milliseconds)` preskače redove gde je `Milliseconds` `NULL`.

## `WHERE` filtrira redove, `HAVING` filtrira grupe

`WHERE` se primenjuje pre grupisanja i zato utiče na to koji redovi učestvuju u agregatima:

```sql
SELECT
    AlbumId,
    COUNT(*) AS tracks_at_least_one_minute
FROM tracks
WHERE Milliseconds >= 60000
GROUP BY AlbumId
ORDER BY AlbumId;
```

`HAVING` se primenjuje na već formirane grupe i može da koristi agregatne rezultate:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count
FROM tracks
GROUP BY AlbumId
HAVING COUNT(*) >= 20
ORDER BY track_count DESC, AlbumId;
```

Nemoj pisati `WHERE COUNT(*) >= 20`: `WHERE` filtrira pojedinačne redove pre izračunavanja agregata. Uslov koji zavisi od broja redova, zbira, proseka ili drugog agregata pripada `HAVING`.

Možeš koristiti oba filtera u jednom upitu. `WHERE` ograničava ulaz, a `HAVING` zatim filtrira grupne rezultate:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    MAX(Milliseconds) AS longest_milliseconds
FROM tracks
WHERE Milliseconds >= 60000
GROUP BY AlbumId
HAVING COUNT(*) >= 10
ORDER BY track_count DESC, AlbumId;
```

## `NULL` u grupnom ključu i agregatima

`GROUP BY` ne odbacuje `NULL`. Redovi čiji je grupni izraz `NULL` pripadaju istoj grupi:

```sql
WITH sample(category, amount) AS (
    VALUES ('food', 10), (NULL, 5), (NULL, 7), ('food', 2)
)
SELECT
    category,
    COUNT(*) AS row_count,
    SUM(amount) AS total_amount
FROM sample
GROUP BY category
ORDER BY category;
```

Rezultat sadrži grupu `NULL` sa 2 reda i zbirom 12, kao i grupu `food` sa 2 reda i zbirom 12. `NULL` kao grupni ključ nije isto što i uklanjanje reda; ako želiš da ga izostaviš, filtriraj ga u `WHERE`.

`NULL` unutar agregata ima pravila same agregatne funkcije. Na primer, `SUM(value)` ignoriše `NULL`, dok `COUNT(*)` i dalje broji red:

```sql
WITH sample(group_id, value) AS (
    VALUES (1, NULL), (1, NULL), (2, 5)
)
SELECT
    group_id,
    COUNT(*) AS row_count,
    COUNT(value) AS non_null_values,
    SUM(value) AS total
FROM sample
GROUP BY group_id
ORDER BY group_id;
```

Grupa `1` postoji, ima 2 reda i nema nijednu nenultu vrednost: `COUNT(value)` je 0, a `SUM(value)` je `NULL`. Grupa `2` ima zbir 5.

## Prazan ulaz i rezultat bez grupa

Grupisani upit nad praznim ulazom nema grupe, pa vraća nula redova:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count
FROM tracks
WHERE AlbumId = -1
GROUP BY AlbumId;
```

Nasuprot tome, agregatni upit bez `GROUP BY` i dalje računa nad jednom implicitnom grupom:

```sql
SELECT COUNT(*) AS track_count
FROM tracks
WHERE AlbumId = -1;
```

Ovaj upit vraća jedan red sa vrednošću `0`. Drugi agregati, kao što su `SUM()` i `AVG()`, imaju drugačije prazno-skup ponašanje: često vraćaju `NULL`. Ne zaključuj ponašanje svih agregata samo na osnovu `COUNT()`.

Ako postoje grupni redovi, ali nijedan ne prođe `HAVING`, rezultat je takođe prazan, iako su grupe bile formirane pre tog filtera.

## Kolone u `SELECT` listi i SQLite-ove „bare columns“

U standardnom agregatnom upitu, izraz u `SELECT` listi treba da bude:

- grupni izraz,
- ili agregatni izraz.

Na primer, ovo je jasno i prenosivo:

```sql
SELECT AlbumId, COUNT(*) AS track_count
FROM tracks
GROUP BY AlbumId;
```

Ovo je problematično:

```sql
SELECT AlbumId, Name, COUNT(*) AS track_count
FROM tracks
GROUP BY AlbumId;
```

`Name` nije ni grupni izraz ni agregat. SQLite dozvoljava takvu negrupisanu i neagregiranu kolonu (`bare column`) i uzima njenu vrednost iz nekog reda grupe, ali izbor nije određen i može se promeniti sa planom upita ili podacima. Druge baze često odbijaju ovaj upit. Ako želiš grupisati po nazivu, dodaj `Name` u `GROUP BY`; ako želiš jedan reprezentativan naziv, definiši pravilo agregiranja ili izdvoj tačan red zasebnim upitom.

SQLite ima posebno ponašanje za jedan ugrađeni `MIN()` ili `MAX()` uz bare columns, ali su veze između redova i dalje dvosmislene kada postoje izjednačeni minimumi ili maksimumi. Ne koristi to kao zamenu za eksplicitno pronalaženje reda.

## Grupisanje, `DISTINCT` i redosled

`GROUP BY` se obično koristi za rezime po grupama, često zajedno sa agregatima. `SELECT DISTINCT` jasnije izražava da želiš samo jedinstvene vrednosti bez izračunavanja agregata:

```sql
SELECT DISTINCT BillingCountry
FROM invoices
ORDER BY BillingCountry;
```

Ovaj upit vraća listu različitih država. `GROUP BY BillingCountry` bez agregata može proizvesti slične grupisane vrednosti, ali `DISTINCT` bolje opisuje nameru kada ne praviš rezime.

`GROUP BY` ne sortira izlaz. Ako je redosled važan, uvek ga zadaj:

```sql
SELECT BillingCountry, COUNT(*) AS invoice_count
FROM invoices
GROUP BY BillingCountry
ORDER BY invoice_count DESC, BillingCountry;
```

Dodatni `BillingCountry` u `ORDER BY` služi kao tie-breaker kada dve države imaju isti broj računa.

## Kolacija pri grupisanju tekstualnih vrednosti

Poređenje tekstualnih ključeva zavisi od kolacije. Ako treba da se velika i mala ASCII slova grupišu kao ista vrednost, navedi kolaciju:

```sql
WITH sample(value) AS (
    VALUES ('a'), ('A'), ('b')
)
SELECT
    value COLLATE NOCASE AS grouped_value,
    COUNT(*) AS row_count
FROM sample
GROUP BY value COLLATE NOCASE
ORDER BY value COLLATE NOCASE;
```

`a` i `A` pripadaju istoj grupi uz `NOCASE`. Ugrađeni SQLite `NOCASE` nije potpuno Unicode case-folding pravilo. Ako su pravila jedinstvenosti tekstualnih ključeva važna, izaberi i dosledno primenjuj odgovarajuću kolaciju ili normalizaciju.

## `GROUP BY` posle `JOIN`-a

Grupisanje se primenjuje na redove koje je proizveo `FROM` i `JOIN`. Ako spajanje umnoži redove, agregati će videti i brojati te ponovljene redove:

```sql
SELECT
    ar.ArtistId,
    ar.Name,
    COUNT(al.AlbumId) AS album_count
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
GROUP BY ar.ArtistId, ar.Name
ORDER BY ar.ArtistId;
```

Ovde svaki umetnik ima jedan grupni red, a `COUNT(al.AlbumId)` broji spojene albume. Ako dodaš još jednu tabelu sa više odgovarajućih redova po albumu, brojevi mogu biti uvećani. Pre agregiranja proveri šta predstavlja jedan red nakon celog spajanja i, po potrebi, agregiraj podatke u podupitu pre dodatnog `JOIN`-a.

Za `LEFT JOIN`, `COUNT(*)` bi brojao i NULL-prošireni red umetnika bez albuma kao 1. `COUNT(al.AlbumId)` broji samo stvarne albume, jer je njihov ID `NULL` na NULL-proširenom redu.

## Veza sa SQLAlchemy 2.0

U SQLAlchemy 2.0 grupisane kolone navode se sa `.group_by()`. Primer pretpostavlja ORM model `Track`:

```python
from sqlalchemy import func, select

statement = (
    select(
        Track.album_id,
        func.count(Track.track_id).label("track_count"),
        func.min(Track.milliseconds).label("shortest_milliseconds"),
        func.max(Track.milliseconds).label("longest_milliseconds"),
    )
    .group_by(Track.album_id)
    .order_by(Track.album_id)
)
```

Uslov nad agregatom dodaje se pomoću `.having(...)`, a uslov nad pojedinačnim redovima pomoću `.where(...)`. I ovde izabrane negrupisane kolone treba izbeći; SQLite-ovo popustljivije ponašanje nije prenosivo na druge dijalekte.

## Česte greške

- **Izostaviš grupni izraz iz `GROUP BY`:** svaka kombinacija grupnih vrednosti mora biti obuhvaćena.
- **Misliš da grupisanje automatski sortira rezultat:** dodaj `ORDER BY`.
- **Koristiš `WHERE` za agregatni uslov:** agregatne rezultate filtriraj u `HAVING`.
- **Misliš da `NULL` grupni ključ uklanja red:** `NULL` vrednosti grupišu se zajedno; koristi `WHERE` ako treba da ih izostaviš.
- **Pobrkaš `COUNT(*)` i `COUNT(kolona)`:** `COUNT(kolona)` ignoriše `NULL`; `COUNT(*)` broji sve ulazne redove.
- **Očekuješ red za svaku potencijalnu grupu:** grupa se vraća samo ako ima bar jedan ulazni red i prođe `HAVING`.
- **Izabereš bare column:** SQLite može da vrati neodređenu vrednost iz grupe; grupiši kolonu ili je agregiraj.
- **Koristiš `GROUP BY` samo da bi uklonio duplikate:** za jedinstvene vrednosti bez agregata koristi `SELECT DISTINCT`.
- **Zaboraviš da `JOIN` menja broj ulaznih redova:** proveri kardinalnost spajanja pre `COUNT`, `SUM`, `AVG` ili `GROUP_CONCAT`.
- **Koristiš poziciju kolone u `GROUP BY`:** eksplicitno navedi grupni izraz radi čitljivosti i lakšeg održavanja.

## Vežbe

1. Prebroj numere po albumu pomoću `GROUP BY AlbumId`.
2. Dodaj `MIN()`, `MAX()` i `AVG()` trajanja u isti upit.
3. Grupiši račune po državi i gradu, pa prebroj račune u svakoj kombinaciji.
4. Grupiši račune po mesecu koristeći `substr(InvoiceDate, 1, 7)`.
5. Uporedi `WHERE Milliseconds >= 60000` sa `HAVING COUNT(*) >= 10`.
6. Napravi CTE sa `NULL` grupnim ključevima i proveri da li čine jednu grupu.
7. Uporedi prazan agregatni upit bez `GROUP BY` sa istim upitom koji ima `GROUP BY`.
8. Prebroj albume po izvođaču uz `LEFT JOIN`; uporedi `COUNT(*)` i `COUNT(AlbumId)`.
9. Grupiši `a`, `A` i `b` sa podrazumevanom kolacijom i sa `COLLATE NOCASE`.
10. Napiši upit sa bare column-om i objasni zašto ne treba zavisiti od njegovog rezultata.
11. Pronađi države sa najmanje 10 računa pomoću `HAVING`.

## Provera razumevanja

1. Šta predstavlja jedna grupa u upitu sa više grupnih izraza?
2. Koliko rezultatnih redova vraća `GROUP BY`?
3. Koja je razlika između `WHERE` i `HAVING`?
4. Šta se dešava sa redovima koji imaju `NULL` u grupnom ključu?
5. Šta vraća `GROUP BY` nad praznim ulazom?
6. Zašto `COUNT(*)` i `COUNT(column)` mogu dati različit broj u istoj grupi?
7. Zašto bare column nije pouzdan način da izabereš red iz grupe?
8. Da li `GROUP BY` garantuje redosled rezultatnih redova?
9. Kada je `SELECT DISTINCT` jasniji izbor od `GROUP BY`?
10. Kako `JOIN` može da promeni agregatni rezultat posle grupisanja?

## Izvori za dalje čitanje

- [SQLite: SELECT — GROUP BY, HAVING i obrada upita](https://www.sqlite.org/lang_select.html)
- [SQLite: Aggregate Functions](https://www.sqlite.org/lang_aggfunc.html)
- [SQLite: Datatypes and comparison rules](https://www.sqlite.org/datatype3.html)
