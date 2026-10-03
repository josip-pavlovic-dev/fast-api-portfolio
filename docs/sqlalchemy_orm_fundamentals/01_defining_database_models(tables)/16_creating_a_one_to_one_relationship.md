# Lekcija 16: Veza jedan-prema-jedan

## Cilj lekcije

Veza jedan-prema-jedan povezuje najviše jedan red sa najviše jednim redom druge tabele. Primer iz lekcije je `Product`–`StockManagement`: proizvod može imati jedan zapis o stanju, a svaki zapis o stanju odnosi se na jedan proizvod.

Foreign key se stavlja u zavisnu tabelu `stock_management`, jer zapis o stanju nema smisla bez proizvoda o kome čuva podatke. Da bi se sprečilo da više stock redova referencira isti proizvod, FK kolona mora biti jedinstvena.

## Izbor strane koja sadrži FK

Pre postavljanja FK-a treba razmotriti zavisnost:

- `Product` može postojati i bez zapisa u `StockManagement`;
- `StockManagement` zapis ne bi trebalo da postoji bez odgovarajućeg proizvoda.

Zato source postavlja `product_id` u tabelu `stock_management`. Takva odluka znači da je učešće asimetrično: svaki stock zapis mora da ima proizvod, ali ne mora svaki proizvod već da ima stock zapis.

Preciznije, ograničenja u source modelu predstavljaju vezu **nula-ili-jedan stock zapis po proizvodu**, a **tačno jedan proizvod po stock zapisu**:

```text
Product 1 -------- 0..1 StockManagement
```

Relacione baze ne zahtevaju da za svaki `Product` postoji odgovarajući red u child tabeli samo zato što child tabela ima FK.

## Ograničenja baze: FK, `NOT NULL` i `UNIQUE`

U kursnom `Column` stilu, ideja source koda je:

```python
product_id = Column(
	Integer,
	ForeignKey("product.id", ondelete="RESTRICT"),
	nullable=False,
	unique=True,
)
```

Svaki deo ima zasebnu ulogu:

- `ForeignKey("product.id")` zahteva da referencirani proizvod postoji;
- `nullable=False` zahteva da svaki stock red navede proizvod;
- `unique=True` sprečava da se isti `product_id` pojavi u dva stock reda.

FK bez `unique=True` opisivao bi jedan-prema-više: jedan proizvod mogao bi da ima više stock redova. Kombinacija FK-a i jedinstvenosti ograničava ponavljanje proizvoda i daje bazni deo one-to-one pravila.

Jedinstvenost se može definisati i named `UniqueConstraint("product_id")`; source koristi `unique=True` direktno na koloni. Oba oblika treba da sprovedu isto jedno-kolonsko jedinstveno pravilo ako se pravilno kreiraju u šemi baze.

## ORM veza u priloženom source-u

Source povezuje modele dvosmerno:

```python
class Product(Base):
	stock = relationship(
		"StockManagement",
		uselist=False,
		back_populates="product",
		single_parent=True,
	)


class StockManagement(Base):
	product_id = Column(
		Integer,
		ForeignKey("product.id", ondelete="RESTRICT"),
		nullable=False,
		unique=True,
	)
	product = relationship("Product", back_populates="stock")
```

`back_populates` uparuje `Product.stock` sa `StockManagement.product`:

- `product.stock` je jedan objekat `StockManagement` ili `None` ako zapis još ne postoji;
- `stock.product` je jedan objekat `Product`.

Na `Product.stock` source postavlja `uselist=False`. ORM veze po pravilu predstavljaju kolekciju kada je odnos one-to-many; ova opcija kaže da se ovde očekuje skalarni atribut. Ona utiče na Python/ORM prikaz veze, ali **ne** stvara bazno `UNIQUE` ograničenje. Bazno pravilo obezbeđuje `unique=True` na `product_id`.

## Šta radi `single_parent=True`

`single_parent=True` dodaje ORM proveru da se ista instanca zavisnog `StockManagement` objekta ne dodeli kao dete više različitih `Product` objekata istovremeno. Može pomoći da se u memoriji očuva model jednog roditelja.

Ovo nije zamena za bazno unique ograničenje: ne štiti od drugog procesa, druge sesije ili direktnog SQL upisa. `unique=True` u bazi ostaje konačna zaštita da dva stock reda ne referenciraju isti proizvod.

`single_parent=True` takođe ne znači da proizvod mora imati stock zapis. Ne nameće postojanje child reda u bazi.

## Poređenje sa one-to-many vezom

Kod prethodne veze `Category`–`Product`, više proizvoda može imati isti `category_id`. Zato FK u tabeli `product` nije unique.

Kod `Product`–`StockManagement`, svaki stock `product_id` mora biti unique. Ta razlika na nivou baze je ono što menja FK odnos iz one-to-many u najviše one-to-one.

| Pravilo nad FK kolonom | Moguća kardinalnost iz roditeljskog ugla          |
| ---------------------- | ------------------------------------------------- |
| FK, bez `UNIQUE`       | jedan roditelj može imati više child redova       |
| FK sa `UNIQUE`         | jedan roditelj može imati najviše jedan child red |

`nullable=False` na child FK-u kaže da svaki child mora imati roditelja, ne da svaki roditelj mora imati child.

## Brisanje proizvoda

Source dodaje `ondelete="RESTRICT"` na `stock_management.product_id`. Ako stock zapis postoji, baza treba da odbije brisanje referenciranog proizvoda. Stock zapis se prvo mora ukloniti ili mora postojati drugo namerno pravilo.

`RESTRICT` u izvoru je podešavanje baze i razlikuje se od ORM `cascade` opcija. Stvarno ponašanje zavisi od FK ograničenja kreiranog u bazi i od toga da li DBMS sprovodi FK pravila.

## Greška u ukupnom source snapshot-u

Deklaracija `StockManagement.product_id` u priloženom fajlu ima ispravan raspored za `ondelete`, `nullable` i `unique`. Ipak, ceo source fajl ne može da se uveze zbog ranijeg FK-a u modelu `Category`:

```python
ForeignKey("category.id", nullable=False, ondelete="RESTRICT")
```

`nullable` ne pripada `ForeignKey(...)`, već `Column(...)`. SQLAlchemy 2.0 baca `TypeError` dok definiše `Category`, pre nego što dođe do `StockManagement` veze. I `Product.category_id` u istom fajlu prosleđuje `ondelete` na pogrešnom nivou (`Column` umesto `ForeignKey`). To su nasleđene greške iz prethodnih lekcija, a ne greške u one-to-one deklaraciji `product_id`. Source fajl nisam menjao.

## Napomena za SQLAlchemy 2.0 stil

Kurs koristi `uselist=False` da ORM atribut bude skalar. Kada u praktičnom radu pređemo na `Mapped[...]` anotacije, SQLAlchemy može da zaključi da je atribut skalarni iz njegovog tipa, ali jedinstvenost FK-a u bazi i dalje treba eksplicitno definisati.

## Pitanja za proveru razumevanja

1. Zašto se FK nalazi u `StockManagement`, a ne u `Product`?
2. Zašto `product_id` mora biti jedinstven za baznu one-to-one kardinalnost?
3. Šta `nullable=False` zahteva, a šta ne zahteva?
4. Da li `uselist=False` pravi unique ograničenje u bazi?
5. Šta `single_parent=True` proverava i zašto nije zamena za `unique=True`?
6. Može li `Product` postojati bez `StockManagement` reda u ovom modelu?
7. Zašto se priloženi source fajl zaustavlja pre mapiranja ove veze?

## Sažetak

- FK je na zavisnoj strani, `StockManagement.product_id`, jer stock zapis zavisi od proizvoda.
- `ForeignKey` potvrđuje postojanje proizvoda; `nullable=False` zahteva proizvod za svaki stock red; `unique=True` ograničava proizvod na najviše jedan stock red.
- Ova postavka dozvoljava proizvod bez stock reda, ali ne i stock red bez proizvoda.
- `uselist=False` čini `Product.stock` skalarnim ORM atributom; ne kreira bazno unique ograničenje.
- `single_parent=True` proverava dodeljivanje iste ORM instance jednom roditelju, ali ne zamenjuje ograničenje baze.
- Source deklaracija one-to-one FK-a je dobro formirana, ali uvoz kompletnog fajla pada ranije zbog pogrešnih FK argumenata u `Category`.
