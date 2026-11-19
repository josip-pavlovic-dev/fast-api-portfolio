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
