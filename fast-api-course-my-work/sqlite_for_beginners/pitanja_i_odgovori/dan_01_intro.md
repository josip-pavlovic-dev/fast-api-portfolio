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
