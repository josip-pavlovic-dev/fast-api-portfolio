# Dan 04 — SQLite `.dump`: plan učenja, vežbe i odgovori

## Namena ovog fajla

Ovde su plan i dodatne vežbe za današnji rad. U ovaj dokument dopunjavaćemo i odgovore na tvoja naredna pitanja iz današnjeg rada, kako bi pitanja, objašnjenja i primeri ostali na jednom mestu.

**Današnji datum:** 24. novembar 2026. Ne moraš pratiti prvobitne datume iz [opšteg plana](../plan_ucenja/README.md): trenutno si na lekciji o povezivanju, a `.dump` je sledeća tema koju želiš da pripremiš. Napreduj kada razumeš gradivo, bez preskakanja.

---

## 1. Cilj dana

Do kraja rada treba samostalno da:

1. Razlikuješ **fajl baze** od aktivne SQLite konekcije i proveriš putanju sa `.databases`.
2. Otvoriš `chinook_practice.db` samo za čitanje sa svojim `rlwrap` podešavanjem.
3. Objasniš šta `.dump`, `.output`, `.once`, `.read` i `.backup` rade i gde se unose.
4. Napraviš SQL dump, pregledaš ga i vratiš u **novu, zasebnu** bazu.
5. Proveriš ishod i razlikuješ SQL dump od SQLite kopije baze.

> **Zaštita podataka:** radna kopija je izvor, ne odredište za `.read`. Originalna i radna Chinook baza ostaju netaknute. `.output` i `.backup` mogu kreirati ili prepisati zasebne izlazne fajlove čak i kada je izvor otvoren sa `-readonly`. Vežbaj samo u novom, posebno napravljenom folderu i ne pokreći komande ako nisi siguran u ciljnu putanju.

---

## 2. Predlog rasporeda — četiri sata

Pauze pravi između blokova; nisu uračunate u četiri sata. Ako negde zastaneš, nastavi kasnije: vreme je okvirno, a ne rok.

| Trajanje            | Aktivnost                                                                                                                                                                                         | Šta treba da ostane kao rezultat                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **30 min**          | Završavanje i ponavljanje povezivanja: pročitaj [lekciju 03 — povezivanje](../00_intro/03_how_to_connect_to_sqlite.md), otvori radnu kopiju i proveri `.databases`, `.tables` i `.schema albums`. | Zapiši razliku između fajla, konekcije i CLI-ja i proverenu putanju.                               |
| **60 min**          | Pročitaj ažuriranu [lekciju o `.dump`](../01_some_basic_sql_commands/03_sqlite_dump_command.md): pripremu, izvoz, obnovu i razliku između `.dump` i `.backup`.                                    | Svojim rečima objasni `.sql` naspram `.db` i zašto se za obnovu pokreće nova sesija.               |
| **120 min**         | Prvo uradi postojeće vežbe povezivanja i izvoza navedene ispod; zatim reši tri dodatna zadatka iz odeljka 4.                                                                                      | Zabeleži komande, zapažanja i eventualne greške; za praktične fajlove koristi zaseban novi folder. |
| **30 min**          | Uporedi rezultate i rešenja, proveri da nema grešaka i odgovori na pitanja iz lekcije bez gledanja.                                                                                               | Zapiši šta ti je jasno i koje pitanje želiš da postaviš.                                           |
| **Ukupno: 240 min** | Četiri sata aktivnog učenja.                                                                                                                                                                      | Nije potrebno da sve uradiš bez pauze.                                                             |

---

### Već postojeće vežbe — bez dupliranja zadataka

1. U [vežbama lekcije o povezivanju](../00_intro/03_how_to_connect_to_sqlite.md#vežbe) uradi naročito **vežbu 1** i **vežbu 3**. U vežbi 1 koristi radnu kopiju i `-readonly` iz ovog dnevnika umesto izvorne baze iz primera; `.databases` treba da pokaže `chinook_practice.db`. Ostale vežbe radi po potrebi. Vežba 5 pokreće aplikaciju koja može menjati bazu, pa **nije potrebna za današnji `.dump`**.

2. U [vežbama lekcije o `.dump`](../01_some_basic_sql_commands/03_sqlite_dump_command.md#vežbe) uradi vežbe 1–4: puni dump, obnova, poređenje sa `.backup` i dump tabele `albums`. Koristi tačne korake i bezbednosne provere iz ažurirane lekcije.

3. Po potrebi ponovi [često korišćene SQLite komande](../01_some_basic_sql_commands/02_some_commonly_used_sqlite3_commands.md#vežbe) i [uputstvo za `rlwrap`](../../../docs/fastapi/cheatsheets/fastapi_extensions_vscode/sqlite_terminal_litecli_rlwrap.md#4-rlwrap-tab-dovršavanje-u-pravom-sqlite-cli-ju).

4. Svoje CLI beleške možeš sačuvati u [predviđenom fajlu za vežbe](../playground/cli/03_sqlite_dump_command.txt). On je namenjen beleškama; nemoj automatski izvršavati njegov ceo sadržaj pomoću `.read` bez prethodnog pregleda.

---

## 3. Priprema terminala i siguran redosled rada

Iz korena repozitorijuma, u **Bash terminalu**, pokreni:

```bash
INPUTRC="$HOME/.config/sqlite-cli/sqlite3-inputrc" \
  rlwrap -a -N -c -i -A -f "$HOME/.config/sqlite-cli/sqlite3-completions" \
  sqlite3 -cmdline-edit off -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db
```

Ako već koristiš tu sesiju, nema potrebe da je pokrećeš ponovo. U otvorenom **SQLite CLI-ju**:

```text
.databases
.tables
SELECT COUNT(*) AS album_count FROM albums;
```

Proveri da `main` pokazuje `chinook_practice.db` i `r/o`; zapiši broj albuma. Rezultat je podatak iz konkretne radne kopije, ne nepromenljivo pravilo baze. SQL naredba završava se sa `;`; dot-komande se unose bez `;`.

Zatim prati odeljke **Priprema**, **Napravi dump** i **Vrati bazu** u [lekciji o `.dump`](../01_some_basic_sql_commands/03_sqlite_dump_command.md). Ukratko:

1. U Bash-u napravi novi folder za vežbu (npr. `fast-api-course-my-work/sqlite_for_beginners/playground/dump_vezba_2026_11_24`) ako već postoji, stani i odaberi drugo novo ime.

2. U `-readonly` sesiji radne kopije (otvorene iz korena repozitorijuma sa `rlwrap` i `sqlite3 -readonly fast-api-course-my-work/sqlite_for_beginners/playground/databases/chinook_practice.db`) napravi `chinook_dump.sql` u novom folderu za vežbu koji si prethodno kreirao (npr. `fast-api-course-my-work/sqlite_for_beginners/playground/dump_vezba_2026_11_24/chinook_dump.sql`). Završi `.dump` i vrati izlaz na terminal.

3. Izađi iz izvorne sesije sa `.quit`. Proveri da ciljni `.db` fajl (npr. `fast-api-course-my-work/sqlite_for_beginners/playground/dump_vezba_2026_11_24/chinook_restored.db`) ne postoji pre nego što otvoriš novu sesiju.

4. Otvori zasebnu **upisivu** SQLite CLI sesiju nad novim fajlom baze (npr. `fast-api-course-my-work/sqlite_for_beginners/playground/dump_vezba_2026_11_24/chinook_restored.db`) i potvrdi `.databases` i da je baza prazna.

5. Pregledani dump učitaj sa `.read` i proveri broj albuma, `integrity_check` i `foreign_key_check`.

Nemoj pomešati prozore ili promptove: ista komanda `.read` izvršava sadržaj fajla u **onoj konekciji u kojoj je uneseš**. Ako u bilo kom koraku putanja ili poruka nije očekivana, stani i proveri je pre nastavka.

---

## 4. Dodatni zadaci za samostalnu vežbu

Prvo odgovori sam. Rešenja su izdvojena u odeljku 5. Zadatke sa izmišljenim podacima možeš rešiti bez upisivanja u bazu.

### Zadatak 1 — Koji alat i koja sesija?

Popuni tabelu tako što ćeš napisati odgovarajuću naredbu ili opis sesije:

| Želim da uradim                                              | Moj odgovor |
| ------------------------------------------------------------ | ----------- |
| Proverim putanju otvorene baze.                              |             |
| Pošaljem izlaz u novi SQL fajl dok ga ne vratim na terminal. |             |
| Izvezem šemu i podatke otvorene baze kao SQL.                |             |
| Vratim izlaz na terminal.                                    |             |
| Izvršim pregledani dump u novoj bazi.                        |             |
| Napravim SQLite kopiju u zasebnom `.db` fajlu.               |             |
| Napišem gde je `-readonly` poželjan, a gde je upis potreban. |             |

---

### Zadatak 2 — Šta dokazujemo proverom?

Zamisli da izvorna radna kopija sadrži 347 albuma, a novi obnovljeni fajl takođe vrati 347 za `SELECT COUNT(*) FROM albums;`.

1. Šta ti to poređenje govori, a šta **ne dokazuje**?

- Broj albuma se poklapa, što znači da su svi redovi u tabeli `albums` preneti, ali to ne dokazuje da su svi povezani podaci u drugim tabelama takođe preneti.
- Ovo poređenje dokazuje samo da je broj redova u tabeli `albums` isti, ali ne garantuje integritet celokupne baze.
- Dakle, iako se broj albuma poklapa, moguće je da su neki redovi u povezanim tabelama izostavljeni ili da postoje narušene veze između tabela.
- Drugim rečima, broj redova u jednoj tabeli ne garantuje da su svi strani ključevi validni ili da su sve zavisne tabele pravilno prenete.

2. Ako `PRAGMA integrity_check;` vrati `ok`, šta si dodatno proverio?

- Ako `PRAGMA integrity_check;` vrati `ok`, to znači da SQLite nije pronašao nikakve unutrašnje greške u strukturi baze, uključujući korupciju podataka i narušene indekse. Drugim rečima, baza je konzistentna sa stanovišta SQLite engine-a, ali to ne garantuje da su svi strani ključevi validni ili da su svi podaci u povezanim tabelama prisutni.

- Dakle, i dalje je moguće da postoje logičke greške u podacima, kao što su nedostajući redovi u povezanim tabelama ili nevalidni strani ključevi, koje `integrity_check` ne može otkriti.

- Drugim rečima, `integrity_check` proverava tehničku ispravnost baze, dok logičku ispravnost i potpunost podataka moraš proveriti dodatnim upitima i proverama veza između tabela.

3. Ako `PRAGMA foreign_key_check;` **ne vrati nijedan red**, kako tumačiš rezultat? Da li to znači da je `PRAGMA foreign_keys` uključena za naredne upise?

- Ako `PRAGMA foreign_key_check;` **ne vrati nijedan red**, to znači da **SQLite nije pronašao narušene strane ključeve u bazi**. Drugim rečima, svi strani ključevi koji postoje u tabelama su **validni i upućuju na postojeće redove u povezanim tabelama**. Međutim, to ne garantuje da su svi podaci u povezanim tabelama prisutni, niti da su svi strani ključevi uključeni u bazu. Takođe, ovo ne utiče na to da li je `PRAGMA foreign_keys` uključena za naredne upise.

- Da bi se uključila provera stranih ključeva za naredne upise, potrebno je eksplicitno izvršiti `PRAGMA foreign_keys = ON;`. Sam rezultat `foreign_key_check` ne menja stanje ove postavke.

4. Šta radiš ako `.read` prijavi grešku i u novoj bazi se pojave samo neke tabele?

- Ako `.read` prijavi grešku i u novoj bazi se pojave samo neke tabele, to znači da dump fajl nije uspešno primenjen u celosti. U tom slučaju treba:
  1. Proveriti sadržaj dump fajla i identifikovati gde je došlo do greške.
  2. Osigurati da su sve zavisne tabele kreirane pre nego što se ubace podaci koji zavise od njih.
  3. Ponovo pokušati učitavanje dump fajla, vodeći računa o redosledu kreiranja tabela i ubacivanja podataka.

  4. Ako je potrebno, izvršiti dump cele baze bez filtera kako bi se obezbedila potpuna kopija svih tabela i njihovih zavisnosti.

  5. Uvek proveriti da li su sve tabele i podaci uspešno učitani u novu bazu nakon ponovnog učitavanja dump fajla.

- Ukratko, **greške pri učitavanju dump fajla mogu dovesti do nepotpunih baza**, pa je važno pratiti redosled kreiranja tabela i ubacivanja podataka, kao i proveriti integritet i potpunost podataka nakon učitavanja.

---

### Zadatak 3 — Ograničeni dump i zavisnosti

Posmatraj Chinook vezu: `albums.ArtistId` upućuje na `artists.ArtistId`. U izvozu sa `.dump albums` nema podataka cele baze.

1. Zašto `albums_only.sql` ne treba smatrati potpunom kopijom baze?

- `albums_only.sql` sadrži samo tabele i podatke vezane za `albums`, ali ne uključuje sve ostale tabele i njihove zavisnosti. Zbog toga ne predstavlja potpunu kopiju cele baze, jer nedostaju povezane tabele kao što su `artists`, `tracks` i druge koje su neophodne za integritet podataka.

- Čak i ako broj redova u `albums_only.sql` odgovara broju redova u originalnoj tabeli `albums`, to ne garantuje da su svi povezani podaci prisutni, jer zavisne tabele mogu biti nepotpune ili odsutne.

- Dakle, broj redova u izolovanom dump-u ne može biti jedini kriterijum za procenu potpune rekonstrukcije baze, jer integritet podataka zavisi od prisustva svih povezanih tabela i njihovih redova.

- Čak i ako se broj redova poklapa, odsustvo zavisnih tabela ili nepotpuni podaci u njima mogu dovesti do neispravne ili nepotpune baze.

2. Zašto broj 347 redova u izdvojenom dump-u, čak i ako se podudari sa izvorom, ne potvrđuje da je moguće rekonstruisati sve povezane podatke?

- Broj redova u izdvojenom dump-u ne potvrđuje prisustvo svih zavisnih tabela i njihovih podataka. Čak i ako se broj redova u tabeli `albums` poklapa sa izvorom, odsustvo ili nepotpunost povezanih tabela kao što su `artists` ili `tracks` može onemogućiti potpunu rekonstrukciju baze. Integritet podataka zavisi od prisustva svih povezanih tabela i njihovih redova, a ne samo od broja redova u jednoj tabeli.

3. Koji izvoz biraš za obnovu cele baze: `.dump albums` ili `.dump` bez filtera?

- Za obnovu cele baze treba koristiti `.dump` bez filtera, jer on uključuje sve tabele i njihove podatke, čime se obezbeđuje potpuna rekonstrukcija baze sa svim zavisnostima. `.dump albums` je ograničen samo na tabelu `albums` i ne uključuje povezane tabele, što može dovesti do nepotpunih podataka i narušenog integriteta baze.

- `.once` je idealan za privremeno preusmeravanje izlaza samo za jednu naredbu, dok `.output` menja izlaz za sve naredne naredbe dok se eksplicitno ne vrati na `stdout`. Dakle, za jednokratni dump ili privremeno preusmeravanje izlaza koristi `.once`, a za dugotrajno preusmeravanje koristi `.output`.

4. U lokalno proverenom SQLite CLI-ju 3.54.1 može li `.once` da preusmeri sledeći `.dump`? Po čemu se razlikuje od `.output`?

- `.once` preusmerava izlaz samo za sledeću komandu, dok `.output` preusmerava izlaz za sve naredne komande dok se ponovo ne promeni ili ne vrati na `stdout`. Dakle, ako želiš da privremeno preusmeriš rezultat jednog `.dump` ili bilo koje druge komande u fajl, koristi `.once putanja/do/fajla.sql`. Ako želiš da trajno preusmeriš izlaz u fajl dok ne promeniš, koristi `.output putanja/do/fajla.sql`.

- `.once` je koristan kada želiš da privremeno preusmeriš izlaz samo za jednu komandu, dok `.output` menja izlaz za sve naredne komande dok se eksplicitno ne vrati na `stdout`. Dakle, za jednokratni dump ili privremeno preusmeravanje izlaza koristi `.once`, a za dugotrajno preusmeravanje koristi `.output`.

---

## 5. Rešenja i objašnjenja dodatnih zadataka

### Rešenje 1 — Komande i sesije

| Želim da uradim                                  | Rešenje i razlog                                                                                                                                                             |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Proverim putanju otvorene baze.                  | `.databases` u SQLite CLI-ju prikazuje ime i putanju trenutne baze.                                                                                                          |
| Pošaljem izlaz u novi SQL fajl dok ga ne vratim. | `.output putanja/do/novog_fajla.sql` u CLI-ju; cilj može biti prepisan ako postoji.                                                                                          |
| Izvezem šemu i podatke kao SQL.                  | `.dump` u CLI-ju otvorenom nad željenim izvorom. Pre toga preusmeri izlaz.                                                                                                   |
| Vratim izlaz na terminal.                        | `.output stdout` u istoj CLI sesiji.                                                                                                                                         |
| Izvršim pregledani dump u novoj bazi.            | `.read putanja/do/dumpa.sql` u **zasebnoj upisivoj sesiji** otvorenoj nad novom praznom bazom.                                                                               |
| Napravim SQLite kopiju.                          | `.backup putanja/do/nove_kopije.db` u CLI-ju otvorenom nad izvorom.                                                                                                          |
| Izaberem režim.                                  | `-readonly` koristi za pregled i izvoz iz radne kopije; upis u posebnu novu ciljnu bazu potreban je za `.read`. `.output` i `.backup` svejedno pišu zasebne izlazne fajlove. |

`.read` ne znači „samo prikaži fajl”: komande u njemu se izvršavaju. Nikada ne učitavaj nepoznatu skriptu bez provere.

---

### Rešenje 2 — Granice provere

1. Jednak broj pokazuje da tabela `albums` u oba posmatrana trenutka ima isti broj redova; **ne dokazuje** da su sadržaj tih redova, druge tabele ili šema identični.

2. `integrity_check` proverava unutrašnju ispravnost strukture baze; `ok` ne dokazuje da je sadržaj jednak izvoru.
3. Nijedan red iz `foreign_key_check` znači da nisu prijavljene FK povrede. To samo po sebi ne uključuje FK proveru za buduće upise; njeno stanje u konkretnoj konekciji proveravaš sa `PRAGMA foreign_keys;`.

4. Obnova nije potvrđena kao uspešna. Pročitaj poruku, proveri izvor i cilj; baza može biti delimično obnovljena. Sledeći pokušaj izvedi u drugom novom fajlu, ne ponavljaj `.read` preko delimične baze.

---

### Rešenje 3 — Izdvojeni dump

1. `.dump albums` izvozi objekte koji odgovaraju tom obrascu, a ne automatski čitavu Chinook bazu i sve zavisnosti. Posebno ne treba pretpostaviti da sadrži tabelu i podatke `artists`.

2. Broj albuma ne proverava da li su prisutni odgovarajući izvođači ili ostale tabele i objekti.
3. Za obnovu cele baze izaberi puni `.dump` bez filtera, uz pregled skripte i proveru rezultata.

4. Da: u proverenom CLI-ju 3.54.1 `.once` preusmerava izlaz sledećeg `.dump`, nakon čega se izlaz vraća na terminal. `.output` ostaje aktivan do `.output stdout` ili zatvaranja sesije. Obe komande mogu pisati u fajl iako je izvor otvoren sa `-readonly`.

---

## 6. Pitanja i odgovori tokom dana

U ovaj odeljak dodavaćemo tvoja naredna pitanja i odgovore, uz proverene primere kada su potrebni. Već pripremljena uputstva i vežbe ostaju u povezanim lekcijama; ovde nećemo nepotrebno umnožavati isti materijal.
