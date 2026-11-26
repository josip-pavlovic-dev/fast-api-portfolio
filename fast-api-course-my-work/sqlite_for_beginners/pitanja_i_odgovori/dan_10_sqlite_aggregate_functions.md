# Dan 10 — SQLite agregatne funkcije

> **Važna napomena:** naziv „Dan 10“ je oznaka dokumenta, a ne očekivanje da se cela oblast završi za jedan dan. Vodič prati svih devet lekcija oblasti 06. Slobodno ih rasporedi u više sesija i nastavi kada razumeš trenutnu temu.

## Cilj oblasti

Agregatne funkcije računaju jednu vrednost iz više redova. U ovoj oblasti obrađuju se:

- `AVG()` — prosek;
- `COUNT()` — broj redova ili nenultih vrednosti;
- `SUM()` — zbir;
- `MAX()` i `MIN()` — najveća i najmanja vrednost;
- `GROUP_CONCAT()` — spajanje vrednosti više redova u tekst;
- `GROUP BY` — formiranje grupa za agregaciju;
- `HAVING` — filtriranje grupa prema njihovim agregatnim rezultatima.

Ovaj vodič povezuje teoriju i proverene vežbe:

- [teorija oblasti 06](../06_sqlite_aggregate_functions/)
- [SQL vežbe oblasti 06](../playground/sql/06_sqlite_aggregate_functions/)
- [Playground uputstvo](../playground/README.md)
- prethodni vodič za [SQLite `JOIN`](./dan_09_table_joins.md)

Skripte iz oblasti 06 su upiti za čitanje i CTE primeri nad privremenim vrednostima. Ipak, radi na lokalnoj Chinook kopiji, ne na bazi FastAPI aplikacije. U SQLite CLI-ju iz root-a repozitorijuma otvori kopiju samo za čitanje:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Zatim učitaj odgovarajuću skriptu pomoću `.read`, na primer:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/01_introduction_to_sqlite_aggregate_functions.sql
```

Skripte sadrže `-- @block` oznake kako bi u SQLTools-u mogao da izvršiš pojedinačan primer.

## Očekivani rezultati u Chinook kopiji

Brojevi su provereni nad trenutnom `chinook_practice.db` kopijom. Drugačiji podaci mogu dati drugačije rezultate, ali pravila SQLite-a ostaju ista.

| Provera                                                   | Očekivani rezultat |
| --------------------------------------------------------- | -----------------: |
| Broj računa                                               |                412 |
| `SUM(invoices.Total)`                                     |             2328.6 |
| `AVG(invoices.Total)`                                     |  približno 5.65194 |
| `MIN(invoices.Total)` / `MAX(invoices.Total)`             |       0.99 / 25.86 |
| Kupci / kupci sa popunjenom kompanijom / različite države |       59 / 10 / 24 |
| Broj numera / broj albuma                                 |         3503 / 347 |
| Najduža / najkraća numera u milisekundama                 |     5286953 / 1071 |
| Albumi sa 18 do 20 numera, uključujući granice            |                 16 |

Ove vrednosti služe kao kontrola konkretnih primera, ne kao definicija funkcija.

---

## Rešenja i objašnjenja vežbi

## Lekcija 01 — Uvod u agregatne funkcije

- **Teorija:** [01_introduction_to_sqlite_aggregate_functions.md](../06_sqlite_aggregate_functions/01_introduction_to_sqlite_aggregate_functions.md)
- **Radni fajl:** [01_introduction_to_sqlite_aggregate_functions.sql](../playground/sql/06_sqlite_aggregate_functions/01_introduction_to_sqlite_aggregate_functions.sql)

### Vežba 1 — Više agregata nad istim skupom

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

Upit vraća jedan red jer nema `GROUP BY`. U Chinook kopiji svi računi imaju `Total`, pa su oba `COUNT` rezultata 412. Zbir je `2328.6`, prosek približno `5.65194`, minimum `0.99`, a maksimum `25.86`.

`COUNT(*)` broji ulazne redove, dok `COUNT(Total)` broji redove u kojima izraz `Total` nije `NULL`. Ostale funkcije ovde računaju nad vrednostima `Total`; svaka ima svoja pravila za `NULL`, duplikate i tipove podataka.

### Vežba 2 — Sve vrednosti su `NULL` ili nema ulaznih redova

```sql
WITH sample(value) AS (
    VALUES (NULL), (NULL)
)
SELECT
    COUNT(*) AS rows_present,
    COUNT(value) AS non_null_values,
    SUM(value) AS sum_value,
    AVG(value) AS average_value,
    MIN(value) AS minimum_value,
    MAX(value) AS maximum_value,
    GROUP_CONCAT(value) AS concatenated_values
FROM sample;
```

Rezultat je `2 | 0 | NULL | NULL | NULL | NULL | NULL`. Dva reda postoje, ali nema nenultih vrednosti za agregaciju. Ako bi ulaz bio prazan, agregatni upit bez `GROUP BY` i dalje bi vratio jedan red: oba `COUNT` rezultata bila bi `0`, a ostale navedene funkcije vratile bi `NULL`.

Nemoj mešati prazan skup sa grupisanim upitom nad praznim ulazom. Ako isti upit doda `GROUP BY`, ne postoje ulazni redovi od kojih bi se formirale grupe, pa rezultat ima nula redova.

## Lekcija 02 — `AVG()`

- **Teorija:** [`AVG()`](../06_sqlite_aggregate_functions/02_sqlite_AVG_function.md)
- **Radni fajl:** [`AVG()` vežbe](../playground/sql/06_sqlite_aggregate_functions/02_sqlite_AVG_function.sql)

### Vežba 1 — Prosek trajanja numera po albumu

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    AVG(Milliseconds) AS average_milliseconds,
    ROUND(AVG(Milliseconds) / 60000.0, 2) AS average_minutes
FROM tracks
GROUP BY AlbumId
ORDER BY average_milliseconds DESC, AlbumId;
```

`AVG()` računa prosek unutar svake grupe. `60000.0` obezbeđuje realno deljenje pri pretvaranju milisekundi u minute. Ako bi se presekao svaki ceo broj sa `Milliseconds / 60000`, deo preciznosti bi se izgubio pre računanja proseka. Za album 1 ispravan izraz daje prosek od `4.0` minuta; prosečenje vrednosti koje su prethodno podeljene celobrojno daje `3.5`.

`ROUND(..., 2)` zaokružuje rezultat, ali ne garantuje prikaz završnih nula kao u tekstu `4.00`. Za fiksni format prikaza koristi formatiranje u klijentskoj aplikaciji.

### Vežba 2 — Zašto prosek proseka može biti pogrešan

```sql
WITH sample(group_id, value) AS (
    VALUES ('A', 10), ('B', 0), ('B', 0), ('B', 0)
),
group_averages AS (
    SELECT
        group_id,
        AVG(value) AS group_average,
        COUNT(value) AS value_count
    FROM sample
    GROUP BY group_id
)
SELECT
    (SELECT AVG(value) FROM sample) AS overall_average,
    (SELECT AVG(group_average) FROM group_averages) AS unweighted_average,
    (SELECT SUM(group_average * value_count) / SUM(value_count)
     FROM group_averages) AS weighted_average;
```

Rezultat je `2.5 | 5.0 | 2.5`. Prosti prosek grupnih proseka daje istoj težini grupu A sa jednim uzorkom i grupu B sa tri uzorka. Ponderisani prosek koristi broj nenultih uzoraka svake grupe kao težinu i ovde se poklapa sa ukupnim prosekom.

### Pitanje — Da li se nula računa, a `NULL` ignoriše?

Da. Nula je poznata numerička vrednost i učestvuje u zbiru i imeniocu proseka. `NULL` se izostavlja. Ako je `NULL` pretvoren u nulu sa `COALESCE`, prosek se menja; radi to samo ako pravilo podataka zaista kaže da nedostajuća vrednost znači nulu.

U SQLite-u tekst koji se ne može protumačiti kao broj može doprineti kao `0` i ipak biti uračunat kao nenulta vrednost u imenitelju. Zato `AVG()` nije validacija kvaliteta podataka; proveri storage klase i sadržaj numeričkih kolona.

## Lekcija 03 — `COUNT()`

- **Teorija:** [`COUNT()`](../06_sqlite_aggregate_functions/03_sqlite_COUNT_function.md)
- **Radni fajl:** [`COUNT()` vežbe](../playground/sql/06_sqlite_aggregate_functions/03_sqlite_COUNT_function.sql)

### Vežba 1 — Razlika između `COUNT(*)` i `COUNT(kolona)`

```sql
SELECT
    COUNT(*) AS all_customers,
    COUNT(Company) AS customers_with_company,
    COUNT(DISTINCT Country) AS distinct_countries
FROM customers;
```

Rezultat u trenutnoj kopiji je `59 | 10 | 24`.

- `COUNT(*)` broji svih 59 redova, pa i one sa `NULL` kolonama.
- `COUNT(Company)` broji vrednosti `Company` koje nisu `NULL`.
- `COUNT(DISTINCT Country)` broji različite nenulte države.

`0`, prazan tekst `''` i običan tekst su sve vrednosti različite od `NULL`, pa ih `COUNT(izraz)` broji. Funkcija ne odlučuje da li je vrednost „smislena“.

### Vežba 2 — Brojanje različitih iznosa i različitih kombinacija

```sql
SELECT
    COUNT(*) AS invoice_rows,
    COUNT(Total) AS totals_present,
    COUNT(DISTINCT Total) AS distinct_totals
FROM invoices;
```

Rezultat je `412 | 412 | 23`: u tabeli ima 412 računa i 23 različita iznosa. Dva računa sa istim iznosom i dalje su dva različita računa; `COUNT(DISTINCT Total)` odgovara na drugo pitanje od `COUNT(*)`.

U SQLite-u `COUNT(DISTINCT ...)` prihvata jedan izraz. Za različite parove više kolona koristi podupit:

```sql
SELECT COUNT(*) AS distinct_country_city_pairs
FROM (
    SELECT DISTINCT BillingCountry, BillingCity
    FROM invoices
);
```

`SELECT DISTINCT` u podupitu može zadržati kombinaciju koja sadrži `NULL`; spoljašnji `COUNT(*)` broji je. To se razlikuje od `COUNT(DISTINCT jedna_kolona)`, koji izostavlja `NULL`.

### Vežba 3 — Uslovno brojanje

```sql
WITH sample(value, is_positive) AS (
    VALUES (NULL, 0), (0, 0), ('', 0), ('x', 0), (1, 1), (1, 1)
)
SELECT
    COUNT(*) AS all_rows,
    COUNT(CASE WHEN is_positive = 1 THEN 1 END) AS positive_values
FROM sample;
```

Rezultat je `6 | 2`. `CASE` vraća `1` samo za redove koji ispunjavaju uslov, a podrazumevano `NULL` za ostale. `COUNT()` ignoriše te `NULL` vrednosti. Nemoj pisati `ELSE 0` ako želiš da neodgovarajući redovi budu izostavljeni: nula nije `NULL`, pa bi ih `COUNT()` takođe brojao.

U ovom primeru uslov se namerno proverava preko eksplicitne numeričke oznake `is_positive`. SQLite-ova poređenja vrednosti različitih storage klasa mogu biti iznenađujuća; tekstualni podatak ne treba automatski tretirati kao broj samo zato što je upotrebljen u izrazu `value > 0`.

### Pitanje — Zašto `COUNT(*)` posle `LEFT JOIN`-a može dati 1 za red bez poklapanja?

`LEFT JOIN` zadržava red leve tabele, pa za njega postoji jedan izlazni red sa `NULL` vrednostima na desnoj strani. `COUNT(*)` ga broji. Ako želiš da prebrojiš samo poklopljene redove desne tabele, koristi njen nenulti ključ, na primer `COUNT(al.AlbumId)`.

## Lekcija 04 — `SUM()`

- **Teorija:** [`SUM()`](../06_sqlite_aggregate_functions/04_sqlite_SUM_function.md)
- **Radni fajl:** [`SUM()` vežbe](../playground/sql/06_sqlite_aggregate_functions/04_sqlite_SUM_function.sql)

### Vežba 1 — Zbir računa

```sql
SELECT
    COUNT(*) AS invoice_count,
    SUM(Total) AS invoice_total,
    TOTAL(Total) AS sqlite_total
FROM invoices;
```

U trenutnoj kopiji `COUNT(*)` je `412`, a `SUM(Total)` je `2328.6`. `TOTAL()` je SQLite specifična funkcija; vraća realni rezultat i `0.0` kada nema vrednosti za sabiranje. `SUM()` u tom praznom slučaju vraća `NULL`, što može bolje da čuva razliku između „nema podataka“ i „zbir je nula“.

### Pitanje — Kako se `SUM()` ponaša sa `NULL`, duplikatima i nevažećim tekstom?

`SUM()` ignoriše `NULL`, ali sabira ponovljene vrednosti. `SUM(DISTINCT Total)` sabira različite iznose, ne različite račune; može biti pogrešno ako dva stvarna računa imaju isti iznos.

U SQLite-u tekst koji izgleda kao broj može biti protumačen kao broj, a tekst koji se ne može numerički protumačiti može doprineti kao `0.0`. Ne oslanjaj se na `SUM()` da odbaci neispravne podatke ili da validira kolonu.

### Pitanje — Može li `SUM()` izazvati overflow ili preciznost?

Da. Kada svi nenulti ulazi ostanu celi brojevi, prekoračenje opsega celog broja prijavljuje integer overflow. Ako zbir uključuje realne brojeve, računanje koristi približnu floating-point aritmetiku, pa decimalni rezultat poput `0.1 + 0.2` možda neće biti tačno predstavljen. Za novac je često bolje čuvati najmanju novčanu jedinicu kao ceo broj, na primer cente, i formatirati rezultat na kraju.

`COALESCE(SUM(value), 0)` može promeniti izlazni `NULL` u nulu, ali to treba da bude svesna poslovna odluka, ne automatska zamena.

## Lekcija 05 — `MAX()`

- **Teorija:** [`MAX()`](../06_sqlite_aggregate_functions/05_sqlite_MAX_function.md)
- **Radni fajl:** [`MAX()` vežbe](../playground/sql/06_sqlite_aggregate_functions/05_sqlite_MAX_function.sql)

### Vežba 1 — Pronađi najdužu numeru

```sql
SELECT
    TrackId,
    Name,
    Milliseconds
FROM tracks
WHERE Milliseconds = (
    SELECT MAX(Milliseconds)
    FROM tracks
)
ORDER BY TrackId;
```

U trenutnoj bazi najveće trajanje je `5286953` milisekundi. `MAX(Milliseconds)` sam vraća samo tu vrednost, ne i naziv ili ceo red numere. Podupit pronalazi sve redove koji imaju to trajanje. Ako više redova deli maksimum, dobićeš sve njih.

Za maksimum po albumu prvo agregiraj po albumu, pa rezultat spoji nazad sa `tracks`. Tako se zadržavaju sve numere koje dele najveće trajanje u svom albumu.

### Pitanje — Da li `MAX()` ignoriše `NULL` i duplikate?

Da. Agregatni `MAX()` ignoriše `NULL`. Ponavljanje iste vrednosti ne može promeniti najveću vrednost, pa su `MAX(value)` i `MAX(DISTINCT value)` jednaki za isti ulaz. Ako nema redova ili su sve vrednosti `NULL`, agregat vraća `NULL`.

SQLite poredi vrednosti prema svojim pravilima za storage klase i kolaciju. U mešavini brojeva i teksta tekstualna vrednost može biti veća od broja po SQLite redosledu, a tekstualni maksimum zavisi od kolacije. `MAX()` nije provera da li je kolona ispravno tipizirana.

### Pitanje — Da li su agregatni `MAX(X)` i skalarni `max(a, b)` isto?

Ne. `MAX(X)` u agregatnom upitu računa preko redova i ignoriše `NULL`. Skalarni `max(a, b, ...)` poredi argumente jednog reda; ako je neki argument `NULL`, skalarni poziv vraća `NULL`.

## Lekcija 06 — `MIN()`

- **Teorija:** [`MIN()`](../06_sqlite_aggregate_functions/06_sqlite_MIN_function.md)
- **Radni fajl:** [`MIN()` vežbe](../playground/sql/06_sqlite_aggregate_functions/06_sqlite_MIN_function.sql)

### Vežba 1 — Pronađi najkraću numeru

```sql
SELECT
    TrackId,
    Name,
    Milliseconds
FROM tracks
WHERE Milliseconds = (
    SELECT MIN(Milliseconds)
    FROM tracks
)
ORDER BY TrackId;
```

U trenutnoj kopiji najkraće trajanje je `1071` milisekunda. Kao i `MAX()`, agregatni `MIN()` vraća samo vrednost, ne ceo red. Podupit izdvaja sve redove koji odgovaraju minimumu, uključujući izjednačene minimume.

### Pitanje — Kako se `MIN()` ponaša sa `NULL`, duplikatima i tekstom?

Agregatni `MIN()` ignoriše `NULL`; ako nema nenultih vrednosti, rezultat je `NULL`. Ponavljanje vrednosti ne menja minimum, pa je `MIN(DISTINCT value)` najčešće suvišan. Za tekst se koristi SQLite-ov redosled poređenja i kolacija; brojevi sačuvani kao tekst zato se ne moraju porediti numerički.

Kao i kod `MAX()`, SQLite ima skalarni `min(a, b, ...)` koji poredi više vrednosti jednog reda i vraća `NULL` ako je neki argument `NULL`. To nije isto što i agregatni `MIN(X)` nad više redova.

## Lekcija 07 — `GROUP_CONCAT()`

- **Teorija:** [`GROUP_CONCAT()`](../06_sqlite_aggregate_functions/07_sqlite_GROUP_CONCAT_function.md)
- **Radni fajl:** [`GROUP_CONCAT()` vežbe](../playground/sql/06_sqlite_aggregate_functions/07_sqlite_GROUP_CONCAT_function.sql)

### Vežba 1 — Spoji nazive numera po albumu

```sql
SELECT
    AlbumId,
    GROUP_CONCAT(Name, ', ' ORDER BY Name, TrackId) AS track_names
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;
```

`GROUP_CONCAT()` pravi jedan tekstualni rezultat od vrednosti iz više redova. Separator je `', '`, a `ORDER BY` unutar agregata određuje redosled vrednosti unutar svake liste. Završni `ORDER BY AlbumId` sortira redove albuma, ne numere unutar konkateniranog teksta.

`ORDER BY` unutar agregata podržan je od SQLite 3.44.0. Ako ga SQLite verzija ne prepoznaje, proveri je pomoću `SELECT sqlite_version();`.

### Pitanje — Šta se dešava sa `NULL`, praznim tekstom i duplikatima?

`GROUP_CONCAT()` preskače `NULL`, ali prazan tekst `''` nije `NULL` i ostaje kao prazna stavka; zato možeš videti dva separatora jedan pored drugog. Duplikati se podrazumevano zadržavaju. Ako su sve vrednosti `NULL` ili nema ulaznih redova, rezultat je `NULL`.

SQLite ne prihvata `GROUP_CONCAT(DISTINCT value, ' | ')`, jer agregat sa `DISTINCT` može imati samo jedan argument. Za jedinstvene vrednosti i sopstveni separator prvo izdvoji jedinstvene vrednosti u podupitu, pa ih konkateniraj spolja:

```sql
WITH sample(value) AS (
    VALUES ('rock'), ('jazz'), ('rock'), (NULL)
)
SELECT GROUP_CONCAT(value, ' | ' ORDER BY value) AS unique_values
FROM (
    SELECT DISTINCT value
    FROM sample
    WHERE value IS NOT NULL
);
```

Rezultat je `jazz | rock`. Ne dodaj `DISTINCT` samo da bi sakrio neočekivano umnožavanje redova nakon `JOIN`-a; prvo proveri šta predstavlja jedan red ulaznog skupa.

## Lekcija 08 — `GROUP BY`

- **Teorija:** [`GROUP BY`](../06_sqlite_aggregate_functions/08_sqlite_GROUP_BY_clause.md)
- **Radni fajl:** [`GROUP BY` vežbe](../playground/sql/06_sqlite_aggregate_functions/08_sqlite_GROUP_BY_clause.sql)

### Vežba 1 — Broj numera po albumu

```sql
SELECT
    AlbumId,
    COUNT(TrackId) AS track_count
FROM tracks
GROUP BY AlbumId
ORDER BY track_count DESC, AlbumId;
```

`GROUP BY AlbumId` formira po jednu grupu za svaki album, a `COUNT(TrackId)` broji numere unutar grupe. U trenutnoj kopiji album 141 ima najviše, 57 numera. Drugi izraz u `ORDER BY` služi kao tie-breaker kada više albuma ima isti broj.

### Pitanje — Da li `GROUP BY` sortira rezultat ili uklanja `NULL`?

Ne. `GROUP BY` ne garantuje izlazni redosled; koristi `ORDER BY` kad je redosled važan. Redovi čiji je grupni izraz `NULL` pripadaju istoj `NULL` grupi. Ako želiš da ih izostaviš, filtriraj ih pre grupisanja pomoću `WHERE group_key IS NOT NULL`.

### Pitanje — Šta ako je ulaz prazan ili `SELECT` sadrži negrupisanu kolonu?

`GROUP BY` nad praznim ulazom formira nula grupa i vraća nula redova. Nasuprot tome, agregat bez `GROUP BY` računa nad jednom implicitnom grupom i vraća jedan red.

U agregatnom upitu `SELECT` lista treba da sadrži grupni izraz ili agregat. SQLite dozvoljava i takozvanu _bare column_ koja nije grupisana ni agregirana, ali njena vrednost dolazi iz neodređenog reda grupe i nije prenosiva na druge baze. Ako želiš grupisanje po toj koloni, dodaj je u `GROUP BY`; ako želiš reprezentativan red, definiši eksplicitno koji red treba izabrati.

`SELECT DISTINCT Country` obično jasnije izražava nameru kada želiš samo jedinstvene vrednosti bez grupnih izračunavanja. Koristi `GROUP BY` kada praviš rezime po grupama.

## Lekcija 09 — `HAVING`

- **Teorija:** [`HAVING`](../06_sqlite_aggregate_functions/09_sqlite_HAVING_clause.md)
- **Radni fajl:** [`HAVING` vežbe](../playground/sql/06_sqlite_aggregate_functions/09_sqlite_HAVING_clause.sql)

### Vežba 1 — Albumi sa 18 do 20 numera

```sql
SELECT
    AlbumId,
    COUNT(TrackId) AS track_count
FROM tracks
GROUP BY AlbumId
HAVING COUNT(TrackId) BETWEEN 18 AND 20
ORDER BY AlbumId;
```

U trenutnoj kopiji upit vraća 16 albuma. `BETWEEN 18 AND 20` uključuje obe granice, pa prihvata broj numera 18, 19 ili 20. `HAVING` zadržava grupe čiji broj numera ispunjava uslov.

### Pitanje — Kada koristiti `WHERE`, a kada `HAVING`?

- `WHERE` filtrira pojedinačne redove pre grupisanja. Ti redovi više ne učestvuju u agregatima.
- `HAVING` filtrira formirane grupe nakon izračunavanja agregata.

Na primer:

```sql
SELECT
    AlbumId,
    COUNT(*) AS qualifying_tracks
FROM tracks
WHERE Milliseconds >= 180000
GROUP BY AlbumId
HAVING COUNT(*) >= 3
ORDER BY qualifying_tracks DESC, AlbumId;
```

`WHERE` prvo zadržava samo numere koje traju najmanje tri minuta. `COUNT(*)` zatim broji te preostale numere po albumu, a `HAVING` zadržava albume sa najmanje tri takve numere. Uslov poput `COUNT(*) >= 3` ne stavljaj u `WHERE`, jer se agregat još nije izračunao.

### Pitanje — Šta radi `HAVING` bez `GROUP BY`?

U agregatnom upitu bez `GROUP BY`, svi ulazni redovi čine jednu implicitnu grupu. `HAVING` zadržava ili odbacuje tu celu grupu; nije zamena za `WHERE`.

```sql
SELECT COUNT(*) AS total_tracks
FROM tracks
HAVING COUNT(*) > 3000;
```

U Chinook kopiji uslov prolazi i upit vraća jedan red sa `3503`. Ako uslov promeniš tako da ne prolazi, rezultat nema nijedan red. Kod praznog ulaza agregatni upit i dalje ima jednu implicitnu grupu, ali je `COUNT(*)` jednak `0`; `HAVING` može i nju da odbaci.

Ako postoji grupni izraz (`GROUP BY`) i ulaz je prazan, nema grupa koje bi `HAVING` mogao da zadrži, pa se vraća nula redova. Ako se uslov u `HAVING` proceni kao `NULL`, grupa se ne zadržava.

---

## 3. Kratka provera razumevanja

1. **Koja je razlika između `COUNT(*)` i `COUNT(kolona)`?** `COUNT(*)` broji redove; `COUNT(kolona)` broji samo redove gde izraz nije `NULL`.
2. **Da li se nula i prazan tekst broje pomoću `COUNT(kolona)`?** Da. Obe vrednosti nisu `NULL`.
3. **Da li `AVG()` računa nulu?** Da. Nula učestvuje u proseku; `NULL` se ignoriše.
4. **Zašto prosek proseka grupa može biti pogrešan?** Grupe različite veličine ne treba automatski da imaju jednaku težinu; po potrebi koristi ponderisani prosek.
5. **Šta vraća `SUM()` nad praznim skupom?** `NULL`; SQLite `TOTAL()` vraća `0.0`.
6. **Da li `SUM(DISTINCT Total)` broji različite račune?** Ne. Sabira različite iznose, pa može odbaciti ponovljene iznose različitih računa.
7. **Da li `MIN()` ili `MAX()` vraća ceo red koji sadrži ekstremnu vrednost?** Ne. Vraća samu ekstremnu vrednost; za redove koristi podupit ili agregat po grupi pa spajanje nazad.
8. **Da li su agregatni i skalarni `min()`/`max()` isti?** Ne. Skalarni oblik poredi argumente jednog reda i vraća `NULL` ako je neki argument `NULL`; agregatni oblik radi preko redova i ignoriše `NULL`.
9. **Da li je redosled u `GROUP_CONCAT()` podrazumevano garantovan?** Ne. Navedi `ORDER BY` unutar agregata u SQLite 3.44.0 ili novijem.
10. **Da li `GROUP_CONCAT()` ignoriše prazne stringove?** Ne. Ignoriše `NULL`; `''` ostaje prazna stavka.
11. **Šta radi `GROUP BY` sa `NULL` ključevima?** Redovi sa `NULL` grupnim izrazom pripadaju istoj grupi.
12. **Da li `GROUP BY` sortira rezultat?** Ne. Dodaj `ORDER BY`.
13. **Kako se razlikuju grupisani i negrupisani agregatni upiti nad praznim ulazom?** Grupisani upit vraća nula grupa i nula redova; agregat bez `GROUP BY` vraća jedan red sa agregatnim rezultatima.
14. **Koja je razlika između `WHERE` i `HAVING`?** `WHERE` filtrira ulazne redove pre agregacije, a `HAVING` filtrira grupe posle nje.
15. **Kako se ponaša `HAVING` bez `GROUP BY` u agregatnom upitu?** Filtrira jednu implicitnu grupu, ne pojedinačne redove.
16. **Zašto agregati posle `JOIN`-a mogu dati neočekivane brojeve?** `JOIN` može umnožiti ulazne redove; proveri granularnost spoja pre agregiranja.
17. **Da li SQLite agregati potvrđuju da su svi podaci ispravnog tipa?** Ne. Naročito `AVG()` i `SUM()` mogu numerički obraditi ili kao nulu protumačiti tekstualne vrednosti; proveri tip i kvalitet podataka.
18. **Kako se dobija stabilan redosled rezultata?** Koristi `ORDER BY` i dodaj jedinstveni tie-breaker ako je potreban deterministički poredak.

## 4. Prioriteti za samostalno vežbanje

1. Razlikuj `COUNT(*)`, `COUNT(kolona)` i `COUNT(DISTINCT kolona)`.
2. Proveri kako `NULL`, nula, prazan tekst i prazan skup utiču na svaku funkciju.
3. Računaj `AVG()` i `SUM()` po grupama i proveri da li `JOIN` menja broj ulaznih redova.
4. Pronađi redove koji odgovaraju rezultatu `MIN()` ili `MAX()`, uključujući izjednačene vrednosti.
5. Za `GROUP_CONCAT()` odredi separator, uklanjanje duplikata i unutrašnji redosled.
6. Uporedi `WHERE`, `GROUP BY` i `HAVING` na istom zadatku.
7. Dodaj `ORDER BY` kad god očekuješ stabilan prikaz.

## Izvori za dalje čitanje

- [SQLite: Aggregate Functions](https://www.sqlite.org/lang_aggfunc.html)
- [SQLite: SELECT — GROUP BY i HAVING](https://www.sqlite.org/lang_select.html)
- [SQLite: Expressions i poređenja](https://www.sqlite.org/lang_expr.html)
