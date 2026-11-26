# 04 — SQLite `SUM()` funkcija

## Cilj lekcije

`SUM()` je agregatna funkcija koja sabira vrednosti izraza iz jednog ili više redova. Bez `GROUP BY` vraća zbir za sve ulazne redove; uz `GROUP BY` računa zaseban zbir za svaku grupu.

U ovoj lekciji koristićemo trajanje numera iz tabele `tracks`. Trajanje je sačuvano u milisekundama, pa ćemo sabrati trajanje po albumu i pretvoriti zbir u minute. Pored primera iz transkripta, obradićemo uticaj `NULL`, `DISTINCT`, praznog skupa, celobrojnog deljenja, prelivanja i floating-point preciznosti.

Prethodno: [uvod u agregatne funkcije](./01_introduction_to_sqlite_aggregate_functions.md). Povezane lekcije: [`AVG()`](./02_sqlite_AVG_function.md), [`COUNT()`](./03_sqlite_COUNT_function.md), [`GROUP BY`](./08_sqlite_GROUP_BY_clause.md) i [`HAVING`](./09_sqlite_HAVING_clause.md).

## Osnovna sintaksa

```sql
SUM([ALL | DISTINCT] izraz)
```

- `SUM(izraz)` sabira sve nenulte vrednosti izraza. To je podrazumevano ponašanje.
- `SUM(ALL izraz)` eksplicitno uključuje ponovljene vrednosti; `ALL` se obično izostavlja.
- `SUM(DISTINCT izraz)` sabira samo različite nenulte vrednosti izraza.

`SUM()` zahteva izraz koji se sabira; za razliku od `COUNT(*)`, ne koristi se oblik `SUM(*)`.

Bez `GROUP BY`, svi redovi koji prođu `WHERE` uslov ulaze u jednu agregaciju:

```sql
SELECT SUM(Total) AS invoice_total
FROM invoices;
```

U priloženoj Chinook kopiji zbir računa je `2328.6`. Broj zavisi od verzije podataka.

## Zbir trajanja numera po albumu

Transkript koristi `GROUP BY` da izdvoji numere svakog albuma, a zatim sabira `Milliseconds` unutar svake grupe:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    SUM(Milliseconds) AS total_milliseconds,
    SUM(Milliseconds) / 60000.0 AS total_minutes,
    ROUND(SUM(Milliseconds) / 60000.0, 2) AS rounded_minutes
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;
```

- `GROUP BY AlbumId` pravi grupu za svaki album.
- `SUM(Milliseconds)` sabira trajanja numera u grupi, u milisekundama.
- Jedan minut ima 60.000 milisekundi, pa se zbir deli sa `60000.0`.
- `ROUND(..., 2)` zaokružuje numeričku vrednost na dve decimale.
- `COUNT(*)` prikazuje broj redova numera u grupi radi provere; nije deo formule za zbir.

Prvi redovi u trenutnoj Chinook kopiji:

| AlbumId | track_count | total_milliseconds | total_minutes | rounded_minutes |
| ------: | ----------: | -----------------: | ------------: | --------------: |
|       1 |          10 |            2400415 | 40.0069166667 |           40.01 |
|       2 |           1 |             342562 |  5.7093666667 |            5.71 |
|       3 |           3 |             858088 | 14.3014666667 |            14.3 |
|       4 |           8 |            2453259 |      40.88765 |           40.89 |
|       5 |          15 |            4411709 | 73.5284833333 |           73.53 |

Ovaj rezultat sadrži 347 grupa albuma. `ORDER BY AlbumId` je važan jer SQL ne garantuje redosled grupa bez sortiranja.

## Važna ispravka: konverzija u minute

U transkriptu su navedeni celi rezultati kao `40`, `5` i `14`. Oni se poklapaju sa celobrojnim deljenjem zbirnih milisekundi sa `60000`, koje odbacuje decimalni deo:

```sql
SELECT
    AlbumId,
    SUM(Milliseconds) / 60000 AS whole_minutes
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;
```

Na primer, drugi album ima zbir `342562` milisekundi. Celobrojno deljenje daje `5`, dok stvarno trajanje iznosi približno `5.71` minuta. Ako želiš preciznije minute, koristi realni delilac `60000.0`:

```sql
SUM(Milliseconds) / 60000.0
```

U SQLite-u, kada su obe strane deljenja celobrojne, rezultat je celobrojan i decimalni deo se skraćuje. Ako jedna strana ima realni tip, rezultat je realan. Ne sabiraj niti zaokružuj po numeri pre pretvaranja, osim ako je to baš željeno pravilo — prvo saberi trajanja, pa konvertuj ukupni zbir.

`ROUND()` vraća numeričku vrednost i ne garantuje završne nule: `40.00` može biti prikazano kao `40.0` ili `40`. Ako je bitan fiksan broj prikazanih decimala, formatiraj rezultat u klijentu.

## `NULL` vrednosti

`SUM()` ignoriše `NULL` argumente. Ako u skupu postoje vrednosti `10`, `20` i `NULL`, zbir je `30`, a ne `NULL` niti `30` uvećano za neku pretpostavljenu nulu:

```sql
WITH sample(value) AS (
    VALUES (10), (20), (NULL)
)
SELECT
    COUNT(*) AS input_rows,
    COUNT(value) AS non_null_values,
    SUM(value) AS total
FROM sample;
```

Očekivano: `3 | 2 | 30`.

Nula je, za razliku od `NULL`, stvarna numerička vrednost i učestvuje u zbiru. `NULL` označava nedostajuću ili nepoznatu vrednost. Nemoj koristiti `COALESCE(value, 0)` automatski; koristi ga samo kada poslovno pravilo izričito kaže da nedostajuće vrednosti treba tretirati kao nulu.

## Prazan skup i `TOTAL()`

Ako agregatni upit bez `GROUP BY` nema nijednu nenultu vrednost za sabiranje, `SUM()` vraća `NULL`. To važi i kada nema ulaznih redova i kada ulazni redovi postoje, ali su sve vrednosti `NULL`:

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
    SUM(value) AS sum_value,
    TOTAL(value) AS total_value
FROM empty
UNION ALL
SELECT
    'all NULL',
    SUM(value),
    TOTAL(value)
FROM all_null;
```

`SUM()` vraća `NULL` u oba slučaja. SQLite-ova posebna funkcija `TOTAL()` vraća `0.0` kada nema nijedne nenulte vrednosti. Za obično numeričko sabiranje koristi `SUM()`; `TOTAL()` je SQLite specifičan i ima drugačiji tip i ponašanje.

Ako upit koristi `GROUP BY` nad praznim ulazom, nema grupa i nema izlaznih redova. Ako grupa postoji, ali su sve njene vrednosti za sabiranje `NULL`, grupa se prikazuje, a `SUM()` za nju je `NULL`.

Kada rezultat bez ulaznih vrednosti treba poslovno da bude nula, to možeš izraziti eksplicitno:

```sql
SELECT COALESCE(SUM(value), 0) AS total
FROM sample;
```

Ovo menja izlazni `NULL` u nulu; ne menja ulazne redove. Ne koristi ga ako „nema podataka“ treba razlikovati od „zbir je nula“.

## `ALL` i `DISTINCT`

Podrazumevani `SUM()` sabira sve vrednosti, uključujući ponovljene:

```sql
WITH sample(value) AS (
    VALUES (1), (1), (NULL)
)
SELECT
    SUM(value) AS default_all,
    SUM(ALL value) AS explicit_all,
    SUM(DISTINCT value) AS distinct_values
FROM sample;
```

Rezultat je `2 | 2 | 1`. `SUM(DISTINCT value)` prvo uklanja ponovljenu vrednost `1`, a zatim sabira jedinstvene nenulte vrednosti.

Pazi šta predstavljaju redovi: dva računa od po 10 dinara jesu dva računa i zbir im je 20, čak iako su vrednosti `Total` iste. `SUM(DISTINCT Total)` bi vratio 10 i zato bi u tom slučaju dao pogrešan poslovni rezultat. `DISTINCT` koristi samo kada želiš zbir jedinstvenih vrednosti, a ne zbir svih događaja ili zapisa.

## SQLite numerički tipovi, overflow i preciznost

### Celi brojevi i prelivanje

Kada su svi nenulti ulazi celi brojevi, `SUM()` vraća celobrojni rezultat. Ako zbir premaši opseg SQLite celog broja sa predznakom, SQLite prijavljuje integer overflow umesto da tiho vrati pogrešan celobrojni rezultat.

Možeš bezbedno reprodukovati granični slučaj u memorijskoj bazi:

```sql
WITH sample(value) AS (
    VALUES (9223372036854775807), (1)
)
SELECT SUM(value)
FROM sample;
```

Ovaj upit namerno prijavljuje integer overflow. Ne pokreći ga nad podacima koje menjaš; izraz ne menja tabelu, ali demonstracija treba da bude odvojena od drugih provera ako želiš da jasno vidiš grešku.

### Realni brojevi i približna aritmetika

Ako zbir uključuje realnu vrednost, `SUM()` vraća približan floating-point rezultat. Na primer, binarni prikaz `0.1` i `0.2` nije potpuno tačan decimalni zapis, pa njihov zbir može biti prikazan kao `0.30000000000000004`.

Za novčane iznose često je sigurnije čuvati najmanju novčanu jedinicu kao ceo broj, na primer cente, i sabirati cele brojeve. Formatiranje ili deljenje za prikaz uradi na kraju. Za specijalizovanu decimalnu aritmetiku SQLite ima decimalnu ekstenziju koja nije deo standardne ugrađene funkcionalnosti.

### Tekstualne vrednosti

SQLite je fleksibilno tipiziran. Tekst koji izgleda kao broj može učestvovati u zbiru kao broj; tekst koji ne može da se protumači numerički i odgovarajuće BLOB vrednosti mogu doprineti kao `0.0`. Zato `SUM()` nije validacija kvaliteta podataka:

```sql
WITH sample(value) AS (
    VALUES ('10'), ('not numeric'), (NULL)
)
SELECT SUM(value) AS total
FROM sample;
```

U SQLite-u ovaj primer daje `10.0`; `'not numeric'` se ne odbacuje kao greška. Pre izračunavanja proveri da kolona sadrži očekivane numeričke vrednosti.

## `WHERE`, `GROUP BY` i `HAVING`

`WHERE` bira ulazne redove pre sabiranja, `GROUP BY` formira grupe, a `HAVING` odbacuje grupe prema izračunatom zbiru:

```sql
SELECT
    AlbumId,
    SUM(Milliseconds) AS total_milliseconds
FROM tracks
WHERE Milliseconds >= 60000
GROUP BY AlbumId
HAVING SUM(Milliseconds) > 1000000
ORDER BY total_milliseconds DESC, AlbumId;
```

- `WHERE Milliseconds >= 60000` izostavlja kraće numere pre sabiranja.
- `GROUP BY AlbumId` pravi zbir po albumu.
- `HAVING` zadržava albume čiji zbir prelazi milion milisekundi.
- `ORDER BY` određuje redosled rezultata.

Za uslov nad agregatom koristi `HAVING`, ne `WHERE SUM(...)`. Agregat se izračunava nad redovima koji su preživeli `WHERE` i grupisanje.

## `SUM()` nakon `JOIN`-a

Agregat sabira redove u rezultatu spajanja. Ako join umnoži isti iznos ili trajanje, `SUM()` će ga sabrati više puta. Pre sabiranja proveri šta predstavlja jedan red ulaznog skupa i da li join ključevi daju očekivanu kardinalnost.

U relaciji tracks–albums jedan album se povezuje sa više numera; sabiranje trajanja numera po albumu je zato očekivano. Ali ako dodaš još jednu tabelu koja stvara više redova po numeri, `SUM(Milliseconds)` može biti uvećan. Nemoj pokušavati da to popraviš slepim dodavanjem `DISTINCT` — ispravi oblik join-a ili pre agregiraj odgovarajući skup.

## Veza sa SQLAlchemy 2.0

SQLAlchemy `func.sum()` generiše SQL agregat `SUM()`. Primer pretpostavlja ORM model `Track`:

```python
from sqlalchemy import func, select

statement = (
    select(
        Track.album_id,
        func.count().label("track_count"),
        func.sum(Track.milliseconds).label("total_milliseconds"),
        func.round(
            func.sum(Track.milliseconds) / 60_000.0,
            2,
        ).label("total_minutes"),
    )
    .group_by(Track.album_id)
    .order_by(Track.album_id)
)
```

`label()` daje ime izrazu u rezultatu; ne kreira kolonu u tabeli. `NULL`, tipovi i numerička preciznost i dalje zavise od vrednosti i dijalekta baze.

## Česte greške

- **Očekuješ da prazan skup da nulu:** `SUM()` vraća `NULL`; SQLite-ov `TOTAL()` vraća `0.0`.
- **Mešaš `NULL` i nulu:** `NULL` se ignoriše, nula učestvuje u zbiru.
- **Koristiš `SUM(DISTINCT X)` da sakriješ dupliranje:** funkcija sabira različite vrednosti, ne jedinstvene zapise.
- **Pretvaraš u cele minute pre agregacije:** gubiš decimalni deo svakog trajanja; saberi milisekunde pa konvertuj ukupan zbir.
- **Zaboravljaš celobrojno deljenje:** `SUM(integer) / 60000` može skratiti decimalni deo; koristi realni delilac ako želiš decimalne minute.
- **Pretpostaviš da tekstualne kolone sadrže validne brojeve:** SQLite može nebrojčani tekst tretirati kao nulu.
- **Ignorišeš overflow ili floating-point preciznost:** veliki celi zbirovi mogu izazvati grešku, a realni zbirovi su približni.
- **Filtriraš zbir u `WHERE`:** upotrebi `HAVING` za uslov nad grupnim rezultatom.
- **Zaboraviš join multiplicitet:** svaki duplirani ulazni red ponovo doprinosi zbiru.
- **Pretpostaviš redosled grupa:** dodaj `ORDER BY` sa tie-breaker-om.

## Vežbe

1. Izračunaj ukupnu vrednost svih računa pomoću `SUM(Total)`.
2. Izračunaj ukupno trajanje numera po albumu u milisekundama i minutima.
3. Uporedi deljenje sa `60000` i `60000.0` za album 1. Objasni razliku.
4. Uporedi `SUM(value)`, `SUM(ALL value)` i `SUM(DISTINCT value)` za vrednosti `(1), (1), (NULL)`.
5. Napravi prazan CTE i CTE sa dve `NULL` vrednosti. Uporedi `SUM()` i `TOTAL()`.
6. Dodaj `COALESCE(SUM(value), 0)` i objasni kada je takva zamena smislena.
7. Proveri `SUM()` nad `0.1` i `0.2` i objasni zašto realni rezultat može biti približan.
8. Pokreni overflow primer samo u memorijskoj bazi i objasni zašto SQLite prijavljuje grešku.
9. Grupisani upit po albumu ograniči pomoću `HAVING SUM(Milliseconds) > 1000000`.
10. Razmisli kako bi dodatni join koji pravi više redova po numeri uticao na zbir trajanja.

## Provera razumevanja

1. Koje vrednosti sabira `SUM(X)`?
2. Da li `SUM(X)` uključuje ponovljene vrednosti podrazumevano?
3. Šta radi `SUM(DISTINCT X)`?
4. Šta `SUM()` vraća ako nema nijedne nenulte vrednosti?
5. Koja je razlika između `SUM()` i `TOTAL()` u SQLite-u?
6. Da li se `NULL` i nula ponašaju isto pri sabiranju?
7. Zašto se trajanje u milisekundama deli sa `60000.0`, a ne sa celim `60000` kada su potrebni decimalni minuti?
8. Šta se dešava ako zbir celobrojnih vrednosti pređe SQLite integer opseg?
9. Zašto zbir floating-point vrednosti može biti neprecizan?
10. Koja klauzula filtrira grupe prema njihovom zbiru?
11. Zašto `SUM()` nad rezultatom join-a može biti veći nego što očekuješ?
12. Zašto `DISTINCT` nije univerzalna popravka za višestruke redove?

## Izvori za dalje čitanje

- [SQLite: Aggregate Functions — `sum(X)` i `total(X)`](https://www.sqlite.org/lang_aggfunc.html#sumunc)
- [SQLite: Expressions — arithmetic operators](https://www.sqlite.org/lang_expr.html)
