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
│   ├── 03_sqlite_dump_command.txt
│   └── 04_sqlite_schema_and_drop_table.txt
└── sql/                               # SQL skripte za vežbe iz lekcija
    ├── 00_intro/
    ├── 02_retriving_data_and_manipulating_data/
    ├── 03_creating_database_tables_updating_data_deleting_records/
    ├── 04_some_sqlite_operators/
    ├── 05_table_joins/
    └── 06_sqlite_aggregate_functions/
```

Fajlovi `sql/` i `cli/` prate lekcije. SQL skripte sadrže proverene primere, rešenja i komentare za samostalnu proveru; prvo pokušaj zadatak bez gledanja rešenja.

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
3. Prvo pokušaj svaki zadatak samostalno. Zatim pokreni odgovarajući SQL blok da proveriš rezultat; tekstualne ili dijagramske odgovore dopiši u komentarima ili svojim beleškama.
4. Izaberi bazu prema vrsti vežbe:
   - Oblast 00: `01_what_is_sqlite.sql` i `03_how_to_connect_to_sqlite.sql` su provere za Chinook kopiju; `02_attaching_sample_database_to_sqlite.sql` i `04_database_concepts.sql` pokreći iz root-a u svežoj `:memory:` konekciji. Skripta 02 priključuje postojeće Chinook fajlove kao read-only; skripta 04 pravi i popunjava sopstvene tabele samo u memoriji.
   - Oblasti 02, 04, 05 i 06 sadrže upite za čitanje Chinook baze. Koristi `databases/chinook_practice.db` samo za čitanje. Agregatne funkcije u oblasti 06 uključuju i CTE primere nad privremenim vrednostima, ali ne menjaju bazu.
   - Oblast 03 kreira tabele i menja ili briše podatke. Za CLI otvori novu memorijsku bazu iz root-a repozitorijuma:

   ```bash
   sqlite3 :memory:
   ```

   U SQLTools-u koristi novu/praznu `databases/sandbox.db` konekciju, nikada Chinook ili bazu aplikacije. SQL skripte oblasti 03 nisu namenjene za pokretanje više puta nad istom već popunjenom bazom; napravi novu probnu bazu ili je bezbedno resetuj pre ponovnog izvršavanja.

5. U SQLite CLI-ju pokreni odgovarajuću skriptu komandom `.read`, na primer za oblast 02:

   ```sql
   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/02_retriving_data_and_manipulating_data/01_sqlite_select_statement.sql
   ```

   Primer iz oblasti 03, koji treba pokrenuti u svežoj `:memory:` konekciji:

   ```sql
   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/03_creating_database_tables_updating_data_deleting_records/01_sqlite_constraints.sql
   ```

   Primer iz oblasti 04:

   ```sql
   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/04_some_sqlite_operators/01_sqlite_BETWEEN_operator.sql
   ```

   Primer iz oblasti 05:

   ```sql
   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/05_table_joins/01_sqlite_LEFT_join.sql
   ```

   Primer iz oblasti 06:

   ```sql
   .read fast-api-course-my-work/sqlite_for_beginners/playground/sql/06_sqlite_aggregate_functions/01_introduction_to_sqlite_aggregate_functions.sql
   ```

Putanje u primerima su date u odnosu na root repozitorijuma. Ako radiš u GUI ekstenziji, otvori `.sql` fajl i izvrši upit nad povezanom bazom. Oblast 01 se vežba kroz fajlove u `cli/`; oni sadrže dot-komande, a ne SQL skripte.

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

Za vežbe iz oblasti 03, [04_sqlite_schema_and_drop_table.txt](./cli/04_sqlite_schema_and_drop_table.txt) koristi `.tables` i `.schema` za pregled DDL-a, zatim demonstrira `DROP TABLE` unutar transakcije i vraćanje šeme sa `ROLLBACK`. Pokreni je iz nove `sqlite3 :memory:` konekcije.

`01_what_is_sqlite3_tool.txt` i `02_some_commonly_used_sqlite3_commands.txt` sadrže bezbedne provere nad Chinook kopijom; druga skripta uključuje i uspešan upit bez rezultata. U CLI-ju 3.54.1 interaktivna kombinacija `.headers on` i praznog CSV rezultata ne prikazuje zaglavlje; teorijska lekcija pokazuje `-header` kao alternativu kada je zaglavlje potrebno. `03_sqlite_dump_command.txt` proverava bazu, a granični slučaj prazne tabele demonstrira se u odvojenoj memorijskoj sesiji. Beleške u `cli/` služe za vežbe komandnog alata. Rešenja redovnih SQL vežbi čuvaj u odgovarajućim `.sql` fajlovima u `playground/sql/`; možeš ih pokrenuti pojedinačno na promptu ili učitati pomoću `.read`.

Vežbe koje izvoze fajlove (na primer CSV ili SQL dump) pokreći iz root-a repozitorijuma i čuvaj rezultate u `playground/`. Pre nego što ih dodaš u Git, proveri da ne sadrže nepotrebne ili osetljive podatke.
