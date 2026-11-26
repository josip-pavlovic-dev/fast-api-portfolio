# Dan 08 — SQLite operatori: `BETWEEN`, `IN`, `LIKE`, `GLOB` i `LIMIT`

> **Važna napomena:** naziv „Dan 08“ je oznaka dokumenta, a ne očekivanje da se sav materijal uradi za jedan dan. Ovaj vodič prati vežbe iz cele oblasti 04, odnosno svih pet lekcija. Slobodno ga rasporedi u više sesija; nastavi kada razumeš trenutnu temu, ne prema kalendaru.

## Cilj oblasti

U ovoj oblasti proširuješ filtriranje iz oblasti 02 operatorima koji su se već pojavljivali u ranijim primerima i pitanjima:

- `BETWEEN` proverava opseg;
- `IN` proverava pripadnost skupu vrednosti ili rezultatu podupita;
- `LIKE` traži tekstualni obrazac pomoću `%` i `_`;
- `GLOB` koristi SQLite obrasce `*`, `?` i skupove znakova;
- `LIMIT` i `OFFSET` ograničavaju i dele rezultat na stranice.

Ovaj vodič povezuje teoriju sa proverenim primerima i SQL skriptama:

- [teorija oblasti 04](../04_some_sqlite_operators/)
- [SQL vežbe oblasti 04](../playground/sql/04_some_sqlite_operators/)
- [plan učenja](../plan_ucenja/sta_je_vazno.md)
- prethodni vodič za [čitanje i filtriranje podataka](./dan_06_retriving_data_and_manipulating_data_vezbe.md)

Svaka SQL skripta je samo za čitanje. Prvo pokušaj vežbu samostalno, pa pokreni odgovarajući `-- @block` ili ceo fajl i uporedi rezultat.

## 1. Bezbedan način rada

### Koristi Chinook kopiju samo za čitanje

Skripte iz oblasti 04 izvršavaju `SELECT` upite; ne menjaju tabele niti redove. Ipak, radi na lokalnoj `chinook_practice.db` kopiji, ne na bazi FastAPI aplikacije. U SQLite CLI-ju iz root-a repozitorijuma možeš otvoriti kopiju u read-only režimu:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Zatim učitaj jednu skriptu, na primer:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/04_some_sqlite_operators/01_sqlite_BETWEEN_operator.sql
```

U SQLTools-u izaberi vezu `ChinookPractice` i proveri da pokazuje na kopiju iz `playground/databases/`. Svaka skripta sadrži `-- @block` oznake kako bi u SQLTools-u mogao da izvršiš samo jedan deo.

### Očekivani rezultati zavise od podataka

Brojevi ispod provereni su nad priloženom Chinook bazom. Ako je tvoja radna kopija izmenjena ili ima drugačiju verziju podataka, `COUNT(*)` i uzorci mogu da se razlikuju, iako pravila operatora ostaju ista.

| Provera u Chinook bazi                                       | Očekivani rezultat |
| ------------------------------------------------------------ | -----------------: |
| `invoices.Total BETWEEN 5 AND 10`                            |         115 računa |
| `invoices.Total NOT BETWEEN 5 AND 10`                        |         297 računa |
| `invoices.Total BETWEEN 5 AND 10 AND BillingCountry = 'USA'` |          25 računa |
| `tracks.Milliseconds BETWEEN 180000 AND 240000`              |         982 numere |
| Računi iz januara 2009.                                      |           6 računa |
| `tracks.MediaTypeId IN (1, 2)`                               |       3.271 numera |
| `tracks.MediaTypeId NOT IN (1, 2)`                           |         232 numere |
| `customers.Country IN ('Brazil', 'Canada')`                  |          13 kupaca |
| `tracks.Name LIKE 'Wild%'`                                   |           5 numera |
| `tracks.Name GLOB 'Man*'`                                    |          11 numera |
| `tracks.Name GLOB '*Man'`                                    |          28 numera |
| Redovi u `tracks`                                            |       3.503 numere |
| `tracks.AlbumId = 1`                                         |          10 numera |

Ove brojke pomažu da prepoznaš rezultat, ali važnije je da razumeš uslov koji ga proizvodi. Ne očekuj da svaka druga SQLite baza vrati iste redove.

---

## 2. Rešenja i objašnjenja vežbi

## Lekcija 01 — `BETWEEN`

Teorija: [01_sqlite_BETWEEN_operator.md](../04_some_sqlite_operators/01_sqlite_BETWEEN_operator.md)
Radni fajl: [01_sqlite_BETWEEN_operator.sql](../playground/sql/04_some_sqlite_operators/01_sqlite_BETWEEN_operator.sql)

### Vežba 1 — Računi u opsegu od 5 do 10

```sql
SELECT InvoiceId, BillingAddress, Total
FROM invoices
WHERE Total BETWEEN 5 AND 10
ORDER BY Total, InvoiceId;
```

U Chinook kopiji uslov vraća 115 redova. `BETWEEN` uključuje obe granice, pa bi vrednosti tačno `5` i `10` takođe odgovarale uslovu.

Da proveriš ukupan broj bez prikazivanja svih računa:

```sql
SELECT COUNT(*) AS broj_racuna
FROM invoices
WHERE Total BETWEEN 5 AND 10;
```

Rezultat je `115`.

Za stabilan prikaz prvih pet redova:

```sql
SELECT InvoiceId, BillingAddress, Total
FROM invoices
WHERE Total BETWEEN 5 AND 10
ORDER BY Total, InvoiceId
LIMIT 5;
```

Očekivani rezultat:

| InvoiceId | BillingAddress         | Total |
| --------: | ---------------------- | ----: |
|         3 | Grétrystraat 63        |  5.94 |
|        10 | 3 Chatham Street       |  5.94 |
|        17 | 319 N. Frances Street  |  5.94 |
|        24 | Ullevålsveien 14       |  5.94 |
|        31 | 9, Place Louis Barthou |  5.94 |

`LIMIT 5` ne menja to da postoji 115 pogodaka; prikazuje samo pet od njih.

### Vežba 2 — Proveri uključive granice

```sql
SELECT
    5 BETWEEN 5 AND 10 AS donja_granica,
    10 BETWEEN 5 AND 10 AS gornja_granica,
    4.99 BETWEEN 5 AND 10 AS ispod_opsega,
    10.01 BETWEEN 5 AND 10 AS iznad_opsega;
```

Rezultat je `1, 1, 0, 0`. SQLite prikazuje tačno kao `1`, a netačno kao `0`.

Uslov je ekvivalentan sledećem za uobičajen stabilan izraz:

```sql
vrednost >= 5 AND vrednost <= 10
```

U SQLite-u se levi izraz kod `BETWEEN` evaluira jednom. Ako ga napišeš dva puta kao dva odvojena poređenja, izrazi mogu biti evaluirani odvojeno; to je važno samo za posebne ili nedeterminističke izraze, ne za običnu kolonu.

### Vežba 3 — Vrednosti izvan opsega

```sql
SELECT COUNT(*) AS broj_van_opsega
FROM invoices
WHERE Total NOT BETWEEN 5 AND 10;
```

Rezultat je `297`. Za običnu numeričku vrednost ovo je ekvivalentno uslovu:

```sql
Total < 5 OR Total > 10
```

Iznosi `5` i `10` nisu van opsega, zato nisu izabrani. Kolona `Total` u ovoj bazi je `NOT NULL`; kod nullable kolone poređenje sa `NULL` ne bi dalo `TRUE`, pa red ne bi ušao ni u `BETWEEN` ni u `NOT BETWEEN` rezultat.

### Vežba 4 — Kombinuj opseg sa dodatnim uslovom

```sql
SELECT InvoiceId, BillingCountry, Total
FROM invoices
WHERE (Total BETWEEN 5 AND 10)
  AND BillingCountry = 'USA'
ORDER BY Total, InvoiceId;
```

Uslov vraća 25 računa. `BETWEEN` ima svoj `AND` unutar sintakse za donju i gornju granicu; poslednji `AND` u `WHERE` dodaje poseban uslov za državu.

### Vežba 5 — Trajanje numera

```sql
SELECT TrackId, Name, Milliseconds
FROM tracks
WHERE Milliseconds BETWEEN 180000 AND 240000
ORDER BY Milliseconds, TrackId
LIMIT 10;
```

U celoj Chinook tabeli 982 numere odgovaraju opsegu. Skripta prikazuje prvih deset prema trajanju i zatim prema `TrackId`. `TrackId` razrešava izjednačenja trajanja.

### Vežba 6 — Ceo januar 2009-te godine

```sql
SELECT InvoiceId, InvoiceDate
FROM invoices
WHERE InvoiceDate >= '2009-01-01 00:00:00'
  AND InvoiceDate <  '2009-02-01 00:00:00'
ORDER BY InvoiceDate, InvoiceId;
```

Rezultat sadrži šest računa iz januara. Koristi se poluotvoren opseg: početak januara je uključen, a početak februara isključen. Tako se obuhvata ceo poslednji dan januara bez pogađanja da li je poslednja moguća vremenska vrednost `23:59:59`, `23:59:59.999...` ili nešto drugo.

Za kolonu koja čuva samo datume u doslednom obliku `YYYY-MM-DD`, `BETWEEN '2025-01-01' AND '2025-01-31'` može biti prikladan. Za timestampove je obično jasnije koristiti `>= početak AND < početak_sledećeg_perioda`.

### Ivični slučajevi za `BETWEEN`

```sql
SELECT COUNT(*) AS obrnuti_opseg
FROM invoices
WHERE Total BETWEEN 10 AND 5;
```

Rezultat je `0`: običan broj ne može istovremeno biti veći ili jednak 10 i manji ili jednak 5. Ako želiš opseg koji prelazi preko granice, napiši kriterijum eksplicitno, najčešće pomoću `OR`.

```sql
SELECT
    NULL BETWEEN 1 AND 10 AS null_u_opsegu,
    NULL NOT BETWEEN 1 AND 10 AS null_van_opsega;
```

Oba rezultata su `NULL` (`UNKNOWN`), a ne `TRUE` ili `FALSE`. `WHERE` zadržava samo `TRUE`. Za pronalaženje nedostajućih vrednosti koristi `IS NULL`.

Kod tekstualnih vrednosti `BETWEEN` radi tekstualno poređenje prema kolaciji; ne traži prefiks i ne obavlja jezički opseg slova. SQLite ima fleksibilne klase skladištenja, pa su za numeričko poređenje važne dosledno sačuvane numeričke vrednosti.

### SQLAlchemy 2.0

```python
from decimal import Decimal

from sqlalchemy import select

minimum = Decimal("5.00")
maximum = Decimal("10.00")

statement = (
    select(Invoice.invoice_id, Invoice.total)
    .where(Invoice.total.between(minimum, maximum))
    .order_by(Invoice.total, Invoice.invoice_id)
)
```

`.between()` uključuje obe granice. Vrednosti se prosleđuju kroz SQLAlchemy izraz, umesto da se spajaju direktno u SQL tekst. U FastAPI endpointu proveri tip i odnos granica; u zavisnosti od proizvoda, možeš odbiti `minimum > maximum` ili posebno definisati šta taj slučaj znači.

---

## Lekcija 02 — `IN`

Teorija: [02_sqlite_IN_operator.md](../04_some_sqlite_operators/02_sqlite_IN_operator.md)
Radni fajl: [02_sqlite_IN_operator.sql](../playground/sql/04_some_sqlite_operators/02_sqlite_IN_operator.sql)

### Vežba 1 — `MediaTypeId` 1 ili 2

```sql
SELECT TrackId, Name, MediaTypeId
FROM tracks
WHERE MediaTypeId IN (1, 2)
ORDER BY Name, TrackId;
```

U Chinook kopiji uslov vraća 3.271 red. Prvih pet po redosledu iz upita:

| TrackId | Name                                                         | MediaTypeId |
| ------: | ------------------------------------------------------------ | ----------: |
|    3027 | `"40"`                                                       |           1 |
|    3412 | `"Eine Kleine Nachtmusik" Serenade In G, K. 525: I. Allegro` |           2 |
|     109 | `#1 Zero`                                                    |           1 |
|    3254 | `#9 Dream`                                                   |           2 |
|     602 | `'Round Midnight`                                            |           1 |

`IN (1, 2)` proverava da li je vrednost jednaka makar jednom članu liste. Ekvivalentni uslov je:

```sql
MediaTypeId = 1 OR MediaTypeId = 2
```

`ORDER BY Name, TrackId` daje predvidiv prikaz; sam `IN` ne sortira rezultate.

### Vežba 2 — Uporedi `IN` sa `OR`

```sql
SELECT COUNT(*) AS sa_or
FROM tracks
WHERE MediaTypeId = 1 OR MediaTypeId = 2;
```

Rezultat je takođe `3.271`. Za poređenje punih skupova redova, pokreni oba oblika sa istim `SELECT` listama i istim `ORDER BY`-om:

```sql
SELECT TrackId, Name, MediaTypeId
FROM tracks
WHERE MediaTypeId IN (1, 2)
ORDER BY Name, TrackId;
```

```sql
SELECT TrackId, Name, MediaTypeId
FROM tracks
WHERE MediaTypeId = 1 OR MediaTypeId = 2
ORDER BY Name, TrackId;
```

### Vežba 3 — Tekstualne vrednosti

```sql
SELECT CustomerId, FirstName, LastName, Country
FROM customers
WHERE Country IN ('Brazil', 'Canada')
ORDER BY Country, LastName, CustomerId;
```

U ovoj bazi upit vraća 13 kupaca. Tekstualne vrednosti pišu se u jednostrukim navodnicima. Velika i mala slova i kolacija mogu uticati na tekstualno poređenje.

### Vežba 4 — Podupit nad `invoice_items`

```sql
SELECT TrackId, Name
FROM tracks
WHERE TrackId IN (
    SELECT TrackId
    FROM invoice_items
    WHERE InvoiceId = 1
)
ORDER BY TrackId;
```

Podupit vraća identifikatore numera sa računa 1; spoljni upit bira odgovarajuće nazive. Rezultat u kursnoj bazi:

| TrackId | Name              |
| ------: | ----------------- |
|       2 | Balls to the Wall |
|       4 | Restless and Wild |

Podupit je jedan `SELECT` unutar spoljnog upita. Za običan skalarni `IN` izraz treba da vraća jednu kolonu, ali može vratiti nula, jedan ili više redova. Duplikati u rezultatu podupita ne umnožavaju spoljne redove jer `IN` proverava pripadnost, a ne pravi parove redova kao što to može `JOIN`.

### Vežba 5 — `NOT IN` i `NULL`

```sql
SELECT COUNT(*) AS drugi_tipovi
FROM tracks
WHERE MediaTypeId NOT IN (1, 2);
```

Rezultat je `232`. Lista ne sadrži `NULL`, pa je uslov jednostavno „nije 1 i nije 2“.

Sada dodaj `NULL` u listu:

```sql
SELECT COUNT(*) AS sa_null_u_listi
FROM tracks
WHERE MediaTypeId NOT IN (1, 2, NULL);
```

Rezultat je `0`. Za vrednost koja se ne poklapa ni sa `1` ni sa `2`, SQLite ne može da odredi da li je jednaka nepoznatoj vrednosti `NULL`. Zato je rezultat `UNKNOWN`, a `WHERE` ne zadržava taj red.

```sql
SELECT
    2 IN (1, 2, NULL) AS postoji_poklapanje,
    3 IN (1, 2, NULL) AS nema_poklapanja,
    3 NOT IN (1, 2, NULL) AS negirani_uslov;
```

Rezultat je `1, NULL, NULL`. `NOT NULL` ostaje `NULL`; negacija ne pretvara nepoznatu vrednost u tačnu.

Kada podupit može vratiti `NULL`, obično je jasnije isključiti te vrednosti u podupitu ili koristiti `NOT EXISTS`:

```sql
SELECT c.CustomerId, c.FirstName, c.LastName
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM invoices AS i
    WHERE i.CustomerId = c.CustomerId
)
ORDER BY c.CustomerId;
```

Ovaj konkretan Chinook upit ne vraća kupce jer svi imaju račun. Njegova svrha je da pokaže oblik provere „ne postoji povezani red“ bez zamke da `NULL` iz rezultata podupita obori `NOT IN`.

### Vežba 6 — `NULL` na levoj strani i prazna lista

```sql
SELECT
    NULL IN (1, 2) AS null_in_listi,
    NULL NOT IN (1, 2) AS null_not_in_listi;
```

Oba izraza vraćaju `NULL`. Ako želiš uključiti i prazne vrednosti u filter, napiši to eksplicitno, na primer:

```sql
WHERE MediaTypeId IN (1, 2)
   OR MediaTypeId IS NULL
```

SQLite dozvoljava praznu listu i vraća:

```sql
SELECT
    5 IN () AS prazno_in,
    5 NOT IN () AS prazno_not_in,
    NULL IN () AS null_prazno_in,
    NULL NOT IN () AS null_prazno_not_in;
```

Rezultati su `0, 1, 0, 1`. Ovo je SQLite specifičnost: ne pretpostavljaj da `IN ()` sintaksa radi u svakoj bazi. U aplikaciji definiši ponašanje za prazan spisak pre nego što napraviš upit.

### `IN` u `CHECK` ograničenju

`IN` nije ograničen samo na filtriranje. U `CHECK` ograničenju može ograničiti dozvoljene vrednosti:

```sql
status TEXT NOT NULL
    CHECK (status IN ('open', 'in_progress', 'done'))
```

`NOT NULL` je bitan ako je status obavezan. Sam `CHECK` može dozvoliti `NULL`, zato što `NULL` nije rezultat `FALSE`. U `WHERE` uslovu `IN` bira postojeće redove; u `CHECK` pravilu proverava novu ili izmenjenu vrednost. Pogledaj i [lekciju o SQLite ograničenjima](../03_creating_database_tables_updating_data_deleting_records/01_sqlite_constraints.md).

### SQLAlchemy 2.0

```python
from sqlalchemy import select

media_type_ids = [1, 2]

statement = (
    select(Track.track_id, Track.name, Track.media_type_id)
    .where(Track.media_type_id.in_(media_type_ids))
    .order_by(Track.name, Track.track_id)
)
```

`.in_()` prima listu vrednosti ili `select()` izraz. Vrednosti se vezuju kao parametri. Ako lista dolazi iz FastAPI zahteva, validiraj elemente i definiši ponašanje za praznu listu. Vezivanje parametara sprečava da vrednosti menjaju SQL strukturu, ali ne definiše samo po sebi šta prazan filter treba da znači.

---

## Lekcija 03 — `LIKE`

Teorija: [03_sqlite_LIKE_operator.md](../04_some_sqlite_operators/03_sqlite_LIKE_operator.md)
Radni fajl: [03_sqlite_LIKE_operator.sql](../playground/sql/04_some_sqlite_operators/03_sqlite_LIKE_operator.sql)

### Džokeri `%` i `_`

| Znak | Značenje              |
| ---- | --------------------- |
| `%`  | Nula ili više znakova |
| `_`  | Tačno jedan znak      |

Položaj `%` menja kriterijum:

| Obrazac    | Značenje                                                                |
| ---------- | ----------------------------------------------------------------------- |
| `'Wild%'`  | Počinje sa `Wild`                                                       |
| `'%Love'`  | Završava se sa `Love`                                                   |
| `'%Love%'` | Sadrži `Love` bilo gde                                                  |
| `'_r%'`    | Drugi znak je `r`                                                       |
| `'A_%'`    | Počinje sa `A` i ima najmanje još jedan znak                            |
| `'A%o'`    | Počinje sa `A` i završava se sa `o`                                     |
| `'A%o%'`   | Počinje sa `A` i posle nje sadrži `o`; može imati još znakova posle `o` |

`%` može odgovarati praznom nizu; `_` uvek zahteva jedan znak.

### Vežba 1 — Nazivi koji počinju sa `Wild`

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE 'Wild%'
ORDER BY Name, TrackId;
```

Rezultat u ovoj bazi ima pet numera:

| TrackId | Name             |
| ------: | ---------------- |
|    2633 | Wild Flower      |
|    2627 | Wild Hearted Son |
|    2944 | Wild Honey       |
|    1973 | Wild Side        |
|    1245 | Wildest Dreams   |

### Vežba 2 — Početak, kraj i sadržaj

```sql
-- Počinje sa Love
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE 'Love%'
ORDER BY Name, TrackId
LIMIT 10;
```

```sql
-- Završava se sa Love
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE '%Love'
ORDER BY Name, TrackId
LIMIT 10;
```

```sql
-- Sadrži Love bilo gde
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE '%Love%'
ORDER BY Name, TrackId
LIMIT 10;
```

U kursnoj kopiji uslovi odgovaraju redom 27, 54 i 114 numerama. Svaki upit prikazuje najviše deset redova. `LIMIT` ne određuje broj ukupnih pogodaka; za to bi koristio `COUNT(*)`.

### Vežba 3 — Znak na određenom mestu

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE '_r%'
ORDER BY Name, TrackId
LIMIT 10;
```

`_r%` traži tekst čiji je drugi znak `r`. U ovoj bazi 207 naziva odgovara uslovu.

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE 'A_%'
ORDER BY Name, TrackId
LIMIT 10;
```

`A_%` traži početno `A` i bar još jedan znak. Odgovara 199 nazivima.

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE 'A%o'
ORDER BY Name, TrackId
LIMIT 10;
```

`A%o` traži naziv koji počinje sa `A` i završava se slovom `o` ili `O`, jer SQLite-ov ugrađeni `LIKE` zanemaruje ASCII razliku velikih i malih slova. Odgovara 18 nazivima u ovoj bazi. Nemoj dodati završni `%` ako je završno slovo uslov: `A%o%` dopušta dodatni tekst posle `o`.

### Vežba 4 — Doslovni `%`, `_` i znak za escape

```sql
SELECT
    '100% organic' LIKE '100!% organic' ESCAPE '!' AS literal_percent,
    'a_b' LIKE 'a!_b' ESCAPE '!' AS literal_underscore,
    'wow!' LIKE 'wow!!' ESCAPE '!' AS literal_escape_character;
```

Rezultat je `1, 1, 1`. Uz `ESCAPE '!'`, `!%` znači doslovni `%`, `!_` doslovni `_`, a `!!` doslovni `!`. Sam escape izraz treba predstavljati jedan znak.

### Vežba 5 — ASCII i Unicode

```sql
SELECT
    'a' LIKE 'A' AS ascii_match,
    'æ' LIKE 'Æ' AS unicode_case_match;
```

U ugrađenom SQLite `LIKE` ponašanju rezultat je `1, 0`. Podrazumevana neosetljivost važi za ASCII slova, ne za pun Unicode case-folding ili lokalizovano poređenje srpskog teksta. Zastareli `PRAGMA case_sensitive_like` nije preporučeno rešenje.

### Vežba 6 — Vrednosti iz korisničkog unosa

SQLAlchemy izraz sa vezanim parametrom može izgledati ovako:

```python
from sqlalchemy import select

term = "Wild"
pattern = f"%{term}%"

statement = (
    select(Track.track_id, Track.name)
    .where(Track.name.like(pattern))
)
```

Parametar štiti strukturu SQL-a, ali `%` i `_` unutar `term` i dalje imaju značenje džokera. Ako korisnik očekuje doslovnu pretragu tih znakova, aplikacija mora escapovati obrazac i proslediti `escape="!"` u `.like()`. SQL injection zaštita i obrazac za doslovno pretraživanje rešavaju dva različita problema.

### Dodatna provera `NULL` i `GLOB`

```sql
SELECT
    NULL LIKE 'A%' AS null_like,
    NULL NOT LIKE 'A%' AS null_not_like;
```

Oba rezultata su `NULL`; ni `LIKE` ni `NOT LIKE` ne pronađu red sa nedostajućom vrednošću. Koristi `IS NULL`.

U `LIKE`, `%` i `_` su džokeri. U `GLOB` džokeri su `*` i `?`. Ne mešaj ih.

---

## Lekcija 04 — `GLOB`

Teorija: [04_sqlite_GLOB_operator.md](../04_some_sqlite_operators/04_sqlite_GLOB_operator.md)
Radni fajl: [04_sqlite_GLOB_operator.sql](../playground/sql/04_some_sqlite_operators/04_sqlite_GLOB_operator.sql)

### Džokeri u `GLOB`

| Znak     | Značenje                               |
| -------- | -------------------------------------- |
| `*`      | Nula ili više znakova                  |
| `?`      | Tačno jedan znak                       |
| `[abc]`  | Jedan znak iz navedenog skupa          |
| `[a-z]`  | Jedan znak iz opsega                   |
| `[^abc]` | Jedan znak koji nije u navedenom skupu |

SQLite `GLOB` je podrazumevano case-sensitive. Operator poredi tekst u bazi; ne pretražuje fajl sistem.

### Vežba 1 — Nazivi koji počinju sa `Man`

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name GLOB 'Man*'
ORDER BY Name, TrackId;
```

U Chinook kopiji 11 naziva počinje velikim `Man`. Prvih pet:

| TrackId | Name                                    |
| ------: | --------------------------------------- |
|      52 | Man In The Box                          |
|    1397 | Man On The Edge                         |
|     106 | Man Or Animal                           |
|     358 | Man With The Woman Head                 |
|    2859 | Man of Science, Man of Faith (Premiere) |

`Man*` zahteva velika slova `M`, `a`, `n` na početku; `*` zatim dozvoljava bilo kakav nastavak.

### Vežba 2 — Nazivi koji se završavaju sa `Man`

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name GLOB '*Man'
ORDER BY Name, TrackId
LIMIT 10;
```

Ovaj uslov odgovara 28 naziva. `*` pre `Man` dozvoljava bilo kakav početni deo, a završni `Man` mora da se poklopi velikim `M`. Zbog case-sensitivity-ja, `'*man'` nije isti obrazac.

`'*Man*'` traži `Man` bilo gde u tekstu i odgovara 62 naziva u ovoj kopiji.

### Vežba 3 — `?` odgovara jednom znaku

```sql
SELECT
    'track1' GLOB 'track?' AS jedan_znak,
    'track10' GLOB 'track?' AS previse_znakova;
```

Rezultat je `1, 0`. `?` odgovara jednom znaku; drugi primer ima dva znaka posle `track`.

### Vežba 4 — Skupovi, opsezi i negacija

```sql
SELECT
    'aable' GLOB '[at]able' AS poklapanje_a,
    'table' GLOB '[at]able' AS poklapanje_t;
```

Rezultat je `1, 1`: `[at]` odgovara jednom znaku `a` ili `t`.

```sql
SELECT
    'apple' GLOB '[a-z]*' AS malo_slovo,
    'Apple' GLOB '[a-z]*' AS veliko_slovo,
    'Apple' GLOB '[^a-z]*' AS nije_malo_slovo;
```

Rezultat je `1, 0, 1`. `[a-z]` je opseg malih ASCII slova; `[^a-z]` traži prvi znak koji nije u tom opsegu. Ovo nije lokalizovano pravilo za sva Unicode slova.

### Vežba 5 — Uporedi `LIKE` i `GLOB`

```sql
SELECT
    'track1' LIKE 'track_' AS like_podvlaka,
    'track1' GLOB 'track?' AS glob_upitnik,
    'track1' GLOB 'track_' AS glob_podvlaka_doslovno;
```

Rezultat je `1, 1, 0`:

- `_` je džoker jednog znaka u `LIKE`;
- `?` je džoker jednog znaka u `GLOB`;
- `_` u `GLOB` je doslovna podvlaka, pa se tekst `track1` ne poklapa sa `track_`.

Doslovni `*` i `?` možeš tražiti preko skupa jednog znaka:

```sql
SELECT '*' GLOB '[*]', '?' GLOB '[?]';
```

Oba rezultata su `1`. `GLOB` nema `LIKE`-ovu `ESCAPE` klauzulu.

### Vežba 6 — Sistemska šema

```sql
SELECT name, type
FROM sqlite_schema
WHERE name GLOB 'sqlite_*'
ORDER BY name;
```

Obrazac bira nazive objekata koji počinju doslovnim `sqlite_`, zatim bilo kojim nastavkom. `_` je doslovan znak u `GLOB`, dok `*` predstavlja džoker. Primer može vratiti objekte kao što su `sqlite_sequence`, `sqlite_stat1` i automatski napravljeni indeksi — njihov tačan skup zavisi od baze.

### Ivični slučaj: `NULL`

```sql
SELECT
    NULL GLOB '*' AS null_glob,
    NULL NOT GLOB 'Man*' AS null_not_glob;
```

Oba izraza vraćaju `NULL` (`UNKNOWN`), a ne `TRUE`. `NOT GLOB` ne pronalazi redove sa `NULL`.

### SQLAlchemy 2.0

`GLOB` je SQLite specifičan operator. U SQLAlchemy-ju ga možeš izraziti pomoću boolean operatora:

```python
from sqlalchemy import select

pattern = "Man*"

statement = (
    select(Track.track_id, Track.name)
    .where(Track.name.bool_op("GLOB")(pattern))
    .order_by(Track.name, Track.track_id)
)
```

Vezani parametar čuva SQL strukturu, ali ne neutralizuje glob džokere. Ako pattern dolazi od korisnika, definiši da li korisnik sme da šalje `*`, `?` i skupove znakova. `GLOB` nije prenosiv na sve DBMS sisteme.

---

## Lekcija 05 — `LIMIT` i `OFFSET`

Teorija: [05_sqlite_LIMIT_clause.md](../04_some_sqlite_operators/05_sqlite_LIMIT_clause.md)
Radni fajl: [05_sqlite_LIMIT_clause.sql](../playground/sql/04_some_sqlite_operators/05_sqlite_LIMIT_clause.sql)

### Vežba 1 — Pet prvih numera

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 5;
```

Tabela `tracks` ima 3.503 reda; ovaj upit vraća pet redova:

| TrackId | Name                                    |
| ------: | --------------------------------------- |
|       1 | For Those About To Rock (We Salute You) |
|       2 | Balls to the Wall                       |
|       3 | Fast As a Shark                         |
|       4 | Restless and Wild                       |
|       5 | Princess of the Dawn                    |

`LIMIT` ograničava broj vraćenih redova, ne broj kolona niti ukupan broj redova u tabeli.

Bez `ORDER BY`, upit bi i dalje vratio najviše pet redova, ali ne bi garantovao da su to isti redovi pri svakom izvršavanju. `ORDER BY TrackId` određuje šta znači „prvih pet“.

### Vežba 2 — Druga stranica

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 5 OFFSET 5;
```

`OFFSET 5` preskače prvih pet sortiranih redova, a `LIMIT 5` vraća narednih pet:

| TrackId | Name                  |
| ------: | --------------------- |
|       6 | Put The Finger On You |
|       7 | Let's Get It Up       |
|       8 | Inject The Venom      |
|       9 | Snowballed            |
|      10 | Evil Walks            |

Ako je broj stranice 1-based, veličina stranice `s`, a trenutna stranica `p`, obračun je:

```text
OFFSET = (p - 1) * s
LIMIT = s
```

Treća stranica sa po pet redova ima `OFFSET 10`.

### Vežba 3 — Preskoči 12, vrati narednih 12

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 12 OFFSET 12;
```

Prvi vraćeni identifikator je `13`, a poslednji `24`. `OFFSET` broji preskočene redove od nule. Zato `OFFSET 12` znači „preskoči 12 redova“, a ne „počni od 12. reda“.

### Vežba 4 — Deset najdužih numera

```sql
SELECT TrackId, Name, Milliseconds
FROM tracks
ORDER BY Milliseconds DESC, TrackId ASC
LIMIT 10;
```

`Milliseconds DESC` stavlja najduže numere prve. `TrackId ASC` daje stabilan redosled ako više numera ima isto trajanje. Ako bi sortirao samo po `Milliseconds`, relativni redosled izjednačenih numera ne bi bio garantovan.

### Vežba 5 — Granične vrednosti

`LIMIT 0` vraća nula redova:

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 0;
```

Negativan `LIMIT` u SQLite-u uklanja gornju granicu broja redova:

```sql
SELECT COUNT(*) AS broj_sa_negativnim_limitom
FROM (
    SELECT TrackId
    FROM tracks
    LIMIT -1
);
```

Rezultat je 3.503. Negativna veličina stranice u aplikaciji zato ne treba da se prosledi kao da je obična vrednost.

Negativan `OFFSET` SQLite tretira kao nulu:

```sql
SELECT TrackId
FROM tracks
ORDER BY TrackId
LIMIT 3 OFFSET -5;
```

Rezultat su `TrackId` 1, 2 i 3. Ipak, validiraj `offset >= 0` u aplikaciji umesto da se oslanjaš na ovo SQLite specifično ponašanje.

Ako je pomeraj izvan dostupnog rezultata:

```sql
SELECT COUNT(*) AS redovi_posle_velikog_offseta
FROM (
    SELECT TrackId
    FROM tracks
    ORDER BY TrackId
    LIMIT 5 OFFSET 4000
);
```

Rezultat je `0`, bez greške. `LIMIT 0`, negativni brojevi i prazna stranica imaju različito značenje; validiraj ulaz i definiši željeno ponašanje.

### Sintaksa sa zarezom

```sql
LIMIT 5 OFFSET 5
```

je ekvivalentno sledećem SQLite obliku:

```sql
LIMIT 5, 5
```

Kod sintakse sa zarezom redosled je `offset, broj_redova`, dok je kod ključnih reči redosled `broj_redova OFFSET offset`. U kursu koristi oblik sa `OFFSET` da izbegneš zamenu argumenata.

### Vežba 6 — `COUNT(*)` nije isto što i `LIMIT`

```sql
SELECT COUNT(*) AS numera_na_albumu_1
FROM tracks
WHERE AlbumId = 1;
```

Rezultat je `10`. Ovo računa sve numere koje ispunjavaju uslov.

```sql
SELECT TrackId, Name
FROM tracks
WHERE AlbumId = 1
ORDER BY TrackId
LIMIT 4;
```

Drugi upit prikazuje samo prve četiri: `TrackId` su 1, 6, 7 i 8. `LIMIT` ne računa ukupan broj pogodaka; za ukupan broj koristi `COUNT(*)`.

### Offset i keyset straničenje

`LIMIT/OFFSET` je jednostavan za prve stranice, ali veliki `OFFSET` može zahtevati da baza pređe i preskoči mnogo prethodnih redova. Ako se podaci menjaju između zahteva, pomeranje redova može dovesti do ponavljanja ili preskakanja rezultata.

Keyset straničenje nastavlja posle poslednje viđene jedinstvene vrednosti:

```sql
SELECT TrackId, Name
FROM tracks
WHERE TrackId > 10
ORDER BY TrackId
LIMIT 5;
```

Ovaj primer nastavlja posle `TrackId` 10. U API-ju aplikacija prosleđuje poslednji prikazani identifikator sledećem zahtevu. Izbor pristupa zavisi od veličine skupa, sortiranja i zahteva aplikacije.

### SQLAlchemy 2.0 i FastAPI

```python
from sqlalchemy import select

page_size = 20
offset = 0

statement = (
    select(Track.track_id, Track.name)
    .order_by(Track.track_id)
    .limit(page_size)
    .offset(offset)
)
```

U FastAPI-ju ograniči ulaz, na primer `page_size` na najmanje 1 i razuman maksimum, a `offset` na najmanje 0. SQLAlchemy vezuje vrednosti, ali aplikacija je i dalje odgovorna za ograničavanje zahteva i predvidiv `ORDER BY`.

---

## 3. Kratka provera razumevanja

1. **Da li `BETWEEN 5 AND 10` uključuje 5 i 10?** Da; obe granice su uključene.
2. **Šta radi `NOT BETWEEN`?** Bira vrednosti manje od donje ili veće od gornje granice; `NULL` i dalje daje `UNKNOWN`.
3. **Koja je osnovna razlika između `IN` i `BETWEEN`?** `IN` proverava članstvo u listi ili podupitu; `BETWEEN` proverava opseg.
4. **Zašto je `NOT IN` opasan ako podupit vraća `NULL`?** Poređenje nepoznate vrednosti može učiniti uslov `UNKNOWN`, pa redovi budu izostavljeni; proveri `NOT EXISTS` ili isključi `NULL` u podupitu.
5. **Koliko znakova poklapaju `%` i `_` u `LIKE`?** `%` nula ili više; `_` tačno jedan.
6. **Koji su odgovarajući džokeri u `GLOB`?** `*` je nula ili više znakova, `?` je jedan; `[]` definiše skup ili opseg jednog znaka.
7. **Da li je `GLOB` isto što i pronalaženje fajlova?** Ne. SQLite operator poredi tekstualne vrednosti u bazi.
8. **Da li SQLite `LIKE` podrazumevano radi Unicode case-folding?** Ne; podrazumevana neosetljivost odnosi se na ASCII slova.
9. **Šta znači `OFFSET 12`?** Preskoči 12 redova, pa prvi vraćeni red je 13. u sortiranom nizu.
10. **Da li `LIMIT 5` određuje koji su to pet redova?** Ne bez `ORDER BY`; ograničava samo broj redova, a redosled nije garantovan.
11. **Kako se obezbeđuje stabilan rezultat stranice?** Koristi `ORDER BY` sa jedinstvenim završnim kriterijumom, obično primarnim ključem.
12. **Šta SQLite radi sa negativnim `LIMIT` i `OFFSET` vrednostima?** Negativan `LIMIT` nema gornju granicu, a negativan `OFFSET` se tretira kao nula; u aplikaciji ih validiraj.
13. **Da li `LIMIT` zamenjuje `COUNT(*)`?** Ne. `LIMIT` prikazuje deo redova, `COUNT(*)` broji sve redove koji ispunjavaju uslov.
14. **Zašto proveriti operator na ciljnoj bazi?** `GLOB`, prazni `IN ()`, case-sensitivity, tipovi i paginacija mogu imati drugačiju podršku ili semantiku u PostgreSQL-u i MySQL-u.

## 4. Šta je prioritet prema planu učenja?

Ovu oblast koristi da učvrstiš prenosive SQL veštine:

- Jasno razlikuj filtriranje (`WHERE`), sortiranje (`ORDER BY`) i ograničavanje (`LIMIT`).
- Razumi šta znači inkluzivna granica, skup vrednosti, tekstualni obrazac i nepoznat `NULL` rezultat.
- Nauči da predvidiv rezultat zahteva sortiranje; uz sortiranje dodaj jedinstveni tie-breaker, posebno za stranečenje.
- Veži vrednosti kroz SQLAlchemy izraze umesto konkatenacije korisničkog unosa. Za `LIKE` i `GLOB` dodatno odluči da li džokeri treba da budu aktivni ili doslovni.
- Prepoznaj SQLite specifičnosti — `GLOB`, `IN ()`, ASCII ponašanje `LIKE` i negativni `LIMIT` — ali ne moraš pamtiti unutrašnju implementaciju SQLite-a.
- Kada budeš radio sa PostgreSQL-om ili MySQL-om, ponovo proveri sintaksu, kolacije, case-sensitivity, Unicode ponašanje, paginaciju i plan upita. SQLAlchemy ne uklanja sve razlike između baza.

Najvažnije je da umeš da napišeš uslov, predvidiš kako će se ponašati za granice i `NULL`, i proveriš koji redovi stvarno odgovaraju pre nego što upit ugradiš u aplikaciju.

### Predlog rasporeda rada

Ovo je samo predlog, ne obavezan rok:

1. `BETWEEN` i `IN`, uključujući granične vrednosti i `NULL`.
2. `LIKE` obrasci i escapovanje doslovnih džokera.
3. `GLOB` skupovi znakova i poređenje sa `LIKE`.
4. `LIMIT`, `OFFSET` i ponavljanje ključnih razlika.

Pređi na sledeći deo kada možeš da objasniš rezultat svakog uslova i zašto mu je potreban baš taj operator.
