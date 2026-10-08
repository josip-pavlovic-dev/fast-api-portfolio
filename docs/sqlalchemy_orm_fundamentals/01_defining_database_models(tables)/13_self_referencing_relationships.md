# Lekcija 13: Samoreferencirajući strani ključevi

## Cilj lekcije

Samoreferencirajući strani ključ (self-referencing foreign key) je FK kolona koja referencira drugi red iste tabele. U našem projektu to je hijerarhija kategorija: jedna kategorija može biti roditelj drugoj kategoriji.

Primer hijerarhije:

```text
Elektronika
└── TV
    └── OLED TV
```

Sva tri zapisa su redovi iste tabele `kategorija`.

## Kako to izgleda u našem domenu

Za stablo kategorija koristimo primarni ključ `id` i dodatnu kolonu koja pokazuje na roditelja:

```text
kategorija.id           identifikuje red
kategorija.roditelj_id  referencira kategorija.id roditelja
```

Korenski čvor nema roditelja, pa `roditelj_id` treba da bude `NULL`.

|  id | roditelj_id | naziv       |
| --: | ----------: | ----------- |
|   1 |        NULL | Elektronika |
|   2 |           1 | TV          |
|   3 |           2 | OLED TV     |

Ovo je adjacency-list model: veza roditelj-dete čuva se u redu deteta.

## Trenutno stanje projekta

U praktičnom kodu (`fast-api-course-my-work/sqlalchemy_orm_fundamentals/models/catalog.py`) lekcija 13 je implementirana u klasi `Kategorija`:

- nullable FK kolona `roditelj_id` referencira `kategorija.id`;
- `roditelj` vodi do roditeljske kategorije ili `None` za koren;
- `deca` je kolekcija direktnih potkategorija;
- postojeći `proizvodi` relationship ka modelu `Proizvod` ostaje nezavisan.

Kod je napisan u SQLAlchemy 2.x stilu i uz svaki dodatak ima kratak komentar lekcije.

## Ispravna deklaracija u SQLAlchemy 2.x stilu

U našem stilu (`Mapped[...]` + `mapped_column()`) to izgleda ovako:

```python
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column


roditelj_id: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey("kategorija.id"),
    nullable=True,
)
```

`ForeignKey("kategorija.id")` obezbeđuje da svaka nenull vrednost pokazuje na postojeći red u istoj tabeli. `nullable=True` je ključno za korenske kategorije.

## `nullable=True` vs `nullable=False`

Ako želimo korenske kategorije bez roditelja, FK kolona mora dozvoliti `NULL`.

- `nullable=True`: dozvoljeni korenski čvorovi.
- `nullable=False`: svaki red mora imati roditelja, pa korenski čvor ne može da se unese bez dodatne poslovne konstrukcije.

Za naš scenario stabla kategorija odgovara `nullable=True`.

## `ForeignKey` i `nullable` su odvojeni argumenti

`nullable` pripada koloni (`mapped_column`/`Column`), ne `ForeignKey` objektu.

Pogresno:

```python
ForeignKey("kategorija.id", nullable=False)
```

Ispravno:

```python
mapped_column(ForeignKey("kategorija.id"), nullable=False)
```

Ili eksplicitno sa tipom:

```python
mapped_column(Integer, ForeignKey("kategorija.id"), nullable=False)
```

## FK kolona nije isto sto i ORM relationship

FK kolona cuva ID roditelja i baza proverava referencu. To je nivo seme.

ORM relationship je dodatni Python sloj za navigaciju kroz objekte. U projektu su dodata oba atributa u klasi `Kategorija`:

```python
from __future__ import annotations

from sqlalchemy.orm import Mapped, relationship


roditelj: Mapped[Kategorija | None] = relationship(
    remote_side=lambda: [Kategorija.id],
    back_populates="deca",
)
deca: Mapped[list[Kategorija]] = relationship(
    "Kategorija",
    back_populates="roditelj",
)
```

`remote_side` govori SQLAlchemy-ju koja strana self-reference je roditeljska strana.

## Sta FK ne garantuje sam po sebi

FK obezbeđuje da roditelj postoji, ali sam po sebi ne rešava sve probleme stabla:

- ne sprečava da red bude sam sebi roditelj;
- ne sprečava cikluse između vise čvorova;
- ne ograničava dubinu stabla;
- ne definiše automatski politiku brisanja podstabla bez dodatnih pravila (`ondelete`, ORM cascade, poslovna validacija).

## Provera implementacije

Implementacija je proverena pozivanjem `configure_mappers()` i korišćenjem privremene memorijske SQLite baze sa uključenim `PRAGMA foreign_keys=ON`. Uspešno su sačuvani koren, dete i unuk, a navigacija `dete.roditelj` i `koren.deca` je proverena. Pokušaj povezivanja na nepostojeći roditeljski ID ispravno je odbijen bazom.

## Sažetak

- Samoreferencirajući FK u ovom projektu treba da bude na tabeli `kategorija` i da referencira `kategorija.id`.
- Za korenske kategorije potreban je `nullable=True`.
- FK kolona i ORM relationship rešavaju različite nivoe problema: sema baze naspram navigacije kroz objekte.
- Lekcija 13 je implementirana u praktičnom modelu; samoreferencirajući FK je nullable kako bi korenske kategorije mogle da nemaju roditelja.
