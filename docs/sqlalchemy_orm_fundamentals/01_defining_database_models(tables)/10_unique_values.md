# Lekcija 10: Jedinstvene vrednosti

## Cilj lekcije

U ovoj lekciji dodajemo `unique=True` na kolone za koje poslovno pravilo zahteva da se ista vrednost ne pojavi u više redova iste tabele.

Primeri iz source koda su nazivi i slug-ovi kategorija i proizvoda, nazivi promotivnih događaja, korisnička imena i email adrese. Jedinstvenost zavisi od namene podatka: nije svaka kolona kandidat za ovo ograničenje.

## Šta znači jedinstvena vrednost

Ako je vrednost kolone jedinstvena, dva reda u istoj tabeli ne mogu imati istu vrednost u toj koloni. Na primer, kada kategorija sa `name="TV"` već postoji, baza odbija drugi red koji pokušava da sačuva isti naziv kategorije.

U klasičnom SQLAlchemy stilu iz kursa pravilo se navodi ovako:

```python
name = Column(String(50), nullable=False, unique=True)
```

U našem SQLAlchemy 2.x stilu isti atribut se zapisuje pomoću `Mapped[...]` i `mapped_column()`:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

naziv: Mapped[str] = mapped_column(
	String(50),
	nullable=False,
	unique=True,
)
```

`unique=True` traži od SQLAlchemy-ja da za kolonu napravi ograničenje jedinstvenosti u šemi baze. Baza proverava pravilo pri upisu ili izmeni reda. Aplikacija može ranije proveriti da li vrednost već postoji radi korisnije poruke, ali provera u aplikaciji ne zamenjuje ograničenje baze.

### Ograničenje nad više kolona u SQLAlchemy 2.x

Za kombinaciju kolona koristi se `UniqueConstraint` u `__table_args__`. U tipizovanom declarative modelu to izgleda ovako:

```python
from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class Membership(Base):
	__tablename__ = "membership"
	__table_args__ = (
		UniqueConstraint(
			"organization_id",
			"user_id",
			name="uq_membership_organization_user",
		),
	)

	organization_id: Mapped[int] = mapped_column(Integer, nullable=False)
	user_id: Mapped[int] = mapped_column(Integer, nullable=False)
```

Ime ograničenja je opciono, ali eksplicitna i dosledna imena olakšavaju čitanje migracija i kasniju izmenu ili uklanjanje ograničenja. Veće aplikacije često postave `MetaData.naming_convention`; naš projekat to još nije uveo, pa za sada ne dodajemo globalnu konvenciju.

## Zašto ograničenje treba da proverava baza

Sama provera pre upisa nije dovoljna za očuvanje integriteta. Dva zahteva mogu skoro istovremeno proveriti da vrednost ne postoji; oba zatim pokušaju da je upišu. Bez ograničenja u bazi oba upisa mogu uspeti.

Sa `unique=True`, baza je konačni autoritet: samo jedan od konfliktnih upisa može uspeti. Drugi će dobiti grešku integriteta. Aplikacija treba da uhvati odgovarajući `IntegrityError`, po potrebi uradi `rollback()` transakcije i korisniku vrati razumljivu poruku. Tačan način obrade pripada sloju upisa/API-ja, ne deklaraciji kolone.

## Polja iz priloženog modela

Source kod ove lekcije dodaje jedinstvenost na sledeće pojedinačne kolone:

| Model            | Kolona     | Razlog iz primera                                  |
| ---------------- | ---------- | -------------------------------------------------- |
| `Category`       | `name`     | naziv identifikuje kategoriju u domenu             |
| `Category`       | `slug`     | URL adresa treba da vodi do jedne kategorije       |
| `PromotionEvent` | `name`     | nazivi promotivnih događaja ne smeju se ponavljati |
| `Product`        | `name`     | svaki naziv proizvoda je jedinstven u ovom modelu  |
| `Product`        | `slug`     | URL slug identifikuje jedan proizvod               |
| `User`           | `username` | korisničko ime je jedinstveno                      |
| `User`           | `email`    | email adresa je jedinstvena                        |

U kodu su ova polja istovremeno `nullable=False` i `unique=True`. To su različita pravila:

- `nullable=False` zabranjuje SQL `NULL`;
- `unique=True` zabranjuje ponovljene vrednosti prema pravilima baze.

U source-u `password` nije jedinstven, što je ispravno: različiti korisnici mogu imati istu lozinku. Jedinstvenost treba dodati samo kada je ponavljanje zaista zabranjeno poslovnim pravilom.

## Jedinstvenost jedne kolone i kombinacije kolona

`unique=True` na koloni primenjuje se na tu kolonu samu. U primeru su `Category.name` i `Category.slug` svaki zasebno jedinstveni. Ne radi se o tome da je jedinstvena samo kombinacija ta dva polja.

Za poređenje, složeno ograničenje nad parom kolona može se zapisati pomoću `UniqueConstraint`:

```python
from sqlalchemy import Column, Integer, UniqueConstraint


class Membership(Base):
		__tablename__ = "membership"
		__table_args__ = (
				UniqueConstraint("organization_id", "user_id"),
		)

		organization_id = Column(Integer, nullable=False)
		user_id = Column(Integer, nullable=False)
```

Ovo sprečava da ista kombinacija organizacije i korisnika postoji dvaput. Samo `organization_id` može se ponoviti u više redova, kao i samo `user_id`; jedinstvena mora biti njihova kombinacija. Ovo je kratak dodatni pregled jer transkript najavljuje složena ograničenja za kasniju lekciju.

## Šta jedinstvenost ne garantuje

### Poređenje velikih i malih slova

`unique=True` ne znači automatski da se tekst normalizuje, niti da su `"Alice"` i `"alice"` uvek ista vrednost. Rezultat zavisi od tipa kolone, baze i njene collation postavke. Ako je potrebno neosetljivo poređenje, pravilo treba namerno definisati, na primer normalizacijom u aplikaciji ili odgovarajućim indeksom/kolacijom koju podržava baza.

Isto tako, jedinstvenost email adrese ne normalizuje automatski razmake, velika slova ili druge varijacije. Takvo pravilo treba definisati i dosledno primenjivati u sistemu.

### `NULL` vrednosti

Priloženi kod kombinuje `unique=True` sa `nullable=False`, pa za ove kolone `NULL` nije dozvoljen. Ako nullable kolona ima unique ograničenje, broj dozvoljenih `NULL` vrednosti zavisi od pravila konkretne baze. Ne treba pretpostaviti da unique znači „najviše jedan `NULL`“; proveri ponašanje svog dijalekta.

### Ograničenje dužine i validacija

`unique=True` ne proverava da li je vrednost smislen naziv, da li je slug dobro formiran ili da li email ima ispravan format. Takođe, ne zamenjuje `nullable=False`. To su odvojena pravila i validacije.

## `unique=True` naspram `Index(unique=True)`

**Dodatak: odnos ograničenja i indeksa.** `unique=True` izražava pravilo integriteta podataka. Baza za proveru jedinstvenosti obično koristi indeks ili strukturu slične namene, pa unique ograničenje često pomaže i pretrazi po toj koloni.

SQLAlchemy takođe omogućava eksplicitni jedinstveni indeks, na primer `Index("ix_product_slug", Product.slug, unique=True)`. Unique indeks takođe sprovodi jedinstvenost, ali indeks i `UniqueConstraint` nisu potpuno zamenljivi u svim bazama i migracionim situacijama. Ne dodavati dodatni unique indeks uz već postojeće unique ograničenje bez razloga: to može napraviti redundantne strukture i usporiti izmene podataka.

Indeks birati prema pravilima integriteta i stvarnim obrascima upita, a ne samo zato što kolona „deluje važna“. Konkretan efekat na performanse treba proveriti na ciljnoj bazi.

`unique=True` i `UniqueConstraint` opisuju šemu preko SQLAlchemy metapodataka. Ako tabela već postoji, sama izmena Python klase ne dodaje ograničenje u bazu; potrebna je migracija. Pre dodavanja unique ograničenja na postojeće podatke treba pronaći i razrešiti duplikate, inače migracija neće moći da se primeni.

## Razlike u source snapshot-ovima

- U `5_required.py` su `User.username` i `User.email` bili unique; u `6_default_values.py` to ograničenje je izostavljeno; `7_unique_column.py` ga ponovo postavlja.
- Ostala ograničenja iz ove lekcije su dodata na `Category.name`, `Category.slug`, `PromotionEvent.name`, `Product.name` i `Product.slug`.
- `updated_at` u `Product` i `Order` i dalje ima `nullable=False` i samo `onupdate`, bez početnog default-a. To je prethodno uočeni problem pri `INSERT`-u i nije posledica jedinstvenosti.
- Modeli još nemaju primarne ključeve, a `ProductPromotionEvent` je prazan; source fajl zato nije kompletan ORM primer za samostalno izvršavanje.

## Pitanja za proveru razumevanja

1. Šta sprečava `unique=True`?
2. Zašto aplikaciona provera „da li slug postoji“ ne zamenjuje unique ograničenje u bazi?
3. Da li su `Category.name` i `Category.slug` unique samo kao par ili svaki zasebno?
4. Kako se razlikuje `UniqueConstraint` nad dve kolone?
5. Da li `unique=True` automatski pravi tekstualnu vrednost neosetljivu na velika i mala slova?
6. Koje pravilo dodatno obezbeđuje `nullable=False`?
7. Zašto lozinka korisnika nije jedinstvena u source modelu?

## Sažetak

- `unique=True` traži od baze da odbaci duplikate u jednoj koloni.
- Ograničenje baze je potrebno čak i kada aplikacija unapred proverava da li vrednost postoji, jer konkurentni upisi mogu zaobići takvu proveru.
- U ovoj skripti jedinstveni su nazivi i slug-ovi kategorija/proizvoda, naziv promocije, korisničko ime i email.
- `nullable=False` i `unique=True` rešavaju različite probleme; source ih kombinuje za sva navedena polja.
- Ponašanje poređenja teksta, uključujući velika i mala slova i nullable unique kolone, zavisi od baze i njenih podešavanja.
- `UniqueConstraint` može da ograniči kombinaciju kolona; `unique=True` na pojedinačnim kolonama ovde pravi odvojena pravila.
- Unique indeks može da sprovodi jedinstvenost, ali ga ne treba redundantno dodavati uz postojeće ograničenje.
- U postojećoj bazi unique pravilo se primenjuje migracijom, nakon provere da već upisani podaci nemaju duplikate.
