# 01 — SQLite `LEFT JOIN`

## Cilj lekcije

U ovoj lekciji naučićeš kako `LEFT JOIN` spaja podatke iz dve tabele, zadržava sve redove leve tabele i dopunjava ih podacima sa desne strane kada postoji poklapanje. Ako ga nema, kolone desne tabele u rezultatu dobijaju `NULL`.

Koristićemo tabele `artists` i `albums` iz Chinook baze. Jedan izvođač može imati nula, jedan ili više albuma; svaki album pripada jednom izvođaču. Ovaj primer pokazuje zašto broj redova rezultata `JOIN` upita ne mora biti jednak broju redova ni u jednoj pojedinačnoj tabeli.

Prethodne lekcije: [filtriranje pomoću `WHERE`](../02_retriving_data_and_manipulating_data/06_filtering_data_with_where_clause.md), [sortiranje pomoću `ORDER BY`](../02_retriving_data_and_manipulating_data/04_sorting_data_using_order_by_clause.md) i [prepoznavanje `NULL`](../02_retriving_data_and_manipulating_data/07_identifying_null_values.md).

## Čemu služi `LEFT JOIN`

`LEFT JOIN` spaja levu tabelu sa desnom tabelom prema uslovu u `ON` delu:

```sql
SELECT kolone
FROM leva_tabela AS l
LEFT JOIN desna_tabela AS r
    ON uslov_poklapanja;
```

- **Leva tabela** je izvor naveden pre `LEFT JOIN`.
- **Desna tabela** je izvor naveden posle `LEFT JOIN`.
- `ON` određuje koje redove desne tabele treba povezati sa svakim redom leve tabele.
- Svi redovi leve tabele ostaju u rezultatu.
- Za levo-desni par koji se poklopi, rezultat sadrži podatke iz obe tabele.
- Ako nema poklapanja, rezultat ipak sadrži red leve tabele, dok se sve izabrane kolone desne tabele prikazuju kao `NULL`.

`LEFT OUTER JOIN` je puniji naziv za isti spoj; uobičajeno je pisati kraće `LEFT JOIN`.

## Primer: izvođači i njihovi albumi

U Chinook bazi `artists.ArtistId` je ključ izvođača, a `albums.ArtistId` pokazuje kojem izvođaču album pripada. Povežimo ih:

```sql
SELECT
    ar.ArtistId,
    ar.Name AS ArtistName,
    al.AlbumId,
    al.Title AS AlbumTitle
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
ORDER BY al.AlbumId, ar.ArtistId;
```

U `ON` uslovu povezujemo iste identifikatore. Alias-i `ar` i `al` čine upit kraćim, a prefiksiranje kolona uklanja dvosmislenost kada obe tabele imaju kolonu sličnog imena.

Za svakog izvođača koji ima albume, rezultat sadrži po jedan red za svaki album. Izvođač bez albuma se i dalje pojavljuje jednom, sa `NULL` u `AlbumId` i `AlbumTitle`.

U radnoj Chinook kopiji ovaj spoj daje:

- **418 redova rezultata**;
- **275 različitih izvođača**;
- **347 poklopljenih albuma**;
- **71 izvođača bez albuma**.

Dakle, 418 nije broj albuma niti broj izvođača. To je broj redova nakon spoja: više albuma može proizvesti više redova za istog izvođača, a svaki izvođač bez albuma dobija jedan null-prošireni red.

Brojeve možeš proveriti ovako:

```sql
SELECT
    COUNT(*) AS joined_rows,
    COUNT(DISTINCT ar.ArtistId) AS artists,
    COUNT(al.AlbumId) AS matched_albums,
    SUM(CASE WHEN al.AlbumId IS NULL THEN 1 ELSE 0 END) AS artists_without_albums
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId;
```

Rezultat za priloženu bazu je `418 | 275 | 347 | 71`. `COUNT(*)` broji svaki red rezultata, uključujući null-proširene redove. `COUNT(al.AlbumId)` broji samo poklopljene albume, jer je `AlbumId` primarni ključ i ne može biti `NULL` u stvarnom redu albuma.

## Pronađi izvođače bez albuma

`LEFT JOIN` omogućava da pronađeš redove leve tabele bez odgovarajućeg reda na desnoj strani. Proveri `NULL` u desnoj tabeli:

```sql
SELECT
    ar.ArtistId,
    ar.Name AS ArtistName
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
WHERE al.AlbumId IS NULL
ORDER BY ar.ArtistId;
```

Pošto `AlbumId` predstavlja primarni ključ stvarnog albuma, `NULL` u toj koloni u rezultatu spoja znači da nije pronađen album. Upit vraća 71 izvođača u priloženoj Chinook kopiji.

Možeš napisati i brojajući upit:

```sql
SELECT COUNT(*) AS artists_without_albums
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
WHERE al.AlbumId IS NULL;
```

Očekivani rezultat je `71`.

### Važna ispravka transkripta: `ORDER BY` nije filter

Transkript pokazuje sortiranje po `AlbumId` da bi se redovi sa `NULL` vrednostima pojavili zajedno. U SQLite-u se `NULL` podrazumevano sortira pre ostalih vrednosti u rastućem redosledu, pa `ORDER BY al.AlbumId` može prikazati izvođače bez albuma na početku.

Međutim, **`ORDER BY` ne izdvaja niti filtrira te redove**: rezultat i dalje sadrži i izvođače sa albumima. Da bi dobio samo izvođače bez albuma, koristi `WHERE al.AlbumId IS NULL`, kao u prethodnom upitu. `ORDER BY` upravlja redosledom; `WHERE` bira redove.

Ako želiš redove sa poklapanjem prvo ili poslednje, navedi smer sortiranja ili eksplicitan položaj `NULL` vrednosti. Za stabilan redosled dodaj dodatnu kolonu, kao što je `ar.ArtistId`, jer više redova može imati isti `AlbumId` vrednosni status (`NULL`).

## Jedan red leve tabele može dati više rezultata

`LEFT JOIN` ne garantuje tačno jedan rezultat po redu leve tabele. Ako se izvođač poklopi sa pet albuma, dobićeš pet rezultata za tog izvođača — po jedan za svaki album.

To nije greška niti dupliranje koje `LEFT JOIN` treba automatski ukloniti. Svaki red predstavlja par koji zadovoljava `ON` uslov. `DISTINCT` može ukloniti ponovljene izlazne kombinacije, ali nemoj ga dodavati samo da bi prikaz „izgledao urednije“: najpre odluči da li želiš jedan red po albumu, jedan red po izvođaču ili zbirni rezultat.

Za po jedan red po izvođaču možeš grupisati i brojati albume:

```sql
SELECT
    ar.ArtistId,
    ar.Name AS ArtistName,
    COUNT(*) AS joined_rows,
    COUNT(al.AlbumId) AS album_count
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
GROUP BY ar.ArtistId, ar.Name
ORDER BY album_count, ar.ArtistId;
```

Kod izvođača bez albuma `COUNT(*)` je `1`, jer postoji jedan null-prošireni red, dok je `COUNT(al.AlbumId)` `0`. Za broj povezanih albuma koristi brojanje nenulte kolone desne tabele, po mogućnosti njenog primarnog ključa.

## Razlika između uslova `ON` i `WHERE`

Uslov u `ON` određuje koje redove desne tabele smatramo poklapanjem. `WHERE` se primenjuje na već formirane rezultate spoja i može ukloniti null-proširene redove.

### Filter desne tabele u `ON`: sačuvaj sve izvođače

Sledeći upit spaja samo albume čiji naziv počinje sa `A`, ali i dalje vraća sve izvođače:

```sql
SELECT ar.ArtistId, ar.Name, al.AlbumId, al.Title
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
   AND al.Title LIKE 'A%'
ORDER BY ar.ArtistId, al.AlbumId;
```

Ako izvođač nema nijedan album sa tim nazivom, njegove kolone albuma postaju `NULL`.

### Isti filter u `WHERE`: ukloni redove bez podudaranja

```sql
SELECT ar.ArtistId, ar.Name, al.AlbumId, al.Title
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
WHERE al.Title LIKE 'A%'
ORDER BY ar.ArtistId, al.AlbumId;
```

Za red bez albuma `al.Title` je `NULL`, pa `al.Title LIKE 'A%'` nije tačno. `WHERE` zato uklanja takav red; praktično, ovaj uslov eliminiše null-proširene redove i menja rezultat koji si očekivao od `LEFT JOIN`.

Izaberi mesto uslova prema nameri:

- filter koji ograničava **poklapanja desne tabele**, ali čuva sve leve redove — stavi u `ON`;
- filter koji treba da ukloni redove iz **konačnog rezultata** — stavi u `WHERE`.

Ova razlika je jedan od najvažnijih rubnih slučajeva kod spoljnog spajanja.

## Šta znače `NULL` vrednosti sa desne strane?

Kada nema poklapanja, SQLite dopunjava svaku izabranu kolonu desne tabele vrednošću `NULL`. To ne znači da je u tabeli `albums` pronađen red čije su kolone `NULL`; taj red desne tabele uopšte ne postoji za ovo poklapanje.

Proveru nepoklapanja radi preko kolone desne tabele koja je garantovano `NOT NULL` kada red postoji, najčešće primarnog ključa:

```sql
WHERE al.AlbumId IS NULL
```

Ako umesto toga proveriš opcionalnu kolonu, kao `al.Title`, možeš pomešati:

1. red koji ne postoji zbog izostalog poklapanja;
2. postojeći red albuma čija je `Title` vrednost stvarno `NULL`, ako šema to dozvoljava.

U trenutnoj Chinook šemi naziv albuma je obavezan, ali pouzdana opšta navika je testiranje desnog primarnog ključa. Za `NULL` koristi `IS NULL`, ne `= NULL`.

## Leva i desna strana su važne

Upit:

```sql
FROM artists AS ar
LEFT JOIN albums AS al
    ON al.ArtistId = ar.ArtistId
```

čuva sve redove iz `artists`. Ako zameniš strane:

```sql
FROM albums AS al
LEFT JOIN artists AS ar
    ON ar.ArtistId = al.ArtistId
```

čuvaš sve redove iz `albums`, a ne izvođače bez albuma. `LEFT JOIN` nije simetričan: odaberi levu tabelu prema tome koji entiteti moraju ostati u rezultatu.

## Poređenje sa `INNER JOIN`

`INNER JOIN` vraća samo redove sa poklapanjem; `LEFT JOIN` vraća i sve redove leve strane bez poklapanja:

```sql
SELECT ar.ArtistId, ar.Name, al.AlbumId, al.Title
FROM artists AS ar
INNER JOIN albums AS al
    ON al.ArtistId = ar.ArtistId;
```

U ovoj Chinook bazi `INNER JOIN` vraća 347 redova — po jedan za svaki album — dok `LEFT JOIN` vraća 418 redova zbog 71 izvođača bez albuma. U drugim podacima broj može biti drugačiji; važan je princip, ne memorisanje ovih vrednosti.

## Redosled klauzula

Kada kombinuješ spoj, filter, sortiranje i ograničavanje, koristi ovaj redosled:

```sql
SELECT kolone
FROM leva_tabela
LEFT JOIN desna_tabela
    ON uslov_poklapanja
WHERE uslov_za_krajnji_rezultat
ORDER BY kolona
LIMIT broj_redova;
```

`ON` definiše poklapanje; `WHERE` filtrira rezultat; `ORDER BY` sortira; `LIMIT` ograničava broj vraćenih redova.

## Veza sa SQLAlchemy 2.0 i FastAPI-jem

U SQLAlchemy 2.0 možeš da napraviš isti spoj pomoću `outerjoin()`:

```python
from sqlalchemy import select

statement = (
    select(
        Artist.artist_id,
        Artist.name,
        Album.album_id,
        Album.title,
    )
    .select_from(Artist)
    .outerjoin(Album, Album.artist_id == Artist.artist_id)
    .order_by(Album.album_id, Artist.artist_id)
)
```

Primer pretpostavlja ORM modele `Artist` i `Album` sa navedenim atributima. Za pronalaženje izvođača bez albuma dodaj uslov:

```python
statement = statement.where(Album.album_id.is_(None))
```

SQLAlchemy izraz `.is_(None)` generiše SQL proveru `IS NULL`. Kao i u običnom SQL-u, izaberi ključ desne tabele koji ne može biti `NULL` u postojećem redu. U FastAPI endpointu proveri oblik odgovora: izvođač može imati nula, jedan ili više pridruženih redova albuma, pa rezultat upita nije nužno jedan red po izvođaču.

## Česte greške

- **Misliš da `ORDER BY ... IS NULL` filtrira redove:** sortiranje samo menja redosled; za izdvajanje koristi `WHERE ... IS NULL`.
- **Filtriraš desnu tabelu u `WHERE` i izgubiš nepoklopljene leve redove:** ako želiš da sačuvaš sve leve redove, proveri da li filter pripada u `ON`.
- **Pretpostaviš jedan rezultat po redu leve tabele:** više poklapanja desne strane stvara više redova.
- **Proveravaš opcionalnu kolonu desne strane za nedostatak poklapanja:** koristi desni PK ili drugu kolonu koja je u stvarnom redu obavezna.
- **Koristiš `= NULL`:** koristi `IS NULL` ili `IS NOT NULL`.
- **Zameniš levu i desnu tabelu:** `LEFT JOIN` čuva samo tabelu navedenu levo od operatora.
- **Pogrešno tumačiš `COUNT(*)`:** red bez poklapanja i dalje daje jedan rezultat; za broj poklopljenih redova broji nenulti desni PK.
- **Ignorišeš duplikate nastale spajanjem:** utvrdi da li ti treba jedan red po paru, po desnom redu ili po grupi pre nego što dodaješ `DISTINCT` ili agregaciju.

## Vežbe

1. Pokreni osnovni `artists LEFT JOIN albums` upit i pronađi izvođača sa više albuma. Objasni zašto se njegovo ime ponavlja.
2. Pronađi izvođače bez albuma pomoću `WHERE al.AlbumId IS NULL`. Proveri da je rezultat 71 u priloženoj bazi.
3. Uporedi `COUNT(*)`, `COUNT(al.AlbumId)` i `COUNT(DISTINCT ar.ArtistId)` nad celim spojem. Objasni rezultate `418`, `347` i `275`.
4. Sortiraj po `al.AlbumId` rastuće. Da li se izvođači bez albuma filtriraju ili samo pomeraju na početak?
5. Premesti uslov `al.Title LIKE 'A%'` iz `ON` u `WHERE`. Uporedi da li se izvođači bez odgovarajućeg albuma zadržavaju.
6. Obrni redosled tabela i objasni koji skup redova se sada garantovano čuva.
7. Uporedi `LEFT JOIN` i `INNER JOIN`. Koji izvođači nedostaju iz rezultata `INNER JOIN`-a?

## Provera razumevanja

1. Koja je razlika između leve i desne tabele u `LEFT JOIN` upitu?
2. Šta se upisuje u kolone desne tabele kada nema poklapanja?
3. Zašto `ORDER BY al.AlbumId` ne izdvaja izvođače bez albuma?
4. Koji uslov vraća samo izvođače bez albuma i zašto je `al.AlbumId` dobar izbor za proveru?
5. Zašto se isti izvođač pojavljuje više puta u spoju sa više albuma?
6. Kako se `COUNT(*)` razlikuje od `COUNT(al.AlbumId)` za izvođača bez albuma?
7. Kako filter u `ON` može da sačuva sve izvođače, dok isti filter u `WHERE` neke uklanja?
8. Šta se menja ako zameniš redosled tabela oko `LEFT JOIN`?
9. Kada je `INNER JOIN` prikladniji od `LEFT JOIN`?
10. Zašto `= NULL` nije ispravna provera za nedostajuće poklapanje?

## Izvori za dalje čitanje

- [SQLite: SELECT — JOIN syntax and processing](https://www.sqlite.org/lang_select.html)
- [SQLAlchemy 2.0: Using SELECT Statements — Joins](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#explicit-from-clauses-and-joins)
