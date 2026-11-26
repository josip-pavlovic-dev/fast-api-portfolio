# 05 — SQLite `LIMIT` klauzula

## Cilj lekcije

U ovoj lekciji naučićeš kako da pomoću `LIMIT` ograničiš broj redova koje `SELECT` upit vraća, a pomoću `OFFSET` preskočiš početni deo rezultata. Obratićemo pažnju na to zašto je `ORDER BY` neophodan za predvidiv rezultat i kako `LIMIT` i `OFFSET` odgovaraju straničenju u aplikaciji.

Prethodna lekcija: [`GLOB` operator](./04_sqlite_GLOB_operator.md).

## Čemu služi `LIMIT`

`LIMIT` ograničava broj redova u rezultatu upita. Ne menja podatke u tabeli i ne ograničava broj kolona:

```sql
SELECT kolone
FROM tabela
LIMIT broj_redova;
```

Na primer, tabela `tracks` u kursnoj Chinook bazi sadrži 3.503 reda. Ovaj upit vraća najviše pet numera:

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 5;
```

Očekivani rezultat:

| TrackId | Name                                    |
| ------: | --------------------------------------- |
|       1 | For Those About To Rock (We Salute You) |
|       2 | Balls to the Wall                       |
|       3 | Fast As a Shark                         |
|       4 | Restless and Wild                       |
|       5 | Princess of the Dawn                    |

`LIMIT 5` ograničava broj vraćenih redova na najviše pet. Ne znači da tabela sadrži samo pet redova niti da je upit pročitao samo pet redova iz svih mogućih planova izvršavanja.

## Zašto je `ORDER BY` važan

Relacione tabele ne garantuju redosled redova. Bez `ORDER BY`, `LIMIT 5` vraća pet redova, ali SQL ne garantuje da će to biti isti redovi pri svakom izvršavanju.

```sql
SELECT TrackId, Name
FROM tracks
LIMIT 5;
```

Ovaj upit ograničava broj redova, ali ne definiše šta znači „prvih pet“. Za predvidiv izbor navedi kriterijum sortiranja:

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 5;
```

Ako vrednosti po kojima sortiraš nisu jedinstvene, dodaj jedinstvenu kolonu kao dodatni kriterijum. Na primer:

```sql
SELECT TrackId, Name, Milliseconds
FROM tracks
ORDER BY Milliseconds DESC, TrackId ASC
LIMIT 10;
```

Upit bira deset najdužih numera. Ako dve numere imaju isto trajanje, manji `TrackId` određuje koja ide prva. Ovo je posebno važno za straničenje, jer izjednačeni redovi bez dodatnog kriterijuma mogu menjati međusobni redosled.

## `OFFSET`: preskakanje redova

`OFFSET` određuje koliko redova treba preskočiti pre nego što se vrate redovi ograničeni pomoću `LIMIT`:

```sql
SELECT kolone
FROM tabela
ORDER BY kolona
LIMIT broj_redova OFFSET broj_za_preskakanje;
```

Sa `ORDER BY TrackId`, sledeći upit preskače prvih pet numera i vraća narednih pet:

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 5 OFFSET 5;
```

Očekivani rezultat:

| TrackId | Name                  |
| ------: | --------------------- |
|       6 | Put The Finger On You |
|       7 | Let's Get It Up       |
|       8 | Inject The Venom      |
|       9 | Snowballed            |
|      10 | Evil Walks            |

`OFFSET` broji broj **preskočenih** redova i počinje od nule:

- `OFFSET 0` ne preskače nijedan red; prvi rezultat je prvi red sortiranog niza.
- `OFFSET 5` preskače prvih pet redova; sledeći rezultat je šesti red.
- `OFFSET 12` preskače prvih 12 redova; sledeći rezultat je 13. red.

Zato upit:

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 12 OFFSET 12;
```

vraća 12 numera počevši od `TrackId` 13, a ne od 12. reda. Ovo precizira primer iz transkripta: `OFFSET 12` ne znači „počni od 12. reda“, već „preskoči 12 redova“.

## Straničenje rezultata

Straničenje deli sortirani rezultat na manje grupe, odnosno stranice. Za stranicu veličine pet, uz redosled po jedinstvenom `TrackId`:

| Stranica | `LIMIT` | `OFFSET` | Očekivani `TrackId` |
| -------: | ------: | -------: | ------------------- |
|        1 |       5 |        0 | 1–5                 |
|        2 |       5 |        5 | 6–10                |
|        3 |       5 |       10 | 11–15               |

Opšti obračun za stranicu `p` koja počinje od 1 i veličinu stranice `s` je:

```text
OFFSET = (p - 1) * s
LIMIT = s
```

Na primer, stranica 3 sa po pet redova koristi `LIMIT 5 OFFSET 10`.

Za stabilno straničenje koristi jedinstven `ORDER BY`. Ipak, ako se između učitavanja stranica redovi dodaju ili brišu, položaji se mogu pomeriti: korisnik može videti ponovljen red ili propustiti red na sledećoj stranici. Za velike tabele ili često menjane podatke razmotri straničenje po ključu (keyset pagination), koje nastavlja posle poslednje viđene vrednosti umesto da preskače sve prethodne redove.

Osnovni oblik straničenja po ključu može izgledati ovako:

```sql
SELECT TrackId, Name
FROM tracks
WHERE TrackId > :last_seen_track_id
ORDER BY TrackId
LIMIT :page_size;
```

Ovo je samo obrazac za nastavak posle poslednjeg prikazanog identifikatora; aplikacija mora sačuvati i proslediti taj identifikator između zahteva.

## SQLite granični slučajevi

### `LIMIT 0`

`LIMIT 0` vraća nula redova:

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 0;
```

Ovo može biti korisno kada ti treba oblik ili metapodatak rezultata bez redova, ali ne koristi ga ako očekuješ podatke.

### Negativan `LIMIT`

SQLite tretira negativan `LIMIT` kao da ne postoji gornje ograničenje broja redova:

```sql
SELECT TrackId
FROM tracks
LIMIT -1;
```

Ovaj upit može vratiti sve redove. Zato u aplikaciji proveri da je veličina stranice pozitivna i postavi razumnu gornju granicu. Nemoj dozvoliti da slučajna negativna vrednost ukloni ograničenje.

### Negativan `OFFSET`

U SQLite-u se negativan `OFFSET` tretira kao nula:

```sql
SELECT TrackId
FROM tracks
ORDER BY TrackId
LIMIT 3 OFFSET -5;
```

Ovaj upit počinje od prvog reda. Ipak, aplikacija treba da validira `OFFSET` kao vrednost veću ili jednaku nuli, umesto da se oslanja na SQLite specifično ponašanje.

### `OFFSET` veći od rezultata

Ako se preskoči više redova nego što ih rezultat sadrži, upit vraća nula redova. `LIMIT` i `OFFSET` ne izazivaju grešku samo zato što je tražena stranica van dostupnog raspona.

## SQLite sintaksa sa zarezom

SQLite prihvata i kraći oblik:

```sql
LIMIT pomeraj, broj_redova
```

Na primer:

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY TrackId
LIMIT 5, 5;
```

Ovo je ekvivalentno obliku:

```sql
LIMIT 5 OFFSET 5
```

U zapisu sa zarezom, **prvi broj je `OFFSET`**, a drugi je broj redova — redosled je drugačiji od jasnijeg `LIMIT broj_redova OFFSET pomeraj`. Da izbegneš zabunu i olakšaš čitanje, u ovom kursu koristi oblik sa ključnom reči `OFFSET`.

## Redosled klauzula

Kada koristiš filtriranje, sortiranje i ograničavanje, klauzule pišeš ovim redosledom:

```sql
SELECT kolone
FROM tabela
WHERE uslov
ORDER BY kolona
LIMIT broj_redova OFFSET broj_za_preskakanje;
```

`WHERE` bira redove, `ORDER BY` određuje njihov redosled, a `LIMIT` i `OFFSET` određuju koji deo sortiranog rezultata se vraća. Ovo je konceptualno objašnjenje rezultata, a ne tvrdnja o tačnom internom planu koji SQLite bira.

Za ukupan broj redova koji ispunjavaju filter koristi `COUNT(*)`, ne `LIMIT`:

```sql
SELECT COUNT(*) AS broj_numera
FROM tracks
WHERE AlbumId = 1;
```

Upit sa `LIMIT` vraća najviše deo odgovarajućih redova; `COUNT(*)` računa koliko ih ukupno ispunjava uslov.

## Veza sa SQLAlchemy 2.0 i FastAPI-jem

U SQLAlchemy 2.0 koristi `.limit()` i `.offset()`:

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

Primer pretpostavlja da model `Track` ima navedene atribute. `ORDER BY` je nameran: bez sortiranja API ne može pouzdano definisati šta je prva ili sledeća stranica.

U FastAPI-ju validiraj veličinu stranice i pomeraj pre nego što ih proslediš upitu. Na primer, `page_size` može imati minimum 1 i razuman maksimum, a `offset` minimum 0. SQLAlchemy vrednosti prosleđuje kroz parametre; i dalje treba ograničiti koliko podataka jedan zahtev može zatražiti.

## Česte greške

- **Očekuješ stabilan „prvi red“ bez `ORDER BY`:** SQL ne garantuje redosled bez sortiranja.
- **Sortiraš po vrednosti koja nije jedinstvena:** dodaj jedinstven kriterijum, često primarni ključ.
- **Tumačiš `LIMIT` kao broj kolona:** ograničava broj redova.
- **Tumačiš `OFFSET 12` kao početak od 12. reda:** preskače 12 redova, pa prvi vraćeni red je 13. u sortiranom nizu.
- **Zameniš redosled u sintaksi sa zarezom:** `LIMIT offset, count` nije isto napisan redosledom kao `LIMIT count OFFSET offset`.
- **Proslediš negativnu veličinu stranice:** u SQLite-u negativan `LIMIT` može ukloniti gornju granicu.
- **Koristiš veliki `OFFSET` bez razmišljanja o trošku:** baza može morati da pređe i preskoči mnogo prethodnih redova.
- **Misliš da `LIMIT` računa ukupan broj pogodaka:** koristi `COUNT(*)` za broj svih odgovarajućih redova.
- **Zaboraviš da promene podataka pomeraju stranice:** `OFFSET` straničenje može prikazati pomerene rezultate ako se podaci menjaju između zahteva.

## Provera razumevanja

1. Na šta `LIMIT 5` utiče — broj kolona ili broj redova?
2. Zašto upit sa `LIMIT` treba obično da ima `ORDER BY`?
3. Šta vraća `LIMIT 5 OFFSET 5` ako je rezultat stabilno sortiran?
4. Koliko redova preskače `OFFSET 12`, i od kog reda počinje sledeći rezultat?
5. Zašto je `LIMIT 5, 12` lako pogrešno pročitati?
6. Šta SQLite radi sa negativnim `LIMIT`-om, a šta sa negativnim `OFFSET`-om?
7. Kako dobijaš ukupan broj pogodaka, a ne samo prvih nekoliko?
8. Zašto jedinstveni kriterijum u `ORDER BY` pomaže pri straničenju?
9. Zašto običan `OFFSET` može biti nepouzdan ako se podaci menjaju između zahteva?
10. Koja je razlika između offset i keyset straničenja?

## Vežbe

### Vežba 1 — Prikaži ograničen broj numera

1. Prikaži `TrackId` i `Name` za prvih pet numera sortirano po `TrackId`.
2. Pokreni upit bez `LIMIT` i uporedi broj vraćenih redova.
3. Objasni zašto `LIMIT 5` ne znači da tabela ima pet redova.

### Vežba 2 — Sledeća stranica

1. Koristi `LIMIT 5 OFFSET 5` da prikažeš drugu stranicu od po pet numera.
2. Proveri da li su identifikatori od 6 do 10.
3. Ponovi za treću stranicu i objasni kako si izračunao `OFFSET`.

### Vežba 3 — Oponašaj primer iz transkripta

Napiši upit koji sortira numere po `TrackId`, preskače 12 redova i vraća narednih 12. Zapiši `TrackId` prvog i poslednjeg vraćenog reda. Objasni zašto prvi nije broj 12.

### Vežba 4 — Sortiranje sa ponovljenim vrednostima

Prikaži deset najdužih numera sortirano po `Milliseconds` opadajuće. Kao dodatni kriterijum koristi `TrackId` rastuće i objasni zašto je koristan.

### Vežba 5 — Granični slučajevi

Pokreni upite sa `LIMIT 0`, negativnim `LIMIT`, negativnim `OFFSET` i `OFFSET` većim od broja redova. Zapiši rezultat svakog od njih i objasni zašto aplikacija ipak treba da validira ulazne vrednosti.

### Vežba 6 — Izbroj pogodke odvojeno od prikaza

Nad tabelom `tracks` izračunaj koliko redova ispunjava `AlbumId = 1`. Zatim prikaži samo četiri reda istog skupa, sortirana po `TrackId`. Uporedi broj iz `COUNT(*)` sa brojem prikazanih redova.
