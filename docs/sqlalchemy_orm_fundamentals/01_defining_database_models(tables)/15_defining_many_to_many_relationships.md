# Lekcija 15: Many-to-many veze

## Cilj lekcije

Veza many-to-many (više-prema-više) postoji kada jedan red prve tabele može biti povezan sa više redova druge tabele, i obrnuto.

Primeri iz dizajna:

- jedna porudžbina može sadržati više proizvoda, a isti proizvod može se naći u više porudžbina;
- jedan proizvod može učestvovati u više promotivnih događaja, a jedan događaj može obuhvatiti više proizvoda.

Relacione baze ovu vezu predstavljaju **link tabelom**, koja za svaki par čuva FK ka oba povezana reda.

## Zašto je potrebna link tabela

Direktno stavljanje samo jednog FK-a u `product` ili `promotion_event` ne može da predstavi obe strane veze. Umesto toga pravi se tabela između njih:

```text
Product 1 ---- više ProductPromotionEvent više ---- 1 PromotionEvent
```

Primer jednog reda u link tabeli:

| `product_id` | `promotion_event_id` |
| -----------: | -------------------: |
|           10 |                    2 |

Ovaj red znači da proizvod sa ID-jem `10` učestvuje u promotivnom događaju `2`. Drugi red može da poveže isti proizvod sa drugim događajem, a više proizvoda može da bude povezano sa istim događajem.

## Tabela iz priloženog source koda

Source koristi `ProductPromotionEvent` kao link tabelu:

```python
class ProductPromotionEvent(Base):
	__tablename__ = "product_promotion_event"

	id = Column(Integer, primary_key=True, autoincrement=True)
	product_id = Column(
		Integer,
		ForeignKey("product.id", ondelete="RESTRICT"),
		nullable=False,
	)
	promotion_event_id = Column(
		Integer,
		ForeignKey("promotion_event.id", ondelete="RESTRICT"),
		nullable=False,
	)
```

Tabela ima sopstveni surogatni PK `id` i dva obavezna strana ključa. Svaki red mora da referencira postojeći proizvod i postojeći promotivni događaj. `ondelete="RESTRICT"` sprečava brisanje proizvoda ili događaja dok postoje link redovi koji ih referenciraju.

## Sprečavanje dupliranja istog para

Sam `id` ne sprečava da se isti proizvod i događaj povežu više puta. Dva reda bi mogla imati različite `id` vrednosti, ali iste `product_id` i `promotion_event_id` vrednosti. Source to sprečava kompozitnim ograničenjem:

```python
from sqlalchemy import UniqueConstraint

__table_args__ = (
	UniqueConstraint(
		"product_id",
		"promotion_event_id",
		name="unique_product_event",
	),
)
```

Ograničenje kaže da kombinacija `(product_id, promotion_event_id)` mora biti jedinstvena. Ono **ne** čini svaku kolonu pojedinačno jedinstvenom:

- isti proizvod može se pojaviti u više redova ako je povezan sa različitim događajima;
- isti događaj može se pojaviti u više redova ako je povezan sa različitim proizvodima;
- isti par proizvoda i događaja ne može se ponoviti.

To je primer `UniqueConstraint`-a nad više kolona, za razliku od `unique=True` koji se koristi za jednu kolonu.

Alternativno, link tabela bi mogla da koristi složeni primarni ključ od `product_id` i `promotion_event_id`, koji bi takođe sprečio dupliranje para. Ovaj kurs zadržava `id` i dodaje named `UniqueConstraint`.

## M2M `relationship()` preko `secondary`

Foreign key kolone i kompozitno ograničenje opisuju baznu tabelu. Da bi ORM omogućio Python pristup povezanim objektima bez ručnog rada sa link redovima, veza se definiše sa `relationship()` i `secondary`:

```python
class Product(Base):
	# ostale kolone su izostavljene
	promotion_event = relationship(
		"PromotionEvent",
		secondary="product_promotion_event",
		back_populates="products",
	)


class PromotionEvent(Base):
	# ostale kolone su izostavljene
	products = relationship(
		"Product",
		secondary="product_promotion_event",
		back_populates="promotion_event",
	)
```

`secondary` upućuje na link tabelu kroz koju se povezuju modeli. Source koristi ime tabele kao string; može se koristiti i objekat SQLAlchemy `Table`. `back_populates` povezuje ORM atribute na obe strane:

- `Product.promotion_event` navodi `back_populates="products"`;
- `PromotionEvent.products` navodi `back_populates="promotion_event"`.

Oba atributa predstavljaju kolekcije: proizvod može imati više događaja, a događaj više proizvoda. Source koristi ime `promotion_event` u jednini na modelu `Product`, iako je vrednost kolekcija; jasniji naziv u novom kodu mogao bi biti `promotion_events`, uz odgovarajuću izmenu `back_populates` na obe strane.

Kada se ORM kolekciji doda drugi objekat, SQLAlchemy koristi `secondary` tabelu da pri upisu napravi link red. Uklanjanje objekta iz kolekcije uklanja vezu iz link tabele; ne briše sam proizvod ili promotivni događaj. Baza i dalje sprovodi FK i unique ograničenja.

## Link tabela kao `secondary` ili kao association object

Kurs mapira `ProductPromotionEvent` kao klasu i istovremeno koristi njenu tabelu kroz `secondary="product_promotion_event"`. U link tabeli su samo ID i dve FK vrednosti, tako da je `secondary` obrazac dovoljan za jednostavno povezivanje.

Ako link red kasnije dobije sopstvene podatke kao što su količina, cena u trenutku porudžbine, datum dodavanja ili status, veza obično treba da se modeluje kao association object: aplikacija direktno koristi klasu link reda umesto da ga tretira samo kao nevidljivu `secondary` tabelu. Ne treba mešati oba načina upravljanja istim link redovima bez jasnog razloga.

## Veze koje postoje, a koje nedostaju u source-u

Priloženi `12_many_to_many.py` implementira M2M za `Product` i `PromotionEvent` preko `ProductPromotionEvent`.

Transkript takođe najavljuje M2M između `Order` i `Product`, ali u source-u `OrderProduct` sadrži samo `id` i `quantity`; nema ni `order_id` ni `product_id` FK kolone i nije naveden kao `secondary`. Zato ta druga many-to-many veza još nije implementirana u ovom snapshot-u.

Isti source pominje `Category.category_id` sa obaveznim self-FK-om, ali korenska kategorija iz prethodne lekcije nema roditelja. Ako su korenske kategorije dozvoljene, to FK polje treba da bude nullable. Ta ranija nedoslednost nije deo M2M modelovanja, ali utiče na validnost ukupnog source fajla.

## Greška u source-u koja sprečava uvoz

U priloženom source-u za `Category` stoji `ForeignKey("category.id", nullable=False, ondelete="RESTRICT")`. `nullable` pripada `Column(...)`, ne konstruktoru `ForeignKey(...)`. Uvoz source fajla u SQLAlchemy 2.0 zato pada sa `TypeError` pre nego što se M2M mapiranje konfiguriše.

Ispravan položaj argumenata u samoj link tabeli je prikazan u primerima iznad: `ondelete` ostaje na `ForeignKey(...)`, dok je `nullable=False` prosleđen `Column(...)`. Source fajl nisam menjao.

## Napomena za SQLAlchemy 2.0 stil

Kursni source koristi `Column` i string argumente za `relationship`. SQLAlchemy 2.0 može iste koncepte da izrazi tipizovano pomoću `Mapped[...]` i `mapped_column(...)`; M2M veza i dalje koristi isti princip link tabele i `secondary`. Promena maperske sintakse ne menja relacioni model baze.

## Pitanja za proveru razumevanja

1. Zašto je između dve tabele u M2M vezi potrebna link tabela?
2. Šta znače `product_id` i `promotion_event_id` u jednom redu link tabele?
3. Zašto primarni ključ `id` sam po sebi ne sprečava dupliranje istog para?
4. Šta tačno ograničava `UniqueConstraint("product_id", "promotion_event_id")`?
5. Koju ulogu ima `secondary` u `relationship()`?
6. Šta se briše kada se objekat ukloni iz ORM M2M kolekcije: link red ili povezani entitet?
7. Zašto `OrderProduct` još ne implementira najavljenu vezu porudžbina–proizvod?
8. Zašto source kod ne može da se uveze pre nego što se dođe do many-to-many mapiranja?

## Sažetak

- M2M veza se predstavlja link tabelom sa FK kolonama ka oba entiteta.
- `ProductPromotionEvent` povezuje proizvode sa promotivnim događajima.
- `UniqueConstraint` nad `(product_id, promotion_event_id)` sprečava ponovljen par, ali dopušta da svaki proizvod i događaj imaju više različitih veza.
- `relationship(..., secondary=...)` omogućava ORM pristup kolekcijama sa obe strane bez ručnog rada sa link redovima.
- `secondary` je pogodan za link tabelu bez dodatnog poslovnog ponašanja; dodatni atributi link reda obično traže association object obrazac.
- Transkript pominje i `Order`–`Product`, ali source još nema FK kolone u `OrderProduct`.
- Source u ovom stanju ne može da se uveze zbog pogrešnog argumenta `nullable` u `Category` FK deklaraciji.
