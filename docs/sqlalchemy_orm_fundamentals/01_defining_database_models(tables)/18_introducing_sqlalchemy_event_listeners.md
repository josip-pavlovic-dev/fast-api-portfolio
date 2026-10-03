# Lekcija 18: Uvod u SQLAlchemy event listener-e

## Cilj lekcije

SQLAlchemy event system omogućava da se funkcija pozove kada se dogodi određeni događaj u ORM-u ili SQLAlchemy Core-u. U ovoj lekciji se pravi mapper listener za model `Category`: pre ORM `INSERT`-a ili `UPDATE`-a, vrednosti `name` i `slug` pretvaraju se u mala slova.

Ovo je uvodna demonstracija, a ne sveobuhvatan pregled event system-a. Važno je razlikovati ovakvu aplikacionu transformaciju od constraint-a baze: event listener može urediti vrednost koju obrađuje SQLAlchemy ORM, ali sam po sebi ne čuva pravilo u šemi baze.

## Gde se uklapaju SQLAlchemy događaji

SQLAlchemy nudi događaje na više nivoa. Transkript ih predstavlja kao pregled mogućnosti:

- **ORM događaji** prate ORM objekte i njihov životni ciklus.
- **Mapper događaji** odnose se na mapiranu klasu i operacije upisa njenih redova, na primer `before_insert` i `before_update`.
- **Session događaji** prate rad sesije, uključujući flush i commit.
- **Flush događaji** se aktiviraju tokom usklađivanja promena iz sesije sa bazom.
- **Engine događaji** odnose se na engine i DBAPI konekcije, kao i na izvršavanje SQL-a.
- **DDL događaji** odnose se na operacije nad šemom, kao što je kreiranje objekata baze.

Ovo su različite tačke proširenja. Izbor događaja zavisi od toga _kada_ treba izvršiti logiku i _na kom nivou_ ona treba da važi. Primer u ovoj lekciji koristi mapper događaje.

## Registracija listener-a

Modul `sqlalchemy.event` sadrži API za registraciju listener-a. Transkript prikazuje dva pristupa:

### Dekorator `event.listens_for`

Dekorator se postavlja iznad funkcije i povezuje je sa ciljnom klasom i nazivom događaja:

```python
from sqlalchemy import event


@event.listens_for(Category, "before_insert")
@event.listens_for(Category, "before_update")
def lowercase_category_fields(mapper, connection, target):
	...
```

Ovde je `Category` cilj listener-a, a ista funkcija se registruje za oba događaja. Dekorator je pogodan za listener-e koji se registruju deklarativno kada se modul učita.

### Funkcija `event.listen`

Listener može umesto dekoratora da se registruje pozivom funkcije:

```python
event.listen(Category, "before_insert", lowercase_category_fields)
event.listen(Category, "before_update", lowercase_category_fields)
```

Ovaj oblik omogućava da se registracija obavi eksplicitnim pozivom u toku izvršavanja programa. Transkript to opisuje kao dinamičku registraciju. Oba pristupa povezuju funkciju, cilj i događaj; dekorator je samo drugačiji, često pregledniji zapis.

## Primer: normalizacija naziva i slug-a

Source definiše listener izvan tela klase `Category`. Listener ne mora biti metoda modela; može se nalaziti bilo gde gde je klasa već definisana i gde se registracija izvršava.

```python
@event.listens_for(Category, "before_insert")
@event.listens_for(Category, "before_update")
def lowercase_category_fields(mapper, connection, target):
	if target.name:
		target.name = target.name.lower()
	if target.slug:
		target.slug = target.slug.lower()
```

Funkcija dobija tri argumenta:

- `mapper` je mapper povezan sa mapiranom klasom `Category`.
- `connection` je konekcija koja se koristi u okviru operacije upisa.
- `target` je konkretna instanca `Category` koja se upisuje ili menja.

Ako `target.name` ima truthy vrednost, `.lower()` je pretvara u mala slova. Isto se radi sa `target.slug`. Provera `if` izbegava poziv `.lower()` nad vrednošću kao što je `None` ili prazan string. Ona, međutim, ne validira niti odbacuje te vrednosti.

Na primer, ako ORM upisuje `Category(name="TeleVizori", slug="Sony-TV")`, listener će pre upisa promeniti vrednosti instance u `televizori` i `sony-tv`.

## Kada se izvršava mapper listener

`before_insert` i `before_update` su mapper događaji vezani za ORM flush. Flush se dešava kada SQLAlchemy pošalje promene iz sesije ka bazi; može se desiti tokom `commit()` ili automatski pre određenih upita, ne samo pri eksplicitnom pozivu `commit()`.

Listener radi nad ORM instancom pre nego što SQLAlchemy pošalje odgovarajući `INSERT` ili `UPDATE`. Zato se promena `target.name` ili `target.slug` upisuje kao deo te ORM operacije.

Ovo nije opšti Python setter koji se poziva čim se atributu dodeli vrednost. Dodela `category.name = ...` sama po sebi ne poziva mapper listener; listener se izvršava u odgovarajućoj fazi ORM flush-a.

## Transformacija nije constraint baze

Primer sa `.lower()` menja podatke u aplikacionom ORM toku. Ne dodaje `CHECK` constraint, ne menja šemu i ne utiče na klijente koji zaobiđu ovaj ORM. Direktan SQL, drugi program ili drugi ORM koji ne registruje isti listener može upisati vrednost sa velikim slovima.

Zato listener ne treba nazivati baznim ograničenjem. U zavisnosti od pravila i potreba sistema, aplikaciona logika može pružiti očekivanu transformaciju, dok se integritet koji mora važiti za sve upise mora obezbediti na nivou baze ili odgovarajućim mehanizmom koji pokriva sve načine pristupa.

Listener takođe nije zamena za API validaciju. API može unapred vratiti jasnu poruku korisniku, dok listener obavlja transformaciju u ORM toku. Ako više aplikacija deli bazu, svaka mora primeniti istu aplikacionu logiku ili se pravilo mora obezbediti zajedničkim mehanizmom.

## Važne posledice primera

- `if target.name` i `if target.slug` samo preskaču prazne ili nedostajuće vrednosti; ne garantuju da polja sadrže tekst.
- Mala slova mogu promeniti rezultat jedinstvenosti. Pošto su `Category.name` i `Category.slug` u source-u označeni sa `unique=True`, vrednosti poput `"TV"` i `"tv"` mogu nakon normalizacije postati duplikati. Baza tada odbija upis zbog `UNIQUE` ograničenja.
- Python-ov `str.lower()` je transformacija aplikacionog koda. Nije automatski isto što i pravila za poređenje velikih i malih slova u svakoj bazi, kolaciji ili drugom klijentu.
- Listener je registrovan za ORM događaje. Ne treba pretpostaviti da se pokreće za svaki SQL upit ili svaki način izmene podataka.

## Ograničenja mapper događaja

Mapper događaji su namenjeni logici vezanoj za upis pojedinačnih mapiranih instanci. Za složene promene kroz sesiju, rad sa više redova ili upravljanje transakcijama često su prikladniji drugi tipovi događaja. Izbor pogrešne tačke može dovesti do toga da listener ne obuhvati operaciju koju je trebalo da pokrije.

U ovom primeru listener samo menja dve vrednosti na `target`. To je usko ograničena transformacija koja odgovara mapper događaju. Lekcija ne obrađuje napredne obrasce, redosled događaja, uklanjanje listener-a niti sve razlike između ORM i Core API-ja.

## Razlike i problemi u priloženom source-u

### Model trenutno sprečava učitavanje modula

U klasi `Category` source prosleđuje `nullable=False` kao argument konstruktoru `ForeignKey`:

```python
category_id: Column[int] = Column(
	ForeignKey("category.id", nullable=False, ondelete="RESTRICT")
)
```

`nullable` je opcija kolone i treba da bude prosleđena `Column`-i, a ne `ForeignKey` objektu. Zbog toga definisanje klase `Category` izaziva grešku pre nego što se izvrše dekoratori ispod nje; listener-i se ne registruju pri uvozu ovog source fajla. Ovo je postojeća greška u snapshot-u, a source nije menjan.

### Prethodni constraint-i su na drugom modelu

Source sadrži `CheckConstraint` deklaracije unutar klase `Product`, iako imena počinju sa `check_category_`. One zato ne definišu ograničenja za `Category`. Listener iz ove lekcije cilja `Category`, ali to ne znači da su raniji check constraint-i za tu tabelu.

## Pitanja za proveru razumevanja

1. Koja je razlika između `event.listens_for` dekoratora i `event.listen` poziva?
2. Šta predstavljaju argumenti `mapper`, `connection` i `target` u ovom mapper listener-u?
3. U kom delu ORM toka se aktiviraju `before_insert` i `before_update`?
4. Zašto promena `target.name` nije ograničenje na nivou baze?
5. Šta se događa ako se posle normalizacije `"TV"` sudari sa postojećom vrednošću `"tv"` uz `unique=True`?
6. Zašto se listener iz priloženog source fajla trenutno ne registruje pri uvozu?

## Sažetak

- SQLAlchemy event system omogućava povezivanje funkcija sa događajima ORM-a, sesije, engine-a i šeme.
- `event.listens_for` i `event.listen` registruju funkciju za određeni cilj i događaj.
- Primer registruje istu funkciju za `Category` događaje `before_insert` i `before_update`.
- Mapper listener dobija mapper, konekciju i instancu koja se upisuje; u primeru normalizuje `name` i `slug` u mala slova.
- Listener radi u aplikacionom ORM toku i ne zamenjuje constraint baze niti validaciju API-ja.
- Source trenutno ne može da se učita zbog `nullable=False` prosleđenog u `ForeignKey`, pa listener-i ne mogu biti registrovani dok se ta ranija greška ne ispravi.
