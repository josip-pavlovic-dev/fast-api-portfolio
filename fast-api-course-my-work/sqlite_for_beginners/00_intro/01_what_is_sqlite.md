# 01 — Šta je SQLite

## Cilj lekcije

U ovoj lekciji upoznaćeš SQLite, razumećeš kako se razlikuje od baze koja radi kao zaseban server i videćeš zašto se često koristi za lokalne aplikacije i razvoj. Upoznaćeš i Chinook bazu koju ćemo koristiti u kursu. Cilj nije samo da zapamtiš naziv tehnologije, već da znaš šta se nalazi u fajlu baze, kako aplikacija pristupa podacima i kada SQLite jeste, a kada nije odgovarajući izbor.

## Šta je SQLite

SQLite je relacioni sistem za upravljanje bazom podataka (RDBMS). Omogućava da podatke organizuješ u tabele, povezuješ ih ključevima, postavljaš ograničenja i čitaš ili menjaš pomoću SQL-a (Structured Query Language).

Naziv „SQLite“ često se koristi za tri povezane, ali različite stvari:

- **SQLite biblioteka i mehanizam** izvršavaju SQL naredbe i upravljaju bazom.
- **Fajl baze** sadrži podatke, definicije tabela, indekse i druge objekte baze. Često ima nastavak `.db`, `.sqlite` ili `.sqlite3`, ali sam nastavak ne određuje da li je fajl SQLite baza.
- **`sqlite3` komandni alat (CLI)** je program kojim iz terminala otvaraš bazu i ručno izvršavaš SQL naredbe i posebne dot-komande.

SQLite nije SQL jezik; SQLite je softver koji razume SQL i pruža bazu podataka. SQLAlchemy, s druge strane, nije baza podataka: to je Python alat koji može da komunicira sa SQLite-om i drugim bazama.

## Ugrađena i „serverless“ arhitektura

SQLite se naziva **ugrađenim** sistemom zato što se SQLite biblioteka izvršava unutar procesa aplikacije. Aplikacija poziva biblioteku, a ona čita ili menja fajl baze. U tipičnoj lokalnoj upotrebi nema zasebnog procesa baze podataka koji moraš da pokreneš, niti aplikacija šalje SQL zahteve SQLite serveru preko mrežnog protokola.

Ovo se razlikuje od uobičajene PostgreSQL ili MySQL arhitekture:

- **SQLite:** aplikacija → SQLite biblioteka → fajl baze
- **PostgreSQL/MySQL:** aplikacija (klijent) → mrežna veza → zaseban DB server → fajlovi kojima server upravlja

„Serverless“ ne znači da SQLite nema softver koji izvršava bazu; znači da za uobičajeni način rada nema posebnog DB serverskog procesa. Takođe, ne znači da se svaka SQLite baza bezbedno deli preko mrežnog diska ili da je automatski pogodna za svaku web aplikaciju.

## Zašto je SQLite praktičan

- **Malo operativnog podešavanja:** za tipičan lokalni projekat nema zasebnog DB servera koji treba instalirati, konfigurisati, pokretati i administrirati.
- **Jednostavno korišćenje i prenos:** baza je obično jedan fajl, pa je jednostavno napraviti razvojnu bazu ili je priložiti uz zadatak.
- **Mala potrošnja resursa:** nema potrebe za zasebnim serverskim procesom za lokalni rad.
- **Transakcije:** više izmena može da se obavi kao jedna celina, tako da se promene potvrde ili ponište zajedno.
- **Podrška u mnogim okruženjima:** SQLite se koristi u desktop i mobilnim aplikacijama, alatima, testovima i drugim ugrađenim scenarijima.
- **Rad u memoriji:** moguće je napraviti bazu koja postoji samo u memoriji, što je korisno u testovima i kratkotrajnim zadacima.

„Malo podešavanja“ ne znači „nikakva priprema“: Python aplikaciji treba odgovarajuća SQLite biblioteka, a za direktan rad iz terminala može biti potrebno posebno instalirati `sqlite3` CLI. Sam SQLite CLI nije isto što i Python-ov modul `sqlite3`.

## Transakcije i ACID

SQLite podržava transakcije. Transakcija je grupa operacija nad bazom koja se tretira kao celina. Na primer, pri plaćanju računa može biti potrebno istovremeno umanjiti stanje jednog računa i uvećati stanje drugog. Ne želimo da se izvrši samo jedna od te dve izmene.

Svojstva transakcija često se opisuju akronimom **ACID**:

- **Atomicity (atomarnost):** transakcija se potvrđuje kao celina ili se njene izmene poništavaju.
- **Consistency (doslednost):** potvrđena transakcija treba da ostavi bazu u stanju koje poštuje definisana pravila i ograničenja.
- **Isolation (izolacija):** istovremene transakcije ne bi trebalo da vide nedovršene promene jedna druge.
- **Durability (trajnost):** potvrđene izmene treba da opstanu nakon završetka transakcije i uobičajenog ponovnog pokretanja sistema.

ACID je koristan model za razumevanje ponašanja baze, ali nije obećanje da nijedan kvar hardvera, operativnog sistema ili skladišta podataka nikada neće izazvati problem. Pouzdanost zavisi i od ispravnog korišćenja transakcija i okruženja u kome se fajl baze čuva.

## Tipovi podataka u SQLite-u

SQLite koristi **dinamičko tipiziranje**: tip vrednosti čuva se uz samu vrednost, a deklarisani tip kolone uglavnom određuje njenu **tip-affinity** (sklonost ka određenoj vrsti podataka). Zbog toga deklaracija tipa u SQLite-u ne funkcioniše uvek kao stroga zabrana svih drugih tipova. Na primer, kolona deklarisana kao `INTEGER` nije automatski isto što i strogo tipizovana celobrojna promenljiva u Python-u.

SQLite vrednosti razvrstava u osnovne klase skladištenja kao što su `NULL`, `INTEGER`, `REAL`, `TEXT` i `BLOB`. Tipovi koje često vidiš u definicijama tabela, poput `VARCHAR`, `NVARCHAR` ili `NUMERIC`, utiču na affinity i konverzije, ali nisu svi nezavisne klase skladištenja.

Za strožu kontrolu, SQLite od verzije 3.37.0 podržava `STRICT` tabele, uz ograničen skup prihvaćenih tipova. I tada je važno razumeti šta baza proverava, a šta treba proveriti u aplikaciji.

Za FastAPI aplikaciju ova razlika je bitna:

- Pydantic šeme proveravaju oblik i validnost ulaza i izlaza API-ja.
- SQLAlchemy mapira Python objekte i izraze na bazu.
- Ograničenja baze štite integritet podataka na nivou baze.

Ovi slojevi se dopunjuju, ali jedan ne zamenjuje druge. Ne treba se oslanjati samo na to da će SQLite odbiti svaki podatak pogrešnog Python tipa.

## Kada SQLite odgovara, a kada razmotriti drugu bazu

SQLite je odličan izbor za učenje, lokalni razvoj, testove, desktop aplikacije, prototipe i aplikacije sa umerenim brojem upisa. Može se koristiti i iza FastAPI-ja; činjenica da je aplikacija web API sama po sebi ne isključuje SQLite.

SQLite dozvoljava više čitalaca, ali istovremeno može da ima samo jednog zapisivača koji menja bazu. WAL režim može da poboljša istovremeni rad čitalaca i zapisivača, ali ne omogućava neograničen broj paralelnih upisa.

Razmotri PostgreSQL ili drugi klijent-server sistem kada aplikacija ima mnogo istovremenih upisa, više aplikacionih instanci na različitim računarima, potrebu za centralizovanom udaljenom bazom ili naprednijim administrativnim i pristupnim pravilima. Izbor baze zavisi od načina korišćenja, a ne samo od toga da li koristiš FastAPI.

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

## SQLite u Python-u i SQLAlchemy-ju

Python standardna biblioteka sadrži modul `sqlite3` koji omogućava povezivanje sa SQLite bazom preko DB-API-ja. `sqlite3` komandni alat je zaseban izvršni program; dostupnost Python modula ne garantuje da je CLI instaliran.

SQLAlchemy koristi SQLite drajver da izvršava upite i upravlja konekcijama. U SQLAlchemy 2.0 aplikaciji SQLAlchemy modeli i izrazi predstavljaju strukturu i operacije baze, dok Pydantic modeli obično opisuju API ulazne i izlazne podatke. FastAPI povezuje HTTP zahteve sa tim slojevima, ali ne menja način na koji SQLite čuva podatke.

Kada budeš proveravao podatke kroz CLI, moraš otvoriti isti fajl koji koristi aplikacija. Dve putanje koje imaju isto ime, na primer `app.db`, mogu pokazivati na dva različita fajla ako ih aplikacija i terminal pokreću iz različitih radnih direktorijuma.

## Provera razumevanja

1. Objasni razliku između SQLite biblioteke, fajla baze i `sqlite3` komandnog alata.
2. Šta znači da je SQLite ugrađen i „serverless“? Šta to **ne** znači?
3. Navedi primer u kome je transakcija važna i objasni koju ACID osobinu štiti.
4. Zašto deklarisani tip SQLite kolone nije uvek stroga provera tipa?
5. Zašto su validacija kroz Pydantic, SQLAlchemy tipovi i ograničenja baze različiti slojevi?
6. Objasni vezu više-prema-više između `playlists` i `tracks` i ulogu tabele `playlist_track`.
7. Navedi jedan slučaj u kome bi izabrao SQLite i jedan u kome bi razmotrio PostgreSQL.

## Vežbe

### Vežba 1 — Pronađi Chinook bazu

1. U VS Code terminalu proveri trenutni direktorijum.
2. Otvori `fast-api-course-my-work/sqlite_for_beginners/chinook/chinook.db` pomoću `sqlite3`.
3. U CLI-ju pokreni `.databases` i proveri da putanja pokazuje na preuzetu bazu.
4. Pokreni `.tables` i pronađi tabele `artists`, `albums`, `tracks`, `customers` i `invoices`.

### Vežba 2 — Istraži šemu

1. Prikaži definicije tabela `albums`, `tracks` i `playlist_track` pomoću `.schema ime_tabele`.
2. Pronađi njihove primarne i strane ključeve.
3. Uporedi izlaz komandnog alata sa dijagramom šeme koji je priložen uz kurs.
4. Zabeleži najmanje jednu razliku između toga kako dijagram prikazuje podatke i kako ih SQL šema definiše.

### Vežba 3 — Istraži verzije i podešavanje stranih ključeva

1. U Chinook bazi izvrši `SELECT sqlite_version();` i zabeleži verziju SQLite biblioteke.
2. Izvrši `PRAGMA foreign_keys;` i zabeleži da li su provere stranih ključeva uključene u toj CLI konekciji.
3. Svojim rečima objasni zašto ovaj rezultat ne treba automatski pretpostaviti za svaku novu konekciju aplikacije.

### Vežba 4 — Izaberi bazu za scenario

Za svaki scenario napiši da li bi SQLite bio razuman početni izbor ili bi razmotrio klijent-server bazu. Obrazloži odgovor na osnovu broja upisa, broja instanci i načina pristupa:

1. Lokalna aplikacija za ličnu kolekciju muzike.
2. Testovi FastAPI aplikacije koji se izvršavaju na jednom računaru.
3. API koji prima veliki broj istovremenih izmena od više instanci aplikacije.

### Vežba 5 — Poveži koncepte sa FastAPI-jem

Napravi kratak dijagram ili listu koja prikazuje putanju jednog podatka od HTTP zahteva do trajnog zapisa. Uključi FastAPI, Pydantic, SQLAlchemy, SQLite drajver i fajl baze, a zatim napiši šta je odgovornost svakog sloja.
