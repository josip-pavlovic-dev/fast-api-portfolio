# Šta je važno naučiti u SQLite-u

Ne moraš **duboko da učiš SQLite interne detalje** ako ti je cilj da kasnije radiš sa MySQL-om i PostgreSQL-om. Važno je da kroz SQLite dobro savladaš temelje relacionih baza i SQL — to znanje se prenosi.

## Osnovni koncepti i veštine koje treba savladati

U ovom delu se fokusiramo na ono što je ključno za razumevanje i praktičan rad sa SQLite-om, a što se lako prenosi na druge relacionе baze. Ne ulazimo u detalje implementacije SQLite-a, već u osnovne koncepte i veštine koje će ti biti potrebne u svakodnevnom radu sa SQL-om i bazama podataka.

Ovo uključuje razumevanje osnovnih SQL naredbi, modela podataka, veza između tabela, ograničenja integriteta, indeksiranja i osnovnog optimizovanja upita. Takođe je važno znati kako aplikacija komunicira sa bazom, kako se upravlja transakcijama i kako se rešavaju konflikti pri istovremenom pristupu. Na ovaj način ćeš steći praktične veštine koje su primenljive i na druge relacionе baze, dok ćeš specifičnosti SQLite-a učiti po potrebi.

---

### Vredi temeljno naučiti

Ovo su ključne oblasti koje će ti omogućiti da razumeš i efikasno koristiš SQLite, a istovremeno stekneš znanje koje se lako prenosi na druge relacionе baze:

- `tabele`, `kolone`, `redove` i `tipove podataka`, uključujući razliku između `storage klasa` i `afiniteta kolona` i kako se oni ponašaju u praksi, kao i osnovne SQLite specifičnosti poput `rowid` i ponašanja `NULL` vrednosti, kao i osnovne operacije nad njima (`ubacivanje`, `ažuriranje`, `brisanje` i `čitanje`)

- `primarne` i `strane ključeve`, `NOT NULL`, `UNIQUE` i `CHECK` ograničenja i njihovu primenu u praksi, uključujući kako se definišu i kako utiču na integritet podataka

- `veze 1:N` i `N:M`, `normalizaciju` i kako se one implementiraju u praksi kroz tabele i veze između njih

- `SELECT`, filtriranje, sortiranje, agregacije i `JOIN`, uključujući razumevanje različitih tipova `JOIN`-ova i kada ih koristiti

- `INSERT`, `UPDATE`, `DELETE` i `transakcije`, sa naglaskom na **pravilno korišćenje transakcija za očuvanje integriteta podataka**, uključujući kada koristiti eksplicitne transakcije, kako se ponašaju u slučaju grešaka i kako se kombinuju sa zaključavanjem i konkurentnim pristupom bazi, kao i kako se pravilno rukuje greškama i konfliktima u praksi

- `indekse` i osnovno razumevanje `plana upita`, uključujući kada i kako koristiti indekse za optimizaciju performansi upita, kao i kako analizirati i interpretirati plan upita u praksi

- `Konekcije`, `transakcije` i kako aplikacija pristupa bazi, uključujući **razumevanje razlike između autocommit režima i eksplicitnog upravljanja transakcijama**, kao i kako se pravilno zatvaraju konekcije i osigurava integritet podataka u višekorisničkom okruženju, posebno u kontekstu SQLite-ovog zaključavanja fajla i ograničenja broja istovremenih pisaca, kao i kako se nositi sa potencijalnim konfliktima i greškama prilikom konkurentnog pristupa bazi u praksi, uključujući primere i najbolje prakse za rukovanje ovim situacijama

---

### Dovoljno je razumeti, ne pamtiti u detalje

SQLite-ove specifičnosti kao što su `rowid`, tipovi i **affinity**, `PRAGMA`, `.dump`, `.backup`, `ATTACH`, zaključavanje fajla i to da SQLite obično dopušta samo jednog pisca u datom trenutku. Dobro je znati da postoje i kada su korisni, ali ne moraš sada proučavati format fajla ili unutrašnju implementaciju SQLite-a. Fokusiraj se na praktičnu upotrebu i razumevanje kako ove specifičnosti utiču na rad sa bazom u realnim scenarijima.

Kada pređeš na `MySQL` i `PostgreSQL`, ponovo ćeš učiti njihove razlike: `tipove`, `automatsko generisanje ID-jeva`, `upsert sintaksu`, `ograničenja` i `ponašanje transakcija`.

`SQLAlchemy` pomaže u radu sa modelima, ali **ne uklanja sve razlike između baza** — aplikaciju i upite treba testirati i na bazi koju ćeš stvarno koristiti.

Moj predlog: **Završi `SQLite osnove` i napravi mali `FastAPI projekat` koji pokriva `CRUD`, `relacije` i `transakcije`. Zatim prebaci taj projekat na `PostgreSQL`, pa po potrebi uči `MySQL`. Tako ćeš lakše uočiti šta je opšti SQL, a šta specifičnost jednog sistema.**
