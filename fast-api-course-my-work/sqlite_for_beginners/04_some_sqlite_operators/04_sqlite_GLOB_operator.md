# 04 — SQLite `GLOB` operator

## Cilj lekcije

U ovoj lekciji naučićeš kako SQLite operatorom `GLOB` porediš tekst sa šablonom. Upoznaćeš džokere `*` i `?`, skupove znakova u uglastim zagradama i razliku između `GLOB` i `LIKE`.

Prethodna lekcija: [`LIKE` operator](./03_sqlite_LIKE_operator.md).

`GLOB` se pojavio i u [ranijem odgovoru o SQLite šemi i sistemskim objektima](../pitanja_i_odgovori/dan_05_intro_and_cli_vezbe.md). Ova lekcija proširuje taj primer i objašnjava pravila operatora za obične tekstualne kolone.

## Čemu služi `GLOB`

`GLOB` proverava da li tekst odgovara obrascu:

```sql
SELECT kolone
FROM tabela
WHERE tekstualna_kolona GLOB 'obrazac';
```

U SQLite-u se koristi za poređenje tekstualnih vrednosti sa obrascem. Iako naziv i džoker `*` podsećaju na obrasce za pronalaženje fajlova, `GLOB` u SQL upitu sam po sebi ne pretražuje fajl sistem — poredi vrednosti iz baze.

`GLOB` je specifičan za SQLite i podrazumevano razlikuje velika i mala slova. Ovo je drugačije od ugrađenog SQLite `LIKE`, koji podrazumevano zanemaruje ASCII razliku velikih i malih slova.

## Džokeri u `GLOB`

| Znak u obrascu | Značenje                                     | Primer                                                          |
| -------------- | -------------------------------------------- | --------------------------------------------------------------- |
| `*`            | Nula ili više znakova                        | `'Man*'` odgovara `'Man'`, `'Man In The Box'` i `'Mango'`       |
| `?`            | Tačno jedan znak                             | `'track?'` odgovara `'track1'`, ali ne `'track'` ni `'track10'` |
| `[abc]`        | Tačno jedan znak iz navedenog skupa          | `'[at]able'` odgovara `'aable'` ili `'table'`                   |
| `[a-z]`        | Tačno jedan znak iz navedenog opsega         | `'[a-z]*'` odgovara tekstu koji počinje malim ASCII slovom      |
| `[^abc]`       | Tačno jedan znak koji nije u navedenom skupu | `'[^a-z]*'` odgovara tekstu koji ne počinje malim ASCII slovom  |

`*` i `?` mogu se kombinovati sa skupovima znakova u jednom obrascu:

```sql
SELECT Name
FROM tracks
WHERE Name GLOB '[Mm]an*'
ORDER BY Name, TrackId;
```

`[Mm]` dozvoljava veliko `M` ili malo `m` na prvom mestu, a `*` zatim odgovara bilo kom nastavku. Pošto je `GLOB` inače case-sensitive, skup znakova je jedan način da eksplicitno dozvoliš obe varijante ASCII slova.

Opsezi poput `[a-z]` korisni su za jednostavne ASCII obrasce, ali nisu lokalizovano sortiranje niti pravilo za sva mala slova u Unicode-u. Nemoj pretpostaviti da `[a-z]` obuhvata sva slova srpske latinice.

## Primer iz transkripta: nazivi koji počinju sa `Man`

U transkriptu se operator primenjuje na `tracks.Name`:

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name GLOB 'Man*'
ORDER BY Name, TrackId;
```

`Man*` traži tekst koji počinje velikim slovom `M`, zatim `a` i `n`, posle čega može slediti bilo koji niz znakova. U kursnoj Chinook bazi uslov odgovara 11 redova. Prvih pet po sortiranom redosledu su:

| TrackId | Name                                    |
| ------: | --------------------------------------- |
|      52 | Man In The Box                          |
|    1397 | Man On The Edge                         |
|     106 | Man Or Animal                           |
|     358 | Man With The Woman Head                 |
|    2859 | Man of Science, Man of Faith (Premiere) |

Broj u bazi može se proveriti odvojeno:

```sql
SELECT COUNT(*) AS broj_numera
FROM tracks
WHERE Name GLOB 'Man*';
```

Rezultat je `11`. Ako alat prikaže samo deo rezultata, proveri da li je upit ograničen pomoću `LIMIT` ili da li je rezultatni prikaz skrolovan.

## Položaj `*` menja kriterijum

Kao i kod `LIKE`, položaj džokera menja značenje obrasca:

```sql
-- Nazivi koji počinju sa Man
WHERE Name GLOB 'Man*'
```

```sql
-- Nazivi koji se završavaju sa Man
WHERE Name GLOB '*Man'
```

```sql
-- Nazivi koji sadrže Man bilo gde
WHERE Name GLOB '*Man*'
```

U kursnoj bazi `Name GLOB '*Man'` vraća 28 redova. Pošto je `GLOB` osetljiv na velika i mala slova, `'Man*'` i `'man*'` nisu isti obrazac. Takođe, `'*Man'` traži veliko `M` u završnoj reči `Man`; obrazac `'*man'` ne bi odgovarao tim istim vrednostima.

## Skupovi i opsezi znakova

Uglaste zagrade `[]` predstavljaju jedan znak iz skupa:

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name GLOB '[Mm]an*'
ORDER BY Name, TrackId;
```

Prvi znak mora biti `M` ili `m`; ostali znakovi se porede doslovno sve do `*`.

Možeš navesti više pojedinačnih znakova:

```sql
SELECT 'aable' GLOB '[at]able' AS matches_a,
       'table' GLOB '[at]able' AS matches_t;
```

Oba izraza vraćaju `1`, jer `[at]` odgovara jednom znaku — `a` ili `t`.

Možeš navesti i opseg:

```sql
SELECT 'apple' GLOB '[a-z]*' AS lowercase_start,
       'Apple' GLOB '[a-z]*' AS uppercase_start;
```

U SQLite-u se uobičajeno dobija `1` za `apple` i `0` za `Apple`. Opseg je case-sensitive.

Da bi dozvolio jedan znak koji nije u skupu, započni skup znakom `^`:

```sql
SELECT 'Apple' GLOB '[^a-z]*' AS starts_not_with_lowercase_ascii;
```

Ovaj izraz vraća `1`, jer je prvi znak veliko `A`, a ne malo ASCII slovo od `a` do `z`. `^` ima ovo značenje unutar uglastih zagrada; izvan njih je običan znak.

## Razlika između `GLOB` i `LIKE`

| Osobina                                                        | `GLOB`                                | `LIKE`                                                  |
| -------------------------------------------------------------- | ------------------------------------- | ------------------------------------------------------- |
| Bilo koji niz znakova                                          | `*`                                   | `%`                                                     |
| Jedan znak                                                     | `?`                                   | `_`                                                     |
| Skup ili opseg jednog znaka                                    | `[abc]`, `[a-z]`, `[^abc]`            | Nema isti oblik skupova znakova                         |
| Podrazumevano poređenje velikih i malih ASCII slova u SQLite-u | Osetljivo                             | Neosetljivo                                             |
| Doslovno traženje džokera                                      | Može preko skupa znakova za `*` i `?` | Koristi `ESCAPE`                                        |
| Prenosivost                                                    | SQLite specifičan                     | Široko podržan, ali ponašanje zavisi od baze i kolacije |

Ne mešaj znakove iz ova dva operatora:

- U `GLOB` je `*` džoker, a `%` običan znak.
- U `LIKE` je `%` džoker, a `*` običan znak.
- U `GLOB` je `?` džoker, a `_` običan znak.
- U `LIKE` je `_` džoker, a `?` običan znak.

Na primer:

```sql
SELECT 'a%b' GLOB 'a%b' AS percent_is_literal,
       'a%b' GLOB 'a*b' AS asterisk_matches_sequence;
```

Oba izraza vraćaju `1`: prvi obrazac sadrži doslovni `%`, a drugi koristi `*` da odgovara nizu znakova.

## Doslovni znakovi i `ESCAPE`

`GLOB` nema `ESCAPE` klauzulu kao `LIKE`. Doslovni `*` i `?` možeš navesti kao skup od jednog znaka:

```sql
SELECT '*' GLOB '[*]' AS literal_asterisk,
       '?' GLOB '[?]' AS literal_question_mark;
```

Oba izraza vraćaju `1`. Zagrade u `[*]` i `[?]` znače da se traži doslovni znak iz skupa, a ne džoker.

Obrazac kao `sqlite_*` koristi `_` doslovno, jer podvlaka nije džoker u `GLOB`-u. To se razlikuje od `LIKE`, gde bi `_` odgovarao bilo kom jednom znaku. Zato ovaj raniji primer nad sistemskim imenima traži doslovni prefiks `sqlite_`, pa bilo koji nastavak:

```sql
SELECT name, type
FROM sqlite_schema
WHERE name GLOB 'sqlite_*'
ORDER BY name;
```

## `NULL` i `NOT GLOB`

Ako je tekstualna vrednost `NULL`, provera obrasca vraća `NULL`, ne `TRUE` ili `FALSE`. `WHERE` zato ne uključuje takav red:

```sql
SELECT TrackId, Name, Composer
FROM tracks
WHERE Composer GLOB 'A*';
```

Ovaj upit ne vraća numere sa `Composer IS NULL`. Isto važi za negirani uslov:

```sql
WHERE Composer NOT GLOB 'A*'
```

`NOT GLOB` ne pretvara `NULL` u podudaranje; za nedostajuće vrednosti koristi `IS NULL`.

## `GLOB` je SQLite specifičan

`GLOB` nije deo standardnog SQL-a i ne podržavaju ga sve baze podataka. Ako koristiš SQLite operator u aplikaciji koja će se kasnije prebaciti na PostgreSQL ili MySQL, proveri ciljnu bazu i po potrebi prevedi obrazac na njenu sintaksu. `LIKE` je šire podržan, ali i njegovo ponašanje vezano za velika i mala slova i kolacije treba proveriti na ciljnom sistemu.

## Veza sa SQLAlchemy 2.0 i FastAPI-jem

SQLAlchemy nema prenosivu posebnu metodu `.glob()` za sve dijalekte. Ako aplikacija koristi SQLite i zaista joj treba `GLOB`, možeš izraziti operator pomoću `.bool_op("GLOB")`, koji označava da izraz vraća logički rezultat:

```python
from sqlalchemy import select

pattern = "Man*"

statement = (
    select(Track.track_id, Track.name)
    .where(Track.name.bool_op("GLOB")(pattern))
    .order_by(Track.name, Track.track_id)
)
```

Primer pretpostavlja da model `Track` ima navedene atribute. SQLAlchemy prosleđuje `pattern` kao vezani parametar. To štiti strukturu SQL-a, ali ne menja značenje džokera: `*`, `?` i `[]` ostaju aktivni u obrascu. Ako obrazac dolazi od korisnika, definiši da li korisnik sme da koristi GLOB sintaksu i ograniči dozvoljene obrasce prema nameni aplikacije.

Pošto je `GLOB` SQLite specifičan, drži ga iza sloja koji može da se prilagodi ako aplikacija kasnije koristi drugu bazu.

## Indeksi i performanse

Obrazac koji počinje običnim prefiksom, kao `Name GLOB 'Man*'`, ponekad može da koristi indeks, u zavisnosti od šeme i plana upita. Obrazac koji počinje sa `*`, kao `Name GLOB '*Man'`, ne predstavlja običnu pretragu prefiksa i često zahteva pregled većeg broja vrednosti. Za velike tabele proveri `EXPLAIN QUERY PLAN` i stvarne podatke; nemoj zaključivati o performansama samo na osnovu operatora.

## Česte greške

- **Mešaš `GLOB` sa pretragom fajlova:** SQLite `GLOB` poredi vrednosti u upitu; sam ne pretražuje direktorijume.
- **Koristiš džokere iz `LIKE`:** u `GLOB` su `*` i `?` džokeri, a `%` i `_` su obični znakovi.
- **Zaboraviš da je `GLOB` case-sensitive:** `'Man*'` i `'man*'` nisu isti obrazac.
- **Misliš da `_` znači jedan znak u `GLOB`-u:** `_` je doslovna podvlaka; `?` odgovara jednom znaku.
- **Koristiš `ESCAPE` sa `GLOB`:** SQLite `GLOB` ne koristi `LIKE`-ovu `ESCAPE` klauzulu; za doslovni `*` ili `?` koristi skup kao `[*]` ili `[?]`.
- **Tretiraš `[a-z]` kao lokalizovanu abecedu:** to je opseg znakova, ne jezički ispravno poređenje svih Unicode slova.
- **Pretpostaviš da `NOT GLOB` uključuje `NULL`:** `NULL` ostaje nepoznat rezultat; koristi `IS NULL` kada tražiš nedostajuće vrednosti.
- **Zaboraviš prenosivost:** `GLOB` je SQLite specifičan i može zahtevati drugačije rešenje u drugoj bazi.

## Provera razumevanja

1. Koja je razlika između `*` i `?` u `GLOB` obrascu?
2. Šta traže obrasci `'Man*'`, `'*Man'` i `'*Man*'`?
3. Kako obrazac `[Mm]an*` razlikuje velika i mala slova?
4. Šta znače `[a-z]` i `[^a-z]`?
5. Zašto `sqlite_*` koristi `_` doslovno u `GLOB` obrascu?
6. Koji džokeri pripadaju `LIKE`, a koji `GLOB` operatoru?
7. Da li SQLite `GLOB` pretražuje fajl sistem?
8. Zašto je `GLOB` manje prenosiv od `LIKE`?
9. Šta se dešava ako se izraz levo od `GLOB` operatora procenjuje na `NULL`?
10. Kako SQLAlchemy 2.0 može da izrazi SQLite `GLOB` uslov?

## Vežbe

### Vežba 1 — Pronađi nazive koji počinju sa `Man`

1. Iz tabele `tracks` prikaži `TrackId` i `Name` za nazive koji počinju velikim slovom `Man`.
2. Sortiraj po nazivu, pa po identifikatoru.
3. Koliko redova odgovara obrascu? Uporedi sa brojem u lekciji.

### Vežba 2 — Pronađi nazive koji se završavaju sa `Man`

Promeni obrazac tako da pronađe nazive koji se završavaju velikim slovom `Man`. Dodaj `ORDER BY Name, TrackId` i uporedi nekoliko rezultata sa vežbom 1.

### Vežba 3 — Tačno jedan znak

Napiši upit koji koristi `?` da pronađe nazive sa tačno jednim znakom posle prefiksa `Track`. Objasni zašto `track10` ne odgovara obrascu `'track?'`.

### Vežba 4 — Skup i opseg

1. Pokreni `'aable' GLOB '[at]able'` i `'table' GLOB '[at]able'`.
2. Uporedi `'apple' GLOB '[a-z]*'` sa `'Apple' GLOB '[a-z]*'`.
3. Objasni ulogu uglastih zagrada i razliku u velikim i malim slovima.

### Vežba 5 — Uporedi `LIKE` i `GLOB`

Uporedi rezultate:

```sql
SELECT
    'track1' LIKE 'track_' AS like_match,
    'track1' GLOB 'track?' AS glob_match,
    'track1' GLOB 'track_' AS underscore_is_literal;
```

Objasni zašto prva dva izraza odgovaraju, a treći ne.

### Vežba 6 — SQLite šema

Pokreni upit nad `sqlite_schema` koji bira objekte čija imena počinju sa doslovnim `sqlite_`. Objasni zašto se u obrascu koristi `'sqlite_*'`, a ne `'sqlite%*'` niti `'sqlite?*'`.
