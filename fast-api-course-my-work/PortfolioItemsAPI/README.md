# Portfolio Items API

Mini-projekat za postepeno učenje `SQL`-a, `SQLite-a`, `SQLAlchemy-ja 2.0`, `Pydantic 2` i `FastAPI`-ja. Cilj je kroz praktične vežbe savladati rad sa `bazama podataka`, `ORM`-om, `validacijom podataka` i izgradnjom `REST API`-ja i testiranjem istog.

---

## Cilj projekta

Napraviti `API` koji čuva `korisnike`, `kategorije` i `portfolio stavke` u `SQLite` bazi, a zatim postepeno dodati `validaciju`, `CRUD` operacije, `testove` i `migracije`.

Rad ide u fazama: prvo razumeti i vežbati `SQL`, pa tek onda preći na ORM i `API` sloj kroz `FastAPI` i `Pydantic`.

---

## Planirane tabele

- **users** — korisnici projekta; početni model u materijalu sadrži `id`, `name` i `email`.
- **categories** — kategorije stavki; početni model sadrži `id` i `name`.
- **items** — portfolio stavke sa poljima kao što su `title`, `description`, `price`, `status`, `created_at` i `updated_at`. `owner_id` povezuje stavku sa `users.id`, a `category_id` sa `categories.id`.

Trenutni modeli su u [models.py](./models.py). `description` je opcion, `status` je ograničen na `draft`/`published`, a cena, status, datumi i oba strana ključa su obavezni. Ovo je edukativna početna šema; pre prve baze potrebno je potvrditi sva domenska pravila.

---

## Struktura

```text
PortfolioItemsAPI/
├── api/
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       ├── users.py
│       ├── categories.py
│       └── items.py
├── core/
│   ├── __init__.py
│   └── config.py       # konfiguracija aplikacije, npr. putanja do baze, tajni ključevi, environment varijable
│
├── data/                 # lokalni SQLite fajlovi; ne commit-ovati bazu podataka
├── db/
│   ├── __init__.py
│   ├── base.py
│   ├── database.py
│   └── session.py
├── progress/             # dnevni zapisi i retrospektive
├── main.py
├── models.py
├── schemas.py           # Pydantic modeli za validaciju i serijalizaciju API ulaza i izlaza
├── __init__.py
└── README.md
```

Uloga koju planiramo za slojeve:

- `__init__.py` — označava Python paket. Prisutan je u svim direktorijumima koji sadrže Python module. Zahvaljujući njemu, Python tretira direktorijum kao paket (direktorijum + `__init__.py`) i omogućava uz pomoć `.` (dot) notacije uvoz modula iz tog paketa. Prisustvo ovog fajla je važno za pravilno prepoznavanje paketa i organizaciju koda.

- `db/` — engine, SQLAlchemy `Base`, sesije i kasnije dependency za DB sesiju. Svi fajlovi u ovom direktorijumu služe za konfiguraciju i inicijalizaciju baze podataka, uključujući kreiranje sesija i povezivanje sa SQLite fajlom. Ovaj sloj omogućava centralizovano upravljanje konekcijom i transakcijama, što olakšava kasniju integraciju sa FastAPI aplikacijom i testiranje. Tipični fajlovi u ovom direktorijumu uključuju `base.py` za definisanje `Base` klase, `database.py` za kreiranje engine-a i povezivanje sa bazom, i `session.py` za upravljanje DB sesijama i eventualno definisanje FastAPI dependency-a za sesiju.

- `models.py` — SQLAlchemy ORM modeli/tabele. Ovaj fajl definiše strukturu baza podataka kroz Python klase koje nasleđuju `Base` i mapiraju se na odgovarajuće tabele. Svaka klasa predstavlja jednu tabelu, a atributi klase kolone tabele, uključujući tipove podataka, primarne i strane ključeve, kao i eventualna ograničenja. Tipični modeli u ovom fajlu uključuju `User`, `Category` i `Item`, koji odgovaraju entitetima u aplikaciji i omogućavaju rad sa podacima kroz ORM pristup umesto direktnog pisanja SQL upita.

- `schemas.py` — Pydantic modeli za API ulaz i izlaz. Ovaj fajl definiše strukturu podataka koje FastAPI očekuje prilikom primanja zahteva (input) i koje vraća kao odgovor (output). Pydantic modeli omogućavaju validaciju podataka, automatsko generisanje dokumentacije i olakšavaju rad sa tipizovanim podacima unutar FastAPI aplikacije. Oni služe kao most između sirovih HTTP zahteva i internih ORM modela, osiguravajući da podaci koji ulaze i izlaze iz aplikacije budu konzistentni i validni.

- `api/routes/` — FastAPI endpoint-i, razdvojeni po resursima. Svaki fajl u ovom direktorijumu definiše rute za određeni resurs (npr. `users`, `categories`, `items`) i sadrži funkcije koje obrađuju HTTP zahteve (GET, POST, PUT, DELETE) za taj resurs. Ovaj sloj omogućava modularnu organizaciju API logike i olakšava održavanje i testiranje pojedinačnih ruta. Tipični fajlovi u ovom direktorijumu uključuju `users.py`, `categories.py` i `items.py`, koji definišu rute i logiku za rad sa odgovarajućim entitetima, koristeći dependency-e, Pydantic modele iz `schemas.py` i ORM modele iz `models.py`.

- `core/` — osnovna logika i konfiguracija aplikacije. Ovaj direktorijum može sadržavati fajlove za konfiguraciju, utility funkcije, dependency-e i eventualno poslovnu logiku koja nije direktno vezana za modele ili rute. Omogućava centralizovano upravljanje ključnim komponentama aplikacije i olakšava održavanje i testiranje. Tipični fajlovi u ovom direktorijumu mogu uključivati `config.py` za konfiguracione parametre, `dependencies.py` za definisanje FastAPI dependency-a i eventualno `utils.py` za pomoćne funkcije koje se koriste širom aplikacije. Takođe, može sadržavati fajlove za inicijalizaciju logger-a, definisanje globalnih konstanti i eventualno middleware-e koji se primenjuju na celu aplikaciju. Ovaj sloj omogućava da se ključne komponente aplikacije, kao što su konfiguracija, dependency-i i pomoćne funkcije, centralizovano upravljaju i lako integrišu sa ostalim slojevima aplikacije.

- `main.py` — sastavljanje FastAPI aplikacije i router-a. Ovaj fajl inicijalizuje FastAPI instancu, uključuje sve potrebne rute iz `api/routes/` direktorijuma i konfiguriše eventualne middleware-e, exception handler-e i startup/shutdown događaje. To je ulazna tačka aplikacije i centralno mesto za povezivanje svih slojeva.

- `data/` — lokalni podaci, uključujući SQLite fajl kada ga projekat bude koristio. Ovaj direktorijum služi kao skladište za statičke podatke i inicijalne baze podataka, omogućavajući jednostavan pristup i manipulaciju podacima tokom razvoja i testiranja aplikacije. Preporučuje se da se u ovom direktorijumu čuvaju samo fajlovi koji su neophodni za lokalni razvoj i testiranje, dok produkcioni podaci treba da budu odvojeni. Tipično uključuje inicijalne `SQL fajlove`, `SQLite baze` i eventualno `JSON` ili `CSV` fajlove sa test podacima.

- `progress/` — dnevni zapisi i retrospektive. Ovaj direktorijum služi za beleženje napretka u razvoju aplikacije, uključujući dnevne zapise, retrospektive i eventualne beleške o problemima i rešenjima. Omogućava praćenje razvoja projekta i olakšava evaluaciju postignutih ciljeva i identifikaciju oblasti za poboljšanje. Tipično uključuje fajlove sa datumima ili iteracijama, gde se evidentiraju aktivnosti, problemi, rešenja i zaključci, čime se stvara istorija razvoja projekta koja može biti korisna za retrospektive i planiranje budućih koraka.

- `README.md` — dokumentacija projekta. Ovaj fajl sadrži informacije o strukturi projekta, uputstva za instalaciju, konfiguraciju i korišćenje aplikacije, kao i plan rada i eventualne napomene za dalji razvoj. Omogućava novim članovima tima ili korisnicima da brzo razumeju svrhu i organizaciju projekta. Tipično uključuje opis direktorijuma i fajlova, uputstva za pokretanje aplikacije, informacije o zavisnostima i eventualno linkove ka dodatnim resursima ili dokumentaciji.

`models.py`, `db/base.py`, `db/database.py` i `main.py` sadrže početnu `ORM` i `SQLite` postavku. `Pydantic` šeme, `rute`, `endpoint`-i i `migracije` još nisu implementirani.

`main.py` poziva `create_all()` pri uvozu aplikacije, zato pre njenog pokretanja proveri DB URL i postojanje `data/` direktorijuma. Ako direktorijum ne postoji, SQLite neće automatski kreirati roditeljske direktorijume, što može dovesti do greške pri inicijalizaciji baze. Takođe, ako `portfolioitemsapp.db` već postoji, `create_all()` se neće izvršiti nad postojećom bazom, pa neće menjati njenu šemu. Trenutno rešenje je brisanje postojeće baze i ponovo pokretanje aplikacije kako bi se kreirala nova baza sa ažuriranom šemom. Mana je što se pri svakom brisanju gube svi podaci, što nije prihvatljivo u produkcionom okruženju.

---

## Plan rada

1. Vežbati osnovne `SELECT`, `WHERE`, `INSERT`, `UPDATE` i `DELETE` upite iz `docs/stage_2/01_setup_database/04_queries_introduction` nad postojećom bazom `Project_3/data/todosapp3.db`. Ovaj korak omogućava razumevanje osnovnih SQL operacija i priprema za rad sa složenijim upitima i ORM slojem u narednim fazama razvoja aplikacije.

2. Nastaviti SQL materijale o modelovanju i SQLite transakcijama, uključujući kreiranje i proveru `users`, `categories` i `items` šeme u `Portfolio Items` aplikaciji.

3. Uvesti SQLAlchemy 2.0: `engine`, `Base`, tipizovane ORM modele i sesije.

4. Povezati FastAPI i `Pydantic 2`, pa dodavati CRUD endpoint-e postepeno.

5. Dodati izolovane testove i kasnije migracije.

Ne preskačemo direktno na ORM CRUD: prvo treba razumeti SQL upite i strukturu relacionih tabela. Dok razvojna baza nema podatke koje treba sačuvati, može se planski obrisati i ponovo napraviti radi promene početne šeme. Kada se uvede Alembic i baza sadrži podatke, promene šeme treba raditi migracijama, a ne brisanjem baze.

---

## Beleške po danima

U `progress/` čuvamo po jedan Markdown fajl po radnom danu, nazvan `YYYY-MM-DD.md`. Fajl beleži šta smo stvarno obradili, naučili, proverili i šta ostaje za sledeći put. Ne označavamo planirane vežbe kao završene pre nego što ih uradimo.

- [Retrospektiva za 2026-11-16](./progress/2026-11-16.md)
- [SQLite terminal vežbe](./sqlite3_exercises.md)

---

## Materijal za učenje

- [SQL Database kursni materijali](../../docs/sql_database/README.md)
- [SQL upiti: SELECT, WHERE, INSERT, UPDATE, DELETE](../../docs/stage_2/01_setup_database/04_queries_introduction/04_queries_introduction_detaljno.md)
- [SQLite terminal praksa](../../docs/stage_2/01_setup_database/05_sqlite3_setting_up_Todos/05_sqlite3_setting_up_Todos_detaljno.md)
- [Plan vežbi i mini-projekat](../../docs/sql_database/09_plan_vezbe_i_mini_projekat.md)
