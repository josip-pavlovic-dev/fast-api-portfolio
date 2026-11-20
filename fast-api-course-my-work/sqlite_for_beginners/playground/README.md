# Playground — prostor za vežbanje

Ovde rešavaj praktične zadatke iz lekcija. Teorijski materijali ostaju u svojim oblastima. Odgovore i upite čuvaj u odgovarajućim fajlovima ispod `sql/` ili `cli/`.

## Struktura

```text
playground/
├── databases/
│   ├── README.md
│   ├── chinook_practice.db            # lokalna kopija Chinook baze
│   └── sandbox.db                     # prazna baza za sopstvene eksperimente
├── cli/                               # beleške i vežbe za SQLite CLI alat
│   ├── 01_what_is_sqlite3_tool.txt
│   ├── 02_some_commonly_used_sqlite3_commands.txt
│   └── 03_sqlite_dump_command.txt
└── sql/                               # SQL skripte za vežbe iz lekcija
    ├── 00_intro/
    └── 02_retriving_data_and_manipulating_data/
```

Fajlovi `sql/` i `cli/` odgovaraju lekcijama istog naziva. Skripte su početni šabloni za rešavanje zadataka.

**Tekstualne i dijagramske zadatke rešavaj u komentarima ili svojim beleškama.**

---

## Priprema baza

Originalna baza ostaje ne izmenjena u `../chinook/chinook.db`. Vežbaj na lokalnoj kopiji. Fajlovi baza i njihovi `SQLite journal/WAL` prateći fajlovi su isključeni iz `Git`-a, dok su `SQL skripte` i `README` fajlovi verzionisani što omogućava praćenje promena u vežbama.

Prvi put napravi kopiju i praznu bazu iz root-a repozitorijuma:

```bash
mkdir -p fast-api-course-my-work/sqlite_for_beginners/playground/databases
cp fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
sqlite3 fast-api-course-my-work/sqlite_for_beginners/playground/databases/sandbox.db
```

Poslednja komanda otvara SQLite CLI i kreira `sandbox.db` ako ne postoji. Izađi iz CLI-ja komandom `.quit`. Za resetovanje Chinook kopije ponovo pokreni `cp` komandu; ona će zameniti lokalnu kopiju originalom.

Detalji o lokalnim bazama i njihovom ponovnom kreiranju nalaze se u [databases/README.md](./databases/README.md).

## Rad na SQL vežbama

1. Otvori teorijsku lekciju i pročitaj zadatke u odeljku **Vežbe**.
2. Otvori istoimeni `.sql` fajl u odgovarajućem podfolderu `sql/`.
3. Ispod zaglavlja zapiši rešenje za svaki zadatak. Koristi komentare poput `-- Vežba 1` da bi se rešenja lakše pratila.
4. Poveži SQLite ekstenziju u VS Code-u sa `databases/chinook_practice.db`, ili pokreni CLI iz root-a repozitorijuma:

   ```bash
   sqlite3 fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
   ```

5. U SQLite CLI-ju pokreni skriptu komandom `.read`, na primer:

   ```sql
   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/01_sqlite_select_statement.sql
   ```

Putanje u primerima su date u odnosu na root repozitorijuma. Ako radiš u GUI ekstenziji, otvori `.sql` fajl i izvrši upit nad povezanom bazom.

Pre `.read` komande, SQLite CLI mora već biti pokrenut nad bazom. Kada vidiš SQLite prompt, na primer `SQLite>`, možeš odmah uneti SQL upit i pritisnuti Enter:

```sql
SELECT Name
FROM artists
LIMIT 5;
```

SQL naredbu završi tačka-zarezom `;`. `.read` je SQLite CLI komanda koja učitava i izvršava linije iz fajla u toj istoj konekciji; ona nije Bash komanda i ne unosi se pre pokretanja `sqlite3`. Ekstenzija fajla (`.txt` ili `.sql`) sama po sebi ne određuje sadržaj ni ponašanje — važno je da fajl sadrži važeće CLI komande ili SQL naredbe.

---

## Rad na SQLite CLI vežbama

Fajlovi u `cli/` služe za beleženje komandi koje počinju tačkom, kao što su `.tables`, `.schema`, `.mode` i `.dump`. To su komande SQLite alata, a ne SQL naredbe; pokreći ih u SQLite CLI-ju, ne kao obične SQL upite u editoru. Možeš ih izvršavati pojedinačno ili učitati tekstualni fajl iz CLI-ja pomoću `.read`, na primer:

```sql
.read fast-api-course-my-work/sqlite_for_beginners/playground/cli/02_some_commonly_used_sqlite3_commands.txt
```

Trenutni `02_some_commonly_used_sqlite3_commands.txt` je samo početni šablon sa komentarima, pa njegovo učitavanje neće prikazati upit ili drugi vidljiv rezultat. Nasuprot tome, `01_what_is_sqlite3_tool.txt` je popunjen primerima SQL upita i SQLite CLI dot-komandi; učitaj ga preko `.read` da vidiš kako obe vrste naredbi rade u istoj sesiji. Beleške u `cli/` služe za vežbe komandnog alata. Rešenja redovnih SQL vežbi čuvaj u odgovarajućim `.sql` fajlovima u `playground/sql/`; možeš ih pokrenuti pojedinačno na promptu ili učitati pomoću `.read`.

Vežbe koje izvoze fajlove (na primer CSV ili SQL dump) pokreći iz root-a repozitorijuma i čuvaj rezultate u `playground/`. Pre nego što ih dodaš u Git, proveri da ne sadrže nepotrebne ili osetljive podatke.
