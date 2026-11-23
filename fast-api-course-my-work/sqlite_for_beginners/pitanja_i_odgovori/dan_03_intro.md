# Pitanja i odgovori — Dan 03: Uvod u SQLite

## Pitanje 1

Koje SQLite PRAGMA naredbe postoje i čemu služe?

---

## Odgovor 1

**PRAGMA** je posebna SQLite naredba za pregled internih informacija ili upravljanje određenim podešavanjima. Neke samo prikazuju informacije, neke menjaju ponašanje konekcije, a neke mogu menjati bazu ili uticati na njenu bezbednost i performanse.

> **Najvažnije za početak:** `database_list`, `table_info`, `foreign_key_list`, `foreign_keys`, `index_list`, `foreign_key_check` i `quick_check`.

Ovo je praktičan pregled, grupisan po nameni. Spisak ispod obuhvata nazive koje je `PRAGMA pragma_list;` vratio u tvojoj proveravanoj verziji SQLite CLI-ja **3.54.1**. Dostupnost i ponašanje mogu zavisiti od verzije, načina kompajliranja i klijenta. Za konačne detalje pogledaj [zvaničnu SQLite dokumentaciju](https://www.sqlite.org/pragma.html).

### 1. Osnovna sintaksa

```sql
PRAGMA foreign_keys;
PRAGMA table_info('tracks');
PRAGMA foreign_keys = ON;
```

- Prva naredba proverava vrednost podešavanja `foreign_keys` u trenutnoj konekciji.
- Druga traži informacije o kolonama tabele `tracks`.
- Treća **menja podešavanje** trenutne konekcije; ne pokreći je nasumično u tuđoj aplikaciji.

Naredbe završavaj sa `;`. `PRAGMA` je SQLite proširenje, a ne univerzalna SQL sintaksa za sve sisteme. Nije isto što i `.schema` ili `.databases`: komande sa tačkom obrađuje **SQLite CLI**, dok `PRAGMA` obrađuje SQLite.

Važno: ako pogrešno napišeš ime PRAGMA naredbe, SQLite je može **tiho ignorisati** umesto da prijavi grešku. Prazan rezultat zato nije uvek dokaz da je provera uspela.

---

### 2. Kako bezbedno vežbati

Iz korena repozitorijuma u Bash terminalu otvori radnu Chinook bazu samo za čitanje:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Zatim u SQLite CLI-ju unosi SQL primere iz ovog vodiča. Po završetku izađi sa:

```text
.quit
```

Režim `-readonly` štiti otvoreni fajl od upisa, ali **ne znači** da su sve PRAGMA naredbe bez posledica po konekciju ili proces. Za sada koristi samo pregledne primere ispod. Ne izvršavaj opcije koje menjaju podešavanja ili održavaju bazu bez razumevanja njihove namene.

---

## 3. Najkorisnije naredbe za pregled

### 3.1. Koja je baza otvorena?

```sql
PRAGMA database_list;
```

Prikazuje bazu `main`, eventualnu `temp` bazu i priključene baze. Rezultat sadrži `seq`, `name` i `file`. Na primer, ako je Chinook priključen pod imenom `chinook`, pojavljuje se red sa tim nazivom i njegovom putanjom.

SQLite CLI ima i `.databases`, ali to je **CLI komanda**, ne PRAGMA.

---

### 3.2. Koje kolone ima tabela?

```sql
PRAGMA table_info('tracks');
```

| Kolona rezultata | Značenje                                                                    |
| ---------------- | --------------------------------------------------------------------------- |
| `cid`            | Redni broj kolone u ovom prikazu.                                           |
| `name`           | Naziv kolone.                                                               |
| `type`           | Deklarisani tip kolone.                                                     |
| `notnull`        | `1` ako je u ovom prikazu označena kao `NOT NULL`, inače `0`.               |
| `dflt_value`     | Deklarisana podrazumevana vrednost, ako postoji.                            |
| `pk`             | `0` ako nije deo PK-a; pozitivan broj označava poziciju u primarnom ključu. |

Na primer, u `tracks` je `AlbumId` opcion, a `MediaTypeId` ima `NOT NULL`. Za pojedine oblike primarnog ključa SQLite ima posebna pravila, pa `notnull` ne treba posmatrati kao jedini dokaz svih ograničenja: uporedi i sa `.schema tracks`.

```sql
PRAGMA table_xinfo('tracks');
```

`table_xinfo` daje i informacije o generisanim ili skrivenim kolonama koje `table_info` može izostaviti. Kolona rezultata `hidden` pomaže u njihovom razlikovanju.

```sql
PRAGMA table_list;
```

Prikazuje tabele i poglede, uključujući informaciju o bazi (`schema`), vrsti objekta i broju kolona. Može uključiti i interne objekte, pa broj redova nije nužno broj korisničkih tabela.

### 3.3. Koji su strani ključevi i da li se proveravaju?

```sql
PRAGMA foreign_key_list('tracks');
```

Prikazuje **deklaracije** FK-ova u `tracks`. Na primer, red za `genres` pokazuje da `tracks.GenreId` referencira `genres.GenreId`. `on_update` i `on_delete` pokazuju definisane akcije; ne govore sami po sebi da li se one trenutno sprovode.

```sql
PRAGMA foreign_keys;
```

- `1`: provera FK-ova je uključena u **trenutnoj konekciji**.
- `0`: provera nije uključena u toj konekciji.

U zasebnoj CLI proveri rezultat je bio `0`; to **ne govori** kakvo je podešavanje u tvojoj otvorenoj aplikaciji ili SQLTools-u. Proveri svaku konekciju posebno.

Ako namerno želiš da uključiš proveru u svojoj konekciji, uradi to **pre transakcije**, pa proveri rezultat:

```sql
PRAGMA foreign_keys = ON;
PRAGMA foreign_keys;
```

Promena ovog podešavanja usred aktivne transakcije nema efekta. Uključenje provere ne popravlja automatski stare neispravne redove.

```sql
PRAGMA foreign_key_check;
```

Traži postojeća kršenja stranih ključeva. **Bez redova** znači da u proverenom opsegu nije pronađeno kršenje; redovi rezultata opisuju pronađene probleme. U read-only proveri radne Chinook baze nije bilo redova. To ne uključuje automatski FK proveru za buduće izmene.

### 3.4. Koji indeksi postoje?

```sql
PRAGMA index_list('albums');
```

Prikazuje indekse povezane sa tabelom. Među kolonama su `name`, `unique`, `origin` i `partial`. U proveravanoj bazi pojavljuje se indeks `IFK_AlbumArtistId`.

```sql
PRAGMA index_info('IFK_AlbumArtistId');
PRAGMA index_xinfo('IFK_AlbumArtistId');
```

`index_info` prikazuje ključne kolone indeksa, dok `index_xinfo` prikazuje i dodatne informacije. Ime indeksa mora postojati u bazi koju proveravaš.

### 3.5. Da li postoje problemi sa bazom?

```sql
PRAGMA quick_check;
PRAGMA integrity_check;
```

`quick_check` je brža, manje temeljna provera; `integrity_check` obavlja opsežniju proveru i može trajati duže. Rezultat `ok` znači da ta provera nije pronašla probleme koje ispituje; nije zamena za rezervnu kopiju.

**Ove provere ne zamenjuju `foreign_key_check`.** Koristi zasebno `PRAGMA foreign_key_check;` za kršenja stranih ključeva. U našoj read-only proveri `quick_check` je vratio `ok`.

### 3.6. Spisak naredbi, verzija i mogućnosti

```sql
PRAGMA pragma_list;
PRAGMA compile_options;
SELECT sqlite_version();
```

- `pragma_list` prikazuje nazive dostupnih PRAGMA naredbi, ne njihovu dokumentaciju.
- `compile_options` prikazuje opcije korišćene prilikom izgradnje SQLite biblioteke.
- `sqlite_version()` je **SQL funkcija**, ne PRAGMA; pokazuje verziju biblioteke klijenta koji izvršava upit.

Tvoj SQLite CLI, Python/`litecli` i SQLTools mogu koristiti različite SQLite biblioteke. Zato proveru uradi u **onom klijentu čije ponašanje te zanima**.

---

## 4. PRAGMA i priključena baza

Ako je baza prethodno priključena kao `chinook`, neke PRAGMA naredbe mogu navesti baš tu bazu:

```sql
PRAGMA chinook.table_info('employees');
PRAGMA chinook.foreign_key_list('tracks');
PRAGMA chinook.foreign_key_check;
```

Bez prefiksa, za ove primere se koristi `main`. Prefiks `chinook` mora odgovarati nazivu iz tvoje trenutne konekcije; nije naziv fajla. **Nije svaki PRAGMA vezan za pojedinačnu bazu**: na primer, `foreign_keys` je podešavanje konekcije.

Neke pregledne PRAGMA naredbe dostupne su i kao funkcije u `SELECT` upitu:

```sql
SELECT name, type, "notnull", pk
FROM pragma_table_info('tracks')
WHERE "notnull" = 1;
```

Ovde možemo filtrirati izlaz pomoću `WHERE`. Ovaj oblik ne postoji za sve PRAGMA naredbe; namenjen je podržanim ugrađenim PRAGMA naredbama koje vraćaju rezultate bez sporednih efekata.

---

## 5. Pregled dostupnih PRAGMA naredbi

U tabelama **pregled / podešavanje** znači da naredba može služiti za oba, u zavisnosti od sintakse. To ne znači da je bezbedno promeniti je. Neka podešavanja važe za konekciju, neka za bazu ili proces; trajnost se razlikuje po naredbi.

### Pregled šeme i okruženja

| PRAGMA             | Namena                                                           |
| ------------------ | ---------------------------------------------------------------- |
| `pragma_list`      | Spisak PRAGMA naziva dostupnih u toj SQLite gradnji.             |
| `database_list`    | Priključene baze i njihove putanje.                              |
| `table_list`       | Tabele i pogledi po šemama.                                      |
| `table_info`       | Osnovne informacije o kolonama tabele.                           |
| `table_xinfo`      | Proširene informacije, uključujući skrivene i generisane kolone. |
| `foreign_key_list` | Deklarisani strani ključevi jedne tabele.                        |
| `index_list`       | Indeksi povezani sa tabelom.                                     |
| `index_info`       | Ključne kolone indeksa.                                          |
| `index_xinfo`      | Proširene informacije o kolonama indeksa.                        |
| `collation_list`   | Dostupne sekvence za poređenje i sortiranje teksta.              |
| `function_list`    | SQL funkcije dostupne u toj konekciji.                           |
| `module_list`      | Moduli virtuelnih tabela dostupni u konekciji.                   |
| `compile_options`  | Opcije korišćene pri kompajliranju SQLite biblioteke.            |

### Integritet, ključevi i proveravanje

| PRAGMA                     | Namena                                                                                         |
| -------------------------- | ---------------------------------------------------------------------------------------------- |
| `foreign_keys`             | Pregled / podešavanje sprovođenja stranih ključeva po konekciji.                               |
| `foreign_key_check`        | Pronalazi postojeća kršenja stranih ključeva.                                                  |
| `defer_foreign_keys`       | Privremeno odlaže proveru svih FK ograničenja do završetka transakcije kada je uključeno.      |
| `ignore_check_constraints` | Pregled / podešavanje ignorisanja `CHECK` ograničenja; isključivanje zaštite zahteva oprez.    |
| `integrity_check`          | Opsežnija provera integriteta baze; ne proverava FK kršenja.                                   |
| `quick_check`              | Brža, manje opsežna provera integriteta.                                                       |
| `cell_size_check`          | Dodatna provera veličina ćelija pri čitanju stranica baze.                                     |
| `query_only`               | Ograničava SQL izmene kroz trenutnu konekciju; nije isto što i otvaranje fajla sa `-readonly`. |
| `trusted_schema`           | Kontroliše poverenje u funkcije i virtuelne tabele korišćene u šemi; bezbednosno podešavanje.  |

### Stranice, memorija i veličina baze

| PRAGMA            | Namena                                                                    |
| ----------------- | ------------------------------------------------------------------------- |
| `page_size`       | Pregled / podešavanje veličine stranice baze; promena ima posebne uslove. |
| `page_count`      | Broj stranica baze.                                                       |
| `freelist_count`  | Broj slobodnih stranica koje baza može ponovo koristiti.                  |
| `max_page_count`  | Pregled / podešavanje maksimalnog broja stranica.                         |
| `cache_size`      | Predložena veličina keša stranica za konekciju i odgovarajuću bazu.       |
| `cache_spill`     | Kontroliše upis izmenjenih keš stranica tokom transakcije.                |
| `mmap_size`       | Pregled / podešavanje korišćenja memorijskog mapiranja fajla.             |
| `temp_store`      | Podešavanje gde se privremene strukture čuvaju, uz ograničenja gradnje.   |
| `shrink_memory`   | Traži od SQLite-a da oslobodi memoriju koju može da vrati.                |
| `hard_heap_limit` | Pregled / smanjivanje čvrste granice SQLite heap memorije.                |
| `soft_heap_limit` | Pregled / podešavanje preporučene granice SQLite heap memorije.           |

### Dnevnik, transakcije i istovremeni pristup

| PRAGMA                 | Namena                                                                                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `journal_mode`         | Pregled / promena režima dnevnika, na primer `DELETE` ili `WAL`; promena može uticati na fajlove i druge konekcije.    |
| `journal_size_limit`   | Pregled / ograničenje veličine zadržanog dnevnika ili WAL-a nakon odgovarajućih operacija.                             |
| `synchronous`          | Podešavanje sinhronizacije upisa i kompromisa između pouzdanosti i brzine.                                             |
| `locking_mode`         | Pregled / podešavanje načina zaključavanja baze za konekciju.                                                          |
| `busy_timeout`         | Vreme u milisekundama koje konekcija čeka na oslobađanje zaključavanja pre nego što odustane; menja njen busy handler. |
| `read_uncommitted`     | Podešavanje povezano sa čitanjem nepotvrđenih podataka; efekat u SQLite-u zavisi od shared-cache režima.               |
| `wal_autocheckpoint`   | Pregled / podešavanje automatskog WAL checkpoint-a za konekciju.                                                       |
| `wal_checkpoint`       | Pokreće WAL checkpoint; nije samo pregledno pitanje.                                                                   |
| `checkpoint_fullfsync` | Podešavanje dodatne sinhronizacije pri checkpoint-u na podržanim platformama.                                          |
| `fullfsync`            | Podešavanje punije sinhronizacije upisa na podržanim platformama.                                                      |

### Održavanje, optimizacija i ponašanje upita

| PRAGMA                      | Namena                                                                                              |
| --------------------------- | --------------------------------------------------------------------------------------------------- |
| `optimize`                  | Može pokrenuti korisne optimizacije, uključujući analizu statistika; može upisivati u bazu.         |
| `analysis_limit`            | Ograničava broj pregledanih redova tokom približne analize indeksa.                                 |
| `automatic_index`           | Uključuje ili isključuje mogućnost pravljenja automatskih indeksa za upite.                         |
| `auto_vacuum`               | Pregled / podešavanje režima vraćanja slobodnih stranica; promena može zahtevati `VACUUM`.          |
| `incremental_vacuum`        | Oslobađa određeni broj slobodnih stranica u odgovarajućem incremental režimu; menja bazu.           |
| `secure_delete`             | Podešava prepisivanje obrisanog sadržaja radi smanjenja mogućnosti njegovog oporavka.               |
| `recursive_triggers`        | Pregled / podešavanje rekurzivnog izvršavanja trigger-a.                                            |
| `reverse_unordered_selects` | Za testiranje okreće redosled mnogih rezultata bez `ORDER BY`; ne zamenjuje eksplicitno sortiranje. |
| `threads`                   | Pregled / ograničenje broja pomoćnih radnih niti koje SQLite može koristiti.                        |
| `legacy_alter_table`        | Podešava starije ponašanje određenih `ALTER TABLE` operacija.                                       |

### Metapodaci i verzije baze

| PRAGMA            | Namena                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------ |
| `encoding`        | Pregled / podešavanje kodiranja teksta baze, uz ograničenja kada se može menjati.          |
| `application_id`  | Pregled / postavljanje ID-ja formata aplikacije u zaglavlju baze.                          |
| `user_version`    | Pregled / postavljanje broja verzije koji određuje aplikacija, često za migracije.         |
| `data_version`    | Pomaže da ista konekcija uoči izmene koje su druge konekcije potvrdile između dve provere. |
| `schema_version`  | Interna verzija šeme; SQLite njome upravlja. Ručno menjanje je opasno.                     |
| `writable_schema` | Omogućava posebne izmene sistemske šeme; može oštetiti bazu i nije za redovnu upotrebu.    |

### Zastarele ili posebne opcije

Ove opcije mogu postojati radi kompatibilnosti sa starim programima. **Ne preporučuju se za nove primere.**

| PRAGMA                   | Namena / upozorenje                                                                 |
| ------------------------ | ----------------------------------------------------------------------------------- |
| `case_sensitive_like`    | Zastarela promena ponašanja `LIKE`; može izazvati probleme sa izrazima i indeksima. |
| `count_changes`          | Zastareli način vraćanja broja izmenjenih redova.                                   |
| `default_cache_size`     | Zastarelo podešavanje podrazumevane veličine keša u zaglavlju baze.                 |
| `empty_result_callbacks` | Zastarelo podešavanje callback ponašanja za prazne rezultate.                       |
| `full_column_names`      | Zastarelo podešavanje formiranja naziva kolona rezultata.                           |
| `short_column_names`     | Zastarelo podešavanje skraćenih naziva kolona rezultata.                            |
| `temp_store_directory`   | Zastarelo globalno podešavanje direktorijuma privremenih fajlova.                   |

Zvanična dokumentacija navodi i druge, po potrebi dostupne PRAGMA naredbe, uključujući zastarele, interne i one koje zahtevaju posebnu debug gradnju. One **nisu nužno prisutne** u tvom `pragma_list` rezultatu; odsustvo ili dostupnost u drugom klijentu zavisi od njegove SQLite biblioteke.

---

## 6. Kratka vežba za proveru

Dok je radna Chinook baza otvorena kao `main` samo za čitanje, probaj redom:

```sql
PRAGMA database_list;
PRAGMA table_info('albums');
PRAGMA foreign_key_list('albums');
PRAGMA foreign_keys;
PRAGMA foreign_key_check;
PRAGMA quick_check;
```

1. Koju putanju pokazuje red `main`?
2. Koja je kolona primarni ključ tabele `albums`?
3. Na koju tabelu i kolonu upućuje `albums.ArtistId`?
4. Da li je FK provera uključena u **ovom klijentu**?
5. Da li `foreign_key_check` vraća redove, a `quick_check` rezultat `ok`?

**Očekivanje za šemu:** `AlbumId` je PK, a `ArtistId` referencira `artists.ArtistId`. Ostali rezultati zavise od otvorene baze i podešavanja konkretne konekcije. `quick_check` može potrajati na velikim bazama.

---

## Pitanje 2

Mogu li se PRAGMA nazivi dodati u `rlwrap` listu dopuna?

---

## Odgovor 2

Da. U `~/.config/sqlite-cli/sqlite3-completions` dodao sam svih **66 naziva** koje je `PRAGMA pragma_list;` prijavio u proveravanom SQLite CLI-ju 3.54.1. Postojeće SQL reči i CLI komande su sačuvane. Lista je statična i ne prilagođava se sama kada promeniš SQLite verziju.

Ako je `rlwrap` već pokrenut, izađi sa `.quit` i ponovo ga pokreni sa `-f` opcijom kao u [uputstvu](../../../../docs/fastapi/cheatsheets/fastapi_extensions_vscode/sqlite_terminal_litecli_rlwrap.md). Zatim probaj:

1. Ukucaj `PRAGMA table_inf`, pa pritisni **Tab**: dopunjava se `table_info`.
2. Dopuni `('albums');` i pritisni **Enter** za pregled kolona.

`PRAGMA` i njegov naziv su **dve zasebne reči**. Ako više predloga ima isti početak, unesi još slova ili ponovo pritisni Tab. Primer je proveren u privremenoj bazi; dostupnost PRAGMA naredbi može se razlikovati u drugim SQLite klijentima. Prisustvo predloga ne znači da je svaka naredba bezbedna za izvršavanje.

---

## Pitanje 3

Zašto se predlozi u `rlwrap`-u pri dvostrukom pritisku na Tab ispisuju stepenasto?

---

## Odgovor 3

U izdvojenoj proveri sa SQLite CLI-jem 3.54.1 i `rlwrap`-om 0.46.1 utvrdio sam da SQLite-ov interni editor linije, kada se koristi zajedno sa `rlwrap`-om, dovodi do toga da terminal ne vraća kursor na početak reda pri ispisu predloga. Ispis bez korekcije je imao znak za novi red bez vraćanja na početak; rezultat može izgledati kao stepenice.

Isprobana komanda iz korena repozitorijuma sada uključuje i podešavanje dopunjavanja iz odgovora 4:

```bash
INPUTRC="$HOME/.config/sqlite-cli/sqlite3-inputrc" \
  rlwrap -a -N -c -i -A -f "$HOME/.config/sqlite-cli/sqlite3-completions" \
  sqlite3 -cmdline-edit off -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

`-cmdline-edit off` isključuje interni editor SQLite CLI-ja za tu sesiju, **ne** Tab dopunjavanje u `rlwrap`-u. `-A` pomaže `rlwrap`-u da pravilno obradi obojeni prompt. U testu su prelomi redova imali i povratak na početak, predlozi su se pojavili, a `PRAGMA foreign_keys;` i dovršavanje `.databases` su radili. Otvorena korisnička sesija nije menjana.

Sa prvobitnom verzijom komande potvrdio si da su predlozi poravnati u tvom VS Code terminalu. U novoj sesiji sa dodatnim podešavanjem iz odgovora 4 prvi Tab posle `PRAGMA fore` dopunjava reč, a još dva Tab-a prikazuju predloge.

---

## Pitanje 4

Zašto Tab ne dopunjava `PRA` u `PRAGMA` i `fore` u `foreign`?

---

## Odgovor 4

U listi predloga postoje reči koje počinju isto, ali nisu zapisane istom veličinom slova: `PRAGMA` i `pragma_list`, odnosno `FOREIGN` i nazivi kao što je `foreign_keys`. Opcija `rlwrap -i` omogućava njihovo pronalaženje bez obzira na veličinu slova, ali Readline bez dodatnog podešavanja nije dopunjavao njihov zajednički početak.

Napravio sam posebni fajl `~/.config/sqlite-cli/sqlite3-inputrc`. On učitava tvoj postojeći `~/.inputrc` i uključuje `set completion-ignore-case on`. Globalni `~/.inputrc` i lista predloga nisu menjani. Ažurirana komanda iz odgovora 3 postavlja `INPUTRC` samo za tu pokrenutu komandu. Zatvori staru sesiju sa `.quit` i ponovo je pokreni tom komandom.

U izolovanoj proveri dobijeno je:

1. `PRA` + Tab → `PRAGMA`. Pošto postoji i `pragma_list`, razmak posle `PRAGMA` treba ručno uneti.
2. `PRAGMA fore` + Tab → `PRAGMA foreign`.
3. `PRAGMA foreign_k` + Tab → `PRAGMA foreign_key`.

Poslednji primer nije završena PRAGMA naredba: postoje `foreign_keys`, `foreign_key_list` i `foreign_key_check`, pa je potrebno dopuniti željeni nastavak. Ako prvi Tab proširi reč, još dva pritiska prikazuju spisak mogućnosti. SQLite ne razlikuje velika i mala slova u ovim nazivima, a dopuna zadržava veličinu koju si započeo. Poravnanje predloga i dovršavanje `.databases` takođe su provereni u izdvojenom terminalu.

---

## Pitanje 5

Kako da sam, pomoću `nano` editora, dodam `PRAGMA foreign_keys = ON;` u `rlwrap` listu dopuna?

---

## Odgovor 5

Prvo važna ispravka: u listi već postoje **odvojene reči** `PRAGMA`, `foreign_keys` i `ON`. Cela naredba nije zapisana kao jedan red, ali `rlwrap` pri učitavanju svakako deli sadržaj na reči. Zato njenim dodavanjem možeš vežbati rad u `nano`, ali **nećeš dobiti dopunjavanje cele naredbe jednim pritiskom na Tab**. To sam proverio na privremenoj kopiji liste, ne na tvom fajlu.

### 1. Izađi iz SQLite CLI-ja

Ako u terminalu vidiš SQLite prompt, unesi:

```text
.quit
```

Pritisni **Enter**. Sada si ponovo u Bash terminalu. Ako već vidiš Bash prompt, ovaj korak preskoči.

### 2. Otvori listu u `nano`

U Bash-u unesi:

```bash
nano "$HOME/.config/sqlite-cli/sqlite3-completions"
```

Pritisni **Enter**. Otvoriće se tekstualni editor sa postojećom listom. Ne briši postojeće redove. Ako se fajl neočekivano otvori prazan, izađi sa **Ctrl+X** bez čuvanja i proveri putanju.

Na dnu `nano` ekrana videćeš prečice. Znak `^` znači **Ctrl**: na primer, `^O` znači istovremeno drži **Ctrl** i pritisni slovo **O**, ne cifru nula. Znak `M` označava **Alt**.

### 3. Dodaj red

1. Pritisni **Alt+/** za prelazak na kraj fajla. Ako to ne radi, pritisni **Esc**, pusti ga, pa pritisni **/**.
2. Ako je kursor na praznom poslednjem redu, ukucaj sledeći tekst. Ako je na kraju reda u kojem već ima teksta, pritisni **End**, pa **Enter**, da prvo napraviš novi red.

   ```text
   PRAGMA foreign_keys = ON;
   ```

3. Proveri da je naredba na svom redu i da prethodne reči nisu obrisane. Ne unosi navodnike ni oznake koda.

### 4. Sačuvaj i zatvori

1. Pritisni **Ctrl+O** — nano će ponuditi ime fajla za čuvanje.
2. Nemoj menjati ponuđeno ime; pritisni **Enter** da potvrdiš.
3. Pritisni **Ctrl+X** da zatvoriš nano i vratiš se u Bash.

Ako pre čuvanja odlučiš da odustaneš, pritisni **Ctrl+X**, pa na pitanje o čuvanju izaberi **N**. To ne poništava izmene koje su već sačuvane.

### 5. Proveri upis i isprobaj dopunjavanje

U Bash-u proveri da je red prisutan:

```bash
grep -n -F 'PRAGMA foreign_keys = ON;' "$HOME/.config/sqlite-cli/sqlite3-completions"
```

Broj ispred reda je broj linije u fajlu. Zatim ponovo pokreni `rlwrap` komandom iz **odgovora 3**, jer već pokrenuti `rlwrap` ne učitava automatski izmenjeni fajl.

U SQLite CLI-ju ukucaj `PRAGMA foreign_k` i pritisni **Tab**: dobićeš zajednički početak `PRAGMA foreign_key`. Ručno dodaj `s = ON;`, tako da cela linija bude:

```sql
PRAGMA foreign_keys = ON;
```

Pritisni **Enter**. Ova naredba obično ne ispisuje rezultat. Zatim proveri:

```sql
PRAGMA foreign_keys;
```

Rezultat `1` znači da je provera stranih ključeva uključena za **ovu konekciju**; `0` znači da nije. Uključivanje nije moguće usred aktivne transakcije. Ovo podešavanje ne uključuje automatski proveru u drugim konekcijama ili u FastAPI aplikaciji, i samo po sebi ne proverava stare podatke.

**Podsetnik:** dodavanje teksta u fajl samo menja listu predloga; ne izvršava SQL. SQL se izvršava tek kada ga uneseš u SQLite CLI i pritisneš **Enter**.

---
