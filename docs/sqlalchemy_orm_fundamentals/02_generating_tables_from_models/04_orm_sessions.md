# Lekcija 4: ORM sesije

## Cilj lekcije

Engine iz prethodne lekcije zna kako SQLAlchemy može da dođe do baze i upravlja pool-om konekcija. U ORM radu koristimo **Session** kao radnu jedinicu za učitavanje i praćenje objekata, pripremu promena i upravljanje transakcijom.

Ova lekcija pravi fabriku sesija pomoću `sessionmaker()` i generator-kontekst-menadžer `get_session()`, koji obezbeđuje da se sesija po uspehu commit-uje, pri grešci rollback-uje, i u svakom slučaju zatvori.

## Šta je ORM `Session`

ORM sesija predstavlja ograničen kontekst rada sa ORM objektima i bazom. Tokom svog životnog ciklusa sesija:

- prati ORM objekte koje je učitala ili koje aplikacija dodaje;
- pamti promene atributa i operacije dodavanja/brisanja;
- grupiše te promene u jedinicu rada (unit of work);
- koristi konekciju do engine-a kada joj je potrebna komunikacija sa bazom;
- upravlja transakcijom u kojoj se upiti i izmene izvršavaju.

Sesija nije isto što i engine niti jedna fizička konekcija. Engine obezbeđuje dijalekt i pool, dok sesija koordinira ORM stanje i transakcioni rad. Sesija često pribavlja konekciju tek kada se prvi put izvrši operacija nad bazom, a po zatvaranju vraća korišćene konekcije engine-ovom pool-u.

U ORM aplikaciji obično se pravi kratkotrajna sesija za jedan ograničen zahtev ili posao, a zatim se zatvara. Ne treba držati jednu sesiju globalno otvorenu za ceo život aplikacije ili deliti istu sesiju između nezavisnih zahteva.

## Session factory: `sessionmaker()`

`sessionmaker()` je ORM funkcija koja konfiguriše fabriku sesija. Fabrika se zatim poziva da napravi pojedinačnu `Session` instancu.

Kurski source u `db.py` izgleda ovako:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/inventory"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine,
)
```

- `bind=engine` povezuje sesije napravljene ovom fabrikom sa odgovarajućim engine-om.
- `SessionLocal` je konvencionalno ime promenljive-fabrike; nije posebna SQLAlchemy klasa niti ime baze.
- `SessionLocal()` pravi novu sesiju. Fabrika nije sama sesija i njeno pravljenje ne mora odmah otvoriti konekciju.

Isti fajl sadrži i engine i fabriku sesija, ali to su različite odgovornosti. Engine je obrađen u lekciji 03; ovde je važan kao veza koju sesija koristi.

## `autocommit=False`

SQLAlchemy sesija koristi transakcioni rad. Sa `autocommit=False`, promene ne treba smatrati potvrđenim dok aplikacija ne pozove `session.commit()` ili neki kontekstni obrazac ne commit-uje transakciju.

Commit potvrđuje aktivnu transakciju. Ako se transakcija uspešno potvrdi, promene su trajne u bazi. Ako se dogodi greška pre potvrde, aplikacija može da pozove `session.rollback()` da prekine i poništi izmene trenutne transakcije.

U savremenom SQLAlchemy 2.x režimu transakcije se koriste eksplicitno. `autocommit=True` nije preporučena alternativa ovom obrascu; SQLAlchemy 2.x zadržava `autocommit` opciju samo radi kompatibilnosti i zahteva da bude `False`.

## Flush nije commit

Transkript opisuje flush kao slanje promena iz sesije ka bazi bez njihove konačne potvrde. Bitno je precizirati šta to znači:

- **Flush** pretvara pending ORM izmene u SQL `INSERT`, `UPDATE` ili `DELETE` naredbe i izvršava ih u trenutnoj transakciji.
- **Commit** završava i potvrđuje transakciju. Tek tada su promene potvrđene kao trajne iz perspektive transakcije.
- **Rollback** prekida transakciju i traži od baze da odbaci njene nepotvrđene izmene.

Flush nije samo čuvanje izmena u memoriji: SQL naredbe se zaista šalju bazi. Ipak, dok se transakcija ne commit-uje, izmene su nepotvrđene i mogu biti vraćene rollback-om. Constraint greške mogu se pojaviti već tokom flush-a, pre eksplicitnog `commit()` poziva.

`session.commit()` po pravilu prvo flush-uje sve pending promene, pa zatim potvrđuje transakciju. Zato `autoflush=False` **ne sprečava flush pri commit-u**.

## `autoflush=False`

Kada je `autoflush=True`, SQLAlchemy može automatski da flush-uje pending izmene pre određenih upita, kako bi se upit izvršio uz prethodno usklađene promene sesije.

Sa `autoflush=False`, taj automatski flush pre upita se isključuje. To ne znači da izmene ostaju samo u memoriji do kraja sesije: one mogu biti flush-ovane eksplicitnim pozivom `session.flush()` ili automatski kada se pozove `session.commit()`.

Kontrola nad flush-om može biti korisna u složenijem toku, ali može dovesti i do iznenađenja ako se očekuje da će upit videti neflush-ovane ORM promene u bazi. Opciju treba izabrati prema potrebama aplikacije, a ne samo zato što se koristi u kurskom primeru.

## Vezivanje sesije za engine

Argument `bind=engine` govori fabrici koji engine treba da koristi za sesije koje napravi. Bez odgovarajućeg bind-a, sesija ne zna automatski kojoj bazi da pošalje upit i operacije koje zahtevaju konekciju mogu da padnu.

Ako aplikacija radi sa više baza, može imati više engine-a i zasebno konfigurisane fabrike sesija. To je napredniji slučaj; u ovoj oblasti koristimo jednu PostgreSQL bazu.

Kada Python radi na host-u/WSL-u, engine URL iz lekcije 03 koristi `localhost:5432`. Kada bi aplikacija radila unutar druge Compose usluge, URL bi koristio ime Compose servisa kao host, na primer `postgres`. Sesija koristi bind-ovani engine i ne bira sama host.

## Upravljanje lifecycle-om kontekstnim menadžerom

Source `session.py` definiše generator-kontekst-menadžer:

```python
from contextlib import contextmanager

from db import SessionLocal


@contextmanager
def get_session():
	session = SessionLocal()
	try:
		yield session
		session.commit()
	except Exception as e:
		session.rollback()
		print(f"Error: {e}")
		raise
	finally:
		session.close()
```

`@contextmanager` iz `contextlib` pretvara generator funkciju u context manager. `yield session` predaje sesiju bloku `with`; kod pre `yield` radi pri ulasku, a kod posle `yield` pri izlasku.

Primer upotrebe:

```python
from session import get_session

with get_session() as session:
	# Upiti i ORM izmene dolaze u kasnijim lekcijama.
	...
```

Redosled je:

1. `SessionLocal()` pravi novu sesiju.
2. `yield` je predaje pozivaocu.
3. Ako blok izađe bez greške, poziva se `session.commit()`.
4. Ako blok ili commit podigne izuzetak, `except` poziva `session.rollback()` i ponovo podiže isti izuzetak pomoću `raise`.
5. `finally` se izvršava u oba slučaja i poziva `session.close()`.

Pošto `contextmanager` ponovo ubacuje izuzetak koji se desio unutar `with` bloka u generator na mestu `yield`, ovaj `except` može da ga obradi. Ako commit sam ne uspe, i ta greška prolazi kroz isti `except` i pokušava se rollback.

## Commit-at-exit obrazac i njegove posledice

Ovaj context manager automatski commit-uje svaki uspešno završen blok, čak i kada je blok radio samo čitanje. To je jednostavno za početni primer, ali je politika upravljanja transakcijom, a ne obavezno ponašanje svakog session context manager-a.

Ako se u jednom `with` bloku obavlja više operacija, one se potvrđuju kao jedna transakcija na izlazu. Izuzetak u bloku dovodi do rollback-a, pa se ne potvrđuje samo deo tog rada.

U većoj aplikaciji commit često ostaje eksplicitna odluka servisa ili funkcije koja zna granice poslovne operacije. Zavisi od arhitekture da li context manager commit-uje automatski ili samo garantuje zatvaranje; ne treba mešati te dve politike.

## Šta tačno radi `close()`

`session.close()` završava trenutnu upotrebu sesije, oslobađa ORM resurse i vraća eventualnu pozajmljenu konekciju engine pool-u. Ne znači nužno da se fizička TCP konekcija prema PostgreSQL-u uništava; pool može da je sačuva za ponovnu upotrebu.

Zatvaranje je važno čak i ako se desila greška. Zato se nalazi u `finally`, koji se izvršava i posle uspeha i posle izuzetka.

## Napomene o source primeru

- Imena argumenta u transkriptu izgovorena su kao `auto commit`, `auto flush` i `bind engine`; stvarni Python keyword argumenti su `autocommit`, `autoflush` i `bind`.
- Source hvata `Exception as e`, ispisuje poruku na terminal i ponovo podiže grešku. U produkcionom kodu umesto `print()` obično se koristi konfigurisan logger; ne treba nekontrolisano ispisivati osetljive detalje greške.
- Source radi `commit()` posle svakog uspešnog `with` bloka. To je izabrani obrazac primera, ne jedini mogući način organizovanja transakcija.
- `SessionLocal` je u source-u definisan u `db.py` zajedno sa engine-om, dok je lifecycle funkcija `get_session()` u `session.py`.

## Pitanja za proveru razumevanja

1. Koja je razlika između `Engine`, session factory-ja i pojedinačne `Session` instance?
2. Šta `bind=engine` omogućava sesiji?
3. Koja je razlika između flush-a i commit-a?
4. Da li `autoflush=False` sprečava flush pri `session.commit()`?
5. Šta se dešava kada se u telu `with get_session()` bloka desi izuzetak?
6. Zašto `session.close()` ne mora da znači gašenje fizičke konekcije ka PostgreSQL-u?
7. Koja je posledica toga što `get_session()` commit-uje svaki uspešan blok, uključujući i blok koji samo čita podatke?

## Sažetak

- `sessionmaker()` je fabrika; njen poziv kao `SessionLocal()` pravi novu ORM sesiju vezanu za engine.
- Sesija prati ORM objekte i upravlja operacijama u transakciji; nije engine niti fizička konekcija.
- Flush šalje SQL u trenutnu transakciju, commit je potvrđuje, a rollback odbacuje nepotvrđene izmene.
- `autoflush=False` isključuje automatski flush pre određenih upita, ali ne i flush koji prethodi commit-u.
- `get_session()` predaje sesiju kroz `yield`, commit-uje pri uspehu, rollback-uje i ponovo podiže grešku, a zatvara sesiju u `finally` bloku.
- Source primer commit-uje na izlasku iz svakog uspešnog context manager-a; ta politika treba da bude svesna odluka aplikacije.
