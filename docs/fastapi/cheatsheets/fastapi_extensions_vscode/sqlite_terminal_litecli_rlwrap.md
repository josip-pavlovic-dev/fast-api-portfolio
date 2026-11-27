# SQLite u terminalu: `litecli` i `rlwrap`

Ovo uputstvo prati tvoj [plan učenja](../../../../fast-api-course-my-work/sqlite_for_beginners/plan_ucenja/README.md) i vežbe u [playground-u](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/README.md). Namenjeno je integrisanom terminalu VS Code-a u WSL-u, ali iste komande možeš koristiti i u običnom WSL terminalu.

---

## 1. Šta je instalirano i koji alat kada koristiš

| Alat                     | Šta je                                                                                                                    | Kada ga koristiš                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `sqlite3`                | Zvanični SQLite komandni alat; na ovom računaru instaliran u `~/.local/bin`.                                              | Kada pratiš lekcije o SQLite CLI-ju, njegovim komandama sa tačkom, `.read`, `.dump` i prilikom izvoza baze. |
| `rlwrap`                 | Omotač koji pokreće postojeći `sqlite3` i dodaje uređivanje ulaza, istoriju i dovršavanje iz zadate liste.                | Kada želiš da radiš u istom `sqlite3`, ali sa dopunjavanjem odabranih komandi pomoću Tab-a.                 |
| `litecli`                | Zaseban terminalski SQLite klijent sa SQL predlozima i isticanjem sintakse. Instaliran je u projektnom `.venv` okruženju. | Kada pišeš i istražuješ SQL upite i želiš predloge naziva tabela, kolona i SQL reči.                        |
| SQLTools i SQLite Viewer | VS Code ekstenzije, nisu terminalski alati.                                                                               | SQLTools za upite iz editora, Viewer za vizuelni pregled baze.                                              |

`litecli` i `rlwrap` **nisu VS Code ekstenzije** i ne zamenjuju `sqlite3`. SQL jezik je zajednički, ali komande koje počinju tačkom pripadaju konkretnom klijentu: nemoj pretpostaviti da `litecli` podržava svaku `sqlite3` komandu. Na primer, `.databases` radi u instaliranom `litecli`-ju, ali `.help` u proveri nije bio implementiran. Za lekcije o CLI komandama koristi `sqlite3`, sa ili bez `rlwrap`-a.

Radna baza ostaje isti fajl bez obzira na alat. Svaki alat, međutim, otvara **sopstvenu konekciju**: njena podešavanja i `ATTACH` baze nisu automatski preneti u drugi alat ili SQLTools.

---

## 2. Priprema terminala

U VS Code-u otvori terminal povezan sa WSL-om. Primeri u nastavku podrazumevaju Bash i **koren ovog repozitorijuma** kao trenutni direktorijum:

```bash
cd ~/code/python-automation-lab/fast-api-portfolio
pwd
source .venv/bin/activate
```

`source` aktivira projektno Python okruženje u **tom terminalu**. `litecli` je dostupan dok je `.venv` aktiviran; nakon otvaranja novog terminala ponovo ga aktiviraj. Alternativno, iz korena projekta možeš pokrenuti `.venv/bin/litecli` bez aktivacije. `rlwrap` je instaliran u WSL sistemu i ne zavisi od aktivnog `.venv`-a.

Ako jednog dana ponovo napraviš `.venv`, može biti potrebno da u njemu ponovo instaliraš `litecli`:

```bash
source .venv/bin/activate
python -m pip install litecli
```

Proveri instalacije:

```bash
command -v sqlite3
sqlite3 --version
command -v litecli
litecli --version
command -v rlwrap
rlwrap --version
```

Prilikom podešavanja proverene su verzije `sqlite3` 3.54.1, `litecli` 1.17.1 i `rlwrap` 0.46.1. Verzije se kasnije mogu promeniti.

**Važno:** `SELECT sqlite_version();` prikazuje verziju SQLite biblioteke koju koristi klijent koji izvršava upit; to nije uvek Pythonova biblioteka. Pri proveri, projektni Python i `litecli` koristili su 3.45.1, a zasebni `sqlite3` CLI 3.54.1. Instalirani Node `sqlite3` paket koji koristi SQLTools drajver prijavio je 3.44.2 u zasebnoj proveri; proveri i u aktivnoj SQLTools konekciji istim SQL upitom. Različite verzije ne znače da je instalacija neuspešna, ali novije SQL funkcije možda neće raditi jednako u svim alatima.

---

## 3. Terminalski prompt i SQLite prompt

- Komande označene kao **Bash** unosiš u terminal pre ulaska u alat ili nakon izlaska iz njega.
- Komande označene kao **SQLite CLI** unosiš dok je `sqlite3` pokrenut, sa ili bez `rlwrap`-a.

- SQL unosiš u otvorenom klijentu, ne u Bash promptu. SQL naredbe završavaj sa `;`. SQLite CLI komande poput `.tables` počinju tačkom i ne završavaju se tačka-zarezom.

- Primeri sa relativnim putanjama polaze od korena repozitorijuma. Ako promeniš direktorijum, promeni i putanju.

---

## 4. `rlwrap`: Tab dovršavanje u pravom SQLite CLI-ju

Za ovaj računar je napravljena lista CLI komandi, čestih SQL reči i PRAGMA naziva u `~/.config/sqlite-cli/sqlite3-completions`. Ona sadrži, između ostalog, `.databases`, `.tables`, `SELECT`, `PRAGMA`, `table_info` i `foreign_key_list`.

Lista (`~/.config/sqlite-cli/sqlite3-completions`) je običan tekstualni fajl: Po potrebi dodaj novu reč u zaseban red. Posle izmene izađi iz SQLite CLI-ja sa `.quit` i ponovo pokreni `rlwrap`.

---

### Pristup i izmena liste dopuna u `rlwrap`-u

Pristup listi iz bash-a je moguć preko promenljive `$HOME`, koja predstavlja korisnički direktorijum.

```bash
echo "$HOME/.config/sqlite-cli/sqlite3-completions"
```

Izmena liste reči u fajlu `sqlite3-completions` možeš izvršiti pomoću bilo kog tekstualnog editora. Na primer, koristi `nano` ili `vim`:

```bash
nano "$HOME/.config/sqlite-cli/sqlite3-completions"
```

Dodaj nove reči u zaseban red, sačuvaj fajl i izađi iz editora. Nakon toga, ponovo pokreni `rlwrap` da bi izmene bile primenjene.

> **Važno:** Dodavanje celog reda, na primer `PRAGMA foreign_keys = ON;`, neće omogućiti dovršavanje cele naredbe jednim pritiskom na Tab. `rlwrap` sadržaj liste učitava kao pojedinačne reči, a ne kao gotove naredbe. Detaljno objašnjenje i uputstvo za rad u `nano` nalaze se u [odgovoru 5 u dan_03_intro.md](../../../../fast-api-course-my-work/sqlite_for_beginners/pitanja_i_odgovori/dan_03_intro/dan_03_intro.md#odgovor-5).

---

### Pokretanje SQLite CLI-ja sa `rlwrap`-om i prilagođenim dopunama

Za pregled radne kopije bez upisa pokreni u Bash-u:

```bash
INPUTRC="$HOME/.config/sqlite-cli/sqlite3-inputrc" \
  rlwrap -a -N -c -i -A -f "$HOME/.config/sqlite-cli/sqlite3-completions" \
  sqlite3 -cmdline-edit off -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Ovo je i dalje zvanični `sqlite3`. `-readonly` je opcija za `sqlite3`, a prethodne opcije pripadaju `rlwrap`-u:

- `-a` omogućava `rlwrap`-ovo uređivanje ulaza i kada pokrenuti program sam uređuje linije.
- `-N` pomaže da `rlwrap` ne ometa programe poput pozvanog editora ili pagera.
- `-c` uključuje dovršavanje putanja i omogućava da tačka bude deo reči za dovršavanje, što je korisno kada se radi sa fajlovima koji imaju ekstenzije ili kada se koristi SQLite-ova sintaksa koja uključuje tačku.

- `-i` omogućava dovršavanje bez razlikovanja velikih i malih slova; mora da stoji pre `-f`. Ne preoblikuje nužno već uneta slova.

- `-A` je opcija za `rlwrap`: pomaže mu da pravilno računa širinu obojenog prompta koji sadrži ANSI sekvence.
- `-f` učitava našu listu reči; to **nije** automatski spisak svih SQLite komandi ili naziva tabela.

- `-cmdline-edit off` je opcija za **SQLite CLI 3.54.1**, ne za `rlwrap`: isključuje SQLite-ov interni editor linije, dok uređivanje i Tab dovršavanje preuzima `rlwrap`. U izolovanom terminalskom testu to sprečava stepenasto ispisivanje liste predloga. Proveri `sqlite3 --help` ako koristiš drugu verziju, jer možda nema ovu opciju.

- `INPUTRC` bira posebna Readline podešavanja samo za ovu komandu. Fajl `sqlite3-inputrc` uključuje postojeći `~/.inputrc` i dodaje `completion-ignore-case on`, kako bi zajednički početak predloga mogao da se dopuni i kada su predlozi različite veličine slova. Ne menja globalni `~/.inputrc`.

- `"$HOME/` predstavlja putanju do korisničkog direktorijuma u kojem se nalazi konfiguracioni fajl sa listom komandi za `rlwrap`. Zamena `$HOME` sa stvarnom putanjom do korisničkog direktorijuma se vrši automatski od strane Bash-a ili drugog kompatibilnog shell-a. Ovo omogućava da konfiguracioni fajl bude prenosiv i da se koristi bez obzira na konkretan korisnički direktorijum.

Isprobaj u otvorenom SQLite CLI-ju:

1. Ukucaj `.databa`, pritisni **Tab**, pa proveri da je dopunjeno u `.databases`.
2. Pritisni **Enter**. Izlaz treba da prikaže `main` i putanju do `chinook_practice.db`.
3. Ukucaj `.tab`, pritisni **Tab**, pa **Enter** da prikažeš tabele.

4. Za SQL, ukucaj `SEL` i pritisni **Tab** da dobiješ `SELECT`. Probaj i `SELECT * FRO` pa **Tab** za `FROM`; izbriši taj nezavršeni upit pre sledećeg koraka.

5. Ukucaj `PRAGMA table_inf`, pa **Tab** za `table_info`. Dodaj `('albums');` i pritisni **Enter**.
6. Pokreni `.schema albums`, a zatim `.quit`.

Tačan naziv je **`.databases`**, sa završnim `s`. `rlwrap` dovršava pojedinačne reči: `INSERT` i `INTO`, kao i `PRAGMA` i `table_info`, unose se odvojeno. Lista uključuje PRAGMA nazive prijavljene u SQLite CLI verziji proveravanoj pri ažuriranju.

Dostupnost prethodno navedenih PRAGMA komandi u drugim klijentima može biti drugačija. Neke PRAGMA komande menjaju bazu ili podešavanja. Zbog toga, predlog koji `rlwrap` daje nije potvrda da je naredba bezbedna. Ako postoji više mogućih dopuna, pritisni Tab ponovo da ih vidiš i dopuni još slova. `rlwrap` koristi i istoriju. Uz pomoć `strelica gore/dole` možemo prolaziti kroz prethodne unose.

Na primer, `PRA` + Tab daje `PRAGMA`, a `PRAGMA fore` + Tab daje `PRAGMA foreign`. Kako postoji više mogućih nastavaka, nije automatski izabrana jedna naredba niti je dodat razmak posle `PRAGMA`: unesi ga ručno, a dodatnim pritiscima na Tab prikaži moguće nastavke. Kada prvi Tab proširi reč, u ovom podešavanju mogu biti potrebna još dva pritiska za prikaz liste.

> **Ispravka ranijeg Odgovora 3:** tvrdnja da standardni SQLite CLI nikada ne podržava Tab dovršavanje bila je previše uopštena: mogućnosti zavise od konkretne gradnje i terminalskog uređivanja linija. Takođe, sama komanda `rlwrap sqlite3 sandbox.db` ne garantuje dopunu `.databases`. Gore navedena komanda sa listom je proverena. Bez Tab-a, `sqlite3` prihvata i dovoljno jednoznačno skraćenu komandu `.databa` uz **Enter**; to nije dopunjavanje.

---

### Kako isključiti `rlwrap`

Izađi iz SQLite CLI-ja pomoću `.quit`, pa sledeći put pokreni `sqlite3` direktno:

```bash
sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Time ne deinstaliraš `rlwrap`; samo ga ne koristiš u toj sesiji. Nije dodat alias niti je promenjen podrazumevani `sqlite3`. Direktni `sqlite3` može imati sopstveno uređivanje i sopstveno dovršavanje, u zavisnosti od gradnje.

**Privatnost istorije:** `rlwrap` i sami klijenti mogu čuvati unesene komande u istoriji. Opcija `-a` može izložiti ili sačuvati i osetljiv unos, uključujući lozinke. Ne unosi lozinke ili tajne u komande i ne pretpostavljaj da je istorija privatna.

---

## 5. `litecli`: SQL predlozi

Prvi način pokretanja `litecli` je `.venv/bin/litecli`, što osigurava da se koristi verzija instalirana u projektnom virtuelnom okruženju. Ovo je posebno važno kada želiš da budeš siguran da koristiš tačno onu verziju `litecli` koja je kompatibilna sa projektom i njegovim zavisnostima, bez oslanjanja na globalno instalirane verzije koje mogu biti različite. Primer:

```bash
.venv/bin/litecli fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Drugi način je pokretanje `litecli` direktno iz aktiviranog `.venv` koristeći samo komandu `litecli`. Ovaj pristup je praktičan kada već radiš u aktiviranom virtuelnom okruženju i želiš da izbegneš navođenje pune putanje do izvršnog fajla. Važno je napomenuti da oba načina pokreću isti klijent (`litecli`), ali prvi način eksplicitno koristi izvršni fajl iz projektnog `.venv`, dok drugi zavisi od aktivnog okruženja. Primer je dat u nastavku.

Prilikom pokretanja iz korena repozitorijuma, uz aktiviran `.venv`, pokreni:

```bash
litecli fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Pokrenut je **poseban klijent `litecli`**, koji otvara **sopstvenu konekciju sa bazom**, nezavisnu od SQLTools konekcije. U ovoj instalaciji `litecli` **koristi Pythonov modul `sqlite3` unutar svog procesa**. To znači da ne pokreće zaseban `sqlite3` CLI proces.

U SQLTools-u pišeš upite u editoru, a ekstenzija ih izvršava preko svog drajvera i konekcije. Oba klijenta (`litecli` i `SQLTools` ili bilo koji drugi klijent) mogu pristupati istom fajlu baze preko odvojenih konekcija. Primer:

U prvom terminalu pokrećeš `litecli` koristeći putanju do izvršnog fajla u `.venv`:

```bash
.venv/bin/litecli fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Zatim možeš izvršavati SQL upite i PRAGMA komande unutar `litecli` prompta. Na primer:

```sql
-- Primer SQL upita koji se može izvršiti u `litecli` nakon otvaranja baze
SELECT Name FROM artists LIMIT 1;

-- Primer PRAGMA upita koji se može izvršiti u `litecli`
PRAGMA foreign_keys;
```

U drugom terminalu koristimo drugu konekciju preko SQLTools ekstenzije u VS Code-u ili bilo kog drugog klijenta koji pristupa istoj SQLite bazi npr. `sqlite3` CLI:

```bash
# Otvori SQLTools konekciju ili drugi klijent u drugom terminalu
# Na primer, za `sqlite3` CLI:
sqlite3 fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

```sql
-- Primer SQL upita koji se može izvršiti u `sqlite3` CLI nakon otvaranja baze
SELECT Name FROM artists LIMIT 1;

-- Primer PRAGMA upita koji se može izvršiti u `sqlite3` CLI
PRAGMA foreign_keys;
```

Ove konekcije omogućavaju istovremeni rad sa istom SQLite bazom iz različitih klijenata, ali svaka konekcija ima svoje postavke i stanje. U slučaju konflikta, poslednja izvršena promena u jednoj konekciji može uticati na druge konekcije, ali promene se ne sinhronizuju automatski.

`litecli` u ovom primeru otvara bazu za **čitanje i pisanje** (read-write): za bezbedan pregled koristi samo `SELECT` i `PRAGMA` upite prikazane ispod.

`PRAGMA` znači podešavanje ili proveru SQLite konfiguracije. Ove komande omogućavaju pregled i modifikaciju različitih aspekata ponašanja baze, kao što su spoljni ključevi, keširanje, journal mode i drugi parametri specifični za SQLite.

**Napomena:** Pažljivo proveri putanju: pogrešna putanja može dovesti do otvaranja ili stvaranja pogrešne, prazne baze.

U `litecli` promptu:

1. Počni da kucaš `SELECT Name FROM art`. Trebalo bi da se pojavi predlog `artists`.
2. Pritisni **Tab** da prihvatiš predlog, pa dopiši ostatak i pritisni **Enter**:

   ```sql
   SELECT Name FROM artists LIMIT 1;
   ```

3. Probaj i pregled verzije i podešavanja trenutne konekcije:

   ```sql
   SELECT sqlite_version();
   PRAGMA foreign_keys;
   ```

`PRAGMA foreign_keys` može imati različitu vrednost u različitim konekcijama; rezultat iz `litecli`-ja ne dokazuje podešavanje SQLTools-a ili aplikacije. Predlozi pomažu pri kucanju, ali i dalje proveravaj upit i njegove rezultate.

Za izlazak upiši `exit` i pritisni Enter ili pritisni **Ctrl+D** na praznom promptu. Izlaskom se zatvara samo ta terminalska konekcija; fajl baze i sačuvana SQLTools konekcija ne brišu se.

---

### Kako isključiti i ponovo uključiti predloge

`litecli` koristi korisnički konfiguracioni fajl `~/.config/litecli/config`, kreiran pri prvom pokretanju. Otvori ga u editoru, pronađi odeljak `[main]` i promeni postojeću postavku:

```ini
autocompletion = False
```

Sačuvaj fajl i ponovo pokreni `litecli`. Automatski prikaz predloga pri kucanju je isključen, **ali Tab i dalje može ručno pokrenuti dovršavanje**. Vrati `autocompletion = True` i ponovo pokreni klijent kada želiš automatske predloge. Ovo podešavanje ne menja `sqlite3` ni `rlwrap`.

Za rad bez `litecli` predloga uopšte, jednostavno koristi običan `sqlite3`; ako želiš `rlwrap`, a ne želiš njegove predloge, pokreni `sqlite3` direktno bez omotača.

---

## 6. Primena na prve lekcije

### Lekcija 01 — šta je SQLite

Pročitaj [01_what_is_sqlite.md](../../../../fast-api-course-my-work/sqlite_for_beginners/00_intro/01_what_is_sqlite.md), a rešenja sačuvaj u [01_what_is_sqlite.sql](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/01_what_is_sqlite.sql).

1. U Bash-u pokreni `sqlite3 -readonly` nad radnom kopijom baze ili prethodnu `rlwrap` komandu.

```bash
INPUTRC="$HOME/.config/sqlite-cli/sqlite3-inputrc" \
  rlwrap -a -N -c -i -A -f "$HOME/.config/sqlite-cli/sqlite3-completions" \
  sqlite3 -cmdline-edit off -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

2. U SQLite CLI-ju isprobaj `.databases`, `.tables` i `.schema albums`.

```sql
.databases
.tables
.schema albums
```

3. Pokreni SQL upite `SELECT sqlite_version();` i `PRAGMA foreign_keys;`.

```sql
SELECT sqlite_version();
PRAGMA foreign_keys;
```

4. Po želji pokreni istu proveru u `litecli`-ju i SQLTools-u, pa uporedi rezultate **svake konekcije**.

- Rezultati konekcije su takvi da se razlikuju u zavisnosti od toga da li je automatsko predlaganje uključeno (npr. u `rlwrap` komandom `-a` ili u `litecli`-ju komandom `--autocomplete`) i koji klijent se koristi (SQLite CLI, `rlwrap` ili `litecli`).

- U `litecli`-ju može doći do razlike u redosledu izvršavanja upita u odnosu na običan `sqlite3` ili `rlwrap`, što može uticati na prikaz rezultata i ponašanje stranih ključeva. Zbog toga je važno uvek proveriti stanje stranih ključeva (npr. `PRAGMA foreign_keys;`) i redosled izvršavanja upita (npr. `SELECT`, `INSERT`, `UPDATE`, `DELETE`) pre nego što se oslanjaš na rezultate iz različitih klijenata.

5. Zapiši svoje zaključke u predviđeni SQL fajlu kao komentare. `.sql` fajl je tekst sa upitima, dok `.db` čuva bazu.

Za izvršavanje celog sačuvanog fajla iz SQLite CLI-ja, posle pokretanju sqlite3 iz korena repozitorijuma koristi u sqlite3 interaktivnom okruženju komandu `.read` sa putanjom do SQL fajla:

```bash
.read fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/01_what_is_sqlite.sql
```

`.read` izvršava **čitav** sadržaj, ne samo izabrani blok. Prvo proveri sadržaj: ako fajl kasnije sadrži `INSERT`, `UPDATE`, `DELETE` ili druge izmene, i one se mogu izvršiti nad otvorenom bazom. Opcija `-readonly` pomaže da se izbegnu upisi u otvorenu bazu, ali nije zamena za pregled skripte.

SQLTools oznake `-- @block` su SQL komentari i SQLite CLI ih ignoriše. U SQLTools-u je ranije došlo do `SQLITE_MISUSE` zbog obrade komentara posle poslednjeg upita; razdvajanje fajla na `@block` blokove i izvršavanje željenog bloka rešilo je prijavljeni problem. To nije komanda za SQLite CLI.

---

### Lekcija 02 — otvaranje i `ATTACH`

Pročitaj [02_attaching_sample_database_to_sqlite.md](../../../../fast-api-course-my-work/sqlite_for_beginners/00_intro/02_attaching_sample_database_to_sqlite.md) i koristi istoimeni fajl u [playground/sql/00_intro](../../../../fast-api-course-my-work/sqlite_for_beginners/playground/sql/00_intro/) za beleške i SQL.

**Otvaranje kao glavne baze:** komanda iz odeljka 4 otvara `chinook_practice.db` kao `main`. `.databases` proverava koju si bazu stvarno otvorio.

**Priključivanje dodatne baze:** zatvori prethodnu sesiju sa `.quit`, pa u Bash-u iz korena repozitorijuma proveri da radna kopija postoji i pokreni privremenu glavnu bazu:

```bash
test -f fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db && echo "Baza postoji" || echo "Baza ne postoji: proveri putanju"
```

Ako vidiš `Baza ne postoji`, ne nastavljaj dok ne proveriš putanju. U suprotnom pokreni:

```bash
sqlite3 :memory:
```

Umesto toga možeš pokrenuti i:

```bash
INPUTRC="$HOME/.config/sqlite-cli/sqlite3-inputrc" \
  rlwrap -a -N -c -i -A -f "$HOME/.config/sqlite-cli/sqlite3-completions" sqlite3 -cmdline-edit off :memory:
```

U SQLite CLI-ju izvrši:

```sql
ATTACH DATABASE 'fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db' AS chinook;
```

```text
.databases
```

```sql
SELECT Name FROM chinook.artists ORDER BY Name LIMIT 5;
DETACH DATABASE chinook;
```

Na kraju proveri `.databases` i izađi sa `.quit`. `main` je ovde privremena baza u memoriji, a `chinook` je alias dodatne baze. `DETACH` ne briše fajl; zatvaranje konekcije takođe uklanja privremeni `ATTACH`. Relativna putanja u `ATTACH`-u računa se od direktorijuma procesa, ne od lokacije `.sql` fajla. Sama `ATTACH` naredba ne menja redove, ali naknadni upisi mogu promeniti priključenu radnu kopiju.

---

### Lekcije 03 i 04 — konekcije i pojmovi

Koristi `sqlite3` ili `rlwrap` za proveru `.databases`, `.tables` i `.schema tracks`. U `litecli`-ju ili SQLTools-u istraži tabele pomoću SQL upita. Uporedi konekciju koja je trenutno otvorena sa sačuvanom SQLTools konfiguracijom: to nisu isti objekti. Rešenja čuvaj u odgovarajućim `.sql` fajlovima u `playground/sql/00_intro/`.

---

## 7. Kasniji dani plana

| Deo plana                                   | Preporuka                                                                                                                                                                                                    |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Dani 3–4: SQLite CLI                        | Koristi `sqlite3` ili `rlwrap … sqlite3` za `.help`, `.tables`, `.schema`, `.mode`, `.headers`, `.read`, `.once` i `.output`. Beleške o CLI komandama čuvaj u `playground/cli/`.                             |
| Dan 5: dump i obnavljanje                   | Koristi zvanični `sqlite3` sa ili bez `rlwrap`-a. Izvozi u novi fajl u `playground/` i obnavljaj u novu bazu, ne u original ili postojeću radnu kopiju. Proveri putanju pre izvoza: cilj može biti prepisan. |
| Dani 6–12: SELECT, WHERE, ORDER BY i ostalo | Piši trajna rešenja u odgovarajuće `.sql` fajlove; probaj predloge u `litecli`-ju i izvršavanje iz SQLTools-a ili SQLite CLI-ja.                                                                             |

Primer za dan 4, u SQLite CLI-ju otvorenom nad radnom kopijom:

```text
.headers on
.mode column
.schema albums
```

Za izvoz i `.dump` prati konkretnu lekciju i koristi posebna nova imena fajlova. Komande `.once` i `.output` utiču na izlaz CLI-ja, a nisu SQL koji treba slati kroz SQLTools.

---

## 8. Najčešći problemi

- **`litecli: command not found`:** iz korena projekta aktiviraj `source .venv/bin/activate`, pa proveri `command -v litecli`. Instalacija je u ovom `.venv`-u, ne u svakom terminalu ili Python okruženju.

- **Tab ne dovršava `.databases` u `rlwrap`-u:** proveri da si pokrenuo komandu iz odeljka 4 i da fajl liste postoji: `ls -l ~/.config/sqlite-cli/sqlite3-completions`. Proveri da sadrži `.databases`, izađi i ponovo pokreni komandu. Sam `rlwrap sqlite3 ...` nije dovoljan da garantuje ovaj rezultat.

- **Predlozi se ispisuju stepenasto:** u SQLite CLI 3.54.1 probaj komandu iz odeljka 4, sa `-cmdline-edit off` iza `sqlite3` i `-A` među opcijama `rlwrap`-a. Kombinacija je proverena u izdvojenom testu i korisnik je potvrdio poravnanje u svom VS Code terminalu. Ako problem ostane, zabeleži šta se dogodilo umesto da menjaš globalna terminalska podešavanja.

- **Prazna baza ili nema tabela:** proveri `pwd` u Bash-u i `.databases` u SQLite CLI-ju. Pogrešna putanja može napraviti novu praznu bazu; za pregled koristi `-readonly`. Nemoj automatski brisati niti prepisivati fajlove.

- **`attempt to write a readonly database`:** pokrenuo si CLI sa `-readonly`; to je očekivano za upis. Za vežbe koje namerno menjaju podatke, nakon provere putanje otvori odgovarajuću radnu ili sandbox bazu bez `-readonly`.

- **`database is locked`:** možda druga konekcija drži otvorenu transakciju. Završi je ili prekini nepotrebnu konekciju, pa pokušaj ponovo; ne briši prateće SQLite fajlove.

- **Predlog ne znači da je upit izvršen:** Tab samo pomaže pri unosu. Proveri ceo SQL i zatim pritisni Enter.

- **Izlazak iz SQLite-ja nije izlazak iz `.venv`-a:** `.quit` ili `exit` zatvara klijent. `deactivate` u Bash-u dodatno isključuje projektno Python okruženje za taj terminal. Ni jedno ne briše bazu ni SQLTools konfiguraciju.

SQLTools konekciju po potrebi prekini kroz `SQLTools: Disconnect`; ponovno pokretanje `sqlite3` ili `litecli` ne uključuje automatski tu konekciju. Za više detalja o radu u editoru pogledaj [uputstvo za VS Code ekstenzije](./sqlite3_extensions_vscode.md).

---
