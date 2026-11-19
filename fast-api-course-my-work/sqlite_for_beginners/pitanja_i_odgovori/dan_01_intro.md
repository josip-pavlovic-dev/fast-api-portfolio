# Pitanja i odgovori - Dan 01: Uvod u SQLite

## Pitanje 1

- Da li **SQLite** ima bazu implementiranu u sebe ili SQLite biblioteka može samo da kreira, čita i manipuliše bazom?

## Odgovor 1

**Kratko objašnjenje:**

- SQLite je **softverska biblioteka**, a **ne** samostalna baza podataka.
- Sama biblioteka **ne sadrži podatke**; ona samo izvršava SQL naredbe i upravlja fajlovima baza koje aplikacija otvori.
- Podaci se čuvaju u **zasebnim fajlovima** koje SQLite biblioteka kreira, čita i menja prema zahtevima aplikacije.
- SQLite **nema** bazu implementiranu u sebi. SQLite je softverska biblioteka koja **omogućava aplikaciji da kreira, čita i menja baze podataka, najčešće sačuvane u zasebnim fajlovima**. Sama biblioteka **ne sadrži podatke**, već samo **izvršava** SQL naredbe koje dobija od aplikacije i **upravlja** fajlovima baza koje aplikacija otvori.

---

### Ključna razlika između SQLite biblioteke i baze podataka

**SQLite biblioteka omogućava da kreiraš, čitaš i menjaš baze**, ali sama biblioteka nije jedna konkretna baza sa tvojim podacima.

Možeš to da zamisliš ovako:

```text
Aplikacija → SQLite biblioteka → fajl baze (npr. chinook.db)
```

- **SQLite biblioteka** je softver koji razume SQL i upravlja podacima.
- **Baza** je skup podataka i struktura poput tabela i indeksa, koji se najčešće čuvaju u posebnom fajlu.
- Ista biblioteka može da otvori različite baze, a baza može postojati nezavisno od same biblioteke u fajlovima na disku.

Dakle, formulacija „baza podataka koja je implementirana unutar njega“ nije tačna. SQLite **nije samostalna baza podataka**, već softverska biblioteka koja omogućava aplikaciji da kreira, čita i menja baze podataka.

Zato je preciznije reći:

> SQLite je softver koji izvršava SQL naredbe i upravlja bazama podataka, najčešće sačuvanim u zasebnim fajlovima. Njegova biblioteka izvršava se unutar aplikacije koja je koristi, bez zasebnog serverskog procesa.
>
> Ukratko, SQLite nije samostalna baza podataka. To je **biblioteka koja omogućava aplikaciji da kreira, čita i menja baze podataka**. Podaci se čuvaju u fajlovima koje biblioteka upravlja, a sama biblioteka **ne sadrži podatke**.

---

## Pitanje 2

Koja je razlika između `.sql` baze i `.db` baze?

---

## Odgovor 2

**Kratko objašnjenje:**

- `.sql` fajl obično sadrži **tekstualni SQL kod**, kao što su naredbe za kreiranje tabela, ubacivanje podataka i druge SQL operacije. To nije sama baza podataka, već skripta koja može da se izvrši nad bazom. Njen sadržaj se koristi za kreiranje ili modifikovanje stvarne baze podataka, ali sam `.sql` fajl ne sadrži podatke u binarnom obliku kao što to čini `.db` fajl.

- `.db` fajl je **fajl koji sadrži stvarnu SQLite bazu podataka**, uključujući tabele, indekse i podatke. To je binarni fajl koji SQLite biblioteka može da otvori i manipuliše njime.

- Ukratko, `.sql` je **tekstualna skripta** sa SQL naredbama, dok je `.db` **stvarna baza podataka** sa tabelama, indeksima i podacima.

**Napomena:** `.sql` fajl može se koristiti za kreiranje ili popunjavanje `.db` baze tako što se izvrši nad SQLite bibliotekom ili drugim alatima koji podržavaju SQL.

- `.sql` može sadržati naredbe poput `CREATE TABLE`, `INSERT` ili `SELECT`. Izvršavanjem tih naredbi nad bazom možeš napraviti strukturu ili izmeniti podatke. U tvom primeru `01_what_is_sqlite.sql` trenutno je samo šablon sa komentarom.

- `.db` u ovom projektu je SQLite baza — binarna datoteka koju otvara SQLite alat, a ne običan tekstualni editor. `sandbox.db` je predviđena za eksperimente; `README` objašnjava kako se koristi.

Dakle, **`.sql` opisuje šta da se uradi, a `.db` čuva bazu i njene podatke**. Ekstenzija `.db` je čest naziv za SQLite bazu, ali sama po sebi ne garantuje koji je format.

---

## Pitanje 3

Da li treba da radim vežbe preko ekstenzija koje smo instalirali ili preko terminala ili da radim i u terminalu i sa ekstenzijama. Kada smo pravili .md skripte ekstenzije nisu bile instalirane ali u playground-u sve baze i .sql fajlovi prate teoriju iz `fast-api-course-my-work/sqlite_for_beginners`. Koji je preporučeni način rada u ovom slučaju?

Takođe, u terminalu kada uđem u `sqlite3` nemam na TAB da mi dovrši komande, npr. `.databa` TAB u `.database`. Koji je razlog za to i da li postoji način da se omogući automatsko dovršavanje komandi u SQLite CLI?

---

## Odgovor 3

Preporučeni način rada zavisi od tvojih ciljeva i okruženja. Ako želiš da pratiš teoriju i vežbaš u `playground`-u, ekstenzije mogu biti zgodne jer omogućavaju lakše upravljanje bazama i izvršavanje SQL skripti direktno iz editora. Terminal je koristan za razumevanje osnovnog rada sa SQLite CLI i za situacije kada želiš da radiš van editora. Najbolje je kombinovati oba pristupa: koristi ekstenzije za brži rad i preglednost, a terminal za učenje osnovnih komandi i rada sa SQLite direktno.

Što se tiče automatskog dovršavanja komandi u SQLite CLI, standardni SQLite CLI ne podržava TAB dovršavanje komandi. To je razlog zašto ti `.databa` TAB ne dovršava u `.database`. Postoje alternativni alati i ekstenzije koje omogućavaju automatsko dovršavanje, kao što su `rlwrap` ili korišćenje SQLite u okviru naprednijih terminala ili IDE ekstenzija koje podržavaju ovu funkcionalnost.
Ako želiš da koristiš automatsko dovršavanje u terminalu, možeš instalirati `rlwrap` i pokrenuti SQLite sa njim, na primer:

```bash
rlwrap sqlite3 sandbox.db
```

Ovo će omogućiti TAB dovršavanje komandi u SQLite CLI. Imaj na umu da `rlwrap` radi kao omotač oko SQLite CLI, pa će sve komande koje uneseš biti sačuvane u istoriji i moći ćeš da koristiš strelice za navigaciju kroz prethodne komande, što dodatno olakšava rad u terminalu.

Ako želiš da trajno omogućiš automatsko dovršavanje komandi bez potrebe za `rlwrap`-om svaki put, možeš istražiti naprednije SQLite CLI alternative ili koristiti terminale i IDE ekstenzije koje imaju ugrađeno automatsko dovršavanje. Na primer, neki moderni terminali i SQLite GUI alati već imaju podršku za automatsko dovršavanje, što može značajno ubrzati rad i smanjiti greške pri unosu komandi.

U svakom slučaju, kombinovanje rada u terminalu i korišćenja ekstenzija ili GUI alata pruža najbolju fleksibilnost i omogućava ti da učiš osnove dok istovremeno koristiš pogodnosti modernih alata za brži i efikasniji rad sa SQLite bazama. Na taj način možeš razvijati svoje veštine u radu sa bazama podataka, dok istovremeno koristiš alate koji ti olakšavaju svakodnevne zadatke i smanjuju mogućnost grešaka pri unosu komandi.

---

### Kako da radiš vežbe

- **Terminal (`sqlite3`):** kada lekcija traži `.databases`, `.tables`, `.schema`, `.quit` ili `ATTACH`. Za lekciju **02** posebno je važno da to probaš u terminalu, jer učiš otvaranje i priključivanje baza.

- **SQLTools:** za pisanje, čuvanje i izvršavanje SQL upita iz odgovarajućih `.sql` fajlova u playground-u.

- **SQLite Viewer:** za vizuelni pregled tabela i podataka; ne izvršava SQL upite.

Na primer, prvo uradi CLI korake iz lekcije 02, zatim u SQLTools-u pregledaj iste tabele. Tako povezuješ teoriju i alate, bez potrebe da sve ponavljaš. Radi na **`chinook_practice.db`**, a original ostavi neizmenjen. Plan i dalje odgovara takvom načinu rada.

---

### Tab u SQLite terminalu

Ispravan pun naziv je **`.databases`**. Dobra vest: ne moraš čekati Tab — proverio sam da tvoj CLI prihvata skraćeni oblik. U SQLite prompt-u ukucaj:

```text
.databa
```

i pritisni **Enter**. To izvršava `.databases`; nije automatsko dopunjavanje.

Postoje i alati za udobniji terminal, na primer [litecli](https://github.com/dbcli/litecli), koji ima dopunjavanje SQL-a, i [rlwrap](https://manpages.ubuntu.com/manpages/resolute/man1/rlwrap.1.html), koji može dodati dopunjavanje uz odgovarajuću konfiguraciju. **Litecli je zaseban klijent**, ne ekstenzija za zvanični `sqlite3`, i ne podržava nužno sve iste dot-komande.

Za sada bih nastavio sa zvaničnim `sqlite3` zbog vežbi; dopunjavanje možemo naknadno podesiti i proveriti baš za `.databases`. Kada jednom budeš siguran da ti Tab dovršavanje radi kako treba, možeš ga koristiti za brže unošenje dot-komandi, ali u početku je dovoljno znati da skraćeni oblik funkcioniše i bez Tab-a.

---

### Opcija za Tab dovršavanje u SQLite CLI-ju

> **Napomena:** Ako želiš da koristiš Tab dovršavanje u zvaničnom SQLite CLI-ju, moraćeš da koristiš `rlwrap` sa odgovarajućom listom komandi, kao što je objašnjeno u uputstvu za rad sa terminalom. Bez `rlwrap`-a, standardni `sqlite3` CLI ne podržava automatsko dovršavanje komandi.

- **Napomena:** Takođe, dopunjavanje komandi u SQLite CLI-ju može da se isključi ili prilagodi pomoću `rlwrap`-a i odgovarajuće konfiguracije. Na taj način možeš imati automatsko dovršavanje komandi, ali i dalje koristiš zvanični `sqlite3` CLI.

- **Litecli:** možeš isključiti automatske predloge, ali `Tab` i dalje radi. Litecli je zaseban program, pa se uvek možeš vratiti na obični `sqlite3`.
- **rlwrap:** možeš pokrenuti `sqlite3` sa njim kada želiš pomoć, a bez njega kada ne želiš.

- Detaljno objašnjenje: [read more](../../../docs/fastapi/cheatsheets/fastapi_extensions_vscode/sqlite_terminal_litecli_rlwrap.md)

---

## Pitanje 4

Šta znače `ON DELETE NO ACTION` i `ON UPDATE NO ACTION` u šemi tabele `albums`? Kako se ponašaju na primeru veze između izvođača i albuma iz Chinook ERD dijagrama i kako mogu bezbedno da ih isprobam?

---

## Odgovor 4

**Ukratko:** ove opcije određuju šta SQLite automatski radi sa povezanim redovima kada se obriše roditeljski red ili promeni vrednost roditeljskog ključa. `NO ACTION` znači da SQLite **ne preduzima posebnu automatsku akciju nad povezanim redovima**. To ne znači da će dozvoliti narušavanje stranog ključa: ako je provera stranih ključeva uključena, neispravna promena će biti odbijena prilikom provere ograničenja.

U tvojoj bazi, uz uključenu proveru i uobičajenu neposrednu proveru ograničenja:

- `ON DELETE NO ACTION`: ne možeš obrisati izvođača dok albumi i dalje upućuju na njegov `ArtistId`.
- `ON UPDATE NO ACTION`: ne možeš promeniti njegov `ArtistId` ako bi albumi ostali da upućuju na staru, više nepostojeću vrednost.
- SQLite **ne briše automatski albume** i **ne menja automatski njihove vrednosti `ArtistId`**.

### 1. Veza na tvom ERD dijagramu

Na [Chinook ERD dijagramu](../chinook/ERD.drawio) veza je označena kao `artists 1 : 0..N albums`. To znači:

1. Jedan izvođač može imati nijedan, jedan ili više albuma.
2. Svaki album mora imati jednog izvođača, jer je `albums.ArtistId` u šemi `NOT NULL` i predstavlja strani ključ ka `artists.ArtistId`.

Pravilo važi kada je provera stranih ključeva uključena i podaci su ispravni. Dijagram pokazuje **ko je sa kim povezan**, ali ne prikazuje konkretne akcije `ON DELETE` i `ON UPDATE`. Njih proveravaš u SQL šemi.

```text
artists — roditeljska tabela             albums — tabela dete

ArtistId (PK)     Name                   AlbumId (PK)   Title                  ArtistId (FK)
-------------     -----                  ------------   -----                  -------------
1                 AC/DC       <--------- 1              For Those About ...    1
                              <--------- 4              Let There Be Rock      1
```

`artists.ArtistId` je **primarni ključ (PK)** izvođača. `albums.ArtistId` je **strani ključ (FK)** koji čuva vrednost roditeljskog ključa. Oznake `PK` i `FK` predstavljaju različite uloge, iako obe kolone u ovom slučaju nose ime `ArtistId`.

Vrednosti `1`, `4` i nazivi albuma odgovaraju podacima koji su pronađeni u tvojoj radnoj kopiji pri pisanju odgovora. Ako kasnije promeniš podatke, rezultati mogu biti drugačiji.

---

### 2. Gde se vide ove opcije?

U SQLite CLI-ju, kada je radna Chinook baza već otvorena, pokreni:

```text
.schema albums
```

Relevantni deo stvarne definicije tabele je:

```sql
[ArtistId] INTEGER NOT NULL,
FOREIGN KEY ([ArtistId]) REFERENCES "artists" ([ArtistId])
    ON DELETE NO ACTION ON UPDATE NO ACTION
```

Čitaj ga ovako:

- Svaki album mora imati vrednost `ArtistId` — to je zasebno ograničenje `NOT NULL`.
- Ta vrednost mora odgovarati postojećem `ArtistId` u `artists`, kada je provera FK uključena.
- `ON DELETE` odnosi se na brisanje **roditeljskog reda** iz `artists`.
- `ON UPDATE` odnosi se na promenu **referencirane vrednosti roditeljskog ključa**, ovde `artists.ArtistId`.

Informaciju možeš pogledati i SQL upitom, pa i iz SQLTools-a:

```sql
PRAGMA foreign_key_list('albums');
```

U rezultatu potraži vezu `albums.ArtistId` → `artists.ArtistId` i kolone `on_delete` i `on_update`. `PRAGMA foreign_key_list` pokazuje definiciju, ali sam po sebi **ne govori da li je njena provera trenutno uključena**.

---

### 3. Preduslov: `PRAGMA foreign_keys`

Proveri u **istoj konekciji** u kojoj ćeš izvršavati naredbe:

```sql
PRAGMA foreign_keys;
```

- `1` znači da je provera uključena.
- `0` znači da je isključena. Tada `NO ACTION` ne sprečava promene koje ostavljaju nepovezane albume.

Uključi je i ponovo proveri:

```sql
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;
```

Očekivani rezultat druge naredbe je `1`. Ovo je podešavanje **po konekciji**: terminal, `litecli`, SQLTools i aplikacija mogu imati različita podešavanja. Kod SQLTools-a proveri da obe naredbe stvarno idu preko iste aktivne konekcije; za proveru ispod preporučujem jednu SQLite CLI sesiju.

`PRAGMA foreign_keys = ON` postavi **pre početka transakcije**: pokušaj promene tog podešavanja usred transakcije nema efekta. Ako provera ne vrati `1`, nemoj se oslanjati na ograničenje dok ne utvrdiš zašto.

Uključivanje provere ne popravlja automatski ranije nastale greške. Postojeće povrede možeš pregledati pomoću `PRAGMA foreign_key_check;`; prazan rezultat znači da tom proverom nisu pronađene povrede.

---

### 4. `ON DELETE NO ACTION` — brisanje izvođača

Zamisli da u tabeli `artists` postoji AC/DC sa `ArtistId = 1`, a dva albuma u `albums` imaju `ArtistId = 1`.

Ako pokušaš da obrišeš tog izvođača:

```sql
DELETE FROM artists WHERE ArtistId = 1;
```

**Uz uključenu proveru stranih ključeva**, ovaj pokušaj u našem primeru ne uspeva: albumi bi ostali sa `ArtistId = 1`, a izvođač sa tim ključem više ne bi postojao. SQLite prijavljuje `FOREIGN KEY constraint failed`. Za ovu neposrednu proveru neuspešna naredba ne briše izvođača; ne briše ni albume.

Ako izvođač **nema** povezane albume, ovo konkretno FK ograničenje ne sprečava brisanje. Mogu, međutim, postojati druga ograničenja ili povezane tabele koje treba uzeti u obzir.

Pre brisanja je potrebno da odnosi ostanu ispravni, na primer da se albumi **namerno** dodele drugom postojećem izvođaču ili da se obrišu, ako je to zaista željena operacija. U stvarnoj Chinook bazi albumi mogu imati povezane pesme i druge zavisnosti: zato ovo ne radi naslepo na radnoj ili originalnoj bazi. Brisanje albuma je ozbiljna izmena podataka, ne samo uklanjanje veze.

---

### 5. `ON UPDATE NO ACTION` — promena ključa izvođača

Početno stanje je isto: AC/DC ima `artists.ArtistId = 1`, a albumi imaju `albums.ArtistId = 1`. Zamisli pokušaj:

```sql
UPDATE artists
SET ArtistId = 9999
WHERE ArtistId = 1;
```

Ako je `9999` slobodan i provera FK uključena, promena ipak ne uspeva: albumi bi ostali da upućuju na `1`, a roditelj bi sada imao ključ `9999`. SQLite prijavljuje `FOREIGN KEY constraint failed`; `NO ACTION` ne prepisuje `albums.ArtistId` na `9999`.

Ovo **nije** zabrana svakog `UPDATE`-a. Na primer, promena `artists.Name` ne menja referencirani `ArtistId`, pa zbog ovog konkretnog stranog ključa sama po sebi ne izaziva ovaj problem. Takođe, ako nijedan album ne upućuje na izvođača, ovo FK ograničenje samo po sebi ne sprečava promenu njegovog ključa. Druga ograničenja mogu i dalje da važe. Primarne ključeve u praksi uglavnom ne treba menjati bez posebnog razloga.

Promena `albums.ArtistId` je druga operacija: njome menjaš **strani ključ deteta**, ne roditeljski ključ. Uz uključenu proveru, nova vrednost mora biti ID postojećeg izvođača; zbog `NOT NULL` ne može biti `NULL`.

---

### 6. Bezbedna vežba — zasebna baza u memoriji

**Nemoj pokretati `DELETE` i `UPDATE` iz ovog primera nad `chinook_practice.db` ili originalnom bazom.** Napravićemo pojednostavljen model istih dveju tabela u memoriji. Ovde su samo primeri potrebnih kolona i nema drugih Chinook tabela, indeksa ni zavisnosti.

U terminalu pokreni SQLite CLI:

```bash
sqlite3 :memory:
```

Sve naredbe ispod unosi u **istu otvorenu SQLite sesiju**, redom. Prvo uključi proveru i potvrdi da je rezultat `1`:

```sql
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;
```

Zatim napravi dve tabele i unesi primere:

```sql
CREATE TABLE artists (
    ArtistId INTEGER PRIMARY KEY,
    Name TEXT
);

CREATE TABLE albums (
    AlbumId INTEGER PRIMARY KEY,
    Title TEXT NOT NULL,
    ArtistId INTEGER NOT NULL,
    FOREIGN KEY (ArtistId) REFERENCES artists(ArtistId)
        ON DELETE NO ACTION ON UPDATE NO ACTION
);

INSERT INTO artists (ArtistId, Name)
VALUES (1, 'AC/DC'), (2, 'Accept');

INSERT INTO albums (AlbumId, Title, ArtistId)
VALUES
    (1, 'For Those About To Rock We Salute You', 1),
    (4, 'Let There Be Rock', 1);
```

Pogledaj početno stanje:

```sql
SELECT ArtistId, Name FROM artists;
SELECT AlbumId, Title, ArtistId FROM albums;
```

Sada **pojedinačno** izvrši sledeće dve naredbe. Za svaku je očekivana greška `FOREIGN KEY constraint failed`:

```sql
DELETE FROM artists WHERE ArtistId = 1;
```

```sql
UPDATE artists SET ArtistId = 9999 WHERE ArtistId = 1;
```

Proveri da su redovi i dalje tu:

```sql
SELECT ArtistId, Name FROM artists;
SELECT AlbumId, Title, ArtistId FROM albums;
```

Zatim u ovom **izmišljenom primeru** namerno prebaci albume na drugog, postojećeg izvođača, pa obriši prvog:

```sql
UPDATE albums SET ArtistId = 2 WHERE ArtistId = 1;
DELETE FROM artists WHERE ArtistId = 1;
SELECT ArtistId, Name FROM artists;
SELECT AlbumId, Title, ArtistId FROM albums;
```

Obe izmene uspevaju jer `ArtistId = 2` postoji, a posle prebacivanja nijedan album ne upućuje na izvođača `1`. U stvarnim muzičkim podacima ne bi dodeljivao albume pogrešnom izvođaču samo da bi omogućio brisanje — ovo je isključivo tehnički eksperiment.

Za kraj unesi `.quit`. Cela privremena baza nestaje kada zatvoriš tu konekciju; ni `chinook_practice.db` ni original nisu izmenjeni. Za ponavljanje vežbe ponovo pokreni `sqlite3 :memory:` i ponovi kreiranje tabela.

---

### 7. Zašto se zove `NO ACTION` ako se operacija odbija?

Zato što `NO ACTION` opisuje **odsustvo posebne automatske akcije nad detetom**, ne odsustvo provere. SQLite neće sam promeniti ili obrisati album, ali FK ograničenje i dalje mora biti ispunjeno kada dođe trenutak njegove provere.

Za poređenje:

| Akcija      | Šta bi se desilo sa povezanim albumima                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------------------------- |
| `NO ACTION` | Ne menja ih automatski; ako ograničenje ostane prekršeno u trenutku provere, dolazi do greške.                            |
| `CASCADE`   | Kod brisanja roditelja briše povezane albume; kod promene roditeljskog ključa prenosi novu vrednost na njihove FK kolone. |
| `SET NULL`  | Postavlja FK deteta na `NULL`. Za `albums.ArtistId` to ne bi uspelo zbog njegovog `NOT NULL` ograničenja.                 |
| `RESTRICT`  | Odbija promenu roditelja čim se pokuša, ako postoje zavisni redovi; taj trenutak može biti raniji nego kod `NO ACTION`.   |

Ovo je poređenje značenja akcija, **ne predlog da menjaš šemu Chinook baze**. SQLite podržava i `SET DEFAULT`, ali tada podrazumevana vrednost takođe mora zadovoljiti ostala ograničenja.

---

### 8. Neposredna i odložena provera

U gornjem modelu i u prikazanoj šemi `albums` ograničenje je neposredno: greška se prijavljuje na kraju naredbe koja bi ga prekršila. Kod posebno definisanog **odloženog** (`DEFERRABLE INITIALLY DEFERRED`) FK ograničenja SQLite može dozvoliti privremeno neispravno stanje unutar transakcije, ali ono mora biti ispravljeno pre uspešnog `COMMIT`-a. Ako nije, `COMMIT` ne uspeva. To ne znači da `NO ACTION` trajno dozvoljava neispravnu vezu.

Zato `NO ACTION` i `RESTRICT` nisu uvek isto: `RESTRICT` se primenjuje odmah pri promeni roditeljskog ključa ili brisanju roditelja, čak i kada je ograničenje odloženo. Više detalja: [SQLite dokumentacija o stranim ključevima](https://www.sqlite.org/foreignkeys.html).

---

### Za pamćenje

1. `artists` je roditelj, a `albums` dete; `albums.ArtistId` upućuje na `artists.ArtistId`.
2. `NO ACTION` ne popravlja vezu automatski; uključena provera FK ipak odbija neispravno stanje.
3. `DELETE` se odnosi na roditeljski red, a `UPDATE` na referencirani roditeljski ključ — ne na svaku promenu reda.
4. Proveravaj `PRAGMA foreign_keys` u svakoj konekciji i vežbaj izmene na izolovanoj bazi.

---

## Pitanje 5

Rekao si da kolone koje imaju PK (`id: int`) automatski imaju indeks i autoincrement, a da na ostale kolone treba da stavim `index=True`. U tabeli `artists` vidim `AUTOINCREMENT` na primarnom ključu. Da li je to automatski dodato zbog PK ili je izričito definisano u bazi?

---

## Odgovor 5

U tvojoj Chinook bazi `AUTOINCREMENT` je **izričito naveden u definiciji tabele**. Nije automatski dodat samom oznakom `PRIMARY KEY`. Šemu možeš pogledati u SQLite CLI-ju komandom:

```text
.schema artists
```

Relevantna definicija je:

```sql
[ArtistId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL
```

**Ispravka mog ranijeg objašnjenja:** pomešao sam automatsko dodeljivanje ID-ja sa posebnom SQLite ključnom rečju `AUTOINCREMENT`. Takođe, savet da staviš `index=True` na sve ostale kolone bio je preširok. To nisu pravila koja treba primenjivati na sve tabele i baze.

---

### 1. `PRIMARY KEY` i automatsko dodeljivanje broja

Primarni ključ (`PRIMARY KEY`, odnosno PK) služi za jedinstveno identifikovanje reda. U običnoj SQLite tabeli, kolona definisana baš kao `INTEGER PRIMARY KEY` ima posebno ponašanje: ona je alias za interni celobrojni identifikator reda, `rowid`.

Ako pri `INSERT`-u ne navedeš vrednost takvog ključa, SQLite je automatski dodeljuje, **čak i bez** ključne reči `AUTOINCREMENT`:

```sql
CREATE TABLE primer (
    id INTEGER PRIMARY KEY,
    naziv TEXT
);

INSERT INTO primer (naziv) VALUES ('Prvi');
SELECT id, naziv FROM primer;
```

U novoj, praznoj tabeli rezultat je obično `1 | Prvi`. Tipično se bira broj za jedan veći od najvećeg trenutno korišćenog ID-ja, ali postoje izuzeci. Ovo je SQLite ponašanje za konkretan oblik `INTEGER PRIMARY KEY`, a ne opšta osobina bilo koje PK kolone u bilo kojoj bazi.

---

### 2. Šta onda dodaje `AUTOINCREMENT`?

`AUTOINCREMENT` menja način **automatskog izbora** ID-ja:

- Bez njega SQLite može ponovo automatski dodeliti ID prethodno obrisanog reda, posebno ako je obrisan najveći ID.

- Sa njim automatski bira ID veći od najvećeg relevantnog ranije upisanog ID-ja u toj tabeli, pa ne koristi ponovo automatski ID-jeve iz prethodno potvrđenih (`COMMIT`) upisa.

- To ne znači da je niz bez prekida. Praznine su moguće, a vrednosti iz poništenih transakcija mogu se ponovo koristiti.

- Ovo pravilo odnosi se na **automatski izbor** ID-ja: ako ručno navedeš slobodan prethodni ID, `AUTOINCREMENT` sam po sebi ne zabranjuje njegovu upotrebu.

Na primer, ako su automatski dodeljeni ID-jevi `1`, `2`, `3`, pa obrišeš red `3`:

| Definicija                          | Šta se tipično desi pri sledećem automatskom unosu                              |
| ----------------------------------- | ------------------------------------------------------------------------------- |
| `INTEGER PRIMARY KEY`               | Može se ponovo dodeliti `3`, jer je sada `2` najveći postojeći ID.              |
| `INTEGER PRIMARY KEY AUTOINCREMENT` | Dodeljuje se `4`; prethodno potvrđeni ID `3` se ne dodeljuje ponovo automatski. |

Ovo je primer pod pretpostavkom da su prethodni upisi potvrđeni i da interno praćenje nije ručno menjano. `AUTOINCREMENT` zahteva dodatni rad i obično nije potreban ako aplikaciji nije važno da automatski dodeljeni ID-jevi nikada ne ponavljaju ranije potvrđene vrednosti.

---

### 3. Da li PK automatski ima indeks?

Primarni ključ ima mehanizam koji obezbeđuje jedinstvenost i omogućava efikasan pristup. Ali to ne mora biti **zaseban indeks** vidljiv u listi indeksa.

U tvojoj SQLite tabeli `artists`, `ArtistId INTEGER PRIMARY KEY` je alias za `rowid`: sama tabela koristi taj ključ za pristup redovima. Zato odsustvo posebnog indeksa za `ArtistId` u `PRAGMA index_list('artists');` ne znači da pretraga po tom ključu nema efikasan pristup. Za druge vrste primarnih ključeva SQLite može koristiti zaseban indeks; detalji zavise i od vrste tabele.

---

### 4. Da li `index=True` ide na svaku drugu kolonu?

Ne. U SQLAlchemy modelu `index=True` traži indeks za kolonu; korisno ga je razmotriti tamo gde upiti često filtriraju, spajaju ili sortiraju podatke. Indeks ubrzava određena čitanja, ali zauzima prostor i povećava posao pri `INSERT`, `UPDATE` i `DELETE` operacijama. Nekada je korisniji zajednički indeks za više kolona nego pojedinačni indeksi.

U tvojoj Chinook bazi postoji konkretan primer:

```sql
CREATE INDEX [IFK_AlbumArtistId] ON "albums" ([ArtistId]);
```

To je **posebno definisan indeks** na stranom (`FOREIGN KEY`) ključu `albums.ArtistId`. Može pomoći pri pronalaženju albuma određenog izvođača i proverama povezanih redova. Sam po sebi strani ključ (`albums.ArtistId`) ne znači da SQLite automatski pravi takav indeks.

Indeks nije isto što i `PRIMARY KEY`, `UNIQUE` ili `AUTOINCREMENT`: običan indeks sam po sebi ne zahteva jedinstvene vrednosti niti dodeljuje ID-jeve. Podrška za automatske ključeve i način na koji ih SQLAlchemy generiše razlikuju se između baza, pa proveravaj konkretnu šemu i upotrebljeni dijalekt.

**Za pamćenje:** u `artists` je `AUTOINCREMENT` definisan u šemi. Automatsko dodeljivanje broja već postoji i bez te ključne reči za SQLite `INTEGER PRIMARY KEY`. Dodatne indekse biraš prema stvarnim upitima.

---
