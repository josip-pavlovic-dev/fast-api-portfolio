# Lekcija 05: Kreiranje šeme baze podataka

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 33:51–40:05
**Glavne teme:** `Base.metadata`, `create_all()`, DDL, model `Address`, strani ključ ka `User` i SQL logovanje.

Transkript opisuje kod sa slajdova, ali ne sadrži njihove kompletne Python blokove. Primeri su zato rekonstruisani i označavaju SQLAlchemy 2.0 obrasce; nisu doslovan prepis izvornog projekta predavanja.

## Od Python opisa do tabele u bazi

U prethodnoj lekciji deklarativna klasa `User` napravila je SQLAlchemy `Table` objekat i registrovala ga u `Base.metadata`. To je do sada bio opis u Python memoriji. Nije samo definisanje klase napravilo tabelu u SQLite-u.

Da bi opis postao fizička tabela, SQLAlchemy mora da izvrši DDL (`Data Definition Language`), na primer SQL naredbu `CREATE TABLE`. Za deklarativne modele pozivamo `Base.metadata.create_all(...)`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
	pass


class User(Base):
	__tablename__ = "user_account"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str]


engine = create_engine("sqlite://", echo=True)

with engine.begin() as connection:
	Base.metadata.create_all(connection)
```

Tok je sledeći:

1. `DeclarativeBase` daje `Base.metadata`, zajedničko mesto gde se registruju deklarativne tabele.
2. Definicija klase `User` doda opis tabele `user_account` u taj metadata objekat.
3. `create_engine("sqlite://")` pripremi engine za memorijsku SQLite bazu; samo pravljenje engine-a ne šalje DDL.
4. `engine.begin()` uzme konekciju i započne transakcijski kontekst.
5. `Base.metadata.create_all(connection)` pregleda tabele registrovane u metadata objektu i zatraži kreiranje onih koje nedostaju.
6. Pri normalnom izlasku iz `engine.begin()` kontekstni menadžer potvrdi transakciju, u meri u kojoj izabrani dijalekt i drajver podržavaju takvo DDL ponašanje.

`Base.metadata` nije sama baza niti Python rečnik vrednosti u redovima. To je SQLAlchemy `MetaData` objekat; njegova mapa tabela dostupna je preko `Base.metadata.tables`. On opisuje šemu koju SQLAlchemy poznaje.

### Baza podataka naspram šeme/tabela

U ovom naslovu „kreiranje šeme baze“ znači emitovanje DDL-a za tabele i ograničenja. `MetaData.create_all()` ne kreira PostgreSQL ili MySQL bazu/server katalog. U SQLite memorijskom primeru, konekcija otvara memorijsku bazu, a `create_all()` u njoj kreira tabele.

To su odvojeni koraci:

- engine/DBAPI konekcija pristupa konkretnoj bazi;
- `MetaData` opisuje koje tabele želimo;
- `create_all()` kreira nedostajuće tabele u već dostupnoj bazi.

## Šta `create_all()` radi, a šta ne radi?

Podrazumevani `checkfirst=True` traži od SQLAlchemy-ja da proveri da li tabela već postoji pre nego što pokuša da je napravi. Zato možemo ponovo da pozovemo `create_all()`; postojeća tabela se preskače, a tabela koja je naknadno dodata u metadata može da se kreira.

Primer toka iz predavanja:

```python
# U metadata je za sada registrovan samo User.
with engine.begin() as connection:
	Base.metadata.create_all(connection)

# Kasnije definišemo Address; Base.metadata sada poznaje User i Address.
# Drugi poziv proverava postojeće tabele i pravi onu koja nedostaje.
with engine.begin() as connection:
	Base.metadata.create_all(connection)
```

Drugi poziv ne pravi ponovo `user_account`; `create_all()` podrazumevano proverava postojeće tabele. Ali ovo nije alat za migracije:

- ne dodaje novu kolonu postojećoj tabeli;
- ne menja tip ili nullable pravilo postojeće kolone;
- ne prepravlja ograničenja postojeće tabele;
- ne briše tabelu ili njene redove.

Za promene postojeće šeme koristi se migracija, na primer Alembic, ili nameran ručni DDL. Model metadata i fizička šema mogu se razići ako izmeniš model, a ne primeniš odgovarajuću migraciju.

Poziv će kreirati samo modele koji su već učitani i registrovani u `Base.metadata`. Ako definicija klase u drugom modulu nikada nije uvezena, SQLAlchemy ne može da kreira tabelu za koju ne zna.

## Transakcija i DDL

Predavač koristi `engine.begin()` i naglašava da DDL treba tretirati kao rad koji treba jasno završiti i potvrditi. To je dobar opšti obrazac za SQLAlchemy:

```python
with engine.begin() as connection:
	Base.metadata.create_all(connection)
```

Normalan izlazak potvrđuje transakcijski blok; izuzetak koji izađe iz bloka vodi do rollback-a tamo gde backend podržava rollback za dati DDL. DDL transakcijsko ponašanje nije isto kod svih baza i drajvera. Transkript posebno napominje SQLite/pysqlite detalj: ponašanje samog SQLite-a i DBAPI drajvera oko implicitnog početka ili potvrde DDL-a može da utiče na to da li je DDL zaista vraćiv. Zato je `engine.begin()` preporučen način da namera transakcije bude jasna, ali ne treba pretpostaviti da svaki backend može identično da poništi već izvršeni DDL.

SQLAlchemy 2.0 ne potvrđuje automatski obične upise umesto nas. Uobičajeno je jasno označiti granice kroz `engine.begin()` ili koristiti `engine.connect()` sa eksplicitnim `commit()`. Driver-level autocommit je poseban režim za specifične potrebe, a ne zamena za standardni transakcijski obrazac.

## Dodavanje `Address` tabele i stranog ključa

Predavač dodaje drugu deklarativnu klasu `Address`, koja predstavlja kontakt adresu korisnika. Jedan korisnik može imati više adresa. Svaki red u `address` zato sadrži `user_id` koji upućuje na ID reda u `user_account`.

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class Address(Base):
	__tablename__ = "address"

	id: Mapped[int] = mapped_column(primary_key=True)
	email_address: Mapped[str] = mapped_column(String(100), nullable=False)
	user_id: Mapped[int] = mapped_column(
		ForeignKey("user_account.id"),
		nullable=False,
	)
```

`ForeignKey("user_account.id")` navodi cilj u obliku `ime_tabele.ime_kolone`. Cilj je ime SQL tabele `user_account` i kolone `id`, a ne Python ime klase `User`.

Ovde postoje dva odvojena pravila:

- `ForeignKey(...)` kaže da `address.user_id` referencira `user_account.id`.
- `nullable=False` kaže da svaki `Address` red mora imati neku vrednost `user_id`.

Strani ključ i obaveznost nisu ista stvar. FK sam po sebi može biti nullable; tada bi `NULL` značio da taj red trenutno nema roditeljski ID. U modelu iz primera korisnička adresa mora biti vezana za korisnika, pa je kolona obavezna.

### Odnos u oba smera

Na nivou relacione šeme, FK je u tabeli na strani „više“:

```text
user_account.id  1 ---- N  address.user_id
```

Iz perspektive jednog `Address` reda, veza prema `User` redu je many-to-one: više adresa može pokazivati na istog korisnika. Iz perspektive `User` reda, veza ka adresama je one-to-many.

Ovaj transkript dodaje FK kolonu i constraint, ali ne prikazuje ORM `relationship()` atribute. Zato model još nema Python putanje kao `address.user` ili `user.addresses`. `ForeignKey` definiše relaciju u SQL šemi; `relationship()` zasebno definiše ORM navigaciju između objekata. Ne treba zaključiti da se navigacija automatski pojavljuje samo zato što je FK dodat.

Jednostavan integer primarni ključ sa jednom kolonom je uobičajen za ovakve primere, ali nije jedina mogućnost. Tabela može imati složeni primarni ključ. U ovom modelu `Address.user_id` referencira `User.id`; tipovi referentne i FK kolone treba da budu kompatibilni prema pravilima ciljane baze.

## Kreiranje obe tabele

Kada su obe klase definisane i učitane, njihov opis se nalazi u istom `Base.metadata` objektu:

```python
with engine.begin() as connection:
	Base.metadata.create_all(connection)
```

SQLAlchemy poznaje zavisnost `address` od `user_account` kroz `ForeignKey` i može da uzme tu zavisnost u obzir pri redosledu DDL operacija. Ako su obe tabele nove, roditeljska tabela se kreira pre tabele koja na nju referencira.

Uobičajeni obrazac za aplikaciju je da prvo uveze sve module sa modelima, pa zatim pokrene jednu operaciju nad zajedničkim metadata objektom. Primer u predavanju poziva `create_all()` dva puta samo da pokaže da se nova tabela može dodati u već postojeći metadata/SQLite kontekst, a da se već kreirana tabela preskoči.

## Važna SQLite napomena: constraint naspram enforcement-a

Kada SQLAlchemy sastavi `Address.__table__`, strani ključ ulazi u njen DDL opis. To znači da SQLAlchemy može da emituje constraint u `CREATE TABLE`. Ali kod SQLite-a to samo po sebi ne garantuje da će svaki nevažeći FK upis biti odbijen: SQLite enforcement stranih ključeva je po podrazumevanom podešavanju isključen za konekciju, osim ako je biblioteka ili aplikacija drugačije konfigurisala.

Za test koji stvarno proverava FK, uključi `PRAGMA foreign_keys=ON` na svakoj DBAPI konekciji. Jedan SQLAlchemy obrazac je connect event:

```python
from sqlalchemy import event


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
	cursor = dbapi_connection.cursor()
	cursor.execute("PRAGMA foreign_keys=ON")
	cursor.close()
```

Listener mora biti registrovan pre nego što engine otvori konekciju. Možeš proveriti podešavanje ovako:

```python
with engine.connect() as connection:
	assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
```

Zatim pokušaj da upišeš adresu sa `user_id` vrednošću koja ne postoji. Uz uključen enforcement SQLite treba da odbije INSERT; bez njega constraint može da bude prisutan u DDL-u, ali testni upis ipak prođe. Ovo je bitno i za playground: provera da se model učitao ili da je `create_all()` prošao nije dokaz da baza zaista sprovodi FK.

## SQL logovanje

Predavač prikazuje dve upotrebe standardnog Python logging sistema.

### Brzo uključivanje preko `echo=True`

```python
engine = create_engine("sqlite://", echo=True)
```

Ovo je zgodan prečac za lokalno učenje i otklanjanje grešaka. SQLAlchemy ispisuje SQL koji izvršava, vrednosti bind parametara i informacije o transakcijama. Vrednosti u logu mogu biti osetljive, zato `echo=True` nije nešto što treba olako uključiti u produkciji.

### Podešavanje logger-a u Python logging sistemu

Za upravljanje standardnim logging konfiguracijama može se podesiti logger `sqlalchemy.engine`:

```python
import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

`echo=True` je praktičan za brzo lokalno proveravanje. Konfiguracija standardnog logging sistema daje veću kontrolu nad handler-ima, formatom i nivoima. Uobičajeno je izabrati jedan način konfiguracije; istovremeno uključivanje oba može dovesti do dupliranih poruka, zavisno od logging podešavanja.

## Primer kao celina

Sledeći primer je rekonstrukcija ideje sa slajdova. Namerno prikazuje dve faze: prvo se kreira `user_account`, pa se posle deklarisanja `Address` ponovo pozove `create_all()` da se napravi nedostajuća tabela.

```python
from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
	pass


class User(Base):
	__tablename__ = "user_account"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(30), nullable=False)


engine = create_engine("sqlite://", echo=True)

with engine.begin() as connection:
	Base.metadata.create_all(connection)


class Address(Base):
	__tablename__ = "address"

	id: Mapped[int] = mapped_column(primary_key=True)
	email_address: Mapped[str] = mapped_column(String(100), nullable=False)
	user_id: Mapped[int] = mapped_column(
		ForeignKey("user_account.id"),
		nullable=False,
	)


with engine.begin() as connection:
	Base.metadata.create_all(connection)
```

Posle prvog poziva `Base.metadata` sadrži samo tabelu `user_account`, pa se ona kreira. Definisanje `Address` klase dodaje i `address` u isti `Base.metadata`. Drugi poziv proverava obe tabele: postojeću preskače i kreira novu.

Ovaj primer ne unosi nijedan red. Njegov posao je da definiše Python metadata i zatraži DDL za nedostajuće tabele. INSERT i SELECT nad tabelama dolaze u narednim lekcijama.

## Šta je ovde specifično za SQLAlchemy 2.0?

- Deklarativni model koristi `DeclarativeBase`, `Mapped[...]` i `mapped_column()`.
- Metadata model može se proslediti SQLAlchemy `Connection` objektu.
- `engine.begin()` daje jasno ograničen transakcijski blok za operacije šeme.
- SQLAlchemy 2.0 ne dodaje raniji library-level autocommit; završetak transakcijskog bloka ostaje eksplicitan.

Osnovni poziv `Base.metadata.create_all(...)` postoji i u ranijim SQLAlchemy verzijama. Ovde je bitno kako se uklapa sa tipizovanim deklarativnim modelom i savremenim transakcijskim obrascem.

## Sažetak za ponavljanje

- ORM klasa registruje opis tabele u `Base.metadata`; to samo po sebi ne izvršava `CREATE TABLE`.
- `Base.metadata.create_all(connection)` šalje DDL za tabele koje nedostaju.
- Podrazumevani `checkfirst=True` proverava postojeće tabele i preskače ih.
- `create_all()` ne menja definiciju postojeće tabele i nije zamena za migracije.
- Svi modeli moraju biti učitani da bi njihove tabele bile registrovane.
- `ForeignKey("user_account.id")` dodaje šemsku vezu od `address.user_id` ka `user_account.id`.
- `nullable=False` je odvojeno pravilo koje zabranjuje da FK kolona bude `NULL`.
- FK constraint ne stvara ORM `relationship()` navigaciju.
- SQLite može imati FK u DDL-u, a da ih ne sprovodi; uključi `PRAGMA foreign_keys=ON` na svakoj konekciji za pouzdan test.
- `echo=True` brzo prikazuje SQL i transakcijske logove; standardni `sqlalchemy.engine` logger nudi veću konfigurabilnost.

## Vežbe za playground

Radi u novom fajlu u `playground/sqlalchemy_2/` i koristi postojeći root `.venv`.

1. Napravi samo `User`, pozovi `create_all()`, pa preko `inspect(engine).get_table_names()` potvrdi da je tabela nastala.
2. Posle prvog poziva definiši `Address` sa `ForeignKey("user_account.id")`, ponovo pozovi `create_all()` i proveri da postoje obe tabele.
3. Pozovi `create_all()` još jednom i posmatraj `echo=True`: postojeća tabela se proverava, ali se ne kreira ponovo.
4. Uključi SQLite FK enforcement event listener-om i proveri `PRAGMA foreign_keys` vrednost.
5. Pokušaj INSERT adrese sa nepostojećim `user_id`; očekuj `IntegrityError`, uradi rollback ako koristiš ručno upravljanu sesiju/konekciju, pa probaj sa stvarnim korisnikom.
6. Napravi Core `insert()` nad `Address.__table__` i uporedi ga sa dodavanjem ORM objekta tek pošto stigneš do lekcija o INSERT-u.
