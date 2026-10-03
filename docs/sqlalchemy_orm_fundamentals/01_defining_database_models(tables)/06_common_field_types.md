# Lekcija 06: Uobičajeni tipovi kolona

## Cilj lekcije

ERD opisuje koje podatke sistem čuva, a model treba da opiše kakva je svaka kolona i koje vrednosti može da predstavlja. U ovoj lekciji dodajemo uobičajene SQLAlchemy tipove u postojeće deklarativne modele:

- tekst promenljive dužine: `String`;
- duži tekst: `Text`;
- cele brojeve: `SmallInteger` i `Integer`;
- decimalne brojeve: `Numeric`;
- logičke vrednosti: `Boolean`.

Glavni cilj nije samo memorisanje naziva tipova. Treba razumeti kakvu vrednost aplikacija želi da čuva, koji SQLAlchemy tip to opisuje i kako izabrani dijalekt prevodi taj tip u tip konkretne baze.

## Od atributa ERD-a do tipa kolone

Entitet u ERD-u ima atribute; atribut se pri modelovanju obično pretvara u kolonu. Za svaku kolonu razmišljamo o sledećem:

1. Koji podatak se čuva: tekst, ceo broj, decimalni iznos ili logičko stanje?
2. Da li postoje ograničenja dužine, opsega, preciznosti ili obaveznosti?
3. Koji SQLAlchemy generički tip najbolje opisuje podatak?
4. Koji tip i ponašanje će odabrani sistem baze stvarno primeniti?

Primer toka za naziv kategorije:

```text
ERD: name, tekst do 100 znakova
				-> SQLAlchemy: String(50) u kursnom modelu
				-> PostgreSQL DDL: tip s ograničenjem dužine, tipično VARCHAR(50)
```

Primer pokazuje i zašto treba porediti ERD i kod: u ovom slučaju ERD i postojeći model se ne slažu oko dužine.

## Tri sloja tipova

Važno je razlikovati tri stvari:

1. **Python tip** opisuje vrednost koju kod koristi, na primer `str`, `int`, `Decimal` ili `bool`.
2. **SQLAlchemy tip** opisuje kolonu na način koji ORM i SQLAlchemy Core mogu prevesti, na primer `String(50)` ili `Numeric(10, 2)`.
3. **Tip baze** je tip koji podržava konkretna baza, na primer PostgreSQL `VARCHAR`, `TEXT`, `SMALLINT`, `INTEGER`, `NUMERIC` ili `BOOLEAN`.

SQLAlchemy nije sama baza. Njegov dijalekt prevodi generički SQLAlchemy tip u odgovarajući SQL za povezanu bazu. Imena i detalji mogu da se razlikuju između PostgreSQL-a, SQLite-a i drugih sistema.

## Kako se kolona deklariše u priloženom kodu

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

U klasi modela atribut kao `name` izgleda kao uobičajen Python atribut, ali nije obična promenljiva klase. SQLAlchemy ga mapira na kolonu i obezbeđuje ORM instrumentaciju. Na instanci modela čitaš i menjaš vrednost, dok se nad atributom klase mogu graditi SQL izrazi.

## `String`: tekst sa poznatom dužinom

`String(length)` opisuje tekstualnu kolonu promenljive dužine sa navedenom dužinom. Primeri iz koda su:

```python
name = Column(String(50))
slug = Column(String(55))
username = Column(String(50))
email = Column(String(255))
```

Pod PostgreSQL-om, `String(50)` se tipično generiše kao `VARCHAR(50)`. Ograničenje dužine je deo definicije tipa baze; ako se pokuša unos predugačke vrednosti, baza može odbiti unos. Ne treba računati da svaka baza sprovodi `VARCHAR(n)` na isti način: na primer SQLite ne sprovodi dužinu `VARCHAR` kao PostgreSQL.

`String` se koristi za vrednosti čiji je sadržaj tekst, uključujući slova, cifre i znakove, kao što su ime, slug ili email. Ako je podatak broj nad kojim se obavljaju računske operacije, treba izabrati numerički tip, čak i kada njegov tekstualni prikaz sadrži samo cifre.

SQLAlchemy dozvoljava `String` i bez dužine u nekim kontekstima, ali konkretnim bazama dužina može biti potrebna za generisanje DDL-a. Za kolonu sa unapred poznatom maksimalnom dužinom eksplicitna granica čini nameru jasnijom.

## `Text`: duži tekst

`Text` je namenjen tekstualnom sadržaju čija je dužina velika ili se unapred ne ograničava malim brojem znakova:

```python
description = Column(Text)
```

U PostgreSQL-u se tipično prevodi u `TEXT`. To ne znači beskonačan prostor: veličina podataka je i dalje ograničena mogućnostima baze i resursima sistema. Znači da model ne zadaje malo ograničenje poput `String(50)`.

Za PostgreSQL, `VARCHAR(n)` i `TEXT` često imaju slične karakteristike performansi i skladištenja. Izbor `String(n)` je prvenstveno koristan kada je ograničenje dužine poslovno pravilo koje baza treba da sprovodi; `Text` je praktičan za opise, beleške i duži sadržaj.

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

Tip baze ne zamenjuje validaciju aplikacije. Ako je `level` dozvoljen samo od 0 do 10, sam `SmallInteger` ne sprovodi taj poslovni opseg; za to su potrebni validacija ili odgovarajuće ograničenje, što dolazi u kasnijim lekcijama.

## `Boolean`: logičke vrednosti

`Boolean` predstavlja logičko stanje, u Pythonu najčešće `True` ili `False`:

```python
is_active = Column(Boolean)
is_digital = Column(Boolean)
```

PostgreSQL ima izvorni tip `BOOLEAN`. SQLAlchemy prevodi tip prema dijalektu; pojedine druge baze imaju drugačiji način predstavljanja logičkih vrednosti.

`Boolean` i `nullable` su različite osobine. Boolean kolona koja dopušta `NULL` ima tri moguća stanja: `True`, `False` i nepoznato/nepostavljeno (`NULL`). Ako je poslovno pravilo strogo binarno, kolona obično treba da bude obavezna (`nullable=False`) i eventualno da ima default; ta podešavanja nisu deo samog tipa `Boolean`.

## `Numeric(precision, scale)`: decimalna preciznost

Kurs koristi:

```python
price = Column(Numeric(10, 2))
```

`Numeric(precision, scale)` prima dva važna argumenta:

- **precision** je ukupan broj cifara;
- **scale** je broj cifara desno od decimalnog separatora.

Zato `Numeric(10, 2)` znači ukupno 10 cifara, od čega su 2 decimalne. Preostaje najviše 8 cifara levo od separatora. U PostgreSQL-u tipično odgovara `NUMERIC(10, 2)`, čiji pozitivni maksimum iznosi `99 999 999.99`.

Decimalni separator nije cifra i ne ulazi u precision. Dakle, formulacija iz transkripta da se računa „maksimalan broj brojeva uključujući decimalnu tačku“ nije precizna.

`Numeric` je posebno koristan za novčane iznose zato što predstavlja decimalne vrednosti, a ne binarne floating-point aproksimacije. SQLAlchemy `Numeric` podrazumevano vraća Python `Decimal` vrednosti (`asdecimal=True`). Sačuvaj tu semantiku i pri računanju; nemoj bez potrebe pretvarati novac u `float`, jer binarni float ne može tačno predstaviti mnoge decimalne vrednosti.

Pri unosu vrednosti sa više decimalnih mesta od deklarisanog `scale`, zaokruživanje ili odbijanje zavisi od baze i njenih pravila. Takođe, prekoračenje ukupne preciznosti može dovesti do greške. Zato preciznost i skalu biraj prema stvarnim poslovnim pravilima.

## Zašto SQLAlchemy tip nije isto što i validacija

Tip kolone opisuje koje vrednosti baza može da sačuva i često utiče na način skladištenja i poređenja. Ipak, on ne proverava sva poslovna pravila.

Primeri:

- `String(50)` ograničava dužinu u bazama koje sprovode ograničenje tog tipa; ne proverava da li je naziv smislen.
- `Integer` prihvata ceo broj u rasponu tipa; ne zna da li količina treba da bude pozitivna.
- `Numeric(10, 2)` određuje preciznost i skalu; ne zna da li cena sme biti negativna.
- `Boolean` predstavlja logičku vrednost; ne određuje podrazumevano stanje niti da li je `NULL` dozvoljen.

Za ostala pravila koriste se `nullable`, default vrednosti, `CHECK` ograničenja, jedinstvenost i validacija aplikacije.

## Kako se SQLAlchemy tip prevodi u bazu

Tok izgleda ovako:

```text
Python model
	-> SQLAlchemy Column i TypeEngine tip
	-> SQLAlchemy dijalekt izabranog engine-a
	-> SQL tip specifičan za bazu
```

Na primer, `Integer` će se prevesti u odgovarajući celobrojni tip konkretnog sistema. PostgreSQL i SQLite ne moraju identično da sprovode ograničenja ili skladište iste deklaracije. Ako je važno koji je tačno tip nastao, proveri generisani DDL ili samu šemu baze u modulu o kreiranju tabela.

SQLAlchemy tipovi zato predstavljaju prenosivu nameru, ali ne garantuju potpuno identično ponašanje u svakom dijalektu. PostgreSQL dokumentacija je važna jer je to baza koju kurs koristi, dok SQLAlchemy dokumentacija objašnjava Python tipove i njihovo mapiranje.

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

## Razlike između ERD-a i source koda

Kod treba porediti sa ERD-om; kod u ovoj fazi nije potpuno usklađen sa svim prikazanim detaljima:

- `Category.name` je u ERD-u prikazan sa dužinom 100, a u skripti je `String(50)`.
- `Category.slug` je u ERD-u prikazan sa dužinom 120, a u skripti je `String(55)`.
- `Category.level` je u ERD-u `Integer`, a u skripti `SmallInteger`.
- `Product.name` je u ERD-u prikazan sa dužinom 200, a u skripti je `String(50)`.
- `Product.slug` je u ERD-u prikazan sa dužinom 220, a u skripti je `String(55)`.
- ERD opisuje neka datum/vreme polja i atribute ključeva koji se namerno ne obrađuju u ovoj lekciji.

Ovo su razlike specifikacije i implementacije, a ne automatski dokaz da je jedan izbor ispravan. Pre stvarne upotrebe modela odluči koja je granica nameravana i uskladi model, ERD i pravila aplikacije.

## Važna napomena: source snapshot još nema primarne ključeve

Skripta dodaje kolone, ali `Category` i ostali modeli još nemaju primarni ključ. Proverom u SQLAlchemy 2.0.38 utvrđeno je da se fajl zaustavlja pri mapiranju `Category` sa greškom da mapper ne može da pronađe primarne ključeve.

To je posledica redosleda progresivnih primera: primarni ključevi dolaze kasnije u kursu. Definicije tipova i dalje prikazuju nameravani oblik kolona, ali ovaj fajl nije samostalno izvršiv ORM model. Ne menjamo source skriptu u okviru teorijske lekcije.

## Savremeni SQLAlchemy 2.0 oblik

Kurs koristi `Column(...)`, što je i dalje podržano u SQLAlchemy 2.0. Za tipizovane modele noviji obrazac koristi `Mapped[...]` i `mapped_column(...)`:

```python
from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column


class Product(Base):
		__tablename__ = "product"

		name: Mapped[str] = mapped_column(String(50))
		is_active: Mapped[bool] = mapped_column(Boolean)
		price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
```

Ovo je dopunski primer, ne zamena za tačan kod transkripta. Tipizacija Python atributa dopunjuje deklaraciju kolone; precizno ponašanje `NULL` vrednosti i dalje zavisi od mapiranja i `nullable` podešavanja.

## Provera razumevanja

1. Koja je razlika između `String(50)` i `Text`?
2. Zašto broj koji predstavlja cenu nije najbolje čuvati kao `Float`?
3. Šta znače precision i scale u `Numeric(10, 2)`?
4. Da li `SmallInteger` sam po sebi ograničava `level` na vrednosti od 0 do 10?
5. Koja je razlika između tipa `Boolean` i obaveznosti kolone?
6. Zašto PostgreSQL i SQLite mogu različito da se ponašaju iako model koristi isti SQLAlchemy tip?
7. Koje razlike postoje između dužina polja u ERD-u i skripti?

## Sažetak

- Izbor tipa počinje od značenja podatka i pravila u ERD-u.
- `String(n)` je za tekst sa poznatom granicom; `Text` je za duži tekst bez male deklarisane dužine.
- `SmallInteger` i `Integer` čuvaju cele brojeve, ali podržavaju različite raspone.
- `Boolean` opisuje True/False vrednost, dok su `NULL`, obaveznost i default odvojena podešavanja.
- `Numeric(10, 2)` ima ukupno 10 cifara i dve cifre iza decimalnog separatora; decimalni separator se ne broji.
- SQLAlchemy tip prevodi se kroz dijalekt u tip izabrane baze; detalji i ograničenja zavise od baze.
- Kod je progresivni snapshot bez primarnih ključeva i zato ne može da se izvrši samostalno u ovoj fazi.
