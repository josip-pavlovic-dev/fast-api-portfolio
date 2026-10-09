# Lekcija 03: Upravljanje konekcijama i transakcijama

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 13:31–21:42
**Glavne teme:** vraćanje konekcije u pool, kontekstni menadžeri, `commit()`/`rollback()`, `commit as you go`, `begin once`. Na kraju počinje kratka najava `MetaData` i `Table`, što se detaljnije nastavlja u sledećoj lekciji.

Transkript počinje usred prethodnog poglavlja, kod zatvaranja konekcije. Zatim objašnjava kako se SQLAlchemy brine o njenom vraćanju u pool i zašto se promene ne potvrđuju automatski. Automatski titlovi na nekim mestima pogrešno prepoznaju SQLAlchemy termine; beleška ih normalizuje i dopunjava kontekstom, ali ne menja nameru predavanja.

## Četiri stvari koje treba razlikovati

Konekcija i transakcija su povezane, ali predstavljaju različite resurse:

| Pojam                   | Šta predstavlja                                                        | Tipičan završetak                                                        |
| ----------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `Engine`                | Dugotrajniji objekat koji zna kako da dođe do baze i upravlja pool-om. | Obično se koristi tokom rada aplikacije; ne pravi se za svaki upit.      |
| SQLAlchemy `Connection` | Privremeno uzeta konekcija za izvršavanje SQL-a.                       | `close()` je vraća u pool ili je pool zatvara, zavisno od konfiguracije. |
| DBAPI konekcija         | Fizički objekat drajvera koji komunicira sa bazom.                     | Vraća se u pool ili se fizički zatvara.                                  |
| Transakcija             | Grupa operacija čije promene treba zajedno potvrditi ili poništiti.    | `commit()` potvrđuje; `rollback()` poništava nepotvrđene promene.        |

Jedna SQLAlchemy `Connection` koristi DBAPI konekciju dok je uzeta iz pool-a. Transakcija može početi i završiti se unutar tog perioda, a ista konekcija može posle jednog `commit()`-a da izvrši još posla u novoj transakciji.

```text
Engine
  -> uzme DBAPI konekciju iz pool-a ili otvori novu
  -> napravi SQLAlchemy Connection
  -> Connection izvršava operacije u jednoj ili više transakcija
  -> Connection se zatvori i DBAPI konekcija se vrati u pool
```

Važna razlika: zatvoriti SQLAlchemy `Connection` nije isto što i potvrditi transakciju. `close()` rešava životni vek konekcije; `commit()` rešava ishod trenutne transakcije.

## Šta znači `Connection.close()`?

U uobičajenom slučaju `connection.close()` ne gasi fizičku vezu sa bazom. SQLAlchemy završava upotrebu svog `Connection` objekta i vraća DBAPI konekciju u pool, gde može da čeka sledeću operaciju.

Pool može da zadrži vraćenu konekciju, a može i da je zatvori ako je bila privremeni višak iznad podešenog broja trajnih konekcija. Konkretno ponašanje zavisi od pool implementacije i konfiguracije. Zato „vratiti konekciju u pool“ ne garantuje da će fizička konekcija ostati otvorena zauvek.

### `reset on return` i `ROLLBACK` u logu

Ako konekcija pri vraćanju u pool još ima aktivnu transakciju, SQLAlchemy je podrazumevano poništava. To se naziva resetovanje pri vraćanju (`reset on return`). Čišćenje stanja sprečava da sledeći korisnik konekcije nasledi nepotvrđene promene, zaključavanja ili drugi transakcijski kontekst.

Zbog toga log može prikazati `ROLLBACK` kada se završi blok sa `engine.connect()`, čak i ako smo samo izvršili `SELECT`. Transakcijski kontekst je postojao, ali nije bilo nepotvrđenog upisa koji bi trebalo sačuvati. Ovaj `ROLLBACK`:

- ne briše promene koje su ranije uspešno potvrđene sa `commit()`;
- poništava samo promene iz još aktivne, nepotvrđene transakcije;
- u read-only primeru uglavnom samo očisti transakcijsko stanje pre vraćanja konekcije.

Ako konekcija ne pripada pool-u koji je zadržava, ili je pool zatvara kao višak, fizički DBAPI objekat može biti zatvoren umesto ponovo korišćen. To je dodatni razlog da kod ne zavisi od toga da li se ista fizička konekcija sledeći put ponovo koristi.

## Koristi kontekstne menadžere

Predavač preporučuje Python `with` obrazac umesto ručnog pozivanja `close()`. Isti princip važi za datoteke i druge resurse: mesto na kom resurs uzimamo treba jasno da odredi i gde se njegova upotreba završava.

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite://", echo=True)

with engine.connect() as connection:
	result = connection.execute(text("SELECT 1 AS broj"))
	print(result.scalar_one())

# Po izlasku iz bloka SQLAlchemy Connection je zatvoren.
# Ako je ostala transakcija, resetuje se pre vraćanja konekcije u pool.
```

Kontekstni menadžer osigurava završetak i ako se unutar bloka dogodi greška. Ne znači, međutim, da se nepotvrđeni upisi automatski čuvaju. Ako blok sa `engine.connect()` napustiš bez `commit()`-a, ne računaj da će podaci ostati sačuvani.

### Nemoj deliti aktivnu konekciju globalno

`Engine` je zamišljen da ga različiti delovi aplikacije koriste i deli se između niti u uobičajenoj konfiguraciji. Aktivna `Connection` ima stanje transakcije i ne treba je paralelno deliti između nezavisnih niti ili zadataka. Isti princip važi za ORM `Session`, koji ćemo učiti kasnije: napravi je za ograničenu jedinicu rada i ne deli jednu aktivnu sesiju između istovremenih zahteva.

Praktični obrazac je:

- dugotrajniji `Engine` čuvamo kao zajedničku aplikacionu konfiguraciju;
- konekciju uzimamo lokalno, unutar funkcije ili kontekstnog bloka;
- transakciju potvrđujemo ili poništavamo na jasno vidljivom mestu;
- ne pravimo novi `Engine` za svaki upit i ne držimo globalnu otvorenu `Connection`.

## SQLAlchemy 2.0 i implicitni početak transakcije

SQLAlchemy 2.0 prati transakcijsko stanje i uobičajeno automatski započne logičku transakciju kada prvi put izvršimo iskaz na konekciji. To se naziva `autobegin`.

Zato se u `echo=True` logu može videti:

```text
BEGIN (implicit)
SELECT 1 AS broj
...
ROLLBACK
```

`BEGIN (implicit)` označava da je SQLAlchemy započeo praćenje transakcije. Ne mora da znači da je SQLAlchemy poslao doslovan SQL tekst `BEGIN`; konkretan DBAPI drajver i dijalekt mogu da pokrenu transakciju implicitno.

Prvi `execute()` u ovom primeru započinje transakcijski kontekst:

```python
with engine.connect() as connection:
	connection.execute(text("SELECT 1"))
```

Po izlasku iz bloka `Connection` se zatvara, a nepotvrđena transakcija se poništava pri čišćenju konekcije. Za `SELECT` nam ne treba `commit()` da bismo „sačuvali“ rezultate; oni nisu izmene podataka. Ali transakcijsko stanje i dalje mora pravilno da se završi.

### Zašto SQLAlchemy 2.0 ne potvrđuje upise sam?

U SQLAlchemy-ju 2.0 izvršavanje `INSERT`, `UPDATE` ili `DELETE` ne znači automatski da je transakcija potvrđena. Program jasno kaže kada je posao uspeo i promene treba sačuvati, koristeći `commit()` ili transakcijski kontekst. Ako je potrebno odustati, poziva `rollback()` ili pusti da greška izađe iz bloka koji upravlja transakcijom.

SQLAlchemy 1.x je imao SQLAlchemy-level `autocommit` ponašanje za neke iskaze. Taj mehanizam je uklonjen u 2.0 jer je otežavao predvidljivo upravljanje transakcijama. To ne treba mešati sa DBAPI/driver-level autocommit režimom, koji i dalje postoji za posebne slučajeve i zavisi od baze. To je napredna postavka, ne zamena za uobičajeni 2.0 obrazac.

Ako se koriste dve fizičke konekcije, promena koju je prva konekcija upisala ali nije potvrdila ne treba da se smatra sačuvanom i dostupnom drugim korisnicima. `commit()` je tačka potvrde transakcije; bez njega podaci mogu nestati kada se nepotvrđena transakcija poništi.

## Obrazac 1: `commit as you go`

U ovom obrascu uzmemo konekciju preko `engine.connect()`, izvršimo deo posla i pozovemo `connection.commit()` kada želimo da sačuvamo taj deo. Posle potvrde, naredni `execute()` na istoj konekciji automatski započinje novu transakciju.

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite://", echo=True)

with engine.connect() as connection:
	connection.execute(
		text("CREATE TABLE poruka (id INTEGER PRIMARY KEY, tekst TEXT NOT NULL)")
	)
	connection.commit()

	connection.execute(
		text("INSERT INTO poruka (tekst) VALUES (:tekst)"),
		{"tekst": "Prvi upis"},
	)
	connection.commit()

	rows = connection.execute(
		text("SELECT id, tekst FROM poruka ORDER BY id")
	).all()
	print(rows)
```

U ovom jednostavnom primeru imamo dva potvrđena koraka:

1. Kreiranje tabele se izvrši, a zatim potvrdi.
2. INSERT se izvrši, a zatim potvrdi.

`SELECT` nakon toga započinje novi implicitni transakcijski kontekst. Ne pozivamo `commit()` da bismo sačuvali rezultate čitanja; po izlasku iz `with` bloka eventualno preostalo stanje se očisti zatvaranjem konekcije.

Ovaj obrazac je fleksibilan i dozvoljava više transakcija na istoj konekciji. Odgovornost za granice je na kodu: mora biti jasno gde se radi `commit()` i šta treba da se desi ako se pojavi greška.

## Obrazac 2: `begin once` preko `Engine`-a

Ako želimo da više iskaza bude u jednoj transakciji, koristimo `engine.begin()`:

```python
with engine.begin() as connection:
	connection.execute(
		text("INSERT INTO poruka (tekst) VALUES (:tekst)"),
		{"tekst": "Drugi upis"},
	)
	connection.execute(
		text("INSERT INTO poruka (tekst) VALUES (:tekst)"),
		{"tekst": "Treći upis"},
	)

# Normalan izlazak iz bloka: transakcija se potvrđuje, konekcija se vraća u pool.
```

`engine.begin()` obezbeđuje SQLAlchemy `Connection` i započinje transakciju. Kada se blok završi normalno, kontekstni menadžer potvrđuje transakciju i vraća konekciju u pool. Ako iz bloka izađe greška, transakcija se poništava, a konekcija se i dalje pravilno vraća.

To je koristan obrazac za grupu izmena koje moraju uspeti ili pasti zajedno. Ako prva komanda uspe, a druga izazove grešku koja izađe iz bloka, prva promena se poništava umesto da ostane delimično sačuvana.

Ako grešku uhvatiš unutar bloka i ne proslediš je dalje, kontekstni menadžer vidi normalan izlazak. U tom slučaju nemoj očekivati da će automatski znati da treba rollback; kod mora eksplicitno upravljati tom situacijom ili pustiti grešku da izađe iz transakcijskog bloka.

## Obrazac 3: `Connection.begin()`

Možemo prvo preuzeti konekciju, pa unutar nje označiti jednu ili više transakcija pomoću `connection.begin()`:

```python
with engine.connect() as connection:
	with connection.begin():
		connection.execute(
			text("INSERT INTO poruka (tekst) VALUES (:tekst)"),
			{"tekst": "Četvrti upis"},
		)

	with connection.begin():
		connection.execute(
			text("INSERT INTO poruka (tekst) VALUES (:tekst)"),
			{"tekst": "Peti upis"},
		)
```

Ovo su dve uzastopne transakcije na istoj SQLAlchemy `Connection`, ne jedna ugnježdena transakcija. Svaka se potvrdi po uspešnom izlasku iz svog bloka; ako iz odgovarajućeg bloka izađe greška, ta transakcija se poništi.

Transakciju treba započeti pre prvog iskaza. Ako je prethodni `execute()` već pokrenuo `autobegin`, pozivanje `connection.begin()` posle toga može prijaviti da je transakcija već započeta. U tom slučaju treba nastaviti postojeću transakciju i pozvati `commit()`/`rollback()`, ili organizovati kod tako da se `begin()` pozove pre upita.

Nemoj mešati uzastopne `connection.begin()` blokove sa `connection.begin_nested()`. Ugnježdena transakcija koristi savepoint i predstavlja drugi obrazac koji ovom lekcijom još ne obrađujemo.

## Poređenje obrazaca

| Obrazac                   | Ko obezbeđuje konekciju?  | Ko završava transakciju?                                                              | Konekcija posle bloka                                          |
| ------------------------- | ------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `with engine.connect()`   | `Engine`                  | Kod poziva `commit()`/`rollback()`; otvorena transakcija se pri zatvaranju poništava. | Vraća se u pool ili se zatvara.                                |
| `with engine.begin()`     | `Engine`                  | Kontekstni menadžer: commit pri uspehu, rollback kada greška izađe iz bloka.          | Vraća se u pool ili se zatvara.                                |
| `with connection.begin()` | Već otvoreni `Connection` | Kontekstni menadžer transakcije: commit pri uspehu, rollback pri grešci koja izađe.   | Ostaje otvorena do zatvaranja spoljnog `Connection` konteksta. |

Brzo pravilo:

- Koristi `engine.connect()` kada želiš direktno da upravljaš jednom konekcijom i granicama commit-a.
- Koristi `engine.begin()` za jednu celovitu transakciju koju kontekstni menadžer potvrđuje ili poništava.
- Koristi `connection.begin()` kada već imaš konekciju i želiš eksplicitni transakcijski blok unutar njenog životnog veka.

## SQLite baza u memoriji i pool

Predavač ističe da je SQLite baza u memoriji poseban slučaj: ona je vezana za konkretnu DBAPI konekciju. Ako se otvore dve odvojene SQLite memorijske konekcije, one po pravilu ne vide istu bazu.

Proverio sam ponašanje u root `.venv` okruženju, koje koristi SQLAlchemy `2.0.38`:

| URL                         | Podrazumevani pool u ovoj verziji | Šta treba zapamtiti                                                                                                                                                                |
| --------------------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sqlite://`                 | `SingletonThreadPool`             | Održava jednu konekciju po niti. U jednonitnom primeru praktično ponovo koristi jednu konekciju i time istu memorijsku bazu. Različite niti mogu dobiti različite memorijske baze. |
| `sqlite:///ime_datoteke.db` | `QueuePool`                       | Više konekcija može da pristupa istoj SQLite datoteci, uz SQLite-ova pravila zaključavanja i ograničenja za istovremene upise.                                                     |

Dakle, rečenicu iz predavanja da memorijska baza zahteva „istu konekciju“ treba razumeti u okviru ovog posebnog pool obrasca i jednonitnog primera. Nije opšte pravilo za PostgreSQL, MySQL ili SQLite bazu u datoteci.

Za tutorijale je `sqlite://` zgodan jer ne pravi bazni fajl. Za podatke koje želimo da sačuvamo posle završetka procesa koristimo SQLite URL sa putanjom datoteke. Podešavanja pool-a mogu se promeniti, ali ih ne treba menjati dok ne razumemo zašto nam je to potrebno.

## Najava sledećeg poglavlja: `MetaData` i `Table`

Od 20:33 predavanje prelazi sa izvršavanja SQL iskaza na strukturu potrebnu za složenije upite: opis tabele.

- `MetaData` je Python kolekcija koja okuplja opise tabela.
- `Table` predstavlja opis jedne tabele.
- `Column` objekti opisuju kolone te tabele, uključujući ime, tip i neka ograničenja.
- Takav opis liči na `CREATE TABLE`, ali je Python metadata, a ne automatski postojeća tabela u bazi.

Sledeća lekcija detaljnije obrađuje kako se `Table` i `MetaData` definišu. U ovoj lekciji važno je samo da shvatimo: pre nego što šaljemo upite koji koriste tabele, SQLAlchemy-ju možemo opisati oblik tih tabela.

## Sažetak za ponavljanje

- `Connection.close()` završava upotrebu SQLAlchemy konekcije; uobičajeno vraća DBAPI konekciju u pool, ne potvrđuje upis.
- Pool podrazumevano resetuje vraćenu konekciju; rollback čisti aktivnu, nepotvrđenu transakciju.
- `with engine.connect()` upravlja konekcijom, ali ne radi automatski commit.
- SQLAlchemy 2.0 koristi `autobegin`; prvi `execute()` može da započne transakcijski kontekst.
- `commit as you go` koristi eksplicitne `connection.commit()` pozive; nakon commit-a naredni upit može pokrenuti novu transakciju.
- `engine.begin()` i `connection.begin()` potvrđuju promene pri normalnom izlasku i poništavaju ih kada greška izađe iz bloka.
- SQLAlchemy 2.0 nema raniji SQLAlchemy-level autocommit; za upise koristi eksplicitno upravljanje transakcijom.
- Memorijski SQLite je vezan za konekciju; SQLAlchemy `2.0.38` podrazumevano koristi `SingletonThreadPool` za `sqlite://`.
- `MetaData` i `Table` su Python opisi šeme; njihova detaljna obrada počinje u narednoj lekciji.

## Vežbe za playground

Radi u novom fajlu u `playground/sqlalchemy_2/`; koristi postojeći root `.venv`.

1. Napravi memorijski engine sa `echo=True`. Izvrši `SELECT 1` unutar `with engine.connect()` i prepoznaj `BEGIN (implicit)` i `ROLLBACK` u logu.
2. Napravi tabelu i izvrši INSERT kroz `engine.connect()`. Prvo izostavi `commit()` pa izađi iz bloka; zatim ponovi sa `commit()` i proveri razliku.
3. Ubaci dva reda kroz jedan `with engine.begin()` blok i proveri da oba postoje posle izlaska.
4. U transakcijskom bloku izazovi grešku posle prvog INSERT-a, pusti da izađe iz bloka, pa proveri da li je prvi INSERT poništen.
5. Na jednoj konekciji izvrši upit, pa pokušaj da naknadno pozoveš `connection.begin()`. Posmatraj `autobegin` stanje; zatim promeni redosled tako da `begin()` bude pre prvog iskaza.
6. Uporedi `sqlite://` i `sqlite:///playground.db`. Nemoj koristiti `drop_all()` ili brisati postojeće korisničke podatke; kreiraj poseban probni fajl samo za ovu vežbu.
