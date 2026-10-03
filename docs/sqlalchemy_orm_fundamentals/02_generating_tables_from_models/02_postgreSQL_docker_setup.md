# Lekcija 2: PostgreSQL u Docker-u

## Cilj lekcije

U ovoj lekciji pripremamo PostgreSQL bazu koju će SQLAlchemy aplikacija koristiti u narednim koracima. Umesto instaliranja servera direktno na računar, kurs ga pokreće kao Docker kontejner definisan u `docker-compose.yml` fajlu.

Docker Compose opisuje servise i njihova podešavanja na jednom mestu, a zatim jednom komandom može da pokrene ceo skup servisa. U dostavljenom source-u to su PostgreSQL i pgAdmin.

Ova lekcija objašnjava koncepte i komande iz transkripta. Komande ispod su za lokalnu upotrebu kada je Docker instaliran; nisam ih pokretao niti sam menjao source konfiguraciju.

## Image, container i Compose

- **Docker image** je paket sa datotekama, bibliotekama i konfiguracijom potrebnim da se pokrene određeni softver. PostgreSQL image sadrži PostgreSQL server i njegovo okruženje.
- **Container** je pokrenuta instanca image-a sa svojim procesima i podešavanjima. Image može poslužiti za kreiranje više kontejnera.
- **Docker Compose** čita YAML konfiguraciju i pokreće povezane servise kao jednu aplikacionu celinu.

Kontejneri obezbeđuju ponovljivo, izolovano okruženje, ali nisu isto što i virtuelna mašina sa punim zasebnim operativnim sistemom. Docker image može da koristi minimalnu Linux osnovu, na primer Debian ili Alpine. Alpine image-i su često manji, ali manja veličina sama po sebi ne znači da je ta varijanta uvek najbolja za svaki projekat.

Kurs koristi PostgreSQL, ali principi rada sa SQLAlchemy mogu se primeniti i na druge podržane baze, uz odgovarajući drajver i razlike u SQL-u i funkcionalnosti DBMS-a.

## Čitanje `docker-compose.yml`

Source snapshot sadrži ovakvu konfiguraciju:

```yaml
name: sqlalchemy_ORM

services:
	postgres:
		image: postgres:latest
		container_name: postgres_db
		restart: always
		environment:
			POSTGRES_USER: postgres
			POSTGRES_PASSWORD: postgres
			POSTGRES_DB: inventory
		ports:
			- "5432:5432"

	pgadmin:
		image: dpage/pgadmin4
		container_name: pgadmin
		restart: always
		environment:
			PGADMIN_DEFAULT_EMAIL: a@a.com
			PGADMIN_DEFAULT_PASSWORD: admin
		ports:
			- "5050:80"
		depends_on:
			- postgres
```

### Compose ime i servisi

`name: sqlalchemy_ORM` zadaje ime Compose projekta, odnosno grupe resursa kojom se upravlja zajedno. `services` navodi kontejnerske servise. Ime `postgres` je Compose ime servisa; `container_name: postgres_db` zadaje eksplicitno ime kontejnera. To su dva različita imena.

Drugi servis, `pgadmin`, pokreće web alat za administraciju PostgreSQL-a. `depends_on` uspostavlja redosled pokretanja servisa, ali ovaj kratki oblik sam po sebi ne garantuje da je PostgreSQL već spreman da prihvati konekcije kada se pgAdmin pokrene.

### Image, restart i environment

`image` određuje image koji Docker treba da pribavi i pokrene. Ako image nije lokalno dostupan, Docker ga preuzima iz registra, u ovom slučaju Docker Hub-a. Tag kao `latest` bira promenljivu oznaku najnovije verzije.

`restart: always` traži od Docker-a da ponovo pokrene kontejner kada se njegov proces zaustavi, prema restart pravilima Docker-a. Ovo ne zamenjuje nadzor, bekap ili konfiguraciju pogodnu za produkciju.

`environment` prosleđuje promenljive okruženja kontejneru. PostgreSQL zvanični image koristi `POSTGRES_USER`, `POSTGRES_PASSWORD` i `POSTGRES_DB` pri početnoj inicijalizaciji baze. Primer kreira korisnika `postgres` i bazu `inventory`.

U zvaničnom PostgreSQL image-u promenljive za početnu inicijalizaciju primenjuju se kada se inicijalizuje prazan data direktorijum. Promena vrednosti u Compose fajlu kasnije ne znači automatski da će postojeća baza ili korisnik biti izmenjeni.

### Port mapping

```yaml
ports:
	- "5432:5432"
```

Format je `HOST_PORT:CONTAINER_PORT`. Zahtev poslat na port `5432` host računara prosleđuje se na PostgreSQL port `5432` u kontejneru. PostgreSQL podrazumevano sluša na portu `5432`; zato SQLAlchemy klijent pokrenut na host računaru može koristiti `localhost:5432`.

Za pgAdmin je mapping `5050:80`: web interfejs u kontejneru sluša na portu `80`, a sa host računara se otvara na portu `5050`.

## Pokretanje i pregled servisa

Iz direktorijuma u kom se nalazi Compose fajl, uobičajene komande su:

```bash
docker compose up
```

Compose preuzima image-e koji nedostaju, kreira potrebne resurse i pokreće servise. Bez `-d`, komanda ostaje u prvom planu i prikazuje logove; terminal je zauzet dok se procesi izvršavaju. Kada PostgreSQL završi inicijalizaciju, u logu se pojavljuje poruka da je sistem spreman da prihvati konekcije. `Ctrl+C` prekida foreground pokretanje i Compose zaustavlja servise.

Za rad u pozadini koristi se:

```bash
docker compose up -d
```

Opcija `-d` znači detached mode: kontejneri rade u pozadini, a terminal se vraća. Za pregled logova PostgreSQL servisa:

```bash
docker compose logs -f postgres
```

Za zaustavljanje i uklanjanje kontejnera i Compose mreže koristi se:

```bash
docker compose down
```

Ova komanda ne uklanja image-e. Ne dodavati `-v` olako: ta opcija uklanja i Compose volume-e, što može obrisati podatke koji su u njima sačuvani.

## Provera iz `psql`

Može se otvoriti PostgreSQL klijent unutar kontejnera:

```bash
docker compose exec postgres psql -U postgres -d postgres
```

`exec` izvršava komandu u već pokrenutom servisu. Ovde se pokreće `psql`, koristi se korisnik `postgres`, a početna konekcija ide na bazu `postgres`. U `psql` konzoli:

```text
\l
```

`\l` prikazuje baze. Trebalo bi da se vidi i `inventory`, zadat promenljivom `POSTGRES_DB`. Za prelazak na nju:

```text
\c inventory
```

Za izlaz iz `psql` koristi se `\q`.

## pgAdmin i drugi klijenti

pgAdmin je web aplikacija za upravljanje PostgreSQL bazom. U source podešavanju dostupan je na `http://localhost:5050`. Prilikom dodavanja server konekcije iz pgAdmin kontejnera, PostgreSQL hostname je tipično Compose service ime `postgres`, a ne `localhost`: unutar pgAdmin kontejnera, `localhost` označava sam pgAdmin kontejner. Konekcija sa programa pokrenutog direktno na host-u koristi objavljeni port i `localhost`.

DataGrip je druga klijentska aplikacija; nije deo PostgreSQL servera niti Docker Compose-a. Oba alata pomažu da se baze, tabele i upiti pregledaju kroz GUI. Aplikacija će se povezivati direktno na server preko engine URL-a u narednoj lekciji.

## Napomene o source-u i transkriptu

- Transkript prvo demonstrira samo PostgreSQL, a kaže da će pgAdmin biti dodat kasnije. Dostavljeni `docker-compose.yml` već sadrži oba servisa.
- Transkript navodi PostgreSQL `17.2` kao najnoviju verziju u vreme snimanja. To je vremenski vezan podatak, ne trajno važeća informacija.
- Promena Compose `name` nakon što je kontejner već napravljen može dovesti do konflikta jer snapshot zadaje fiksni `container_name`. Uobičajeno je izbeći nepotreban `container_name` kako bi Compose upravljao imenima resursa.
- Transkript koristi Docker Desktop i njegov UI, ali Docker Compose CLI je dovoljan za komande prikazane u ovoj lekciji. Tačan postupak instalacije Docker-a zavisi od operativnog sistema i nije detaljno obrađen u dostavljenom materijalu.

## Savremene i bezbednosne napomene

Sledeće tačke su dodatak za praksu, a ne tvrdnje iz predavanja:

- **Izbegavaj `latest` za ponovljive projekte.** Oznaka može pokazivati na drugu PostgreSQL verziju kasnije, pa razvojno okruženje može neprimetno promeniti ponašanje. Izaberi i zabeleži odgovarajući major tag, pa ga kontroliš kontrolisano.
- **Demo lozinke nisu bezbedne za stvarne sisteme.** Vrednosti `postgres`, `admin` i `a@a.com` iz snapshot-a služe samo za lokalni primer. Ne koristiti ih na javnom serveru; tajne ne čuvati u repozitorijumu.
- **Ograniči izlaganje portova.** Mapping bez IP adrese može objaviti port na više mrežnih interfejsa host-a, zavisno od Docker okruženja. Za lokalni razvoj može se vezati samo za loopback, na primer `127.0.0.1:5432:5432`.
- **Podesi trajno skladište eksplicitno.** Snapshot nema imenovani Compose volume. Za rad sa podacima koje treba sačuvati definiši volume za PostgreSQL data direktorijum i razumi razliku između uklanjanja kontejnera, volume-a i image-a. Za vežbu resetovanja baze pretpostavi da su podaci privremeni.
- **`depends_on` nije health check.** Ako je važno da zavisni servis sačeka da PostgreSQL zaista prihvata konekcije, dodaje se health check i odgovarajuće čekanje, a ne oslanja se samo na redosled pokretanja.

## Pitanja za proveru razumevanja

1. Koja je razlika između image-a i kontejnera?
2. Šta u `5432:5432` označava host port, a šta port kontejnera?
3. Koju početnu bazu kreira `POSTGRES_DB=inventory`?
4. Šta se menja kada se pokrene `docker compose up -d` umesto `docker compose up`?
5. Zašto `depends_on` ne garantuje da je PostgreSQL spreman za konekcije?
6. Zašto promena `POSTGRES_PASSWORD` u Compose fajlu ne mora promeniti lozinku postojeće baze?
7. Zašto `postgres:latest` i demo kredencijali nisu dobar izbor za produkciju?
8. Koji hostname koristi pgAdmin kontejner da dođe do PostgreSQL Compose servisa, i zašto se razlikuje od klijenta na host-u?

## Sažetak

- Docker image je osnova za pokretanje kontejnera; Docker Compose opisuje i pokreće servise zajedno.
- Source definiše PostgreSQL bazu `inventory` na portu `5432` i pgAdmin na portu `5050`.
- `docker compose up` prikazuje logove u prvom planu, dok `docker compose up -d` ostavlja servise u pozadini.
- `psql` može proveriti da li `inventory` postoji; `\l` prikazuje baze, a `\c inventory` se povezuje na nju.
- Compose fajl je lokalni kurski primer: image tag, lozinke, portovi i skladištenje podataka zahtevaju pažljivije podešavanje van izolovane vežbe.
- Ova lekcija priprema PostgreSQL servis; sledeća povezuje Python aplikaciju sa bazom preko SQLAlchemy engine-a.
