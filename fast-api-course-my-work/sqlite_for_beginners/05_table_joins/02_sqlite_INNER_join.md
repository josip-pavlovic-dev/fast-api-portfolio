# 02 — SQLite `INNER JOIN`

## Cilj lekcije

U ovoj lekciji naučićeš kako `INNER JOIN` kombinuje redove iz dve tabele kada postoji poklapanje prema uslovu u `ON` delu upita. Za razliku od `LEFT JOIN`-a, red bez poklapanja ne pojavljuje se u rezultatu.

Koristićemo `tracks` i `albums` iz Chinook baze. Svaka numera ima `AlbumId` koji pokazuje na album; jedan album može imati više numera.

Prethodna lekcija: [`LEFT JOIN`](./01_sqlite_LEFT_join.md). Korisno predznanje: [izbor kolona](../02_retriving_data_and_manipulating_data/03_querying_data_from_specific_columns_in_a_table.md), [aliasi](../02_retriving_data_and_manipulating_data/09_sqlite_aliases.md) i [`NULL`](../02_retriving_data_and_manipulating_data/07_identifying_null_values.md).

## Čemu služi `INNER JOIN`

`INNER JOIN` vraća samo kombinacije redova čiji uslov poklapanja u `ON` delu daje `TRUE`:

```sql
SELECT kolone
FROM prva_tabela AS p
INNER JOIN druga_tabela AS d
    ON uslov_poklapanja;
```

- `ON` definiše kako se redovi iz tabela povezuju.
- Ako red iz jedne tabele nema odgovarajući red u drugoj, ne ulazi u rezultat.
- Ako jedan red ima više poklapanja, dobijaš po jedan rezultat za svaku odgovarajuću kombinaciju.
- `JOIN` bez reči `INNER` podrazumeva unutrašnje spajanje u SQLite-u:

```sql
FROM tracks AS t
JOIN albums AS a
    ON a.AlbumId = t.AlbumId
```

To ima isto značenje kao `FROM tracks AS t INNER JOIN albums AS a ...`.

## Primer iz transkripta: numere i albumi

`tracks.AlbumId` povezuje numeru sa `albums.AlbumId`. Primarni ključ albuma je jedinstven, pa je u ovom modelu svaka numera povezana sa najviše jednim albumom:

```sql
SELECT
    t.TrackId,
    t.Name AS TrackName,
    a.AlbumId,
    a.Title AS AlbumTitle
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
ORDER BY t.TrackId;
```

Kolone su kvalifikovane alias-ima `t` i `a`, tako da je jasno iz koje tabele dolaze. Nije neophodno da kolone na obe strane imaju isto ime: bitno je da `ON` poveže odgovarajuće vrednosti — ovde strani ključ `tracks.AlbumId` sa primarnim ključem `albums.AlbumId`.

Prvih pet redova u priloženoj Chinook kopiji:

| TrackId | TrackName                               | AlbumId | AlbumTitle                            |
| ------: | --------------------------------------- | ------: | ------------------------------------- |
|       1 | For Those About To Rock (We Salute You) |       1 | For Those About To Rock We Salute You |
|       2 | Balls to the Wall                       |       2 | Balls to the Wall                     |
|       3 | Fast As a Shark                         |       3 | Restless and Wild                     |
|       4 | Restless and Wild                       |       3 | Restless and Wild                     |
|       5 | Princess of the Dawn                    |       3 | Restless and Wild                     |

U toj bazi spoj vraća **3.503 reda**, koji predstavljaju **3.503 različite numere** sa **347 albuma**. Svi redovi `tracks` u ovoj kopiji imaju poklapanje u `albums`.

Broj redova i jedinstvenih ključeva možeš proveriti ovako:

```sql
SELECT
    COUNT(*) AS joined_rows,
    COUNT(DISTINCT t.TrackId) AS distinct_tracks,
    COUNT(DISTINCT a.AlbumId) AS albums_in_result
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId;
```

Očekivani rezultat je `3503 | 3503 | 347`. Brojevi važe za priloženu Chinook kopiju; u drugoj bazi mogu biti drugačiji.

## Zašto se nazivi albuma ponavljaju?

U transkriptu se nazivi albuma ponavljaju u više redova. To je očekivano: tabela `tracks` ima jedan red po numeri, a svaki red rezultata sadrži podatke o numeri i njenom albumu. Album zato ponavlja svoj `Title` za svaku numeru koja mu pripada.

Na primer, album `Greatest Hits` u priloženoj bazi ima 57 numera. Spoj zato prikazuje njegov naslov uz 57 različitih redova numera. To nisu duplikati istih numera.

Ako želiš listu svih numera sa albumom, zadrži `TrackId` i `TrackName`. Ako želiš samo jedinstvenu listu albuma koji imaju numere, izaberi identitet albuma i ukloni ponovljene izlazne vrednosti:

```sql
SELECT DISTINCT
    a.AlbumId,
    a.Title
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
ORDER BY a.AlbumId;
```

`DISTINCT` menja oblik rezultata, ne tabelu. Nemoj ga dodavati samo zato što je naslov albuma ponovljen: ponovljeni naslov može predstavljati ispravnu vezu sa više različitih numera.

## Poklapanje, ključevi i kardinalnost

U `ON` delu poveži kolone koje predstavljaju stvarnu relaciju — najčešće FK u jednoj tabeli i PK ili jedinstveni ključ u drugoj:

```sql
ON a.AlbumId = t.AlbumId
```

Nemoj birati kolone samo zato što im se nazivi poklapaju ili zato što trenutno sadrže slične tekstualne vrednosti. Pogrešan uslov može dati nedostajuće redove ili mnogo više kombinacija nego što očekuješ.

Broj redova zavisi od broja poklapanja:

- bez poklapanja: red se izostavlja;
- jedno poklapanje: nastaje jedan rezultat;
- više poklapanja: nastaje po jedan rezultat za svako poklapanje.

Ako povezuješ tabelu sa roditeljskom kolonom koja nije jedinstvena, jedan red leve tabele može se poklopiti sa više redova desne tabele. To može biti ispravno za vezu 1:N ili N:M, ali moraš znati koju kombinaciju predstavlja jedan rezultat.

## `INNER JOIN` naspram `LEFT JOIN`

| Ponašanje | `INNER JOIN` | `LEFT JOIN` |
|---|---|---|
| Red sa poklapanjem | Vraća kombinaciju | Vraća kombinaciju |
| Red leve tabele bez poklapanja | Izostavlja ga | Zadržava ga i postavlja desne kolone na `NULL` |
| Red desne tabele bez poklapanja | Izostavlja ga | Ne čuva ga samo zbog `LEFT JOIN`-a |

Na primeru `artists` i `albums`, prethodna lekcija koristi `LEFT JOIN` da sačuva svih 275 izvođača, uključujući 71 bez albuma. `INNER JOIN` bi zadržao samo izvođače koji imaju barem jedan album. Pogledaj [LEFT JOIN primer i objašnjenje](./01_sqlite_LEFT_join.md).

Za `tracks INNER JOIN albums` u trenutnoj kopiji svi redovi `tracks` imaju album, pa broj rezultata odgovara broju numera. To je slučaj u ovim podacima, ne opšte pravilo niti razlog da se `INNER JOIN` i `LEFT JOIN` smatraju zamenljivim.

## `NULL` vrednosti i nepoklopljeni redovi

Kada `ON` koristi obično poređenje jednakosti (`=`), `NULL = neka_vrednost` i `NULL = NULL` ne daju `TRUE`; rezultat je nepoznat (`NULL`/`UNKNOWN`). Takav par ne zadovoljava uslov unutrašnjeg spoja, pa se red bez validnog poklapanja izostavlja.

Razlikuj dve situacije:

1. **Nema povezanog reda:** `INNER JOIN` ne vraća red.
2. **Povezani red postoji, ali neka njegova opciona kolona je `NULL`:** red se vraća, a ta izabrana kolona je `NULL`.

`INNER JOIN` zahteva poklapanje prema `ON` uslovu, ne da svaka izabrana kolona bude popunjena. Ako je join ključ nullable, redovi sa `NULL` ključem obično neće imati poklapanje pomoću `=`.

## Filteri u `ON` i `WHERE`

Za unutrašnji spoj, uslov koji ograničava poklapanja može se pisati u `ON` delu:

```sql
SELECT t.TrackId, t.Name, a.Title
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
   AND a.Title LIKE 'A%'
ORDER BY t.TrackId;
```

Ili kao filter rezultata u `WHERE` delu:

```sql
SELECT t.TrackId, t.Name, a.Title
FROM tracks AS t
INNER JOIN albums AS a
    ON a.AlbumId = t.AlbumId
WHERE a.Title LIKE 'A%'
ORDER BY t.TrackId;
```

U ovim primerima oba uslova moraju biti tačna da bi red ušao u rezultat. Kod `INNER JOIN`-a takav filter ne čuva nepoklopljene redove, jer ih unutrašnji spoj već izostavlja. Nemoj ovo pravilo automatski preneti na `LEFT JOIN`: tamo premeštanje uslova između `ON` i `WHERE` može promeniti koje se leve strane zadržavaju.

## Redosled klauzula

Kada kombinuješ spajanje sa dodatnim filtriranjem, sortiranjem i ograničavanjem rezultata, piši klauzule ovim redosledom:

```sql
SELECT kolone
FROM prva_tabela
INNER JOIN druga_tabela
    ON uslov_poklapanja
WHERE dodatni_filter
ORDER BY kolona
LIMIT broj_redova;
```

`ON` definiše parove koji se spajaju, `WHERE` filtrira rezultat, `ORDER BY` ga sortira, a `LIMIT` ograničava broj vraćenih redova. Bez `ORDER BY` redosled nije garantovan.

## Veza sa SQLAlchemy 2.0 i FastAPI-jem

U SQLAlchemy 2.0 metoda `.join()` pravi unutrašnji spoj:

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

Primer pretpostavlja modele `Track` i `Album` sa navedenim atributima. SQLAlchemy može koristiti i definisanu ORM relaciju, na primer `.join(Track.album)`, ako takva relacija postoji. U FastAPI endpointu proveri oblik rezultata: naslov albuma može se ponoviti za više numera, pa odgovor ne predstavlja jedinstvenu listu albuma.

## Česte greške

- **Očekuješ da unutrašnji spoj zadrži redove bez para:** takve redove izostavlja; koristi `LEFT JOIN` ako treba sačuvati levu stranu.
- **Spajaš kolone samo zato što imaju isto ime:** `ON` treba da izrazi stvarnu relaciju PK/FK ili drugo namerno pravilo.
- **Iznenade te ponovljeni naslovi:** jedan album može imati više numera; svaki rezultat predstavlja povezani par.
- **Dodaješ `DISTINCT` da sakriješ ponovljeni naslov:** prvo proveri da li su redovi zaista duplikati ili predstavljaju različite povezane zapise.
- **Ne kvalifikuješ kolone:** koristi alias-e poput `t.AlbumId` i `a.AlbumId` da izbegneš nejasnoće i greške.
- **Pretpostaviš da se `NULL` poklapa sa `NULL` pomoću `=`:** takav uslov nije `TRUE`; red neće zadovoljiti `INNER JOIN`.
- **Pretpostaviš redosled redova:** dodaj `ORDER BY`, a za stabilan redosled uključi jedinstveni kriterijum.
- **Preneseš `ON`/`WHERE` zaključke sa unutrašnjeg na spoljašnji spoj:** `LEFT JOIN` ima drugačije ponašanje za nepoklopljene leve redove.

## Vežbe

1. Spoji `tracks` i `albums` preko `AlbumId`; prikaži `TrackId`, naziv numere i naslov albuma.
2. Dodaj `ORDER BY TrackId` i `LIMIT 5`. Uporedi rezultat sa tabelom u lekciji.
3. Izračunaj broj redova spoja, različitih numera i različitih albuma. Uporedi sa očekivanim vrednostima `3503`, `3503` i `347` u priloženoj bazi.
4. Pronađi album koji se pojavljuje uz više numera. Objasni zašto ponovljen naslov nije dupliran red numere.
5. Napravi jedinstvenu listu albuma sa `DISTINCT AlbumId, Title` i uporedi je sa rezultatom koji sadrži sve numere.
6. Uporedi `tracks INNER JOIN albums` sa `tracks LEFT JOIN albums`. Zašto u ovoj kopiji imaju isti broj redova i u kom slučaju bi se razlikovali?
7. Promeni uslov spajanja na pogrešnu kolonu ili izostavi ključnu komponentu. Proveri kako se broj redova menja, pa vrati ispravan `ON` uslov.
8. U SQLAlchemy 2.0 sastavi isti upit pomoću `.join()` i prikaži ga uz sortiranje po `Track.track_id`.

## Provera razumevanja

1. Koji redovi ulaze u rezultat `INNER JOIN`-a?
2. Šta uloga `ON` uslova znači za spajanje `tracks` i `albums`?
3. Da li dve kolone moraju imati isto ime da bi se mogle povezati?
4. Zašto se naslov istog albuma pojavljuje uz više numera?
5. Kada `LEFT JOIN` vraća red koji bi `INNER JOIN` izostavio?
6. Zašto `NULL` join ključ ne daje poklapanje u poređenju pomoću `=`?
7. Zašto `COUNT(*)` nad spojenim tabelama ne mora biti broj redova leve tabele?
8. Šta je razlika između ponovljenog naslova albuma i dupliranog zapisa numere?
9. Zašto je `ORDER BY` potreban kada očekuješ stabilan redosled?
10. Zašto filteri u `ON` i `WHERE` mogu imati različit uticaj na `LEFT JOIN`?

## Izvori za dalje čitanje

- [SQLite: SELECT — JOIN syntax and processing](https://www.sqlite.org/lang_select.html)
- [SQLAlchemy 2.0: Using SELECT Statements — Joins](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#explicit-from-clauses-and-joins)
