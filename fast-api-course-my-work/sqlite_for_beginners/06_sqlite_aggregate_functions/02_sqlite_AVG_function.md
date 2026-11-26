# 02 — SQLite `AVG()` funkcija

## Cilj lekcije

`AVG()` je agregatna funkcija koja računa aritmetičku sredinu ulaznih vrednosti. Može da izračuna jedan prosek za sve redove koji prođu filter ili po jedan prosek za svaku grupu definisanu pomoću `GROUP BY`.

U ovoj lekciji koristićemo trajanje numera iz Chinook tabele `tracks`. Kolona `Milliseconds` čuva trajanje u milisekundama; rezultat ćemo pretvoriti u minute i za prikaz zaokružiti na dve decimale.

Prethodno: [uvod u agregatne funkcije](./01_introduction_to_sqlite_aggregate_functions.md). Naredne povezane lekcije: [`COUNT()`](./03_sqlite_COUNT_function.md), [`SUM()`](./04_sqlite_SUM_function.md), [`GROUP BY`](./08_sqlite_GROUP_BY_clause.md) i [`HAVING`](./09_sqlite_HAVING_clause.md).

## Osnovna sintaksa

```sql
AVG([ALL | DISTINCT] izraz)
```

- `AVG(izraz)` računa prosek svih nenultih ulaznih vrednosti. To je podrazumevano ponašanje.
- `AVG(ALL izraz)` eksplicitno uključuje ponovljene vrednosti; `ALL` se obično izostavlja.
- `AVG(DISTINCT izraz)` prvo razmatra različite nenulte vrednosti, a zatim računa njihov prosek.

Bez `GROUP BY`, SQLite agregira sve redove koji prođu `WHERE` uslov u jednu grupu:

```sql
SELECT AVG(Milliseconds) AS average_milliseconds
FROM tracks;
```

U priloženoj Chinook kopiji prosek trajanja je približno `393599.21` milisekundi. Rezultat može da se razlikuje u drugoj kopiji podataka.

## Prosek po albumu

U transkriptu se numere dele po `AlbumId`-ju, a `AVG()` se računa zasebno za svaku grupu. Jedan milisekund iznosi `1 / 60000` minuta:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    ROUND(AVG(Milliseconds) / 60000.0, 2) AS average_minutes
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;
```

`GROUP BY AlbumId` formira grupu po albumu. `AVG(Milliseconds)` računa prosek trajanja u svakoj grupi, deljenje sa `60000.0` pretvara rezultat u minute, a `ROUND(..., 2)` zaokružuje numeričku vrednost na dve decimale. `COUNT(*)` je dodat radi konteksta i nije deo formule za prosek.

Prvi redovi u trenutnoj Chinook kopiji:

| AlbumId | track_count | average_minutes |
| ------: | ----------: | --------------: |
|       1 |          10 |             4.0 |
|       2 |           1 |            5.71 |
|       3 |           3 |            4.77 |
|       4 |           8 |            5.11 |
|       5 |          15 |             4.9 |

Ovaj rezultat sadrži 347 grupa albuma. Redosled grupa nije garantovan bez `ORDER BY`; zato upit sortira po `AlbumId`.

## Prosek grupa nije uvek ukupni prosek

Prosek proseka grupa nije automatski jednak proseku svih redova. Kada grupe imaju različit broj vrednosti, prost prosek grupnih proseka svakoj grupi daje jednaku težinu, bez obzira na broj redova u njoj:

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
    (SELECT AVG(group_average) FROM group_averages) AS unweighted_group_average,
    (SELECT SUM(group_average * value_count) / SUM(value_count)
     FROM group_averages) AS weighted_group_average;
```

Rezultati su `2.5 | 5.0 | 2.5`. Ukupni prosek računa svaku vrednost jednom. Neponderisani prosek grupnih proseka daje grupama A i B jednaku težinu i zato ovde odstupa. Ponderisani prosek množi prosek svake grupe brojem njenih nenultih vrednosti pre sabiranja. Ako su sve grupe iste veličine, neponderisani prosek grupnih proseka može biti jednak ukupnom proseku; u suprotnom proveri koje pitanje upit treba da odgovori.

## Zašto je važno gde se nalazi `ROUND()`

Zaokruži rezultat nakon računanja proseka i konverzije u minute:

```sql
ROUND(AVG(Milliseconds) / 60000.0, 2)
```

Nemoj prvo zaokružiti trajanje svake numere na ceo minut. To menja ulazne vrednosti pre računanja proseka i gubi preciznost:

```sql
-- Drugačiji rezultat: celobrojno deljenje skraćuje svako trajanje pre proseka.
AVG(Milliseconds / 60000)
```

Za album 1 u priloženoj kopiji pravilan izraz daje `4.0` minuta, dok prosek trajanja nakon celobrojnog deljenja po numeri daje `3.5`. Ako deliš cele brojeve u SQLite-u, rezultat se skraćuje na ceo broj. Korišćenje `60000.0` jasno zahteva deljenje u realnom brojevnom tipu.

`ROUND()` vraća numeričku vrednost, pa prikaz može biti `4.0`, a ne tekstualni zapis `4.00`; funkcija ne garantuje završne nule. Koristi formatiranje u klijentu ako je važan fiksan broj prikazanih decimala. Zaokružena vrednost nije isto što i neograničena preciznost internog proseka; nemoj nepotrebno zaokruživati pre daljih proračuna.

## Kako `AVG()` postupa sa `NULL`

`AVG()` ignoriše `NULL` argumente. Prosek se računa nad vrednostima koje nisu `NULL`, ne nad svim redovima:

```sql
WITH sample(value) AS (
    VALUES (10), (20), (NULL)
)
SELECT
    COUNT(*) AS row_count,
    COUNT(value) AS values_counted,
    AVG(value) AS average_value
FROM sample;
```

Očekivano: `3 | 2 | 15.0`. Red sa `NULL` se ne računa ni u zbir ni u brojilac proseka.

U SQLite-u, za numeričke vrednosti koje su ispravnog tipa, `AVG(X)` se ponaša kao zbir nenultih vrednosti podeljen njihovim brojem. Zbog toga se u jednostavnim slučajevima poredi sa:

```sql
TOTAL(X) / COUNT(X)
```

Ne zamenjuj `COUNT(X)` sa `COUNT(*)` ako `X` može biti `NULL`. Na primer, `TOTAL(10, 20, NULL) / 3` bi pogrešno uključio nedostajuću vrednost u imenilac; `AVG()` zanemaruje `NULL`.

### Nula se računa, `NULL` se ignoriše

Nula je poznata numerička vrednost i učestvuje u proseku:

```sql
WITH sample(value) AS (
    VALUES (0), (10), (NULL)
)
SELECT AVG(value) AS average_value
FROM sample;
```

Rezultat je `5.0`, odnosno prosek vrednosti `0` i `10`. `NULL` ne menja ni zbir ni broj vrednosti.

Nemoj menjati `NULL` u nulu automatski. Ako `NULL` znači „nema merenja“, njegovo pretvaranje u nulu menja značenje proseka. Upotrebi `COALESCE()` samo kada poslovno pravilo zaista kaže da nedostajuću vrednost treba tretirati kao nulu.

## Uslovni prosek

Da izračunaš prosek samo za redove koji zadovoljavaju uslov, možeš koristiti `AVG(CASE WHEN ... THEN vrednost END)`. Bez grane `ELSE`, `CASE` vraća `NULL` za ostale redove, a `AVG()` ih ignoriše:

```sql
WITH sample(category, value) AS (
    VALUES ('paid', 100), ('paid', 200), ('free', 0)
)
SELECT
    AVG(CASE WHEN category = 'paid' THEN value END) AS average_paid,
    AVG(CASE WHEN category = 'paid' THEN value ELSE 0 END) AS average_with_zeroes
FROM sample;
```

Rezultat je `150.0 | 100.0`. Prvi izraz računa prosek dve plaćene stavke. Drugi unosi `0` i za besplatnu stavku, pa u imenitelju ima tri vrednosti. Dodaj `ELSE 0` samo ako nula zaista treba da učestvuje u proseku; u suprotnom promenićeš rezultat.

## Prazan skup i grupe bez numeričkih vrednosti

Ako agregatni upit bez `GROUP BY` nema nijedan ulazni red, i dalje vraća jedan rezultatni red. `AVG()` u njemu vraća `NULL`:

```sql
SELECT AVG(Milliseconds) AS average_milliseconds
FROM tracks
WHERE AlbumId = -1;
```

Ako postoji grupa, ali su sve vrednosti njenog izraza `NULL`, red grupe postoji, a `AVG()` za tu grupu je `NULL`. Ako nema nijednog ulaznog reda i upit koristi `GROUP BY`, nema grupa i nema izlaznih redova.

`AVG()` vraća `NULL` i kada su svi argumenti `NULL`, kao u ovom primeru:

```sql
WITH sample(album_id, milliseconds) AS (
    VALUES (1, NULL), (1, NULL)
)
SELECT album_id, AVG(milliseconds) AS average_milliseconds
FROM sample
GROUP BY album_id;
```

Grupa `album_id = 1` se vraća, ali je prosek `NULL`. Razlikuj to od praznog skupa: u ovom primeru postoje dva reda, samo nemaju numeričko trajanje.

Tabela naglašava razliku između praznog ulaza i ulaza sa redovima čije su vrednosti `NULL`:

| Ulaz               | `COUNT(*)` | `COUNT(value)` | `AVG(value)` |
| ------------------ | ---------: | -------------: | ------------ |
| Bez redova         |          0 |              0 | `NULL`       |
| Dva reda sa `NULL` |          2 |              0 | `NULL`       |

`AVG()` daje `NULL` u oba slučaja, zato uz njega proveri i broj redova ili broj nenultih vrednosti ako treba da razlikuješ „nema podataka“ od „postoje redovi bez vrednosti“.

## `AVG(DISTINCT ...)` i ponovljene vrednosti

Podrazumevani `AVG()` računa svaku pojavu vrednosti. Ako se neka vrednost ponavlja, svaka pojava utiče na prosek:

```sql
WITH sample(milliseconds) AS (
    VALUES (60000), (60000), (120000), (NULL)
)
SELECT
    AVG(milliseconds) AS average_all,
    AVG(DISTINCT milliseconds) AS average_distinct
FROM sample;
```

Očekivano: `80000.0 | 90000.0`.

- `AVG(milliseconds)` računa `(60000 + 60000 + 120000) / 3`.
- `AVG(DISTINCT milliseconds)` računa `(60000 + 120000) / 2`.
- `NULL` se ignoriše u oba izraza.

`DISTINCT` nije alat za uklanjanje „dupliranih redova“ bez razumevanja podataka. Ako dva zapisa predstavljaju dve stvarne numere istog trajanja, obe treba da utiču na prosečno trajanje. Koristi `AVG(DISTINCT ...)` samo kada je cilj prosek jedinstvenih vrednosti, a ne prosek svih događaja ili zapisa.

## SQLite tipovi i numeričke vrednosti

SQLite agregatne funkcije rade nad vrednostima, a kolone mogu sadržati različite storage klase. `AVG()` tretira tekstualnu ili BLOB vrednost koja ne izgleda kao broj kao `0`, ali je i dalje računa kao nenultu vrednost u imenitelju:

```sql
WITH sample(value) AS (
    VALUES ('10'), ('not numeric'), (NULL)
)
SELECT
    COUNT(value) AS non_null_values,
    AVG(value) AS average_value
FROM sample;
```

U SQLite-u rezultat je `2 | 5.0`: `'10'` doprinosi kao 10, tekst `'not numeric'` kao 0, a `NULL` se ignoriše. Ovo može dati rezultat koji na prvi pogled deluje neočekivano; proveri tip i kvalitet podataka pre računanja.

`AVG()` u SQLite-u vraća floating-point rezultat, i kada su ulazni brojevi celi. Realni brojevi mogu imati uobičajenu binarnu grešku preciznosti; za vrednosti poput novca razmisli o modelovanju jedinica kao celih brojeva, na primer centi, i zaokruži samo kada je to potrebno.

Pošto je rezultat realni broj, `AVG()` izbegava integer overflow koji bi mogao da se desi kada `SUM()` sabira isključivo cele brojeve. To ne znači da je rezultat tačan za proizvoljno velike cele brojeve: floating-point vrednost ima ograničenu preciznost. Možeš proveriti tip rezultata ovako:

```sql
WITH sample(value) AS (
    VALUES (9223372036854775807), (9223372036854775807)
)
SELECT typeof(AVG(value)) AS result_type
FROM sample;
```

U SQLite-u je `result_type` `real`. Ako su ti potrebni tačni celobrojni proračuni u punom opsegu, nemoj pretpostaviti da je `AVG()` zamena za decimalnu aritmetiku.

## `WHERE`, `GROUP BY` i `HAVING`

`WHERE` uklanja ulazne redove pre računanja proseka:

```sql
SELECT
    AlbumId,
    AVG(Milliseconds) AS average_milliseconds
FROM tracks
WHERE Milliseconds >= 60000
GROUP BY AlbumId
HAVING AVG(Milliseconds) > 300000
ORDER BY average_milliseconds DESC, AlbumId;
```

U ovom primeru:

- `WHERE Milliseconds >= 60000` bira numere koje ulaze u grupe;
- `GROUP BY AlbumId` pravi grupu za svaki album;
- `AVG(Milliseconds)` računa prosek po albumu;
- `HAVING` zadržava samo grupe čiji prosek prelazi 300000 milisekundi;
- `ORDER BY` određuje redosled prikaza.

`AVG()` ne može da se koristi kao agregatni uslov u `WHERE`-u jer se prosek računa tek nakon izbora ulaznih redova i formiranja grupe. Za uslov nad prosekom koristi `HAVING`.

## `AVG()` nakon `JOIN`-a

`AVG()` računa prosek nad redovima koje je proizveo ceo upit. Ako spajanje ponovi red sa istom numeričkom vrednošću, ta vrednost dobija veću težinu u proseku. Na primer, spajanje albuma sa numerama daje po jedan red po numeri, pa `AVG(Milliseconds)` računa prosek numera, a ne prosek albuma. Ako zatim spojiš još jednu tabelu koja ima više odgovarajućih redova za svaku numeru, prosek može biti izmenjen ponavljanjem numera.

Pre agregiranja proveri šta predstavlja jedan red nakon spajanja. Ako cilj jeste prosek po albumima, prvo izračunaj po jedan prosek za svaki album, a zatim odluči da li želiš običan ili ponderisani prosek tih rezultata.

## Veza sa SQLAlchemy 2.0

SQLAlchemy-jev `func.avg()` generiše poziv SQL `AVG()`. Primer pretpostavlja ORM model `Track` sa atributima `album_id` i `milliseconds`:

```python
from sqlalchemy import func, select

statement = (
    select(
        Track.album_id,
        func.count().label("track_count"),
        func.round(
            func.avg(Track.milliseconds) / 60_000.0,
            2,
        ).label("average_minutes"),
    )
    .group_by(Track.album_id)
    .order_by(Track.album_id)
)
```

`label()` daje ime izrazu u rezultatu; ne kreira kolonu u tabeli. Rezultati i dalje zavise od tipova kolona, podataka, `NULL` vrednosti i dijalekta baze.

## Česte greške

- **Očekuješ da `AVG()` računa `NULL` kao nulu:** `NULL` se ignoriše; eksplicitna nula se računa.
- **Koristiš `COUNT(*)` kao imenilac kada prosek ignoriše `NULL`:** broj redova može biti veći od broja vrednosti u proseku.
- **Pogrešno zaokružiš svaku vrednost pre proseka:** sačuvaj preciznost, izračunaj prosek i tek onda zaokruži rezultat.
- **Podeliš celobrojno trajanje celim brojem:** SQLite može skratiti svako trajanje pre nego što `AVG()` dobije vrednost; za konverziju koristi realni delilac poput `60000.0`.
- **Pretpostaviš da `AVG(DISTINCT X)` znači prosek jedinstvenih redova:** uklanjaju se ponovljene vrednosti izraza `X`, čak i kada potiču iz različitih redova.
- **Pretpostaviš da neispravan tekst biva preskočen:** SQLite može da ga tretira kao nulu, a ipak ga uključi u broj vrednosti.
- **Koristiš `WHERE AVG(...)`:** filtriranje na osnovu agregata ide u `HAVING`.
- **Očekuješ `0` za prazan skup ili grupu bez vrednosti:** `AVG()` vraća `NULL`.
- **Osloniš se na redosled grupa bez `ORDER BY`:** SQL ne garantuje redosled rezultata.

## Vežbe

1. Izračunaj prosečno trajanje svih numera u milisekundama.
2. Izračunaj prosečno trajanje svake numere po albumu i prikaži ga u minutima zaokruženim na dve decimale.
3. Dodaj `COUNT(*)` po albumu. Objasni zašto broj numera nije imenilac kada `Milliseconds` sadrži `NULL`.
4. Uporedi `AVG(value)` i `AVG(DISTINCT value)` nad vrednostima `(60000), (60000), (120000), (NULL)`.
5. Napravi prazan CTE i CTE sa redovima čije su prosečne vrednosti sve `NULL`. Uporedi rezultat agregacije bez `GROUP BY` i sa `GROUP BY`.
6. Uporedi `AVG(Milliseconds) / 60000.0` sa `AVG(Milliseconds / 60000)` za album 1. Objasni celobrojno deljenje.
7. Proveri kako `AVG()` u SQLite-u obrađuje `'10'`, `'not numeric'` i `NULL`.
8. Dodaj `HAVING AVG(Milliseconds) > 300000` na grupisani upit i objasni razliku u odnosu na `WHERE`.
9. Uporedi ukupni prosek sa prosekom grupnih proseka kada grupe imaju različit broj vrednosti.
10. Izračunaj uslovni prosek pomoću `AVG(CASE WHEN ... THEN value END)` i proveri šta se menja kada dodaš `ELSE 0`.
11. Objasni kako dodatni `JOIN` koji ponavlja redove može promeniti prosek.

## Provera razumevanja

1. Koje vrednosti ulaze u `AVG(X)`?
2. Da li se `NULL` računa kao nula?
3. Šta vraća `AVG()` ako nema nenultih ulaznih vrednosti?
4. Da li prazan agregatni upit bez `GROUP BY` vraća nula redova ili jedan red sa `NULL` prosekom?
5. Kako `AVG(DISTINCT X)` menja izračunavanje?
6. Zašto prosečno trajanje po albumu zahteva `GROUP BY AlbumId`?
7. Zašto delimo sa `60000.0`, a ne sa `60000` pre računanja proseka?
8. Kada treba koristiti `HAVING` umesto `WHERE`?
9. Kako SQLite može da obradi tekst koji nije numerički u `AVG()`?
10. Zašto rezultat treba zaokružiti nakon računanja proseka, a ne svaku ulaznu vrednost zasebno?
11. Kada se prosek grupnih proseka razlikuje od ukupnog proseka?
12. Zašto je uslovni prosek sa `ELSE 0` drugačiji od `ELSE NULL`?
13. Kako dupliranje redova u rezultatu `JOIN`-a utiče na `AVG()`?

## Izvori za dalje čitanje

- [SQLite: Aggregate Functions — `avg(X)`](https://www.sqlite.org/lang_aggfunc.html#avgunc)
- [SQLite: Expressions — arithmetic operators](https://www.sqlite.org/lang_expr.html)
