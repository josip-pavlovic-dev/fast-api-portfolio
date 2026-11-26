# 02 — SQLite `IN` operator

## Cilj lekcije

U ovoj lekciji naučićeš kako da proveriš da li se vrednost nalazi među više ponuđenih vrednosti. Operator `IN` može koristiti listu vrednosti ili podupit. U primeru iz transkripta filtriraćemo numere prema tipu medija u Chinook bazi.

Prethodna lekcija: [`BETWEEN` operator](./01_sqlite_BETWEEN_operator.md).

## Čemu služi `IN`

`IN` proverava da li je vrednost jednaka nekoj od vrednosti navedenih u listi:

```sql
izraz IN (vrednost1, vrednost2, ...)
```

U `WHERE` uslovu, na primer:

```sql
SELECT kolone
FROM tabela
WHERE izraz IN (vrednost1, vrednost2, ...);
```

Ako je izraz jednak bar jednoj vrednosti iz liste, uslov je tačan. Lista može sadržati brojeve, tekst ili druge vrednosti koje mogu da se porede sa izrazom. Tekstualne vrednosti stavljaju se u jednostruke navodnike.

## Primer iz transkripta: `MediaTypeId` 1 ili 2

Tabela `tracks` sadrži identifikator tipa medija u koloni `MediaTypeId`. Transkript prikazuje numere čiji je tip medija `1` ili `2`:

```sql
SELECT TrackId, Name, MediaTypeId
FROM tracks
WHERE MediaTypeId IN (1, 2)
ORDER BY Name, TrackId;
```

Ovaj uslov je ekvivalentan sledećem:

```sql
WHERE MediaTypeId = 1 OR MediaTypeId = 2
```

Kada proveravaš više vrednosti iste kolone, `IN` je obično pregledniji od dugog niza `OR` uslova. U priloženoj Chinook bazi upit bez `LIMIT` vraća 3.271 red, kao u transkriptu.

Za pregled prvih pet redova možeš dodati `LIMIT`:

```sql
SELECT TrackId, Name, MediaTypeId
FROM tracks
WHERE MediaTypeId IN (1, 2)
ORDER BY Name, TrackId
LIMIT 5;
```

Očekivani rezultat:

| TrackId | Name                                                         | MediaTypeId |
| ------: | ------------------------------------------------------------ | ----------: |
|    3027 | `"40"`                                                       |           1 |
|    3412 | `"Eine Kleine Nachtmusik" Serenade In G, K. 525: I. Allegro` |           2 |
|     109 | `#1 Zero`                                                    |           1 |
|    3254 | `#9 Dream`                                                   |           2 |
|     602 | `'Round Midnight`                                            |           1 |

`ORDER BY Name, TrackId` sortira po nazivu, a zatim koristi `TrackId` kao dodatni kriterijum kada su nazivi jednaki. `LIMIT 5` ograničava prikaz; ne menja uslov `IN`.

## `IN` sa tekstualnim vrednostima

Vrednosti u listi mogu biti tekst:

```sql
SELECT CustomerId, FirstName, LastName, Country
FROM customers
WHERE Country IN ('Brazil', 'Canada')
ORDER BY Country, LastName, CustomerId;
```

Upit bira kupce čija je država Brazil ili Kanada. Tekst u listi mora odgovarati načinu na koji je sačuvan i poređen u koloni; na rezultat mogu uticati velika i mala slova i kolacija.

## `IN` u ograničenju `CHECK`

`IN` nije ograničen samo na `WHERE`. Može se koristiti i u izrazu za `CHECK` ograničenje da bi se dozvolile samo navedene vrednosti:

```sql
status TEXT NOT NULL
    CHECK (status IN ('open', 'in_progress', 'done'))
```

U `WHERE` uslovu `IN` bira postojeće redove; u `CHECK` ograničenju proverava da li nova ili izmenjena vrednost ispunjava pravilo tabele. `NOT NULL` je nameran: sam `CHECK` može dozvoliti `NULL`, jer nepoznat rezultat nije isto što i `FALSE`. Ovaj obrazac se pojavljuje u lekciji [SQLite ograničenja](../03_creating_database_tables_updating_data_deleting_records/01_sqlite_constraints.md).

## `IN` sa podupitom

Umesto ručno upisane liste, možeš navesti podupit:

```sql
izraz IN (
    SELECT jedna_kolona
    FROM tabela
    WHERE uslov
)
```

Podupit je jedan upit unutar spoljnog upita. On nije „više `SELECT` naredbi“; u ovom obliku je to jedan `SELECT` koji može vratiti nula, jedan ili više redova. Za poređenje pomoću `IN`, podupit treba da vrati jednu kolonu.

U Chinook bazi možemo pronaći numere sa računa čiji je `InvoiceId` jednak `1`:

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

Unutrašnji upit dobija `TrackId` vrednosti iz `invoice_items`; spoljni upit bira odgovarajuće numere iz `tracks`. U priloženoj bazi rezultat sadrži dve numere:

| TrackId | Name              |
| ------: | ----------------- |
|       2 | Balls to the Wall |
|       4 | Restless and Wild |

Podupit može vratiti isti `TrackId` više puta. `IN` proverava pripadnost skupu vrednosti, pa duplikati u podupitu ne dupliraju redove spoljnog rezultata. To se razlikuje od nekih upita sa `JOIN`, koji mogu vratiti više redova za više poklapanja; `JOIN` obrađujemo u posebnoj oblasti.

Ako podupit ne vrati nijedan red, nema vrednosti koje bi zadovoljile običan `IN` uslov. `IN` sa podupitom mora i dalje vraćati jednu kolonu, čak i kada ne vraća nijedan red.

## `NOT IN`: vrednosti koje nisu na listi

Dodavanjem `NOT` dobijaš vrednosti koje se ne podudaraju ni sa jednom vrednošću iz liste:

```sql
SELECT TrackId, Name, MediaTypeId
FROM tracks
WHERE MediaTypeId NOT IN (1, 2)
ORDER BY MediaTypeId, TrackId
LIMIT 10;
```

Za listu koja ne sadrži `NULL`, `MediaTypeId NOT IN (1, 2)` je ekvivalentno uslovu:

```sql
MediaTypeId <> 1 AND MediaTypeId <> 2
```

## Važna zamka: `NULL` u `IN` i `NOT IN`

SQL koristi trovalentnu logiku: rezultat uslova može biti `TRUE`, `FALSE` ili `UNKNOWN`. U SQLite-u se `TRUE` i `FALSE` obično prikazuju kao `1` i `0`, dok je `UNKNOWN` predstavljen kao `NULL`.

Na primer:

```sql
SELECT
    2 IN (1, 2, NULL) AS postoji_poklapanje,
    3 IN (1, 2, NULL) AS nema_poklapanja,
    3 NOT IN (1, 2, NULL) AS nije_na_listi;
```

Rezultati su `1`, `NULL` i `NULL`:

- `2` se poklapa sa jednim članom liste, zato je prvi rezultat tačan.
- `3` se ne poklapa sa `1` ni sa `2`, ali se ne može utvrditi da li je jednak nepoznatoj vrednosti `NULL`; zato je rezultat nepoznat, a ne `FALSE`.
- `NOT NULL` je i dalje `NULL`, zato `NOT IN` ne pretvara nepoznat rezultat u tačan.

`WHERE` zadržava samo redove za koje je uslov `TRUE`. Zato `NOT IN` može neočekivano izostaviti sve redove kada podupit vrati makar jedan `NULL`, čak i ako se konkretna vrednost ne pojavljuje među poznatim vrednostima podupita.

Pre `NOT IN` nad podupitom proveri da li rezultat može sadržati `NULL`. Mogućnosti su:

1. Isključi `NULL` vrednosti u samom podupitu:

   ```sql
   WHERE CustomerId NOT IN (
       SELECT CustomerId
       FROM another_table
       WHERE CustomerId IS NOT NULL
   )
   ```

2. Koristi `NOT EXISTS` kada želiš da proveriš da odgovarajući red ne postoji:

   ```sql
   SELECT c.CustomerId, c.FirstName, c.LastName
   FROM customers AS c
   WHERE NOT EXISTS (
       SELECT 1
       FROM invoices AS i
       WHERE i.CustomerId = c.CustomerId
   );
   ```

Uslov unutar `NOT EXISTS` proverava poklapanje redova; `NULL` u nepovezanom redu podupita ne poništava rezultat provere kao što može da se desi sa `NOT IN`. Ako spoljašnja vrednost sama može biti `NULL`, odluči posebno da li želiš da je rezultat uključiš ili isključiš.

I lista literala može sadržati `NULL`. Na primer, `3 NOT IN (1, 2, NULL)` daje `NULL`, pa ga `WHERE` neće tretirati kao „3 nije na listi“.

## Prazna lista

SQLite dozvoljava praznu listu:

```sql
SELECT
    5 IN () AS prazno_in,
    5 NOT IN () AS prazno_not_in,
    NULL IN () AS null_prazno_in,
    NULL NOT IN () AS null_prazno_not_in;
```

U SQLite-u rezultati su `0`, `1`, `0` i `1`. Prazan skup ne sadrži poklapanja, pa je `IN ()` netačan, a `NOT IN ()` tačan — čak i kada je leva vrednost `NULL`.

Iako je ovo definisano ponašanje SQLite-a, sintaksa `IN ()` nije prenosiva na sve baze. Kada aplikacija dinamički pravi listu parametara, unapred definiši šta prazan spisak znači. Ako prazna lista treba da vrati nula redova, napravi odgovarajući uslov ili koristi podršku biblioteke za parametre; nemoj uklanjati filter ako to nije nameravano ponašanje.

## `IN` i `NULL` u samoj koloni

Ako je leva vrednost `NULL`, poređenje sa nepraznom listom uglavnom daje `NULL`:

```sql
SELECT NULL IN (1, 2) AS null_na_listi;
```

Rezultat je `NULL`. Zato `WHERE nullable_column IN (1, 2)` ne bira redove u kojima je `nullable_column` `NULL`. Za njih koristi poseban uslov:

```sql
WHERE nullable_column IN (1, 2)
   OR nullable_column IS NULL
```

Ovo eksplicitno uključuje i vrednosti iz liste i redove bez vrednosti.

## Redosled klauzula

Kada upit koristi `IN`, sortiranje i ograničavanje, klauzule pišeš ovim redosledom:

```sql
SELECT kolone
FROM tabela
WHERE izraz IN (vrednosti)
ORDER BY kolona
LIMIT broj_redova;
```

`IN` je deo uslova `WHERE`; `ORDER BY` određuje redosled rezultata, a `LIMIT` ograničava broj vraćenih redova.

## Veza sa SQLAlchemy 2.0 i FastAPI-jem

U SQLAlchemy 2.0 metoda `.in_()` pravi uslov `IN`:

```python
from sqlalchemy import select

media_type_ids = [1, 2]

statement = (
    select(Track.track_id, Track.name, Track.media_type_id)
    .where(Track.media_type_id.in_(media_type_ids))
    .order_by(Track.name, Track.track_id)
)
```

Primer pretpostavlja da ORM model `Track` ima navedene atribute. SQLAlchemy vrednosti iz liste prosleđuje kao vezane parametre, a ne spaja ih direktno u SQL tekst. Ako `media_type_ids` dolazi iz FastAPI zahteva, validiraj ulaz i definiši ponašanje za praznu listu. Prazna lista obično treba da ima namerno ponašanje, na primer da ne vrati nijedan red, a ne da nenamerno ukloni filter.

Za listu koju vraća podupit, `.in_()` može da primi i `select()` izraz:

```python
media_type_ids_query = select(MediaType.media_type_id).where(
    MediaType.name.like("%AAC%")
)

statement = select(Track.track_id, Track.name).where(
    Track.media_type_id.in_(media_type_ids_query)
)
```

Ovaj primer pretpostavlja modele `Track` i `MediaType` sa odgovarajućim atributima. SQLAlchemy sastavlja podupit kao deo SQL izraza.

## Česte greške

- **Napišeš `IN` bez zagrada:** lista vrednosti ili podupit moraju biti unutar `(...)`.
- **Mešaš `IN` i `BETWEEN`:** `IN` proverava članstvo u skupu navedenih vrednosti; `BETWEEN` proverava opseg.
- **Koristiš `NOT IN` sa podupitom koji vraća `NULL`:** rezultat može postati `UNKNOWN`, pa redovi izostanu iz rezultata.
- **Pretpostaviš da je `NULL` isto što i prazna vrednost:** za `NULL` koristi `IS NULL`, a ne `IN` proveru.
- **Pretpostaviš da duplikati u listi dupliraju rezultat:** `IN` proverava poklapanje, ne pravi po jedan rezultat za svaku ponovljenu vrednost u listi.
- **Staviš tekst bez navodnika:** piši, na primer, `Country IN ('Brazil', 'Canada')`.
- **Pretpostaviš da `IN ()` radi u svakoj bazi:** SQLite ga podržava, ali druge baze mogu odbiti tu sintaksu.
- **Očekuješ da `LIMIT` promeni filtriranje:** `LIMIT` ograničava prikazani rezultat posle uslova.

## Provera razumevanja

1. Šta proverava `MediaTypeId IN (1, 2)`?
2. Kako se ovaj uslov može zapisati pomoću `OR`?
3. Koja je razlika između liste vrednosti i podupita u `IN` izrazu?
4. Koliko kolona treba da vrati podupit upotrebljen sa običnim `IN` izrazom?
5. Da li ponovljena vrednost u podupitu duplira red spoljnog upita?
6. Zašto `NOT IN (SELECT ...)` može dati neočekivano prazan rezultat ako podupit vrati `NULL`?
7. Kada je `NOT EXISTS` bolji izbor od `NOT IN`?
8. Kako `WHERE nullable_column IN (1, 2)` tretira red u kom je kolona `NULL`?
9. Šta SQLite vraća za `5 IN ()` i zašto ne treba pretpostaviti da je ta sintaksa prenosiva?
10. Koja je razlika između `IN` i `BETWEEN`?

## Vežbe

### Vežba 1 — Filtriraj po više tipova medija

1. Iz tabele `tracks` prikaži `TrackId`, `Name` i `MediaTypeId` za numere sa `MediaTypeId` vrednostima `1` ili `2`.
2. Sortiraj po `Name`, pa po `TrackId`.
3. Koliko redova vraća upit?
4. Ograniči prikaz na pet redova i uporedi ih sa primerom u lekciji.

### Vežba 2 — Zameni `IN` sa `OR`

Prepiši uslov `MediaTypeId IN (1, 2)` pomoću `OR`. Dodaj isti `ORDER BY Name, TrackId` u oba upita, pokreni ih i proveri da li vraćaju iste redove.

### Vežba 3 — Filtriraj tekstualne vrednosti

Iz tabele `customers` prikaži identifikator, ime, prezime i državu za kupce iz Brazila ili Kanade. Sortiraj po državi, prezimenu i identifikatoru.

### Vežba 4 — Koristi podupit

Pronađi `TrackId` i `Name` numera koje se nalaze na računu sa `InvoiceId = 1`. Koristi podupit nad tabelom `invoice_items`, zatim proveri rezultat pomoću primera iz lekcije.

### Vežba 5 — Uporedi `IN` i `NOT IN`

Prikaži numere čiji `MediaTypeId` nije `1` niti `2`. Zatim dodaj `NULL` u listu `NOT IN` uslova i objasni zašto se rezultat menja. Proveri ponašanje zasebno sa izrazom `3 NOT IN (1, 2, NULL)`.

### Vežba 6 — Proveri `NULL` i praznu listu

Pokreni izraze `NULL IN (1, 2)`, `5 IN ()` i `5 NOT IN ()`. Zapiši rezultate u SQLite-u i objasni zašto ne treba mešati praznu listu sa listom koja sadrži `NULL`.
