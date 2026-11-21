# Pitanja i odgovori — Dan 02: Uvod u SQLite

## Pitanje 1

Zašto se pored naziva terminala `python - fast-api-portfolio` pojavljuje znak uzvika? Da li svaki put treba da ugasim terminal i otvorim novi?

---

## Odgovor 1

Na tvojoj slici postoje **dva različita znaka**:

1. Narandžasti trougao sa uzvičnikom pored imena terminala je **VS Code indikator statusa terminala**.
2. `!2` u tekstu prompta, pored imena Git grane, dolazi iz podešavanja **Starship Git prompta**, ne iz VS Code upozorenja.

### Trougao pored naziva terminala

VS Code prikazuje indikatore kada se status terminala promeni. Sama slika nije pokazivala tekst upozorenja; naknadno si ga poslao i konkretan uzrok je objašnjen u **Odgovoru 3**.

Postavi pokazivač miša **preko trougla** i sačekaj poruku. Jedan mogući razlog je da ekstenzija želi da promeni promenljive okruženja i predlaže ponovno pokretanje terminala, ali to je samo mogućnost dok ne pročitamo poruku.

- Ako poruka traži **Relaunch Terminal**, ponovno pokretanje može biti korisno da se primene navedene promene. Pročitaj poruku pre izbora.
- Ako sve što ti je trenutno potrebno radi, **ne moraš automatski gasiti terminal samo zato što vidiš uzvičnik**.
- Pre zatvaranja sačuvaj rad i završi ili bezbedno prekini aktivne procese. Zatvaranje terminala prekida njegovu sesiju, uključujući otvoreni `litecli`; može prekinuti i druge programe koji u njemu rade.
- Ako ponovo otvoriš terminal i trougao nestane, to samo po sebi ne dokazuje šta je bio uzrok. Pošalji tekst poruke ili sliku sa otvorenim opisom ako želiš da utvrdimo baš taj slučaj.

Više o indikatorima: [VS Code Terminal Basics](https://code.visualstudio.com/docs/terminal/basics#_managing-terminals).

---

### `!2` pored Git grane

U tvojoj Starship konfiguraciji `!` je oznaka za **izmenjene praćene Git fajlove**, a broj pokazuje koliko ih je. Na primer, `!2` znači da je prompt tada prijavio dva izmenjena praćena fajla. To nije SQLite greška i nema veze sa narandžastim trouglom.

Proveri tačno stanje iz **Bash** prompta:

```bash
git status --short
```

Komanda prikazuje i druge vrste promena, na primer nove nepraćene fajlove; `!2` se ne mora odnositi na ukupan broj svih prikazanih stavki. Dok si unutar `litecli`, prvo izađi sa `exit` da bi se vratio u Bash.

---

## Pitanje 2

Ako iz korena projekta pokrenem `.venv/bin/litecli` i dobijem `(none)>`, da li je klijent pokrenut bez baze? Mogu li naknadno da otvorim bazu bez izlaska?

---

## Odgovor 2

Da. U tvojoj instalaciji `litecli` 1.17.1, pokretanje bez argumenta za bazu otvara klijent **bez aktivne konekcije ka bazi**. Prompt `(none)>` ukazuje da nije izabrana baza. To nije isto što i automatski otvorena `:memory:` baza.

Proverio sam: kada se u tom stanju pokuša `SELECT 1;`, `litecli` prijavi `Not connected to database.`. Prompt je prilagodljiv, ali u tvojoj prikazanoj konfiguraciji `(none)` označava da nije zadata baza.

**Ne moraš da izađeš.** U postojećem `(none)>` promptu ukucaj:

```text
.open fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Pritisni Enter. Ovo je `litecli` komanda, ne SQL: nema tačka-zareza. Očekuje se poruka da je klijent povezan sa bazom, a prompt se menja u skladu sa konfiguracijom.

Zatim u istom `litecli`-ju proveri otvoreni fajl:

```sql
PRAGMA database_list;
```

U redu `main` potraži putanju koja se završava sa `playground/databases/chinook_practice.db`. Probaj i upit:

```sql
SELECT ArtistId, Name
FROM artists
ORDER BY ArtistId
LIMIT 5;
```

Primer je proveren: `.open` otvara postojeću radnu kopiju i SQL upit vraća podatke, bez ponovnog pokretanja `litecli`-ja.

---

### Važne napomene o putanji i bezbednosti

- Relativna putanja u `.open` primeru računa se od direktorijuma iz kojeg je pokrenut `litecli` — ovde od korena repozitorijuma, ne od lokacije otvorenog `.sql` ili `.md` fajla.

- Proveri putanju pre otvaranja. Ako direktorijum postoji, a ime `.db` fajla je pogrešno, SQLite može napraviti novu praznu bazu. Komanda u primeru otvara bazu **za čitanje i pisanje**, pa se drži upita za čitanje dok ne želiš namerno da menjaš radnu kopiju.

- Ako želiš da proveriš da fajl postoji pre pokretanja, u Bash-u iz korena projekta koristi `test -f fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db && echo "Baza postoji" || echo "Proveri putanju"`.

- Za privremenu bazu možeš u `litecli`-ju upotrebiti `.open :memory:`. To je zasebna baza u memoriji: ne sadrži Chinook podatke i nestaje po zatvaranju te konekcije.

- Kada je baza već otvorena, `.open` otvara drugu kao glavnu i zatvara prethodnu konekciju; nije isto što i SQL `ATTACH`, koji dodaje bazu postojećoj konekciji. Pre promene baze završi transakciju koju želiš da sačuvaš ili poništiš.

- Za izlazak iz `litecli`-ja upiši `exit` i pritisni Enter. To zatvara njegovu konekciju, ali ne briše fajl baze niti prekida zasebnu SQLTools konekciju.

Pokretanje `.venv/bin/litecli` direktno koristi izvršni fajl iz projektnog `.venv`, ali samo po sebi **ne aktivira `.venv` za ostale komande tog terminala**. Oznaka `py:v3.12.3` u promptu prikazuje verziju Pythona. Sama po sebi ne dokazuje da je `.venv` aktiviran.

---

## Pitanje 3

U opisu upozorenja piše da ekstenzija **Python Debugger** želi da ponovo pokrene terminal kako bi doprinela njegovom okruženju. Šta to znači?

---

## Odgovor 3

Sada znamo konkretan razlog upozorenja (trougao sa uskličnikom u VS Code-u): **Python Debugger traži ponovno pokretanje terminala da bi se primenile njegove promene okruženja**. Opis navodi podršku za debagovanje bez posebne konfiguracije i komandu `debugpy <script.py>`. To nije SQLite greška niti poruka da je `litecli` neispravan.

Ekstenzija je navedena i među onima koje su već doprinele okruženju terminala, ali istovremeno prijavljuje da želi ponovno pokretanje. Sam opis ne govori tačno koja se promenljiva promenila ni zašto. To nije potrebno da znamo unapred i ne moramo da nagađamo.

- Ako sada radiš SQLite vežbe i `litecli` funkcioniše, možeš **nastaviti u postojećem terminalu**. Ne moraš ga odmah gasiti.

- Kada budeš želeo promene za Python debugger u tom terminalu, završi rad, izađi iz `litecli` komandom `exit`, pa izaberi **Relaunch Terminal** ako ti VS Code tu opciju ponudi. Ponovno pokretanje prekida aktivne procese u tom terminalu.

- Novi terminal takođe može dobiti ažurirano okruženje. Nije potrebno ponovo pokretati terminal svaki put kada vidiš ikonicu: prvo pročitaj opis upozorenja.

`Shell integration: Rich` označava da je integracija terminala sa shell-om aktivna. Nazivi ekstenzija u odeljku „contributed“ opisuju njihove doprinose terminalu. Sami po sebi ne znače da postoji greška ili da je projektni `.venv` aktiviran.

---

## Pitanje 4

Zašto se u `litecli`-ju red sa komandom izgubi iz prikaza kada pritisnem Backspace? Želim da zadržim automatske predloge.

---

## Odgovor 4

U prvom testu problem je nestao kada si isključio **Terminal Sticky Scroll** u VS Code-u. Zatim si otvorio novi terminal i prijavio da sve radi i kada je Sticky Scroll uključen. Zato isključivanje Sticky Scroll-a ne možemo smatrati potvrđenim trajnim rešenjem niti znamo šta je bio uzrok problema.

Sticky Scroll prikazuje prethodnu shell komandu pri vrhu terminala dok se sadržaj pomera. To je podešavanje prikaza terminala, a ne `litecli`-jev meni za dovršavanje komandi: **automatski predlozi ostaju uključeni**. Ako sada sve radi, slobodno ostavi Sticky Scroll uključen.

### Kako privremeno testirati podešavanje ako se problem vrati

1. U VS Code-u otvori Settings pomoću `Ctrl+,`.
2. Potraži `Terminal Integrated Sticky Scroll Enabled`.
3. Izaberi **Workspace** ako želiš da promena važi za otvoreni workspace, pa isključi **Terminal › Integrated › Sticky Scroll: Enabled**.
4. Vrati se u `litecli`, otkucaj `.outpu` i pritisni Backspace. Proveri da li red ostaje vidljiv i da li se predlozi i dalje pojavljuju.

Postavka u odgovarajućem `settings.json` fajlu izgleda ovako:

```json
"terminal.integrated.stickyScroll.enabled": false
```

Isključivanje utiče na Sticky Scroll za terminale u izabranom opsegu podešavanja, ne samo na `litecli`. Ako želiš da ga vratiš, ponovo uključi istu opciju. Donji red `litecli`-ja sa oznakom `[F3] Multiline` i iskačući meni predloga su zasebni elementi i ovom promenom ih ne isključuješ.

Napomena: tokom prethodne provere nisam pronašao ovu postavku u projektnom `.vscode/settings.json` fajlu. U VS Code Settings možeš proveriti njenu vrednost u željenom opsegu.

---

## Pitanje 5

U novom terminalu sve radi i sa uključenim Sticky Scroll-om. Da li je problem nastao zbog upozorenja Python Debugger ekstenzije?

---

## Odgovor 5

To je mogućnost, ali **nemamo dokaz da je upozorenje izazvalo problem sa prikazom**. Upozorenje kaže da Python Debugger želi ponovno pokretanje terminala zbog svojih promena okruženja; ne navodi problem sa skrolovanjem ili `litecli`-jem.

Otvaranjem novog terminala započeta je nova terminalska sesija, pa se promenilo više stvari odjednom. Problem je mogao biti i privremeno stanje prikaza ili nešto drugo. Znamo samo da se u novoj sesiji, prema tvom testu, ne pojavljuje ni kada je Sticky Scroll uključen.

Ako se problem vrati, zabeleži da li je upozorenje prisutno, pa u **istoj sesiji** uporedi ponašanje sa uključenim i isključenim Sticky Scroll-om. Možeš zatim uporediti i novi terminal. Pre zatvaranja ili ponovnog pokretanja starog terminala završi rad u njemu, jer se aktivni procesi prekidaju.

---
