# Lekcija 06: Uobičajeni tipovi kolona

## Cilj lekcije

ERD (Entity-Relationship Diagram) opisuje koje podatke sistem čuva, a model treba da opiše kakva je svaka kolona i koje vrednosti može da predstavlja. U ovoj lekciji dodajemo uobičajene SQLAlchemy tipove u postojeće deklarativne modele:

- tekst promenljive dužine: `String`;
- duži tekst: `Text`;
- cele brojeve: `SmallInteger` i `Integer`;
- decimalne brojeve: `Numeric`;
- logičke vrednosti: `Boolean`.

Glavni cilj nije samo memorisanje naziva tipova. Treba razumeti kakvu vrednost aplikacija želi da čuva, koji SQLAlchemy tip to opisuje i kako izabrani dijalekt (npr. `PostgreSQL`, `SQLite`) prevodi taj tip u tip konkretne baze.

---

## Od atributa ERD-a do tipa kolone

Entitet (npr. `Kategorija`) u ERD-u ima atribute; atribut se pri modelovanju obično pretvara u kolonu. Za svaku kolonu razmišljamo o sledećem:

1. Koji podatak se čuva: `tekst`, `ceo broj`, `decimalni iznos` ili `logičko stanje`?
2. Da li postoje `ograničenja dužine, opsega, preciznosti ili obaveznosti`?
3. Koji SQLAlchemy generički tip (`String`, `Text`, `SmallInteger`, `Integer`, `Numeric`, `Boolean`) najbolje opisuje podatak?
4. Koji tip i ponašanje će odabrani sistem baze (npr. `PostgreSQL`, `SQLite`) stvarno primeniti? Ovo je važno jer različite baze mogu imati različite implementacije istog SQLAlchemy tipa.

Primer toka za naziv kategorije:

```text
ERD: name, tekst do 100 znakova
				-> SQLAlchemy: String(50) u kursnom modelu
				-> PostgreSQL DDL: tip s ograničenjem dužine, tipično VARCHAR(50)
```

Primer pokazuje i zašto treba porediti ERD i kod: u ovom slučaju ERD i postojeći model se ne slažu oko dužine.

`DDL` (Data Definition Language) opisuje SQL komande koje kreiraju i modifikuju strukturu baze, kao što su `CREATE TABLE` i `ALTER TABLE`. U primeru iznad, `PostgreSQL DDL` pokazuje kako će konkretna baza (`PostgreSQL`) interpretirati SQLAlchemy tipove, pa se tako SQLAlchemy `String(50)` prevodi u PostgreSQL `VARCHAR(50)`.

Ovo prevođenje se naziva **type mapping** ili mapiranje tipova. Njega izvršava `SQLAlchemy dijalekt` za odabranu bazu (npr. `PostgreSQL`, `SQLite`).

PITANJE: Da li se dijalekt nalazi u `ORM` delu `SQLAlchemy`-ja ili u `Core` delu?

ODGOVOR: Dijalekt nije posebno deo ni `ORM`-a ni `Core`-a; to je SQLAlchemy komponenta koja poznaje specifičnosti određene baze. `Engine`, obično napravljen pomoću `create_engine()` i database URL-a, bira dijalekt. ORM i Core koriste isti `Engine`/dijalekt za generisanje i izvršavanje upita. Zato se dijalekt ne podešava posebno zato što koristimo ORM.

---

## Tri sloja tipova

Važno je razlikovati tri stvari:

1. **Python tip i ORM anotacija:** u `Mapped[str]`, `str` je Python tip vrednosti, a `Mapped` je SQLAlchemy anotacija koja označava ORM-mapirani atribut. SQLAlchemy može iz Python tipa da zaključi podrazumevani SQLAlchemy tip pomoću svoje mape anotacija; anotacija takođe može da utiče na nullability. Za precizan tip ili dužinu, kao `String(50)`, tip se zadaje u `mapped_column()`.
2. **SQLAlchemy tip kolone:** `String(50)` i `Numeric(10, 2)` su SQLAlchemy tipovi iz sistema `TypeEngine`. Oni opisuju tip kolone na prenosiv način i koriste se, između ostalog, za obradu vrednosti i kompajliranje DDL-a. ORM i Core koriste ovaj sistem tipova; ne prevode ga nezavisno jedan od drugog.
3. **SQL tip konkretne baze:** dijalekt kompajlira SQLAlchemy tip u tip koji podržava izabrana baza, na primer PostgreSQL `VARCHAR`, `TEXT`, `SMALLINT`, `INTEGER`, `NUMERIC` ili `BOOLEAN`. To je deklarisani SQL tip kolone, a ne nužno opis njenog fizičkog načina skladištenja; implementacija i ponašanje zavise od baze.

Primer toka je: deklaracija `Mapped[str] = mapped_column(String(50))` -> SQLAlchemy tip `String(50)` -> PostgreSQL SQL tip `VARCHAR(50)`. SQLAlchemy nije sama baza; dijalekt obavlja prevođenje, a detalji mogu da se razlikuju između PostgreSQL-a, SQLite-a i drugih sistema.

Na primer, `SQLite` koristi `type affinity` (tipove kolona određuje prema tipu vrednosti koje se unose npr. `INTEGER`, `TEXT`, `BLOB`), pa se njegovo ponašanje ne može uvek poistovetiti sa `PostgreSQL`-ovim tipovima i ograničenjima.

---

## Kako se kolona deklariše u priloženom kodu (stari stil)

Kurs koristi klasični declarative oblik:

```python
from sqlalchemy import Boolean, Column, Integer, Numeric, SmallInteger, String, Text


class Category(Base):
		__tablename__ = "category"

		name = Column(String(50))
		slug = Column(String(55))
		is_active = Column(Boolean)
		level = Column(SmallInteger)
```

`Column(...)` predstavlja deklaraciju kolone. Prvi argument opisuje tip, a dodatni imenovani argumenti mogu da definišu opcije i ograničenja, kao što su `nullable=False` ili `unique=True`. Ova lekcija se uglavnom fokusira na tipove; detaljnija pravila slede kasnije.

U klasi modela atribut kao `name` izgleda kao uobičajen Python atribut, ali nije obična promenljiva klase.

SQLAlchemy mapira atribut klase na kolonu i obezbeđuje ORM instrumentaciju (npr. praćenje promena, lenjo (lazy) učitavanje, itd.).

Na instanci modela čitaš i menjaš vrednost kolone (npr. `instance.name` ili `instance.slug`), dok se nad atributom klase mogu graditi SQL izrazi(npr. `Category.name == "Some Name"`).

---

### Nazivi u našem praktičnom paketu

Kursni primeri i snapshot-i zadržavaju engleska imena. U praktičnim modelima koristimo srpske ASCII identifikatore, a SQLAlchemy tipove i API nazive ostavljamo nepromenjene:

| Kursni model      | Praktični model      | Kursna polja                                                      | Praktična polja                                         |
| ----------------- | -------------------- | ----------------------------------------------------------------- | ------------------------------------------------------- |
| `Category`        | `Kategorija`         | `name`, `slug`, `is_active`, `level`                              | `naziv`, `slug`, `aktivna`, `nivo`                      |
| `PromotionEvent`  | `PromotivniDogadjaj` | `name`, `price_reduction`                                         | `naziv`, `umanjenje_cene`                               |
| `Product`         | `Proizvod`           | `name`, `slug`, `description`, `is_digital`, `is_active`, `price` | `naziv`, `slug`, `opis`, `digitalni`, `aktivan`, `cena` |
| `StockManagement` | `StanjeZaliha`       | `quantity`                                                        | `kolicina`                                              |
| `User`            | `Korisnik`           | `username`, `email`, `password`                                   | `korisnicko_ime`, `email`, `lozinka`                    |
| `OrderProduct`    | `StavkaPorudzbine`   | `quantity`                                                        | `kolicina`                                              |

`Order`/`Porudzbina` i `ProductPromotionEvent`/`VezaProizvodaIPromocije` u ovoj lekciji još nemaju dodatna polja. Prevod naziva ne menja tipove ni pravila iz source-a.

---

## `String`: tekst sa poznatom dužinom

`String(length)` opisuje tekstualnu kolonu promenljive dužine sa navedenom dužinom. Primeri iz kursnog koda su:

```python
name = Column(String(50))
slug = Column(String(55))
username = Column(String(50))
email = Column(String(255))
```

Moderni ORM-ovi, uključujući SQLAlchemy, ne primenjuju ograničenja dužine stringa na nivou objektnog modela; to je odgovornost baze podataka.

```python
name: Model[str] = model_column(String(50))
slug: Model[str] = model_column(String(55))
username: Model[str] = model_column(String(50))
email: Model[str] = model_column(String(255))
```

NAPOMENA: SQLAlchemy ne ograničava dužinu stringa na nivou ORM-a; ograničenje se primenjuje na nivou baze. Ovo znači da dužina stringa nije automatski proveravana od strane ORM-a, već se oslanja na mehanizme baze podataka i tek kada se pokuša unos predugačke vrednosti, baza će ga odbiti.

Pod PostgreSQL-om, `String(50)` se tipično generiše kao `VARCHAR(50)`. Ograničenje dužine je deo definicije tipa baze; ako se pokuša unos predugačke vrednosti, baza može odbiti unos. Ne treba računati da svaka baza sprovodi `VARCHAR(n)` na isti način: na primer SQLite ne sprovodi dužinu `VARCHAR` kao PostgreSQL.

`String` se koristi za vrednosti čiji je sadržaj tekst, uključujući slova, cifre i znakove, kao što su `ime`, `slug` ili `email`.

Ako je `podatak broj nad kojim se obavljaju računske operacije`, treba izabrati `numerički tip` (`SmallInteger`, `Integer`, `BigInteger`, `Float` itd.), čak i kada njegov tekstualni prikaz sadrži samo cifre (npr. brojevi telefona tipa `+381641234567`).

SQLAlchemy dozvoljava `String` i bez dužine u nekim kontekstima, ali što se tiče konkretnih baza, dužina može biti potrebna za generisanje DDL-a. Za kolonu sa unapred poznatom maksimalnom dužinom eksplicitna granica čini nameru jasnijom.

---

## `Text`: duži tekst

`Text` je namenjen tekstualnom sadržaju čija je dužina velika ili se unapred ne ograničava malim brojem znakova:

```python
description = Column(Text)
```

U PostgreSQL-u se tipično prevodi u `TEXT`.

Ovo ne znači beskonačan prostor: `veličina podataka je i dalje ograničena mogućnostima baze i resursima sistema`. Na primer, PostgreSQL `TEXT` kolona može sadržati do 1 GB teksta.

Razlika između `String(n)` i `Text` je u tome što prvi nameće ograničenje dužine na nivou baze, dok kod drugog takvo ograničenje ne postoji. `Text` je pogodniji za kolone sa nepredvidivom ili velikom količinom teksta.

Takođe, za `PostgreSQL`, `VARCHAR(n)` i `TEXT` često imaju slične karakteristike performansi i skladištenja.

Izbor `String(n)` je prvenstveno koristan kada je ograničenje dužine poslovno pravilo koje baza treba da sprovodi na nivou same baze.

`Text` je praktičan za opise, beleške i duži sadržaj. Ovo je naročito korisno kada se očekuje da tekst može biti veoma dug ili nepredvidive dužine.

---

## `SmallInteger` i `Integer`: celi brojevi

`SmallInteger` i `Integer` opisuju cele brojeve. U PostgreSQL-u se tipično prevode u `SMALLINT` i `INTEGER`.

| SQLAlchemy tip | PostgreSQL tip | Uobičajeni raspon PostgreSQL-a     |
| -------------- | -------------- | ---------------------------------- |
| `SmallInteger` | `SMALLINT`     | od -32 768 do 32 767               |
| `Integer`      | `INTEGER`      | od -2 147 483 648 do 2 147 483 647 |
| `BigInteger`   | `BIGINT`       | širi, 64-bitni celobrojni raspon   |

Rasponi su svojstvo PostgreSQL-a; u drugim bazama proveri dokumentaciju njihovog dijalekta. Izaberi najmanji tip koji pouzdano pokriva validan domen vrednosti, ali nemoj koristiti `SmallInteger` samo zato što trenutni primeri imaju male brojeve ako sistem može rasti.

U kursnom kodu:

- `Category.level` koristi `SmallInteger`;
- `PromotionEvent.price_reduction`, `StockManagement.quantity` i `OrderProduct.quantity` koriste `Integer`.

Tip baze ne zamenjuje validaciju aplikacije. Ako je `level` dozvoljen samo od 0 do 10, sam `SmallInteger` ne sprovodi taj poslovni opseg; za to su potrebni odgovarajuća validacija polja (`field validation`) ili odgovarajuće ograničenje (`CHECK`), što dolazi u kasnijim lekcijama.

---

## `Boolean`: logičke vrednosti

`Boolean` predstavlja logičko stanje, u Pythonu najčešće `True` ili `False`:

```python
# Stari način definisanja statusa kolona u SQLAlchemy-ju preko `Column` objekta
is_active = Column(Boolean)
is_digital = Column(Boolean)
```

```python
# Novi način definisanja statusa kolona u SQLAlchemy-ju preko `Mapped` i `mapped_column`
is_active: Mapped[bool] = mapped_column(Boolean)
is_digital: Mapped[bool] = mapped_column(Boolean)
```

PostgreSQL ima izvorni tip `BOOLEAN`. SQLAlchemy prevodi tip prema dijalektu; pojedine druge baze imaju drugačiji način predstavljanja logičkih vrednosti.

`Boolean` i `nullable` su različite osobine. Boolean kolona koja dopušta `NULL` ima tri moguća stanja: `True`, `False` i nepoznato/nepostavljeno (`NULL`). Ako je poslovno pravilo strogo binarno, kolona obično treba da bude obavezna (`nullable=False`) i eventualno da ima `default=False`. Obično se za default vrednost uzima `False` zbog poslovne logike na nivou aplikacije. Naprimer `is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)` pretpostavlja da je korisnik neaktivan sve dok se ne aktivira i is_active postane `True`; ovo je tipičan obrazac za logičke zastavice u aplikacijama.

---

## `Numeric(precision, scale)`: decimalna preciznost

Kurs koristi stari način definisanja kolona u SQLAlchemy-ju preko `Column` objekta:

```python
price = Column(Numeric(10, 2))
```

Novi način definisanja kolona u SQLAlchemy-ju preko `Mapped` i `mapped_column` je sledeći:

```python
price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
```

`Numeric(precision, scale)` prima dva važna argumenta:

- **precision** je ukupan broj cifara;
- **scale** je broj cifara desno od decimalnog separatora.

Zato `Numeric(10, 2)` znači ukupno 10 cifara, od čega su 2 decimalne. Preostaje najviše 8 cifara levo od separatora. U PostgreSQL-u tipično odgovara `NUMERIC(10, 2)`, čiji pozitivni maksimum iznosi `99 999 999.99`.

`Numeric` je posebno koristan za novčane iznose zato što predstavlja decimalne vrednosti, a ne binarne floating-point aproksimacije. SQLAlchemy `Numeric` podrazumevano vraća Python `Decimal` vrednosti (`asdecimal=True`). Sačuvaj tu semantiku i pri računanju; nemoj bez potrebe pretvarati novac u `float`, jer binarni float ne može tačno predstaviti mnoge decimalne vrednosti.

Pri unosu vrednosti sa više decimalnih mesta od deklarisanog `scale`, zaokruživanje ili odbijanje zavisi od baze i njenih pravila. Takođe, prekoračenje ukupne preciznosti može dovesti do greške. Zato preciznost i skalu biraj prema stvarnim poslovnim pravilima.

---

## Zašto SQLAlchemy tip nije isto što i validacija

Tip kolone opisuje koje vrednosti baza može da sačuva i često utiče na način skladištenja i poređenja. Ipak, on ne proverava sva poslovna pravila.

Primeri:

- `String(50)` ograničava dužinu u bazama koje sprovode ograničenje tog tipa; ne proverava da li je naziv smislen.
- `Integer` prihvata ceo broj u rasponu tipa; ne zna da li količina treba da bude pozitivna.
- `Numeric(10, 2)` određuje preciznost i skalu; ne zna da li cena sme biti negativna.
- `Boolean` predstavlja logičku vrednost; ne određuje podrazumevano stanje niti da li je `NULL` dozvoljen.

Za ostala pravila koriste se `nullable`, `default vrednosti`, `CHECK` ograničenja, `jedinstvenost` i `validacija` aplikacije.

---

## Kako se SQLAlchemy tip prevodi u bazu

Tok izgleda ovako:

```text
Python model
	-> SQLAlchemy anotacija `Mapped` i `mapped_column` koji definišu kolone u modelu
	-> SQLAlchemy dijalekt izabranog engine-a
	-> SQL tip specifičan za bazu
```

Na primer, `Integer` će se prevesti u odgovarajući celobrojni tip konkretnog sistema. PostgreSQL i SQLite ne moraju identično da sprovode ograničenja ili skladište iste deklaracije. Ako je važno koji je tačno tip nastao, proveri generisani DDL ili samu šemu baze u modulu o kreiranju tabela.

SQLAlchemy tipovi zato predstavljaju prenosivu nameru, ali ne garantuju potpuno identično ponašanje u svakom dijalektu. PostgreSQL dokumentacija je važna jer je to baza koju kurs koristi, dok SQLAlchemy dokumentacija objašnjava Python tipove i njihovo mapiranje.

---

## Šta je dodato u modelima iz skripte?

Skripta `3_common_field_types.py` dodaje tipove na nekoliko modela:

| Model             | Atributi iz primera                                               | SQLAlchemy tipovi                                                          |
| ----------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `Category`        | `name`, `slug`, `is_active`, `level`                              | `String(50)`, `String(55)`, `Boolean`, `SmallInteger`                      |
| `PromotionEvent`  | `name`, `price_reduction`                                         | `String(50)`, `Integer`                                                    |
| `Product`         | `name`, `slug`, `description`, `is_digital`, `is_active`, `price` | `String(50)`, `String(55)`, `Text`, `Boolean`, `Boolean`, `Numeric(10, 2)` |
| `StockManagement` | `quantity`                                                        | `Integer`                                                                  |
| `User`            | `username`, `email`, `password`                                   | `String(50)`, `String(255)`, `String(100)`                                 |
| `OrderProduct`    | `quantity`                                                        | `Integer`                                                                  |

`ProductPromotionEvent` i `Order` u ovom koraku još nemaju polja. Datumska polja i ključevi izostavljeni su jer se obrađuju u drugim lekcijama.

U praktičnom kodu `Mapped[...]` tipovi prate nullabilnost kolona: na primer, `Mapped[str | None]` za kursna polja koja nemaju `nullable=False`, dok `Korisnik.korisnicko_ime` koristi `Mapped[str]` uz `nullable=False` i `unique=True`. Ova pravila su preneta iz source-a; njihovo detaljno značenje obrađujemo u narednim lekcijama.

---

## Razlike između ERD-a i source koda

Kod treba porediti sa ERD-om; kod u ovoj fazi nije potpuno usklađen sa svim prikazanim detaljima:

- `Category.name` je u ERD-u prikazan sa dužinom 100, a u skripti je `String(50)`.
- `Category.slug` je u ERD-u prikazan sa dužinom 120, a u skripti je `String(55)`.
- `Category.level` je u ERD-u `Integer`, a u skripti `SmallInteger`.
- `Product.name` je u ERD-u prikazan sa dužinom 200, a u skripti je `String(50)`.
- `Product.slug` je u ERD-u prikazan sa dužinom 220, a u skripti je `String(55)`.
- ERD opisuje neka `datum/vreme` polja i `atribute ključeva` koji se namerno ne obrađuju u ovoj lekciji.

Ovo su razlike specifikacije i implementacije, a ne automatski dokaz da je jedan izbor ispravan. Pre stvarne upotrebe modela odluči koja je granica nameravana i uskladi model, ERD i pravila aplikacije.

---

## Važna napomena: source snapshot još nema primarne ključeve

Skripta dodaje kolone, ali `Category` i ostali modeli još nemaju primarni ključ. Proverom u SQLAlchemy 2.0.38 utvrđeno je da se fajl zaustavlja pri mapiranju `Category` sa greškom da mapper ne može da pronađe primarne ključeve.

To je posledica redosleda progresivnih primera: primarni ključevi dolaze kasnije u kursu. Definicije tipova i dalje prikazuju nameravani oblik kolona, ali ovaj fajl nije samostalno izvršiv ORM model. Ne menjamo source skriptu u okviru teorijske lekcije.

---

## Savremeni SQLAlchemy 2.0 oblik

Kurs koristi `Column(...)`, što je i dalje podržano u SQLAlchemy 2.0. Za tipizovane modele noviji obrazac koristi `Mapped[...]` i `mapped_column(...)`:

```python
from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class Proizvod(Base):
	__tablename__ = "proizvod"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	naziv: Mapped[str | None] = mapped_column(String(50))
	slug: Mapped[str | None] = mapped_column(String(55))
	opis: Mapped[str | None] = mapped_column(Text)
	digitalni: Mapped[bool | None] = mapped_column(Boolean)
	aktivan: Mapped[bool | None] = mapped_column(Boolean)
	cena: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
```

Ovo je dopunski primer našeg tipizovanog modela, ne zamena za tačan kod transkripta. Uključuje minimalni `id` potreban našem izvršivom ORM modelu. Tipizacija Python atributa dopunjuje deklaraciju kolone; precizno ponašanje `NULL` vrednosti prati `Mapped[...]` i `nullable` podešavanja.

---

## Provera razumevanja

1. Koja je razlika između `String(50)` i `Text`?

ODGOVOR: `String(50)` ima ograničenje dužine na 50 karaktera, dok `Text` može da sadrži proizvoljno dug tekst. `PostgreSQL` tretira ove tipove kao različite kolone: `String(n)` kao `VARCHAR(n)`, a `Text` kao `TEXT`.

2. Zašto broj koji predstavlja cenu nije najbolje čuvati kao `Float`?

ODGOVOR: `Float` može da uvede greške zbog ograničene preciznosti pri reprezentaciji decimalnih brojeva. Za novac je bolje koristiti `Numeric` ili `Decimal` tipove koji čuvaju tačne vrednosti.

3. Šta znače precision i scale u `Numeric(10, 2)`?

ODGOVOR: `precision` označava ukupan broj cifara koje broj može imati, dok `scale` označava broj cifara iza decimalnog separatora. Na primer, `Numeric(10, 2)` može da čuva brojeve sa ukupno 10 cifara, od kojih su 2 iza decimalnog separatora.

4. Da li `SmallInteger` sam po sebi ograničava `level` na vrednosti od 0 do 10?

ODGOVOR: Ne, `SmallInteger` samo definiše manji opseg celih brojeva u odnosu na `Integer`, ali ne nameće konkretna ograničenja na vrednosti. Ograničenja poput 0 do 10 treba eksplicitno definisati kroz dodatne provere ili `CheckConstraint`.

5. Koja je razlika između tipa `Boolean` i obaveznosti kolone?

ODGOVOR: `Boolean` definiše tip podatka koji može biti `True` ili `False`, dok obaveznost kolone (`nullable=False`) određuje da li kolona može imati `NULL` vrednost. Dakle, kolona može biti tipa `Boolean` i istovremeno biti obavezna ili opciona.

6. Zašto PostgreSQL i SQLite mogu različito da se ponašaju iako model koristi isti SQLAlchemy tip?

ODGOVOR: SQLAlchemy tipovi se prevode kroz dijalekte u tipove specifične za bazu. PostgreSQL i SQLite imaju različite implementacije i ograničenja za iste tipove, pa se ponašanje može razlikovati.

7. Koje razlike postoje između dužina polja u ERD-u i skripti?

ODGOVOR: ERD često prikazuje apstraktne dužine polja, dok skripta sa SQLAlchemy tipovima može imati konkretna ograničenja (`String(50)`). Takođe, neke baze (`PostgreSQL`, `SQLite`) ignorišu dužinu za tipove poput `Text`.

---

## Sažetak

- Izbor tipa počinje od značenja podatka i pravila u ERD-u.
- `String(n)` je za tekst sa poznatom granicom; `Text` je za duži tekst bez male deklarisane dužine.
- `SmallInteger` i `Integer` čuvaju cele brojeve, ali podržavaju različite raspone.
- `Boolean` opisuje True/False vrednost, dok su `NULL`, obaveznost i default odvojena podešavanja.
- `Numeric(10, 2)` ima ukupno 10 cifara i dve cifre iza decimalnog separatora; decimalni separator se ne broji.
- SQLAlchemy tip prevodi se kroz dijalekt u tip izabrane baze; detalji i ograničenja zavise od baze.
- Kod je progresivni snapshot bez primarnih ključeva i zato ne može da se izvrši samostalno u ovoj fazi.
