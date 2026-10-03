# Lekcija 12: Strani ključevi

## Cilj lekcije

Strani ključ (foreign key, FK) povezuje kolonu u jednoj tabeli sa ključem u drugoj tabeli i omogućava bazi da proverava referencijalni integritet. SQLAlchemy ORM može dodatno da opiše istu vezu pomoću `relationship()`, što olakšava pristup povezanim objektima iz Python-a.

Ključna razlika:

- `ForeignKey(...)` definiše kolonu i ograničenje na nivou baze;
- `relationship(...)` definiše ORM atribut za rad sa povezanim objektima; sam po sebi ne dodaje FK kolonu u tabelu.

Ove dve deklaracije se često koriste zajedno, ali rešavaju različite zadatke.

## Veza jedan-prema-više

U primeru `Category`–`Product` jedna kategorija može imati više proizvoda, a svaki proizvod pripada jednoj kategoriji. Zato se strani ključ postavlja na „više“ stranu, u tabelu `product`:

```text
Category (jedna)  1 ---- više  Product
						 product.category_id -> category.id
```

Na primer, kategorija „TV“ može biti povezana sa više proizvoda. Svaki od tih proizvoda čuva ID kategorije kojoj pripada.

Transkript na jednom mestu nespretno opisuje da je „one product“ povezan sa više proizvoda. Kardinalnost koju objašnjava ostatak primera i koju source kod implementira jeste: **jedna kategorija ima više proizvoda; jedan proizvod referencira jednu kategoriju**.

## `ForeignKey`: ograničenje u šemi baze

U source kodu kolona proizvoda je definisana ovako:

```python
from sqlalchemy import Column, ForeignKey, Integer

category_id = Column(
	Integer,
	ForeignKey("category.id"),
	nullable=False,
)
```

`ForeignKey("category.id")` kaže da se vrednost `product.category_id` odnosi na kolonu `id` tabele `category`. String koristi oblik `ime_tabele.ime_kolone`, ne ime Python klase.

Pri pokušaju upisa, baza proverava da li referencirana kategorija postoji. Tako `category_id=42` ne može da se sačuva ako kategorija `id=42` ne postoji, pod uslovom da baza sprovodi FK ograničenja.

`nullable=False` je odvojeno pravilo: ono zahteva da svaki proizvod ima vrednost `category_id`. Strani ključ sam po sebi ne znači da je kolona obavezna. Ako bi FK kolona bila nullable, `NULL` bi mogao da označi da veza nije navedena; svaka konkretna, nenull vrednost i dalje bi morala da referencira postojeći red.

U source kodu `category.id` je primarni ključ, pa je odgovarajuća ciljna kolona jednoznačna. Strani ključ se uobičajeno referencira na primarni ključ ili drugu jedinstvenu kolonu.

## `relationship()`: ORM pristup povezanim objektima

Pored FK kolone, source kod definiše atribute na obe strane:

```python
from sqlalchemy.orm import relationship


class Category(Base):
	# ostale kolone su izostavljene
	product = relationship("Product", back_populates="category")


class Product(Base):
	# category_id je deklarisan kao ForeignKey("category.id")
	category = relationship("Category", back_populates="product")
```

`relationship()` ne predstavlja dodatnu kolonu. Ona govori ORM-u kako da poveže Python objekte i omogući pristup podacima preko atributa. FK kolona i njeno ograničenje i dalje su ono što baza koristi za čuvanje i proveru veze.

Na primer, preko ORM-a može se raditi sa `product.category` da bi se pristupilo kategoriji proizvoda ili sa `category.product` da bi se pristupilo povezanim proizvodima. SQLAlchemy koristi FK mapiranje i relationship konfiguraciju da izvede potrebna učitavanja i sinhronizuje vezu između objekata.

### Uparivanje sa `back_populates`

Vrednosti `back_populates` moraju da navedu ime odgovarajućeg atributa na drugom modelu:

- `Category.product` navodi `back_populates="category"`;
- `Product.category` navodi `back_populates="product"`.

Ovim se dobija dvosmerno povezivanje. Ako se veza menja sa jedne strane u ORM-u, druga strana može da odražava isto povezivanje. `back_populates` ne pravi FK ograničenje; to radi `ForeignKey`.

U source kodu je `Category.product` nazvan u jednini, ali predstavlja kolekciju proizvoda zato što je to „više“ strana veze. Jasniji naziv u novom kodu obično bi bio `products`; ako se ime promeni, odgovarajući `back_populates` mora da se promeni zajedno sa njim. Ovde je zadržan naziv source primera.

## Još jedan primer: `User` i `Order`

Jedan korisnik može imati više porudžbina, dok svaka porudžbina pripada jednom korisniku. FK je zato u `order` tabeli:

```python
class User(Base):
	orders = relationship("Order", back_populates="user")


class Order(Base):
	user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
	user = relationship("User", back_populates="orders")
```

`Order.user_id` je stvarna FK kolona. `Order.user` je ORM atribut koji vodi do jednog `User` objekta, a `User.orders` vodi do kolekcije porudžbina. Pošto je `user_id` nullable=False, source kod zahteva da svaka porudžbina bude povezana sa korisnikom.

Naziv tabele `order` je sačuvan iz kursnog source koda. `ORDER` je SQL ključna reč u mnogim dijalektima; SQLAlchemy dijalekt obično zna kada treba da citira takav naziv, ali je za aplikacije često jasnije izabrati nekonfliktno ime tabele.

## Foreign key nije isto što i relationship

| Deklaracija                     | Gde deluje  | Šta obezbeđuje                                          |
| ------------------------------- | ----------- | ------------------------------------------------------- |
| `ForeignKey("category.id")`     | šema i baza | FK kolonu/ograničenje i proveru referencirane vrednosti |
| `relationship("Category", ...)` | ORM model   | Python pristup povezanim objektima i mapiranje veze     |

FK može postojati i bez `relationship()`. Tada baza i dalje čuva referencijalni integritet, ali ORM nema taj praktičan atribut za navigaciju; upite je i dalje moguće napisati eksplicitno. `relationship()` bez odgovarajuće FK informacije ili druge konfiguracije ne zamenjuje ograničenje baze.

## Veze u ostatku source koda

Pored `Product.category_id` i `Order.user_id`, source kod definiše još dve FK kolone u `OrderProduct`:

```python
order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
```

Ove kolone postavljaju osnovu za veznu tabelu između porudžbina i proizvoda. U ovom snapshot-u `OrderProduct` još nema `relationship()` atribute, a ni `Order` i `Product` nemaju ORM veze ka toj tabeli. Potpuno mapiranje many-to-many veze i ponašanje vezne tabele pripada narednoj temi.

Slično tome, `ProductPromotionEvent` trenutno sadrži samo `id`; iako transkript pominje vezu proizvoda sa promotivnim događajem preko vezne tabele, ta dva FK polja još nisu u priloženoj skripti.

## Ograničenja i ponašanje baze

- FK ograničenje proverava postojanje ciljnog reda, ali `nullable=False` posebno određuje da li veza sme da izostane.
- U source kodu nije navedeno `ondelete="CASCADE"`. Ne treba pretpostaviti da brisanje kategorije automatski briše proizvode; ponašanje pri brisanju zavisi od baze i FK opcija.
- SQLite po podrazumevanim podešavanjima ne sprovodi uvek FK ograničenja. U aplikaciji koja koristi SQLite, FK enforcement treba eksplicitno uključiti na konekciji. PostgreSQL ih sprovodi kada su ograničenja kreirana.
- FK u source modelima referencira `id` primarni ključ, pa više redova može bezbedno referencirati isti roditeljski zapis.

## Zapažanje o vremenskim oznakama

Kao i u prethodnim source snapshot-ovima, `Product.updated_at` i `Order.updated_at` su `nullable=False` i imaju samo `onupdate=func.now()`, bez početnog default-a. `onupdate` ne obezbeđuje vreme pri `INSERT`-u. Zato novi proizvod ili porudžbina moraju da dobiju `updated_at` eksplicitno ili će upis pasti zbog `NOT NULL` ograničenja. Ovo nije izazvano stranim ključem, ali utiče na izvršivost modela.

## Pitanja za proveru razumevanja

1. Zašto se strani ključ u vezi jedan-prema-više postavlja na „više“ stranu?
2. Šta je stvarna FK kolona u modelu `Product`?
3. Kako se razlikuju `ForeignKey` i `relationship()`?
4. Šta znače `back_populates="category"` i `back_populates="product"` u paru `Category`–`Product`?
5. Da li `ForeignKey` sam po sebi znači da kolona mora biti `NOT NULL`?
6. Koje FK kolone postoje u `OrderProduct`, a koje ORM relacije još nedostaju?
7. Zašto treba proveriti podešavanja FK enforcement-a pri korišćenju SQLite-a?

## Sažetak

- `ForeignKey("tabela.kolona")` definiše vezu na nivou šeme baze i proverava da referencirana vrednost postoji.
- U vezi jedan-prema-više FK se obično nalazi na strani „više“: `Product.category_id` i `Order.user_id`.
- `nullable=False` uz FK čini vezu obaveznom; to je odvojeno od referencijalnog integriteta.
- `relationship()` daje ORM pristup povezanim objektima, ali ne pravi baznu FK kolonu.
- `back_populates` uparuje odgovarajuće atribute na obe strane ORM veze.
- `OrderProduct` ima FK kolone ka `Order` i `Product`, ali potpuno many-to-many mapiranje još nije urađeno.
- Transkript pominje relacije koje nedostaju iz source snapshot-a; SQLite FK ograničenja i `updated_at` takođe zahtevaju posebnu pažnju.
