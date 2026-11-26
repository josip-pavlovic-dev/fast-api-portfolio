# 09 — SQLite `HAVING` klauzula

## Cilj lekcije

`HAVING` filtrira grupe nakon što `GROUP BY` formira grupe i agregatne funkcije izračunaju njihove vrednosti. Koristi se za uslove nad grupnim rezultatima, na primer za pronalaženje albuma sa određenim brojem numera.

Transkript traži albume koji imaju između 18 i 20 numera. U ovoj lekciji razjasnićemo razliku između `WHERE` i `HAVING`, kada `HAVING` može da se koristi bez `GROUP BY`, kako se ponaša sa `NULL` i praznim ulazom, i zašto izraz kojim se broje redovi mora da odgovara stvarnom pitanju.

Prethodno: [`GROUP BY`](./08_sqlite_GROUP_BY_clause.md). Povezane lekcije: [uvod u agregatne funkcije](./01_introduction_to_sqlite_aggregate_functions.md), [`COUNT()`](./03_sqlite_COUNT_function.md), [`SUM()`](./04_sqlite_SUM_function.md), [`AVG()`](./02_sqlite_AVG_function.md) i [`MAX()`](./05_sqlite_MAX_function.md).

## Osnovna sintaksa

```text
SELECT grupni_izraz, agregatna_funkcija(izraz)
FROM tabela
WHERE uslov_za_ulazne_redove
GROUP BY grupni_izraz
HAVING uslov_za_grupe
ORDER BY izlazni_izraz;
```

`WHERE` i `GROUP BY` nisu obavezni u svakom upitu, ali `HAVING` se koristi u kontekstu agregacije. U tipičnom upitu sa grupama, redosled klauzula je `WHERE`, `GROUP BY`, `HAVING`, pa `ORDER BY`.

## Primer iz transkripta: broj numera po albumu

Transkript grupiše redove iz `tracks` po albumu, a zatim zadržava grupe čiji broj numera iznosi od 18 do 20:

```sql
SELECT
    AlbumId,
    COUNT(TrackId) AS track_count
FROM tracks
GROUP BY AlbumId
HAVING COUNT(TrackId) BETWEEN 18 AND 20
ORDER BY AlbumId;
```

- `GROUP BY AlbumId` formira jednu grupu za svaki album.
- `COUNT(TrackId)` računa broj numera u svakoj grupi.
- `HAVING` zadržava albume za koje je broj između 18 i 20.
- `BETWEEN 18 AND 20` uključuje obe granice: prihvata 18, 19 i 20.
- `ORDER BY AlbumId` sortira rezultat uzlazno; ipak je jasnije navesti `ASC` kada želiš eksplicitno označiti smer.

U priloženoj Chinook kopiji rezultat sadrži 16 albuma. Prvi redovi su:

| AlbumId | track_count |
| ------: | ----------: |
|      21 |          18 |
|      37 |          20 |
|      54 |          20 |
|      55 |          20 |
|      72 |          18 |

Uslov u `HAVING` može koristiti agregat koji nije prikazan u `SELECT` listi. Naredni primer prikazuje broj numera, ali zadržava samo albume čije je najduže trajanje veće od 300000 milisekundi:

```sql
SELECT
    AlbumId,
    COUNT(TrackId) AS track_count
FROM tracks
GROUP BY AlbumId
HAVING MAX(Milliseconds) > 300000
ORDER BY AlbumId;
```

`TrackId` je primarni ključ i ne može biti `NULL`, pa je ovde `COUNT(TrackId)` jednak `COUNT(*)`. Brojanje `AlbumId` bi brojalo samo redove sa popunjenim `AlbumId`; ako kolona može biti `NULL`, to možda nije broj redova ili numera koji očekuješ.

## `WHERE` naspram `HAVING`

Glavna razlika je trenutak kada se uslov primenjuje:

- `WHERE` uklanja pojedinačne ulazne redove pre grupisanja i agregacije.
- `HAVING` uklanja cele grupe nakon grupisanja i izračunavanja agregata.

Na primer, ovaj upit prvo bira numere koje traju najmanje tri minuta, zatim broji takve numere po albumu i na kraju zadržava albume sa najmanje tri odgovarajuće numere:

```sql
SELECT
    AlbumId,
    COUNT(*) AS qualifying_track_count
FROM tracks
WHERE Milliseconds >= 180000
GROUP BY AlbumId
HAVING COUNT(*) >= 3
ORDER BY qualifying_track_count DESC, AlbumId;
```

`WHERE Milliseconds >= 180000` deluje na pojedinačne numere. Zato `COUNT(*)` broji samo numere koje su prošle taj uslov. `HAVING COUNT(*) >= 3` zatim odbacuje grupe čiji je taj broj manji od tri.

Nemoj zameniti `WHERE` sa `HAVING` ili obrnuto:

```text
-- Filtrira numere pre brojanja.
WHERE Milliseconds >= 180000

-- Filtrira album nakon brojanja numera.
HAVING COUNT(*) >= 3
```

Uslov nad agregatom, kao što su `COUNT(*) >= 3`, `SUM(Total) > 100` ili `AVG(Milliseconds) < 300000`, ne pripada u `WHERE`, zato što `WHERE` obrađuje pojedinačne redove pre nego što se agregat izračuna.

## `HAVING` bez `GROUP BY`

Transkript navodi da se `HAVING` bez `GROUP BY` ponaša kao `WHERE`. To nije tačno kao opšte pravilo za SQLite. U agregatnom upitu bez `GROUP BY`, svi ulazni redovi čine jednu implicitnu grupu, a `HAVING` prihvata ili odbacuje tu grupu:

```sql
SELECT COUNT(*) AS total_tracks
FROM tracks
HAVING COUNT(*) > 3000;
```

U Chinook kopiji uslov je tačan, pa upit vraća jedan red sa `3503`. Ako promeniš uslov na `HAVING COUNT(*) > 4000`, upit ne vraća nijedan red — cela jedina grupa je odbačena.

`HAVING` se zato ne ponaša kao redni filter `WHERE`. U SQLite-u običan upit bez grupisanja i agregata ne može samo da doda `HAVING` kao zamenu za `WHERE`; za filtriranje redova koristi `WHERE`.

Kada upit nema `GROUP BY`, ali ima agregate, ima jednu implicitnu grupu. Ako je ulaz prazan, `COUNT(*)` za tu grupu je `0`, dok su `SUM()` i druge funkcije koje vraćaju `NULL` na praznom ulazu podložne uobičajenim pravilima za `NULL`. `HAVING` i dalje može da odbaci tu grupu.

## Uslovi, `NULL` i granične vrednosti

Izraz u `HAVING` se procenjuje za svaku grupu kao logički uslov. Grupa ostaje u rezultatu samo ako je uslov tačan. Ako je rezultat uslova netačan ili `NULL` (nepoznat), grupa se izostavlja.

Ovo je važno kada je agregat `NULL`:

```sql
WITH sample(group_id, value) AS (
    VALUES (1, NULL), (1, NULL), (2, 5), (2, 0)
)
SELECT
    group_id,
    SUM(value) AS total
FROM sample
GROUP BY group_id
HAVING SUM(value) > 0
ORDER BY group_id;
```

Rezultat je samo `2 | 5`. Za grupu 1 `SUM(value)` je `NULL`; poređenje `NULL > 0` nije tačno, pa grupa nije vraćena. Za grupu 2 zbir je 5 i uslov je tačan.

Za `BETWEEN`, obe granice su uključene. Ako su donja granica veća od gornje, nijedna vrednost ne zadovoljava uslov. Ako je izraz koji se poredi `NULL`, uslov `BETWEEN` ima vrednost `NULL` i grupa se ne zadržava.

Možeš kombinovati više uslova uz `AND`, `OR` i zagrade:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    MAX(Milliseconds) AS longest_milliseconds
FROM tracks
GROUP BY AlbumId
HAVING COUNT(*) >= 10
   AND MAX(Milliseconds) > 300000
ORDER BY track_count DESC, AlbumId;
```

Ovde grupa mora ispuniti oba uslova. Koristi zagrade kada kombinuješ `AND` i `OR` da bi nameravana logika bila jasna.

## `HAVING` i grupni ključevi

`HAVING` može da proverava i grupni ključ, ali ako uslov ne zavisi od agregata, obično je efikasnije i jasnije primeniti ga u `WHERE` pre grupisanja:

```sql
SELECT
    BillingCountry,
    COUNT(*) AS invoice_count
FROM invoices
WHERE BillingCountry = 'USA'
GROUP BY BillingCountry;
```

Ovo je izbor redova iz `USA`. Nasuprot tome, uslov kao što je `HAVING COUNT(*) >= 10` odlučuje da li će cela grupa države ostati u rezultatu.

U `HAVING` uslovima drži se grupnih izraza i agregata. SQLite može biti popustljiv prema negrupisanim kolonama, ali vrednost takve kolone može dolaziti iz neodređenog reda grupe. Za predvidljiv i prenosiv upit koristi grupni ključ ili agregatni izraz.

## Redosled rezultata

`HAVING` odlučuje koje grupe ostaju; ne određuje njihov redosled. Bez `ORDER BY`, redosled rezultatnih redova nije garantovan:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count
FROM tracks
GROUP BY AlbumId
HAVING COUNT(*) BETWEEN 18 AND 20
ORDER BY track_count DESC, AlbumId ASC;
```

Ovaj upit prvo sortira po broju numera opadajuće, a zatim po `AlbumId` uzlazno kao tie-breaker.

## Veza sa SQLAlchemy 2.0

SQLAlchemy dodaje agregatni uslov pomoću `.having(...)`, a uslov nad redovima pomoću `.where(...)`. Primer pretpostavlja ORM model `Track`:

```python
from sqlalchemy import func, select

statement = (
    select(
        Track.album_id,
        func.count(Track.track_id).label("track_count"),
    )
    .group_by(Track.album_id)
    .having(func.count(Track.track_id).between(18, 20))
    .order_by(Track.album_id)
)
```

`.having()` dodaje uslov za grupe; ne zamenjuje `.where()`. U SQL-u koji se generiše uslov se postavlja posle `GROUP BY`.

## Česte greške

- **Staviš agregat u `WHERE`:** koristi `HAVING` za uslov nad agregatnim rezultatom.
- **Misliš da `HAVING` bez `GROUP BY` postaje `WHERE`:** u agregatnom upitu bez grupisanja filtrira se jedna implicitna grupa.
- **Filtriraš redove u `HAVING` umesto u `WHERE`:** tako možeš promeniti agregat i zadržati redove koje si nameravao da isključiš pre izračunavanja.
- **Zaboraviš da je `BETWEEN` uključujući:** obe granice su deo opsega.
- **Brojiš kolonu koja može biti `NULL` misleći da je to broj svih redova:** `COUNT(kolona)` preskače `NULL`; proveri da li treba `COUNT(*)` ili primarni ključ.
- **Očekuješ da uslov sa `NULL` bude tačan:** uslovi koji se procene kao `NULL` ne zadržavaju grupu.
- **Očekuješ da `HAVING` sortira grupe:** dodaj `ORDER BY`.
- **Koristiš negrupisanu kolonu u `HAVING`:** koristi grupni izraz ili agregat da rezultat ne zavisi od neodređenog reda.
- **Misliš da prazan grupisani upit vraća grupu sa nulom:** prazan ulaz sa `GROUP BY` daje nula grupa i nula izlaznih redova.

## Vežbe

1. Pronađi albume koji imaju od 18 do 20 numera pomoću `HAVING COUNT(TrackId) BETWEEN 18 AND 20`.
2. Potvrdi da `BETWEEN` uključuje vrednosti 18 i 20.
3. Prvo filtriraj numere duže od tri minuta u `WHERE`, pa pomoću `HAVING` zadrži albume sa najmanje tri takve numere.
4. Pronađi države sa najmanje 10 računa.
5. Izaberi albume čiji najduži zapis prelazi 300000 milisekundi, iako `MAX()` nije prikazan u `SELECT` listi.
6. Napravi upit sa agregatom i `HAVING`, ali bez `GROUP BY`. Uporedi uslov koji zadržava jedinu implicitnu grupu sa uslovom koji je odbacuje.
7. Napravi dve grupe: jednu čiji je agregat `NULL` i drugu čiji agregat ispunjava uslov. Objasni zašto prva ne prolazi `HAVING`.
8. Uporedi rezultat grupisanog upita nad praznim ulazom sa agregatnim upitom bez `GROUP BY`.
9. Kombinuj dva uslova u `HAVING` pomoću `AND`, pa dodaj `ORDER BY` sa tie-breaker-om.

## Provera razumevanja

1. U kom trenutku se primenjuje `HAVING`?
2. Koja je glavna razlika između `WHERE` i `HAVING`?
3. Zašto `WHERE COUNT(*) >= 10` nije ispravno mesto za uslov nad brojem redova?
4. Da li `BETWEEN 18 AND 20` uključuje vrednosti 18 i 20?
5. Kako se `HAVING` ponaša u agregatnom upitu bez `GROUP BY`?
6. Zašto `HAVING` bez grupisanja nije zamena za `WHERE`?
7. Šta se dešava ako se `HAVING` uslov proceni kao `NULL`?
8. Da li `HAVING` određuje redosled rezultatnih grupa?
9. Zašto je važno izabrati odgovarajući izraz u `COUNT()`?
10. Šta vraća `GROUP BY` nad praznim ulazom?

## Izvori za dalje čitanje

- [SQLite: SELECT — GROUP BY, HAVING i obrada upita](https://www.sqlite.org/lang_select.html)
- [SQLite: Aggregate Functions](https://www.sqlite.org/lang_aggfunc.html)
- [SQLite: Expressions — `BETWEEN` i logički izrazi](https://www.sqlite.org/lang_expr.html)
