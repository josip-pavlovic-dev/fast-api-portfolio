# 01 — Uvod u SQLite agregatne funkcije

## Cilj lekcije

U ovoj lekciji upoznaćeš SQLite agregatne funkcije: `AVG`, `COUNT`, `MAX`, `MIN`, `SUM` i `GROUP_CONCAT`. One obrađuju više ulaznih redova i računaju jednu vrednost za ceo skup ili za svaku grupu redova.

Važno je da uz rezultat razumeš i koje redove funkcija računa. `NULL`, duplikati, prazan skup i SQLite-ovo fleksibilno rukovanje tipovima mogu promeniti rezultat ili brojanje.

Ova lekcija je uvod; pojedinačne funkcije i grupisanje obrađuju se detaljnije u narednim lekcijama:

- [`AVG`](./02_sqlite_AVG_function.md)
- [`COUNT`](./03_sqlite_COUNT_function.md)
- [`SUM`](./04_sqlite_SUM_function.md)
- [`MAX`](./05_sqlite_MAX_function.md)
- [`MIN`](./06_sqlite_MIN_function.md)
- [`GROUP_CONCAT`](./07_sqlite_GROUP_CONCAT_function.md)
- [`GROUP BY`](./08_sqlite_GROUP_BY_clause.md) i [`HAVING`](./09_sqlite_HAVING_clause.md)

## Šta je agregatna funkcija?

Agregatna funkcija prima vrednosti iz više redova i izračunava jedan rezultat:

```sql
SELECT agregatna_funkcija(izraz)
FROM tabela;
```

Bez `GROUP BY`, sve redove koji prođu `WHERE` uslov SQLite obrađuje kao jednu grupu i upit vraća jedan rezultat agregacije. Kada dodaš `GROUP BY`, dobijaš rezultat za svaku grupu.

Na primer, sledeći upit izračunava agregate za sve račune:

```sql
SELECT
    COUNT(*) AS invoice_rows,
    COUNT(Total) AS totals_present,
    SUM(Total) AS total_sum,
    AVG(Total) AS average_total,
    MIN(Total) AS minimum_total,
    MAX(Total) AS maximum_total
FROM invoices;
```

U priloženoj Chinook kopiji vraća jedan red: ima 412 računa, zbir `Total` je `2328.6`, prosek je približno `5.65194`, minimum `0.99`, a maksimum `25.86`. Ovi brojevi zavise od podataka u kopiji.

## Pregled funkcija

| Funkcija          | Šta računa                                                              | Primer               |
| ----------------- | ----------------------------------------------------------------------- | -------------------- |
| `AVG(X)`          | Aritmetičku sredinu nenultih vrednosti izraza `X`.                      | `AVG(Total)`         |
| `COUNT(*)`        | Broj ulaznih redova, uključujući redove čije kolone sadrže `NULL`.      | `COUNT(*)`           |
| `COUNT(X)`        | Broj redova u kojima izraz `X` nije `NULL`.                             | `COUNT(Total)`       |
| `MAX(X)`          | Najveću nenultu vrednost prema SQLite redosledu poređenja.              | `MAX(Total)`         |
| `MIN(X)`          | Najmanju nenultu vrednost prema SQLite redosledu poređenja.             | `MIN(Total)`         |
| `SUM(X)`          | Zbir nenultih vrednosti izraza `X`.                                     | `SUM(Total)`         |
| `GROUP_CONCAT(X)` | Spaja vrednosti `X` koje nisu `NULL`. Podrazumevani separator je zarez. | `GROUP_CONCAT(Name)` |

`GROUP_CONCAT` ne spaja dva stringa iz istog reda — on sakuplja vrednosti više redova u jedan tekstualni rezultat. Redosled spojenih vrednosti nije garantovan osim ako nije eksplicitno zadat redosled u agregatu.

## Agregati nad redovima i nad grupama

`WHERE` filtrira ulazne redove pre agregacije. Ovaj upit sabira račune samo za kupce iz SAD:

```sql
SELECT
    COUNT(*) AS invoice_count,
    SUM(Total) AS invoice_total
FROM invoices
WHERE BillingCountry = 'USA';
```

Za zbir po državi dodaj `GROUP BY`:

```sql
SELECT
    BillingCountry,
    COUNT(*) AS invoice_count,
    SUM(Total) AS invoice_total
FROM invoices
GROUP BY BillingCountry
ORDER BY BillingCountry;
```

Sada se vraća po jedan red za svaku državu. `HAVING` može da filtrira grupe prema agregatnom rezultatu:

```sql
SELECT
    BillingCountry,
    COUNT(*) AS invoice_count
FROM invoices
GROUP BY BillingCountry
HAVING COUNT(*) >= 10
ORDER BY invoice_count DESC, BillingCountry;
```

Nemoj mešati redosled uloge ovih klauzula:

- `WHERE` bira ulazne redove pre grupisanja;
- `GROUP BY` određuje grupe;
- agregatne funkcije računaju vrednosti za svaku grupu;
- `HAVING` zadržava ili odbacuje već izračunate grupe.

Zbog toga se uobičajeni agregatni filter piše u `HAVING`, a ne u `WHERE`:

```sql
-- Neispravno za agregatni rezultat:
-- WHERE COUNT(*) >= 10

-- Ispravno:
HAVING COUNT(*) >= 10
```

`GROUP BY` i `HAVING` detaljno se obrađuju u posebnim lekcijama.

## `ALL` i `DISTINCT`

Agregat po podrazumevanom ponašanju obrađuje sve ulazne vrednosti, uključujući ponovljene. U SQLite-u možeš to eksplicitno napisati sa `ALL`:

```sql
SELECT
    SUM(value) AS default_all,
    SUM(ALL value) AS explicit_all,
    SUM(DISTINCT value) AS distinct_values
FROM (
    SELECT 1 AS value
    UNION ALL SELECT 1
    UNION ALL SELECT NULL
);
```

Rezultat je `2 | 2 | 1`. Prva dva izraza saberu obe jedinice; `DISTINCT` uklanja ponovljenu vrednost pre sabiranja. `ALL` je podrazumevan, pa se najčešće izostavlja.

`DISTINCT` odnosi se na vrednosti izraza koje agregat prima, a ne na redove u tabeli. To može promeniti značenje izračunavanja:

- `COUNT(DISTINCT CustomerId)` broji različite nenulte ID-jeve kupaca;
- `SUM(DISTINCT Total)` sabira različite iznose računa, pa dva različita računa istog iznosa doprinesu zbiru samo jednom.

Nemoj koristiti `SUM(DISTINCT ...)` kao način da „popraviš“ dupliranje redova iz pogrešnog join-a. Prvo utvrdi granularnost rezultata i popravi relaciju ili izbor redova.

## `NULL` i agregatne funkcije

Većina agregatnih funkcija ignoriše `NULL` argumente. `COUNT(*)` je važan izuzetak: broji redove bez obzira na vrednosti njihovih kolona.

```sql
WITH sample(value) AS (
    VALUES (1), (1), (NULL)
)
SELECT
    COUNT(*) AS row_count,
    COUNT(value) AS non_null_count,
    COUNT(DISTINCT value) AS distinct_non_null_count,
    SUM(value) AS sum_all_values,
    SUM(DISTINCT value) AS sum_distinct_values
FROM sample;
```

Očekivano: `3 | 2 | 1 | 2 | 1`.

- `COUNT(*)` broji tri reda.
- `COUNT(value)` broji dve vrednosti koje nisu `NULL`.
- `COUNT(DISTINCT value)` broji jednu različitu nenultu vrednost.
- `SUM(value)` sabira obe jedinice i ignoriše `NULL`.

Nemoj tumačiti `NULL` kao nulu. To je nepoznata ili nedostajuća vrednost, a ponašanje zavisi od funkcije. Ako želiš da prikažeš nulu umesto `NULL` rezultata, možeš to učiniti eksplicitno, na primer sa `COALESCE(SUM(value), 0)`, ali samo kada nula zaista odgovara značenju podataka.

## Prazan skup i grupa bez nenultih vrednosti

Kada agregatni upit bez `GROUP BY` nema nijedan ulazni red, on i dalje vraća jedan rezultatni red. Rezultat zavisi od funkcije:

```sql
WITH empty(value) AS (
    SELECT 1
    WHERE 0
)
SELECT
    COUNT(*) AS row_count,
    COUNT(value) AS non_null_count,
    SUM(value) AS sum_value,
    TOTAL(value) AS total_value,
    AVG(value) AS average_value,
    MIN(value) AS minimum_value,
    MAX(value) AS maximum_value,
    GROUP_CONCAT(value) AS concatenated_values
FROM empty;
```

SQLite vraća `0` za oba `COUNT` izraza; `SUM`, `AVG`, `MIN`, `MAX` i `GROUP_CONCAT` vraćaju `NULL`; SQLite-ova posebna funkcija `TOTAL` vraća `0.0`.

Isto pravilo o rezultatu ne znači da je svaka grupa prisutna. Ako upit koristi `GROUP BY` i nema ulaznih redova, nema ni grupa, pa se ne vraćaju redovi za nepostojeće grupe. Ako grupa postoji, ali su sve njene agregatne vrednosti `NULL`, grupa se ipak vraća; `COUNT(X)` daje `0`, a `SUM(X)`, `AVG(X)`, `MIN(X)`, `MAX(X)` i `GROUP_CONCAT(X)` daju `NULL`.

`TOTAL()` je SQLite specifična funkcija. Za razliku od `SUM()`, vraća `0.0` za prazan skup i uvek daje rezultat sa floating-point tipom. Koristi je samo ako takvo ponašanje i tip odgovaraju zadatku.

## Granični slučajevi i SQLite tipovi

### `COUNT(*)` nije isto što i `COUNT(kolona)`

Ako tabela ima pet redova, a kolona popunjena samo u tri, `COUNT(*)` vraća `5`, dok `COUNT(kolona)` vraća `3`. `COUNT(DISTINCT kolona)` broji samo različite vrednosti koje nisu `NULL`.

### SQLite može da čuva različite storage klase u istoj koloni

SQLite je fleksibilno tipiziran. Kada `AVG()` ili `SUM()` dobije tekst koji ne izgleda kao broj ili BLOB vrednost, SQLite može da je protumači kao `0` za računanje. `AVG()` takođe broji takvu nenultu vrednost u imenitelju. Na primer, `AVG` nad vrednostima `'10'`, `'not numeric'` i `NULL` u SQLite-u iznosi `5.0`, a ne `10.0`.

Za pouzdane numeričke rezultate proveri da kolona sadrži vrednosti očekivanog tipa i opsega. Nemoj računati da će neispravan tekst automatski biti preskočen.

### `MIN` i `MAX` porede vrednosti, ne značenje kolone

Za numeričke vrednosti `MIN` i `MAX` vraćaju najmanju i najveću vrednost. Za tekst zavise od SQLite redosleda poređenja i kolacije. Ako su vrednosti brojevi sačuvani kao tekst, nemoj pretpostaviti da će se porediti kao numeričke vrednosti.

### `GROUP_CONCAT` i redosled

`GROUP_CONCAT` ignoriše `NULL` ulazne vrednosti. Ako nema nijedne nenulte vrednosti, rezultat je `NULL`. Bez eksplicitnog redosleda ne oslanjaj se na redosled elemenata u tekstualnom rezultatu. SQLite 3.44.0 i noviji podržava `ORDER BY` unutar poziva agregata; za starije verzije proveri raspoloživu sintaksu.

## Agregat nad rezultatima `JOIN`-a

Agregat računa redove koji postoje u ulazu upita, uključujući redove nastale spajanjem. Ako jedan album ima mnogo numera, `COUNT(*)` nad spojenim redovima broji numere, a ne albume:

```sql
SELECT
    COUNT(*) AS track_album_pairs,
    COUNT(DISTINCT a.AlbumId) AS albums
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId;
```

U trenutnoj kopiji to je `3503` parova i `347` albuma. Pre agregacije odluči šta jedan rezultatni red predstavlja. `DISTINCT` može biti ispravan ako želiš da brojiš jedinstvene ključeve, ali nije zamena za razumevanje kardinalnosti join-a.

## Česte greške

- **Koristiš `COUNT(kolona)` očekujući broj svih redova:** `NULL` vrednosti se ne broje; koristi `COUNT(*)` za broj ulaznih redova.
- **Pretpostaviš da svi agregati vraćaju `0` za prazan skup:** samo `COUNT` vraća `0`; `SUM`, `AVG`, `MIN`, `MAX` i `GROUP_CONCAT` vraćaju `NULL`. `TOTAL` je SQLite izuzetak.
- **Pretvoriš svaki `NULL` u nulu bez provere značenja:** nedostajuće merenje i izmerena nula nisu isto.
- **Dodaš `DISTINCT` samo zato što zbir deluje preveliko:** proveri da li join proizvodi više redova po entitetu i šta se zapravo sabira.
- **Staviš uslov agregata u `WHERE`:** koristi `HAVING` za filtriranje grupa prema agregatnom rezultatu.
- **Zaboraviš da se `GROUP_CONCAT` redosled ne podrazumeva:** postavi redosled kada je važan.
- **Računaš prosek nad neispravnim tekstualnim vrednostima:** SQLite ih može tretirati kao nulu, a ne kao nevažeće i zanemarljive.
- **Mešaš jednu ukupnu agregaciju sa grupisanjem:** bez `GROUP BY` dobijaš jedan rezultatni red; sa `GROUP BY` po jedan za svaku grupu.

## Vežbe

1. Nad `invoices` prikaži ukupan broj redova, broj popunjenih `Total` vrednosti, zbir, prosek, minimum i maksimum.
2. Uporedi `COUNT(*)`, `COUNT(Total)` i `COUNT(DISTINCT Total)`. Objasni šta se računa u svakom slučaju.
3. Napravi CTE sa vrednostima `(1), (1), (NULL)` i uporedi `SUM(value)`, `SUM(ALL value)` i `SUM(DISTINCT value)`.
4. Napravi prazan CTE i proveri rezultate `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `GROUP_CONCAT` i `TOTAL`.
5. Napravi grupisani izveštaj sa brojem računa po državi. Dodaj `HAVING` tako da ostanu samo države sa najmanje 10 računa.
6. Spoji `tracks` i `albums`, pa uporedi `COUNT(*)` sa `COUNT(DISTINCT AlbumId)`. Objasni zašto brojevi nisu jednaki.
7. Napravi mali skup koji sadrži tekst `'10'`, tekst `'not numeric'` i `NULL`. Proveri `AVG` i objasni rezultat u SQLite-u.
8. Spoji vrednosti više redova pomoću `GROUP_CONCAT`. Proveri ponašanje `NULL` vrednosti i nemoj pretpostavljati redosled bez njegovog eksplicitnog zadavanja.

## Provera razumevanja

1. Šta vraća agregatna funkcija u odnosu na broj ulaznih redova?
2. Koliko rezultatnih redova vraća agregat bez `GROUP BY`?
3. Koja je razlika između `COUNT(*)` i `COUNT(expression)`?
4. Šta znači `DISTINCT` unutar agregata?
5. Da li se `NULL` broji u `COUNT(DISTINCT expression)`?
6. Šta vraćaju `SUM()` i `AVG()` kada nema nenultih vrednosti?
7. Koja je razlika između `SUM()` i SQLite-ovog `TOTAL()` za prazan skup?
8. Koja klauzula filtrira ulazne redove pre agregacije, a koja filtrira grupe posle nje?
9. Zašto `COUNT(*)` nad join-om može biti veći od broja jedinstvenih roditeljskih zapisa?
10. Da li je redosled vrednosti `GROUP_CONCAT` garantovan bez `ORDER BY`?
11. Kako SQLite može da tretira tekstualnu vrednost koja nije numerička u `AVG()`?
12. Zašto ne treba dodavati `DISTINCT` kao automatski lek za dupliranje redova?

## Izvori za dalje čitanje

- [SQLite: Aggregate Functions](https://www.sqlite.org/lang_aggfunc.html)
- [SQLite: SELECT — GROUP BY, HAVING i obrada upita](https://www.sqlite.org/lang_select.html)
