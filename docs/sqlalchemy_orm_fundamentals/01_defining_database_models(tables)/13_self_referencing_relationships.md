# Lekcija 13: Samoreferencirajući strani ključevi

## Cilj lekcije

Samoreferencirajući strani ključ (self-referencing foreign key) je FK kolona koja referencira drugu kolonu u istoj tabeli. Koristi se kada zapisi mogu da budu povezani hijerarhijski, na primer kategorija i njene potkategorije.

Primer hijerarhije:

```text
Elektronika
└── TV
	└── OLED TV
```

Sva tri zapisa su redovi tabele `category`. Svaki red osim korenskog može da sačuva ID svog roditelja.

## Model stabla u jednoj tabeli

Za hijerarhiju kategorija koristimo primarni ključ `id` i dodatnu kolonu koja pokazuje na roditeljsku kategoriju:

```text
category.id          identifikuje red
category.parent_id   referencira category.id roditelja
```

Na primer, red za `TV` čuva ID kategorije `Elektronika` u koloni `parent_id`. Red za `OLED TV` čuva ID kategorije `TV`. Korenska kategorija nema roditelja.

| `id` | `parent_id` | `name`      |
| ---: | ----------: | ----------- |
|    1 |      `NULL` | Elektronika |
|    2 |           1 | TV          |
|    3 |           2 | OLED TV     |

Ovaj oblik baze naziva se adjacency list: veza roditelj–dete čuva se direktno na redu deteta. Kolona u dostavljenom kodu se zove `category_id`; naziv `parent_id` bi bio jasniji jer razlikuje roditeljsku kategoriju od `Product.category_id`, koji referencira kategoriju proizvoda.

## Ispravna deklaracija samoreferencirajućeg FK-a

Strani ključ referencira istu tabelu preko stringa `"category.id"`:

```python
from sqlalchemy import Column, ForeignKey, Integer


class Category(Base):
	__tablename__ = "category"

	id = Column(Integer, primary_key=True, autoincrement=True)
	parent_id = Column(
		Integer,
		ForeignKey("category.id"),
		nullable=True,
	)
```

Ovde `ForeignKey("category.id")` kaže da svaka nenull vrednost `parent_id` mora da odgovara postojećem `Category.id`. `nullable=True` dozvoljava korenski red bez roditelja. Ako se zadrži naziv iz kursnog source-a, isti oblik je `category_id = Column(Integer, ForeignKey("category.id"), nullable=True)`.

## Korenski čvor i `nullable`

U transkriptu se najpre kaže da korenska kategorija nema parent ID, a zatim se pominje `nullable=False`. Te dve postavke su u konfliktu:

- ako hijerarhija ima korenske kategorije bez roditelja, FK kolona mora dozvoliti `NULL`;
- ako se postavi `nullable=False`, svaki red mora imati roditelja i ne može se direktno napraviti korenska kategorija.

Za model stabla u kojem postoje koreni, odgovarajuće pravilo je `nullable=True`. Ako poslovno pravilo zaista zahteva roditelja za svaki red, može se koristiti `nullable=False`, ali tada koreni moraju biti predstavljeni na drugi način, na primer posebnom vršnom kategorijom. Izbor je poslovno pravilo, ne nešto što FK sam odlučuje.

## `ForeignKey` i `nullable` su argumenti različitih nivoa

Source kod sadrži:

```python
category_id: Column[int] = Column(ForeignKey("category.id", nullable=False))
```

`nullable` nije argument `ForeignKey(...)`. Ono pripada `Column(...)`, pored tipa i FK-a. SQLAlchemy 2.0 pri uvozu priloženog source fajla baca `TypeError` jer je `nullable` prosleđen `ForeignKey` konstruktoru.

Oblik deklaracije za obaveznog roditelja bio bi:

```python
category_id = Column(
	Integer,
	ForeignKey("category.id"),
	nullable=False,
)
```

Taj primer je sintaksno ispravan, ali ne dozvoljava korensku kategoriju. Za korene treba koristiti `nullable=True`, kao u prethodnom primeru. Source fajl nisam prepravljao; greška i razlika u poslovnom pravilu su zabeležene ovde.

## FK kolona nije isto što i ORM `relationship()`

Transkript za ovu lekciju kaže da je za osnovnu samoreferencirajuću vezu dovoljno dodati FK kolonu. To je dovoljno da baza čuva roditeljski ID i proverava referencu. Dostavljeni source ne dodaje ORM atribute za roditelja i decu; postojeći `Category.product` opisuje vezu kategorije sa proizvodima, ne vezu kategorije sa drugim kategorijama.

**Dodatak: ORM navigacija kroz hijerarhiju.** Da bi se u SQLAlchemy ORM-u pristupalo roditelju i deci preko Python atributa, veza može da se opiše na obe strane. `remote_side` ukazuje koji je `id` udaljena, referentna strana samoreferencirajuće veze:

```python
from sqlalchemy.orm import relationship


class Category(Base):
	__tablename__ = "category"

	id = Column(Integer, primary_key=True, autoincrement=True)
	parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)

	parent = relationship(
		"Category",
		remote_side=[id],
		back_populates="children",
	)
	children = relationship("Category", back_populates="parent")
```

Sada `category.parent` predstavlja roditelja ili `None` za korenski red, dok `category.children` predstavlja kolekciju potkategorija. Ova ORM konfiguracija ne dodaje FK kolonu; FK kolona je i dalje `parent_id`. Primer je dopuna, ne deklaracija iz priloženog source fajla.

## FK ne sprečava svaki problem stabla

FK ograničenje obezbeđuje da roditeljski red postoji, ali samo po sebi ne garantuje da podaci čine ispravno stablo:

- red može biti postavljen kao sopstveni roditelj;
- dve ili više kategorija mogu napraviti ciklus;
- ne ograničava se automatski dubina hijerarhije;
- brisanje roditelja sa decom zavisi od FK `ondelete` pravila i konfiguracije baze.

Takva pravila zahtevaju dodatnu validaciju, pažljivo definisanu politiku brisanja ili druga ograničenja. U source kodu nije navedeno `ondelete="CASCADE"`, pa ne treba pretpostaviti da se deca automatski brišu sa roditeljem.

## Primer iz transkripta

Transkript opisuje tri kategorije:

1. `id=1`, bez roditelja: korenska kategorija;
2. `id=2`, `parent_id=1`: potkategorija prve kategorije;
3. `id=3`, `parent_id=2`: potkategorija druge kategorije.

Tako nastaje više nivoa hijerarhije bez posebne tabele za svaki nivo. Transkript se usput pogrešno poziva na „product“ kada opisuje kategoriju; primer i relacija koju treba izgraditi odnose se na kategorije.

## Sažetak

- Samoreferencirajući FK pokazuje iz kolone tabele na primarni ključ reda u istoj tabeli.
- Za kategorije i potkategorije, dete čuva ID roditelja; to je adjacency-list model hijerarhije.
- Ako korenski red nema roditelja, FK kolona mora biti `nullable=True`; `nullable=False` zabranjuje korene.
- `nullable` pripada `Column(...)`, ne `ForeignKey(...)`; dostavljeni source ovako napisan ne može da se uveze.
- Sam FK obezbeđuje referencu u bazi; ORM navigacija `parent`/`children` je poseban `relationship()` dodatak i nije prisutna u source kodu.
- FK sam ne otkriva cikluse, ne ograničava dubinu i ne zadaje automatsko brisanje dece.
