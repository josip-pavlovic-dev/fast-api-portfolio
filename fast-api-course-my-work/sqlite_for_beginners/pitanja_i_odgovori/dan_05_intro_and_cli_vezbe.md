# Dan 05 — Uvod i vežbe u `playground`

## Cilj dana

Danas ponavljaš vežbe iz [oblasti 00 — Uvod](../00_intro/README.md) i uvežbavaš gde da sačuvaš odgovore, kako da ih pokreneš i kojim alatom. Najvažnije je da razdvojiš tri stvari:

1. **Lekcija** (`.md`) objašnjava pojmove i postavlja vežbe.
2. **Radni fajl** (`.sql` ili `.txt`) čuva tvoje upite, CLI komande i beleške.
3. **Klijent** (`sqlite3`, po želji obavijen sa `rlwrap`, ili `litecli`) otvara konekciju i izvršava unos.

Radni fajlovi **ne zamenjuju** `litecli`, `rlwrap` ili SQLite CLI. Oni zamenjuju potrebu da rešenja čuvaš samo u istoriji terminala ili da ih svaki put prekucavaš. I dalje moraš da otvoriš odgovarajući klijent i pokreneš fajl ili pojedinačni upit.

---

## 1. Kako da biraš između `playground/cli` i `playground/sql`

### `playground/cli/` — komande SQLite alata i beleške

Fajlovi `.txt` u ovom folderu služe za **SQLite CLI komande**, uputstva i beleške. Mogu sadržati:

- dot-komande koje počinju tačkom, npr. `.databases`, `.tables`, `.schema`;
- SQL naredbe koje se unose u SQLite CLI i završavaju sa `;`;
- komentare koji opisuju očekivani rezultat ili upozorenje.

Dot-komande nisu SQL, pa ovaj fajl pokreći u **SQLite CLI-ju**, ne kao SQL upit. Na primer, iz korena repozitorijuma:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/cli/01_what_is_sqlite3_tool.txt
```

`.read` je dot-komanda: unosi se nakon što si već pokrenuo `sqlite3` i vidiš SQLite prompt. Ona učitava fajl red po red u **trenutnoj konekciji**. Pročitaj sadržaj pre pokretanja, jer `.read` izvršava sve komande u njemu. Ako fajl sadrži samo komentare, neće biti vidljivog izlaza.

### `playground/sql/00_intro/` — SQL rešenja za uvodne lekcije

Fajlovi `.sql` odgovaraju lekcijama u `00_intro/`. U njih upisuješ SQL upite i komentare koji objašnjavaju rešenja. Pokreni ih na jedan od sledećih načina:

1. **SQLite CLI:** otvori odgovarajuću bazu, pa učitaj fajl sa `.read`:

   ```text
   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/01_what_is_sqlite.sql
   ```

2. **SQLTools:** poveži ekstenziju sa odgovarajućom bazom, otvori `.sql` fajl i pokreni označeni `-- @block` ili selektovani SQL upit. Ovo je pogodno za samostalne upite za čitanje. Skripte koje zavise od redosleda stanja konekcije, kao što su `ATTACH`/`DETACH` u fajlu 02, pokreni kao celinu iz SQLite CLI-ja. Fajl 04 sadrži `CREATE TABLE` i `INSERT`, zato ga nemoj pokretati kroz SQLTools konekciju ka Chinook-u.

Sam nastavak `.sql` **ne** pokreće fajl i ne čini ga automatski bezbednim. Pročitaj komande pre izvršavanja. `SELECT` i `PRAGMA` provere iz prvih lekcija su namenjene pregledu; `CREATE`, `INSERT`, `UPDATE` i `DELETE` menjaju bazu.

### SQLTools konekcija i vizuelni pregled baze

Pošto već imaš uspostavljenu SQLTools konekciju **ChinookPractice**, možeš da radiš i kroz VS Code, bez pokretanja terminalskog klijenta:

1. U SQLTools panelu proveri da je pored **ChinookPractice** zelena oznaka konekcije.
2. Otvori odgovarajući `.sql` fajl iz `playground/sql/00_intro/`.
3. Iznad `-- @block` videćeš **Run on active connection**. Klikni ga da izvršiš taj blok na trenutno aktivnoj konekciji. Možeš i da označiš samo SQL naredbu i izabereš **Run Selected Query**.
4. Pregledaj rezultat i istoriju upita u SQLTools panelu. Query History je istorija pokretanja, nije zamena za čuvanje rešenja u `.sql` fajlu.

Na primer, u [03_how_to_connect_to_sqlite.sql](../playground/sql/00_intro/03_how_to_connect_to_sqlite.sql) pokreni blokove `PRAGMA database_list;`, `SELECT sqlite_version();` i `PRAGMA foreign_keys;`. Oni prikazuju putanju, SQLite verziju i FK postavku **SQLTools konekcije**. Te vrednosti mogu biti drugačije u `rlwrap`/CLI ili aplikaciji, jer su to zasebne konekcije.

U [02_attaching_sample_database_to_sqlite.sql](../playground/sql/00_intro/02_attaching_sample_database_to_sqlite.sql) blokovi koji koriste `practice.sqlite_schema` zavise od aliasa `practice`. Ako ga nema u SQLTools konekciji, prvo izvrši `ATTACH DATABASE ... AS practice;` iz istog SQLTools konektora, a zatim izvrši blokove koji ga koriste. `ATTACH` u terminalskom CLI-ju ne priključuje bazu u SQLTools: alias pripada samo onoj konekciji gde je naredba pokrenuta. Ako je `ChinookPractice` već glavna baza te konekcije, možeš umesto aliasa koristiti `sqlite_schema` i `PRAGMA foreign_key_list(albums);`. Za vežbanje celog redosleda `ATTACH`/upiti/`DETACH`, jednostavnije je učitati ceo fajl u svežoj `sqlite3 :memory:` sesiji.

Možeš i da koristiš ekstenziju koja prikazuje tabele i redove vizuelno:

1. Otvori bazu u njenom Explorer/Viewer panelu.
2. Proveri **ime i punu putanju fajla** pre nego što tumačiš prikazane tabele.
3. Proširi tabelu, na primer `albums`, i pregledaj kolone i redove. Koristi ovo kao vizuelnu proveru; za zadatke i ponovljive rezultate i dalje sačuvaj SQL upit u `.sql` fajlu.
4. Nemoj menjati ćelije ili šemu tokom ovog ponavljanja; ostani na pregledu.

Na tvojim slikama SQLTools konektor je nazvan `ChinookPractice`, dok je otvoreni Viewer tab nazvan `chinook_restore.db`. Imena su različita, zato nemoj pretpostaviti da prikazuju isti fajl: uporedi punu putanju svakog konektora. Viewer prikazuje **13** tabela, među kojima su `sqlite_sequence` i `sqlite_stat1`; to su SQLite pomoćne/system tabele. Ostalih **11** su Chinook tabele koje se broje u vežbi. Zato broj u Viewer-u može biti veći od broja korisničkih tabela prikazanog u CLI-ju.

### Da li da koristim `litecli` ili `rlwrap`?

Za ove lekcije preporuka je **zvanični SQLite CLI obavijen sa `rlwrap`**:

- `sqlite3` je SQLite komandni klijent i razume SQLite dot-komande kao `.read`, `.tables` i `.schema`.
- `rlwrap` je omotač koji dodaje uređivanje komandne linije, istoriju i dovršavanje; on sam nije baza niti zamena za `sqlite3`.
- `litecli` je zaseban SQL klijent sa SQL predlozima. Nije `sqlite3` obavijen sa `rlwrap` i ne treba pretpostaviti da prihvata iste SQLite dot-komande.

Za pokretanje `rlwrap` sesije nad **radnom kopijom samo za čitanje**, iz korena repozitorijuma:

```bash
INPUTRC="$HOME/.config/sqlite-cli/sqlite3-inputrc" \
  rlwrap -a -N -c -i -A -f "$HOME/.config/sqlite-cli/sqlite3-completions" \
  sqlite3 -cmdline-edit off -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

U CLI-ju možeš direktno uneti SQL ili koristiti `.read`. Za privremenu `:memory:` bazu, npr. vežbu sa `ATTACH`, koristi istu `rlwrap` komandu, ali zameni deo `sqlite3 ... chinook_practice.db` sa:

```bash
sqlite3 :memory:
```

U ovoj varijanti nemoj dodavati `-readonly` za glavnu bazu u memoriji: `-readonly` nije potreban za `:memory:` i može ograničiti šta možeš uraditi u toj konekciji.

`litecli` je dostupan u projektnom okruženju. Ako želiš da probaš njegove SQL predloge, iz korena repozitorijuma možeš pokrenuti:

```bash
.venv/bin/litecli fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Ova komanda ne otvara bazu read-only, zato se za pregled drži `SELECT` upita. Za vežbe koje zavise od SQLite CLI komandi kao što su `.read`, `.tables` ili `.schema`, koristi `rlwrap` + `sqlite3`. SQLTools je još jedan način izvršavanja SQL-a, ali nije terminalski SQLite CLI.

### Važne razlike u fajlovima

| Fajl ili alat                       | Sadrži / radi                             | Kako se koristi                                                          |
| ----------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------ |
| Lekcija `.md`                       | Objašnjenje i zadaci                      | Čitaš je; vežbu rešavaš u radnom fajlu ili beleškama.                    |
| `.sql` u `playground/sql/00_intro/` | SQL i komentari za uvodne lekcije         | `.read` u SQLite CLI-ju ili pokretanje SQL bloka kroz SQLTools.          |
| `.txt` u `playground/cli/`          | SQLite dot-komande, SQL primeri i beleške | `.read` u SQLite CLI-ju; ne pokreće se kao Bash komanda.                 |
| `sqlite3`                           | Zvanični SQLite CLI klijent               | Prima SQL i svoje dot-komande.                                           |
| `rlwrap`                            | Omotač oko drugog programa                | U ovom slučaju pokreće `sqlite3` uz bolje uređivanje i dovršavanje.      |
| `litecli`                           | Poseban SQL klijent                       | Koristiš ga opciono za SQL upite; nije zamena za SQLite CLI dot-komande. |

Napomena o imenima: `playground/cli/01_what_is_sqlite3_tool.txt` odgovara lekciji o **sqlite3 alatu** u `01_some_basic_sql_commands/`, a ne lekciji `00_intro/01_what_is_sqlite.md`. Slični brojevi i nazivi ne znače da su to isti zadaci. Proveri zaglavlje `-- Lekcija:` u `.txt` fajlu.

---

## 2. Bezbedan redosled rada

1. Iz korena repozitorijuma otvori radnu kopiju `chinook_practice.db` sa `-readonly` za vežbe čitanja.
2. Proveri `.databases`, a zatim `.tables`; nemoj pretpostaviti da je baza ispravna samo zato što je prompt otvoren.
3. SQL upite i rešenja sačuvaj u odgovarajućem `.sql` fajlu. Dot-komande i terminalska zapažanja stavi u `.txt` fajl ili dnevnik.
4. Pre `.read`, otvori fajl i pregledaj sve njegove naredbe. `.read` može izvršiti i naredbe koje menjaju bazu.
5. Vežbu koja pravi tabele, kao što je model voća i boja, izvršavaj u novoj `:memory:` konekciji ili pažljivo izabranom novom sandbox fajlu — nikada u Chinook bazi.
6. Ne pokreći TodoApp samo radi provere putanje bez provere radnog direktorijuma i baze: inicijalizacija aplikacije poziva `create_all()` i može napraviti nedostajuće tabele.

---

## 3. Rešenja vežbi — `00_intro/01_what_is_sqlite.md`

Radni fajl: [01_what_is_sqlite.sql](../playground/sql/00_intro/01_what_is_sqlite.sql). U njemu su već pripremljeni bezbedni SQL upiti i objašnjenja; CLI dot-komande iz vežbe pokreću se u SQLite promptu.

### Vežba 1 — Pronađi Chinook bazu

Iz korena repozitorijuma pokreni:

```bash
pwd
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Ako želiš uređivanje i Tab dovršavanje, koristi komandu `rlwrap` iz odeljka 1. U SQLite promptu:

```text
.databases
.tables
```

`main` treba da pokazuje na `playground/databases/chinook_practice.db` i `r/o`. `.tables` treba da prikaže Chinook tabele kao što su `artists`, `albums`, `tracks`, `customers` i `invoices`. U ovoj vežbi koristi se kopija, a ne originalni `chinook/chinook.db`.

### Vežba 2 — Istraži šemu

U CLI-ju:

```text
.schema albums
.schema tracks
.schema playlist_track
```

Pročitaj ključne delove:

| Tabela           | Primarni ključ                     | Strani ključevi i napomena                                                                                          |
| ---------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `albums`         | `AlbumId`                          | `ArtistId` referencira `artists.ArtistId` i u ovoj šemi je `NOT NULL`.                                              |
| `tracks`         | `TrackId`                          | `AlbumId` referencira `albums.AlbumId` i može biti `NULL`; `GenreId` može biti `NULL`; `MediaTypeId` je `NOT NULL`. |
| `playlist_track` | Složeni PK `(PlaylistId, TrackId)` | Svaka od te dve kolone je zaseban FK: `PlaylistId` ka `playlists`, `TrackId` ka `tracks`.                           |

ERD daje pregled odnosa i kardinalnosti. SQL šema definiše konkretne kolone, ključeve, `NOT NULL` i ponašanje poput `ON DELETE NO ACTION`. Zbog toga ERD i šemu treba čitati zajedno; dijagram može izostaviti detalje ograničenja.

### Vežba 3 — Verzija i strani ključevi

U konekciji čiji rezultat želiš da proveriš:

```sql
SELECT sqlite_version();
PRAGMA foreign_keys;
```

Zabeleži prikazanu verziju; ona zavisi od SQLite biblioteke koju koristi taj klijent. `PRAGMA foreign_keys` vraća `1` ako su provere uključene u toj konekciji i `0` ako nisu. Nemoj unapred upisivati očekivanu vrednost: CLI, SQLTools i aplikacija mogu koristiti različite konekcije/podešavanja. To je per-connection postavka.

### Vežba 4 — Izaberi bazu za scenario

1. **Lična kolekcija muzike na jednom računaru:** SQLite je razuman, jednostavan izbor za lokalni fajl i mali broj upisa.
2. **Lokalni FastAPI testovi na jednom računaru:** SQLite je često praktičan za brze, izolovane testne baze. Ako produkcija koristi drugu bazu, deo testova treba pokretati i na toj bazi radi provere kompatibilnosti.
3. **Mnogo istovremenih izmena iz više instanci API-ja:** razmotri klijent-server bazu, npr. PostgreSQL. SQLite može opslužiti više čitalaca, ali pisanja se serijalizuju tako da u jednom trenutku piše jedna konekcija; veća konkurentnost može čekati ili izazvati `database is locked`.

### Vežba 5 — Putanja podatka kroz FastAPI

Primer toka za zapis:

```mermaid
flowchart TD
    client["Klijent: HTTP zahtev"] --> fastapi["FastAPI endpoint"]
    fastapi --> input["Pydantic: validacija ulaza"]
    input --> orm["SQLAlchemy: model i transakcija"]
    orm --> driver["SQLite drajver"]
    driver --> db[("SQLite fajl baze")]
    db --> driver
    driver --> orm
    orm --> output["Pydantic: izlazna šema"]
    output --> response["FastAPI: HTTP/JSON odgovor"]
    response --> client
```

- **FastAPI** prima HTTP zahtev i poziva endpoint.
- **Pydantic** proverava oblik i tipove ulaznih/izlaznih podataka; sam po sebi ne proverava da li FK vrednost postoji u bazi.
- **SQLAlchemy** upravlja ORM objektima, SQL upitima i transakcijom (`commit`/`rollback`).
- **SQLite drajver** prenosi naredbe između Python koda i SQLite biblioteke.
- **SQLite baza** izvršava SQL i čuva potvrđene promene u fajlu.
- **FastAPI** vrši serijalizaciju odgovora i šalje ga klijentu.

---

## 4. Rešenja vežbi — `00_intro/02_attaching_sample_database_to_sqlite.md`

Radni fajl: [02_attaching_sample_database_to_sqlite.sql](../playground/sql/00_intro/02_attaching_sample_database_to_sqlite.sql). `.schema`, `.tables` i `.databases` ostaju CLI dot-komande; SQL fajl sadrži SQL naredbe za `ATTACH`, upite i `DETACH`.

### Vežba 1 — Otvori Chinook kao `main`

Iz korena repozitorijuma pokreni SQLite CLI nad kopijom:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Zatim u CLI-ju:

```text
.databases
.tables
.schema albums
.quit
```

`chinook_practice.db` je glavna baza i u toj konekciji se zove `main`. `.schema albums` treba da prikaže `AlbumId` kao PK i `ArtistId` kao FK ka `artists.ArtistId`. `-readonly` štiti ovu konekciju od pisanja u radnu kopiju.

### Vežba 2 — `ATTACH` kao dodatna baza

Otvori privremenu glavnu bazu u memoriji:

```bash
sqlite3 :memory:
```

U SQLite CLI-ju izvrši:

```sql
ATTACH DATABASE 'fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db' AS chinook;
```

Zatim proveri:

```text
.databases
```

`main` je prazna, privremena baza u memoriji. `chinook` je alias dodatne baze koja pokazuje na Chinook fajl. Da bi upit pročitao umetnike iz priključene baze, koristi alias kao prefiks:

```sql
SELECT Name
FROM chinook.artists
ORDER BY Name
LIMIT 5;
```

Po završetku:

```sql
DETACH DATABASE chinook;
```

`DETACH` uklanja bazu iz te konekcije, ali ne briše fajl. `.databases` nakon toga više ne treba da prikazuje `chinook`. Izađi sa `.quit`.

### Vežba 3 — Relativne putanje i direktorijum

Iz korena repozitorijuma:

```bash
pwd
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db
```

Kraći primer radi **iz samog foldera `chinook`**:

```bash
cd fast-api-course-my-work/sqlite_for_beginners/chinook
pwd
sqlite3 -readonly chinook.db
```

Relativna putanja se računa prema trenutnom radnom direktorijumu procesa, a ne prema `.md` ili `.sql` fajlu. Promena direktorijuma zato može da učini da ista relativna putanja pokazuje na drugo mesto ili ne postoji. Ako je direktorijum dostupan i upisiv, pogrešna putanja uz običan read-write CLI može napraviti praznu bazu; ako direktorijuma nema ili nema dozvole, otvaranje može pasti. `-readonly` sprečava da se nepostojeći fajl tiho napravi kao baza za pisanje.

### Vežba 4 — Dva toka otvaranja

**Otvaranje Chinook kao glavne baze:**

```mermaid
flowchart TD
    shell["Terminal: trenutni direktorijum"] --> start["Pokreni sqlite3 sa Chinook putanjom"]
    start --> resolve["Relativna putanja se razrešava pri otvaranju"]
    resolve --> main["chinook.db je main u toj konekciji"]
    main --> close[".quit zatvara konekciju; fajl ostaje na disku"]
```

**`main` u memoriji i dodatni `chinook` alias:**

```mermaid
flowchart TD
    shell["Terminal: trenutni direktorijum"] --> start["Pokreni sqlite3 :memory:"]
    start --> main["Napravljena je privremena main baza u memoriji"]
    main --> attach["ATTACH DATABASE ... AS chinook"]
    attach --> resolve["Putanja do fajla se razrešava pri ATTACH-u"]
    resolve --> both["main i chinook su dostupni u istoj konekciji"]
    both --> detach["DETACH chinook uklanja samo alias iz konekcije"]
    detach --> close[".quit zatvara konekciju; chinook.db ostaje na disku"]
```

U oba toka CLI konekcija je privremena. Samo prva otvara Chinook kao `main`; u drugoj je `main` memorijska, a Chinook je dodatna baza pod aliasom.

---

## 5. Rešenja vežbi — `00_intro/03_how_to_connect_to_sqlite.md`

### Vežba 1 — Otvori bazu i proveri putanju

Za ponavljanje koristi radnu kopiju:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

U CLI-ju:

```text
.databases
.tables
.schema albums
```

Očekivano: `main` pokazuje na `chinook_practice.db` i `r/o`; `.tables` prikazuje 11 korisničkih tabela u datoj Chinook kopiji; `.schema albums` prikazuje definiciju albuma. Ako ne odgovara putanja, izađi i ispravi je pre bilo kakvog upisa.

### Vežba 2 — Tri konekcije ka istom fajlu

Ispravan crtež ima **jedan fajl** i **tri odvojene konekcije**:

```mermaid
flowchart LR
    cli["sqlite3 CLI"] --> cliConn["CLI konekcija"]
    gui["GUI alat"] --> guiConn["GUI konekcija"]
    app["FastAPI + SQLAlchemy"] --> appConn["Aplikaciona konekcija"]
    cliConn --> db[("isti chinook.db fajl")]
    guiConn --> db
    appConn --> db
```

Svaki program zasebno otvara fajl. Tri konekcije nisu jedan zajednički kanal, a fajl ostaje na disku kada se zatvore. Ista imena fajlova nisu dovoljna: putanje moraju voditi do istog fajla. GUI profil je podešavanje, ne aktivna konekcija. SQLAlchemy može uzimati konekcije iz pool-a po potrebi; ne treba crtati da jedna konekcija obavezno traje koliko i cela aplikacija.

### Vežba 3 — Pogrešna putanja

U Bash-u proveri direktorijum sa `pwd`. Ako otvoriš `chinook.db` pogrešnom relativnom putanjom, SQLite može da napravi **novu praznu bazu** ako odredišni direktorijum postoji i ima dozvole za pisanje. Ako direktorijum ne postoji, nema dozvole ili sesija je read-only, otvaranje može dati grešku umesto da napravi fajl.

U CLI-ju proveri:

```text
.databases
.tables
```

`.databases` prikazuje putanju otvorene baze. `.tables` daje dodatni trag: prazna lista može značiti novu praznu bazu, ali sama po sebi ne dokazuje zašto nema tabela.

### Vežba 4 — CLI i GUI

| Pitanje              | CLI                                            | GUI alat                                                |
| -------------------- | ---------------------------------------------- | ------------------------------------------------------- |
| Izbor fajla          | Putanja kao argument `sqlite3 path/to/file.db` | Izbor postojećeg fajla kroz interfejs/profil            |
| Pregled tabela       | `.tables`                                      | Lista tabela u panelu alata                             |
| Zatvaranje konekcije | `.quit` ili `.exit`                            | Disconnect ili zatvaranje konekcije/profila prema alatu |
| Da li se fajl briše? | Ne; zatvara se CLI konekcija, fajl ostaje      | Ne; zatvara se GUI konekcija, fajl ostaje               |

### Vežba 5 — FastAPI TodoApp

Konfiguracija pregledana u [database.py](../../TodoApp/db/database.py) sadrži:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./TodoApp/data/todosapp.db"
```

Relativni SQLite URL razrešava se u odnosu na **radni direktorijum procesa aplikacije**. U lekciji aplikacija se pokreće iz `fast-api-course-my-work/`, pa očekivana putanja je `TodoApp/data/todosapp.db` ispod tog direktorijuma. To treba potvrditi za konkretan proces, ne nagađati na osnovu mesta gde je `database.py`.

**Upozorenje:** [main.py](../../TodoApp/main.py) poziva `Base.metadata.create_all(bind=engine)` pri učitavanju aplikacije. Zato je pokretanje aplikacije operacija koja može napraviti nedostajuće tabele. Nemoj pokretati je nad bazom koju ne želiš da menjaš; prvo proveri punu putanju i napravi rezervnu kopiju ako su podaci važni.

Postupak iz lekcije:

1. U prvom terminalu, iz korena repozitorijuma:

   ```bash
   source .venv/bin/activate
   cd fast-api-course-my-work
   pwd
   python -m uvicorn TodoApp.main:app
   ```

   Pre toga proveri zavisnosti i eventualni `JWT_SECRET_KEY` iz bezbednog `.env`/okruženja. Nemoj ispisivati tajnu u dnevnik.

2. Zabeleži Uvicorn-ov `Started server process [PID]`. U drugom terminalu u Linux/WSL-u proveri:

   ```bash
   readlink /proc/PID/cwd
   ```

   Zameni `PID` brojem stvarnog server procesa. Ovo pokazuje radni direktorijum tog procesa, ne direktorijum drugog terminala.

3. U drugom terminalu otvori TodoApp bazu read-only i proveri `.databases`:

   ```bash
   sqlite3 -readonly fast-api-course-my-work/TodoApp/data/todosapp.db
   ```

   Putanja u izlazu treba da bude ista puna putanja do koje se razrešava SQLite URL. `r/o` se odnosi samo na CLI konekciju.

4. Zatvori pregled sa `.quit`, pa zaustavi server sa `Ctrl+C`.

Ako se radni direktorijum ili putanja razlikuju, nemoj zaključiti da su obe konekcije otvorile isti fajl. Rešenje vežbe je dokazati putanju za oba procesa i uporediti je; za današnje ponavljanje nije neophodno pokretati aplikaciju.

---

## 6. Rešenja vežbi — `00_intro/04_database_concepts.md`

Radni fajl [04_database_concepts.sql](../playground/sql/00_intro/04_database_concepts.sql) sadrži izvršiv primer šeme za vežbu 2. Pokreći ga samo u novoj `:memory:` konekciji, jer sadrži `CREATE TABLE` i `INSERT`.

### Vežba 1 — Prepoznaj delove tabele

Za primer voća sa jednom glavnom bojom:

| Kolona    |  Primer | Uloga                                                           |
| --------- | ------: | --------------------------------------------------------------- |
| `FruitId` |     `1` | PK koji identifikuje red voća.                                  |
| `Name`    | `Apple` | Ime voća.                                                       |
| `ColorId` |     `1` | FK ka `colors.ColorId`; u prikazanom primeru boja 1 je `Green`. |

Celovit red: `FruitId = 1, Name = 'Apple', ColorId = 1`. PK nije nužno naziv: `FruitId` je stabilan identifikator. `Name` možda nije jedinstven, na primer ako se više sorti čuva kao zasebni redovi. Broj `ColorId` je veza samo ako je FK definisan i provera stranih ključeva uključena; ID sam po sebi ne proverava da roditeljski red postoji.

### Vežba 2 — Voće i povrće sa više boja

Ponovljeni tekstovi poput `Red` u kolonama ne stvaraju sami po sebi vezu niti sprečavaju typo-e (`Red`, `Redd`). Tabela `colors` i FK ograničenja daju jedan autoritativan zapis boje, a povezničke tabele omogućavaju više boja po voću/povrću.

U novoj `:memory:` konekciji možeš pokrenuti:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/04_database_concepts.sql
```

Šema koristi:

- `INTEGER PRIMARY KEY` za ID-jeve;
- `NOT NULL` da naziv ili ID veze ne izostane;
- `UNIQUE` nad `colors.Name` da spreči dupliranje naziva boje;
- složeni PK `(FruitId, ColorId)` ili `(VegetableId, ColorId)` da spreči dupliranje istog para, ali dozvoli više boja po zapisu;
- FK-ove da bi svaki poveznički red pokazivao na postojeće roditeljske zapise kada je `PRAGMA foreign_keys = ON`.

`UNIQUE` nad bojom ne znači automatski case-insensitive poređenje, a FK proveru treba uključiti za svaku konekciju. Ova šema dopušta da voće nema nijednu boju: FK proverava povezničke redove, ali ne nameće najmanje jedan poveznički red za svaki roditelj. To poslovno pravilo traži dodatnu logiku aplikacije ili pažljivo projektovane okidače/ograničenja.

Očekivani rezultat upita za uzorak jabuke jeste dva reda: `Apple | Green` i `Apple | Red`. To je jedan zapis jabuke povezan sa dve boje. ERD:

```mermaid
erDiagram
    fruits ||--o{ fruit_colors : has
    colors ||--o{ fruit_colors : labels
    vegetables ||--o{ vegetable_colors : has
    colors ||--o{ vegetable_colors : labels
```

`o{` označava da je dozvoljeno nula ili više veza sa roditeljske strane; zato dijagram prikazuje šta šema stvarno dopušta, ne poslovnu želju da svako voće ima boju.

### Vežba 3 — Relacije u Chinook-u

**`artists`–`albums`:** jedan umetnik može imati nula ili više albuma; svaki album mora da upućuje na jednog umetnika (`albums.ArtistId NOT NULL`). Uz uključenu FK proveru, taj umetnik mora postojati.

**`albums`–`tracks`:** album može imati nula ili više numera; numera može imati nula ili jedan album jer `tracks.AlbumId` dozvoljava `NULL`. To što trenutni podaci imaju vrednost ne znači da šema zahteva da je vrednost prisutna.

```mermaid
erDiagram
    artists ||..o{ albums : has
    albums |o..o{ tracks : contains
```

Isprekidana veza je neidentifikujuća: FK nije deo PK-a deteta. Proveri stvarne definicije sa `.schema albums`, `.schema tracks` i `.schema playlist_track`. Brojevi redova u bazi su stanje podataka i mogu se menjati.

`playlists`–`tracks` je N:M veza koju razlaže `playlist_track`: svaki red te tabele sadrži `PlaylistId` i `TrackId`; složeni PK sprečava dupliranje istog para, ali dopušta da jedna plejlista sadrži mnogo numera i ista numera bude u više plejlista.

```mermaid
erDiagram
    playlists ||--o{ playlist_track : contains
    tracks ||--o{ playlist_track : appears_in
```

Oba ID-ja u međutabeli su zasebni strani ključevi i zajedno čine složeni primarni ključ. Zato `(PlaylistId, TrackId)` može da se pojavi samo jednom, ali isti `TrackId` može biti u drugoj plejlisti.

Primeri za pregled samo za čitanje:

```sql
SELECT a.AlbumId, a.Title
FROM albums AS a
WHERE NOT EXISTS (
    SELECT 1 FROM tracks AS t WHERE t.AlbumId = a.AlbumId
);

SELECT TrackId, Name
FROM tracks
WHERE AlbumId IS NULL;

SELECT p.PlaylistId, p.Name AS plejlista, t.TrackId, t.Name AS numera
FROM playlists AS p
JOIN playlist_track AS pt ON p.PlaylistId = pt.PlaylistId
JOIN tracks AS t ON t.TrackId = pt.TrackId
WHERE p.PlaylistId = 1
ORDER BY t.TrackId
LIMIT 3;
```

Prvi upit nalazi albume bez povezanih numera; drugi numere bez zabeleženog albuma; treći prikazuje tri numere iz plejliste 1. Poslednji `ORDER BY TrackId` daje stabilan prikaz, ne tvrdi da model čuva redosled numera.

### Vežba 4 — Poveži Chinook sa ORM pojmovima

| Pojam              | Primer                                                                                                                     |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| SQLAlchemy model   | Klasa `Album` mapirana na `albums`.                                                                                        |
| Red / ORM instanca | Red sa `AlbumId = 1`, naslovom `For Those About To Rock We Salute You` i `ArtistId = 1`; Python objekat je instanca klase. |
| Mapirani atribut   | `Album.title` može mapirati SQL kolonu `albums.Title`.                                                                     |
| Pydantic odgovor   | `AlbumResponse` sa `album_id`, `title`, `artist_id`.                                                                       |
| FK                 | `albums.ArtistId` ka `artists.ArtistId`.                                                                                   |

Ilustrativni model:

```python
from pydantic import BaseModel, ConfigDict
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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

Klasa mapira tabelu; instanca predstavlja jedan zapis. Samo pravljenje Python objekta ne upisuje ga u bazu. `ForeignKey` opisuje baznu vezu; ORM `relationship()` je drugi, opciono dodati mehanizam za navigaciju između objekata. Ovaj skraćeni primer pretpostavlja da je tabela `artists` takođe definisana ili reflektovana kada se kompletna šema pravi.

### Vežba 5 — Putanja podatka

```mermaid
flowchart TD
    client["Klijent: POST /albums"] --> fastapi["FastAPI prima zahtev"]
    fastapi --> input["Pydantic validira AlbumCreate"]
    input --> endpoint["Endpoint primenjuje pravila"]
    endpoint --> orm["SQLAlchemy: Album + Session"]
    orm --> driver["sqlite3 drajver"]
    driver --> table[("SQLite tabela albums")]
    table --> driver
    driver --> orm
    orm --> output["Pydantic: AlbumResponse"]
    output --> response["FastAPI vraća JSON"]
    response --> client
```

Pydantic proverava oblik/tip ulaznih podataka, ne postojanje `artist_id`. Endpoint/servis pravi ORM instancu. SQLAlchemy i drajver predaju SQL SQLite-u. SQLite primenjuje ograničenja tabele; FK kontrola zahteva da bude uključena na konekciji. Nakon uspešnog `commit()` aplikacija može pripremiti odgovor, dok greška treba da vodi u rollback i odgovor koji ne tvrdi da je upis uspeo. Ovo je primer toka, ne postojeći endpoint u TodoApp-u i ne treba ga izvršavati nad Chinook bazom.

---

## 7. Kratka provera razumevanja

Pre nego što završiš, probaj bez gledanja u rešenja da odgovoriš:

1. Da li `.sql` ili `.txt` fajl sam po sebi otvara bazu? **Ne** — klijent mora da ga učita/izvrši.
2. Da li `rlwrap` izvršava SQL? **Ne** — prosleđuje unos programu `sqlite3`.
3. Gde se unosi `.read`? **U SQLite CLI promptu**, ne u Bash-u.
4. Da li `.tables` SQL naredba? **Ne**, to je SQLite CLI dot-komanda.
5. Da li dve konekcije sa istim nazivom `chinook.db` sigurno vide isti fajl? **Ne** — moraju imati istu putanju.
6. Da li treba praviti tabele iz Vežbe 2 u Chinook-u? **Ne** — koristi novu `:memory:` sesiju.
