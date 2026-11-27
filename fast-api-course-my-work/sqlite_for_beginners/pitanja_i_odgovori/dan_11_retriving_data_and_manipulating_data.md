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

### Pitanje 7 — Kako obrisati sve tabele iz `sandbox.db` u SQLite CLI-ju?

**Odgovor:** `DELETE FROM tabela;` briše redove, ali ostavlja tabelu i njenu strukturu. Za uklanjanje same tabele i svih njenih podataka koristi se `DROP TABLE`.

U proveri tekuće `sandbox.db` kopije pronađene su dve korisničke tabele: `reading_notes` i `user`. Njihovo postojanje možeš proveriti u SQLite CLI-ju pomoću `.tables` ili `PRAGMA table_list;`. Imena se mogu razlikovati ako si u međuvremenu dodao ili uklonio tabele.

Ako CLI još nije otvoren, iz korena repozitorijuma otvori **upravo sandbox bazu**, bez opcije `-readonly`:

```bash
sqlite3 fast-api-course-my-work/sqlite_for_beginners/playground/databases/sandbox.db
```

U SQLite CLI promptu prvo proveri aktivnu bazu i tabele:

```text
.databases
.tables
```

Proveri da putanja pod `main` zaista pokazuje na `sandbox.db`, a ne na Chinook ili bazu aplikacije. Brisanje tabele uklanja njene podatke i strukturu, zajedno sa indeksima i triggerima koji pripadaju toj tabeli. Napravi rezervnu kopiju ako ti podaci mogu zatrebati.

Za trenutno zatečene dve tabele unesi:

```sql
BEGIN;
DROP TABLE main.reading_notes;
DROP TABLE main."user";
```

Zatim proveri `.tables`. Ako želiš da poništiš promene pre potvrde, unesi `ROLLBACK;`. Ako si siguran da želiš da ih trajno ukloniš, unesi `COMMIT;` i ponovo proveri `.tables`. Posle `COMMIT`-a `ROLLBACK` više ne može da vrati tabele.

Ovaj primer uklanja navedene dve tabele, ne automatski sve buduće tabele. SQLite nema opštu CLI komandu `.drop-all-tables`; za druge tabele potrebne su odgovarajuće `DROP TABLE` naredbe. Sistemske tabele čija imena počinju sa `sqlite_` nisu obične korisničke tabele i ne treba ih ručno brisati. Pogledi su zasebni objekti i uklanjaju se sa `DROP VIEW`, ako to zaista želiš.

Ako postoje strani ključevi, zavisnosti ili virtuelne tabele, redosled i postupak mogu biti drugačiji; pregledaj šemu i zavisnosti pre brisanja. U ovoj proveri nijedna od navedene dve tabele nema definisan strani ključ.

---

### Pitanje 8 — Kako `ASC` i `DESC` sortiraju tekst i koja Python funkcija pokazuje kod znaka?

**Odgovor:** `ASC` znači rastući, a `DESC` opadajući redosled. Kod teksta „manje“ i „veće“ određuju pravila poređenja, odnosno **kolacija**. U SQLite-u, ako izraz ili kolona ne određuju drugačiju kolaciju, koristi se `BINARY`: za sledeća ASCII slova velika dolaze pre malih.

```sql
WITH slova(vrednost) AS (
    VALUES ('a'), ('Z'), ('A'), ('z')
)
SELECT vrednost
FROM slova
ORDER BY vrednost COLLATE BINARY ASC;
```

Rezultat je `A`, `Z`, `a`, `z`. Ako u istom upitu promeniš `ASC` u `DESC`, redosled je `z`, `a`, `Z`, `A`. `ASC` je podrazumevan kada ne navedeš smer.

Python poredi stringove leksikografski, po Unicode kodnim tačkama: poredi znakove sleva nadesno, do prve razlike; ako je jedan string prefiks drugog, kraći ide prvi. Funkcija koju tražiš verovatno je **`ord()`**, koja vraća kodnu tačku jednog znaka; `chr()` vraća znak za zadatu kodnu tačku:

```python
print(ord("A"), ord("Z"), ord("a"), ord("z"))
# 65 90 97 122

print(chr(65))  # A
print(sorted(["a", "Z", "A", "z"]))
# ['A', 'Z', 'a', 'z']
print(sorted(["a", "Z", "A", "z"], reverse=True))
# ['z', 'a', 'Z', 'A']
```

Na primer, `"Bob" < "alice"` je `True` jer se najpre porede `B` i `a`, a `ord("B")` je manji od `ord("a")`. `"ab" < "abc"` je takođe `True`: prvi string je prefiks drugog.

SQLite nudi i `unicode()` za kodnu tačku **prvog** znaka stringa:

```sql
SELECT unicode('A'), unicode('Z'), unicode('a'), unicode('z');
-- 65 | 90 | 97 | 122
```

Rezultat `ord()` pomaže da razumeš redosled ovog ASCII primera, ali Python i SQLite ne moraju uvek dati isti redosled: SQLite `BINARY` poredi prema bajtovima, dok Python poredi Unicode kodne tačke; SQLite može koristiti i drugačiju kolaciju.

Za sortiranje koje zanemaruje veličinu ASCII slova koristi `COLLATE NOCASE`:

```sql
SELECT TrackId, Name
FROM tracks
ORDER BY Name COLLATE NOCASE ASC, TrackId ASC
LIMIT 10;
```

Ovde `NOCASE` tretira ASCII velika i mala slova kao jednaka pri poređenju; `TrackId` daje stabilan redosled kada su nazivi jednaki prema toj kolaciji. `NOCASE` nije potpuna Unicode kolacija ni srpski rečnički redosled. `NULL` je takođe poseban slučaj: SQLite ga podrazumevano stavlja na početak za `ASC`, a na kraj za `DESC`.

Više o sortiranju i `NULLS FIRST`/`NULLS LAST` nalazi se u [lekciji `ORDER BY`](../02_retriving_data_and_manipulating_data/04_sorting_data_using_order_by_clause.md).

---

### Pitanje 9 — Da li svaka kolacija poredi Unicode kodne tačke?

**Odgovor:** Ne nužno. **Unicode kodna tačka** je broj dodeljen znaku, dok je **kolacija** pravilo koje određuje kako se dve tekstualne vrednosti porede. Pravilo može uzeti u obzir i druga svojstva, kao što su velika i mala slova ili jezička pravila.

U Pythonu se stringovi podrazumevano porede leksikografski prema Unicode kodnim tačkama. U SQLite-u ugrađena kolacija `BINARY` poredi tekst po bajtovima, dok `NOCASE` zanemaruje razliku između velikih i malih ASCII slova. To nisu ista pravila:

```sql
SELECT
    unicode('B') AS kod_B,
    unicode('a') AS kod_a,
    'B' < 'a' COLLATE BINARY AS binary_poredjenje,
    'B' < 'a' COLLATE NOCASE AS nocase_poredjenje;
```

Rezultat je `66 | 97 | 1 | 0`, gde `1` znači tačno, a `0` netačno. Uz `BINARY`, `B` dolazi pre `a`. Uz `NOCASE`, porede se kao `b` i `a`, pa `B` ne dolazi pre `a`. Funkcija `unicode()` ovde samo prikazuje kodne tačke; ne određuje automatski koju kolaciju upit koristi.

Dakle, za prethodni ASCII primer vrednosti iz `ord()` korisne su za razumevanje rezultata `BINARY` sortiranja, ali nemoj ih smatrati opštim pravilom za sve kolacije. `ASC` i `DESC` određuju smer sortiranja, a kolacija određuje redosled tekstualnih vrednosti.

---

### Pitanje 10 — Kako da proverim koliko bajtova zauzima znak?

Broj bajtova zavisi od **kodiranja**: isto slovo može imati različit broj bajtova u UTF-8 i UTF-16. Najpre odredi kodiranje koje želiš da ispitaš.

U Pythonu eksplicitno kodiraj string u UTF-8, pa izmeri rezultat:

```python
for znak in ["A", "č", "Ж", "😀"]:
    bajtovi = znak.encode("utf-8")
    print(znak, len(bajtovi), bajtovi.hex().upper())
```

| Znak | Broj bajtova u UTF-8 | Bajtovi u heksadecimalnom zapisu |
| --- | ---: | --- |
| `A` | 1 | `41` |
| `č` | 2 | `C4 8D` |
| `Ж` | 2 | `D0 96` |
| `😀` | 4 | `F0 9F 98 80` |

Python ispisuje heksadecimalne cifre spojeno, na primer `C48D`; u tabeli su bajtovi razdvojeni radi čitljivosti. Jedan bajt predstavljaju dve heksadecimalne cifre.

`len("č")` je `1`, jer meri broj kodnih tačaka u Python stringu, dok je `len("č".encode("utf-8"))` `2`, jer meri broj bajtova nakon kodiranja. `ord("č")` vraća kodnu tačku `269`, ne broj bajtova. Jedan vizuelni znak ponekad može biti zapisan pomoću više kodnih tačaka, pa ni broj vidljivih znakova ne mora biti isti kao `len()` stringa.

U SQLite CLI-ju prvo proveri kodiranje baze:

```sql
PRAGMA encoding;
```

Trenutna Chinook kopija koristi `UTF-8`. Zatim možeš proveriti znak:

```sql
SELECT
    unicode('č') AS kodna_tacka,
    length('č') AS broj_kodnih_tacaka,
    length(CAST('č' AS BLOB)) AS broj_bajtova,
    hex(CAST('č' AS BLOB)) AS bajtovi_hex;
```

U UTF-8 bazi rezultat je `269 | 1 | 2 | C48D`. `length()` nad tekstom broji kodne tačke do prvog NUL znaka, dok `length()` nad BLOB vrednošću broji bajtove. Pretvaranje teksta u BLOB koristi kodiranje baze, pa za drugačije kodiranje ne pretpostavljaj iste bajtove ili isti broj.

**Važno za sortiranje:** `BINARY` ne sortira po broju bajtova u tekstu, već poredi njihove vrednosti prema pravilima te kolacije. Na primer, `z` u UTF-8 ima bajt `7A`, a `č` počinje bajtom `C4`; uz `BINARY ASC` zato `z` dolazi pre `č`. Broj bajtova nije isto što i redosled teksta.

---

### Pitanje 11 — Da li su odgovori u proveri razumevanja za `ORDER BY` ispravni?

U [proveri razumevanja lekcije `ORDER BY`](../02_retriving_data_and_manipulating_data/04_sorting_data_using_order_by_clause.md#provera-razumevanja) odgovori **1, 2 i 3 su ispravni**: bez `ORDER BY` nema garantovanog redosleda, podrazumevani smer je `ASC`, a `ORDER BY AlbumId ASC, TrackId DESC` najpre sortira po albumu rastuće, pa unutar istog albuma po numeri opadajuće.

Preostale odgovore treba precizirati ili ispraviti:

4. **Kolona van `SELECT` liste:** u običnom jednostavnom upitu moguće je sortirati po koloni izvora koja nije prikazana. Međutim, tvrdnja da se to može raditi sa **bilo kojom** kolonom u svakom SQL upitu je preširoka: složeni upiti, na primer `UNION`, imaju dodatna pravila za izraze u `ORDER BY`.
5. **Jedinstveni završni ključ:** to je dobar način da se razreše veze između redova koji su jednaki po prethodnim kriterijumima, ako taj ključ zaista jednoznačno razlikuje rezultatne redove. Ne garantuje nepromenjene stranice ako se podaci menjaju između zahteva; nakon `JOIN`-a ključ jedne tabele može se ponavljati u više rezultatnih redova.
6. **Trajni redosled i `NULLS FIRST/LAST`:** `ORDER BY` uređuje rezultat upita, ne uspostavlja garantovan trajni redosled redova u tabeli. Ni `CREATE TABLE ... AS SELECT ... ORDER BY ...` ne garantuje redosled budućih upita bez sopstvenog `ORDER BY`. SQLite podržava `NULLS FIRST` i `NULLS LAST` od verzije **3.30.0**; dodatni izrazi sa `IS NULL` jesu moguća alternativa, ali nisu obavezni u novijim verzijama.
7. **Položaj `NULL`:** podrazumevano se u SQLite-u `NULL` prikazuje **prvi za `ASC`**, a **poslednji za `DESC`**, ne kao najveća vrednost za rastuće sortiranje. Prazan tekst `''` nije `NULL`: kod `BINARY` poređenja dolazi pre nepraznog teksta, ali tekstualni redosled uopšte zavisi od kolacije.

Proveri u SQLite CLI-ju bez menjanja baze:

```sql
WITH vrednosti(v) AS (VALUES (NULL), (''), ('A'))
SELECT quote(v) AS vrednost
FROM vrednosti
ORDER BY v ASC;
```

Očekivani redosled je `NULL`, `''`, `'A'`. Sa `ORDER BY v DESC` je `'A'`, `''`, `NULL`; sa `ORDER BY v ASC NULLS LAST` je `''`, `'A'`, `NULL`. Funkcija `quote()` čini prazan tekst i `NULL` lakše razlikovanim u prikazu.

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
