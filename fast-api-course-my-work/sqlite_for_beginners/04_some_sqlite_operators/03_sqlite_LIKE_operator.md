# 03 — SQLite `LIKE` operator

## Cilj lekcije

U ovoj lekciji naučićeš kako da filtriraš tekst pomoću obrazaca. Naučićeš šta znače džokeri `%` i `_`, kako da tražiš doslovni znak `%` ili `_`, i po čemu se `LIKE` razlikuje od `GLOB`.

Prethodna lekcija: [`IN` operator](./02_sqlite_IN_operator.md).

## Čemu služi `LIKE`

`LIKE` poredi tekst sa obrascem. Koristi se najčešće u `WHERE` uslovu kada ne znaš celu vrednost ili tražiš tekst koji počinje, završava se ili sadrži određeni niz znakova:

```sql
SELECT kolone
FROM tabela
WHERE tekstualna_kolona LIKE 'obrazac';
```

Obrazac je tekst u jednostrukim navodnicima. U njemu `%` i `_` imaju posebno značenje:

| Džoker | Značenje              | Primer                                                   |
| ------ | --------------------- | -------------------------------------------------------- |
| `%`    | Nula ili više znakova | `'A%'` odgovara `'A'`, `'Apple'` i `'A long title'`      |
| `_`    | Tačno jedan znak      | `'A_'` odgovara `'AB'` i `'A7'`, ali ne `'A'` ni `'ABC'` |

Ostali znakovi obrasca porede se doslovno, uz pravila poređenja `LIKE` opisana kasnije u lekciji.

`LIKE` je uslov, pa može da se koristi i u `WHERE` delu naredbe `UPDATE` ili `DELETE`, ne samo u upitu `SELECT`. Pre nego što izvršiš promenu ili brisanje, prvo proveri isti uslov u `SELECT` upitu i radi nad odgovarajućom probnom bazom.

## Položaj džokera menja značenje obrasca

| Obrazac    | Šta traži                                          |
| ---------- | -------------------------------------------------- |
| `'Wild%'`  | Tekst koji počinje sa `Wild`                       |
| `'%Love'`  | Tekst koji se završava sa `Love`                   |
| `'%Love%'` | Tekst koji sadrži `Love` bilo gde                  |
| `'_r%'`    | Tekst čiji je drugi znak `r`                       |
| `'A_%'`    | Tekst koji počinje sa `A` i ima bar još jedan znak |
| `'A%o'`    | Tekst koji počinje sa `A` i završava se sa `o`     |
| `'A%o%'`   | Tekst koji počinje sa `A` i kasnije sadrži `o`     |

Važno je razlikovati poslednja dva primera. U obrascu `'A%o'` znak `o` je na kraju; u obrascu `'A%o%'` završni `%` dopušta još znakova posle slova `o`, pa obrazac ne zahteva da se tekst završava slovom `o`.

`%` može odgovarati i praznom nizu, dok `_` zahteva jedan znak. Zato `'A%'` može odgovarati i samom tekstu `'A'`, ali `'A_%'` zahteva najmanje dva znaka.

## Primer iz transkripta: nazivi numera koji počinju sa `Wild`

U transkriptu se iz tabele `tracks` traže nazivi numera koji počinju sa `Wild`:

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE 'Wild%'
ORDER BY Name, TrackId;
```

U kursnoj Chinook bazi ovaj upit vraća pet numera:

| TrackId | Name             |
| ------: | ---------------- |
|    2633 | Wild Flower      |
|    2627 | Wild Hearted Son |
|    2944 | Wild Honey       |
|    1973 | Wild Side        |
|    1245 | Wildest Dreams   |

`ORDER BY Name, TrackId` daje predvidiv redosled. Bez `ORDER BY` baza ne garantuje željeni redosled rezultata.

## Uobičajeni obrasci pretrage

### Počinje određenim tekstom

```sql
SELECT CustomerId, FirstName, LastName
FROM customers
WHERE FirstName LIKE 'A%'
ORDER BY LastName, CustomerId;
```

`'A%'` traži imena koja počinju slovom `A`. Pošto `%` odgovara nula ili više znakova, obrazac može odgovarati i samom slovu `A`.

### Završava se određenim tekstom

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE '%Love'
ORDER BY Name, TrackId;
```

Početni `%` dozvoljava bilo koji niz znakova pre `Love`, uključujući i prazan niz.

### Sadrži određeni tekst

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE '%love%'
ORDER BY Name, TrackId
LIMIT 10;
```

`%` sa obe strane traži niz `love` bilo gde u nazivu. `LIMIT 10` ograničava broj prikazanih redova, a ne sam obrazac.

### Traži jedan znak na određenom mestu

```sql
SELECT TrackId, Name
FROM tracks
WHERE Name LIKE '_r%'
ORDER BY Name, TrackId
LIMIT 10;
```

`_` odgovara tačno jednom znaku, pa `'_r%'` traži nazive u kojima je `r` drugi znak.

## Traženje doslovnih `%` i `_` pomoću `ESCAPE`

Pošto su `%` i `_` džokeri u `LIKE` obrascu, za njihovo doslovno traženje koristi `ESCAPE`. Znak naveden posle `ESCAPE` označava da sledeći znak treba tretirati doslovno:

```sql
SELECT
    '100% organic' LIKE '100!% organic' ESCAPE '!' AS literal_percent,
    'a_b' LIKE 'a!_b' ESCAPE '!' AS literal_underscore;
```

Oba izraza vraćaju `1`. U obrascu `100!% organic`, `!%` znači doslovni znak `%`; u obrascu `a!_b`, `!_` znači doslovnu podvlaku.

Izraz posle `ESCAPE` mora predstavljati jedan znak. U ovom primeru je to `!`. Ako i sam znak `!` treba da bude doslovan u obrascu, udvostruči ga:

```sql
SELECT 'wow!' LIKE 'wow!!' ESCAPE '!' AS literal_escape_character;
```

Ovaj izraz takođe vraća `1`.

`ESCAPE` je važan i kada u aplikaciji korisnik unosi pojam za pretragu. Vezani parametar štiti strukturu SQL upita, ali `%` i `_` u njegovoj vrednosti i dalje imaju značenje džokera. Ako korisnik očekuje doslovnu pretragu, aplikacija mora escapovati te znakove i koristiti odgovarajući `ESCAPE` znak.

## Osetljivost na velika i mala slova u SQLite-u

Ugrađeni SQLite `LIKE` podrazumevano ne razlikuje velika i mala **ASCII** slova:

```sql
SELECT 'a' LIKE 'A' AS ascii_match;
```

Rezultat je `1`. Međutim, to ne znači da SQLite radi potpuno Unicode ili lokalizovano poređenje. Bez dodatnih proširenja, razlika velikih i malih ne-ASCII slova, na primer `æ` i `Æ`, ne mora biti zanemarena:

```sql
SELECT 'æ' LIKE 'Æ' AS unicode_case_match;
```

U uobičajenoj SQLite konfiguraciji rezultat je `0`. Zato ne pretpostavljaj da `LIKE` obavlja jezički ispravno poređenje za srpska ili druga Unicode slova.

SQLite ima `PRAGMA case_sensitive_like`, ali je to zastarela opcija i ne treba je koristiti kao novo rešenje. Promena njenog ponašanja može izazvati probleme ako se `LIKE` koristi u indeksima ili ograničenjima šeme. Za aplikaciju kojoj treba pouzdana Unicode pretraga izaberi i testiraj odgovarajuće proširenje, normalizaciju ili namensku strategiju pretrage.

Ponašanje `LIKE` može se razlikovati među bazama i u zavisnosti od njihove kolacije ili konfiguracije. Ako aplikaciju prebacuješ sa SQLite-a na PostgreSQL ili MySQL, proveri case-sensitivity i Unicode ponašanje na ciljnoj bazi umesto da pretpostaviš da su ista.

## `LIKE` i `NULL`

Ako je tekstualna kolona `NULL`, izraz `kolona LIKE obrazac` daje `NULL` — ne daje `TRUE` ni `FALSE`. `WHERE` zadržava samo redove za koje je uslov `TRUE`, pa takvi redovi neće biti vraćeni:

```sql
SELECT TrackId, Name
FROM tracks
WHERE Composer LIKE 'A%';
```

Ovaj upit ne vraća numere sa `Composer IS NULL`. `NOT LIKE` ne menja ovo pravilo: negacija nepoznatog rezultata ostaje nepoznata. Za pronalaženje nedostajućih vrednosti koristi `IS NULL`, a ne `LIKE`.

## `LIKE` nije `GLOB` niti regularni izraz

`LIKE` i `GLOB` oba porede tekst sa obrascem, ali koriste različite džokere:

| Operator | Bilo koji niz znakova | Jedan znak |
| -------- | --------------------- | ---------- |
| `LIKE`   | `%`                   | `_`        |
| `GLOB`   | `*`                   | `?`        |

SQLite `GLOB` je podrazumevano osetljiv na velika i mala slova i ima dodatnu sintaksu za skupove znakova. Nemoj prenositi `LIKE` džokere u `GLOB` obrazac ili obrnuto. Nijedan od ovih operatora sam po sebi nije puna zamena za regularne izraze.

## Redosled klauzula

Kada `LIKE` kombinuješ sa sortiranjem i ograničavanjem rezultata, klauzule pišeš ovim redosledom:

```sql
SELECT kolone
FROM tabela
WHERE tekstualna_kolona LIKE 'obrazac'
ORDER BY kolona
LIMIT broj_redova;
```

`WHERE` filtrira redove, `ORDER BY` određuje njihov redosled, a `LIMIT` ograničava koliko redova se vraća.

## Veza sa SQLAlchemy 2.0 i FastAPI-jem

U SQLAlchemy 2.0 koristi `.like()` da napraviš `LIKE` uslov. Primer traži nazive koji sadrže `Wild`:

```python
from sqlalchemy import select

term = "Wild"
pattern = f"%{term}%"

statement = (
    select(Track.track_id, Track.name)
    .where(Track.name.like(pattern))
    .order_by(Track.name, Track.track_id)
)
```

Primer pretpostavlja da model `Track` ima navedene atribute. SQLAlchemy prosleđuje obrazac kao vezani parametar; nemoj sastavljati SQL naredbu konkatenacijom korisničkog unosa.

Vezani parametar ipak ne pretvara `%` i `_` iz unosa u doslovne znakove. Ako pojam za pretragu dolazi od korisnika i treba da se traži doslovno, escapuj te znakove u aplikaciji i prosledi `.like()` odgovarajući `escape` argument, na primer `escape="!"`. To je odvojeno od SQL injection zaštite: parametri čuvaju strukturu upita, a escapovanje određuje značenje obrasca.

## Indeksi i performanse

Obrazac koji počinje običnim tekstom, kao `Name LIKE 'Wild%'`, ponekad može koristiti indeks, u zavisnosti od indeksa, kolacije i konfiguracije. Obrazac koji počinje džokerom, kao `Name LIKE '%Wild%'`, obično ne može koristiti običan B-tree indeks kao pretragu prefiksa. Nemoj pretpostaviti da je svaki `LIKE` brz ili da svaki koristi indeks; za velike tabele proveri plan upita i stvarne podatke.

## Česte greške

- **Zaboraviš da je `%` džoker:** `'%cat%'` traži `cat` unutar teksta; za doslovni `%` koristi `ESCAPE`.
- **Mešaš `%` i `_`:** `%` odgovara nula ili više znakova, `_` tačno jednom.
- **Staviš `%` na pogrešno mesto:** `'A%'` traži početak sa `A`, a `'%A'` traži završetak sa `A`.
- **Dodaš završni `%` kada želiš tačno završno slovo:** `'A%o%'` znači da se `o` pojavljuje posle početnog `A`; koristi `'A%o'` ako tekst mora da se završava slovom `o`.
- **Koristiš džokere iz `GLOB`:** `*` i `?` nisu džokeri za SQLite `LIKE`.
- **Pretpostaviš punu Unicode case-insensitivity:** SQLite-ov ugrađeni `LIKE` podrazumevano obrađuje samo ASCII razliku velikih i malih slova.
- **Očekuješ da `NOT LIKE` pronađe `NULL`:** koristi `IS NULL` za nedostajuću vrednost.
- **Pretpostaviš da vezani parametar čini džokere doslovnim:** parametar štiti SQL strukturu, ali `%` i `_` zadržavaju značenje obrasca.
- **Pretpostaviš da `%pojam%` koristi indeks:** početni džoker obično sprečava običnu pretragu prefiksa indeksom.

## Provera razumevanja

1. Šta znače džokeri `%` i `_`?
2. Koji obrazac traži tekst koji počinje sa `Wild`?
3. Koja je razlika između `'A%o'` i `'A%o%'`?
4. Kako se pomoću `LIKE` traži doslovni znak `%`?
5. Zašto SQLite upit `'æ' LIKE 'Æ'` podrazumevano ne mora vratiti tačno?
6. Šta se dešava ako leva vrednost `LIKE` izraza bude `NULL`?
7. Koje džokere koristi `GLOB`, a koje `LIKE`?
8. Da li SQLAlchemy vezani parametar automatski čini `%` i `_` doslovnim znakovima?
9. Zašto obrazac koji počinje sa `%` može biti sporiji na velikoj tabeli?
10. Zašto ne treba koristiti `PRAGMA case_sensitive_like` kao novo rešenje?

## Vežbe

### Vežba 1 — Pronađi nazive koji počinju sa `Wild`

1. Iz tabele `tracks` prikaži `TrackId` i `Name` za nazive koji počinju sa `Wild`.
2. Sortiraj po nazivu i identifikatoru.
3. Koliko redova vraća upit? Uporedi rezultat sa primerom u lekciji.

### Vežba 2 — Početak, kraj i sadržaj

Napiši tri upita nad `tracks.Name`:

1. nazivi koji počinju sa `Love`;
2. nazivi koji se završavaju sa `Love`;
3. nazivi koji sadrže `Love` bilo gde.

Objasni kako položaj `%` menja kriterijum.

### Vežba 3 — Znak na određenom mestu

Pronađi nazive numera čiji je drugi znak `r`. Zatim izmeni obrazac tako da traži tekst koji počinje sa `A` i ima najmanje još jedan znak.

### Vežba 4 — Doslovni džoker

Pokreni izraze koji pomoću `ESCAPE` traže doslovni `%` i `_`. Zatim objasni šta bi se promenilo kada bi uklonio `ESCAPE` ili znak `!` iz obrasca.

### Vežba 5 — Ponašanje velikih i malih slova

Uporedi rezultate izraza `'a' LIKE 'A'` i `'æ' LIKE 'Æ'`. Objasni zašto ovaj primer ne dokazuje da je SQLite `LIKE` potpuno case-insensitive.

### Vežba 6 — Bezbedan obrazac iz korisničkog unosa

Pretpostavi da FastAPI endpoint prima pojam za pretragu. Objasni razliku između:

1. prosleđivanja korisničkog pojma kao vezanog parametra;
2. escapovanja `%` i `_` kada korisnik želi doslovno pretraživanje tih znakova.
