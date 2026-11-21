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

**Ukratko:** ove opcije određuju šta SQLite automatski radi sa povezanim redovima kada se obriše roditeljski red ili promeni vrednost roditeljskog ključa. **Roditeljski ključ predstavlja vrednost koja se koristi u povezanim redovima. Na primer, `artists.ArtistId` je roditeljski ključ (PK u tabeli `artists`) za `albums.ArtistId`. Jednostavno rečeno, roditelj je "vlasnik" vrednosti na koju se drugi redovi pozivaju. FK ograničenje (foreign key constraint) definiše pravila za te veze i osigurava integritet podataka između povezanih tabela.** Bez FK ograničenja, SQLite ne bi mogao da proverava ove veze i mogao bi da dozvoli narušavanje integriteta podataka.

`NO ACTION` znači da SQLite **ne preduzima posebnu automatsku akciju nad povezanim redovima**. To ne znači da će dozvoliti narušavanje stranog ključa. Ako je provera stranih ključeva uključena, neispravna promena će biti odbijena prilikom provere ograničenja.

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

## Pitanje 6

Da li je roditeljski ključ u vezi između `artists` i `albums` PK (primarni ključ) u tabeli `artists`?

---

## Odgovor 6

Da. U ovoj vezi, roditeljski ključ u tabeli `artists` je primarni ključ (PK) kolone `ArtistId`.

```text
albums.ArtistId  ─────►  artists.ArtistId
   strani ključ (FK)       roditeljski ključ (PK)
```

- `artists.ArtistId` je **roditeljski ključ**: kolona u roditeljskoj tabeli `artists`, čije se vrednosti referenciraju. U tvojoj bazi je to primarni ključ (PK).

- `albums.ArtistId` je **strani ključ**: kolona u tabeli dete `albums`, koja upućuje na `artists.ArtistId`. To znači da vrednosti u `albums.ArtistId` moraju odgovarati vrednostima u `artists.ArtistId` ili biti `NULL` (ako je dozvoljeno).

Na primer, ako je izvođač upisan kao `artists.ArtistId = 1`, onda vrednost `albums.ArtistId = 1` označava da album pripada tom izvođaču. Broj `1` je **vrednost ključa**. Drugim rečima, to je konkretna vrednost koja povezuje redove. Roditeljski ključ i strani ključ su nazivi uloga koje imaju kolone u vezi.

Roditeljski ključ je često primarni ključ, kao u ovom primeru, ali može biti i druga kolona ili skup kolona na koje se može ispravno referencirati, na primer kolona sa `UNIQUE` ograničenjem. Zato nemoj izjednačavati pojam „roditeljski ključ“ sa „FK“: FK je na strani tabele dete. Roditeljski ključ je cilj na koji FK pokazuje.

---

## Pitanje 7

Kada kažemo da strani ključ „referencira“ roditeljski ključ, šta se tačno dešava? Znam šta znači referencirati ili pokazivati na isti objekat u Python-u, ali nisam siguran kako to funkcioniše u bazi. Ako je veza između `artists` i `albums` 1:N, da li to znači da jedan izvođač može imati više albuma, ali svaki album može pripadati samo jednom izvođaču?

## Odgovor 7

Da — tako je. Veza `artists`–`albums` je **jedan-prema-više (1:N)**:

- jedan izvođač može imati nijedan, jedan ili više albuma;
- svaki album je povezan sa jednim izvođačem.

U ovoj Chinook šemi `albums.ArtistId` je `NOT NULL`, pa album mora imati povezanog izvođača.

Ovde „referencira“ **ne znači da `albums.ArtistId` čuva Python pokazivač na ceo objekat ili red u tabeli `artists` tj. na izvođača sa svim podacima iz kolona**. Nasuprot tome, baza čuva samo ID vrednost. Zatim proverava da li se ta vrednost poklapa sa ID-jem nekog reda u `artists`.

Na primer, tabele mogu sadržati:

**`artists`**

| ArtistId | Name  |
| -------: | ----- |
|        1 | AC/DC |

**`albums`**

| AlbumId | Title                    | ArtistId |
| ------: | ------------------------ | -------: |
|       1 | For Those About To Rock… |        1 |
|       4 | Let There Be Rock        |        1 |

Oba reda albuma čuvaju `ArtistId = 1`. Taj broj znači: „poveži ovaj album sa izvođačem čiji je `ArtistId` jednak 1“. Baza pronalazi red poređenjem vrednosti; nema Python objekta ni memorijske adrese u SQLite fajlu.

Strano-ključno ograničenje definiše pravilo veze: ako je provera stranih ključeva uključena, vrednost `albums.ArtistId` mora odgovarati postojećem `artists.ArtistId`. Na primer, `albums.ArtistId = 999` nije dozvoljen ako ne postoji izvođač sa `ArtistId = 999`. Istovremeno, isti postojeći ID može se pojaviti u više redova `albums` — zato jedan izvođač može imati više albuma.

Kada upit spaja ove tabele, uslov poređenja vrednosti izgleda ovako:

```sql
SELECT artists.Name, albums.Title
FROM artists
JOIN albums ON albums.ArtistId = artists.ArtistId;
```

Ukratko, FK „pokazuje“ na roditeljski red **posredno, preko jednake vrednosti ključa**. To nije Python referenca ili pokazivač; veza je sačuvana u podacima i proverava se pravilom stranog ključa.

---

## Pitanje 8

Kako tačno funkcionišu `JOIN` i `LEFT JOIN`? Kako se razlikuju i šta se dešava kada red sa leve strane nema odgovarajući red sa desne strane?

---

## Odgovor 8

`JOIN` povezuje redove iz dve tabele prema uslovu koji zadaš u `ON`. Najlakše je razumeti razliku preko Chinook veze `artists`–`albums`:

- `artists` je leva tabela u primerima ispod.
- `albums` je desna tabela.
- `albums.ArtistId = artists.ArtistId` je uslov koji kaže koji redovi odgovaraju jedni drugima.

Važno: `JOIN` sam po sebi ne menja podatke. On pravi rezultat upita sastavljen od kolona iz povezanih redova.

### 1. `JOIN` odnosno `INNER JOIN`

Kada napišeš samo `JOIN`, SQLite podrazumeva `INNER JOIN`. Rezultat sadrži **samo parove redova za koje je uslov u `ON` tačan**.

```sql
SELECT artists.ArtistId, artists.Name, albums.AlbumId, albums.Title
FROM artists
JOIN albums
  ON albums.ArtistId = artists.ArtistId
WHERE artists.Name = 'AC/DC';
```

U tvojoj bazi ovaj upit vrati dva reda:

| ArtistId | Name  | AlbumId | Title                                 |
| -------: | ----- | ------: | ------------------------------------- |
|        1 | AC/DC |       1 | For Those About To Rock We Salute You |
|        1 | AC/DC |       4 | Let There Be Rock                     |

SQLite uporedi `albums.ArtistId` sa `artists.ArtistId`. Pošto oba albuma imaju `ArtistId = 1`, oba se uparuju sa redom `AC/DC`. Zbog toga se izvođač ponavlja u rezultatu — dobija se po jedan red za svaki pronađeni par.

Izvođač bez albuma nema nijedan par, pa se njegov red **ne pojavljuje** u običnom `JOIN` rezultatu.

---

### 2. `LEFT JOIN`

`LEFT JOIN` zadržava **sve redove iz leve tabele** (`artists`), bez obzira na to da li imaju odgovarajući album. Kada postoji podudaranje, rezultat izgleda kao kod običnog `JOIN`-a. Kada podudaranja nema, SQLite i dalje vrati red izvođača, a kolone koje dolaze iz `albums` popuni sa `NULL`.

```sql
SELECT artists.ArtistId, artists.Name, albums.AlbumId, albums.Title
FROM artists
LEFT JOIN albums
  ON albums.ArtistId = artists.ArtistId
WHERE artists.Name = 'AC/DC';
```

Za AC/DC rezultat je isti kao kod običnog `JOIN`-a, jer AC/DC ima albume. Da vidiš i izvođače bez albuma, ukloni uslov koji bira AC/DC:

```sql
SELECT artists.ArtistId, artists.Name, albums.AlbumId, albums.Title
FROM artists
LEFT JOIN albums
  ON albums.ArtistId = artists.ArtistId
ORDER BY artists.ArtistId
LIMIT 10;
```

Ovaj rezultat sadrži redove izvođača sa njihovim albumima. Za izvođača bez albuma bi, na primer, izgledao ovako:

| ArtistId | Name                       | AlbumId | Title  |
| -------: | -------------------------- | ------: | ------ |
|       25 | Milton Nascimento & Bebeto |  `NULL` | `NULL` |

To ne znači da je u tabeli `albums` upisan red čiji je `AlbumId` ili `Title` `NULL`. To je privremeni rezultat `LEFT JOIN`-a koji pokazuje da za tog izvođača nije nađen odgovarajući red sa desne strane.

---

### 3. Kako jedan-prema-više utiče na rezultat?

Kod veze 1:N jedan izvođač može da se upari sa više albuma. `JOIN` zato vraća po jedan red za svaki par izvođač–album:

```text
artists              albums
AC/DC (ArtistId=1) ── Album 1 (ArtistId=1)
                  └─ Album 4 (ArtistId=1)
```

Isto važi za `LEFT JOIN`. Ako postoje tri albuma, jedan izvođač će se pojaviti u tri rezultujuća reda. Ako nema albuma, `LEFT JOIN` će ga prikazati jednom, uz `NULL` vrednosti za kolone iz `albums`.

---

### 4. Pronađi izvođače bez albuma

Često se `LEFT JOIN` koristi da se pronađu redovi leve tabele bez podudaranja. Proveri nullable kolonu sa desne tabele koja bi u stvarnom albumu morala imati vrednost, kao što je njegov primarni ključ `albums.AlbumId`:

```sql
SELECT artists.ArtistId, artists.Name
FROM artists
LEFT JOIN albums
  ON albums.ArtistId = artists.ArtistId
WHERE albums.AlbumId IS NULL
ORDER BY artists.ArtistId;
```

U Chinook radnoj kopiji ovo pronađe izvođače koji nemaju albume. U proveravanim podacima ima 275 izvođača i 347 albuma; 71 izvođač nema album. Zbog toga običan `JOIN` daje 347 redova, a `LEFT JOIN` bez dodatnog filtriranja daje 418 redova: 347 uparenih redova i po jedan red za svakog od 71 nepovezanog izvođača. To su vrednosti trenutne kopije baze; mogu se promeniti ako promeniš podatke.

Nemoj koristiti `WHERE albums.ArtistId IS NULL` kao opšte pravilo kada postoji pouzdan PK, jer je bolje eksplicitno proveriti da nije pronađen desni red, na primer `albums.AlbumId IS NULL`.

---

### 5. Važna razlika: uslov u `ON` i uslov u `WHERE`

Kod `LEFT JOIN`-a, filter koji određuje **koji redovi smeju da se uparuju** stavi u `ON`, ako i dalje želiš da sačuvaš sve redove sa leve strane. Na primer, prikaži sve izvođače, a pridruži samo albume čiji naziv sadrži „Rock“:

```sql
SELECT artists.Name, albums.Title
FROM artists
LEFT JOIN albums
  ON albums.ArtistId = artists.ArtistId
 AND albums.Title LIKE '%Rock%';
```

Izvođači bez odgovarajućeg „Rock“ albuma ostaju u rezultatu, a kolone albuma su `NULL`.

Ako isti filter staviš u `WHERE`:

```sql
SELECT artists.Name, albums.Title
FROM artists
LEFT JOIN albums
  ON albums.ArtistId = artists.ArtistId
WHERE albums.Title LIKE '%Rock%';
```

redovi sa `albums.Title IS NULL` ne zadovoljavaju uslov `LIKE` i bivaju uklonjeni. Tako se gubi glavna osobina `LEFT JOIN`-a za taj slučaj, a rezultat se ponaša kao da su traženi samo izvođači sa albumom koji zadovoljava filter.

**Pravilo za pamćenje:** `ON` određuje uparivanje; `WHERE` filtrira rezultat nakon spajanja. Kod `INNER JOIN`-a se mnogi uslovi mogu premeštati između `ON` i `WHERE` bez promene rezultata, ali kod `LEFT JOIN`-a premeštanje može promeniti značenje.

---

### 6. `COUNT(*)` i `COUNT(albums.AlbumId)` uz `LEFT JOIN`

Kod izvođača bez albuma, `LEFT JOIN` ipak stvara jedan rezultatni red sa `NULL` vrednostima sa desne strane. Zbog toga:

- `COUNT(*)` broji i taj rezultatni red, pa bi za izvođača bez albuma dao `1`;
- `COUNT(albums.AlbumId)` ignoriše `NULL`, pa bi dao `0`.

Za brojanje albuma po izvođaču koristi:

```sql
SELECT
    artists.ArtistId,
    artists.Name,
    COUNT(albums.AlbumId) AS album_count
FROM artists
LEFT JOIN albums
  ON albums.ArtistId = artists.ArtistId
GROUP BY artists.ArtistId, artists.Name
ORDER BY artists.ArtistId
LIMIT 10;
```

Ovde `COUNT(albums.AlbumId)` koristi se namerno da bi izvođač bez albuma dobio broj `0`.

---

### Ukratko

| Operacija             | Šta ostaje u rezultatu?                                               |
| --------------------- | --------------------------------------------------------------------- |
| `JOIN` / `INNER JOIN` | Samo redovi koji su upareni sa odgovarajućim redovima u obe tabele.   |
| `LEFT JOIN`           | Svi redovi leve tabele; desne tabele su `NULL` kada nema podudaranja. |

U Chinook primeru izvođač je leva strana, album desna. Koristi `JOIN` kada su ti potrebni samo izvođači koji imaju albume, a `LEFT JOIN` kada želiš da sačuvaš sve izvođače, uključujući one bez albuma.

---

## Pitanje 9

Da li je rečenica „Baza čuva samo ID vrednost. Zatim proverava da li se ta vrednost poklapa sa ID-jem nekog reda u `artists`“ ispravna?

---

## Odgovor 9

Da, **kao pojednostavljeno objašnjenje je ispravna**, ali joj nedostaje važan uslov: SQLite sprovodi proveru stranog ključa samo kada je provera uključena u toj konekciji. Uključivanje provere stranih ključeva obično se vrši naredbom:

```sql
PRAGMA foreign_keys = ON;
```

U vezi između Chinook tabela:

- `albums.ArtistId` čuva ID vrednost, na primer `1`. Ne čuva Python objekat, memorijsku adresu ili kopiju celog reda iz `artists`.

- Kada se red albuma upisuje ili se menja njegov `ArtistId`, uz uključenu proveru preko `PRAGMA foreign_keys = ON;`, SQLite proverava da li postoji odgovarajući `artists.ArtistId`. Ako ne postoji, operacija će biti odbijena i biće prijavljena greška.

- Provera važi i pri brisanju izvođača ili izmeni njegovog roditeljskog ključa, prema pravilima `ON DELETE` i `ON UPDATE` definisanim u šemi.

Dakle, preciznija formulacija bi bila:

> Tabela `albums` čuva ID izvođača u koloni `ArtistId`. Kada se upisuje ili menja album, SQLite proverava da li ta vrednost odgovara postojećem `artists.ArtistId` — pod uslovom da je provera stranih ključeva uključena u toj konekciji.

Proveru u trenutnoj SQLite konekciji možeš videti ovako:

```sql
PRAGMA foreign_keys;
```

Rezultat `1` znači da je uključena, a `0` da nije. Ovo podešavanje važi po konekciji i obično mora biti uključeno pre početka transakcije. Ako je provera bila isključena, postojeći neispravni podaci neće se automatski popraviti; možeš ih potražiti pomoću `PRAGMA foreign_key_check;`.

---

## Pitanje 10

Za šta je `PRAGMA` tačno skraćenica? Šta znači svako slovo u reči `PRAGMA`?

## Odgovor 10

`PRAGMA` **nije skraćenica** i slova `P`, `R`, `A`, `G`, `M`, `A` ne predstavljaju pojedinačne reči. Zato za njih ne postoji prošireni naziv koji treba naučiti.

`pragma` je obična reč, a ne akronim. Potiče od starogrčkog `πρᾶγμα` (_prâgma_), u značenju „stvar“, „posao“ ili „učinjeno delo“ ([etimologija reči](https://en.wiktionary.org/wiki/pragma)). To poreklo ne treba tumačiti kao naziv šest SQL pojmova.

U SQLite-u, `PRAGMA` označava SQLite-specifične naredbe kojima možeš da **pročitaš ili promeniš određena podešavanja i informacije o radu SQLite biblioteke**. Na primer:

```sql
PRAGMA foreign_keys;
```

čita da li je provera stranih ključeva uključena u trenutnoj konekciji, dok:

```sql
PRAGMA table_info('artists');
```

prikazuje informacije o kolonama tabele `artists`.

Dakle, zapamti `PRAGMA` kao naziv vrste posebnih SQLite naredbi — ne kao akronim. Sintaksa i podrška za pragma naredbe mogu se razlikovati među bazama; dokumentacija za SQLite nalazi se u [spisku PRAGMA naredbi](https://www.sqlite.org/pragma.html).

---

## Pitanje 11

Pokrenuo sam blok „Vežba 2: Definicije tabela“ u `01_what_is_sqlite.sql` i u rezultatu video tekst `CREATE TABLE`. Zašto sam dobio `CREATE TABLE`?

---

## Odgovor 11

Zato što upit traži prikaz **definicija tabela**, a ne njihovih redova sa podacima:

```sql
SELECT name, sql
FROM sqlite_schema
WHERE type = 'table'
  AND name IN ('albums', 'tracks', 'playlist_track')
ORDER BY name;
```

`sqlite_schema` je SQLite-ov interni katalog šeme — sistemski prikaz informacija o objektima u bazi, poput tabela, indeksa, pogleda i okidača. U njemu:

- `name` je naziv objekta, na primer `albums`;
- `type = 'table'` ograničava rezultat na tabele;
- `sql` sadrži SQL definiciju kojom je tabela napravljena.

Zato rezultat prikazuje imena `albums`, `playlist_track` i `tracks`, a u koloni `sql` tekst koji počinje sa `CREATE TABLE ...`. Taj tekst opisuje strukturu tabele: kolone i tipove, primarne i strane ključeve i druga ograničenja.

**Važno:** upit samo čita taj tekst iz kataloga i prikazuje ga kao rezultat. Ne izvršava tekst iz kolone `sql`, ne pravi ponovo tabele i ne menja bazu.

Razlikuj ova dva pitanja:

```sql
-- Koje su definicije tabela?
SELECT name, sql
FROM sqlite_schema
WHERE type = 'table'
  AND name IN ('albums', 'tracks', 'playlist_track')
ORDER BY name;
```

```sql
-- Koji redovi sa podacima postoje u tabeli albums?
SELECT *
FROM albums
LIMIT 5;
```

Prvi upit prikazuje **šemu** (kako je tabela definisana), a drugi **podatke** (redove sačuvane u tabeli). U prikazu SQLTools-a duga definicija može biti skraćena vizuelno; pomeri horizontalnu traku da pročitaš ostatak. To ne znači da je SQL tekst ili definicija nepotpuni.

---

## Pitanje 12

Kada u SQLTools-u izaberem **Open results as CSV** ili **Open results as JSON**, Windows mi prikaže poruku da nema aplikaciju za otvaranje `vscode-remote` linka. Da li mi nedostaje CSV/JSON drajver?

---

## Odgovor 12

Ne, ne nedostaje ti CSV/JSON drajver. SQLTools već ume da formatira rezultate u CSV i JSON, a SQLTools SQLite drajver je instaliran.

U WSL Remote sesiji komanda **Open Results** formira privremeni fajl, a zatim pokušava da ga otvori kao spoljašnji link. U ovom slučaju Windows dobija `vscode-remote` link koji ne može da obradi i zato prikazuje obaveštenje. To nije problem sa tvojim SQL upitom, bazom ili CSV/JSON formatom. Ne treba da instaliraš aplikaciju iz Microsoft Store-a zbog te poruke.

Da rezultat otvoriš pouzdano unutar VS Code-a:

1. Pokreni upit i fokusiraj njegov result tab.
2. Otvori Command Palette pomoću `Ctrl+Shift+P`.
3. Pokreni **SQLTools: Save Results**.
4. Izaberi **Save results as CSV** ili **Save results as JSON** i odredi gde da se fajl sačuva. SQLTools će sačuvani fajl otvoriti u VS Code-u.

**Napomena:** ovo je specifično za WSL Remote sesiju u VS Code-u. U običnom Windows terminalu ili Linux terminalu bez VS Code Remote ekstenzije, otvaranje CSV/JSON fajlova obično funkcioniše direktno sa podrazumevanim aplikacijama. U WSL Remote sesiji, VS Code pokušava da otvori fajl koristeći `vscode-remote` protokol, koji Windows ne prepoznaje kao standardnu aplikaciju, pa se pojavljuje poruka o nedostatku aplikacije. Zato je preporučeno koristiti opciju **Save Results** unutar VS Code-a ili kopirati rezultate u clipboard i ručno ih sačuvati. Ovo važi za sve spoljašnje linkove koje VS Code pokušava da otvori iz WSL Remote sesije, ne samo za CSV/JSON fajlove.

**Saveti za praktičnu upotrebu:**

- Ako često radiš sa CSV/JSON rezultatima u WSL Remote sesiji, navikni se na opciju **Save Results** i odabir lokacije unutar VS Code-a.

- Za brzi pregled možeš koristiti **Copy results as CSV/JSON to clipboard** i nalepiti u novi fajl u VS Code-u.

- Razumevanje razlike između SQLTools rezultata i SQLite CLI-ja u terminalu pomaže da izbegneš konfuziju oko otvaranja fajlova i fokusiranja na rezultate.

- Ako ne želiš da sačuvaš fajl, u istom meniju možeš izabrati **Copy results as CSV to clipboard** ili **Copy results as JSON to clipboard**, pa sadržaj nalepiti u novi fajl u VS Code-u.

---

## Pitanje 13

Koja je uloga **SQL Console** u VS Code-u i po čemu se razlikuje od SQLite CLI-ja u terminalu? Šta znači poruka **Not focused to results view**?

---

## Odgovor 13

**SQL Console nije SQLite CLI prompt.** To je panel SQLTools ekstenzije u VS Code-u koji prikazuje poruke vezane za trenutno fokusirani SQLTools prikaz rezultata. SQL upit pokrećeš iz `.sql` editora preko komandi SQLTools-a, a tabelu sa rezultatima gledaš u zasebnom results tabu.

Poruka **Not focused to results view** znači da SQLTools trenutno nema fokusiran tab sa rezultatima. Sama poruka **nije greška** i ne znači nužno da upit ili konekcija nisu uspeli. Klikni tab rezultata upita, na primer `ChinookPractice: SELECT ...`, da vidiš rezultat. SQL Console nije namenjen unosu SQL naredbi ili SQLite dot-komandi.

SQLite CLI radi u terminalu kao poseban program i zasebna konekcija:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Posle pokretanja vidiš SQLite prompt i u njega unosiš SQL:

```sql
SELECT Name FROM artists LIMIT 5;
```

ili SQLite CLI dot-komande:

```text
.tables
.schema albums
.quit
```

| SQLTools u VS Code-u                                                                                | SQLite CLI u terminalu                                                               |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Upit pokrećeš iz `.sql` editora, na primer **Run Selected Query** ili **Run on active connection**. | CLI pokrećeš iz Bash-a komandom `sqlite3 putanja/do/baze.db`.                        |
| SQLTools drajver koristi sačuvanu i izabranu konekciju. Rezultat se prikazuje u result tabu.        | SQLite CLI otvara bazu navedenu u komandi. SQL i dot-komande unosiš u SQLite prompt. |
| SQL Console prikazuje poruke vezane za rezultat i status njegovog fokusa.                           | Terminal prikazuje SQLite prompt, SQL rezultate i izlaz dot-komandi.                 |
| Zatvaranje results taba ne mora prekinuti sačuvanu ili aktivnu konekciju.                           | `.quit` zatvara SQLite CLI proces i njegovu konekciju.                               |

Oba alata mogu pristupiti istom `.db` fajlu, ali svaki uspostavlja **svoju konekciju**. Na primer, `PRAGMA foreign_keys` ili `ATTACH DATABASE` podešeni u jednoj konekciji ne postaju automatski podešavanja druge.

---

## Pitanje 14

Kako da pokrenem `.txt` fajl iz `playground/cli/`? Da li SQL upit treba da ukucam u taj fajl ili u terminal?

---

## Odgovor 14

Najpre razlikuj Bash terminal od SQLite CLI prompta:

1. U **Bash terminalu**, iz korena repozitorijuma, otvori radnu bazu:

   ```bash
   sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
   ```

2. Kada vidiš SQLite prompt, kao što je `SQLite>`, možeš direktno ukucati SQL upit:

   ```sql
   SELECT Name
   FROM artists
   LIMIT 5;
   ```

   Završi naredbu tačka-zarezom `;` i pritisni Enter. Ovo SQL upit izvršava odmah nad bazom otvorenom u toj konekciji.

3. Da učitaš fajl, na **SQLite promptu** unesi `.read` i putanju:

   ```text
   .read fast-api-course-my-work/sqlite_for_beginners/playground/cli/02_some_commonly_used_sqlite3_commands.txt
   ```

   Ta putanja je relativna u odnosu na direktorijum u kom je pokrenut SQLite CLI. U primeru ga pokrećeš iz korena repozitorijuma. `.read` nije Bash komanda; radi tek kada je SQLite CLI otvoren.

`.read` učitava fajl red po red kao ulaz u **trenutnu SQLite CLI konekciju**. Fajl može sadržati SQLite CLI dot-komande, SQL naredbe ili komentare. Ekstenzija `.txt` sama po sebi ne izvršava ništa — važno je šta je unutar fajla.

Tvoj trenutni `02_some_commonly_used_sqlite3_commands.txt` sadrži samo komentare koji opisuju lekciju, pa se pri učitavanju ne vidi rezultat. Nema SQL upita koji bi se izvršio. Fajl `01_what_is_sqlite3_tool.txt` sada sadrži **primere SQL upita i CLI dot-komandi**, pa možeš preko `.read` da vidiš obe vrste unosa. Za odgovore na redovne SQL vežbe koristi odgovarajući `.sql` fajl u `playground/sql/`; `.txt` u `playground/cli/` služe za beleške i vežbanje samog komandnog alata. Možeš ih otvoriti u editoru, dopisati sadržaj, sačuvati, pa tek onda pokrenuti `.read`.

Na primer, ako sačuvaš upit u `.sql` fajlu, istu skriptu možeš učitati iz SQLite prompta ovako:

```text
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/01_what_is_sqlite.sql
```

Pre `.read` proveri sadržaj skripte i otvorenu bazu. Skripta može sadržati naredbe koje menjaju podatke, a `.read` će ih izvršiti nad tom konekcijom.

---

## Pitanje 15

Da li je ispravna tvrdnja da mogu da koristim `litecli` bez aktiviranja `.venv` u svakom terminalu, ako ga pokrenem preko `.venv/bin/litecli`?

---

## Odgovor 15

Da. Iz **korena repozitorijuma**, u Bash terminalu, možeš pokrenuti:

```bash
.venv/bin/litecli --version
```

Ta komanda poziva `litecli` direktno preko putanje do izvršnog fajla. U ovom projektu taj fajl je podešen da koristi Python iz projektnog `.venv`, pa aktivacija nije preduslov da bi se koristili paketi instalirani u tom okruženju.

Aktivacija pomoću `source .venv/bin/activate` prvenstveno menja podešavanja **trenutnog terminala**, naročito `PATH`, tako da možeš napisati kraće `litecli` umesto putanje. Direktno pokretanje ne aktivira `.venv` za ostale komande u terminalu: na primer, sledeća komanda `python` ne mora koristiti projektni interpreter.

Putanja `.venv/bin/litecli` je **relativna**: radi iz korena projekta, ali ne nužno iz drugog direktorijuma. Tamo možeš navesti odgovarajuću relativnu ili apsolutnu putanju do istog izvršnog fajla. `.venv` i `litecli` moraju postojati u okruženju u kojem komandu pokrećeš; ova WSL putanja nije automatski dostupna u Windows PowerShell-u.

---

## Pitanje 16

Zar nije svaki terminal zaseban? Kako `litecli` može da radi u novom terminalu bez aktiviranja `.venv`?

---

## Odgovor 16

Da, svaki terminal ima **svoje shell okruženje**. Ako u jednom terminalu aktiviraš `.venv`, time ga ne aktiviraš automatski u drugom. Novi terminal ipak može naslediti neka početna podešavanja od procesa koji ga pokreće.

Trik je u razlici između dva načina pokretanja:

1. **`litecli`** — shell traži program kroz svoj `PATH`. Aktivacija `.venv` dodaje njegov `bin` direktorijum u `PATH` tog terminala, pa tako pronalazi projektni `litecli`. U novom terminalu bez aktivacije ova kratka komanda ne mora raditi, osim ako je `litecli` dostupan u `PATH`-u na neki drugi način.
2. **`.venv/bin/litecli`** — shell dobija direktnu putanju do programa, pa ne mora da ga traži u `PATH`-u. Instalirani launcher zatim koristi Python iz projektnog `.venv`, iako okruženje nije aktivirano u shell-u.

Dakle, u novom WSL Bash terminalu iz korena projekta možeš pokrenuti `.venv/bin/litecli` bez aktivacije, ali to **ne aktivira `.venv` u tom terminalu** niti menja komandu `python` za naredne pozive. Fajl `.venv/bin/litecli` mora postojati, a iz drugog radnog direktorijuma potrebna je odgovarajuća putanja.

Ranija rečenica važi za poziv **sa putanjom**, ne kao obećanje da će sama komanda `litecli` raditi u svakom novom terminalu.

Primer i razlika između pokretanja `litecli` sa direktnom putanjom do izvršnog fajla i pokretanja samo `litecli` u terminalu bez aktivacije `.venv` može se ilustrovati ovako:

```bash
# Direktno preko putanje do izvršnog fajla u projektnom .venv
.venv/bin/litecli --version

# Samo komanda litecli, bez aktivacije .venv
litecli --version
```

U ovom primeru, prva komanda koristi direktnu putanju do `litecli` u projektnom `.venv` i uspešno prikazuje verziju, dok druga komanda pokušava da pozove `litecli` iz `PATH`-a bez aktivacije `.venv`. Ako `litecli` nije globalno instaliran ili nije u `PATH`-u, druga komanda će prijaviti grešku da komanda nije pronađena. Ovo jasno ilustruje razliku između pozivanja izvršnog fajla sa apsolutnom ili relativnom putanjom i oslanjanja na `PATH` promenljivu u shell-u.

Dakle, kada želiš da koristiš projektni `litecli` bez aktivacije `.venv`, uvek je sigurnije pozvati ga preko direktne putanje do izvršnog fajla (`.venv/bin/litecli`).

---

## Pitanje 17

Pošto ne koristim SQLTools u drugim projektima, da li je bolje da sve SQLite verzije uskladimo na 3.54.1 ili da instaliramo najnoviju verziju za CLI, Python i SQLTools?

## Odgovor 17

Pri proveri zvanične [SQLite stranice za preuzimanje](https://www.sqlite.org/download.html), **3.54.1 je najnovija objavljena SQLite verzija**, pa su trenutno „3.54.1“ i „najnovija SQLite verzija“ isti cilj. To se može promeniti kada izađe novo izdanje.

Za sada preporučujem da **ne menjamo sve biblioteke samo radi jednakog broja verzije**. Za uvodne vežbe možemo koristiti postojeće alate i proveravati verziju klijenta sa `SELECT sqlite_version();`. Ako kasnije bude potrebna određena novija SQL funkcija ili postoji važna bezbednosna ispravka, tada ćemo planirati ažuriranje i testiranje.

Pri proveri ovog okruženja:

| Klijent | SQLite verzija | Napomena |
| --- | --- | --- |
| SQLite CLI | 3.54.1 | Samostalno instaliran komandni alat. |
| Projektni Python i `litecli` | 3.45.1 | Projektni Python koristi sistemsku SQLite biblioteku. |
| SQLTools SQLite drajver | 3.44.2 | Toliko je prijavio njegov instalirani Node `sqlite3` paket u zasebnoj proveri; proveri i aktivnu SQLTools konekciju. |

Verzija SQLite biblioteke **nije isto** što i verzija Python-a, Node.js-a, npm paketa `sqlite3` ili SQLTools ekstenzije. Nadogradnja CLI-ja ne nadograđuje automatski ostale. Isti broj verzije takođe ne garantuje identična podešavanja konekcije ili opcije sa kojima su biblioteke izgrađene.

Činjenica da nema drugih projekata koji koriste SQLTools smanjuje opseg moguće štete, ali projektni Python trenutno koristi **sistemsku** biblioteku koja može služiti i drugim programima. Zamena sistemske biblioteke nije isto što i nadogradnja jednog projektnog paketa. SQLTools drajver trenutno zahteva Node paket `sqlite3` verzije `5.1.7`, pa ni instaliranje proizvoljno novijeg Node paketa nije automatski kompatibilno. Usklađivanje bi zahtevalo pažljiv izbor načina instalacije i proveru nakon promene.

Za uporednu proveru pokreni `SELECT sqlite_version();` posebno u CLI-ju, `litecli`-ju i SQLTools-u. Za projektnu Python biblioteku možeš, uz aktiviran `.venv`, pokrenuti:

```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

Ostavljanje različitih verzija nije razlog da zanemariš ažuriranja: sistemske pakete održavaj kroz podržane Ubuntu nadogradnje, a ostale alate prema njihovom načinu instalacije. Kada neki zadatak zavisi od nove funkcije, proveri da je podržava **svaki klijent** u kojem želiš da ga izvršiš.

---
