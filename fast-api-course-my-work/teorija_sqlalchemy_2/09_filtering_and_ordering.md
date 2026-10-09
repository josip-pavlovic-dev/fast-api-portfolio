# Lekcija 09: Filtriranje, label-e i redosled rezultata

**Predavanje:** Mike Bayer, _Tutorial: SQLAlchemy 2.0_, Python Web Conf 2023
**Obrađeni transkript:** 1:10:00–1:22:32
**Tema:** `label()`, `WHERE` izrazi, parametri i SQL injection, operatori, `IN`, `ORDER BY`, string SQL izrazi i JOIN tipovi.

Ovo je pretposlednja lekcija ovog dela kursa. Transkript pravi brzi pregled SQLAlchemy Core izraza i načina na koji se oni grade od tipizovanih ORM atributa. Neki obrasci su prikazani kao demonstracija širine API-ja; ova beleška ih objašnjava, ali ne tvrdi da su sve SQL funkcije i JOIN varijante detaljno obrađene.

## Label-e: imenuj rezultat SELECT izraza

SQLAlchemy može automatski napraviti ime izlazne kolone, ali se ne treba oslanjati na automatske, dugačke ili dijalekt-specifične nazive. `label()` pravi alias za izabranu kolonu ili SQL izraz:

```python
statement = select(
	User.name.label("username"),
	Address.email_address.label("email"),
)
```

Približan SQL:

```sql
SELECT user_account.name AS username,
       address.email_address AS email
FROM ...
```

Label utiče na ime kolone u rezultatu. Kada dobijemo `Row`, vrednosti možemo čitati imenima alias-a:

```python
with engine.connect() as connection:
	row = connection.execute(statement).first()
	if row is not None:
		print(row.username, row.email)
```

Label-e su naročito korisne kada:

- biramo istoimene kolone iz više tabela, na primer `User.id` i `Address.id`;
- biramo SQL funkciju ili izračunati izraz kome bi automatsko ime bilo nejasno;
- rezultat želimo da koristimo preko stabilnog i smislenog `row.some_name` pristupa.

Biraj jasna, dosledna imena, na primer `username`, `email_address` ili `address_count`. SQL alias i Python naziv atributa modela su povezani sa rezultatom, ali label ne menja definiciju ORM modela niti ime fizičke kolone.

## `WHERE` i class-level izrazi

U prethodnoj lekciji videli smo da `User.name` na klasi predstavlja SQLAlchemy atribut kolone. Kada ga poredimo sa Python vrednošću, SQLAlchemy vrati objekat SQL izraza, a ne `True` ili `False`:

```python
condition = User.name == "spongebob"
statement = select(User.name).where(condition)
```

Ovo odgovara SQL obliku:

```sql
SELECT user_account.name
FROM user_account
WHERE user_account.name = ?
```

SQLite koristi `?` placeholder; druga baza može koristiti drugi paramstyle. Tekstualna vrednost se šalje odvojeno kao bind parametar.

Razlikuj class-level poređenje od poređenja Python vrednosti:

```python
User.name == "spongebob"   # SQLAlchemy SQL izraz
user.name == "spongebob"   # Python bool za već učitan objekat
```

`.where(...)` dodaje uslov u SELECT iskaz. Ne izvršava ga; izvršavanje i dalje radimo preko `Connection`-a ili ORM `Session`-a.

## Zašto operatori prave SQL umesto Python rezultata?

SQLAlchemy-jev mapirani class-level atribut implementira Python operatore poput `==`, `!=`, `<` i `>`. Za SQLAlchemy kolonu ti operatori grade SQLAlchemy expression objekte:

```python
User.id > 10
User.name != "patrick"
```

Svaki izraz predstavlja levu stranu, operator i desnu stranu. Primer:

```python
condition = User.id > 10
```

Ovde `User.id` je SQL kolona, `>` je SQL operator, a `10` postaje bind parametar. Python ne izvršava proveru nad jednom vrednošću `User.id`, jer ovde radimo sa atributom klase, ne sa instancom.

U običnom Python-u `==` između dva broja daje `bool`. U SQLAlchemy-ju `User.id == 10` daje SQL uslov zato što je class-level descriptor preusmerio ponašanje operatora. Ovo je moćno, ali traži da pazimo da u `WHERE` ne koristimo slučajno instancu kada nam treba mapirana kolona.

## Bind parametri i SQL injection

Kada napišemo:

```python
statement = select(User.name).where(User.name == user_input)
```

SQLAlchemy ne umeće `user_input` direktno u SQL tekst. Vrednost se prosleđuje odvojeno kao bind parametar. Ako je vrednost:

```text
SpongeBob
```

SQL oblik ostaje isti, a tekst se šalje kao parametar. Ako je vrednost sumnjiv tekst koji liči na SQL, ona se i dalje tretira kao podatak za poređenje, a ne kao nova SQL naredba. To je osnovna odbrana od SQL injection-a.

Zato izbegavamo ručno sklapanje SQL-a f-stringom:

```python
# Ne raditi ovako sa nepoverljivim unosom
statement = text(f"SELECT name FROM user_account WHERE name = '{user_input}'")
```

Umesto toga koristimo SQLAlchemy izraz:

```python
statement = select(User.name).where(User.name == user_input)
```

ili tekstualni SQL sa eksplicitnim bind parametrom:

```python
statement = text("SELECT name FROM user_account WHERE name = :name")
rows = connection.execute(statement, {"name": user_input})
```

Kompajlirani iskaz i njegovi parametri mogu se pregledati radi dijagnostike:

```python
compiled = statement.compile(engine)
print(compiled)
print(compiled.params)
```

`literal_binds=True` može za neke tipove prikazati vrednosti unutar SQL teksta radi debug-a, ali to nije obrazac izvršavanja niti način da se bezbedno gradi query od korisničkog unosa. Vrednosti u logovima mogu biti privatne.

Bind parametri predstavljaju vrednosti, ne imena tabela ili kolona. Ako naziv kolone mora biti dinamičan, koristi dozvoljenu listu poznatih mapiranih kolona, a ne nepoverljiv string koji se umeće u SQL.

Parametrizacija omogućava SQLAlchemy-ju da isti oblik iskaza koristi sa različitim vrednostima i ponovo iskoristi kompilaciju. Pojedini drajveri i baze mogu koristiti pripremljene iskaze ili slične optimizacije, ali bind parametri sami po sebi ne garantuju server-side prepared statement za svaku kombinaciju baze i drajvera.

## Tekstualni operatori: `LIKE`, `contains()` i `ilike()`

SQLAlchemy izlaže SQL operatore i kao metode kolona:

```python
contains_statement = select(User.name).where(User.name.contains("bob"))
like_statement = select(User.name).where(User.name.like("s%"))
ilike_statement = select(User.name).where(User.name.ilike("%SANDY%"))
```

- `like("s%")` odgovara SQL `LIKE` obrascu. `%` znači nula ili više znakova, a `_` tačno jedan znak.
- `contains("bob")` traži tekst koji sadrži `bob`; uobičajeno se prevodi u LIKE obrazac sa `%` oko vrednosti.
- `ilike(...)` traži case-insensitive LIKE ponašanje, ali tačna implementacija zavisi od dijalekta. SQLite može izraziti poređenje preko `LOWER(...) LIKE LOWER(...)`, dok PostgreSQL ima `ILIKE` operator.

Osetljivost na velika i mala slova, kolacija i escaping wildcard znakova zavise od baze. Zato izraz koji radi na SQLite testu ne mora imati sasvim iste tekstualne ili jezičke osobine na PostgreSQL-u ili MySQL-u.

`contains()` je substring pretraga, ne isto što i indeksirana pretraga prefiksa. Obrazac koji počinje wildcard-om, poput `%tekst%`, često ne može koristiti običan B-tree indeks za efikasnu pretragu. Za veliki skup podataka može biti potreban full-text indeks ili drugi pristup.

## `IN` i expanding parametri

Za proveru da li vrednost pripada listi koristimo `.in_(...)`:

```python
statement = select(User.name).where(
	User.name.in_(["spongebob", "patrick", "sandy"])
)
```

Semantički ovo odgovara SQL-u:

```sql
WHERE user_account.name IN (?, ?, ?)
```

Broj vrednosti nije uvek poznat kada se `Select` objekat pravi. SQLAlchemy zato koristi ekspandirajući bind parametar: pri izvršavanju proširiće listu na odgovarajući broj placeholder-a. U debug prikazu može se videti oznaka poput `__[POSTCOMPILE_name_1]`; to je normalan međukorak kompilacije, a ne vrednost koju treba ručno menjati.

Svaka vrednost liste i dalje se šalje kao bind parametar. Ako se ista iskazna struktura izvrši sa drugačijim brojem vrednosti, SQLAlchemy prilagođava placeholder-e pri izvršavanju.

Za skup vrednosti koji može biti prazan, SQLAlchemy obezbeđuje dijalektu odgovarajući izraz koji daje prazan rezultat. U poslovnom kodu i dalje odluči da li prazan filter treba da znači „ne vrati ništa“ ili „nemoj primeniti filter“; to su različita pravila aplikacije.

## Kombinovanje uslova: AND i OR

Ako `where()` dobije više uslova, oni se podrazumevano kombinuju sa SQL `AND`:

```python
statement = select(User.name).where(
	User.id > 1,
	User.name != "patrick",
)
```

To je slično:

```sql
WHERE user_account.id > ? AND user_account.name != ?
```

Isto važi ako pozovemo `.where(...)` više puta; kriterijumi se dodaju iskazu i kombinuju sa `AND`.

Za eksplicitno kombinovanje postoji `and_()` i `or_()`:

```python
from sqlalchemy import and_, or_

all_conditions = and_(User.id > 1, User.name != "patrick")
either_condition = or_(User.name == "sandy", User.name == "patrick")

statement = select(User.name).where(either_condition)
```

SQLAlchemy takođe preusmerava bitwise `&`, `|` i `~` da predstavljaju SQL `AND`, `OR` i `NOT`:

```python
statement = select(User.name).where(
	(User.id > 1) & (User.name != "patrick")
)

statement = select(User.name).where(
	(User.name == "sandy") | (User.name == "patrick")
)
```

Svaki uslov mora biti u zagradama kada kombinujemo `&` ili `|`. Python ima svoja pravila prioriteta operatora, a `&`/`|` nisu isto što i reči `and`/`or`. Nemoj pisati:

```python
# Pogrešno za SQLAlchemy SQL izraze
(User.id > 1) and (User.name != "patrick")
```

Python `and` pokušava da izračuna istinitost izraza odmah, dok SQLAlchemy uslov treba da ostane deo SQL stabla. Koristi zagrađene `&`/`|`, odnosno `and_()`/`or_()`.

Za SQL `NULL` koristi SQL semantiku `IS NULL`, ne Pythonovo poređenje sa običnom vrednošću:

```python
statement = select(User.name).where(User.fullname.is_(None))
```

SQLAlchemy tako emituje `fullname IS NULL`. Za ne-null vrednosti postoji `.is_not(None)`.

## Ulančavanje izraza i `ORDER BY`

SQLAlchemy `Select` objekti su generativni: `.where()`, `.order_by()` i slične metode vraćaju novi prošireni iskaz, ne menjaju objekat u mestu.

```python
statement = select(User.id, User.name)
statement = statement.where(User.id > 1)
statement = statement.order_by(User.name, User.id.desc())
```

Pozivi mogu da se ulančaju:

```python
statement = (
	select(User.id, User.name)
	.where(User.id > 1)
	.order_by(User.name.asc(), User.id.desc())
)
```

`order_by()` prima izraze za sortiranje:

- `User.name` sortira uzlazno podrazumevano;
- `User.name.asc()` eksplicitno traži uzlazno;
- `User.id.desc()` traži silazno.

Ako više redova ima istu vrednost prve kolone, dodaj još kolona u `ORDER BY` da dobiješ stabilan i predvidljiv redosled. Bez `ORDER BY` baza ne garantuje redosled.

## SQL izraz nad tekstom

SQLAlchemy može da pravi i izračunate kolone. Predavač prikazuje literalni tekst spojen sa korisničkim imenom:

```python
from sqlalchemy import literal

display_name = (literal("User: ") + User.name).label("display_name")
statement = select(display_name)
```

`literal("User: ")` pravi SQLAlchemy literal vrednost koja se normalno šalje kao bind parametar. `+` je preusmeren na SQL string konkatenaciju za tekstualni operand; za numeričke kolone isti operator može predstavljati sabiranje. Konkretan SQL za konkatenaciju zavisi od dijalekta.

Izračunati izraz može se označiti sa `.label("display_name")`, a rezultat zatim čitati preko `row.display_name`. To je praktičnije od oslanjanja na automatsko ime izraza.

U primerima za brojčane izraze operatori se takođe pretvaraju u SQL:

```python
price_with_tax = Product.price * 1.2
```

Ovo gradi SQL izraz i ne računa Python rezultat dok se query ne izvrši u bazi. Tipovi i pravila računanja određuju ponašanje; ako mešamo tekstualne i numeričke tipove, treba eksplicitno voditi računa o konverzijama.

## JOIN tipovi

### INNER JOIN

Standardni `.join_from(User, Address)` je INNER JOIN. Prikazuje samo parove redova koji zadovoljavaju JOIN uslov. Korisnik bez adrese se ne pojavljuje.

```python
statement = select(User.name, Address.email_address).join_from(User, Address)
```

### LEFT OUTER JOIN

LEFT OUTER JOIN zadržava sve redove sa leve strane, čak i kada desna strana nema poklapanje. Za korisnika bez adrese, kolone iz `Address` rezultata imaju `None`:

```python
statement = select(User.name, Address.email_address).outerjoin_from(
	User,
	Address,
)
```

Pošto SQLAlchemy metadata sadrži FK, može da izvede i ovde `ON user_account.id = address.user_id`. Ako korisnik ima dve adrese, biće dva rezultujuća reda; ako nema nijednu, biće jedan red sa `email_address is None`.

### RIGHT JOIN i obrnuti redosled

Ako je cilj „zadrži sve adrese i eventualno poveži korisnika“, može se obrnuti redosled strana u LEFT OUTER JOIN-u:

```python
statement = select(Address.email_address, User.name).outerjoin_from(
	Address,
	User,
)
```

To je ekvivalentna ideja RIGHT OUTER JOIN-a iz perspektive početnog redosleda `User RIGHT JOIN Address`: svi `Address` redovi ostaju, čak i kada korisnička strana nema poklapanje. U ovom modelu `Address.user_id` je obavezan FK, pa normalno stanje ne bi trebalo da sadrži adresu bez korisnika ako baza sprovodi constraint, ali obrazac objašnjava smer JOIN-a.

### FULL OUTER JOIN

FULL OUTER JOIN zadržava nepoklopljene redove sa obe strane. SQLAlchemy ga može izraziti preko `full=True`:

```python
statement = select(User.name, Address.email_address).outerjoin_from(
	User,
	Address,
	full=True,
)
```

Podrška zavisi od konkretne baze i njenog dijalekta; proveri kompatibilnost pre upotrebe u produkciji. Uobičajeni INNER i LEFT OUTER JOIN obrasci su dovoljni za većinu početnih primera.

### Kada treba ON uslov navesti ručno?

SQLAlchemy može zaključiti `ON` preko FK metadata-e kada postoji jedna jasna veza. Ako nema FK metadata-e ili između tabela postoji više FK puteva, treba navesti uslov:

```python
statement = select(User.name, Address.email_address).outerjoin_from(
	User,
	Address,
	User.id == Address.user_id,
)
```

SQLAlchemy ne treba da bira nasumično između dvosmislenih putanja. Ako nije jasno kako se tabele povezuju, eksplicitan `ON` je i čitljiviji i bezbedniji.

## Tekstualni SQL i SQLAlchemy izrazi

Sve opisane operacije mogu se napisati tekstualnim SQL-om preko `text()`. SQLAlchemy Core izrazi nisu obavezni. Prednost Core izraza je kompozicija iz tipizovanih Python objekata: atributi kolona nose metadata, bind parametri se prave automatski, a dijalekat prevodi SQL prema bazi.

To ne znači da je SQLAlchemy izraz univerzalan za svaku bazu u svim slučajevima. Generički operatori poput poređenja i osnovnih JOIN-ova uglavnom se prilagođavaju, ali specifične JSON funkcije, string funkcije, tipovi i operatorska semantika mogu biti vezani za određeni backend. I dalje treba razumeti SQL i mogućnosti ciljane baze.

## Sažetak za ponavljanje

- `.label("alias")` daje stabilno ime izlaznoj koloni ili izračunatom izrazu.
- `User.name == value` pravi SQL uslov i bind parametar; `user.name == value` poredi Python vrednost instance.
- `.where()` dodaje WHERE izraz; više kriterijuma se spaja sa AND.
- Za AND/OR koristi `and_()`/`or_()` ili zagrađene `&`/`|`; ne koristi Python `and`/`or` nad SQL izrazima.
- `in_([...])` koristi expanding parametar koji se širi pri izvršavanju.
- `.like()`, `.contains()` i `.ilike()` daju tekstualne filtere čije detalje može određivati dijalekt/kolacija.
- `order_by()` definiše rezultatni redosled; bez njega redosled nije garantovan.
- SQL operatori na class-level ORM atributima grade SQL izraze; `literal()` pravi vrednost koja se šalje kao parametar.
- INNER JOIN zadržava poklopljene redove; LEFT OUTER JOIN čuva sve redove leve strane; desni join može se prikazati obrnutim levim join-om.
- FULL OUTER JOIN podržavaju samo odgovarajuće baze/dijalekti.
- `text()` ostaje validan izbor kada želimo ručno napisati SQL; Core izrazi pomažu u kompoziciji i tipizaciji.

## Vežbe za playground

Radi u zasebnom fajlu u `playground/sqlalchemy_2/` uz postojeći root `.venv`.

1. Dodaj `label()`-e za username i email u JOIN upitu i čitaj ih preko `row.username` i `row.email`.
2. Filtriraj imena sa `==`, `!=`, `<` ili `>`; pregledaj SQL i bind parametre.
3. Koristi `like("s%")`, `contains("bob")` i `ilike("%SANDY%")`; uporedi SQLite rezultat i generisani SQL.
4. Primeni `in_(["spongebob", "patrick"])` i pogledaj expanding placeholder pre i posle izvršavanja.
5. Kombinuj uslove sa više `.where()` poziva, `and_()` i `or_()`; zatim uporedi sa zagrađenim `&` i `|` izrazima.
6. Napravi izračunatu label-u koristeći `literal("User: ") + User.name`.
7. Uporedi INNER JOIN i LEFT OUTER JOIN za korisnika bez adrese; proveri `None` u email koloni.
8. Probaj FULL OUTER JOIN samo ako ga tvoja lokalna SQLite verzija podržava; nemoj pretpostaviti da svaki produkcioni backend ima isti operator.
