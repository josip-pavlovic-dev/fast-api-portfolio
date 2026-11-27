# Dan 11 — Čitanje i manipulisanje podacima

## Cilj dana

Danas ponavljamo čitanje rezultata u SQLite CLI-ju i razliku između običnog `SELECT` upita i `SELECT DISTINCT`. Važno je da razlikuješ prikaz reda po redu iz tabele od prikaza jedinstvenih vrednosti i da znaš kako da očistiš ekran terminala dok radiš u SQLite CLI-ju.

Ovaj dnevnik prati [oblast 02 — čitanje i manipulisanje podacima](../02_retriving_data_and_manipulating_data/README.md) i dopunjuje [prethodni vodič za vežbe](./dan_06_retriving_data_and_manipulating_data_vezbe.md). Radne upite čuvaj u odgovarajućim `.sql` fajlovima u [playground/sql/](../playground/sql/).

---

## 1. Bezbedan način rada

Primeri nad `albums` koriste lokalnu Chinook kopiju. Otvori je iz korena repozitorijuma u read-only režimu:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Komande koje počinju tačkom, kao što su `.shell` i `.read`, unose se u SQLite CLI prompt, a ne u Bash prompt. Ako nisi siguran u dostupne komande, prikaži pomoć pomoću `.help`.

---

---

## 2. Pitanja i odgovori

### Pitanje 1 — Da li se u SQLite CLI-ju može očistiti sadržaj terminala?

**Odgovor:** Da. Na Linuxu, uključujući WSL, u SQLite CLI promptu unesi:

```text
.shell clear
```

SQLite CLI pokreće `clear` kao komandu sistemske ljuske. Ovo očisti samo trenutno vidljiv prikaz terminala — **ne briše bazu, istoriju upita niti rezultate sačuvane u fajlu**.

U mnogim terminalima radi i prečica `Ctrl+k` i `Ctrl+L`. To je prečica terminala ili readline-a, a ne SQL naredba; ponašanje može zavisiti od terminala i podešavanja.

`sqlite3` pokrenut u `bash` terminalu poštuje prečicu `Ctrl+k` **koja inače čisti ekran terminala i kada nije u SQLite CLI-ju**. Na Windows komandnom promptu odgovarajuća komanda je `cls`, dok je u WSL-u uobičajeno `clear`.

Ako `.shell clear` ne radi, proveri da li je komanda `clear` dostupna u okruženju i da li SQLite CLI radi u interaktivnom terminalu. Komanda zavisi od operativnog sistema i okruženja.

---

### Pitanje 2 — Zašto `SELECT ArtistId FROM albums;` i `SELECT DISTINCT ArtistId FROM albums;` ne vraćaju isti broj redova?

**Odgovor:** U trenutnoj Chinook kopiji **ne vraćaju isti broj redova**:

```sql
SELECT ArtistId
FROM albums;
```

Vraća **347 redova**, po jedan za svaki album.

```sql
SELECT DISTINCT ArtistId
FROM albums;
```

Vraća **204 reda**, po jedan za svakog različitog izvođača koji ima album. Jedan izvođač može imati više albuma, pa se njegov `ArtistId` ponavlja u prvom upitu. `DISTINCT` uklanja te ponovljene vrednosti iz rezultata; ne menja podatke u tabeli.

Brojeve možeš proveriti jednim upitom:

```sql
SELECT
    COUNT(*) AS album_rows,
    COUNT(DISTINCT ArtistId) AS distinct_artist_ids
FROM albums;
```

Očekivani rezultat u ovoj kopiji je:

| album_rows | distinct_artist_ids |
| ---------: | ------------------: |
|        347 |                 204 |

Prethodno objašnjenje u lekciji tvrdilo je da su svi `ArtistId`-ovi jedinstveni i da zato upiti vraćaju isti broj redova. To nije tačno za ovu tabelu: `albums.ArtistId` povezuje album sa izvođačem i može se ponoviti za više albuma istog izvođača. Objašnjenje je ispravljeno u [lekciji `SELECT`](../02_retriving_data_and_manipulating_data/01_sqlite_select_statement.md).

---

### Pitanje 3 — Kada bi `SELECT` i `SELECT DISTINCT` mogli da vrate isti broj redova?

**Odgovor:** Kada se vrednost izabrane kolone već ne ponavlja u ulaznim redovima, `DISTINCT` nema duplikate koje bi uklonio, pa broj redova može ostati isti. To nije slučaj sa `albums.ArtistId` u Chinook kopiji.

Imaj na umu da isti broj redova ne mora značiti i isti **redosled**. Bez `ORDER BY`, SQL ne garantuje redosled izlaznih redova — ni za običan `SELECT`, ni za `SELECT DISTINCT`.

---

### Pitanje 4 — Na koje kolone se odnosi `DISTINCT` kada izaberem više od jedne?

**Odgovor:** `DISTINCT` poredi celu kombinaciju izabranih kolona. Na primer:

```sql
SELECT DISTINCT ArtistId, Title
FROM albums;
```

Uklanja samo ponovljene parove `(ArtistId, Title)`. Ne znači „izaberi jedinstven `ArtistId`, pa proizvoljno prikaži jedan naslov“. Ako se isti `ArtistId` pojavi uz različite naslove, svaki par ostaje u rezultatu. Ako ti trebaju samo izvođači, izaberi samo `ArtistId`.

---

### Pitanje 5 — Kako se `NULL` ponaša u `SELECT DISTINCT` u odnosu na `COUNT(DISTINCT ...)`?

**Odgovor:** `SELECT DISTINCT kolona` zadržava najviše jedan red sa `NULL`, jer uklanja ponovljene vrednosti u rezultatu. `COUNT(DISTINCT kolona)` broji samo različite vrednosti koje nisu `NULL`, pa `NULL` ne doprinosi broju.

U trenutnoj Chinook kopiji nema nijednog `NULL` u `albums.ArtistId`, zato je broj redova koji vraća `SELECT DISTINCT ArtistId` jednak vrednosti `COUNT(DISTINCT ArtistId)`, odnosno 204. U drugim tabelama ili podacima proveri `NULL` posebno:

```sql
SELECT
    COUNT(*) AS album_rows,
    COUNT(ArtistId) AS non_null_artist_ids,
    COUNT(DISTINCT ArtistId) AS distinct_non_null_artist_ids
FROM albums;
```

---

### Pitanje 6 — Da li su nazivi kolona u SQLite-u osetljivi na velika i mala slova?

**Odgovor:** SQLite ne razlikuje velika i mala ASCII slova u nazivima identifikatora, kao što su imena kolona i tabela. To nije posebno pravilo za nazive od jedne reči: `Name`, `name` i `NAME` upućuju na istu kolonu bez obzira na to da li je ime kratko, dugo ili navodnicima ograničeno.

Zato sledeći izbori čitaju istu kolonu `tracks.Name`:

```sql
SELECT Name, name, NAME, "Name"
FROM tracks
ORDER BY TrackId
LIMIT 1;
```

U rezultatima ćeš videti istu vrednost u svakoj od četiri kolone. SQLite CLI može prikazati `Name` kao naziv zaglavlja i kada si upisao `name`, jer se kolona u šemi zove `Name`. Ako želiš drugačije zaglavlje rezultata, daj izrazu alias, na primer `name AS lowercase_name`.

Dupli navodnici označavaju identifikator — korisni su kada naziv sadrži razmake ili je rezervisana reč — ali ne čine poređenje naziva osetljivim na velika i mala slova. To je nezavisno od vrednosti tekstualnih podataka: poređenje stringova, poput `'Rock' = 'rock'`, po podrazumevanoj `BINARY` kolaciji je osetljivo na velika i mala slova. Kolacija `NOCASE` menja to ponašanje za ASCII slova:

```sql
SELECT
    'Rock' = 'rock' AS binary_comparison,
    'Rock' COLLATE NOCASE = 'rock' AS nocase_comparison;
```

Rezultat je `0 | 1`. Dakle, razlikuj **ime kolone** (`Name`) od **vrednosti u koloni** (`'Rock'`): pravilo koje važi za identifikatore ne znači da su tekstualni podaci automatski neosetljivi na veličinu slova.

---

## 3. Kratka provera razumevanja

1. **Šta radi `.shell clear` u SQLite CLI-ju?** Pokreće sistemsku komandu `clear`, koja čisti vidljivi terminalski prikaz; ne menja bazu niti briše istoriju upita.

- `.shell clear` je SQLite CLI dot-komanda koja čisti terminalski prikaz. Može se koristiti kada želimo da osvežimo ekran i uklonimo prethodne rezultate upita iz vidljivog dela terminala. Ova komanda je korisna kada radimo sa velikim brojem upita i želimo čist prikaz za nove rezultate.

2. **Da li je `.shell clear` SQL naredba?**

- **Ne**. To je SQLite CLI dot-komanda. Ne radi ništa sa samom bazom podataka, već samo utiče na prikaz u terminalu.

3. **Koliko redova vraća običan `SELECT ArtistId FROM albums` u trenutnoj kopiji?**

- **347**, po jedan za svaki album. To uključuje sve redove, bez obzira na to da li se `ArtistId` ponavlja ili ne.

4. **Koliko različitih nenultih `ArtistId` vrednosti ima?**

- **204**. To je broj različitih izvođača koji imaju albume u tabeli `albums`, bez obzira na to koliko albuma svaki izvođač ima.

5. **Zašto se `ArtistId` ponavlja u `albums`?**

- **Jedan izvođač može imati više albuma**, pa se `ArtistId` ponavlja u tabeli `albums`.

6. **Da li `DISTINCT` menja tabelu?**

- **Ne menja tabelu**; menja samo redove vraćene u rezultatu upita. Dakle, `DISTINCT` utiče samo na prikaz rezultata, a ne na stvarne podatke u bazi. Ako želimo da trajno uklonimo duplikate, moramo koristiti `DELETE` sa odgovarajućim uslovom ili kreirati novu tabelu sa jedinstvenim redovima.

7. **Šta poredi `SELECT DISTINCT ArtistId, Title`?**

- Poredi cele kombinacije vrednosti `ArtistId` i `Title`, tako da uklanja samo redove koji imaju identične vrednosti u obe kolone. Redovi koji dele isti `ArtistId`, ali imaju različite `Title` vrednosti, neće biti uklonjeni.

8. **Da li je redosled rezultata zagarantovan bez `ORDER BY`?**

- **Ne**. Bez `ORDER BY`, redosled rezultata nije garantovan i može se razlikovati između različitih izvršenja upita. Ako želimo da dobijemo rezultate u određenom redosledu, uvek treba koristiti `ORDER BY`.

9. **Da li `COUNT(DISTINCT ArtistId)` broji `NULL`?**

- **Ne**. `COUNT(DISTINCT ArtistId)` broji samo različite nenulte vrednosti `ArtistId`. Ako postoji `NULL` vrednost u koloni `ArtistId`, ona se neće uračunati u rezultat. Dakle, `NULL` vrednosti se ignorišu prilikom brojanja različitih vrednosti.

10. **Da li je `Name` druga kolona od `name` u SQLite-u?**

- **Ne**. Nazivi identifikatora se ne razlikuju po velikim i malim ASCII slovima. Poređenje tekstualnih vrednosti je zasebno i zavisi od kolacije.

---

## 4. Vežba

U `read-only` Chinook konekciji pokreni:

```sql
SELECT ArtistId
FROM albums
ORDER BY ArtistId;

SELECT DISTINCT ArtistId
FROM albums
ORDER BY ArtistId;
```

**Uporedi broj prikazanih redova i uoči izvođače čiji se ID ponavlja u prvom rezultatu**. Zatim proveri da li višekolonski `DISTINCT` daje isti broj redova:

```sql
SELECT DISTINCT ArtistId, Title
FROM albums
ORDER BY ArtistId, Title;
```

Objasni zašto ovaj poslednji upit uklanja samo identične parove, a ne sve redove koji dele isti `ArtistId`.

**Odgovor:** Poslednji upit uklanja samo identične parove `ArtistId` i `Title`, jer `DISTINCT` funkcioniše na kombinaciji svih kolona navedenih u upitu. Ako dva reda imaju isti `ArtistId`, ali različite `Title` vrednosti, oni se smatraju različitim i neće biti uklonjeni. Dakle, `DISTINCT` ne uklanja sve redove sa istim `ArtistId`, već samo one koji su potpuno identični u svim navedenim kolonama.

---
