# Dan 06 — Čitanje i manipulisanje podacima

## Cilj dana

Danas vežbaš `SELECT` upite nad Chinook bazom: izbor izraza i kolona, čitanje rezultata, sortiranje i filtriranje, uklanjanje ponovljenih vrednosti, obradu `NULL`, SQLite tipove i aliase.

Koristi ovaj dnevnik kao objašnjenje, a radne upite čuvaj u odgovarajućim `.sql` fajlovima:

- Lekcija (`.md`) objašnjava pojam i postavlja zadatke.
- `.sql` fajl sadrži proverena rešenja i SQL komentare. Pokušaj prvo samostalno da napišeš upit, pa ga pokreni ili uporedi sa rešenjem.
- SQLite CLI ili SQLTools izvršava upit nad konkretnom konekcijom i bazom.

Ovaj dnevnik prati [lekcije oblasti 02](../02_retriving_data_and_manipulating_data/README.md) i dopunjuje način rada objašnjen u [danu 05](./dan_05_intro_and_cli_vezbe.md).

## 1. Bezbedan način rada

### Radna baza

Za Chinook primere koristi radnu kopiju `chinook_practice.db`, a ne originalni `chinook.db` niti bazu aplikacije. Iz korena repozitorijuma možeš otvoriti kopiju samo za čitanje:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

U SQLite CLI promptu možeš pokrenuti, na primer:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/01_sqlite_select_statement.sql
```

Promeni naziv fajla prema lekciji. `.read` unosi sadržaj fajla u već otvorenu konekciju; ne pokreće se u Bash promptu.

U SQLTools-u proveri aktivnu konekciju i punu putanju baze. Zatim otvori odgovarajući `.sql` fajl i pokreni `-- @block` ili označeni upit. Naziv konekcije sam po sebi nije dokaz da je aktivna prava baza.

Fajlovi `01–07` i `09` sadrže upite za čitanje. Fajl `08` pravi samo `TEMP` tabele u trenutnoj konekciji; one ne menjaju glavnu Chinook datoteku i nestaju kada se konekcija zatvori. U SQLTools-u pokreni setup i proveru `TEMP` tabele na istoj konekciji. SQLite `STRICT` primer zahteva verziju 3.37.0 ili noviju; proveri `SELECT sqlite_version();`, jer SQLTools i CLI mogu koristiti različite SQLite biblioteke.

### Proverene vrednosti u trenutnoj radnoj kopiji

Sledeće brojke su iz proverene verzije tvoje `chinook_practice.db`; ako se baza kasnije promeni, ponovo pokreni upite za brojanje:

| Tabela / provera                       |   Rezultat |
| -------------------------------------- | ---------: |
| `albums`                               | 347 redova |
| `artists`                              | 275 redova |
| `tracks`                               |  3503 reda |
| `customers`                            |  59 redova |
| Različiti gradovi u `customers.City`   |         53 |
| Različite države u `customers.Country` |         24 |
| Kupci sa `Company IS NULL`             |         49 |
| Numere sa `Composer IS NULL`           |        978 |

---

## 2. Rešenja i objašnjenja vežbi

## Lekcija 01 — `SELECT`: čitanje podataka i izraza

Radni fajl: [01_sqlite_select_statement.sql](../playground/sql/02_retriving_data_and_manipulating_data/01_sqlite_select_statement.sql)
Teorija: [01_sqlite_select_statement.md](../02_retriving_data_and_manipulating_data/01_sqlite_select_statement.md)

### Vežba 1 — Izračunaj bez tabele

`SELECT` može izračunati izraze bez `FROM` klauzule:

```sql
SELECT 7 + 7 AS zbir;

SELECT
    10 / 2 AS rezultat_deljenja,
    3 * 5 AS rezultat_mnozenja;

SELECT
    5 / 2 AS celobrojno,
    5.0 / 2 AS decimalno;
```

Rezultati su redom `14`; `5` i `15`; zatim `2` i `2.5`. Kod `5 / 2` oba operanda su cela broja, pa SQLite radi celobrojno deljenje. `5.0` je realan broj, zato drugi izraz daje `2.5`.

Alias posle `AS` daje čitljiv naziv koloni rezultata. On ne menja bazu niti pravi novu kolonu.

### Vežba 2 — Pročitaj pet albuma

```sql
SELECT AlbumId, Title
FROM albums
ORDER BY AlbumId
LIMIT 5;
```

Prvih pet redova u radnoj kopiji:

| AlbumId | Title                                   |
| ------: | --------------------------------------- |
|       1 | For Those About To Rock (We Salute You) |
|       2 | Balls to the Wall                       |
|       3 | Restless and Wild                       |
|       4 | Let There Be Rock                       |
|       5 | Big Ones                                |

`SELECT` bira dve kolone, `FROM` određuje izvor, `ORDER BY` daje predvidiv redosled, a `LIMIT` ograničava broj vraćenih redova. ERD prikazuje strukturu i veze; ovaj upit vraća podatke iz tabela.

### Vežba 3 — Istraži `DISTINCT`

```sql
SELECT ArtistId
FROM albums
ORDER BY ArtistId;

SELECT DISTINCT ArtistId
FROM albums
ORDER BY ArtistId;
```

Prvi upit vraća po jedan `ArtistId` za svaki album, dakle 347 redova. Drugi vraća 204 različite vrednosti `ArtistId`. Razlika postoji zato što jedan umetnik može imati više albuma.

Sa više kolona `DISTINCT` poredi celu izabranu kombinaciju:

```sql
SELECT DISTINCT ArtistId, Title
FROM albums
ORDER BY ArtistId, Title;
```

Ovaj upit ne traži samo različite umetnike. Redovi se smatraju istim samo kada su iste i vrednosti `ArtistId` i `Title`.

`DISTINCT` uklanja ponavljanja iz rezultata, ne iz tabele. Bez `ORDER BY` ne treba zaključivati o redosledu dobijenih različitih vrednosti.

### Vežba 4 — Prepoznaj klauzule

```sql
SELECT ArtistId, COUNT(*) AS album_count
FROM albums
WHERE ArtistId > 0
GROUP BY ArtistId
HAVING COUNT(*) > 1
ORDER BY album_count DESC, ArtistId ASC
LIMIT 5;
```

- `FROM albums` bira izvor redova.
- `WHERE ArtistId > 0` odbacuje ulazne redove pre grupisanja.
- `GROUP BY ArtistId` pravi po jednu grupu za svaki umetnik.
- `COUNT(*)` broji albume u grupi, a `AS album_count` imenuje rezultat.
- `HAVING COUNT(*) > 1` uklanja grupe sa samo jednim albumom.
- `ORDER BY album_count DESC` stavlja veće brojeve prve.
- `ArtistId ASC` razrešava izjednačenja u broju albuma i čini redosled stabilnijim.
- `LIMIT 5` vraća najviše pet grupa.

Bez završnog `ArtistId` kriterijuma redosled grupa sa jednakim `album_count` nije garantovan. U radnoj kopiji pet prvih redova sa ovim tie-breaker-om su `(90, 21)`, `(22, 14)`, `(58, 11)`, `(50, 10)` i `(150, 10)`.

## Lekcija 02 — Čitanje svih kolona

Radni fajl: [02_querying_data_from_all_columns_in_a_table.sql](../playground/sql/02_retriving_data_and_manipulating_data/02_querying_data_from_all_columns_in_a_table.sql)
Teorija: [02_querying_data_from_all_columns_in_a_table.md](../02_retriving_data_and_manipulating_data/02_querying_data_from_all_columns_in_a_table.md)

### Vežba 1 — Prikaži sve kolone

```sql
SELECT *
FROM albums;
```

U radnoj kopiji vraća 347 redova i tri kolone: `AlbumId`, `Title` i `ArtistId`, redom kako su definisane u tabeli. Broj redova možeš proveriti ovako:

```sql
SELECT COUNT(*) AS album_count
FROM albums;
```

`PRAGMA table_info(albums);` prikazuje šemu i pozicije kolona. To je pregled definicije tabele, ne sadržaja njenih redova.

### Vežba 2 — Ograniči pregled

```sql
SELECT *
FROM albums
ORDER BY AlbumId
LIMIT 5;
```

Rezultat ima iste tri kolone kao prethodni upit, ali samo pet redova. `LIMIT` utiče na broj redova, ne na broj ili redosled kolona. `ORDER BY AlbumId` je važan jer bez sortiranja „prvih pet“ nije pouzdano definisano.

### Vežba 3 — Uporedi širok i uzak rezultat

```sql
SELECT *
FROM albums
ORDER BY AlbumId
LIMIT 5;

SELECT AlbumId, Title
FROM albums
ORDER BY AlbumId
LIMIT 5;
```

Oba upita vraćaju istih pet albuma. Prvi vraća tri kolone, drugi dve. Izbor konkretnih kolona ne filtrira redove.

U FastAPI endpointu obično je bolje birati samo polja koja odgovor zaista koristi. Tako je jasno šta endpoint vraća i ne prenose se nepotrebne kolone.

### Vežba 4 — Preciziraj izvor kolona

```sql
SELECT albums.*
FROM albums
ORDER BY AlbumId
LIMIT 5;
```

`albums.*` bira sve kolone iz tabele `albums`. To nije „sve kolone iz svih tabela baze“. Ovaj zapis je koristan kada upit kasnije koristi više tabela.

### Vežba 5 — Primeni na `artists`

```sql
SELECT artists.*
FROM artists
ORDER BY ArtistId
LIMIT 5;

SELECT ArtistId, Name
FROM artists
ORDER BY ArtistId
LIMIT 5;
```

Prvih pet umetnika po ID-ju su AC/DC, Accept, Aerosmith, Alanis Morissette i Alice In Chains. Oba upita vraćaju iste redove; prvi bira sve kolone iz `artists`, drugi samo `ArtistId` i `Name`.

## Lekcija 03 — Čitanje određenih kolona

Radni fajl: [03_querying_data_from_specific_columns_in_a_table.sql](../playground/sql/02_retriving_data_and_manipulating_data/03_querying_data_from_specific_columns_in_a_table.sql)
Teorija: [03_querying_data_from_specific_columns_in_a_table.md](../02_retriving_data_and_manipulating_data/03_querying_data_from_specific_columns_in_a_table.md)

### Vežba 1 — Izaberi četiri kolone

```sql
SELECT TrackId, Name, Composer, UnitPrice
FROM tracks
ORDER BY TrackId;
```

Rezultat ima četiri kolone. U radnoj kopiji `tracks` ima 3503 reda. `Composer` može biti `NULL`; prazna vrednost u nekim klijentima može izgledati kao prazna ćelija.

```sql
SELECT COUNT(*) AS track_count
FROM tracks;
```

Brojanje proverava redove, ne broj izabranih kolona.

### Vežba 2 — Promeni redosled kolona

```sql
SELECT Name, TrackId, UnitPrice, Composer
FROM tracks
ORDER BY TrackId;
```

Upit vraća iste podatke kao u Vežbi 1, ali kolone se pojavljuju redom navedenim posle `SELECT`. Broj redova se ne menja.

### Vežba 3 — Ograniči rezultat

```sql
SELECT TrackId, Name, UnitPrice
FROM tracks
ORDER BY TrackId
LIMIT 5;
```

Rezultat ima tri kolone i pet redova. `SELECT` bira kolone, `ORDER BY` sortira redove, a `LIMIT` ograničava njihov broj.

### Vežba 4 — Izaberi kolone iz druge tabele

```sql
SELECT ArtistId, Name
FROM artists
ORDER BY ArtistId
LIMIT 5;
```

Uporedi sa `SELECT * FROM artists ORDER BY ArtistId LIMIT 5;`. Isti umetnici se prikazuju, ali `SELECT *` može vratiti dodatne kolone.

### Vežba 5 — Pronađi vrednosti koje nedostaju

Pri pregledu `Composer` u rezultatu prve vežbe uočićeš da, na primer, numera `TrackId = 2` nema poznatog kompozitora. Kada si već prošao lekciju o `NULL`, pronađi sve takve redove:

```sql
SELECT TrackId, Name, Composer
FROM tracks
WHERE Composer IS NULL
ORDER BY TrackId;
```

U radnoj kopiji 978 numera ima `Composer IS NULL`. To nisu nužno prazni tekstovi; `NULL` se proverava sa `IS NULL`, ne sa `= NULL`.

## Lekcija 04 — Sortiranje pomoću `ORDER BY`

Radni fajl: [04_sorting_data_using_order_by_clause.sql](../playground/sql/02_retriving_data_and_manipulating_data/04_sorting_data_using_order_by_clause.sql)
Teorija: [04_sorting_data_using_order_by_clause.md](../02_retriving_data_and_manipulating_data/04_sorting_data_using_order_by_clause.md)

### Vežba 1 — Rastući redosled

```sql
SELECT TrackId, Name, AlbumId
FROM tracks
ORDER BY AlbumId ASC, TrackId ASC;
```

Isti smer dobijaš bez `ASC`, jer je rastući smer podrazumevan:

```sql
SELECT TrackId, Name, AlbumId
FROM tracks
ORDER BY AlbumId, TrackId;
```

Dodati `TrackId` razrešava redosled numera koje pripadaju istom albumu.

### Vežba 2 — Deset najdužih numera

```sql
SELECT TrackId, Name, Milliseconds
FROM tracks
ORDER BY Milliseconds DESC, TrackId ASC
LIMIT 10;
```

`DESC` prikazuje veća trajanja prva. Prvih pet u trenutnoj bazi su:

| TrackId | Name                        | Milliseconds |
| ------: | --------------------------- | -----------: |
|    2820 | Occupation / Precipice      |      5286953 |
|    3224 | Through a Looking Glass     |      5088838 |
|    3244 | Greetings from Earth, Pt. 1 |      2960293 |
|    3242 | The Man With Nine Lives     |      2956998 |
|    3227 | Battlestar Galactica, Pt. 2 |      2956081 |

`TrackId ASC` čini izbor predvidivim kada dve numere imaju isto trajanje.

### Vežba 3 — Sortiraj po više kolona

```sql
SELECT TrackId, AlbumId, Name, Milliseconds
FROM tracks
ORDER BY AlbumId ASC, TrackId DESC
LIMIT 8;
```

Prvo se sortiraju albumi rastuće, a unutar istog albuma ID-jevi numera opadajuće. Prvih osam redova pripada albumu `AlbumId = 1`, sa `TrackId` vrednostima od 14 do 7.

### Vežba 4 — Sortiraj po neprikazanoj koloni

```sql
SELECT Name, AlbumId
FROM tracks
ORDER BY Milliseconds ASC, TrackId ASC
LIMIT 5;
```

`Milliseconds` utiče na redosled, iako nije prikazan. `TrackId` razrešava jednake vrednosti trajanja.

### Vežba 5 — Stabilan redosled

```sql
SELECT TrackId, Name, Milliseconds
FROM tracks
ORDER BY Milliseconds DESC, TrackId ASC
LIMIT 10;
```

Ovo rešava zadatak sa deset najdužih numera. Ako izostaviš jedinstveni `TrackId` kriterijum, redovi sa istim trajanjem mogu menjati međusobni redosled. To je naročito važno uz straničenje (`LIMIT`/`OFFSET`).

### Ivični slučajevi pri sortiranju

- Bez `ORDER BY`, redosled rezultata nije garantovan.
- Ako više redova ima istu vrednost u svim kriterijumima `ORDER BY`, njihov međusobni redosled i dalje nije definisan. Dodaj jedinstveni ključ.
- SQLite podrazumevano sortira `NULL` pre ostalih vrednosti u `ASC`, a posle njih u `DESC`. `NULLS FIRST` i `NULLS LAST` omogućavaju eksplicitan položaj u SQLite-u 3.30.0+.
- Prazan tekst `''` nije `NULL`, pa ga `NULLS LAST` ne pomera na kraj.
- Ugrađeni `NOCASE` zanemaruje ASCII velika/mala slova, ali nije lokalizovano sortiranje srpskog teksta.

## Lekcija 05 — Uklanjanje ponavljanja pomoću `DISTINCT`

Radni fajl: [05_removing_duplicate_records_using_distinct_clause.sql](../playground/sql/02_retriving_data_and_manipulating_data/05_removing_duplicate_records_using_distinct_clause.sql)
Teorija: [05_removing_duplicate_records_using_distinct_clause.md](../02_retriving_data_and_manipulating_data/05_removing_duplicate_records_using_distinct_clause.md)

### Vežba 1 — Spisak gradova

```sql
SELECT City
FROM customers;

SELECT DISTINCT City
FROM customers
ORDER BY City;
```

Prvi upit vraća grad kupca za svaki red — 59 redova. Drugi uklanja ponovljene vrednosti `City` samo iz rezultata i vraća 53 grada. `ORDER BY` uređuje prikaz; sam `DISTINCT` ne garantuje redosled.

```sql
SELECT COUNT(DISTINCT City) AS unique_city_count
FROM customers;
```

Rezultat je 53 u trenutnoj kopiji.

### Vežba 2 — Spisak država

```sql
SELECT DISTINCT Country
FROM customers
ORDER BY Country;

SELECT COUNT(DISTINCT Country) AS unique_country_count
FROM customers;
```

U radnoj kopiji ima 24 različite države. Broj država nije broj kupaca; `DISTINCT` prikazuje samo jedinstvene vrednosti izabrane kolone.

### Vežba 3 — Jedinstveni parovi država i gradova

```sql
SELECT DISTINCT Country, City
FROM customers
ORDER BY Country, City;
```

Upit vraća jedinstvene parove, ne samo države. Provereni broj parova je 53:

```sql
SELECT COUNT(*) AS unique_country_city_pairs
FROM (
    SELECT DISTINCT Country, City
    FROM customers
);
```

Ako je `Country` isti, a `City` različit, redovi nisu duplikati za ovaj rezultat.

### Vežba 4 — Predvidi rezultat

```sql
WITH sample(Country, City) AS (
    VALUES
        ('Brazil', 'São Paulo'),
        ('Brazil', 'São Paulo'),
        ('Brazil', 'Rio de Janeiro')
)
SELECT DISTINCT Country, City
FROM sample
ORDER BY Country, City;
```

Rezultat sadrži dva reda: jedan za par `Brazil`–`Rio de Janeiro` i jedan za `Brazil`–`São Paulo`. Dva identična reda za São Paulo svedena su na jedan.

### Vežba 5 — Razlikuj rezultat od tabele

```sql
SELECT City
FROM customers
ORDER BY City, CustomerId;

SELECT DISTINCT City
FROM customers
ORDER BY City;
```

Prvi upit prikazuje ponavljanja iz izvornih redova kupaca; drugi ih uklanja samo iz rezultata. Nijedan od ovih `SELECT` upita ne menja tabelu.

### Ivični slučajevi za `DISTINCT`

```sql
WITH sample(city) AS (
    VALUES ('Paris'), ('PARIS'), ('Paris'), (NULL), (NULL), ('')
)
SELECT DISTINCT city
FROM sample
ORDER BY city;
```

Sa podrazumevanom `BINARY` kolacijom rezultat zadržava `Paris` i `PARIS` kao različite vrednosti, jedan `NULL` i prazan tekst. `NULL` vrednosti se pri `SELECT DISTINCT` svode na jednu, ali `''` je posebna tekstualna vrednost.

Ako izraz koristi `COLLATE NOCASE`, ugrađeni SQLite poredi ASCII velika i mala slova kao jednaka:

```sql
WITH sample(city) AS (
    VALUES ('Paris'), ('PARIS'), ('Paris'), (NULL), (NULL), ('')
)
SELECT DISTINCT city COLLATE NOCASE AS city
FROM sample
ORDER BY city COLLATE NOCASE;
```

`COUNT(DISTINCT city)` ne broji `NULL`, jer agregat `COUNT(expression)` ignoriše `NULL` vrednosti. Zato upit `SELECT DISTINCT city` može prikazati jedan `NULL`, dok `COUNT(DISTINCT city)` broji samo različite vrednosti koje nisu `NULL`.

## Lekcija 06 — Filtriranje pomoću `WHERE`

Radni fajl: [06_filtering_data_with_where_clause.sql](../playground/sql/02_retriving_data_and_manipulating_data/06_filtering_data_with_where_clause.sql)
Teorija: [06_filtering_data_with_where_clause.md](../02_retriving_data_and_manipulating_data/06_filtering_data_with_where_clause.md)

### Vežba 1 — Filtriraj po albumu

```sql
SELECT Name, Composer, AlbumId
FROM tracks
WHERE AlbumId = 1;
```

U trenutnoj kopiji uslov vraća 10 numera. Za pregled prva četiri reda sortirana po ID-ju:

```sql
SELECT TrackId, Name, Composer, AlbumId
FROM tracks
WHERE AlbumId = 1
ORDER BY TrackId
LIMIT 4;
```

Vraćeni su `TrackId` 1, 6, 7 i 8. `LIMIT 4` ne znači da postoje samo četiri odgovarajuća reda; ukupno ih je deset.

### Vežba 2 — Filtriraj po poređenju

```sql
SELECT TrackId, Name, Milliseconds
FROM tracks
WHERE Milliseconds > 300000
ORDER BY Milliseconds DESC, TrackId ASC
LIMIT 5;
```

Uslov `>` je strogo veće od 300000; red sa tačno 300000 ne bi bio uključen. Sortiranje prikazuje najduže prve, a `TrackId` razrešava izjednačenja.

### Vežba 3 — Filtriraj kupce po tekstu

```sql
SELECT CustomerId, FirstName, LastName, Country
FROM customers
WHERE Country = 'Brazil'
ORDER BY LastName, FirstName, CustomerId
LIMIT 5;
```

Tekst je u jednostrukim navodnicima. U trenutnoj kopiji prvih pet kupaca po prezimenu i imenu su Roberto Almeida, Luís Gonçalves, Eduardo Martins, Fernanda Ramos i Alexandre Rocha.

### Vežba 4 — Kombinuj `AND` i `OR`

Namera zadatka je: numera je sa albuma 1 **ili** 2, i u oba slučaja mora trajati duže od 240000 ms:

```sql
SELECT TrackId, Name, AlbumId, Milliseconds
FROM tracks
WHERE (AlbumId = 1 OR AlbumId = 2)
  AND Milliseconds > 240000
ORDER BY AlbumId, TrackId;
```

Rezultat ima pet redova u ovoj kopiji. Zagrade određuju da li se uslov dužine primenjuje na oba albuma.

Bez zagrada:

```sql
WHERE AlbumId = 1 OR AlbumId = 2 AND Milliseconds > 240000
```

`AND` ima jači prioritet od `OR`, pa se ovo tumači kao:

```sql
WHERE AlbumId = 1
   OR (AlbumId = 2 AND Milliseconds > 240000)
```

Zbog toga se u radnoj kopiji vraća 11 redova. To nije ista logika kao nameravani uslov sa zagradama.

### Vežba 5 — Pronađi nepoznate vrednosti

```sql
SELECT TrackId, Name, Composer
FROM tracks
WHERE Composer IS NULL
ORDER BY TrackId;
```

Ovo vraća numere bez poznatog kompozitora — 978 redova u radnoj kopiji. Suprotan uslov:

```sql
SELECT TrackId, Name, Composer
FROM tracks
WHERE Composer IS NOT NULL
ORDER BY TrackId;
```

`Composer <> 'neki kompozitor'` ne uključuje automatski redove gde je `Composer` `NULL`: poređenje tada daje `UNKNOWN`, a `WHERE` zadržava samo `TRUE`.

### Tekstualni obrasci: `LIKE` i `GLOB`

```sql
SELECT CustomerId, FirstName, LastName
FROM customers
WHERE FirstName LIKE 'A%'
ORDER BY LastName, CustomerId;
```

U ovoj kopiji dobijaju se Astrid Gruber, Aaron Mitchell i Alexandre Rocha. Kod `LIKE`, `%` znači nula ili više znakova, a `_` tačno jedan znak. `GLOB` koristi druge džokere (`*` i `?`) i podrazumevano je osetljiv na velika i mala slova. Ne mešaj ih.

## Lekcija 07 — Prepoznavanje `NULL`

Radni fajl: [07_identifying_null_values.sql](../playground/sql/02_retriving_data_and_manipulating_data/07_identifying_null_values.sql)
Teorija: [07_identifying_null_values.md](../02_retriving_data_and_manipulating_data/07_identifying_null_values.md)

### Vežba 1 — Kupci bez kompanije

```sql
SELECT CustomerId, FirstName, LastName, Company
FROM customers
WHERE Company IS NULL
ORDER BY CustomerId;
```

U radnoj kopiji ima 49 takvih redova. Za brojanje:

```sql
SELECT COUNT(*) AS customers_without_company
FROM customers
WHERE Company IS NULL;
```

### Vežba 2 — Kupci sa kompanijom

```sql
SELECT CustomerId, FirstName, LastName, Company
FROM customers
WHERE Company IS NOT NULL
ORDER BY CustomerId;
```

Rezultat sadrži 10 redova. Zbir 49 + 10 = 59, što odgovara broju svih kupaca.

Razliku možeš proveriti i agregatima:

```sql
SELECT
    COUNT(*) AS all_customers,
    COUNT(Company) AS customers_with_company,
    COUNT(*) - COUNT(Company) AS customers_without_company
FROM customers;
```

Rezultat je `(59, 10, 49)`. `COUNT(*)` broji redove; `COUNT(Company)` preskače vrednosti `NULL`. Prazan tekst bi se računao kao vrednost.

### Vežba 3 — Uporedi `NULL` i prazan tekst

```sql
SELECT CustomerId, Company
FROM customers
WHERE Company IS NULL;

SELECT CustomerId, Company
FROM customers
WHERE Company = '';
```

Prvi upit vraća 49 redova. Drugi trenutno ne vraća nijedan, jer nema praznih tekstova u `Company`. U drugoj bazi rezultat može biti drugačiji. `NULL` je nepoznata/nedostajuća vrednost, dok je `''` poznat tekst dužine nula.

### Vežba 4 — Primeni na `Composer`

Koristi `Composer IS NULL` da pronađeš nepoznate kompozitore; `IS NOT NULL` pronalazi poznate. Provereno je 978 `NULL` i 2525 poznatih vrednosti u `tracks`.

Nemoj koristiti `= NULL` ili `<> NULL`. Na primer, `NULL = NULL` daje `NULL`/nepoznato, dok `NULL IS NULL` daje tačno.

## Lekcija 08 — SQLite tipovi i klase skladištenja

Radni fajl: [08_sqllite_data_types.sql](../playground/sql/02_retriving_data_and_manipulating_data/08_sqllite_data_types.sql)
Teorija: [08_sqllite_data_types.md](../02_retriving_data_and_manipulating_data/08_sqllite_data_types.md)

### Vežba 1 — Proveri pet klasa vrednosti

```sql
SELECT
    typeof(100),
    typeof(10.5),
    typeof('SQLite'),
    typeof(X'53514C'),
    typeof(NULL);
```

Rezultat je `integer`, `real`, `text`, `blob`, `null`. `typeof()` opisuje konkretnu vrednost/izraz, ne deklaraciju kolone.

### Vežba 2 — Istraži afinitet

Privremeni primer:

```sql
DROP TABLE IF EXISTS temp.affinity_demo;

CREATE TEMP TABLE affinity_demo (
    integer_value INTEGER,
    text_value TEXT,
    blob_value BLOB
);

INSERT INTO affinity_demo
VALUES ('42', 42, X'53514C');

SELECT
    integer_value, typeof(integer_value),
    text_value, typeof(text_value),
    blob_value, typeof(blob_value)
FROM affinity_demo;
```

Afinitet `INTEGER` pretvara tekst `'42'` u ceo broj 42. Afinitet `TEXT` pretvara broj 42 u tekst `'42'`. BLOB literal ostaje binarna vrednost. Zatim, obična `INTEGER` kolona i dalje može da primi `'not a number'`, jer se ta vrednost ne može konvertovati i ostaje klase `text`. Zato deklaracija `INTEGER` u običnoj SQLite tabeli nije stroga garancija tipa.

Ovo su `TEMP` tabele: postoje samo na istoj konekciji i bezbedne su za ovaj eksperiment; ne menjaju Chinook glavnu datoteku.

### Vežba 3 — Obična i `STRICT` tabela

SQLite `STRICT` tabele zahtevaju verziju 3.37.0 ili noviju:

```sql
CREATE TEMP TABLE strict_demo (
    value INTEGER
) STRICT;

INSERT INTO strict_demo VALUES (42.0);
INSERT INTO strict_demo VALUES (NULL);

SELECT value, typeof(value)
FROM strict_demo;
```

`42.0` može bez gubitka da se konvertuje u integer 42. `NULL` je dozvoljen jer kolona nema `NOT NULL`. `STRICT` proverava tip, ali sam ne dodaje `NOT NULL`, `UNIQUE` ni `CHECK`.

Očekivano odbijeni pokušaji (u fajlu su komentarisani da ne bi prekidali normalno izvršavanje):

```sql
INSERT INTO strict_demo VALUES ('not a number');
INSERT INTO strict_demo VALUES (42.5);
```

Tekst nije moguće pretvoriti u integer. `42.5` bi izgubio decimalni deo pri pretvaranju u integer, pa ni ta konverzija nije bez gubitka i `STRICT` je odbija. Pokreni svaki pokušaj zasebno ako želiš da vidiš grešku.

### Vežba 4 — Proveri Chinook tipove

```sql
PRAGMA table_info(tracks);

SELECT
    TrackId, typeof(TrackId),
    Name, typeof(Name),
    Milliseconds, typeof(Milliseconds),
    UnitPrice, typeof(UnitPrice)
FROM tracks
LIMIT 1;
```

U šemi su deklaracije `TrackId INTEGER`, `Name NVARCHAR(200)`, `Milliseconds INTEGER` i `UnitPrice NUMERIC(10,2)`. U postojećim redovima odgovarajuće klase su `integer`, `text`, `integer` i `real`. Deklarisani tip i runtime storage class nisu ista informacija.

SQLite nema posebnu storage klasu za boolean, datum ili vreme. `TRUE` i `FALSE` se ponašaju kao `1` i `0` (storage class `integer`); datumi se obično čuvaju kao ISO tekst, Julian day broj ili Unix vreme. `NUMERIC(10,2)` u običnoj tabeli nije garancija fiksne decimalne preciznosti: `REAL` koristi binarni floating point.

## Lekcija 09 — Aliasi kolona i tabela

Radni fajl: [09_sqlite_aliases.sql](../playground/sql/02_retriving_data_and_manipulating_data/09_sqlite_aliases.sql)
Teorija: [09_sqlite_aliases.md](../02_retriving_data_and_manipulating_data/09_sqlite_aliases.md)

### Vežba 1 — Skrati zaglavlja rezultata

```sql
SELECT
    CustomerId AS id,
    FirstName AS first_name,
    LastName AS last_name
FROM customers
ORDER BY CustomerId
LIMIT 3;
```

Vraća ista tri kupca kao izvorne kolone, ali zaglavlja su `id`, `first_name` i `last_name`. Primer prvog reda je `(1, 'Luís', 'Gonçalves')`. `AS` ne preimenuje kolone u tabeli.

### Vežba 2 — Koristi alias tabele

```sql
SELECT c.FirstName, c.LastName, c.City
FROM customers AS c
WHERE c.City LIKE 'A%'
ORDER BY c.LastName, c.CustomerId;
```

U radnoj kopiji rezultat je Johannes Van der Berg iz Amsterdama. `c` označava tabelu `customers`, pa se kolone pišu `c.City`, `c.FirstName` itd.

### Vežba 3 — Kombinuj alias tabele i kolona

```sql
SELECT
    c.FirstName AS first_name,
    c.LastName AS last_name,
    c.City AS city
FROM customers AS c
WHERE c.City LIKE 'A%'
ORDER BY last_name, c.CustomerId;
```

Rezultat ima tri alias zaglavlja. SQLite dozvoljava alias kolone u `ORDER BY`. `CustomerId` je dodat kao tie-breaker ako se prezimena ponavljaju.

### Vežba 4 — Prepoznaj opseg aliasa

```sql
SELECT CustomerId AS id, FirstName AS first_name
FROM customers
WHERE CustomerId = 1
ORDER BY id;
```

`id` se može koristiti u `ORDER BY`, ali naziv kolone u tabeli ostaje `CustomerId`. Sledeći zaseban upit ne radi jer tabela nema kolonu `id`:

```sql
SELECT id
FROM customers;
```

SQLite ponekad prihvata alias iz `SELECT` liste u `WHERE` kao nestandardno proširenje, ali nemoj se oslanjati na to ako želiš prenosiv SQL. Koristi stvarnu kolonu (`WHERE FirstName = ...`) ili obavij izračunati rezultat u podupit/CTE. Kada tabeli dodeliš alias `c`, u tom upitu koristi `c.City`; `customers.City` više nije ispravno ime izvora.

---

## 3. Kratka provera razumevanja

1. **Da li `SELECT *` garantuje redosled redova?** Ne. Za predvidiv redosled koristi `ORDER BY`.
2. **Da li `LIMIT 5` samo po sebi bira iste redove svaki put?** Ne, ne bez dovoljno stabilnog `ORDER BY`.
3. **Da li `DISTINCT City` briše ponavljanja iz tabele?** Ne, uklanja ih samo iz rezultata.
4. **Šta `DISTINCT Country, City` čini jedinstvenim?** Ceo par vrednosti.
5. **Kako se proverava nedostajuća vrednost?** `IS NULL` ili `IS NOT NULL`, nikad `= NULL`.
6. **Zašto `COUNT(*)` i `COUNT(Company)` daju različite rezultate?** Prvi broji sve redove; drugi ignoriše `NULL` u koloni.
7. **Da li `INTEGER` deklaracija u običnoj SQLite tabeli odbija svaku tekstualnu vrednost?** Ne. Afinitet pokušava konverziju; obične tabele su fleksibilne.
8. **Da li alias menja šemu?** Ne, važi samo u okviru upita.
9. **Da li je `NOCASE` srpska lokalizovana kolacija?** Ne, ugrađeni `NOCASE` pokriva ASCII velika/mala slova.
10. **Koje su SQLite specifičnosti ovog dana?** Storage klase, afinitet, `typeof()`, `STRICT` i pojedina ponašanja kolacija; osnovni `SELECT`, filtriranje i sortiranje prenose se na druge baze.

## 4. Na šta da obratiš pažnju prema planu učenja

U ovoj oblasti temeljno savladaj veštine koje ćeš koristiti i u MySQL-u i PostgreSQL-u:

- sastavi `SELECT` iz izvora, izabranih kolona, uslova, sortiranja i ograničenja;
- razlikuj filtriranje redova (`WHERE`) od izbora kolona (`SELECT`);
- koristi `ORDER BY` uz jedinstveni tie-breaker kada redosled mora biti stabilan;
- razumi kako `DISTINCT` poredi celu izabranu kombinaciju i da ne menja tabelu;
- tretiraj `NULL` kao posebnu nepoznatu vrednost i pravilno ga filtriraj;
- proveri da li agregat broji sve redove ili preskače `NULL`;
- u aplikaciji biraj samo kolone koje endpoint koristi i koristi parametarsko vezivanje kroz SQLAlchemy.

SQLite specifičnosti poput afiniteta, storage klasa, `STRICT`, `NOCASE` i predstavljanja datuma treba da razumeš dovoljno da prepoznaš njihov uticaj, ali ne moraš pamtiti SQLite interne detalje. Kada pređeš na drugu bazu, proveri tipove, kolacije, `LIMIT`/paginaciju i ponašanje transakcija konkretne baze.

Za pregled prioriteta u celoj oblasti koristi i [README oblasti 02](../02_retriving_data_and_manipulating_data/README.md), dopunjen prema [planu učenja](../plan_ucenja/sta_je_vazno.md).
