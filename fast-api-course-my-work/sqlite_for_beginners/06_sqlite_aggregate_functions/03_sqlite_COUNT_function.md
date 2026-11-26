# 03 — SQLite `COUNT()` funkcija

## Cilj lekcije

`COUNT()` broji ulazne redove ili vrednosti koje nisu `NULL`. Razlika između `COUNT(*)`, `COUNT(izraz)` i `COUNT(DISTINCT izraz)` određuje šta se tačno broji, pa nije dovoljno samo dodati funkciju u upit.

U ovoj lekciji koristićemo tabelu `customers` i tabelu `tracks` iz Chinook baze. Takođe ćemo videti kako `COUNT()` radi sa `GROUP BY`, praznim skupom, `NULL` vrednostima i rezultatima `JOIN`-a.

Prethodno: [uvod u agregatne funkcije](./01_introduction_to_sqlite_aggregate_functions.md). Povezane lekcije: [`AVG()`](./02_sqlite_AVG_function.md), [`GROUP BY`](./08_sqlite_GROUP_BY_clause.md) i [`HAVING`](./09_sqlite_HAVING_clause.md).

## Osnovna sintaksa

```sql
COUNT(*)
COUNT(izraz)
COUNT(DISTINCT izraz)
```

- `COUNT(*)` broji sve ulazne redove.
- `COUNT(izraz)` broji redove u kojima je vrednost izraza različita od `NULL`.
- `COUNT(DISTINCT izraz)` broji različite vrednosti izraza koje nisu `NULL`.

`COUNT(*)` ne znači da SQLite broji sve kolone jednu po jednu. Zvezdica označava svaki ulazni red. To je najjasniji oblik kada želiš ukupan broj redova.

`COUNT(1)` takođe broji svaki ulazni red zato što je izraz `1` za svaki red nenulta vrednost. Za ovu namenu daje isti rezultat kao `COUNT(*)`, ali `COUNT(*)` jasnije izražava da se broje redovi. Nasuprot tome, `COUNT(nullable_column)` preskače redove u kojima je kolona `NULL`.

## Brojanje svih redova sa `COUNT(*)`

Transkript počinje brojanjem kupaca:

```sql
SELECT COUNT(*) AS customer_count
FROM customers;
```

U priloženoj Chinook kopiji rezultat je `59`: u tabeli `customers` nalazi se 59 redova. Alias `customer_count` je naziv izlazne kolone za ovaj rezultat; ne dodaje se u šemu tabele.

`COUNT(*)` broji ulazne redove nakon primene `FROM`, spajanja i `WHERE` filtera. Ne broji redove koji su odbačeni uslovom `WHERE`.

## `COUNT(*)` i `COUNT(kolona)`

`COUNT(kolona)` zanemaruje `NULL`, ali računa i nulu i prazan tekst jer su to vrednosti, a ne `NULL`:

```sql
SELECT
    COUNT(*) AS all_customers,
    COUNT(Company) AS customers_with_company,
    COUNT(DISTINCT Country) AS distinct_countries
FROM customers;
```

Rezultat u trenutnoj kopiji je `59 | 10 | 24`.

- `COUNT(*)` broji svih 59 redova.
- `COUNT(Company)` broji samo redove sa popunjenom vrednošću `Company`; rezultat je 10.
- `COUNT(DISTINCT Country)` broji različite države koje nisu `NULL`; rezultat je 24.

Ako kolona sadrži `0`, `''` ili tekst, `COUNT(kolona)` ih broji. Funkcija proverava da li je izraz `NULL`, a ne da li je vrednost „smislena“ ili nenulta.

### Mali primer sa `NULL`, nulom i praznim tekstom

```sql
WITH sample(value) AS (
    VALUES (NULL), (0), (''), ('x')
)
SELECT
    COUNT(*) AS row_count,
    COUNT(value) AS non_null_count,
    COUNT(DISTINCT value) AS distinct_non_null_count
FROM sample;
```

Očekivano: `4 | 3 | 3`. `NULL` se ne broji u `COUNT(value)`, dok se `0`, prazan tekst i `'x'` broje. U ovom skupu tri nenulte vrednosti su različite.

## `COUNT(DISTINCT ...)`

`DISTINCT` uklanja ponovljene vrednosti izraza pre brojanja. Ne uklanja redove iz tabele i ne menja podatke:

```sql
SELECT
    COUNT(*) AS invoice_rows,
    COUNT(Total) AS totals_present,
    COUNT(DISTINCT Total) AS distinct_totals
FROM invoices;
```

U priloženoj kopiji rezultat je `412 | 412 | 23`: ima 412 računa, svih 412 imaju `Total`, ali se pojavljuju 23 različita iznosa.

Za ponovljene vrednosti, `COUNT(*)` može biti veći od `COUNT(DISTINCT kolona)`. To ne znači da su redovi duplikati: dva računa mogu imati isti iznos, a i dalje biti različiti računi.

U SQLite-u `COUNT(DISTINCT izraz)` prima jedan izraz. Ako želiš da prebrojiš različite kombinacije više kolona, prvo izdvoji jedinstvene parove ili kombinacije u podupitu:

```sql
SELECT COUNT(*) AS distinct_country_city_pairs
FROM (
    SELECT DISTINCT BillingCountry, BillingCity
    FROM invoices
);
```

Ne koristi `COUNT(DISTINCT *)` za brojanje jedinstvenih redova; taj oblik nije podržana SQLite sintaksa. Izaberi eksplicitno kolone koje određuju jedinstvenost.

### Kako se određuje da li su vrednosti različite

`DISTINCT` koristi SQLite pravila poređenja za izraz, uključujući kolaciju teksta. Sa uobičajenom `BINARY` kolacijom, `'a'` i `'A'` su različite vrednosti; uz `NOCASE` kolaciju tretiraju se kao jednake:

```sql
WITH sample(value) AS (
    VALUES ('a'), ('A'), (NULL)
)
SELECT
    COUNT(DISTINCT value) AS binary_distinct_count,
    COUNT(DISTINCT value COLLATE NOCASE) AS nocase_distinct_count
FROM sample;
```

Rezultat je `2 | 1`. `NULL` se ne broji ni u jednom izrazu. Kolaciju izaberi prema pravilima domena: na primer, brojanje različitih korisničkih imena bez razlikovanja velikih i malih slova može zahtevati `COLLATE NOCASE`. Nemoj menjati kolaciju nasumično jer time menjaš definiciju jedinstvenosti.

Kada brojiš različite kombinacije više kolona preko podupita, `SELECT DISTINCT` može da vrati kombinacije koje sadrže `NULL`; spoljašnji `COUNT(*)` broji te kombinacije. To se razlikuje od `COUNT(DISTINCT jedna_kolona)`, koji izostavlja `NULL` iz te kolone. Uvek odluči da li kombinacije sa nedostajućim delom treba da budu deo rezultata.

## `COUNT()` sa `GROUP BY`: broj numera po albumu

U transkriptu se broje numere u svakom albumu:

```sql
SELECT
    AlbumId,
    COUNT(TrackId) AS track_count
FROM tracks
GROUP BY AlbumId
ORDER BY track_count DESC, AlbumId;
```

`GROUP BY AlbumId` formira grupu za svaki album, a `COUNT(TrackId)` broji ID-jeve numera u toj grupi. `TrackId` je primarni ključ i ne može biti `NULL`, zato bi `COUNT(*)` u ovoj tabeli dao isti broj. `COUNT(TrackId)` je blizak transkriptu i jasno broji numere.

Prvi redovi u trenutnoj Chinook kopiji:

| AlbumId | track_count |
| ------: | ----------: |
|     141 |          57 |
|      23 |          34 |
|      73 |          30 |
|     229 |          26 |
|     230 |          25 |

Album 141 ima najviše numera u ovoj kopiji. `AlbumId` je dodat kao tie-breaker, jer više albuma može imati isti broj numera. Bez `ORDER BY` rezultat grupa nema garantovan redosled.

### Razlika između `WHERE` i `HAVING`

`WHERE` filtrira ulazne redove pre grupisanja:

```sql
SELECT AlbumId, COUNT(*) AS track_count
FROM tracks
WHERE Milliseconds >= 60000
GROUP BY AlbumId;
```

`HAVING` filtrira već formirane grupe prema njihovom agregatnom rezultatu:

```sql
SELECT AlbumId, COUNT(*) AS track_count
FROM tracks
GROUP BY AlbumId
HAVING COUNT(*) >= 20
ORDER BY track_count DESC, AlbumId;
```

Ako pitaš „koliko albuma ima najmanje 20 numera?“, spoljašnji upit može prebrojati grupe koje zadovoljavaju `HAVING`:

```sql
SELECT COUNT(*) AS albums_with_at_least_20_tracks
FROM (
    SELECT AlbumId
    FROM tracks
    GROUP BY AlbumId
    HAVING COUNT(*) >= 20
);
```

Ne piši agregatni filter poput `WHERE COUNT(*) >= 20`; `WHERE` se obrađuje pre agregacije, zato za uslov nad grupnim brojem koristi `HAVING`.

## Prazan skup i nedostajuće vrednosti

Agregat bez `GROUP BY` i bez ulaznih redova i dalje vraća jedan rezultatni red. `COUNT(*)` i `COUNT(izraz)` vraćaju `0`:

```sql
SELECT
    COUNT(*) AS row_count,
    COUNT(AlbumId) AS album_ids
FROM tracks
WHERE AlbumId = -1;
```

U trenutnoj kopiji oba rezultata su `0`. Ako se ista prazna selekcija grupiše, ne postoje grupe pa se ne vraćaju izlazni redovi:

```sql
SELECT AlbumId, COUNT(*) AS track_count
FROM tracks
WHERE AlbumId = -1
GROUP BY AlbumId;
```

Za postojeću grupu u kojoj je izraz `NULL` u svim redovima, `COUNT(izraz)` je `0`, dok `COUNT(*)` i dalje broji redove:

```sql
WITH sample(group_id, value) AS (
    VALUES (1, NULL), (1, NULL)
)
SELECT
    group_id,
    COUNT(*) AS rows_in_group,
    COUNT(value) AS non_null_values
FROM sample
GROUP BY group_id;
```

Očekivano: `1 | 2 | 0`. Razlikuj grupu koja postoji, ali nema nenultih vrednosti izraza, od grupe koja uopšte ne postoji.

Prazan ulaz i redovi sa samo `NULL` vrednostima daju različite brojeve redova, iako je `COUNT(value)` u oba slučaja nula:

```sql
WITH empty(value) AS (
    SELECT NULL
    WHERE 0
),
all_null(value) AS (
    VALUES (NULL), (NULL)
)
SELECT 'empty' AS input_case, COUNT(*) AS row_count, COUNT(value) AS value_count
FROM empty
UNION ALL
SELECT 'all NULL', COUNT(*), COUNT(value)
FROM all_null;
```

Rezultat je `empty | 0 | 0` i `all NULL | 2 | 0`. To je korisno kada treba razlikovati nepostojanje redova od redova sa nedostajućim vrednostima.

### Uslovno brojanje

Za brojanje redova koji ispunjavaju uslov možeš koristiti `COUNT(CASE WHEN ... THEN 1 END)`. Kada uslov nije ispunjen, `CASE` vraća `NULL`, pa taj red ne ulazi u `COUNT(izraz)`:

```sql
WITH sample(value) AS (
    VALUES (NULL), (0), (1), (1)
)
SELECT
    COUNT(*) AS all_rows,
    COUNT(CASE WHEN value > 0 THEN 1 END) AS positive_values
FROM sample;
```

Rezultat je `4 | 2`. Nemoj dodati `ELSE 0` u ovaj `CASE`: nula nije `NULL`, pa bi se njome brojali i redovi koji ne ispunjavaju uslov. Ako treba samo da proveriš da li bar jedan red postoji, `EXISTS` izražava tu nameru jasnije nego izračunavanje ukupnog broja.

## `COUNT()` nad `JOIN`-om

Spajanje može da umnoži redove: album sa mnogo numera daje po jedan red za svaku numeru. Zato `COUNT(*)` nad spojenim tabelama može brojati parove, a ne jedinstvene albume:

```sql
SELECT
    COUNT(*) AS track_album_pairs,
    COUNT(DISTINCT a.AlbumId) AS albums,
    COUNT(DISTINCT t.TrackId) AS tracks
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId;
```

U trenutnoj kopiji rezultat je `3503 | 347 | 3503`: `COUNT(*)` broji redove spoja, `COUNT(DISTINCT a.AlbumId)` jedinstvene albume, a `COUNT(DISTINCT t.TrackId)` numere.

Kod `LEFT JOIN`-a pažljivo biraj šta brojiš:

```sql
SELECT
    ar.ArtistId,
    COUNT(*) AS joined_rows,
    COUNT(al.AlbumId) AS album_count
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
GROUP BY ar.ArtistId
ORDER BY ar.ArtistId;
```

Izvođač bez albuma i dalje ima jedan NULL-prošireni rezultatni red, pa mu je `COUNT(*)` jednak `1`. `COUNT(al.AlbumId)` broji stvarne albume, pa je jednak `0`. Za izdvajanje izvođača bez albuma možeš koristiti `HAVING COUNT(al.AlbumId) = 0`.

## Veza sa SQLAlchemy 2.0

SQLAlchemy `func.count()` može da broji redove, a prosleđivanje kolone broji njene nenulte vrednosti. Primer pretpostavlja modele `Track` i `Album`:

```python
from sqlalchemy import func, select

statement = (
    select(
        Track.album_id,
        func.count(Track.track_id).label("track_count"),
    )
    .group_by(Track.album_id)
    .order_by(
        func.count(Track.track_id).desc(),
        Track.album_id,
    )
)
```

Za brojanje svih redova bez grupisanja koristi `select(func.count()).select_from(Track)`. Za jedinstvene vrednosti koristi `func.count(func.distinct(Track.album_id))`. Kao i kod SQL-a, izaberi izraz prema tome da li želiš da brojiš redove, nenulte vrednosti ili različite vrednosti.

## Česte greške

- **Tumačiš `COUNT(*)` kao broj kolona:** broji ulazne redove, ne broj kolona niti broj popunjenih ćelija.
- **Koristiš `COUNT(kolona)` za ukupan broj redova:** `NULL` vrednosti se preskaču; za sve redove koristi `COUNT(*)`.
- **Misliš da se nula ili prazan tekst preskaču:** broje se jer nisu `NULL`.
- **Pobrkaš `COUNT(DISTINCT X)` sa brojem jedinstvenih redova:** broje se jedinstvene nenulte vrednosti jednog izraza.
- **Koristiš `COUNT(*)` nad `LEFT JOIN`-om da nađeš decu:** NULL-prošireni red se broji; broji nenulti ključ desne tabele.
- **Zaboraviš umnožavanje redova posle spajanja:** brojiš parove ili numere umesto jedinstvenih roditelja.
- **Staviš uslov agregata u `WHERE`:** upotrebi `HAVING` ili spoljašnji upit.
- **Očekuješ redove po grupi iz praznog skupa:** nema ulaznih redova, pa `GROUP BY` ne može da napravi grupe.
- **Osloniš se na slučajni redosled grupa:** dodaj `ORDER BY` i tie-breaker kada se vrednosti ponavljaju.

## Vežbe

1. Prebroj kupce pomoću `COUNT(*)`.
2. Uporedi `COUNT(*)`, `COUNT(Company)` i `COUNT(DISTINCT Country)` za kupce.
3. Uporedi broj računa, broj popunjenih `Total` vrednosti i broj različitih iznosa.
4. Prebroj numere po albumu pomoću `COUNT(TrackId)` i sortiraj po broju numera opadajuće, a zatim po `AlbumId`.
5. Pronađi izvođače bez albuma pomoću `LEFT JOIN` i `HAVING COUNT(al.AlbumId) = 0`.
6. Prebroj ulazne redove, nenulte vrednosti i različite vrednosti u skupu `(NULL), (0), (''), ('x')`.
7. Proveri rezultat `COUNT(*)` i `COUNT(AlbumId)` kada `WHERE` ne vrati nijedan red; ponovi sa `GROUP BY`.
8. Spoji `tracks` i `albums`; uporedi broj parova sa brojem različitih albuma i numera.
9. Prebroj različite parove `BillingCountry` i `BillingCity` pomoću podupita sa `SELECT DISTINCT`.
10. Uporedi `COUNT(*)` i `COUNT(1)` i potvrdi da oba broje sve ulazne redove.
11. Prebroj redove koji ispunjavaju uslov pomoću `COUNT(CASE WHEN ... THEN 1 END)`.
12. Uporedi `COUNT(DISTINCT value)` sa `COUNT(DISTINCT value COLLATE NOCASE)` za tekstualne vrednosti `a` i `A`.

## Provera razumevanja

1. Šta broji `COUNT(*)`?
2. Koje vrednosti broji `COUNT(expression)`?
3. Da li se `0`, `''` i tekstualne vrednosti broje u `COUNT(expression)`?
4. Da li `COUNT(DISTINCT expression)` broji `NULL`?
5. Koliko vraća `COUNT(*)` nad praznim ulazom bez `GROUP BY`?
6. Šta se dešava ako praznom upitu dodaš `GROUP BY`?
7. Zašto `COUNT(*)` nad `LEFT JOIN`-om može vratiti `1` za izvođača bez albuma?
8. Koji izraz broji samo stvarne albume u tom `LEFT JOIN`-u?
9. Zašto se broj redova `JOIN`-a može razlikovati od broja jedinstvenih ključeva?
10. Koja je razlika između `WHERE` i `HAVING` pri brojanju grupa?
11. Zašto se `COUNT(*)` i `COUNT(value)` razlikuju kada je `value` `NULL`?
12. Kako kolacija utiče na `COUNT(DISTINCT text_value)`?
13. Zašto `COUNT(CASE WHEN uslov THEN 1 END)` ne treba da ima `ELSE 0` kada brojimo samo podudarne redove?

## Izvori za dalje čitanje

- [SQLite: Aggregate Functions — `count(X)` i `count(*)`](https://www.sqlite.org/lang_aggfunc.html#count)
- [SQLite: SELECT — GROUP BY, HAVING i obrada upita](https://www.sqlite.org/lang_select.html)
