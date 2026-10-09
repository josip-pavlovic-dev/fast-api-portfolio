# Lekcija 10: ORM `Session` i Unit of Work

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 1:22:38–1:43:53
**Glavne teme:** `Session`, `sessionmaker`, ORM rezultati, `add()`, pending/persistent stanja, flush, identity map i transakcije.

Ovo je završna lekcija u ovom nizu i prelazi sa Core obrasca „napiši iskaz pa ga izvrši“ na ORM obrazac „promeni Python objekat, a ORM uskladi promenu sa bazom“. Transkript na kraju tek počinje da najavljuje dirty UPDATE; ceo primer izmene objekta nije prikazan. Taj deo ispod je jasno označen kao dopuna.

## Core i ORM: dva načina rada

U prethodnim lekcijama direktno smo opisivali SQL iskaze:

```python
connection.execute(insert(User), parameters)
```

Ovo je statement-oriented način rada: aplikacija konstruiše SQL iskaz, prosleđuje parametre i odlučuje kada se transakcija potvrđuje.

ORM dodaje object-oriented način rada:

```python
user = User(name="spongebob", fullname="SpongeBob SquarePants")
session.add(user)
```

Ovde aplikacija menja stanje Python objekta i kaže `Session`-u da ga prati. ORM kasnije određuje koji SQL `INSERT`, `UPDATE` ili `DELETE` treba poslati da bi se stanje objekta uskladilo sa bazom.

ORM ne uklanja SQL. On automatizuje njegovo sastavljanje i praćenje stanja objekata. Ispod ORM-a i dalje postoje tabele, SQL iskazi, konekcije i transakcije.

## Šta je `Session`?

`Session` je ORM-ov glavni objekat za rad sa mapiranim Python objektima i transakcijom. Pojednostavljeno, kao što je `Connection` glavni objekat za Core izvršavanje, tako je `Session` centralni objekat za ORM rad.

Ova analogija ne znači da su isti:

- `Engine` upravlja dijalektom i pool-om DBAPI konekcija.
- `Connection` izvršava Core SQL iskaze preko konkretne konekcije.
- `Session` prati ORM objekte, koordinira flush i upravlja ORM transakcijskim radom.
- Kada joj zatreba baza, `Session` uzima `Connection` od `Engine`-a.

`Session` može izvršavati i Core iskaze. Razlika je u tome da se ORM-specifično mapiranje rezultata i praćenje objekata primenjuje kada izaberemo ORM entitete i koristimo ORM putanju.

## `sessionmaker`: fabrika sesija

Transkript koristi `sessionmaker` kao dugotrajniju aplikacionu fabriku koja je vezana za engine:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite://")
SessionFactory = sessionmaker(engine)
```

`SessionFactory` je konfiguracija/fabrika, a ne jedna otvorena `Session`. Kada je potrebna jedinica ORM rada, fabrika pravi novu sesiju:

```python
session = SessionFactory()
```

U aplikaciji su `Engine` i `SessionFactory` obično dugotrajniji, application-scoped objekti. Sama `Session` je kratkotrajan objekat za jednu operaciju ili zahtev. Ne pravimo nov `Engine` i novu fabriku za svaki upit, i ne delimo jednu aktivnu `Session` između istovremenih niti ili zahteva.

## Lenjo povezivanje i transakcija

Pravljenje engine-a, fabrike i same sesije obično ne otvara odmah fizičku vezu sa bazom. `Session` traži konekciju kada prvi put mora da izvrši SQL, na primer pri `flush()`-u, SELECT-u ili kada eksplicitno tražimo `session.connection()`.

`session.connection()` je koristan za dijagnostiku ili specijalne slučajeve, ali ORM kod obično ne mora direktno da uzima konekciju: poziva ORM metode nad sesijom.

Transkript pravi jednu važnu nijansu. `Session` počinje da prati svoj transakcijski kontekst kada počne rad; stvarni DBAPI connection može se uzeti tek onda kada je stvarno potreban. U logu `BEGIN (implicit)` je informacija o SQLAlchemy transakcijskom stanju i ne mora da znači da je poslat doslovni tekst `BEGIN`.

Jedna `Session` upravlja svojim ORM radom u transakcijskom kontekstu. Za upise koristimo eksplicitan `commit()` ili transakcijski kontekst, a ne očekujemo da ORM sam trajno potvrdi promene.

## Bezbedni obrasci životnog veka

### Sesija kao kontekstni menadžer

```python
with SessionFactory() as session:
	users = session.scalars(select(User)).all()
```

Izlazak iz `with` bloka zatvara sesiju i oslobađa njene resurse. Ovaj obrazac sam po sebi ne potvrđuje upise. Ako postoji otvorena, nepotvrđena transakcija, zatvaranje sesije je ne čuva; transakcija se čisti/poništava.

### Transakcijski blok preko fabrike

Za jednu celovitu jedinicu rada zgodno je:

```python
with SessionFactory.begin() as session:
	session.add(User(name="spongebob", fullname="SpongeBob SquarePants"))
```

`SessionFactory.begin()` napravi sesiju i transakciju. Pri normalnom izlasku blok potvrđuje transakciju i zatvara sesiju. Ako iz bloka izađe izuzetak, transakcija se poništava, a sesija se zatvara.

### Eksplicitni `commit()` ili `rollback()`

Kada nam treba veća kontrola nad trenutkom potvrde:

```python
with SessionFactory() as session:
	session.add(User(name="spongebob", fullname="SpongeBob SquarePants"))
	session.commit()
```

`commit()` prvo obavlja potrebni flush, a zatim potvrđuje transakciju. Ako posao treba odbaciti, pozivamo `rollback()`.

Ako flush ili commit padne, sesija mora da se vrati u upotrebljivo transakcijsko stanje pozivom `rollback()` pre nego što nastavimo da je koristimo. Transakcijski kontekst `with SessionFactory.begin()` ovo često pojednostavljuje, jer rollback radi kada se izuzetak propusti iz bloka.

## `Session.execute()` i `Session.scalars()`

`Session.execute()` prima SELECT iskaze kao što smo ih koristili u Core-u, ali rezultat može uključiti ORM entitete:

```python
statement = select(User).where(User.name == "spongebob")

with SessionFactory() as session:
	result = session.execute(statement)
	row = result.one()
	user = row[0]
```

`Session.execute(select(User))` vraća rezultat čiji red sadrži `User` objekat. Pošto je najčešći slučaj da želimo baš taj objekat, koristimo `scalars()` da uzmemo prvu izabranu vrednost svakog reda:

```python
with SessionFactory() as session:
	user = session.scalars(statement).one()
```

Ovde `user` je ORM instanca. `Session.scalars()` je zgodan način rada za SELECT koji bira jedan ORM entitet ili jednu kolonu. Ako SELECT bira više kolona, `scalars()` vraća samo prvu izabranu vrednost po redu; za sve kolone koristimo `execute()` i `Row` rezultat.

Važna razlika u odnosu na prethodnu lekciju:

```python
connection.execute(select(User))
session.execute(select(User))
session.scalars(select(User))
```

`Connection` izvršava iskaz u Core stilu i vraća `Row` sa kolonama. `Session.execute()` koristi ORM kontekst, pa `User` entitet postaje element reda. `Session.scalars()` izdvaja taj entitet iz prvog elementa svakog reda.

## Unit of Work: objekti se prate, SQL se odlaže

**Unit of Work** je obrazac u kom `Session` prati promene objekata i kasnije ih pretvara u SQL operacije. Umesto da aplikacija odmah šalje INSERT svaki put kada napravi instancu, sesija prikuplja nameravane izmene:

```python
user = User(name="spongebob", fullname="SpongeBob SquarePants")
session.add(user)
```

Nakon `add()`, objekat je pending. To znači da je pridružen sesiji i da sesija planira INSERT, ali SQL možda još nije poslat.

```python
user in session.new
```

Ova provera je `True` dok je objekat pending. Ključna razlika: `Session.add()` registruje objekat za praćenje; `flush()` šalje SQL.

### Flush

Flush usklađuje trenutno praćene promene sa bazom u okviru aktivne transakcije:

- pending objekti vode do `INSERT`-a;
- izmenjeni persistent objekti vode do `UPDATE`-a;
- objekti označeni za brisanje vode do `DELETE`-a.

```python
session.add(user)
session.flush()
```

Posle flush-a SQL je izvršen u trenutnoj transakciji, pa baza može da dodeli primarni ključ ili serverski default. Međutim, transakcija još nije potvrđena:

- `flush()` šalje SQL, ali ne radi `COMMIT`;
- `commit()` po pravilu prvo flush-uje pa potvrdi transakciju;
- `rollback()` može poništiti flush-ovane promene koje nisu commit-ovane.

SQLAlchemy automatski flush-uje u važnim trenucima, na primer pre ORM SELECT-a koji treba da vidi te promene i pre commit-a. Ručni `session.flush()` se koristi kada program treba vrednost koju baza dodeli pre kraja transakcije ili kada želimo eksplicitno da pokažemo trenutak slanja SQL-a.

## Stanja ORM objekta

Transkript posebno prikazuje pending i persistent stanja. Koristan širi pregled je:

| Stanje     | Značenje                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------ |
| Transient  | Python objekat postoji, ali nije dodat u sesiju i nema ORM vezu sa redom u bazi.                 |
| Pending    | Objekat je dodat u sesiju i čeka INSERT pri flush-u.                                             |
| Persistent | Objekat pripada sesiji i odgovarajući red postoji ili je upravo upisan u trenutnoj transakciji.  |
| Deleted    | Objekat je označen za brisanje; DELETE se izvršava pri flush-u.                                  |
| Detached   | Objekat više nije povezan sa sesijom; Python vrednosti mogu ostati, ali sesija ga više ne prati. |

Ovo su ORM koncepti. Nemoj izjednačiti „persistent“ sa „već commit-ovan“: red može postojati u trenutnoj transakciji posle flush-a, a ta transakcija kasnije može biti rollback-ovana.

## Identity map: jedna instanca po identitetu u sesiji

Sesija održava identity map, mapu koja povezuje ORM klasu i primarni ključ sa odgovarajućom Python instancom. Ako učitamo korisnika sa ID-jem 1, a zatim ga ponovo izaberemo u istoj sesiji, SQLAlchemy vraća istu instancu iz identity map-a:

```python
with SessionFactory() as session:
	user = session.get(User, 1)
	user_again = session.scalars(
		select(User).where(User.id == 1)
	).one()

	assert user_again is user
```

Identity map sprečava da jedna sesija istovremeno ima dve odvojene `User` Python instance koje predstavljaju isti ORM identitet. Tako se dosledno prati izmena objekta koju je aplikacija već napravila.

Ponovljeni SELECT i dalje može da se izvrši; identity map obezbeđuje da učitani identitet odgovara postojećoj instanci. To nije opšti keš svih query rezultata niti garancija da sesija uvek vidi izmene koje su drugi klijenti napravili u bazi.

## ORM objekat i generisane vrednosti

Kada flush izvrši INSERT, baza može da generiše primarni ključ i `server_default` vrednosti. SQLAlchemy ih, kada ih dijalekt može vratiti ili naknadno učitati, sinhronizuje sa ORM objektom:

```python
session.add(user)
session.flush()

print(user.id)
print(user.created_at)
```

Pre flush-a `user.id` obično nema dodeljenu vrednost. Posle flush-a ID je često dostupan odmah; generisani server defaults zavise od dijalekta i `RETURNING` podrške, pa proveravaj ciljnu bazu ako logika mora da ih koristi pre commit-a.

U SQLite primeru sa `server_default=func.now()` SQLAlchemy 2.0.38 može da dobije timestamp nakon INSERT-a. To ne znači da svaki dijalekt vraća sve default vrednosti na isti način.

## Dopuna: izmena persistent objekta i dirty stanje

Transkript na kraju najavljuje da će menjati Python objekte i pokazati UPDATE, ali se snimak prekida pre demonstracije. Sledeći mali primer je dopuna:

```python
with SessionFactory.begin() as session:
	user = session.get(User, 1)
	assert user is not None

	user.fullname = "SpongeBob SquarePants"
	assert user in session.dirty

	session.flush()
```

ORM pamti prvobitno mapirano stanje i vrednost koju smo promenili. Pri flush-u izračunava koje mapirane vrednosti su se promenile i generiše UPDATE. Sama Python dodela još ne izvršava SQL; SQL se šalje pri flush-u, autoflush događaju ili commit-u.

Ako izmena ne treba da bude sačuvana, pozovi rollback ili pusti grešku da izađe iz `SessionFactory.begin()` bloka. Unit of Work omogućava da više novih, izmenjenih i obrisanih objekata budu usklađeni u jednoj transakciji.

### Commit i expiration

Po podrazumevanom podešavanju ORM sesija može da istekne (`expire`) svoje persistent objekte posle commit-a, da bi se njihove vrednosti pri sledećem pristupu ponovo sinhronizovale sa bazom. Dok je sesija otvorena, čitanje isteklog atributa može izazvati SELECT. Posle zatvaranja sesije, odvojeni (`detached`) objekat više ne može od te sesije da učita istekle podatke.

Ovo je jedan od razloga da podatke koji su potrebni izvan sesije vratiš u obliku koji je predviđen za aplikaciju ili učitaš potrebna polja pre zatvaranja. `expire_on_commit=False` postoji, ali je podešavanje ponašanja koje treba birati svesno, ne podrazumevani popravak za sve detached objekte.

## Praktičan obrazac za aplikaciju

Uobičajena podela životnog veka je:

- jedan `Engine` i jedna `sessionmaker` fabrika po konfiguraciji baze, dugog životnog veka;
- nova `Session` za jednu aplikacionu operaciju, zahtev ili jedinicu rada;
- transakcija se jasno potvrdi ili poništi;
- sesija se zatvori deterministički pomoću kontekstnog menadžera.

```python
def create_user(SessionFactory):
	with SessionFactory.begin() as session:
		user = User(
			name="spongebob",
			fullname="SpongeBob SquarePants",
		)
		session.add(user)
		session.flush()
		return user.id
```

Za produkcioni servis često ne vraćamo ORM instancu direktno iz zatvorenog session scope-a; umesto toga napravimo DTO/response vrednosti dok su potrebna polja dostupna. Primer ovde ilustruje transakcijsku granicu, a ne kompletan FastAPI obrazac.

Nemoj praviti globalnu aktivnu `Session` koju dele svi zahtevi. Deljeni objekat je obično `Engine`/fabrika, dok je `Session` ograničena na jednu jedinicu rada i nije namenjena istovremenom korišćenju iz više niti ili task-ova.

## Sažetak za ponavljanje

- Core eksplicitno izvršava iskaze; ORM `Session` prati objekte i organizuje njihovo čitanje i upis.
- `sessionmaker(engine)` je dugotrajnija fabrika; pojedinačna `Session` je kratkotrajna.
- `Session` koristi `Connection` iz engine-a na zahtev i upravlja ORM transakcijskim radom.
- `Session.add()` registruje pending objekat; samo po sebi ne šalje INSERT.
- Flush šalje potrebne INSERT/UPDATE/DELETE iskaze, ali nije commit.
- Commit prvo flush-uje pa potvrđuje transakciju; rollback poništava nepotvrđene promene.
- ORM SELECT preko `Session` može vratiti `User` instance; `session.scalars(select(User))` ih izdvaja iz rezultata.
- Identity map povezuje ORM identitet sa jednom instancom unutar sesije.
- Persistent znači da sesija prati odgovarajući red; ne znači nužno da je transakcija već commit-ovana.
- Izmena atributa čini objekat dirty; UPDATE se šalje pri flush-u.
- Sesija je scoped po operaciji/zahtevu, ne globalno deljena; zatvaraj je kontekstnim menadžerom.

## Vežbe za playground

Koristi postojeći root `.venv` i zasebnu SQLite memorijsku bazu.

1. Napravi `SessionFactory = sessionmaker(engine)` i proveri da pravljenje fabrike i sesije samo po sebi ne radi INSERT.
2. Napravi `User`, pozovi `session.add(user)` i proveri `user in session.new` pre flush-a.
3. Pozovi `session.flush()`; proveri ID, `created_at` i da je objekat persistent u toj sesiji.
4. U istoj sesiji učitaj korisnika preko `session.scalars(select(User))` i proveri identitet sa `is`.
5. Promeni `fullname`, proveri `session.dirty`, zatim rollback-uj i potvrdi kroz novu sesiju da promena nije sačuvana.
6. Ponovi izmenu kroz `with SessionFactory.begin()` bez izuzetka; potvrdi da je promena sačuvana.
7. Izazovi izuzetak unutar transakcijskog bloka i proveri da su svi upisi iz tog bloka poništeni.
