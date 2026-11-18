# 01 — Šta je SQLite

## Cilj lekcije

U ovoj lekciji upoznaćeš SQLite, razumećeš kako se razlikuje od baze koja radi kao zaseban server i videćeš zašto se često koristi za lokalne aplikacije i razvoj. Upoznaćeš i **Chinook bazu** koju ćemo koristiti u kursu. Cilj nije samo da zapamtiš naziv tehnologije, **već da znaš šta se nalazi u fajlu baze, kako aplikacija pristupa podacima i kada SQLite jeste, a kada nije odgovarajući izbor**.

---

## Šta je SQLite

SQLite je relacioni sistem za upravljanje bazom podataka (RDBMS). Omogućava da **podatke organizuješ u tabele, povezuješ ih ključevima, postavljaš ograničenja (constraints) i čitaš ili menjaš pomoću SQL-a (Structured Query Language)**.

Naziv „SQLite“ često se koristi za tri povezane, ali različite stvari:

- **SQLite biblioteka i mehanizam** izvršavaju SQL naredbe i upravljaju bazom podataka najčešće sačuvanom u zasebnim fajlovima na disku. Sama biblioteka **ne sadrži bazu podataka**, već samo omogućava aplikaciji da **upravlja fajlovima baza**. Jednako tako, ista biblioteka može da otvori različite baze, a baza može postojati nezavisno od same biblioteke u fajlovima na disku.

- **Fajl baze** sadrži podatke, definicije tabela, indekse i druge objekte baze. Često ima nastavak `.db`, `.sqlite` ili `.sqlite3`, ali sam nastavak ne određuje da li je fajl SQLite baza.

- **`sqlite3` komandni alat (CLI)** je program kojim iz terminala otvaraš bazu i ručno izvršavaš SQL naredbe i posebne dot-komande (npr. `.tables` za prikaz tabela, `.schema` za prikaz šeme baze itd.). Ovaj alat je koristan za brzo testiranje i interaktivni rad sa SQLite bazama, ali nije neophodan za rad sa SQLite-om iz aplikacija, jer aplikacije direktno koriste SQLite biblioteku.

- SQLite **nije** SQL jezik. SQLite je **ugrađeni softver koji izvršava SQL naredbe i upravlja bazama podataka, najčešće sačuvanim u zasebnim fajlovima**. Njegova biblioteka izvršava se unutar aplikacije koja je koristi, bez zasebnog serverskog procesa.

- Pod **zasebnim serverskim procesom** podrazumeva se da **baza podataka radi kao poseban proces**, ali aplikacija ne mora sama da ga pokrene — server je obično već pokrenut kao nezavisna usluga. Aplikacija komunicira sa serverom preko **konekcije**, koja može biti **mrežna ili lokalna**, na primer preko **Unix socket-a**. Unix socket je datoteka koja omogućava lokalnu komunikaciju između aplikacije i servera na istom računaru. Ovo je suprotno od SQLite-a, gde aplikacija direktno koristi biblioteku koja upravlja fajlovima baze, bez potrebe za dodatnim serverskim procesom.

- Kod **serverskih baza**, kao što su **PostgreSQL i MySQL**, DB server radi kao **zaseban** proces. Aplikacija se povezuje sa njim i šalje mu zahteve. Nasuprot tome, **kod SQLite-a ne postoji zaseban DB server**. SQLite biblioteka se izvršava unutar procesa aplikacije i direktno upravlja bazom, bez zasebnog DB servera. Zbog toga se SQLite naziva **ugrađenim i serverless** sistemom.

- SQLAlchemy, s druge strane, **nije baza podataka**. SQLAlchemy je **Python alat** koji može da komunicira sa SQLite-om i drugim bazama preko odgovarajućih drajvera i konekcija, omogućavajući nam da **pišemo Python kod umesto direktnog SQL-a** za rad sa podacima.

---

## Ugrađena i „serverless“ (bez zasebnog DB servera) arhitektura

SQLite se naziva **ugrađenim** sistemom zato što se **SQLite biblioteka izvršava unutar procesa aplikacije**. Aplikacija poziva biblioteku, a ona **čita ili menja fajl baze**.

U tipičnoj lokalnoj upotrebi **nema** zasebnog procesa baze podataka koji moraš da pokreneš, niti aplikacija šalje SQL zahteve SQLite serveru preko mrežnog protokola.

Ovo se razlikuje od uobičajene PostgreSQL ili MySQL arhitekture. Pojednostavljeno, putanja zahteva izgleda ovako:

```text
SQLite:
aplikacija → SQLite biblioteka u procesu aplikacije → lokalni fajl baze
                 ↑                                  (+ mogući pomoćni fajlovi)
                 └──────── rezultat upita ───────────┘

PostgreSQL / MySQL:
aplikacija → konekcija → zaseban DB server → fajlovi kojima upravlja server
    ↑                          │
    └────── rezultat upita ────┘
```

| Korak       | SQLite                                                                                | PostgreSQL / MySQL                                                                                                       |
| ----------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Povezivanje | Aplikacija preko drajvera i SQLite biblioteke otvara bazu, najčešće kao lokalni fajl. | Aplikacija se preko drajvera povezuje sa zasebnim DB serverskim procesom. Server može biti na istom ili drugom računaru. |
| Izvršavanje | SQLite biblioteka izvršava SQL unutar procesa aplikacije.                             | Aplikacija šalje SQL zahtev serveru, koji ga izvršava i vraća rezultat.                                                  |
| Čuvanje     | SQLite upravlja fajlom baze i, po potrebi, pomoćnim fajlovima.                        | Server upravlja svojim fajlovima; aplikacija im obično ne pristupa direktno.                                             |

Konekcija ka serveru najčešće koristi mrežni protokol, čak i kada su aplikacija i server na istom računaru. Moguće su i lokalne konekcije, na primer preko Unix socket-a.

**Važno: izvršavanje naredbe i potvrđivanje transakcije nisu isto.** Kada naredba promeni podatke unutar otvorene transakcije, promene još nisu potvrđene. `COMMIT` potvrđuje transakciju, dok `ROLLBACK` poništava njene nepotvrđene izmene. Ovo važi i za SQLite i za serverske baze; način automatskog započinjanja i potvrđivanja transakcija zavisi od baze, drajvera i podešavanja.

Potvrda transakcije ne znači nužno da su svi izmenjeni podaci upravo tada upisani u glavni fajl baze. Na primer, SQLite u **WAL režimu** može da potvrdi promene zapisane u WAL fajl, a da ih kasnije prenese u glavni fajl baze. Serverske baze takođe mogu koristiti dnevnike i naknadne upise. Ne treba pretpostaviti ni da se svi fizički upisi dešavaju tek nakon `COMMIT`-a: baza njima upravlja tako da očuva pravila transakcija.

### Šta je WAL režim?

**WAL** je skraćenica za _Write-Ahead Logging_ — način vođenja dnevnika promena. U tom režimu SQLite zapisuje izmene u poseban WAL fajl, umesto da ih odmah prenese u glavni fajl baze.

```text
Izmena podataka → WAL fajl → COMMIT potvrđuje transakciju
                                  ↓
                       checkpoint kasnije prenosi izmene
                                  ↓
                           glavni fajl baze
```

Čitalac ne mora da čeka checkpoint da bi video potvrđene promene: SQLite pri čitanju koristi glavni fajl i odgovarajuće podatke iz WAL-a. Kada dođe do **checkpoint-a**, SQLite prenosi potvrđene izmene iz WAL-a u glavni fajl. Dugotrajna čitanja mogu odložiti potpuni prenos.

WAL omogućava da čitaoci i zapisivač često rade istovremeno, ali i dalje postoji **najviše jedan zapisivač u datom trenutku**. Već započeta transakcija čitanja može nastaviti da vidi ranije stanje dok se ne završi.

Uz bazu `primer.db` mogu se pojaviti pomoćni fajlovi `primer.db-wal` i `primer.db-shm`. WAL može sadržati potvrđene promene koje još nisu prenete u glavni fajl, zato ga ne treba ručno brisati niti pretpostaviti da je kopiranje samo glavnog fajla bezbedna rezervna kopija aktivne baze. Za rezervnu kopiju koristi SQLite mehanizam kao što je CLI komanda `.backup`.

„Serverless“ ne znači da SQLite nema softver koji izvršava bazu; znači da za uobičajeni način rada nema posebnog DB serverskog procesa. Takođe, ne znači da se svaka SQLite baza bezbedno deli preko mrežnog diska ili da je automatski pogodna za svaku web aplikaciju.

---

## Zašto je SQLite praktičan

- **Malo operativnog podešavanja:** za tipičan lokalni projekat nema zasebnog DB servera koji treba instalirati, konfigurisati, pokretati i administrirati.
- **Jednostavno korišćenje i prenos:** baza je obično jedan fajl, pa je jednostavno napraviti razvojnu bazu ili je priložiti uz zadatak.
- **Mala potrošnja resursa:** nema potrebe za zasebnim serverskim procesom za lokalni rad.
- **Transakcije:** više izmena može da se obavi kao jedna celina, tako da se promene potvrde ili ponište zajedno.
- **Podrška u mnogim okruženjima:** SQLite se koristi u desktop i mobilnim aplikacijama, alatima, testovima i drugim ugrađenim scenarijima.
- **Rad u memoriji:** moguće je napraviti bazu koja postoji samo u memoriji, što je korisno u testovima i kratkotrajnim zadacima.

„Malo podešavanja“ ne znači „nikakva priprema“: Python aplikaciji treba odgovarajuća SQLite biblioteka, a za direktan rad iz terminala može biti potrebno posebno instalirati `sqlite3` CLI. Sam SQLite CLI nije isto što i Python-ov modul `sqlite3`.

---

## Transakcije i ACID

SQLite podržava transakcije. Transakcija je grupa operacija nad bazom koja se tretira kao celina. Na primer, pri plaćanju računa može biti potrebno istovremeno umanjiti stanje jednog računa i uvećati stanje drugog. Ne želimo da se izvrši samo jedna od te dve izmene.

Svojstva transakcija često se opisuju akronimom **ACID**:

- **Atomicity (atomarnost):** transakcija se potvrđuje kao celina ili se njene izmene poništavaju.
- **Consistency (doslednost):** potvrđena transakcija treba da ostavi bazu u stanju koje poštuje definisana pravila i ograničenja.
- **Isolation (izolacija):** istovremene transakcije ne bi trebalo da vide nedovršene promene jedna druge.
- **Durability (trajnost):** potvrđene izmene treba da opstanu nakon završetka transakcije i uobičajenog ponovnog pokretanja sistema.

ACID je koristan model za razumevanje ponašanja baze, ali nije obećanje da nijedan kvar hardvera, operativnog sistema ili skladišta podataka nikada neće izazvati problem. Pouzdanost zavisi i od ispravnog korišćenja transakcija i okruženja u kome se fajl baze čuva.

---

## Tipovi podataka u SQLite-u

SQLite koristi **dinamičko tipiziranje**: tip vrednosti čuva se uz samu vrednost, a deklarisani tip kolone uglavnom određuje njenu **tip-affinity** (sklonost ka određenoj vrsti podataka). Zbog toga deklaracija tipa u SQLite-u ne funkcioniše uvek kao stroga zabrana svih drugih tipova. Na primer, kolona deklarisana kao `INTEGER` nije automatski isto što i strogo tipizovana celobrojna promenljiva u Python-u.

SQLite vrednosti razvrstava u osnovne klase skladištenja kao što su `NULL`, `INTEGER`, `REAL`, `TEXT` i `BLOB`. Tipovi koje često vidiš u definicijama tabela, poput `VARCHAR`, `NVARCHAR` ili `NUMERIC`, utiču na affinity i konverzije, ali nisu svi nezavisne klase skladištenja.

Za strožu kontrolu, SQLite od verzije 3.37.0 podržava `STRICT` tabele, uz ograničen skup prihvaćenih tipova. I tada je važno razumeti šta baza proverava, a šta treba proveriti u aplikaciji.

Za FastAPI aplikaciju ova razlika je bitna:

- Pydantic šeme proveravaju oblik i validnost ulaza i izlaza API-ja.
- SQLAlchemy mapira Python objekte i izraze na bazu.
- Ograničenja baze štite integritet podataka na nivou baze.

Ovi slojevi se dopunjuju, ali jedan ne zamenjuje druge. Ne treba se oslanjati samo na to da će SQLite odbiti svaki podatak pogrešnog Python tipa.

---

## Kada SQLite odgovara, a kada razmotriti drugu bazu

SQLite je odličan izbor za učenje, lokalni razvoj, testove, desktop aplikacije, prototipe i aplikacije sa umerenim brojem upisa. Može se koristiti i iza FastAPI-ja; činjenica da je aplikacija web API sama po sebi ne isključuje SQLite.

SQLite dozvoljava više čitalaca, ali istovremeno može da ima samo jednog zapisivača koji menja bazu. WAL režim može da poboljša istovremeni rad čitalaca i zapisivača, ali ne omogućava neograničen broj paralelnih upisa.

Razmotri PostgreSQL ili drugi klijent-server sistem kada aplikacija ima mnogo istovremenih upisa, više aplikacionih instanci na različitim računarima, potrebu za centralizovanom udaljenom bazom ili naprednijim administrativnim i pristupnim pravilima. Izbor baze zavisi od načina korišćenja, a ne samo od toga da li koristiš FastAPI.

---

## Chinook baza iz kursa

U folderu [chinook/](../chinook/) nalazi se fajl baze `chinook.db` i dijagram šeme. To je primer muzičke prodavnice sa podacima o izvođačima, albumima, numerama, kupcima, računima i plejlistama.

Neke važne tabele i veze u Chinook bazi:

- `artists` → `albums` → `tracks`: jedan izvođač može imati više albuma, a album više numera.
- `customers` → `invoices` → `invoice_items`: kupac može imati više računa, a račun više stavki.
- `playlists` ↔ `tracks`: plejlista može sadržati više numera, a numera se može nalaziti na više plejlista. Veza više-prema-više realizovana je pomoćnom tabelom `playlist_track`.
- `tracks` se povezuje i sa tabelama `genres` i `media_types`.
- `employees` sadrži i hijerarhijsku vezu preko reference na drugog zaposlenog.

Dijagram je vizuelni prikaz tabela i veza; fajl `chinook.db` je stvarna baza nad kojom ćemo izvršavati upite. Diagrami nekad skraćuju prikaz kolona, pa za tačnu definiciju koristi `.schema` ili odgovarajući SQL upit.

Uočena veza u dijagramu i deklarisani strani ključ ne znače nužno da će svaka konekcija automatski odbijati nevažeći strani ključ. SQLite provera stranih ključeva zavisi od podešavanja konekcije (`PRAGMA foreign_keys`). To je važno za kasnije i obradićemo ga detaljnije kada budemo pravili šemu i povezivali SQLAlchemy.

Da iz terminala otvoriš bazu iz kursa, pokreni:

```bash
sqlite3 fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db
```

Komanda pretpostavlja da je trenutni direktorijum terminala koren repozitorijuma. Ako nisi siguran, najpre proveri tekući direktorijum (`pwd` u Linux/macOS terminalu ili `Get-Location` u PowerShell-u), pa prilagodi putanju. Putanja do fajla je relativna u odnosu na terminal, ne u odnosu na ovaj Markdown dokument.

Možeš da proveriš verziju SQLite biblioteke dostupne u otvorenoj bazi SQL naredbom:

```sql
SELECT sqlite_version();
```

Ovo može biti korisnije od provere CLI verzije, jer u nekim okruženjima verzija SQLite biblioteke koju koristi Python aplikacija može da se razlikuje od verzije komandnog alata.

---

## SQLite u Python-u i SQLAlchemy-ju

Python standardna biblioteka sadrži modul `sqlite3` koji omogućava povezivanje sa SQLite bazom preko DB-API-ja. `sqlite3` komandni alat je zaseban izvršni program; dostupnost Python modula ne garantuje da je CLI instaliran.

SQLAlchemy koristi SQLite drajver da izvršava upite i upravlja konekcijama. U SQLAlchemy 2.0 aplikaciji SQLAlchemy modeli i izrazi predstavljaju strukturu i operacije baze, dok Pydantic modeli obično opisuju API ulazne i izlazne podatke. FastAPI povezuje HTTP zahteve sa tim slojevima, ali ne menja način na koji SQLite čuva podatke.

Kada budeš proveravao podatke kroz CLI, moraš otvoriti isti fajl koji koristi aplikacija. Dve putanje koje imaju isto ime, na primer `app.db`, mogu pokazivati na dva različita fajla ako ih aplikacija i terminal pokreću iz različitih radnih direktorijuma.

---

## Provera razumevanja

1. Objasni razliku između SQLite biblioteke, fajla baze i `sqlite3` komandnog alata.

- SQLite biblioteka je deo Python standardne biblioteke i omogućava rad sa SQLite bazama kroz Python kod.
- Fajl baze je fizički fajl na disku koji čuva podatke.
- `sqlite3` komandni alat je CLI program koji omogućava interakciju sa SQLite bazom iz terminala.
- SQLite fajl može biti otvoren i kroz Python kod i kroz CLI, ali oba pristupa rade sa istim fizičkim fajlom.

- Verzija SQLite biblioteke u Python-u i verzija CLI alata mogu biti različite, što može uticati na dostupne funkcionalnosti i ponašanje upita. CLI alat i Python modul mogu imati različite implementacije određenih funkcionalnosti, pa je važno znati koju verziju koristiš u datom kontekstu. Različite verzije mogu uticati na podržane tipove podataka, sintaksu upita i ponašanje transakcija.

2. Šta znači da je SQLite ugrađen i „serverless“? Šta to **ne** znači?

- SQLite je ugrađena biblioteka, što znači da je deo aplikacije i ne zahteva poseban server.
- „Serverless“ znači da nema odvojenog procesa koji upravlja bazom; aplikacija direktno čita i piše u fajl baze.
- To **ne** znači da SQLite **nema transakcije, zaključavanja ili ACID osobine** — one su i dalje prisutne, ali se implementiraju unutar same biblioteke i fajla baze.

3. Navedi primer u kome je transakcija važna i objasni koju ACID osobinu štiti.

- Primer: Prilikom transfera novca između dva računa, transakcija je važna da bi se osiguralo da se oba upita (smanjenje sa jednog računa i povećanje na drugom) izvrše kao celina. ACID osobina koja se ovde štiti je **Atomicity** — ili se oba upita izvrše, ili nijedan.

- Još jedan primer: Prilikom kreiranja nove narudžbine u e-commerce sistemu, potrebno je da se upis u tabelu `orders` i upis u tabelu `order_items` izvrše kao jedna transakcija. ACID osobina koja se ovde štiti je takođe **Atomicity**, kako bi se izbeglo da narudžbina postoji bez stavki ili obrnuto.

4. Zašto deklarisani tip SQLite kolone nije uvek stroga provera tipa?

- SQLite koristi **dinamičko tipiziranje**, što znači da **kolona može prihvatiti vrednosti različitog tipa od deklarisanog**. Na primer kolona deklarisana kao `INTEGER` može prihvatiti i `TEXT` vrednosti. Zbog toga možemo reći da deklarisani tip služi više kao smernica nego kao striktno pravilo, pa se tipovi proveravaju samo u određenim situacijama, a ne uvek.

- Zbog toga je važno koristiti **dodatne slojeve validacije**, kao što su **Pydantic modeli** u Python-u ili **constraints** (ograničenja) u SQLAlchemy-ju, kako bi se **osigurala konzistentnost i ispravnost podataka pre nego što stignu do baze**. Ovi slojevi validacije omogućavaju da se greške u tipu podataka ili neispravni podaci otkriju pre nego što dođu do SQLite baze, čime se smanjuje rizik od korupcije podataka i nepredviđenog ponašanja aplikacije.

5. Zašto su validacija kroz Pydantic, SQLAlchemy tipovi i ograničenja baze različiti slojevi?

- Validacija kroz **Pydantic modele** obezbeđuje da podaci koji ulaze u aplikaciju budu ispravnog tipa i formata, pre nego što se uopšte pokuša upis u bazu.

- **SQLAlchemy tipovi** služe kao dodatna provera na nivou ORM-a (**Object-Relational Mapper-a**), osiguravajući da se podaci koji se mapiraju na tabele baze podataka poštuju definisane tipove. **Mapiranje tipova se vrši prilikom definisanja modela i kolona u SQLAlchemy-ju**, čime se smanjuje rizik od neusklađenosti između aplikacionih podataka i strukture baze.

- **Ograničenja baze** (constraints) su poslednji sloj odbrane, koji garantuje integritet podataka na nivou same baze, čak i ako prethodni slojevi propuste grešku. U njih spadaju **primarni ključevi**, **strani ključevi**, **jedinstvena ograničenja** i **proverna ograničenja** (CHECK), koji osiguravaju da baza ostane konzistentna i da se ne unesu neispravni podaci. Ovaj sloj je ključan jer SQLite, zbog svoje dinamičke tipizacije, ne može sam po sebi garantovati strogu proveru tipova, pa ograničenja na nivou baze služe kao poslednja linija odbrane protiv neispravnih podataka. **Zbog toga je preporučljivo koristiti sve tri vrste validacije zajedno kako bi se postigla maksimalna sigurnost i konzistentnost podataka.**

6. Objasni vezu više-prema-više između `playlists` i `tracks` i ulogu tabele `playlist_track`.

- Veza više-prema-više (`many-to-many`) znači da jedan `playlist` može sadržati više `tracks`, i jedan `track` može biti u više `playlists`. **SQLite ne podržava direktno više-prema-više veze**, pa se koristi **spojna tabela** `playlist_track` koja sadrži strane ključeve ka `playlists` i `tracks`. Ova tabela omogućava da se evidentira svaki pojedinačni odnos između plejlista i pesama, čime se implementira veza više-prema-više. **Bez spojne tabele, ne bi bilo moguće pratiti sve kombinacije plejlista i pesama, što bi ograničilo fleksibilnost i integritet podataka u bazi.**

7. Navedi jedan slučaj u kome bi izabrao SQLite i jedan u kome bi razmotrio PostgreSQL.

- Jedan slučaj u kome bi izabrao **SQLite** je kada razvijam manju aplikaciju ili prototip koji ne zahteva kompleksne funkcionalnosti baze i gde je bitna jednostavnost i brzina postavljanja. Na primer, lokalna aplikacija za upravljanje ličnom muzikom ili beleškama.

- Jedan slučaj u kome bi razmotrio **PostgreSQL** je kada razvijam aplikaciju koja zahteva napredne funkcionalnosti baze, kao što su složene upite, transakcije, visoka konkurentnost ili integritet podataka na višem nivou. Na primer, web aplikacija sa velikim brojem korisnika i kompleksnim relacijama između podataka.

---

## Vežbe

### Vežba 1 — Pronađi Chinook bazu

1. U VS Code terminalu proveri trenutni direktorijum. Koristi komandu `pwd` na Linux/Mac ili `cd` na Windows-u da vidiš gde se trenutno nalaziš. Ovo je važno kako bi znao gde da tražiš `chinook.db` fajl i kako bi se uverio da radiš u pravom projektu.

2. Otvori `fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db` pomoću `sqlite3`.

3. U CLI-ju pokreni `.databases` i proveri da putanja pokazuje na preuzetu bazu. Ovo je važno kako bi se uverio da SQLite CLI radi sa ispravnom bazom i da neće doći do grešaka zbog pogrešne putanje.

4. Pokreni `.tables` i pronađi tabele `artists`, `albums`, `tracks`, `customers` i `invoices`.

---

### Vežba 2 — Istraži šemu

1. Prikaži definicije tabela `albums`, `tracks` i `playlist_track` pomoću `.schema ime_tabele`. Obrati pažnju na strukturu kolona, tipove podataka i definicije ključeva kako bi razumeo osnovne elemente svake tabele.

2. Pronađi njihove primarne i strane ključeve. Obrati pažnju na to kako su definisani u SQL šemi i kako se odnose na druge tabele. Ovo će ti pomoći da razumeš strukturu baze i veze između podataka. Zapiši koje kolone služe kao primarni ključevi i koje kolone referenciraju druge tabele kao strani ključevi.

3. Uporedi izlaz komandnog alata sa dijagramom šeme (ERD — Entity-Relationship Diagram) koji je priložen uz kurs. Obrati pažnju na to kako su veze između tabela prikazane na dijagramu u odnosu na definicije stranih ključeva u SQL šemi. Zapiši svoja zapažanja i razmisli o tome kako bi eventualne razlike mogle uticati na razumevanje strukture baze i integritet podataka.

4. Zabeleži najmanje jednu razliku između toga kako dijagram prikazuje podatke i kako ih SQL šema definiše. Razmisli o tome kako bi ta razlika mogla uticati na razumevanje strukture baze i integritet podataka u praksi.

---

### Vežba 3 — Istraži verzije i podešavanje stranih ključeva

1. U Chinook bazi izvrši `SELECT sqlite_version();` i zabeleži verziju SQLite biblioteke. Ovo je važno kako bi znao koje funkcionalnosti i ograničenja su dostupni u tvojoj instanci SQLite-a.

2. Izvrši `PRAGMA foreign_keys;` i zabeleži da li su provere stranih ključeva uključene u toj CLI konekciji. Obrati pažnju na to da li je rezultat `1` (uključeno) ili `0` (isključeno). Ovo je važno jer isključeni strani ključevi mogu dovesti do narušavanja integriteta podataka prilikom izvršavanja operacija koje uključuju povezane tabele. U praksi, ovo znači da čak i ako tvoja trenutna CLI konekcija ima uključene provere stranih ključeva, ne možeš pretpostaviti da će svaka nova konekcija aplikacije imati iste postavke, pa je neophodno eksplicitno uključiti ovu opciju za svaku konekciju.

3. Svojim rečima objasni zašto ovaj rezultat ne treba automatski pretpostaviti za svaku novu konekciju aplikacije. Razmisli o tome kako različite konekcije mogu imati različite postavke i kako to može uticati na integritet podataka. Takođe, razmisli o tome kako bi uključivanje ili isključivanje provere stranih ključeva moglo uticati na ponašanje aplikacije prilikom izvršavanja operacija koje uključuju povezane tabele.

- ODGOVOR: Ovaj rezultat ne treba automatski pretpostavljati za svaku novu konekciju aplikacije, jer različite konekcije mogu imati različite postavke. Uključivanje ili isključivanje provere stranih ključeva može značajno uticati na integritet podataka i ponašanje aplikacije prilikom izvršavanja operacija koje uključuju povezane tabele. Zato je važno eksplicitno postaviti `PRAGMA foreign_keys = ON;` za svaku novu konekciju kako bi se osiguralo dosledno ponašanje i očuvao integritet podataka. Provera stranih ključeva treba biti deo inicijalizacije svake konekcije prema bazi podataka zbog toga što se na taj način garantuje da će svi upiti i izmene poštovati definisane veze između tabela preko stranih ključeva.

---

### Vežba 4 — Izaberi bazu za scenario

Za svaki scenario napiši da li bi SQLite bio razuman početni izbor ili bi razmotrio klijent-server bazu. Obrazloži odgovor na osnovu broja upisa, broja instanci i načina pristupa:

1. Lokalna aplikacija za ličnu kolekciju muzike.
2. Testovi FastAPI aplikacije koji se izvršavaju na jednom računaru.
3. API koji prima veliki broj istovremenih izmena od više instanci aplikacije.

---

### Vežba 5 — Poveži koncepte sa FastAPI-jem

Napravi kratak dijagram ili listu koja prikazuje putanju jednog podatka od HTTP zahteva do trajnog zapisa. Uključi FastAPI, Pydantic, SQLAlchemy, SQLite drajver i fajl baze, a zatim napiši šta je odgovornost svakog sloja.

```mermaid
graph TD
    A[HTTP zahtev od korisnika] --> B[FastAPI]
    B[FastAPI prima i obrađuje zahtev i prosleđuje podatke iz HTTP zahteva aplikaciji] --> C[Pydantic]
    C[Pydantic validira i parsira podatke iz HTTP zahteva] --> D[SQLAlchemy]
    D[SQLAlchemy mapira podatke u SQL upite i upravlja interakcijom sa bazom] --> E[SQLite drajver]
    E[SQLite drajver izvršava SQL upite nad fajl bazom (fajl na disku)] --> F[Fajl baze]
    F[Fajl baze čuva podatke na disku] --> G[Podaci trajno sačuvani u fajlu baze]
    G --> H[Korisnik vidi rezultat]
    H --> I[Korisnik dobija potvrdu o uspehu ili grešci]
    I --> J[Kraj interakcije]
    J --> A[Korisnik može poslati novi zahtev]

    Korisnik može poslati novi zahtev --> A[HTTP zahtev od korisnika]
    Novi zahtev od korisnika pokreće isti proces od HTTP zahteva do trajnog čuvanja podataka
```

- ODGOVOR:
- FastAPI: Prima HTTP zahtev i prosleđuje podatke aplikaciji.
- Pydantic: Validira i parsira podatke iz HTTP zahteva.
- SQLAlchemy: Mapira Python objekte na SQL upite i upravlja interakcijom sa bazom.
- SQLite drajver: Izvršava SQL upite nad SQLite bazom.
- Fajl baze: Trajno čuva podatke na disku.

Ova putanja pokazuje kako podaci prolaze kroz različite slojeve aplikacije, od trenutka kada korisnik pošalje HTTP zahtev, preko validacije i mapiranja u Python objekte, do izvršavanja SQL upita i trajnog čuvanja u SQLite bazi. Svaki sloj ima svoju odgovornost i doprinosi očuvanju integriteta i konzistentnosti podataka.

Napomena: U realnim aplikacijama, slojevi mogu biti složeniji i uključivati dodatne komponente kao što su keširanje, autentifikacija, autorizacija i logovanje, ali osnovni princip ostaje isti — svaki sloj ima jasno definisanu ulogu u obradi i čuvanju podataka.
