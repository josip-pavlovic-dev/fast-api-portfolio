# Lekcija 02: Rad sa `Engine`-om

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 4:52–13:31
**Tema:** pravljenje `Engine`-a, URL baze, prva konekcija, tekstualni SQL, `Result`/`Row` i vraćanje konekcije u pool.

Transkript opisuje kod sa slajdova, ali ne sadrži kompletne Python blokove. Primeri ispod prate predavačevo objašnjenje; proširenja koja nisu izgovorena u ovom delu označena su kao dodatne napomene.

## Mentalni model

`Engine` je SQLAlchemy-jeva dugotrajna ulazna tačka za određenu bazu. On povezuje tri stvari:

1. **Dijalekt** koji zna kako SQLAlchemy tipove i iskaze prilagoditi konkretnoj bazi.
2. **DBAPI drajver** koji obavlja stvarnu komunikaciju, na primer Pythonov `sqlite3` drajver za SQLite.
3. **Pool konekcija** iz kog se konekcije uzimaju i u koji se vraćaju radi ponovne upotrebe.

Zato `Engine` nije isto što i jedna otvorena konekcija. Aplikacija obično napravi jedan `Engine` za bazu i koristi ga tokom svog rada. Kada je potreban rad sa bazom, `Engine` obezbedi SQLAlchemy `Connection`; ta konekcija je povezana sa konkretnom DBAPI konekcijom dok je uzeta iz pool-a.

Pojednostavljeno:

```text
create_engine(URL) -> Engine
Engine.connect()   -> SQLAlchemy Connection
Connection.execute(...) -> SQLAlchemy Result
Connection.close() -> DBAPI konekcija nazad u pool
```

## Pravljenje `Engine`-a

Predavač prikazuje `create_engine()` i URL koji opisuje bazu. Najjednostavniji primer iz ovog kursa je SQLite u memoriji:

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite://", echo=True)
```

`create_engine()` napravi i konfiguriše SQLAlchemy `Engine`, ali ne uspostavlja odmah fizičku DBAPI konekciju. Konekcija se obično otvori tek kada prvi put zatražimo `Connection` ili izvršimo iskaz kroz `Engine`. To je lenjo povezivanje (lazy connection): možemo da pripremimo konfiguraciju, a bazu ne dodirnemo dok je stvarno ne koristimo.

`echo=True` uključuje SQLAlchemy logovanje SQL-a i pratećih informacija, kao što su bind parametri i granice transakcija. Korisno je za učenje i otklanjanje grešaka. U produkciji ga ne treba olako uključivati jer logovi mogu sadržati osetljive vrednosti iz upita.

U logu se mogu pojaviti poruke kao `[generated in ...]` ili `[cached since ...]`. One se odnose na SQLAlchemy-jevu kompilaciju iskaza: prvi put se struktura SQLAlchemy iskaza prevede u SQL za dijalekt, a odgovarajući sledeći iskaz iste strukture može da ponovo iskoristi tu kompilaciju. To nije keširanje redova koje je baza vratila. Upit se i dalje izvršava nad bazom svaki put, a nove bind vrednosti se i dalje šalju.

### Kako čitati URL

Za mrežne baze tipičan oblik URL-a je:

```text
dijalekt+driver://korisnik:lozinka@host:port/ime_baze
```

- **Dijalekt** označava vrstu baze, na primer `postgresql`, `mysql` ili `sqlite`.
- **Drajver** je konkretna Python biblioteka kojom se komunicira sa bazom; kod PostgreSQL-a, na primer, može biti `psycopg`.
- **Korisnik, lozinka, host i port** koriste se kod baza kojima se pristupa preko mreže.
- **Ime baze** bira konkretnu bazu na serveru.

SQLite je poseban slučaj: baza je obično datoteka ili memorijska baza u procesu, pa nema mrežni host, port ni korisničko ime.

```python
# SQLite baza u memoriji
memory_engine = create_engine("sqlite://")

# SQLite datoteka sa putanjom relativnom prema trenutnom direktorijumu
file_engine = create_engine("sqlite:///catalog.db")

# PostgreSQL primer za instaliran psycopg drajver; vrednosti su samo primer
# postgres_engine = create_engine(
#     "postgresql+psycopg://user:password@localhost:5432/catalog"
# )
```

SQLite URL `sqlite://` (kao i `sqlite:///:memory:`) bira bazu u memoriji; `sqlite:///catalog.db` bira datoteku `catalog.db`. Samo kreiranje `Engine`-a ne napravi tu datoteku niti memorijsku bazu. Ona nastaje kada se prvi put uspostavi DBAPI konekcija.

## Od `Engine`-a do `Connection`-a

Kada aplikaciji treba izvršavanje SQL-a, traži konekciju od `Engine`-a:

```python
with engine.connect() as connection:
	# connection je SQLAlchemy Connection
	...
```

Pri prvom korišćenju pool može da otvori novu DBAPI konekciju. Kod narednog korišćenja može da vrati već postojeću konekciju iz pool-a. Tačno ponašanje zavisi od baze i podešavanja pool-a, ali obrazac ostaje isti: `Engine` upravlja životnim ciklusom, dok naš kod privremeno koristi `Connection`.

### SQLAlchemy `Connection` i DBAPI konekcija nisu ista klasa

Naziv „konekcija“ se koristi na dva nivoa:

| Objekat                 | Ko ga obezbeđuje?       | Uloga                                                       |
| ----------------------- | ----------------------- | ----------------------------------------------------------- |
| SQLAlchemy `Connection` | SQLAlchemy              | Stabilan API za izvršavanje SQL-a, transakcije i rezultate. |
| DBAPI konekcija         | Drajver, npr. `sqlite3` | Konkretan objekat koji razgovara sa bazom.                  |

SQLAlchemy `Connection` obavija ili posreduje pristup DBAPI konekciji. U uobičajenom radu koristi se SQLAlchemy objekat, a ne direktno drajver. Za dijagnostiku se DBAPI objekat može pogledati ovako:

```python
with engine.connect() as connection:
	driver_connection = connection.connection.driver_connection
	print(type(driver_connection))
```

Ovo je uvid u implementacioni drajver i nije obrazac za svakodnevno izvršavanje upita. Direktan rad sa `driver_connection`-om vezuje kod za konkretan drajver i zaobilazi deo apstrakcije koju obezbeđuje SQLAlchemy.

## Tekstualni SQL preko `text()`

Predavač počinje tekstualnim iskazom koji nema ni tabelu ni model: baza može da vrati izraz kao kolonu rezultata.

```python
from sqlalchemy import text

statement = text("SELECT :message AS greeting")
```

`text()` pretvara SQL tekst u SQLAlchemy `TextClause`, odnosno izvršiv SQLAlchemy iskaz. `:message` je bind parametar: vrednost se šalje odvojeno od strukture SQL-a.

```python
with engine.connect() as connection:
	result = connection.execute(
		text("SELECT :message AS greeting"),
		{"message": "Hello, SQLAlchemy!"},
	)
	row = result.first()

	if row is not None:
		print(row.greeting)
```

Očekivani ispis:

```text
Hello, SQLAlchemy!
```

U ovom primeru `greeting` je alias kolone u SQL rezultatu. SQLite ne zahteva da `SELECT` čita iz postojeće tabele kada biramo samo konstantnu ili parametarsku vrednost.

U SQLAlchemy-ju 2.0 običan Python string nije izvršiv argument za `Connection.execute()`. Koristi `text(...)` za SQL tekst koji obrađuje SQLAlchemy. `Connection.exec_driver_sql(...)` postoji za slučajeve kada namerno želimo da prosledimo tekst direktno DBAPI drajveru.

### Zašto bind parametar umesto formatiranja stringa?

Nemoj praviti upit ubacivanjem korisničkog teksta u SQL string:

```python
# Loš obrazac: vrednost postaje deo SQL teksta
statement = text(f"SELECT '{user_input}' AS greeting")
```

Umesto toga, ostavi SQL strukturu fiksnom, a vrednost pošalji kao parametar:

```python
statement = text("SELECT :message AS greeting")
result = connection.execute(statement, {"message": user_input})
```

SQLAlchemy i drajver vezuju vrednost uz iskaz. Tako se smanjuje rizik od SQL injection napada i izbegava ručno citiranje vrednosti. Bind parametri su za **vrednosti**; ne služe da se njima dinamički zamene imena tabela ili kolona.

## Šta znači `BEGIN (implicit)` u logu?

Kada je uključen `echo=True`, izvršavanje može da prikaže nešto slično:

```text
BEGIN (implicit)
SELECT ? AS greeting
...
ROLLBACK
```

`BEGIN (implicit)` je SQLAlchemy-jeva poruka da je započet transakcijski kontekst automatski (autobegin), kada je konekcija počela da izvršava rad. Ta poruka ne dokazuje da je SQLAlchemy poslao doslovan tekst `BEGIN` bazi. DBAPI i dijalekt mogu transakciju započeti svojim uobičajenim implicitnim ponašanjem; detalj zavisi od drajvera i baze.

Osnovni DBAPI model podrazumeva da je automatsko potvrđivanje isključeno, pa promenama upravlja transakcija. SQLAlchemy zbog toga prati stanje transakcije i daje nam eksplicitne metode za potvrdu ili poništavanje. `echo` log je koristan trag o tom stanju, ali nije u svakom slučaju doslovan snimak svakog SQL tokena koji je poslat.

`with engine.connect()` **ne znači automatski commit**. Ako je transakcija ostala otvorena kada se blok završi, zatvaranje SQLAlchemy konekcije je poništava pre vraćanja DBAPI konekcije u pool. Za izmenu podataka koristi eksplicitno `connection.commit()` ili kontekst transakcije `with engine.begin() as connection:`; ovaj obrazac ćemo detaljnije obraditi u lekciji o konekcijama i transakcijama.

## Rezultat `execute()` poziva

Poziv `connection.execute(...)` vraća SQLAlchemy `Result`; za uobičajeni rezultat upita preko konekcije konkretna implementacija je `CursorResult`. On posreduje pristup redu koji vraća DBAPI kursor i nudi metode za preuzimanje podataka.

### `Row` objekat

`result.first()` vraća prvi `Row` ili `None` ako upit nije vratio nijedan red. `Row` se ponaša slično imenovanom tuple-u:

```python
row[0]                      # prva vrednost u redu
row.greeting                # atribut prema imenu/alias-u kolone
row._mapping["greeting"]    # pristup kroz Mapping interfejs
dict(row._mapping)          # običan dict sa imenima i vrednostima
```

`Row` nije običan `dict`. Njegov tuple interfejs znači da se provera `"greeting" in row` odnosi na vrednosti reda. Za proveru imena kolona koristi:

```python
"greeting" in row._mapping
```

Prefiks u `_mapping` čuva poseban interfejs pod imenom koje se neće sudarati sa mogućim imenima kolona. Za dinamično ime kolone, `row._mapping[ime_kolone]` je jasnije od pristupa atributom.

### `first()` nije isto što i SQL `LIMIT 1`

`first()` uzima prvi red koji je dostupan i zatvara result set, čime oslobađa kursor. Ako baza vrati više redova, preostali se odbacuju. Ova metoda **ne menja već izvršeni SQL i ne dodaje `LIMIT 1`**.

Zato je primer sa `SELECT :message AS greeting` bezbedan za `first()` jer taj iskaz prirodno vraća jedan red. Ako pravi upit može da vrati mnogo redova, a potreban je samo jedan, ograniči rezultat i u samom SQL iskazu, na primer SQLAlchemy izrazom `.limit(1)`. Ako cilj nije „daj mi neki prvi“, nego „mora postojati tačno jedan“, koristi odgovarajuću metodu provere kardinalnosti, kao `one()` ili `scalar_one()`.

Zatvaranje `Result`-ovog kursora ne zatvara `Connection`. Konekcija može da izvrši još iskaza dok je njen `with` blok otvoren.

## Više redova: iteracija, `all()` i `scalars()`

Kada rezultat sadrži više kolona po redu, može se iterirati kroz redove i raspakovati tuple vrednosti:

```python
with engine.connect() as connection:
	result = connection.execute(
		text(
			"SELECT :first AS greeting "
			"UNION ALL SELECT :second AS greeting"
		),
		{"first": "Hello", "second": "SQLAlchemy"},
	)

	for row in result:
		print(row.greeting)
```

Iteracija je zgodna kada svaki red treba obraditi redom. `result.all()` umesto toga potroši rezultat i napravi Python listu svih redova, što je praktično za mali rezultat koji želiš dalje da koristiš, ali može nepotrebno da zauzme memoriju za veliki rezultat.

Ako te zanima samo prva izabrana kolona svakog reda, pozovi `scalars()`:

```python
with engine.connect() as connection:
	greetings = connection.execute(
		text(
			"SELECT :first AS greeting "
			"UNION ALL SELECT :second AS greeting"
		),
		{"first": "Hello", "second": "SQLAlchemy"},
	).scalars().all()

	print(greetings)
```

Rezultat:

```text
['Hello', 'SQLAlchemy']
```

`scalars()` ne znači „uzmi jedan skalar ukupno“. Ono pravi pogled koji za **svaki red** daje jednu Python vrednost: podrazumevano prvu izabranu kolonu. Zatim `.all()` pravi listu tih vrednosti. Zato:

- `result.all()` daje listu `Row` objekata;
- `result.scalars().all()` daje listu vrednosti iz prve kolone;
- `for row in result` obrađuje redove pojedinačno kroz SQLAlchemy Result API.

Način na koji drajver baferuje podatke u pozadini zavisi od baze i podešavanja. Iteracija izbegava da naš kod odmah napravi dodatnu listu svih redova, ali sama po sebi ne garantuje serversko strimovanje za svaki drajver.

## Kako čitati vežbu `01_engine_usage.py`

Vežba [01_engine_usage.py](../playground/sqlalchemy_2/01_engine_usage.py) prolazi iste koncepte jednim izvršivim primerom. Važno je pratiti koji poziv pravi novi `Result`:

```python
statement = text("SELECT 'hello world' AS greeting")

first_row = connection.execute(statement).first()
rows = connection.execute(statement).all()

multiple_rows = text(
	"SELECT 1 AS item_id, 'hello' AS greeting "
	"UNION ALL SELECT 2, 'SQLAlchemy'"
)
tuple_rows = connection.execute(multiple_rows).all()
scalar_values = connection.execute(multiple_rows).scalars().all()
```

- `statement` opisuje jedan red sa kolonom `greeting`; pošto je vrednost fiksna, ovde nema bind parametra.
- Prvi `execute()` napravi `Result`, a `.first()` uzme njegov prvi `Row` i zatvori taj rezultatni skup.
- Drugi `execute(statement)` pravi nov `Result`, pa `.all()` može bezbedno da ga potroši. Ne nastavljamo čitanje prvog rezultata posle `.first()`.
- `tuple_rows` sadrži dva reda: `(1, "hello")` i `(2, "SQLAlchemy")`.
- `scalar_values` je `[1, 2]`, jer `scalars()` uzima prvu izabranu kolonu (`item_id`) iz svakog reda, a ne kolonu `greeting`.

Ako želimo da `scalars()` vrati pozdrave, pozdrav mora biti prva izabrana kolona ili jedina kolona:

```python
greeting_statement = text(
	"SELECT 'hello' AS greeting "
	"UNION ALL SELECT 'SQLAlchemy'"
)
greetings = connection.execute(greeting_statement).scalars().all()
assert greetings == ["hello", "SQLAlchemy"]
```

U vežbi se `driver_connection` ispisuje samo da pokaže da SQLAlchemy `Connection` koristi DBAPI objekat ispod sebe. Uobičajeni upiti idu preko `connection.execute()`, ne direktno preko tog drajverskog objekta.

Po izlasku iz `with engine.connect()` bloka SQLAlchemy `Connection` se zatvara, ali se DBAPI konekcija obično vraća u pool. Na kraju vežbe `engine.dispose()` odbacuje pool-ovane konekcije; ovde nema konekcije koja je još pozajmljena iz `with` bloka. Pošto je URL `sqlite://`, gašenje poslednje konekcije uklanja i memorijsku bazu.

`echo=True` čini tok vidljivim: log prikazuje izvršene SELECT iskaze i transakcijske poruke. Posle čitanja može se videti `ROLLBACK` pri zatvaranju konekcije; to čisti transakcijski kontekst i ne poništava nikakve SELECT rezultate.

## Zatvaranje konekcije i pool

Kada izađemo iz `with engine.connect() as connection:`, SQLAlchemy poziva zatvaranje svog `Connection` objekta. U uobičajenom slučaju to **ne gasi fizičku DBAPI konekciju**: vraća je u pool da bi je sledeći deo aplikacije mogao ponovo da koristi.

```python
with engine.connect() as connection:
	connection.execute(text("SELECT 1"))

# SQLAlchemy Connection je zatvoren za dalju upotrebu ovde;
# DBAPI konekcija je obično vraćena u pool, ne fizički ugašena.
```

Kontekstni menadžer je poželjniji od ručnog `connect()`/`close()` jer zatvara SQLAlchemy konekciju i u slučaju greške. Ako je ostala aktivna transakcija, SQLAlchemy je poništava pre vraćanja konekcije u pool; zatvaranje konekcije nije zamena za commit.

## Dodatne napomene za SQLite i `Engine`

Sledeće nijanse su korisne za vežbanje, iako nisu detaljno obrađene u ovom delu predavanja:

- SQLite `sqlite://` ne pravi `.db` datoteku; podaci su u memoriji i vezani su za stvarnu SQLite konekciju. Pool ih može sačuvati dostupnim dok tu konekciju zadržava otvorenom.
- Kod uobičajenog jednonitnog primera engine vraća konekciju u pool, pa isti engine može ponovo da pristupi istoj memorijskoj bazi. Ako se konekcija stvarno zatvori ili se pool odbaci pomoću `engine.dispose()`, memorijska baza nestaje. Podešavanja pool-a za više niti mogu promeniti ponašanje; to ćemo obrađivati samo ako nam zatreba.
- SQLite putanja do datoteke, npr. `sqlite:///catalog.db`, je prikladnija kada podaci treba da ostanu posle završetka skripte.
- `echo=True` može ispisati bind parametre; ne uključuj ga u okruženju gde bi logovi mogli otkriti lozinke, tokene ili privatne podatke.
- Engine je obično dugotrajan i deli se kroz aplikaciju. Nemoj praviti novi `Engine` za svaki `SELECT`; time bi se izgubila svrha pool-a i nepotrebno bi se stvarali resursi.

## Verzijski okvir SQLAlchemy 2.0

U ovoj lekciji koristimo obrasce koji su prirodni u SQLAlchemy-ju 2.0:

- tekstualni iskaz za `Connection.execute()` obmotava se sa `text()`;
- vrednosti se prosleđuju kao bind parametri;
- pristup imenima kolona u `Row` objektu koristi atribut ili `row._mapping`;
- `Result.scalars()` je transformacija rezultata, ne posebna SQL naredba.

Kasniji ORM primeri koriste isti temeljni princip izvršavanja, ali će `Session` dodatno upravljati ORM objektima i transakcijskim radom.

## Sažetak za ponavljanje

- `create_engine()` konfiguriše `Engine`; fizička konekcija se otvara tek pri prvoj upotrebi.
- `Engine` upravlja pool-om; `Connection` se privremeno uzima za izvršavanje.
- `Connection.execute(text(...), parametri)` izvršava SQL tekst uz bind parametre.
- Rezultat je `Result`/`CursorResult`; njegovi redovi su tuple-slični `Row` objekti.
- `first()` vraća prvi red ili `None` i zatvara rezultat, ali ne dodaje SQL `LIMIT`.
- `scalars()` bira prvu vrednost svakog reda; `.all()` pravi listu.
- `Connection.close()` obično vraća DBAPI konekciju u pool; ne radi commit.
- `BEGIN (implicit)` označava automatski početak transakcijskog konteksta, ne nužno doslovan SQL `BEGIN` poslat od SQLAlchemy-ja.

## Vežba za playground

U posebnom fajlu u `playground/sqlalchemy_2/` prekucaj primer sa `create_engine("sqlite://", echo=True)` i tekstualnim `SELECT`-om. Zatim:

1. Promeni bind parametar `message` i potvrdi da se vrednost menja bez menjanja SQL strukture.
2. Ispiši rezultat kao `row[0]`, `row.greeting` i `row._mapping["greeting"]`.
3. Napravi iskaz koji vraća dva reda; uporedi iteraciju, `.all()` i `.scalars().all()`.
4. Zatvori jednu konekciju i zatraži novu preko istog engine-a; obrati pažnju na SQLAlchemy log i na to da se konekcija vraća u pool.
5. Ne dodaj `commit()` u primer koji samo izvršava `SELECT`; kasnije proverićemo eksplicitni commit i rollback za izmene podataka.
