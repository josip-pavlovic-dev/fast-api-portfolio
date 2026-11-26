# 07 — SQLite `GROUP_CONCAT()` funkcija

## Cilj lekcije

`GROUP_CONCAT()` je agregatna funkcija koja spaja vrednosti iz više redova u jedan tekstualni rezultat. Može da napravi jedan spisak za ceo ulazni skup ili zaseban spisak za svaku grupu definisanu pomoću `GROUP BY`.

Transkript koristi `tracks` tabelu i pravi listu naziva numera za album čiji je `AlbumId` jednak `10`. U lekciji ćemo obraditi separatore, redosled vrednosti, `NULL`, prazne stringove, duplikate, `DISTINCT`, grupisanje, spajanja i ograničenja dužine rezultata.

Prethodno: [SQLite `MIN()`](./06_sqlite_MIN_function.md). Povezane lekcije: [uvod u agregatne funkcije](./01_introduction_to_sqlite_aggregate_functions.md), [`GROUP BY`](./08_sqlite_GROUP_BY_clause.md) i [`HAVING`](./09_sqlite_HAVING_clause.md).

## Osnovna sintaksa

```text
GROUP_CONCAT(izraz [, separator] [ORDER BY redosled_izraza])
GROUP_CONCAT(DISTINCT izraz [ORDER BY redosled_izraza])
```

- `GROUP_CONCAT(izraz)` spaja nenulte vrednosti izraza i kao separator koristi zarez bez razmaka: `,`.
- `GROUP_CONCAT(izraz, separator)` koristi zadati separator između spojenih vrednosti.
- `GROUP_CONCAT(DISTINCT izraz)` prvo uklanja ponovljene vrednosti izraza.
- `ORDER BY` unutar poziva određuje redosled vrednosti u konkateniranom rezultatu.

Funkcija vraća tekstualnu vrednost. `NULL` vrednosti izraza se preskaču; ako nema nijedne vrednosti za spajanje, rezultat je `NULL`.

## Lista numera za jedan album

Osnovni primer iz transkripta pravi listu naziva numera za album 10:

```sql
SELECT GROUP_CONCAT(Name) AS track_names
FROM tracks
WHERE AlbumId = 10;
```

U priloženoj Chinook kopiji album 10 ima 14 numera. Podrazumevani separator je zarez bez razmaka. Pošto poziv nema svoj `ORDER BY`, redosled spojenih naziva nije garantovan.

Za stabilan, čitljiv rezultat navedi separator i redosled unutar agregata:

```sql
SELECT GROUP_CONCAT(Name, ', ' ORDER BY TrackId) AS track_names
FROM tracks
WHERE AlbumId = 10;
```

Rezultat je lista od 14 naziva poređanih po `TrackId`, razdvojenih zarezom i razmakom. `ORDER BY` u ovom pozivu uređuje elemente unutar liste.

## Redosled elemenata i verzija SQLite-a

Agregat bez unutrašnjeg `ORDER BY` nema garantovan redosled ulaznih vrednosti. Redosled može da se promeni zbog indeksa, plana izvršavanja, promena podataka ili verzije SQLite-a. Spoljašnji `ORDER BY` sortira rezultatne redove, ali ne određuje redosled vrednosti unutar svakog stringa:

```sql
SELECT
    AlbumId,
    GROUP_CONCAT(Name, ', ') AS track_names
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;
```

Ovde su albumi sortirani, ali redosled numera u svakoj listi nije određen. Za stabilan redosled koristi `ORDER BY` kao deo agregata:

```sql
SELECT
    AlbumId,
    GROUP_CONCAT(Name, ', ' ORDER BY Name, TrackId) AS track_names
FROM tracks
GROUP BY AlbumId
ORDER BY AlbumId;
```

`TrackId` je dodat kao tie-breaker da redosled bude potpun i predvidljiv kada se nazivi numera ponavljaju. SQLite podržava `ORDER BY` unutar agregatnog poziva od verzije 3.44.0. Na starijoj verziji ovaj oblik može prijaviti sintaksnu grešku; proveri verziju pomoću `SELECT sqlite_version();`.

Nemoj se oslanjati na sortiranje podupita kao zamenu za unutrašnji `ORDER BY` ako ti je potreban garantovan redosled agregata. Za verzije koje podržavaju agregatni `ORDER BY`, navedi redosled direktno u `GROUP_CONCAT()`.

## Prilagođeni separator

Separator može biti bilo koji tekstualni izraz. Primeri su `', '`, `' | '` ili novi red:

```sql
SELECT
    GROUP_CONCAT(Name, ' | ' ORDER BY TrackId) AS track_names
FROM tracks
WHERE AlbumId = 10;
```

Ako je separator `NULL`, SQLite ne umeće tekst između susednih vrednosti. Na primer, vrednosti `'a'` i `'b'` uz `NULL` separator daju `ab`. Ako je čitljivost važna, izaberi separator koji jasno razdvaja vrednosti i ne pojavljuje se često unutar samih vrednosti.

Separator se koristi samo između vrednosti koje ulaze u konkatenaciju, ne pre prve niti posle poslednje vrednosti.

## `NULL`, prazni stringovi i prazan skup

`GROUP_CONCAT()` preskače `NULL` vrednosti. Prazan string (`''`) nije `NULL`, pa učestvuje u rezultatu kao prazna stavka:

```sql
WITH sample(value) AS (
    VALUES ('a'), (NULL), (''), ('b')
)
SELECT
    COUNT(*) AS input_rows,
    COUNT(value) AS non_null_values,
    GROUP_CONCAT(value, '|') AS concatenated
FROM sample;
```

Rezultat je `4 | 3 | a||b`. Red sa `NULL` se izostavlja. Prazan string ostaje, a separator se pojavljuje i pre i posle te prazne stavke.

Ako agregat nema ulazne redove ili su sve vrednosti `NULL`, `GROUP_CONCAT()` vraća `NULL`:

```sql
WITH empty(value) AS (
    SELECT 'x'
    WHERE 0
),
all_null(value) AS (
    VALUES (NULL), (NULL)
)
SELECT
    'empty' AS input_case,
    COUNT(*) AS input_rows,
    GROUP_CONCAT(value) AS concatenated
FROM empty
UNION ALL
SELECT
    'all NULL',
    COUNT(*),
    GROUP_CONCAT(value)
FROM all_null;
```

Prvi red predstavlja prazan ulaz: `COUNT(*)` je `0`, a rezultat konkatenacije je `NULL`. Drugi ima dva ulazna reda, ali oba su `NULL`; rezultat konkatenacije je takođe `NULL`. Ako je potreban tekstualni prikaz poput `''` ili oznaka „nema vrednosti“, obradi `NULL` eksplicitno, na primer sa `COALESCE(GROUP_CONCAT(...), '')`, samo ako to odgovara značenju podataka.

Uz `GROUP BY`, grupa čiji su izrazi svi `NULL` i dalje postoji, ali je rezultat `GROUP_CONCAT()` za tu grupu `NULL`. Ako je ulaz prazan, nema grupa ni izlaznih redova.

## Duplikati, `DISTINCT` i separator

Podrazumevani `GROUP_CONCAT()` zadržava ponovljene vrednosti. Ako vrednost `x` postoji tri puta, u listi će se pojaviti tri puta:

```sql
WITH sample(value) AS (
    VALUES ('rock'), ('jazz'), ('rock'), (NULL)
)
SELECT
    GROUP_CONCAT(value, ' | ' ORDER BY value) AS all_values,
    GROUP_CONCAT(DISTINCT value ORDER BY value) AS unique_values
FROM sample;
```

Rezultat je `jazz | rock | rock` i `jazz,rock`. `DISTINCT` uklanja ponovljene vrednosti izraza; ne uklanja redove iz tabele i ne menja podatke.

SQLite ne prihvata prilagođeni separator direktno uz `DISTINCT`:

```sql
WITH sample(value) AS (
    VALUES ('rock'), ('jazz'), ('rock')
)
SELECT GROUP_CONCAT(DISTINCT value, ' | ')
FROM sample;
```

Ovaj oblik prijavljuje grešku zato što SQLite zahteva da agregat sa `DISTINCT` ima tačno jedan argument. Ako želiš jedinstvene vrednosti i sopstveni separator, izdvoji ih u podupitu pa ih spoji spolja:

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

Rezultat je `jazz | rock`. `WHERE value IS NOT NULL` čini nameru vidljivom, iako bi spoljašnji `GROUP_CONCAT()` svakako ignorisao `NULL`.

Poređenje `DISTINCT` vrednosti poštuje kolaciju izraza. Na primer, `COLLATE NOCASE` može tretirati `'a'` i `'A'` kao duplikate. Ako su vrednosti jednake prema kolaciji, nemoj zavisiti od toga koje će se izvorno pisanje zadržati u rezultatu.

## Vrednosti različitih tipova

SQLite može u koloni imati različite storage klase. `GROUP_CONCAT()` ih pretvara u tekstualni rezultat:

```sql
WITH sample(value) AS (
    VALUES (1), (2.5), ('x'), (NULL)
)
SELECT GROUP_CONCAT(value, '; ' ORDER BY value) AS concatenated
FROM sample;
```

U SQLite-u rezultat je `1; 2.5; x`. `NULL` se izostavlja, a preostale vrednosti se prikazuju kao tekst. Nemoj koristiti `GROUP_CONCAT()` kao način validacije ili čuvanja tipiziranih podataka; rezultat je jedan string i ne čuva pouzdano granice vrednosti ako separator postoji i unutar samih podataka.

## `GROUP_CONCAT()` sa `GROUP BY`, `WHERE` i `HAVING`

`WHERE` bira redove pre grupisanja, `GROUP BY` određuje koje vrednosti ulaze u svaku listu, a `HAVING` može da ukloni grupe nakon agregacije:

```sql
SELECT
    AlbumId,
    COUNT(*) AS track_count,
    GROUP_CONCAT(Name, ', ' ORDER BY TrackId) AS track_names
FROM tracks
WHERE Name IS NOT NULL
GROUP BY AlbumId
HAVING COUNT(*) >= 10
ORDER BY AlbumId;
```

- `WHERE Name IS NOT NULL` bira redove pre grupisanja. Kod `GROUP_CONCAT(Name)` ovaj uslov nije neophodan samo radi izbacivanja `NULL` naziva, jer ih funkcija ignoriše; ovde jasno pokazuje gde se filtriraju ulazni redovi.
- `GROUP BY AlbumId` pravi zasebnu listu za svaki album.
- `HAVING COUNT(*) >= 10` zadržava albume sa najmanje 10 ulaznih redova.
- `ORDER BY AlbumId` sortira izlazne grupe.

## Spajanja mogu ponoviti stavke

`GROUP_CONCAT()` konkatenira redove koje je proizveo ceo upit. Ako `JOIN` umnoži redove, vrednosti će se ponoviti i u listi. Pre agregiranja proveri šta predstavlja jedan red nakon spajanja i da li je ponavljanje smisleno.

Nemoj automatski dodati `DISTINCT` da bi sakrio neočekivano umnožavanje: možda postoje stvarni ponovljeni zapisi ili je uslov `JOIN`-a pogrešan. Ako lista treba da sadrži jedinstvene stavke, definiši eksplicitno koje kolone određuju jedinstvenost, izdvoji ih u podupitu i zatim ih konkateniraj.

## Dužina rezultata

Konkatenirani rezultat zauzima memoriju i podleže SQLite ograničenju dužine stringa (`SQLITE_LIMIT_LENGTH`). Veoma veliki rezultat može izazvati grešku umesto da se tiho skrati. Za velike skupove razmotri da li je jedna duga tekstualna vrednost zaista pravi izlaz ili je bolje vratiti redove odvojeno i spojiti ih u aplikaciji.

## Veza sa SQLAlchemy 2.0

U SQLite upitu SQLAlchemy `func.group_concat()` poziva SQLite funkciju. Primer pretpostavlja modele `Track` i `Album`:

```python
from sqlalchemy import func, select

statement = (
    select(
        Track.album_id,
        func.group_concat(Track.name, ", ").label("track_names"),
    )
    .group_by(Track.album_id)
    .order_by(Track.album_id)
)
```

`GROUP_CONCAT()` je SQLite specifično ime; drugi dijalekti mogu koristiti drugačiju funkciju ili sintaksu, na primer `string_agg`. `label()` imenuje rezultatnu kolonu i ne kreira kolonu u tabeli. Ovaj ORM primer ne određuje redosled elemenata unutar liste; za njega je potreban `ORDER BY` unutar agregatnog izraza, uz podršku odgovarajućeg dijalekta i SQLite verzije.

## Česte greške

- **Očekuješ da je redosled elemenata podrazumevano stabilan:** navedi `ORDER BY` unutar agregata.
- **Sortiraš samo izlazne grupe:** spoljašnji `ORDER BY` ne uređuje elemente unutar svakog stringa.
- **Očekuješ da separator podrazumevano sadrži razmak:** podrazumevani separator je samo zarez.
- **Misliš da se prazan string preskače kao `NULL`:** `''` učestvuje u rezultatu i može stvoriti susedne separatore.
- **Očekuješ prazan string za prazan skup:** rezultat je `NULL`, osim ako ga eksplicitno ne obradiš.
- **Koristiš `DISTINCT` sa separatorom kao drugim argumentom:** SQLite odbacuje taj oblik; koristi podupit.
- **Koristiš `DISTINCT` da sakriješ problematičan `JOIN`:** prvo proveri zašto se redovi ponavljaju.
- **Pretpostaviš da rezultat čuva granice originalnih vrednosti:** separator može postojati unutar podataka, pa string možda nije moguće jednoznačno rastaviti.
- **Ignorišeš verziju SQLite-a:** unutrašnji `ORDER BY` za agregate zahteva SQLite 3.44.0 ili noviji.
- **Pretpostaviš da konkatenirani rezultat može biti proizvoljno dug:** rezultat podleže ograničenju dužine i memorije.

## Vežbe

1. Napravi listu naziva numera za `AlbumId = 10` pomoću podrazumevanog separatora.
2. Ponovi upit sa separatorom `', '` i eksplicitnim redosledom po `TrackId`.
3. Grupisano napravi listu numera za svaki album.
4. Uporedi redosled sa i bez `ORDER BY` unutar agregata. Objasni koji redosled je garantovan.
5. Napravi skup sa ponovljenim vrednostima i uporedi `GROUP_CONCAT(value)` sa `GROUP_CONCAT(DISTINCT value)`.
6. Koristi podupit da napraviš listu jedinstvenih vrednosti sa separatorom `' | '`.
7. Napravi ulaz koji sadrži `NULL` i prazan string. Uporedi `COUNT(*)`, `COUNT(value)` i rezultat konkatenacije.
8. Uporedi rezultat praznog skupa sa grupom koja postoji, ali sadrži samo `NULL` vrednosti.
9. Ispitaj šta se događa kada je separator `NULL`.
10. Razmisli kako bi `JOIN` koji ponavlja redove promenio listu.

## Provera razumevanja

1. Šta vraća `GROUP_CONCAT(X)` i koji separator koristi ako ga ne navedeš?
2. Da li se `NULL` vrednosti konkateniraju?
3. Da li se prazan string tretira kao `NULL`?
4. Kakav je rezultat konkatenacije nad praznim skupom?
5. Zašto `ORDER BY` izvan agregata ne uređuje vrednosti unutar liste?
6. Kako se `DISTINCT` ponaša u `GROUP_CONCAT()`?
7. Zašto SQLite odbija `GROUP_CONCAT(DISTINCT X, separator)`?
8. Kako možeš dobiti jedinstvene vrednosti sa prilagođenim separatorom?
9. Kako `JOIN` može da napravi duplikate u rezultatu?
10. Od koje verzije SQLite-a je podržan `ORDER BY` unutar agregatnog poziva?

## Izvori za dalje čitanje

- [SQLite: Aggregate Functions — `group_concat(X,Y)`](https://www.sqlite.org/lang_aggfunc.html#group_concat)
- [SQLite: Aggregate Functions — redosled unutar agregata](https://www.sqlite.org/lang_aggfunc.html)
- [SQLite: Limits — maksimalna dužina stringa ili BLOB-a](https://www.sqlite.org/limits.html#max_length)
