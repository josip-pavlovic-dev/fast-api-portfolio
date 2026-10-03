# Lekcija 3: Kreiranje SQLAlchemy engine-a

## Cilj lekcije

PostgreSQL server je sada dostupan u Docker-u. Sledeći korak je da Python aplikacija može da komunicira sa njim. U SQLAlchemy-ju se za to konfiguriše **engine**: centralni objekat koji povezuje SQLAlchemy dijalekt, Python DBAPI drajver i pool konekcija.

Ova lekcija obrađuje engine, PostgreSQL drajver i URL konekcije. ORM sesije se nalaze u source fajlu `db.py`, ali su tema sledeće lekcije.

## Uloga engine-a

Engine je aplikacioni interfejs prema određenoj bazi. SQLAlchemy ga koristi da:

- zna koji dijalekt baze treba da koristi;
- koristi izabrani Python drajver za komunikaciju sa DBMS-om;
- pribavlja i vraća konekcije kroz pool;
- šalje SQL naredbe kada kod zatraži konekciju ili izvrši upit.

Engine nije ORM sesija i nije jedna stalno otvorena konekcija. Obično se napravi jedan engine za datu konfiguraciju baze u jednom procesu aplikacije, a engine upravlja pool-om iz kog se konekcije pozajmljuju i u koji se vraćaju.

Kada se konekcija koristi u `with` bloku, po završetku se zatvara SQLAlchemy `Connection` objekat i konekcija se tipično vraća u pool; to ne mora značiti da je fizička mrežna konekcija svaki put uništena.

## Dijalekt i DBAPI drajver

Za komunikaciju sa PostgreSQL-om potrebna su dva povezana dela:

- **Dijalekt** opisuje SQLAlchemy-jevo razumevanje konkretne baze, njenih tipova, SQL sintakse i ponašanja.
- **Drajver** je Python DBAPI implementacija koja prenosi zahteve između SQLAlchemy-ja i PostgreSQL-a.

Česti PostgreSQL drajveri su `psycopg2` (paket `psycopg2-binary`), `psycopg` verzije 3 i `pg8000`. Transkript pominje i `asyncpg`; on se koristi za asinhroni rad i nije samo zamena koju možemo staviti u sinhroni `create_engine()` poziv bez drugih promena.

Paket instaliran u aktivnom Python okruženju mora odgovarati drajveru navedenom ili podrazumevanom u URL-u. Docker pokreće PostgreSQL server; Python drajver se instalira u Python okruženje aplikacije.

## URL konekcije

SQLAlchemy URL sadrži podatke koji su potrebni za nalaženje baze i prijavu. Uobičajeni oblik je:

```text
dialect+driver://username:password@host:port/database
```

Delovi znače:

- `dialect`: tip baze, ovde `postgresql`;
- `driver`: Python DBAPI implementacija, na primer `psycopg2`;
- `username` i `password`: kredencijali za PostgreSQL korisnika;
- `host`: adresa servera;
- `port`: port na kom je server dostupan;
- `database`: ime baze kojoj se povezujemo.

Primer eksplicitnog URL-a:

```text
postgresql+psycopg2://postgres:postgres@localhost:5432/inventory
```

Kurski source koristi kraći oblik:

```text
postgresql://postgres:postgres@localhost:5432/inventory
```

Kada se izostavi `+driver`, SQLAlchemy bira podrazumevani PostgreSQL drajver, u ovom okruženju `psycopg2`. Zapis bez eksplicitnog drajvera zato ne znači da Python-u nije potreban drajver.

### Host i port u ovom kursu

Compose fajl objavljuje kontejnerski PostgreSQL port `5432` na host portu `5432`. Zato Python program koji radi na host-u/WSL okruženju koristi `localhost:5432`. Ime baze `inventory` i kredencijali u primeru odgovaraju lokalnoj razvojnoj Compose konfiguraciji.

Ako se sama Python aplikacija kasnije pokrene kao Compose servis u istoj Compose mreži, `localhost` bi označavao taj Python kontejner, ne PostgreSQL kontejner. Tada se kao host obično koristi Compose ime servisa, ovde `postgres`. Host zavisi od mesta sa kog klijent pokušava da se poveže.

## Kreiranje engine-a

Kurski primer u `db.py`:

```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/inventory"

engine = create_engine(DATABASE_URL)
```

`create_engine()` pravi i vraća SQLAlchemy `Engine` konfigurisan datim URL-om. On priprema dijalekt i pool, ali po pravilu ne otvara odmah konekciju ka serveru. Prva stvarna konekcija nastaje kada kod prvi put zatraži konekciju ili izvrši SQL operaciju.

Zbog toga uspešno izvršavanje `create_engine()` samo po sebi ne dokazuje da su PostgreSQL server, mrežna adresa, korisnik, lozinka i ime baze ispravni. Da bi se proverila stvarna veza, engine mora da se koristi.

Primer minimalne provere:

```python
from sqlalchemy import create_engine, text

engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
	result = connection.execute(text("SELECT 1"))
	print(result.scalar_one())
```

Ako veza uspe, primer ispisuje `1`. `text()` eksplicitno označava SQL tekst koji se izvršava preko SQLAlchemy-ja. `with` obezbeđuje da se `Connection` po završetku pravilno zatvori i resurs vrati pool-u.

Ova provera se ne izvršava automatski pri definisanju engine-a; u transkriptu je engine postavljen kao osnovna konfiguracija, a ne demonstriran pun tok upita.

## Connection pool i konekcije

Otvaranje fizičke mrežne konekcije ima cenu. Engine uobičajeno koristi pool da bi već otvorenu konekciju mogao ponovo da pozajmi sledećoj operaciji. Kada se koristi SQLAlchemy `Connection`, tačno trajanje i vraćanje resursa zavise od načina korišćenja; zato konekcije treba zatvarati kontekstnim menadžerom ili drugim odgovarajućim obrascem.

Engine omogućava izvršavanje SQL-a, ali je važno precizno razdvojiti odgovornosti:

- engine obezbeđuje konfiguraciju, pool i pristup konekcijama;
- `Connection` predstavlja korišćenu konekciju i može upravljati transakcijom;
- ORM `Session` upravlja ORM objektima i transakcijama u ORM radu.

Transkript engine opisuje kao objekat koji upravlja konekcijama i transakcijama. U praksi se transakcione granice eksplicitno koriste kroz `Connection` ili `Session`; engine ih ne zamenjuje.

## Opcioni parametri

### `echo`

```python
engine = create_engine(DATABASE_URL, echo=True)
```

Sa `echo=True`, SQLAlchemy ispisuje SQL naredbe koje šalje i povezane informacije. To pomaže pri učenju i otklanjanju grešaka, ali može stvoriti mnogo logova. U njima se mogu pojaviti osetljivi podaci, pa `echo=True` uglavnom treba isključiti van lokalnog razvoja.

### `connect_args`

```python
engine = create_engine(
	DATABASE_URL,
	connect_args={"application_name": "learning_app"},
)
```

`connect_args` prosleđuje dodatne opcije Python drajveru prilikom otvaranja konekcije. `application_name` je PostgreSQL/libpq opcija koja se koristi sa `psycopg2` i nekim drugim kompatibilnim drajverima. Tip, naziv i značenje opcija zavise od izabranog drajvera i DBMS-a. SSL/TLS podešavanja su jedan mogući primer, ali zahtevaju usklađenu konfiguraciju servera i klijenta; ne postoji jedna univerzalna vrednost koja je bezbedna za svako okruženje.

## Bezbedno rukovanje URL-om

Kurski URL sadrži demo korisničko ime i lozinku direktno u Python fajlu. To je prihvatljivo samo kao lokalni primer. U stvarnom projektu kredencijale ne treba commit-ovati u source kontrolu; čuvaju se u konfiguraciji okruženja ili namenskom sistemu za tajne.

Posebni znakovi u korisničkom imenu ili lozinci, kao što su `@`, `/` ili `:`, imaju značenje u URL sintaksi. Ručno sastavljen URL tada mora pravilno da ih kodira. SQLAlchemy `URL.create()` prima delove odvojeno i izbegava ručno URL-kodiranje:

```python
import os

from sqlalchemy import URL, create_engine

database_url = URL.create(
	"postgresql+psycopg2",
	username=os.environ["DB_USER"],
	password=os.environ["DB_PASSWORD"],
	host=os.environ.get("DB_HOST", "localhost"),
	port=int(os.environ.get("DB_PORT", "5432")),
	database=os.environ.get("DB_NAME", "inventory"),
)

engine = create_engine(database_url)
```

Ovo je dodatni obrazac za praksu, nije kod iz predavanja. On pretpostavlja da su promenljive okruženja unapred podešene i ne zamenjuje upravljanje tajnama u produkciji.

## Sinhroni i asinhroni drajveri

Primer kursa je sinhroni: koristi `create_engine()` i u source zahteva `psycopg2-binary`. `pg8000` je još jedna sinhrona alternativa, uz odgovarajući URL driver identifikator. `asyncpg` se koristi sa asinhronim SQLAlchemy API-jem, kao što su `create_async_engine()` i asinhroni rad sa sesijama. Asinhroni URL obično navodi `postgresql+asyncpg://...`.

Zato savet iz transkripta da se proba `asyncpg` treba razumeti kao drugačiji pristup povezivanju, ne kao instaliranje zamenskog paketa bez promene aplikacionog koda. Asinhroni rad nije potreban za primer ove lekcije.

## Granica prema lekciji 04

Source `db.py` sadrži i sledeće:

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

Ovaj deo pravi fabriku ORM sesija vezanu za engine, ali `SessionLocal` nije engine i ne uspostavlja samostalno stalnu konekciju. Rad sa sesijama, `autoflush`, `commit`, `rollback` i zatvaranjem pripada lekciji 04. Ovde je bitan samo odnos: engine je izvor konfiguracije konekcija na kom se sesije zasnivaju.

## Pitanja za proveru razumevanja

1. Koja je razlika između SQLAlchemy dijalekta i Python DBAPI drajvera?
2. Šta znače `postgresql`, `psycopg2`, `localhost`, `5432` i `inventory` u URL-u?
3. Zašto `create_engine()` može uspešno da se izvrši iako server nije dostupan?
4. Šta se dešava sa konekcijom kada se koristi `with engine.connect()`?
5. Koju vrstu dijagnostike omogućava `echo=True`, i zašto može biti rizičan van razvoja?
6. Zašto `asyncpg` nije direktna zamena za `psycopg2` u sinhronom primeru?
7. Koji deo source `db.py` pripada sledećoj lekciji?

## Sažetak

- Engine je SQLAlchemy-jeva konfigurisana veza ka DBMS-u, uključujući dijalekt, drajver i pool konekcija.
- PostgreSQL URL sadrži dialect, opcioni driver, kredencijale, host, port i ime baze.
- Source koristi `postgresql://...`; uz instalirani `psycopg2-binary`, SQLAlchemy bira podrazumevani PostgreSQL drajver `psycopg2`.
- `create_engine()` je lenj: priprema engine, ali stvarna konekcija se obično otvara tek kada se engine upotrebi.
- `echo` pomaže pri debugovanju, dok je `connect_args` namenjen opcijama konkretnog drajvera.
- Tajne ne treba čuvati u source fajlu; sinhroni i asinhroni drajveri zahtevaju odgovarajuće API-je.
- `sessionmaker()` se nalazi u istom source fajlu, ali se obrađuje u lekciji 04.
