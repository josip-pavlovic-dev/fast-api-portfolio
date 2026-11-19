# SQLite CLI, SQLTools i SQLite Viewer u VS Code-u

Ovo uputstvo pokriva dva načina rada sa SQLite bazom:

1. `sqlite3` komandni alat u Linux/WSL terminalu.
2. SQLite Viewer za pregled baze i SQLTools sa SQLite drajverom za izvršavanje upita.

Ekstenzija ne zamenjuje CLI: terminal je koristan za komande, skripte i brzu proveru, a ekstenzija za pregled baze i SQL upite iz editora.

Napomena: u ovom uputstvu se pretpostavlja da je SQLite CLI instaliran u `~/.local/bin/sqlite3` i da je VS Code podešen za rad sa WSL okruženjem.

---

## Trenutno stanje

| Alat                                      | Stanje                                                                                                                                                  |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SQLite CLI                                | `3.54.1`, instaliran u `~/.local/bin/sqlite3`.                                                                                                          |
| SQLite Viewer, SQLTools i SQLTools SQLite | Instalirani za rad u VS Code/WSL okruženju.                                                                                                             |
| Node.js i npm                             | Dostupni u WSL-u; u trenutku provere `v24.11.0` i `11.6.1`.                                                                                             |
| SQLTools runtime                          | U profilnim podešavanjima `AI-WORKFLOW` podešeno je `"sqltools.useNodeRuntime": true`.                                                                  |
| `ChinookPractice`                         | Konekcija je sačuvana u workspace podešavanjima i pokazuje na radnu kopiju `chinook_practice.db`. Sačuvana konekcija nije isto što i aktivna konekcija. |

SQLite CLI i Python-ov `sqlite3` modul nisu isto. Aktiviranje `.venv` okruženja ne menja CLI niti SQLite biblioteku koju koristi Python. Ni SQLTools SQLite drajver ne mora da koristi istu verziju SQLite-a kao CLI.

---

## 1. SQLite CLI u terminalu

### Proveri CLI i njegovu putanju

U terminalu projekta pokreni:

```bash
command -v sqlite3
sqlite3 --version
```

Očekivana putanja instalacije iz ovog uputstva je `~/.local/bin/sqlite3`, a verzija je `3.54.1`. Ako terminal i dalje nalazi `/usr/bin/sqlite3`, otvori novi terminal ili proveri da li je `~/.local/bin` ispred `/usr/bin` u `PATH`:

Za proveru trenutnog `PATH` i redosleda direktorijuma u njemu, koristi sledeću komandu:

```bash
printf '%s\n' "$PATH"
```

Ako `command -v sqlite3` već pokazuje na `~/.local/bin/sqlite3` i `sqlite3 --version` prikazuje očekivanu verziju, **ne moraš ponovo podešavati `PATH`**. Dovoljno je da `~/.local/bin` bude pre direktorijuma sa drugim `sqlite3` programom, ne mora biti prvi: aktivirani `.venv/bin` može biti ispred njega.

Ako terminal nalazi staru verziju zato što je `/usr/bin` ispred `~/.local/bin`, dodaj `~/.local/bin` na početak `PATH` kao u nastavku.
Napomena: nakon promene `PATH`, otvori novi terminal ili izvrši `source ~/.bashrc` (ili `source ~/.zshrc` za Zsh) da bi promene stupile na snagu. Ovo je važno jer VS Code terminal može zadržati prethodni `PATH` dok se ne otvori novi terminal ili dok se ne izvrši odgovarajući `source` fajl.

Komanda za dodavanje `~/.local/bin` na početak `PATH` u Bash okruženju i osvežavanje trenutnog terminala je:

```bash
grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" ||
  printf '%s\n' 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
source "$HOME/.bashrc"
hash -r
sqlite3 --version
```

Ako koristiš Zsh, istu `export PATH=...` liniju dodaj u `~/.zshrc`.

---

### Aktiviranje `.venv`

Za Python komande i aplikaciju aktiviraj projektno virtuelno okruženje:

```bash
source .venv/bin/activate
```

SQLite CLI je nezavisan od `.venv`; možeš ga koristiti i bez aktiviranog okruženja. U ovom projektu `.venv` se aktivira pre Python komandi, a SQLite se pokreće zasebno.

---

### Otvori bazu

Pokreni komandu iz korena repozitorijuma. Na primer, za praznu bazu za vežbe:

```bash
sqlite3 fast-api-course-my-work/sqlite_for_beginners/playground/databases/sandbox.db
```

Ako fajl baze ne postoji, SQLite će ga napraviti. Zato proveri putanju pre pokretanja komande — tipografska greška može nenamerno napraviti novu praznu bazu.

U SQLite prompt-u možeš koristiti SQL:

```sql
SELECT sqlite_version();
```

i SQLite CLI dot-komande:

```text
.help
.tables
.schema
.quit
```

Dot-komande počinju tačkom i pripadaju `sqlite3` alatu; nisu standardni SQL i ne rade u svim SQL editorima.

---

### Korisne CLI komande

| Komanda                                | Namena                                           |
| -------------------------------------- | ------------------------------------------------ |
| `sqlite3 putanja/do/baze.db`           | Otvori bazu ili napravi novu na toj putanji.     |
| `sqlite3 -readonly putanja/do/baze.db` | Otvori postojeću bazu samo za čitanje.           |
| `.tables`                              | Prikaži tabele i poglede.                        |
| `.schema`                              | Prikaži SQL kojim je definisana šema.            |
| `.headers on`                          | Uključi nazive kolona u rezultatima.             |
| `.mode box`                            | Prikaži rezultate u tabelarnom obliku.           |
| `.read putanja/do/skripte.sql`         | Izvrši SQL skriptu nad trenutno otvorenom bazom. |
| `.backup putanja/do/kopije.db`         | Napravi SQLite rezervnu kopiju.                  |
| `.quit`                                | Zatvori SQLite prompt.                           |

Primer interaktivnog pregleda:

```sql
.headers on
.mode box
.tables
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```

Za izlaz iz prompt-a možeš koristiti i `Ctrl+D`.

### Izvršavanje `.sql` fajla

`.sql` fajl je tekstualna skripta, dok je `.db` fajl baze. Otvori željenu bazu, a zatim u SQLite prompt-u izvrši:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/01_what_is_sqlite.sql
```

Skripta utiče na bazu koja je trenutno otvorena. Proveri sadržaj i putanju baze pre izvršavanja, posebno ako skripta sadrži `INSERT`, `UPDATE`, `DELETE`, `DROP` ili `CREATE`.

---

### Instalacija najnovije zvanične verzije na Ubuntu x86_64

SQLite izdaje zvanične CLI pakete na [sqlite.org/download.html](https://sqlite.org/download.html). Paket za Linux x64 je ZIP arhiva koja sadrži `sqlite3` i druge alate. Broj verzije i putanja arhive se menjaju pri novom izdanju.

Sledeći primer koristi verziju `3.54.1` koja je najnovija u ovom okruženju u vreme pisanja. Proveri aktuelnu verziju na zvaničnoj stranici pre nego što prilagodiš adresu za buduće izdanje.

```bash
source .venv/bin/activate
mkdir -p "$HOME/Downloads/sqlite-3.54.1" "$HOME/.local/bin"
cd "$HOME/Downloads/sqlite-3.54.1"

curl -fLO https://sqlite.org/2026/sqlite-tools-linux-x64-3540100.zip
python - <<'PY'
from pathlib import Path
from zipfile import ZipFile

archive = Path("sqlite-tools-linux-x64-3540100.zip")
with ZipFile(archive) as bundle:
    entry = next(
        (name for name in bundle.namelist() if name.rsplit("/", 1)[-1] == "sqlite3"),
        None,
    )
    if entry is None:
        raise SystemExit("Arhiva ne sadrži sqlite3 CLI")
    bundle.extract(entry, ".")
    extracted = Path(entry)
    if extracted != Path("sqlite3"):
        extracted.replace("sqlite3")
PY

install -m 755 sqlite3 "$HOME/.local/bin/sqlite3"
"$HOME/.local/bin/sqlite3" --version
```

Ovaj primer je za arhitekturu `x86_64` (`uname -m`). Nemoj koristiti x64 binarni paket na ARM uređaju. Instalacija u `~/.local/bin` ne zamenjuje sistemski paket u `/usr/bin` i ne zahteva `sudo`; putanja `~/.local/bin` mora biti u `PATH` da bi se nova verzija pronašla komandom `sqlite3`.

---

## 2. Alati za rad u VS Code-u

| Alat                                                                                                                                                                               | Za šta ga koristiš                                                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| [SQLite Viewer](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer)                                                                                           | Vizuelni pregled tabela i redova u `.db` fajlu; besplatni pregled je samo za čitanje i ne pokreće SQL upite. |
| [SQLTools](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools) + [SQLTools SQLite](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools-driver-sqlite) | Konekcija, pregled šeme i izvršavanje SQL upita iz editora.                                                  |
| `sqlite3` CLI                                                                                                                                                                      | SQL i SQLite dot-komande iz terminala; potreban za CLI delove lekcija.                                       |

Ekstenzija **SQLite** izdavača alexcvzz nije potrebna za ovaj workflow; njene `SQLite: ...` komande nisu komande SQLTools-a.

---

### Profil, WSL i Node.js

Otvori repo u WSL prozoru i koristi profil **AI-WORKFLOW**. U Extensions panelu (`Ctrl+Shift+X`) proveri da su navedene ekstenzije dostupne i uključene u tom prozoru. Ako VS Code za rad nad WSL fajlovima ponudi **Install in WSL**, instaliraj potrebnu ekstenziju u WSL-u.

U profilnom User Settings-u već je dodato:

```json
"sqltools.useNodeRuntime": true
```

Time SQLTools pokušava automatski da pronađe Node.js. Ako ga ne pronađe, u WSL terminalu proveri `command -v node`, `node --version` i `npm --version`. Zvanična dokumentacija dopušta i apsolutnu putanju do Node programa umesto `true`; WSL putanja je specifična za WSL i može se promeniti nakon nadogradnje Node-a preko nvm-a.

VS Code u WSL prozoru koristi profilna Windows podešavanja kao osnovu. WSL **Remote Settings** se takođe koriste i mogu nadjačati odgovarajuća korisnička podešavanja; workspace podešavanja mogu dodatno uticati na rezultat. Nemoj dodavati duple stavke naslepo.

Prilikom prvog korišćenja SQLite drajver može zatražiti dozvolu da instalira svoj Node `sqlite3` paket. To nije isto što i CLI `sqlite3`, niti Python-ov modul. Drajver može koristiti drugu SQLite verziju od CLI-ja. Ako instalacija ili povezivanje ne uspeju, pročitaj poruku i SQLTools log pre ponovnog pokušaja.

---

### Sačuvana konekcija `ChinookPractice`

U [workspace podešavanjima](../../../../.vscode/settings.json) je preko SQLTools Connection Assistant-a sačuvana konekcija:

```json
{
  "previewLimit": 50,
  "driver": "SQLite",
  "name": "ChinookPractice",
  "database": "${workspaceFolder:fast-api-portfolio}/fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db"
}
```

Ovo je jedan objekat unutar `sqltools.connections`, ne sadržaj celog `settings.json`. Izbor apsolutne putanje u asistentu pretvoren je u workspace promenljivu; VS Code je razrešava prema otvorenom folderu nazvanom `fast-api-portfolio`. Ako drugačije otvoriš ili preimenuješ workspace folder, proveri putanju u podešavanjima konekcije.

`previewLimit: 50` je podrazumevano ograničenje pregleda redova u SQLTools-u, ne menja podatke i ne zamenjuje eksplicitni `LIMIT` u tvojim upitima.

**Sačuvano ne znači povezano:** klikni **Connect Now** u asistentu ili u SQLTools panelu izaberi `ChinookPractice` i poveži se. Uspešan upit potvrđuje rad konekcije; prekid konekcije ne briše fajl.

---

### SQLTools: prvi upit korak po korak

1. Otvori **SQLTools** u bočnoj traci i u **Connections** pronađi `ChinookPractice`.
2. Poveži se klikom na konekciju ili kroz **SQLTools: Connect** iz Command Palette-a (`Ctrl+Shift+P`). Proširi konekciju da vidiš tabele.
3. Otvori SQL fajl za lekciju u `playground/sql/00_intro/`, na primer [01_what_is_sqlite.sql](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/01_what_is_sqlite.sql).
4. U tom fajlu već postoje blokovi za vežbe. Za prvi pregled pronađi blok **Vežba 1: Tražene tabele** ili u posebnom SQL dokumentu upiši:

   ```sql
   SELECT name
   FROM sqlite_schema
   WHERE type = 'table'
   ORDER BY name;
   ```

5. Označi samo taj upit i iz Command Palette-a pokreni **SQLTools Connection: Run Selected Query**. Ako te VS Code pita za konekciju, izaberi `ChinookPractice`. Podrazumevana prečica za označen upit je `Ctrl+E`, zatim `Ctrl+E`; moguće je da tvoje prečice budu drugačije.
6. U rezultatu proveri, na primer, tabele `artists`, `albums` i `tracks`. Sačuvaj `.sql` fajl da sačuvaš svoj rad.

**Run Selected Query** izvršava označeno; **Run Current Query** izvršava trenutni upit, a **Run This File** može izvršiti ceo fajl. Posebno proveri izbor i konekciju pre pokretanja fajla sa više naredbi. Upisivanje SQL-a u fajl ne izvršava ga samo po sebi.

U fajlu `01_what_is_sqlite.sql` svaki `-- @block` označava poseban SQLTools blok. Klikni **Run on active connection** iznad željenog bloka, nakon što proveriš da je `ChinookPractice` aktivna. **Select block** samo označava blok. Ako nema `@block` oznaka, SQLTools može tretirati ceo fajl kao jedan blok, a ne svaki upit zasebno.

Proveri na koji je fajl aktivna SQLTools konekcija otvorena:

```sql
PRAGMA database_list;
```

U redu `main` putanja treba da završava sa `playground/databases/chinook_practice.db`. `PRAGMA` je SQLite SQL naredba i možeš je izvršiti u SQLTools-u; `.tables`, `.schema` i `.databases` su CLI dot-komande, ne SQLTools komande.

---

### SQL session fajl i lokacija upita

SQLTools može otvoriti SQL session fajl za pisanje upita, na primer `ChinookPractice.session.sql`. Taj fajl je **tekstualni fajl sa upitima**, nije baza niti definicija konekcije. U ovom projektu premešten je u [playground/sql](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/sql/).

Lokacija SQL fajla ne određuje automatski koja će baza izvršiti upit. I iz session fajla i iz `sql/00_intro/01_what_is_sqlite.sql` možeš raditi nad `ChinookPractice`, ako je upravo ona izabrana kao aktivna konekcija. Premeštanje ili brisanje SQL fajla ne briše bazu ni sačuvanu konekciju; brisanjem SQL fajla gubiš upite koje si u njemu sačuvao.

Za vežbe koristi odgovarajući `.sql` fajl iz `sql/00_intro/`, a session fajl po potrebi za privremene upite. Ako se session fajl pojavi u korenu repozitorijuma, možeš ga premestiti kroz VS Code Explorer (**Cut** → **Paste**). Ne mora da znači da ga je tamo smestio trenutni direktorijum terminala.

---

### SQLite Viewer: pregled baze

1. U VS Code Explorer-u pronađi [chinook_practice.db](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db).
2. Otvori fajl; ako se ne otvori vizuelni prikaz, desni klik na fajl → **Open With...** → **SQLite Viewer**.
3. Izaberi `artists`, `albums` ili `tracks` i pogledaj kolone i redove. Uporedi npr. `ArtistId` u `albums` sa odgovarajućom kolonom u `artists`.
4. Viewer koristi za čitanje i pregled, a SQLTools za SQL. Pregled je keširan: ako drugi alat izmeni bazu, ponovo učitaj prikaz i proveri aktuelno stanje.

---

## 3. Vežbe iz oblasti `00_intro`

### Priprema za svaku lekciju

1. Otvori [lekcije oblasti 00](../../../../fast-api-course-my-work/sqlite_for_beginners/00_intro/README.md) i pročitaj zadatke u odeljku **Vežbe**.
2. Rešenja čuvaj u odgovarajućem `.sql` šablonu u [playground/sql/00_intro](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/). Tekstualne odgovore i dijagrame možeš zapisati kao SQL komentare koji počinju sa `--`.
3. Za pregled u SQLTools-u poveži `ChinookPractice`; u SQLite Viewer-u otvori isti fajl.
4. Primeri u pojedinim lekcijama koriste **original** `chinook/chinook.db`. Za pregled i bezbedan rad možeš koristiti radnu kopiju `playground/databases/chinook_practice.db`; kada zadatak traži originalnu putanju, jasno zabeleži koju si od njih koristio. Ne menjaj original.
5. CLI komande ispod pokreću se iz korena repozitorijuma. U WSL terminalu proveri `pwd`, pa po želji aktiviraj projektni `.venv`:

   ```bash
   source .venv/bin/activate
   ```

   Aktivacija ne menja SQLite CLI. Iz CLI-ja se vraćaš u Bash pomoću `.quit`.

---

### Lekcija 01 — Šta je SQLite

- **Pronalaženje baze i tabela:** u SQLTools-u se poveži na `ChinookPractice` i proširi tabele; u SQLite Viewer-u otvori isti fajl. Za zadatak koji izričito traži CLI proveri i `.databases` i `.tables`:

  ```bash
  sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
  ```

  U SQLite prompt-u:

  ```text
  .databases
  .tables
  .schema albums
  .schema tracks
  .schema playlist_track
  ```

- **Šema i ključevi:** `.schema` je najbolji način da ispuniš CLI deo vežbe. Uporedi ga sa [ERD dijagramom](../../../../fast-api-course-my-work/sqlite_for_beginners/chinook/ERD.drawio). U SQLTools-u dodatno možeš označiti i zasebno izvršiti:

  ```sql
  PRAGMA table_info(albums);
  PRAGMA foreign_key_list(albums);
  ```

  Za ostale tabele zameni ime u zagradi. Na osnovu izlaza samostalno zapiši primarne i strane ključeve.

- **Verzija i strani ključevi:** u CLI-ju pokreni `SELECT sqlite_version();` i `PRAGMA foreign_keys;`. Ako ih ponoviš u SQLTools-u, rezultat se može razlikovati: svaki alat može koristiti drugu SQLite biblioteku i zasebnu konekciju, a `foreign_keys` je podešavanje konekcije.
- **Scenariji i FastAPI:** odgovore i dijagram napiši u komentarima u [01_what_is_sqlite.sql](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/01_what_is_sqlite.sql) ili u svojim beleškama; ekstenzija nije potrebna da bi se opisali slojevi aplikacije.

---

### Lekcija 02 — Otvaranje i priključivanje baze

- **Otvori bazu:** sa `ChinookPractice` otvaraš radnu kopiju kao glavnu bazu SQLTools konekcije. U SQLTools-u izvrši `PRAGMA database_list;` i proveri red `main`. Za CLI deo pokreni istu kopiju komandom iz prethodne lekcije, zatim `.databases`, `.tables` i `.schema albums`.
- **`ATTACH` nije isto što i Connect:** SQLTools konekcija otvara glavni fajl. Vežbu priključivanja dodatne baze uradi u CLI-ju nad privremenom memorijskom bazom, iz korena repozitorijuma:

  ```bash
  sqlite3 :memory:
  ```

  U SQLite prompt-u:

  ```sql
  ATTACH DATABASE 'fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db' AS chinook;
  ```

  Zatim pokreni `.databases`, pa upit:

  ```sql
  SELECT Name FROM chinook.artists ORDER BY Name LIMIT 5;
  ```

  Na kraju izvrši `DETACH DATABASE chinook;`, ponovi `.databases` i izađi sa `.quit`. `ATTACH` ne kopira podatke, a `DETACH` ne briše fajl. Alias postoji samo u toj konekciji; SQLTools ima zasebnu konekciju i neće automatski videti alias iz CLI-ja.

- **Relativne putanje:** uradi promenu direktorijuma po zadatku i zapiši kako se putanja razrešava. Pre otvaranja proveri da fajl postoji; pogrešna putanja može napraviti novu praznu bazu. Skice i beleške sačuvaj u [02_attaching_sample_database_to_sqlite.sql](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/02_attaching_sample_database_to_sqlite.sql).

---

### Lekcija 03 — Povezivanje sa SQLite bazom

- U SQLTools-u proveri sačuvanu konekciju i izvrši `PRAGMA database_list;`; u CLI-ju na radnoj kopiji uporedi `.databases`, `.tables` i `.schema albums`. Ovo su zasebne konekcije ka istom fajlu ako se njihove putanje poklapaju.

- Uporedi CLI i SQLTools ili SQLite Viewer: kako biraš bazu, vidiš tabele i zatvaraš konekciju. U SQLTools-u koristi **SQLTools: Disconnect**; u CLI-ju `.quit`. Zatvaranje ne briše bazu.

- U kodu projekta pronađi URL baze koju koristi FastAPI/SQLAlchemy. Uporedi ga sa putanjom `ChinookPractice`, vodeći računa o trenutnom radnom direktorijumu i konfiguraciji. Svoje odgovore i dijagrame upiši u [03_how_to_connect_to_sqlite.sql](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/03_how_to_connect_to_sqlite.sql).

---

### Lekcija 04 — Pojmovi baza podataka

- U SQLite Viewer-u otvori tabelu `albums`: kolone predstavljaju osobine zapisa, a svaki red jedan zapis. U SQLTools-u uporedi pregled sa SQL upitom:

  ```sql
  SELECT AlbumId, Title, ArtistId
  FROM albums
  LIMIT 5;
  ```

- Koristi SQLTools pregled šeme ili CLI `.schema albums`, `.schema tracks` i `.schema playlist_track`, pa uporedi ključeve sa [ERD dijagramom](../../../../fast-api-course-my-work/sqlite_for_beginners/chinook/ERD.drawio). Naročito prouči zašto `playlist_track` povezuje plejlistu i numeru.

- Primeri `fruits`, `vegetables` i `colors` služe za razmišljanje o modelu; ne moraš ih stvarati u Chinook bazi. Tekst, predlog modela, Mermaid dijagram i ORM/Pydantic poređenje sačuvaj u komentarima [04_database_concepts.sql](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/04_database_concepts.sql) ili u beleškama.

---

## 4. Kako završiti rad i sledeći put nastaviti

**Prekidanje SQLTools konekcije je preporučeno kada završiš, ali nije obavezno posle svakog upita.** Sačuvani profil konekcije možeš zadržati da ne unosiš putanju ponovo.

1. Sačuvaj izmene u `.sql` fajlovima (`Ctrl+S`).
2. Ako si namerno otvorio transakciju koja još traje, prvo proveri šta želiš sa njom i izvrši `COMMIT` za potvrdu ili `ROLLBACK` za poništavanje. Samo čuvanje `.sql` fajla ne potvrđuje transakciju u bazi.
3. U SQLTools-u prekini aktivnu konekciju: otvori Command Palette (`Ctrl+Shift+P`), izaberi **SQLTools: Disconnect** i, ako se pojavi izbor, izaberi `ChinookPractice`. Možeš koristiti i dugme za prekid pored povezane konekcije u SQLTools panelu.
4. Zatvori tab sa rezultatima, `.sql` fajl ili SQLite Viewer ako ti više nisu potrebni. Zatvaranje taba SQL fajla nije isto što i prekid SQLTools konekcije.
5. Ako je SQLite CLI otvoren u terminalu i vidiš `sqlite>` prompt, izvrši `.quit`. To zatvara samo CLI konekciju i vraća te u Bash; ne zatvara zasebnu SQLTools konekciju.
6. Ako želiš da napustiš Python virtuelno okruženje, u Bash-u pokreni `deactivate`. To je opciono i ne prekida SQLTools konekciju.

Kada sledeći put vežbaš, otvori projekat u WSL-u, u SQLTools panelu ponovo poveži **ChinookPractice**, otvori SQL fajl i pokreni željeni blok. Ako koristiš CLI, ponovo otvori odgovarajući `.db` fajl.

| Radnja | Šta ostaje |
| --- | --- |
| **Disconnect** | Sačuvana SQLTools konekcija, SQL fajlovi i baza ostaju. |
| **Delete Connection** | Uklanja sačuvanu SQLTools konfiguraciju; ne briše `.db` fajl ni SQL fajlove. Koristi je samo ako zaista više ne želiš sačuvanu konekciju. |
| Brisanje `.session.sql` | Briše taj fajl i upite u njemu, ali ne briše bazu ni konekciju. |
| `.quit` u CLI-ju | Zatvara CLI i njegovu konekciju; SQLTools konekcija se ne menja. |

---

## 5. Bezbednost i česti problemi

- `chinook_practice.db` je radna kopija, a `sandbox.db` služi za eksperimente. Pre izmena napravi rezervnu kopiju pomoću SQLite `.backup`; ne zamenjuj radnu kopiju originalom ako želiš da sačuvaš svoje izmene.

- `SELECT` i `PRAGMA` za pregled ne menjaju redove. `INSERT`, `UPDATE`, `DELETE`, `DROP` i drugi upiti za izmene rade nad **izabranom** bazom, čak i ako su pokrenuti iz `.sql` fajla.

- Nemoj brisati `-wal` ili `-shm` dok je baza u upotrebi. Za kopiju aktivne baze koristi SQLite `.backup`, a ne samo kopiranje glavnog fajla.

- **Konekcija ne radi:** proveri da je VS Code u WSL-u, da je `ChinookPractice` sačuvana i izabrana, i da je putanja do postojećeg fajla ispravna. U Command Palette-u pokreni **SQLTools Management: Show Output Channel Logs** i pročitaj grešku.

- **Marketplace i dalje nudi Install:** prethodna CLI provera pokazala je ekstenziju u jednom kontekstu, ali nije potvrdila da je dostupna u aktivnom Windows profilu i WSL prozoru. Proveri profil **AI-WORKFLOW** i Extensions panel u prozoru u kom radiš, pa instaliraj ekstenziju tamo gde VS Code ponudi da je potrebna.

- **Node runtime nije pronađen:** proveri `node --version`, `npm --version` i efektivnu vrednost `sqltools.useNodeRuntime`; po potrebi ponovo učitaj VS Code prozor. Ne instaliraj Node ponovo ako ga WSL već ima.

- **SQLite CLI prikazuje novu verziju iako ga nisi ručno instalirao:** CLI `3.54.1` već je instaliran u WSL-u u `~/.local/bin`. Proveri `command -v sqlite3` i `sqlite3 --version`; nema potrebe da ponavljaš instalaciju ako koristiš očekivanu verziju.

- **Ne vidiš očekivane tabele:** pokreni `PRAGMA database_list;` u SQLTools-u ili `.databases` u CLI-ju. `sandbox.db` može biti prazan, a pogrešna putanja može otvoriti drugu praznu bazu.

- **Upit nije pokrenut ili je pokrenut nad pogrešnom bazom:** označi upit, proveri aktivnu konekciju i koristi **SQLTools Connection: Run Selected Query**. Proveri rezultat i log.
- **`SQLITE_MISUSE: not an error`:** pri pokretanju cele prethodne verzije vežbe SQLTools je prijavio grešku jer su posle poslednje naredbe ostali samo komentari. SQLTools SQLite drajver može pokušati da ih izvrši kao zasebnu naredbu. Fajl je preuređen u `-- @block` blokove sa SQL naredbama na kraju; korisnik je potvrdio da sada funkcioniše. Kod drugih fajlova označi samo SQL naredbu ili razdvoji blokove tako da u izvršenom bloku ne ostanu samo komentari posle poslednjeg upita. Pogledaj [SQLTools issue 1324](https://github.com/mtxr/vscode-sqltools/issues/1324).

- **Verzije se razlikuju:** `sqlite3 --version` pokazuje CLI. `SELECT sqlite_version();` iz SQLTools-a pokazuje SQLite verziju koju koristi ta konekcija, ne nužno CLI verziju.

---

## Izvori

- [SQLite CLI dokumentacija](https://sqlite.org/cli.html)
- [SQLite downloads](https://sqlite.org/download.html)
- [SQLite Viewer na Visual Studio Marketplace-u](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer)
- [SQLTools na Visual Studio Marketplace-u](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools)
- [SQLTools SQLite drajver — početni vodič](https://vscode-sqltools.mteixeira.dev/en/drivers/sq-lite.html)
