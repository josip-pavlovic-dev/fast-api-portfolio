# Lekcija 12: Strani ključevi

## Cilj lekcije

Strani ključ (foreign key, FK) povezuje kolonu u jednoj tabeli sa ključem u drugoj tabeli i omogućava bazi da proverava referencijalni integritet. SQLAlchemy ORM može dodatno da opiše istu vezu pomoću `relationship()`, što olakšava pristup povezanim objektima iz Python-a.

Ključna razlika:

- `ForeignKey(...)` definiše kolonu i ograničenje na nivou baze;
- `relationship(...)` definiše ORM atribut za rad sa povezanim objektima; sam po sebi ne dodaje FK kolonu u tabelu.

Ove dve deklaracije se često koriste zajedno, ali rešavaju različite zadatke.

Kurski source primeri ispod koriste engleska imena i stariji `Column(...)` stil. Naš praktični projekat koristi srpske nazive tabela i SQLAlchemy 2.x `Mapped[...]` / `mapped_column()` stil. Sledeća tabela je stvarno stanje projektnih modela nakon ove lekcije:

| FK kolona                                           | Referencirana kolona     | Obavezna? | ORM navigacija                                                                      |
| --------------------------------------------------- | ------------------------ | --------- | ----------------------------------------------------------------------------------- |
| `proizvod.kategorija_id`                            | `kategorija.id`          | da        | `Proizvod.kategorija` / `Kategorija.proizvodi`                                      |
| `porudzbina.korisnik_id`                            | `korisnik.id`            | da        | `Porudzbina.korisnik` / `Korisnik.porudzbine`                                       |
| `stavka_porudzbine.porudzbina_id`                   | `porudzbina.id`          | da        | `StavkaPorudzbine.porudzbina` / `Porudzbina.stavke`                                 |
| `stavka_porudzbine.proizvod_id`                     | `proizvod.id`            | da        | `StavkaPorudzbine.proizvod` / `Proizvod.stavke_porudzbine`                          |
| `veza_proizvoda_i_promocije.proizvod_id`            | `proizvod.id`            | da        | `VezaProizvodaIPromocije.proizvod` / `Proizvod.veze_promocija`                      |
| `veza_proizvoda_i_promocije.promotivni_dogadjaj_id` | `promotivni_dogadjaj.id` | da        | `VezaProizvodaIPromocije.promotivni_dogadjaj` / `PromotivniDogadjaj.veze_proizvoda` |

Svih šest FK kolona u ovoj implementaciji ima `nullable=False`. FK osigurava da nenull vrednost pokazuje na postojeći red; `nullable=False` dodatno zahteva da vrednost uopšte bude navedena. PK `id` kolone postojale su već ranije i nisu ponovo dodavane.

ORM navigacioni atributi ne postaju kolone: na primer `Proizvod.kategorija` je Python atribut za objekat kategorije, a stvarni FK podatak koji se čuva jeste `Proizvod.kategorija_id`. Detalji implementacije i kod nalaze se u `models/catalog.py`, `models/orders.py` i `models/promotions.py`; sve promene iz ove lekcije označene su komentarima `Lekcija 12`.

## Veza jedan-prema-više

U primeru `Category`–`Product` jedna kategorija može imati više proizvoda, a svaki proizvod pripada jednoj kategoriji. Zato se strani ključ postavlja na „više“ stranu, u tabelu `product`:

```text
Category (jedna)  1 ---- više  Product
						 product.category_id -> category.id
```

Na primer, kategorija „TV“ može biti povezana sa više proizvoda. Svaki od tih proizvoda čuva ID kategorije kojoj pripada.

Transkript na jednom mestu nespretno opisuje da je „one product“ povezan sa više proizvoda. Kardinalnost koju objašnjava ostatak primera i koju source kod implementira jeste: **jedna kategorija ima više proizvoda; jedan proizvod referencira jednu kategoriju**.

U našem projektu isto pravilo koristi `kategorija` i `proizvod`. Kolona `kategorija_id` nalazi se na strani `Proizvod`, jer je to strana „više“: više proizvoda može da referencira istu kategoriju.

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

U projektu se string prilagođava stvarnom imenu tabele, ne imenu Python klase:

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

kategorija_id: Mapped[int] = mapped_column(
	ForeignKey("kategorija.id"),
	nullable=False,
)
```

Ovde `kategorija` mora tačno da se poklopi sa `Kategorija.__tablename__`, a `id` sa imenom PK kolone. `Mapped[int]` opisuje Python vrednost; `ForeignKey(...)` postavlja referencijalno pravilo u metapodacima šeme. SQLAlchemy može da kompajlira to pravilo u DDL, ali ako baza već postoji, potrebna je migracija da bi se ograničenje dodalo u nju.

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

U SQLAlchemy 2.x projektu veze se tipizuju pomoću `Mapped[...]`, na primer:

```python
class Kategorija(Base):
	# Kolone su izostavljene.
	proizvodi: Mapped[list["Proizvod"]] = relationship(back_populates="kategorija")


class Proizvod(Base):
	kategorija_id: Mapped[int] = mapped_column(
		ForeignKey("kategorija.id"),
		nullable=False,
	)
	kategorija: Mapped["Kategorija"] = relationship(back_populates="proizvodi")
```

Ovo je skraćeni prikaz stvarnih imena iz našeg projekta; kolone koje nisu važne za vezu izostavljene su.

Na primer, preko ORM-a može se raditi sa `proizvod.kategorija` da bi se pristupilo kategoriji proizvoda ili sa `kategorija.proizvodi` da bi se pristupilo kolekciji proizvoda. SQLAlchemy koristi FK mapiranje i relationship konfiguraciju da izvede potrebna učitavanja i sinhronizuje vezu između objekata.

### Uparivanje sa `back_populates`

Vrednosti `back_populates` moraju da navedu ime odgovarajućeg atributa na drugom modelu:

- `Kategorija.proizvodi` navodi `back_populates="kategorija"`;
- `Proizvod.kategorija` navodi `back_populates="proizvodi"`.

Ovim se dobija dvosmerno povezivanje. Ako se veza menja sa jedne strane u ORM-u, druga strana može da odražava isto povezivanje. `back_populates` ne pravi FK ograničenje; to radi `ForeignKey`.

U source kodu je `Category.product` nazvan u jednini, ali predstavlja kolekciju proizvoda zato što je to „više“ strana veze. U našem projektu koristimo jasnije ime `Kategorija.proizvodi`; ime atributa na obe strane mora ostati dosledno navedeno u `back_populates`.

## Još jedan primer: `User` i `Order`

Jedan korisnik može imati više porudžbina, dok svaka porudžbina pripada jednom korisniku. FK je zato u tabeli `porudzbina`, na strani „više“:

```python
class Korisnik(Base):
	porudzbine: Mapped[list["Porudzbina"]] = relationship(back_populates="korisnik")


class Porudzbina(Base):
	korisnik_id: Mapped[int] = mapped_column(ForeignKey("korisnik.id"), nullable=False)
	korisnik: Mapped["Korisnik"] = relationship(back_populates="porudzbine")
```

`Porudzbina.korisnik_id` je stvarna FK kolona. `Porudzbina.korisnik` je ORM atribut koji vodi do jednog objekta `Korisnik`, a `Korisnik.porudzbine` do kolekcije porudžbina. Pošto je `korisnik_id` `nullable=False`, svaka porudžbina mora pripadati korisniku.

Kurski source koristi tabelu `order`; naš projekat je naziva `porudzbina`, pa izbegavamo potencijalni sukob sa SQL ključnom reči `ORDER`. FK string u našem kodu zato je `ForeignKey("korisnik.id")`, a ne ime Python klase niti source tabela `user`.

## Foreign key nije isto što i relationship

| Deklaracija                   | Gde deluje  | Šta obezbeđuje                                          |
| ----------------------------- | ----------- | ------------------------------------------------------- |
| `ForeignKey("kategorija.id")` | šema i baza | FK kolonu/ograničenje i proveru referencirane vrednosti |
| `relationship(...)`           | ORM model   | Python pristup povezanim objektima i mapiranje veze     |

FK može postojati i bez `relationship()`. Tada baza i dalje čuva referencijalni integritet, ali ORM nema taj praktičan atribut za navigaciju; upite je i dalje moguće napisati eksplicitno. `relationship()` bez odgovarajuće FK informacije ili druge konfiguracije ne zamenjuje ograničenje baze.

## Vezne tabele u projektu

Tabela `StavkaPorudzbine` je asocijativni (vezni) model između porudžbine i proizvoda. Nosi i poslovni podatak `kolicina`, pa nije samo tehnička tabela za vezu. Jedna porudžbina ima više stavki, a jedan proizvod može se pojaviti u stavkama više porudžbina:

```python
class StavkaPorudzbine(Base):
	porudzbina_id: Mapped[int] = mapped_column(
		ForeignKey("porudzbina.id"), nullable=False
	)
	proizvod_id: Mapped[int] = mapped_column(ForeignKey("proizvod.id"), nullable=False)
	kolicina: Mapped[int] = mapped_column(Integer, nullable=False)
	porudzbina: Mapped["Porudzbina"] = relationship(back_populates="stavke")
	proizvod: Mapped["Proizvod"] = relationship(back_populates="stavke_porudzbine")
```

Odgovarajuće kolekcije nalaze se na `Porudzbina.stavke` i `Proizvod.stavke_porudzbine`. To modeluje vezu porudžbina–proizvod preko stavki i omogućava da stavka sadrži količinu. Ne dodajemo zaseban direktni `relationship()` many-to-many između `Porudzbina` i `Proizvod`, jer je `StavkaPorudzbine` eksplicitno mapirana klasa sa sopstvenim podacima.

`VezaProizvodaIPromocije` je druga vezna tabela i povezuje proizvode sa promotivnim događajima. Sada sadrži `proizvod_id` i `promotivni_dogadjaj_id`, oba kao obavezne FK kolone. ORM veze su `Proizvod.veze_promocija`, `PromotivniDogadjaj.veze_proizvoda` i njihove pojedinačne veze na asocijativnom modelu. Pošto isti proizvod sme biti u više promocija, a ista promocija sme obuhvatiti više proizvoda, par FK vrednosti dobija složeni `UniqueConstraint`; time se sprečava samo ponavljanje iste veze.

Ovo je asocijativni-object obrazac: aplikacija može doći od proizvoda ili promocije do kolekcije objekata veze, pa zatim do druge strane. Ne mapiramo istu tabelu istovremeno kao asocijativni ORM objekat i kao nezavisnu writable `secondary` vezu, čime izbegavamo dva ORM puta za izmenu istih FK kolona.

Kurski source snapshot-i nisu svi jednako potpuni: `9_foreign_key.py` prikazuje FK za kategoriju i korisnika, a kasniji source i transkript proširuju vezne tabele. Naš projekat je sada usklađen sa celinom obrađenom u lekciji 12; originalne snapshot-e ne menjamo.

## Ograničenja i ponašanje baze

- FK ograničenje proverava postojanje ciljnog reda, ali `nullable=False` posebno određuje da li veza sme da izostane.
- U projektnim modelima nije navedeno `ondelete="CASCADE"` niti ORM `delete-orphan` kaskada. Ne treba pretpostaviti da brisanje kategorije automatski briše proizvode ili da ORM sam briše zavisne redove; brisanje obrađujemo tek kada obradimo tu temu.
- SQLite po podrazumevanim podešavanjima ne sprovodi uvek FK ograničenja. U aplikaciji koja koristi SQLite, FK enforcement treba eksplicitno uključiti na konekciji. PostgreSQL ih sprovodi kada su ograničenja kreirana.
- Svi projektni FK-ovi referenciraju `id` primarni ključ, pa više redova može bezbedno referencirati isti roditeljski zapis.
- Samo deklarisanje `ForeignKey` u Python-u ne menja već kreiranu bazu. Potrebna je migracija ili ponovno kreiranje šeme u razvojnoj bazi; `create_all()` pravi nedostajuće tabele, ali ne migrira postojeće.

## Zapažanje o vremenskim oznakama

Kurski source snapshot ima problem: `Product.updated_at` i `Order.updated_at` su `nullable=False` i imaju samo `onupdate=func.now()`, bez početnog default-a. U našem praktičnom projektu `izmenjeno_u` već ima početni `default=func.now()` uz `onupdate=func.now()`, pa obavezno polje dobija vreme i pri INSERT-u. Ova praktična korekcija nije deo FK promene.

## Pitanja za proveru razumevanja

1. Zašto se strani ključ u vezi jedan-prema-više postavlja na „više“ stranu?
2. Šta je stvarna FK kolona u našem modelu `Proizvod`?
3. Kako se razlikuju `ForeignKey` i `relationship()`?
4. Kako `back_populates` povezuje `Kategorija.proizvodi` i `Proizvod.kategorija`?
5. Da li `ForeignKey` sam po sebi znači da kolona mora biti `NOT NULL`?
6. Koje dve FK kolone povezuju `StavkaPorudzbine` sa porudžbinom i proizvodom?
7. Zašto treba proveriti podešavanja FK enforcement-a pri korišćenju SQLite-a?
8. Zašto veza proizvoda i promocije ima složeni `UniqueConstraint` nad FK parom?
9. Zašto samo `Kategorija`→`Proizvod` FK ne opisuje buduću vezu kategorije sa roditeljskom kategorijom?

## Sažetak

- `ForeignKey("tabela.kolona")` definiše vezu na nivou šeme baze i proverava da referencirana vrednost postoji.
- U vezi jedan-prema-više FK se obično nalazi na strani „više“: `Proizvod.kategorija_id`, `Porudzbina.korisnik_id` i FK-ovi stavke.
- `nullable=False` uz FK čini vezu obaveznom; to je odvojeno od referencijalnog integriteta.
- `relationship()` daje ORM pristup povezanim objektima, ali ne pravi baznu FK kolonu.
- `back_populates` uparuje odgovarajuće atribute na obe strane ORM veze.
- `StavkaPorudzbine` i `VezaProizvodaIPromocije` su eksplicitni asocijativni modeli; drugi ima složeno unique pravilo protiv duplog para.
- Svih šest FK kolona i odgovarajuća ORM navigacija sada su implementirani u srpski imenovanom projektu; samoreferencirajući FK kategorije ostaje za lekciju 13.
- Za SQLite treba uključiti FK enforcement; za postojeću bazu šema se menja migracijom, ne samo izmenom modela.
