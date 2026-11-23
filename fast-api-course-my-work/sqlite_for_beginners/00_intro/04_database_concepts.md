# 04 — Osnovni pojmovi o bazama podataka

## Cilj lekcije

U ovoj lekciji upoznaćeš pojmove baza podataka, tabele, reda, kolone, relacionog modela i sistema za upravljanje bazom podataka. Kroz primere ćeš naučiti kako se podaci predstavljaju u tabelama i zašto ponovljena vrednost u dve tabele sama po sebi još ne uspostavlja relaciju.

> **Napomena o ispravkama:** Vežba 1 koristi pojednostavljen model sa jednom glavnom bojom, a Vežba 2 zaseban model sa više boja. U Vežbi 2 uklonjeni su duplirani indeksi i objašnjena su ograničenja ključeva, naziva i obavezne boje. Ova dva modela nisu ista šema.

---

## Baza podataka i sistem koji njome upravlja

**Baza podataka** je organizovana kolekcija podataka i njihove strukture. Pored redova u tabelama, baza može da sadrži definicije tabela, indekse, ograničenja, poglede i druge objekte.

**Sistem za upravljanje bazom podataka** (DBMS — Database Management System) je softver koji omogućava da bazu napraviš, čitaš, menjaš i kontrolišeš pristup njenim podacima. **Relacioni DBMS** (RDBMS) organizuje podatke u relacije, koje se u praksi predstavljaju tabelama, kolonama, redovima i pravilima za povezivanje podataka.

| Pojam         | Značenje                                          | Primer iz ovog kursa               |
| ------------- | ------------------------------------------------- | ---------------------------------- |
| Baza podataka | Podaci zajedno sa njihovom strukturom i pravilima | Fajl `chinook.db`                  |
| DBMS / RDBMS  | Softver koji upravlja bazom i izvršava upite      | SQLite                             |
| Tabela        | Strukturisana celina sličnih zapisa               | `artists` ili `albums`             |
| SQL           | Jezik za definisanje, čitanje i menjanje podataka | `SELECT`, `CREATE TABLE`, `INSERT` |

Drugi poznati relacioni sistemi uključuju PostgreSQL, MySQL/MariaDB, Microsoft SQL Server i Oracle Database. SQLite je takođe relacioni DBMS, ali se u tipičnoj upotrebi ugrađuje u aplikaciju umesto da radi kao zaseban server.

---

## Tabela, red i kolona

Tabela opisuje jednu vrstu podataka, kao što su izvođači ili albumi. **Kolona** predstavlja svojstvo svakog zapisa, a **red** predstavlja jedan konkretan zapis. Izrazi **red** i **zapis** se često koriste kao sinonimi.

Primer tabele `fruits`:

| FruitId | Name  | Color |
| ------: | ----- | ----- |
|       1 | Apple | Green |
|       2 | Kiwi  | Brown |

U ovom primeru:

- `FruitId`, `Name` i `Color` su kolone.
- Red sa vrednostima `2`, `Kiwi` i `Brown` je jedan zapis o kiviju.
- Svaka vrednost u redu pripada odgovarajućoj koloni.

Baza nije Excel tabela sa podrazumevanim redosledom zapisa. U relacionoj bazi ne treba pretpostaviti da će redovi biti vraćeni redosledom kojim su dodati. Ako je redosled rezultata važan, upit mora izričito da ga zatraži, na primer pomoću `ORDER BY`; to ćemo obraditi u kasnijim lekcijama.

---

## Šta čini bazu relacionom

U transkriptu se prikazuju tabele `fruits` i `vegetables`, obe sa kolonom `Color`. To što obe tabele sadrže tekstualnu vrednost `Green` ili `Brown` **ne uspostavlja samo po sebi vezu između tabela**. Vrednosti mogu slučajno da se poklapaju, mogu biti različito napisane ili se mogu promeniti samo u jednoj tabeli.

SQL upit može da poredi dve tekstualne kolone i pronađe podudarne vrednosti, ali takvo poređenje samo po sebi ne garantuje integritet niti kaže da baza te vrednosti smatra zvaničnom relacijom.

---

### Primer: iste vrednosti, ali bez deklarisane relacije

| `fruits` |       |       | `vegetables` |          |       |
| -------- | ----- | ----- | ------------ | -------- | ----- |
| FruitId  | Name  | Color | VegetableId  | Name     | Color |
| 1        | Apple | Green | 1            | Cucumber | Green |
| 2        | Kiwi  | Brown | 2            | Potato   | Brown |

Kolona `Color` se ponavlja u obe tabele, ali nema stranog ključa koji bi povezao redove sa jednim zajedničkim zapisom boje. Ovaj prikaz je koristan da prepoznaš slične vrednosti, ali nije sam po sebi model referencijalnog integriteta.

---

## Eksplicitna relacija preko ključeva: jedna glavna boja

Ako boja predstavlja podatak koji se deli između voća i povrća, možeš je predstaviti posebnom tabelom `colors`. U tabelama `fruits` i `vegetables` čuva se `ColorId`, koji referencira primarni ključ tabele `colors`.

Ovo je **pojednostavljen primer jedne obavezne glavne boje**, a ne tvrdnja da svako voće ili povrće u stvarnosti ima samo jednu boju. Ako želiš da beležiš više boja istog zapisa, potreban je drugačiji model, prikazan u Vežbi 2.

Tabela `colors` čuva po jedan zapis za svaku boju:

| ColorId (PK) | Name  |
| -----------: | ----- |
|            1 | Green |
|            2 | Brown |
|            3 | Red   |

Tabela `fruits` čuva ključ boje umesto ponavljanja naziva boje:

| FruitId (PK) | Name  | ColorId (FK) |
| -----------: | ----- | -----------: |
|            1 | Apple |            1 |
|            2 | Kiwi  |            2 |

Isto važi i za tabelu `vegetables`:

| VegetableId (PK) | Name     | ColorId (FK) |
| ---------------: | -------- | -----------: |
|                1 | Cucumber |            1 |
|                2 | Potato   |            2 |

Sada `fruits.ColorId` i `vegetables.ColorId` imaju jasno definisano značenje: oba referenciraju `colors.ColorId`. Po želji, možeš postaviti i ograničenje `UNIQUE` na `colors.Name` da sprečiš dupliranje istog naziva boje.

```mermaid
erDiagram
    COLORS ||..o{ FRUITS : "boja"
    COLORS ||..o{ VEGETABLES : "boja"

    COLORS {
        int ColorId PK
        string Name
    }
    FRUITS {
        int FruitId PK
        string Name
        int ColorId FK
    }
    VEGETABLES {
        int VegetableId PK
        string Name
        int ColorId FK
    }
```

U ovom modelu jedan zapis u `colors` može biti povezan sa više zapisa u `fruits` ili `vegetables`. Svako voće i svako povrće upućuje na jedan zapis boje. `PK` znači **primarni ključ**, `FK` **strani ključ**, a `UK` **jedinstven ključ**.

---

## Primarni i strani ključevi

**Primarni ključ** (Primary Key, PK) služi za jednoznačnu identifikaciju reda. **Strani ključ** (Foreign Key, FK) upućuje na primarni ili odgovarajući jedinstveni ključ druge ili iste tabele. SQLite ima posebne slučajeve u kojima neke deklaracije PK-a dozvoljavaju `NULL`; za konkretan primer vidi Vežbu 2.

| Ključ          | Uloga                                                   | Primer                                          |
| -------------- | ------------------------------------------------------- | ----------------------------------------------- |
| Primarni ključ | Jedinstveno identifikuje zapis u svojoj tabeli          | `artists.ArtistId`                              |
| Strani ključ   | Povezuje zapis sa odgovarajućim zapisom u drugoj tabeli | `albums.ArtistId` upućuje na `artists.ArtistId` |

U Chinook bazi `albums.ArtistId` povezuje album sa njegovim izvođačem. Relacija ne nastaje samo zato što se broj `ArtistId` pojavljuje u obe tabele; ona je definisana kao strani ključ u šemi baze.

SQLite ima važnu posebnost: provera stranih ključeva zavisi od podešavanja konekcije (`PRAGMA foreign_keys`). Zato treba razlikovati **deklaraciju ključa u šemi** od toga da li konkretna konekcija trenutno sprovodi proveru. O ovome ćemo više raditi kada budemo pravili šemu i povezivali SQLAlchemy.

---

## Vrste relacija između tabela

| Vrsta relacije          | Primer                            | Tipična realizacija                                |
| ----------------------- | --------------------------------- | -------------------------------------------------- |
| 1:1 (jedan-prema-jedan) | Korisnik ima jedan profil         | Strani ključ uz ograničenje `UNIQUE`               |
| 1:N (jedan-prema-više)  | Jedan izvođač ima više albuma     | Strani ključ se čuva u tabeli na strani „više“     |
| N:M (više-prema-više)   | Više plejlista sadrži više numera | Pomoćna tabela sa stranim ključevima ka obe tabele |

Chinook baza sadrži primere relacija 1:N i N:M:

```mermaid
erDiagram
    ARTISTS ||..o{ ALBUMS : "ima"
    ALBUMS |o..o{ TRACKS : "sadrži"
    CUSTOMERS ||..o{ INVOICES : "dobija"
    INVOICES ||..o{ INVOICE_ITEMS : "sadrži"
    TRACKS ||..o{ INVOICE_ITEMS : "pojavljuje se u"
    PLAYLISTS ||--o{ PLAYLIST_TRACK : "ima stavke"
    TRACKS ||--o{ PLAYLIST_TRACK : "pripada stavkama"
    GENRES |o..o{ TRACKS : "klasifikuje"
    MEDIA_TYPES ||..o{ TRACKS : "određuje format"
    EMPLOYEES |o..o{ CUSTOMERS : "podržava"
    EMPLOYEES |o..o{ EMPLOYEES : "rukovodi"
```

`PLAYLIST_TRACK` je pomoćna tabela za N:M relaciju između `PLAYLISTS` i `TRACKS`. U njoj su `PlaylistId` i `TrackId` zajedno kompozitni primarni ključ, a oba su ujedno i strani ključevi. Svaki red povezuje jednu plejlistu sa jednom numerom.

U dijagramu `|o` sa leve strane linije označava da veza sa te strane može biti prazna ili pokazivati na jedan zapis. Na primer, `tracks.AlbumId` i `tracks.GenreId` mogu biti `NULL` u Chinook bazi. Dijagram je vizuelni sažetak; tačne kolone i ograničenja proveravaju se u šemi baze.

Pogledaj i [ERD.drawio](../chinook/ERD.drawio), koji prikazuje svih 11 tabela i njihove veze prema stvarnoj Chinook šemi.

---

## Relacioni DBMS i primeri

`SQLite`, `PostgreSQL`, `MySQL/MariaDB`, `Microsoft SQL Server` i `Oracle Database` su primeri relacionih sistema za upravljanje bazama. **Razlikuju se po arhitekturi, funkcijama i načinu administracije**, ali svi podržavaju **relacionu** organizaciju podataka i SQL.

| DBMS                 | Uobičajen način korišćenja                            |
| -------------------- | ----------------------------------------------------- |
| SQLite               | Ugrađen u aplikaciju; najčešće radi sa fajlom baze    |
| PostgreSQL           | Klijent-server baza, čest izbor za web aplikacije     |
| MySQL/MariaDB        | Klijent-server sistemi, česti u web aplikacijama      |
| Microsoft SQL Server | Klijent-server sistem u Microsoft ekosistemu          |
| Oracle Database      | Klijent-server sistem za različite poslovne scenarije |

Relaciona baza ne mora da ima najmanje dve tabele. U relacionom modelu izraz **relacija** označava strukturu koja se u praksi predstavlja tabelom, dok **veza između zapisa** označava njihov odnos. Veza se može definisati i unutar iste tabele, pomoću stranog ključa koji upućuje na nju samu.

Primer relacione baze sa jednom tabelom:

```sql
CREATE TABLE artists (
    ArtistId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
);
```

Primer pokazuje jednostavnu tabelu `artists` sa primarnim ključem `ArtistId` i obaveznim poljem `Name`. Ova tabela može postojati samostalno, bez drugih tabela, što je validna relacija u bazi podataka. Kada se kasnije doda tabela `albums` sa stranim ključem `ArtistId`, uspostavlja se veza između albuma i umetnika, čime se demonstrira koncept relacija između tabela.

Primer relacione baze sa dve tabele i vezom između njih:

```sql
CREATE TABLE artists (
    ArtistId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
);

CREATE TABLE albums (
    AlbumId INTEGER PRIMARY KEY,
    Title TEXT NOT NULL,
    ArtistId INTEGER NOT NULL,
    FOREIGN KEY (ArtistId) REFERENCES artists(ArtistId)
);
```

Primer pokazuje kako se uspostavlja veza između tabela `artists` i `albums` preko stranog ključa `ArtistId`. `NOT NULL` zahteva upisan ID, a uključen FK sprečava da taj ID upućuje na nepostojećeg umetnika. U SQLite-u proveru uključi sa `PRAGMA foreign_keys = ON;` za svaku konekciju, pre početka transakcije. Sama veza ne garantuje efikasnost svih upita niti celokupnu konzistentnost podataka.

---

## Kako se pojmovi preslikavaju na FastAPI i SQLAlchemy

Tabela, `SQLAlchemy model`, `Pydantic šema` i `API odgovor` su povezani, ali **nisu isti objekat**. Na primer, `SQLAlchemy model` opisuje rad sa bazom, dok `Pydantic šema` opisuje strukturu podataka koju `endpoint` prima ili vraća.

| Koncept baze | Uobičajen pojam u SQLAlchemy-ju | Značenje u FastAPI aplikaciji                            |
| ------------ | ------------------------------- | -------------------------------------------------------- |
| Tabela       | `ORM model` ili `Table` objekat | Trajno **skladištenje** tipova podataka                  |
| Red          | `ORM instanca`                  | Jedan **konkretan zapis**, npr. jedan album              |
| Kolona       | Mapirani atribut                | Jedno polje (**atribut**) zapisa                         |
| Strani ključ | `FK kolona` i `ORM relacija`    | **Veza** između povezanih **zapisa**                     |
| API šema     | Nema nužno direktnu DB tabelu   | Validacija `request`/`response` podataka kroz `Pydantic` |

Tipičan tok jednog zahteva izgleda ovako:

```mermaid
flowchart LR
    request["HTTP zahtev"] --> validation["Pydantic validacija"]
    validation --> endpoint["FastAPI endpoint"]
    endpoint --> orm["SQLAlchemy model / upit"]
    orm --> driver["SQLite drajver"]
    driver --> row[("Red u SQLite tabeli")]
    row --> result["SQLAlchemy rezultat"]
    result --> response["Pydantic response"]
```

Ovaj prikaz je konceptualan: stvarni `endpoint` može imati dodatne slojeve, a ne mora svaki Pydantic model da odgovara jednoj tabeli. Važno je da validacija API podataka, pristup bazi i pravila integriteta imaju jasno razdvojene odgovornosti.

---

## Provera razumevanja

1. Koja je razlika između **baze podataka** i **sistema koji njome upravlja**?

- **Baza podataka** je skup organizovanih podataka, dok **DBMS** (Database Management System) je **softver** koji omogućava **upravljanje podacima** kroz `CRUD` operacije: `Create`, `Read`, `Update`, `Delete` i obezbeđuje integritet, sigurnost i efikasnost pristupa tim podacima kroz definisane strukture:
  1. Tipovi podataka (**tabele i kolone**)
  2. Relacije (**veze između tabela preko primarnih i stranih ključeva**)
  3. Pravila integriteta(**constraints**, pravila koja osiguravaju konzistentnost i validnost podataka).

2. Kako razlikuješ **red** od **kolone** u tabeli?

- **Red** predstavlja jedan zapis u tabeli (jedan konkretan podatak ili entitet), dok **kolona** predstavlja jedno polje tog zapisa.

- Na primer, u tabeli `albums`, red bi mogao biti konkretan album, dok kolone mogu biti `Title`, `ArtistId` itd. Svaka kolona ima svoj `tip podataka` i može imati `dodatna ograničenja`, kao što su primarni ključ (`PK`), strani ključ (`FK`) ili jedinstvenost (`UNIQUE`).

3. Zašto podudaranje teksta `Green` u dve tabele (`fruits` i `vegetables`) samo po sebi ne uspostavlja **relaciju**?

- Podudaranje teksta `Green` u dve tabele samo po sebi **ne definiše strani ključ niti garantuje referencijalni integritet**. Upit može povezati redove poređenjem teksta i bez FK-a, ali baza tada ne proverava tu vezu kao FK. I tekstualna kolona može biti ključ ako zadovoljava potrebne uslove.

4. Koja je razlika između **primarnog** (`PK`) i **stranog** (`FK`) ključa?

- **Primarni ključ** (`PK`) je kolona ili skup kolona koje identifikuju red u tabeli. **Strani ključ** (`FK`) je kolona ili skup kolona koje referenciraju primarni ili odgovarajući jedinstveni ključ druge tabele — ili iste tabele.

- **Primarni ključ** obezbeđuje jedinstvenost, a FK proverava vezu kada je njegova provera uključena. U SQLite-u za neke oblike PK-a u običnim tabelama postoji izuzetak koji dozvoljava `NULL`; zato se u složenom PK-u iz Vežbe 2 kolone izričito označavaju sa `NOT NULL`.

5. Kako se **N:M relacija** između plejlista i numera ostvaruje u Chinook bazi?

- **N:M relacija** između plejlista (`playlists`) i numera (`tracks`) u Chinook bazi ostvaruje se pomoću **pomoćne tabele** `playlist_track`, koja sadrži strane ključeve `PlaylistId` i `TrackId`.

- **Pomoćna tabela** omogućava da jedna plejlista sadrži više numera, a jedna numera može biti u više plejlista, čime se uspostavlja mnogostruka veza između `playlists` i `tracks`.

```sql

-- Pojednostavljen primer za zasebnu bazu, nije doslovna Chinook šema.
-- Kreiranje tabele `playlists`
CREATE TABLE playlists (
    PlaylistId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
);

-- Kreiranje tabele `tracks` (primer)
CREATE TABLE tracks (
    TrackId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
);

-- Tabela `playlist_track` povezuje plejliste i numere u N:M relaciji

CREATE TABLE playlist_track (
    PlaylistId INTEGER NOT NULL,
    TrackId INTEGER NOT NULL,
    PRIMARY KEY (PlaylistId, TrackId),
    FOREIGN KEY (PlaylistId) REFERENCES playlists(PlaylistId),
    FOREIGN KEY (TrackId) REFERENCES tracks(TrackId)
);
```

6. Zašto **SQLAlchemy model** i **Pydantic šema** nisu isto?

- **SQLAlchemy model** predstavlja **strukturu tabele u bazi podataka i koristi se za interakciju sa bazom**.
- **Pydantic šema** definiše **validaciju i serijalizaciju podataka koji ulaze i izlaze iz API-ja**.

- **Model** je vezan za bazu i njene relacije, dok **šema** služi za osiguranje da podaci imaju ispravan oblik i tip pre nego što se obrade ili pošalju klijentu. Drugim rečima, model je za perzistenciju podataka, a šema za validaciju i transformaciju podataka.

7. Da li **`relaciona` baza** može da ima samo jednu tabelu?

- Da. Čak i jedna tabela može biti odgovarajuće normalizovana i imati PK, `UNIQUE`, `NOT NULL` ili druga ograničenja.

- Strani ključ nije obavezan, ali može upućivati i na **istu tabelu**: primer je `employees.ReportsTo` u Chinook bazi. Dodatne tabele su korisne kada model zahteva zasebne entitete i veze, ali njihovo postojanje samo po sebi ne garantuje odsustvo redundantnosti.

---

## Vežbe

Sledeće tabele su ilustracija **pojednostavljenog modela jedne glavne boje** za Vežbu 1. Vežba 2 koristi drugačiju šemu sa povezničkim tabelama i više boja; njene tabele `fruits` i `vegetables` nemaju kolonu `ColorId`.

Tabela `colors` čuva po jedan zapis za svaku boju:

| ColorId (PK) | Name   |
| -----------: | ------ |
|            1 | Green  |
|            2 | Brown  |
|            3 | Red    |
|            4 | Yellow |

Tabela `fruits` čuva ključ boje umesto ponavljanja naziva boje:

| FruitId (PK) | Name   | ColorId (FK) |
| -----------: | ------ | -----------: |
|            1 | Apple  |            1 |
|            2 | Kiwi   |            2 |
|            3 | Banana |            4 |

Isto važi i za tabelu `vegetables`:

| VegetableId (PK) | Name     | ColorId (FK) |
| ---------------: | -------- | -----------: |
|                1 | Cucumber |            1 |
|                2 | Potato   |            2 |
|                3 | Tomato   |            3 |

Tabela `vegetables` takođe koristi `ColorId` kao strani ključ koji upućuje na tabelu `colors`, čime se izbegava ponavljanje naziva boja i omogućava održavanje referencijalnog integriteta. Na ovaj način, svaka boja se definiše samo jednom u tabeli `colors`, a sve povezane tabele (`fruits` i `vegetables`) referenciraju tu boju preko njenog jedinstvenog identifikatora (`ColorId`).

---

### Vežba 1 — Prepoznaj delove tabele

> U ovoj vežbi ćemo se fokusirati na prepoznavanje delova tabele i razumevanje uloge primarnih i stranih ključeva u modelu podataka. Vežba je osmišljena tako da se upoznate sa osnovnim konceptima relacionih baza podataka kroz praktične primere. Cilj je da shvatite kako se podaci organizuju u tabele, kako se povezuju preko ključeva i zašto je važno koristiti primarne i strane ključeve za održavanje integriteta podataka.

Koristeći pojednostavljeni primer tabele `fruits` iz odeljka „Eksplicitna relacija preko ključeva: jedna glavna boja“ (gde se boje voća čuvaju u posebnoj tabeli `colors` i povezuju preko `ColorId`):

1. Navedi njene kolone.

| Kolona  | Tip podatka | Opis                                          |
| ------- | ----------- | --------------------------------------------- |
| FruitId | INTEGER     | Primarni ključ, jedinstveno identifikuje voće |
| Name    | TEXT        | Naziv voća                                    |
| ColorId | INTEGER     | Strani ključ koji upućuje na tabelu `colors`  |

2. Prepiši jedan red kao celovit zapis i objasni šta svaka vrednost znači.

```text
FruitId = 1, Name = 'Apple', ColorId = 1
```

`FruitId = 1` identifikuje zapis; `Name = 'Apple'` je naziv voća; `ColorId = 1` upućuje na boju `Green` u primeru tabele `colors`. Ovo je **prikaz reda**, ne naredba koja ga upisuje. U prethodnom tekstualnom primeru bez tabele boja kolone su `FruitId`, `Name` i `Color`, umesto `ColorId`. Sam broj ne garantuje integritet: potrebni su deklarisan FK i uključena FK provera. Ključ može biti i tekstualan.

Primer unosa za **pojednostavljeni model**, ako su tabele već napravljene, boja sa ID-jem 1 postoji i `FruitId = 1` još nije zauzet:

```sql
INSERT INTO fruits (FruitId, Name, ColorId) VALUES (1, 'Apple', 1);
```

Ovaj `INSERT` **ne radi u šemi Vežbe 2**, jer ona nema `fruits.ColorId`; ne izvršavaj ga ponovo nad prikazanom tabelom ako red već postoji.

3. Predloži kolonu koja bi mogla da bude primarni ključ (`PK`) i objasni zašto.

`FruitId` je dobar kandidat za primarni ključ. **Identifikuje pojedinačan zapis i ne ponavlja se unutar tabele (UNIQUE), čime obezbeđuje jedinstvenost svakog reda i pravilnu identifikaciju svakog voća.** Ovo je posebno važno kada se koristi u kombinaciji sa stranim ključevima u drugim tabelama, jer omogućava pouzdano povezivanje podataka.

- Naziv voća (`Name`) nije dobar izbor u slučaju kada **više zapisa može imati isti naziv**. Na primer u tabeli `fruits` može postojati više zapisa kod kojih je vrednost kolone `Name = 'Apple'`, ali sa **različitim vrednostima drugih kolona** (npr. različite sorte jabuka mogu imati isti naziv, ali različite `ColorId` vrednosti), pa naziv sam po sebi ne garantuje jedinstvenost. Na primer:

Sledeći primer zamišlja dodatnu kolonu `Sort`; ona **ne postoji** u prikazanoj šemi:

```text
FruitId = 1, Name = 'Apple', ColorId = 1, Sort = 'Granny Smith'
FruitId = 2, Name = 'Apple', ColorId = 3, Sort = 'Red Delicious'
```

- Pri pravljenju nove SQLite tabele može se definisati kao `FruitId INTEGER PRIMARY KEY`, kao u Vežbi 2.

- **NAPOMENA:** SQLite ne podržava `ALTER TABLE fruits ADD PRIMARY KEY (FruitId)` za naknadno dodavanje PK-a postojećoj tabeli. **Promena postojeće šeme** obično zahteva **ponovno pravljenje tabele** i pažljivo prebacivanje podataka. `Vežba 2` proširuje model za više boja, pa se tamo `ColorId` više ne čuva direktno u `fruits`.

---

### Vežba 2 — Ispravi model voća i povrća

1. Objasni zašto iste tekstualne vrednosti u kolonama `Color` **same po sebi ne garantuju** referencijalni integritet.

- Bez odgovarajućih ograničenja ponovljene tekstualne vrednosti ne garantuju referencijalni integritet. Različito pisanje (npr. `Red` i `red`) dodatno može dovesti do nekonzistentnosti. Tekstualni ključ uz odgovarajuća ograničenja takođe može obezbediti integritet.

- Korišćenjem primarnog ključa (`ColorId`) u tabeli `colors` i stranih ključeva u povezničkim tabelama, uz **uključenu proveru stranih ključeva** (`PRAGMA foreign_keys = ON;`), svaki zapis veze (`connection`) **mora** upućivati na postojeću boju i postojeće voće ili povrće. Ovo se ostvaruje kroz definisanje **stranih ključeva** u povezničkim (`junction`) tabelama koji **referenciraju primarni ključ** u tabeli `colors` koji je **jedinstven i obavezno prisutan**. Ključ (`ColorId`) može biti i tekstualan ako ispunjava potrebne uslove. **Nije nužno numerički!**

- Kada promenimo naziv boje u tabeli `colors`, upit koji povezuje tabele prikazuje novi naziv za sve odgovarajuće zapise. **Međutim,** vrednosti `ColorId` u njima se ne menjaju.

- U modelu gde je tekst (npr. `'Red'`) ponovljen u svakom redu, **promena naziva boje** zahteva ažuriranje svih odgovarajućih redova u svim tabelama. Jedan `UPDATE` može promeniti više redova iste tabele; propušteni redovi ostaju nekonzistentni.

- **Strani ključevi štite vezu**, ali sami **ne** sprečavaju dva različita ID-ja boje sa istim nazivom (npr. dva različita `ColorId` sa nazivom `'Red'`). Za to je potrebno dodatno ograničenje poput `UNIQUE` nad nazivom.

2. Dopuni model tako da voće i povrće mogu imati više boja.

- Umesto jednog `ColorId` u svakoj tabeli, koristimo dve **povezničke tabele**: `fruit_colors` i `vegetable_colors`. Tako svaki zapis može biti povezan sa više boja, a jedna boja sa više zapisa. U ovom modelu cilj je da svaki zapis ima bar jednu zabeleženu boju; ispod objašnjavamo šta SQL šema garantuje, a šta mora dodatno da se obezbedi.

Pokreni sledeći primer u **novoj, zasebnoj bazi**, a ne nad Chinook bazom ili postojećim tabelama iz Vežbe 1. Nazivi `fruits` i `vegetables` se ponavljaju, ali njihove strukture nisu iste.

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE fruits (
    FruitId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
);

CREATE TABLE vegetables (
    VegetableId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL
);

CREATE TABLE colors (
    ColorId INTEGER PRIMARY KEY,
    Name TEXT NOT NULL UNIQUE
);

CREATE TABLE fruit_colors (
    FruitId INTEGER NOT NULL,
    ColorId INTEGER NOT NULL,
    PRIMARY KEY (FruitId, ColorId),
    FOREIGN KEY (FruitId) REFERENCES fruits(FruitId),
    FOREIGN KEY (ColorId) REFERENCES colors(ColorId)
);

CREATE TABLE vegetable_colors (
    VegetableId INTEGER NOT NULL,
    ColorId INTEGER NOT NULL,
    PRIMARY KEY (VegetableId, ColorId),
    FOREIGN KEY (VegetableId) REFERENCES vegetables(VegetableId),
    FOREIGN KEY (ColorId) REFERENCES colors(ColorId)
);
```

**Šta znači svako ograničenje i zašto je tu:**

1. `INTEGER PRIMARY KEY` identifikuje red u tabelama `fruits`, `vegetables` i `colors`. U SQLite-u je takva kolona posebni alias za `rowid`: kada se ID izostavi ili navede `NULL`, SQLite dodeljuje ID.
2. `Name TEXT NOT NULL` zahteva naziv: `NULL` nije dozvoljen. Ne sprečava prazan tekst `''`; za to bi bilo potrebno dodatno pravilo.
3. `UNIQUE` na `colors.Name` sprečava ponavljanje istog naziva boje. Uz podrazumevano poređenje `Red` i `red` su različiti; ako treba da budu isti, potrebno je dodatno pravilo poređenja. `NOT NULL` je zasebno važan jer SQLite `UNIQUE` sam dozvoljava više `NULL` vrednosti.
4. `fruits.Name` i `vegetables.Name` **nisu `UNIQUE`**: više zapisa može imati isti naziv, recimo različite sorte jabuka. Njihovi ID-jevi ih razlikuju; trenutna šema nema kolonu za sortu.
5. U povezničkim tabelama `NOT NULL` na oba ID-ja zahteva da par bude potpun. To je naročito važno jer SQLite u običnim tabelama može dozvoliti `NULL` u nekim složenim primarnim ključevima ako `NOT NULL` nije izričito naveden.
6. Složeni `PRIMARY KEY (FruitId, ColorId)` sprečava ponavljanje **istog para**, ali dozvoljava da se isti `FruitId` pojavi uz drugu boju i isti `ColorId` uz drugo voće. Isto važi za povrće.
7. `FOREIGN KEY` određuje na koje roditeljske ključeve ID-jevi upućuju. `PRAGMA foreign_keys = ON;` uključuje proveru za **tu konekciju**, pre transakcije; proveri je pomoću `PRAGMA foreign_keys;` — očekuje se `1`.

**Šta je sa indeksima?** `INDEX` pomaže pri traženju redova, a `UNIQUE INDEX` dodatno zabranjuje duplikate indeksiranih vrednosti. SQLite ovde automatski pravi indekse za `UNIQUE` na nazivu boje i složene primarne ključeve. Uklonjeni eksplicitni `CREATE UNIQUE INDEX` za iste kolone bili su duplikati: troše prostor i povećavaju rad pri upisu, bez dodatne zaštite. `INTEGER PRIMARY KEY` je poseban slučaj vezan za `rowid`, ne zahteva takav dodatni indeks. Indeks različitog rasporeda ili kolona može biti koristan za konkretne upite, ali to je zasebna odluka.

Na primer, jabuka može biti i crvena i zelena. Ovaj primer pokreni **posle prethodnog SQL bloka**, u istoj novoj bazi i konekciji:

```sql
BEGIN;
INSERT INTO colors (ColorId, Name) VALUES (1, 'Green'), (2, 'Red');
INSERT INTO fruits (FruitId, Name) VALUES (1, 'Apple');
INSERT INTO fruit_colors (FruitId, ColorId) VALUES (1, 1), (1, 2);
COMMIT;

SELECT fruits.Name AS Fruit, colors.Name AS Color
FROM fruits
JOIN fruit_colors ON fruit_colors.FruitId = fruits.FruitId
JOIN colors ON colors.ColorId = fruit_colors.ColorId
ORDER BY colors.Name;
```

Upit vraća dva reda: `Apple | Green` i `Apple | Red`. To je **jedan zapis jabuke** povezan sa dve boje, a ne dve različite jabuke.

**Važno — poslovno pravilo i ograničenja šeme nisu isto:** želimo da svaki zapis voća i povrća ima **najmanje jednu** boju. Ipak, gornji strani ključevi proveravaju postojeće redove povezničkih tabela; sami **ne zahtevaju** da za svaki red u `fruits` ili `vegetables` postoji bar jedna veza. Šema zato tehnički dopušta zapis bez boje i brisanje njegove poslednje veze. To ne znači da je stvarno voće „bez boje“: može značiti da podaci nisu uneti.

Ako je pravilo **„najmanje jedna boja“ obavezno**, aplikacija **mora** u transakciji:

- **Upisati zapis i bar jednu vezu pre potvrde**

- **Sprečiti uklanjanje poslednje veze**

- **Sprečiti ili kontrolisati upise mimo provera aplikacije.** Za garanciju pri svim direktnim SQL upisima potreban je pažljivo osmišljen drugačiji dizajn i odgovarajuća ograničenja, eventualno sa triggerima. Sam `CHECK` u SQLite-u ne može proveriti postojanje reda u drugoj tabeli pomoću podupita; jednostavan trigger pri unosu roditelja takođe nije dovoljan jer se roditelj u ovom primeru upisuje pre veze.

- **NAPOMENA:** Primer iznad sam po sebi **nije** takva garancija i nema ugrađenu zaštitu od kršenja pravila o najmanje jednoj boji ili drugih poslovnih pravila koja se očekuju za voće i povrće.

3. Nacrtaj relacije u Mermaid `erDiagram` formatu ili na papiru.

```mermaid
erDiagram
    fruits ||--o{ fruit_colors : ima
    colors ||--o{ fruit_colors : "označava"
    vegetables ||--o{ vegetable_colors : ima
    colors ||--o{ vegetable_colors : "označava"
```

Svaki red u povezničkoj tabeli `fruit_colors` upućuje na **tačno jedno** voće i **tačno jednu** boju (`||`). Jedna boja i jedno voće mogu se pojaviti u **nula ili više** redova te povezničke tabele `fruit_colors` (`o{`). Isto važi za povrće. Tako nastaju dve N:M relacije: `fruits`–`colors` i `vegetables`–`colors`. Puna linija `--` označava identifikujuću vezu: strani ključevi su deo složenog primarnog ključa povezničke tabele.

`o{` ovde namerno prikazuje šta gornji SQL **zaista dopušta**, uključujući nula veza. Poslovno pravilo da voće i povrće imaju najmanje jednu boju zahteva dodatnu proveru opisanu iznad. Jedna boja i dalje može biti u tabeli `colors` bez ijednog povezanog voća ili povrća. Dijagram pretpostavlja uključenu FK proveru; on sam ne sprovodi ograničenja baze.

4. Opiši šta bi se dogodilo kada bi naziv boje trebalo promeniti u modelu sa jednom tabelom boja, a šta u modelu gde je tekst ponovljen u svakom redu.

U modelu sa tabelom `colors`, promeni se naziv u jednom redu te tabele; povezani redovi zadržavaju isti ID, a povezani upiti vide novi naziv. Kada se tekst čuva u svakom redu obe tabele, potrebno je ažurirati odgovarajuće redove na svim mestima; propušteni redovi mogu ostati sa starim nazivom.

---

### Vežba 3 — Istraži relacije u Chinook bazi

1. Otvori [ERD.drawio](../chinook/ERD.drawio) i pronađi relacije `artists`–`albums` i `albums`–`tracks`.

```mermaid
erDiagram
    artists ||..o{ albums : has
    albums |o..o{ tracks : has
```

Relacija `artists`–`albums` je jedan-prema-više (1 : 0..N): jedan umetnik ne mora imati album, ali može imati jedan ili više albuma, dok svaki album mora imati upisan jednog umetnika: `albums.ArtistId` je `NOT NULL`. Kada je provera stranih ključeva uključena, taj umetnik mora postojati u tabeli `artists`.

Relacija `albums`–`tracks` je **jedan-prema-više, uz opcionu vezu** (`0..1 : 0..N`):

- Jedna numera može imati **nula ili jedan** zabeležen album. `tracks.AlbumId` je strani ključ koji dozvoljava `NULL`; to može značiti da album nije poznat ili nije unet. Ako nije `NULL`, uz uključenu proveru stranih ključeva mora odgovarati postojećem albumu.

- Jedan album može imati **nula, jednu ili više** povezanih numera. Više redova u `tracks` može imati isti `AlbumId`, jer ta kolona nije jedinstvena.

**Nula numera nije `NULL` pesma.** To znači da u tabeli `tracks` trenutno ne postoji nijedan red koji pokazuje na taj album. Šema dozvoljava takav zapis, na primer dok se podaci o albumu tek unose. To ne znači da autor tvrdi da je album bez pesama smislen u svakom stvarnom kontekstu. Ako je poslovno pravilo da svaki album mora imati bar jednu numeru, aplikacija mora dodatno obezbediti to pravilo. Prikazani strani ključ ga sam ne nameće.

U gornjem Mermaid dijagramu `|o` označava nula ili jedan album po numeri, a `o{` nula ili više numera po albumu. Isprekidana linija `..` označava neidentifikujuću vezu: strani ključ nije deo primarnog ključa deteta.

U radnoj bazi je u trenutku provere bilo **347 albuma i 3.503 numere**: nijedan album nije bio bez povezane numere i nijedna numera nije imala `NULL` u `AlbumId`. To je stanje podataka, ne ograničenje šeme. Možeš proveriti:

```sql
-- Albumi bez povezanih numera
SELECT a.AlbumId, a.Title
FROM albums AS a
WHERE NOT EXISTS (
    SELECT 1 FROM tracks AS t WHERE t.AlbumId = a.AlbumId
);

-- Numere bez zabeleženog albuma
SELECT TrackId, Name
FROM tracks
WHERE AlbumId IS NULL;
```

2. U CLI-ju proveri `.schema albums` i `.schema tracks`.

U **SQLite CLI-ju**, kada je Chinook baza otvorena ili priključena, unesi:

```text
.schema albums
.schema tracks
```

Komande prikazuju `CREATE TABLE` definicije i mogu prikazati i povezane indekse. Ovo je pregled strukture; ne menja bazu.

3. Pronađi primarni ključ i strane ključeve u tim definicijama.

U izdvojenim delovima rezultata vidi se:

```sql
-- albums
[AlbumId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
[ArtistId] INTEGER NOT NULL,
FOREIGN KEY ([ArtistId]) REFERENCES "artists" ([ArtistId])
    ON DELETE NO ACTION ON UPDATE NO ACTION

-- tracks
[TrackId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
[AlbumId] INTEGER,
[MediaTypeId] INTEGER NOT NULL,
[GenreId] INTEGER,
FOREIGN KEY ([AlbumId]) REFERENCES "albums" ([AlbumId])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
FOREIGN KEY ([GenreId]) REFERENCES "genres" ([GenreId])
    ON DELETE NO ACTION ON UPDATE NO ACTION,
FOREIGN KEY ([MediaTypeId]) REFERENCES "media_types" ([MediaTypeId])
    ON DELETE NO ACTION ON UPDATE NO ACTION
```

Ovo su **delovi definicija**, ne samostalne SQL naredbe.

| Tabela   | Kolona        | Uloga i značenje                                                                   |
| -------- | ------------- | ---------------------------------------------------------------------------------- |
| `albums` | `AlbumId`     | PK: jedinstveno identifikuje album.                                                |
| `albums` | `ArtistId`    | FK ka `artists.ArtistId`; `NOT NULL`, pa album mora imati upisanog umetnika.       |
| `tracks` | `TrackId`     | PK: jedinstveno identifikuje numeru.                                               |
| `tracks` | `AlbumId`     | FK ka `albums.AlbumId`; dozvoljava `NULL`, pa album numere ne mora biti zabeležen. |
| `tracks` | `GenreId`     | FK ka `genres.GenreId`; dozvoljava `NULL`, pa žanr ne mora biti zabeležen.         |
| `tracks` | `MediaTypeId` | FK ka `media_types.MediaTypeId`; `NOT NULL`, pa tip medija mora biti upisan.       |

`NOT NULL` zahteva vrednost, a **FK određuje na koji ključ vrednost upućuje**. Da bi SQLite odbio nepraznu vrednost koja ne postoji u roditeljskoj tabeli, provera stranih ključeva mora biti uključena za tu konekciju; proveri je pomoću `PRAGMA foreign_keys;`.

Kod svih navedenih FK-ova `ON DELETE NO ACTION` i `ON UPDATE NO ACTION` ne menjaju automatski povezane redove kada se obriše roditeljski red ili promeni njegov ključ. Uz uključenu FK proveru, operacija koja ostavi nevažeću vezu može biti odbijena.

4. Objasni zašto `playlist_track` postoji između `playlists` i `tracks`.

**`playlists` i `tracks` imaju vezu više-prema-više (N:M):** jedna plejlista može sadržati više numera, a ista numera može biti u više plejlista. Numeru možemo imati i bez plejliste, a plejlistu bez numera.

Međutabela `playlist_track` beleži te veze. Svaki njen red označava **jedan par: jedna plejlista i jedna numera**. Uprošćen, izmišljen primer:

| `PlaylistId` | `TrackId` | Značenje                           |
| ------------ | --------- | ---------------------------------- |
| 1            | 10        | Numera 10 je u plejlisti 1.        |
| 1            | 11        | Numera 11 je takođe u plejlisti 1. |
| 2            | 10        | Numera 10 je i u plejlisti 2.      |

Ponavljanje `PlaylistId = 1` pokazuje više numera u jednoj plejlisti; ponavljanje `TrackId = 10` pokazuje istu numeru u više plejlista. Ovo su dve veze 1:N prema međutabeli:

```mermaid
erDiagram
    playlists ||--o{ playlist_track : contains
    tracks ||--o{ playlist_track : appears_in
```

Puna linija označava identifikujuću vezu: oba strana ključa su ujedno deo primarnog ključa međutabele. Jedan red u `playlist_track` pripada tačno jednoj plejlisti i jednoj numeri, pod uslovom da se FK ograničenja sprovode.

Proveri samu definiciju:

```text
.schema playlist_track
```

Bitni delovi su:

```sql
[PlaylistId] INTEGER NOT NULL,
[TrackId] INTEGER NOT NULL,
PRIMARY KEY ([PlaylistId], [TrackId]),
FOREIGN KEY ([PlaylistId]) REFERENCES "playlists" ([PlaylistId]),
FOREIGN KEY ([TrackId]) REFERENCES "tracks" ([TrackId])
```

Primarni ključ je **složen**: jedinstven mora biti ceo par `(PlaylistId, TrackId)`, a ne svaka kolona zasebno. Tako su dozvoljeni parovi `(1, 10)`, `(1, 11)` i `(2, 10)`, ali drugi `(1, 10)` nije. Zbog toga u ovoj šemi istu numeru nije moguće dodati dva puta u istu plejlistu. Ove dve kolone su istovremeno **dva odvojena strana ključa**, ne jedan složeni FK.

Umesto liste ID-jeva u jednoj ćeliji ili dodavanja novih kolona za svaku plejlistu, međutabela čuva po jedan red za svaku vezu. Ona sama u ovoj šemi ne beleži redosled numera u plejlisti.

Za pregled stvarnih veza u radnoj Chinook bazi:

```sql
-- Tri numere iz plejliste 1 sa najmanjim TrackId
SELECT p.PlaylistId, p.Name AS plejlista, t.TrackId, t.Name AS numera
FROM playlists AS p
JOIN playlist_track AS pt ON p.PlaylistId = pt.PlaylistId
JOIN tracks AS t ON t.TrackId = pt.TrackId
WHERE p.PlaylistId = 1
ORDER BY t.TrackId
LIMIT 3;

-- Sve plejliste koje sadrže numeru 1
SELECT p.PlaylistId, p.Name AS plejlista
FROM playlists AS p
JOIN playlist_track AS pt ON p.PlaylistId = pt.PlaylistId
WHERE pt.TrackId = 1
ORDER BY p.PlaylistId;
```

U proveri radne baze plejlista 1 imala je više numera, a numera 1 bila je u tri plejliste. `ORDER BY TrackId` u prvom upitu služi samo za stabilan prikaz rezultata, ne predstavlja redosled numera u plejlisti.

---

### Vežba 4 — Poveži bazu sa ORM pojmovima

Izaberi tabelu `albums` i napravi tabelu sa sledećim kolonama:

| Pojam                                                  | Odgovor                                                                                                                              |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| SQLAlchemy model koji bi mogao da je predstavlja       | Primer klase `Album` ispod, sa `__tablename__ = "albums"`.                                                                           |
| Primer jednog reda / ORM instance                      | Red sa `AlbumId = 1`, naslovom `For Those About To Rock We Salute You` i `ArtistId = 1`; ORM može da ga predstavi instancom `Album`. |
| Primer kolone / mapiranog atributa                     | Kolona `albums.Title` odgovara Python atributu `Album.title`.                                                                        |
| Pydantic šema koja bi mogla da posluži kao API odgovor | `AlbumResponse`, sa poljima `album_id`, `title` i `artist_id`.                                                                       |
| Veza ka drugoj tabeli preko stranog ključa             | `albums.ArtistId` upućuje na `artists.ArtistId`.                                                                                     |

Ovo je **ilustrativan model za Chinook**, ne postojeća TodoApp klasa. Tabela i njena imena kolona već postoje u Chinook bazi; Python atributi mogu imati druga imena:

```python
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel, ConfigDict


class Base(DeclarativeBase):
    pass


class Album(Base):
    __tablename__ = "albums"

    album_id: Mapped[int] = mapped_column("AlbumId", Integer, primary_key=True)
    title: Mapped[str] = mapped_column("Title", String(160), nullable=False)
    artist_id: Mapped[int] = mapped_column(
        "ArtistId", ForeignKey("artists.ArtistId"), nullable=False
    )


class AlbumResponse(BaseModel):
    album_id: int
    title: str
    artist_id: int

    model_config = ConfigDict(from_attributes=True)
```

- `Album` je **klasa koja mapira tabelu**, a `Album(...)` ili objekat dobijen ORM upitom je instanca koja predstavlja jedan red. Kreiranje Python objekta samo po sebi ne upisuje red u bazu.
- `mapped_column("Title", ...)` povezuje Python atribut `title` sa postojećom SQL kolonom `Title`. `ForeignKey("artists.ArtistId")` opisuje vezu u SQLAlchemy modelu; za pravljenje cele šeme nedostaje i definicija ili reflektovana tabela `artists`.
- `AlbumResponse` je zasebna Pydantic šema za API; `from_attributes=True` omogućava da čita vrednosti iz ORM instance. Na primer, `AlbumResponse.model_validate(album)` pravi šemu iz učitanog objekta.
- `ForeignKey` i ORM `relationship()` nisu isto: prvi opisuje strani ključ, a drugi po želji daje pogodnost za rad sa povezanim ORM objektima. U ovom primeru `relationship()` nije definisan.

Model i pretvaranje učitanog albuma u `AlbumResponse` provereni su nad radnom Chinook bazom **samo za čitanje**. Primer ne poziva `create_all()` i ne menja bazu.

---

### Vežba 5 — Prikaži putanju podatka

Nacrtaj dijagram koji prikazuje putanju albuma od HTTP zahteva do odgovora FastAPI endpoint-a. Uključi Pydantic validaciju, SQLAlchemy, SQLite drajver i tabelu `albums`, a uz svaki element napiši njegovu odgovornost.

Primer ispod je **zamišljeni endpoint** za kreiranje albuma u aplikaciji koja koristi Chinook; nije postojeći TodoApp endpoint. Ne treba ga pokretati nad radnom bazom samo radi čitanja primera.

```mermaid
flowchart TD
    client["Klijent: HTTP POST /albums"] --> request["Pydantic: AlbumCreate"]
    request --> endpoint["FastAPI endpoint"]
    endpoint --> session["SQLAlchemy: Album i Session"]
    session --> driver["Python sqlite3 drajver"]
    driver --> db[("SQLite: tabela albums")]
    db --> session
    session --> response["Pydantic: AlbumResponse"]
    response --> client_response["HTTP odgovor: JSON"]
```

---

#### Primer toka

1. **Klijent šalje HTTP zahtev.** Na primer, telo zamišljenog zahteva `POST /albums`:

   ```json
   {
     "title": "Novi album",
     "artist_id": 1
   }
   ```

2. **FastAPI i Pydantic proveravaju ulaz.** Zamišljena ulazna šema `AlbumCreate` ima `title: str` i `artist_id: int`. Pydantic proverava i obrađuje primljena polja; ne dokazuje sam po sebi da umetnik sa tim ID-jem postoji u bazi. Pri neuspešnoj validaciji FastAPI vraća grešku klijentu.

3. **Endpoint obrađuje zahtev.** Na osnovu validiranih podataka pravi ORM objekat `Album(title=..., artist_id=...)`, dodaje ga u `Session` i traži potvrdu transakcije pomoću `commit()`. Ako je potrebna provera poslovnih pravila, endpoint ili njegov servis je obavlja.

4. **SQLAlchemy i drajver pristupaju bazi.** SQLAlchemy prevodi ORM operaciju u SQL i prosleđuje ga Pythonovom SQLite drajveru `sqlite3`. Drajver poziva SQLite biblioteku koja izvršava upis u tabelu `albums` i primenjuje njena ograničenja. FK provera u SQLite-u mora biti uključena za tu konekciju; u suprotnom ne treba pretpostaviti da je `artist_id` proveren.

5. **Potvrđuje se promena.** Posle uspešnog `commit()` upis je potvrđen; kod baze na disku ostaje sačuvan. U slučaju greške, ne treba vraćati uspešan odgovor: transakciju treba poništiti i grešku odgovarajuće obraditi. Po potrebi se objekat osvežava sa `session.refresh(album)` da bi se pročitale vrednosti iz baze, uključujući generisani ID.

6. **Priprema se HTTP odgovor.** Aplikacija pretvara ORM objekat u `AlbumResponse`, a FastAPI priprema JSON odgovor. Na primer, ako je baza dodelila ID `348`, odgovor može biti:

   ```json
   {
     "album_id": 348,
     "title": "Novi album",
     "artist_id": 1
   }
   ```

   ID i podaci su ilustrativni; ID dodeljuje baza i ne treba unapred pretpostaviti njegovu vrednost.

**Razlika između slojeva:** Pydantic proverava oblik API podataka; SQLAlchemy upravlja ORM objektima i transakcijom; `sqlite3` je drajver; SQLite upravlja bazom i ograničenjima. `albums` je tabela u bazi, a ne Python klasa ili JSON odgovor. Kod `GET` zahteva tok je sličan, ali aplikacija čita postojeći album umesto da ga kreira.
