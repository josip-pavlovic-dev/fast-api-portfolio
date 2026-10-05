# Lekcija 09: Podrazumevane vrednosti

## Cilj lekcije

Podrazumevana vrednost popunjava kolonu kada `INSERT` ne navede njenu vrednost. U ovoj lekciji koristimo default-e za booleanske statuse, nivo kategorije, količinu na stanju i vreme kreiranja.

Kurs uvodi dva mesta na kojima default može da se primeni:

- `default=...`: SQLAlchemy obezbeđuje vrednost dok priprema upis;
- `server_default=...`: podrazumevana vrednost je definisana u šemi baze i primenjuje je sama baza.

Važno je da default ne zamenjuje poslovnu odluku. Njegova vrednost treba da predstavlja bezbedno i smisleno početno stanje za taj podatak.

## Zašto su ERD i data dictionary korisni

ERD prvenstveno prikazuje strukturu i odnose među entitetima. Često ne navodi dovoljno detalja da bi se znalo koja vrednost treba da se koristi kada aplikacija ne pošalje podatak.

Data dictionary, odnosno rečnik podataka, može za svaku kolonu da zabeleži naziv, značenje, tip, obaveznost, ograničenja, odnose i eventualnu podrazumevanu vrednost. Na primer, ERD može pokazati polje `quantity`, dok data dictionary može da objasni da nova stavka zaliha počinje sa količinom `0`.

Default treba da proistekne iz tih pravila, a ne samo iz pogodnosti u kodu. Nula je odgovarajuća početna količina ako „nema evidentiranih komada“ zaista znači nula; ne bi bila ispravna zamena za nepoznatu količinu.

## `default`: vrednost koju obezbeđuje SQLAlchemy

Primeri iz source koda:

```python
is_active = Column(Boolean, nullable=False, default=False)
level = Column(SmallInteger, nullable=False, default=0)
quantity = Column(Integer, nullable=False, default=0)
created_at = Column(DateTime, default=func.now(), nullable=False)
```

### Isti obrazac u SQLAlchemy 2.x

U našem praktičnom paketu koristimo tipizovanu deklaraciju. Default-i su isti koncepti; menja se oblik deklaracije:

```python
from datetime import datetime

from sqlalchemy import Boolean, DateTime, SmallInteger, func
from sqlalchemy.orm import Mapped, mapped_column

aktivna: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
nivo: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
kreirano_u: Mapped[datetime] = mapped_column(
	DateTime,
	default=func.now(),
	nullable=False,
)
```

`default` nije ograničen samo na ORM `Session`: SQLAlchemy ga primenjuje na SQL iskaze koje generiše, uključujući ORM i Core `INSERT` operacije. Direktan SQL koji zaobilazi SQLAlchemy ne koristi ovaj client-side default.

Kada SQLAlchemy priprema `INSERT` i kolona nema prosleđenu vrednost, `default` obezbeđuje podrazumevanu vrednost. U prva tri primera to su Python vrednosti odgovarajućeg tipa: `False` ili `0`. Vrednost se šalje kao deo upita koji SQLAlchemy izvršava.

Default se izvršava pri upisu, a ne nužno u trenutku kada se ORM objekat napravi u Python-u. Zato se ne treba oslanjati na to da će atribut na novom objektu odmah prikazivati `False` ili `0` pre `flush()`/`INSERT` operacije.

Default važi samo kada upis ne navodi vrednost za kolonu. Konkretna vrednost koju aplikacija prosledi ima prednost. Takođe, SQLAlchemy `default` nije ograničenje u šemi baze: običan SQL upit ili drugi program koji ne koristi taj SQLAlchemy model neće dobiti ovu vrednost automatski.

### Podrazumevana vrednost po tipu

Source kod bira vrednosti koje odgovaraju značenju kolone:

| Model i kolona                           | Tip            | Default      | Obrazloženje u primeru                               |
| ---------------------------------------- | -------------- | ------------ | ---------------------------------------------------- |
| `Category.is_active`                     | `Boolean`      | `False`      | kategorija nije aktivna dok se ne aktivira           |
| `Category.level`                         | `SmallInteger` | `0`          | početni nivo kategorije                              |
| `Product.is_digital`                     | `Boolean`      | `False`      | proizvod se podrazumevano ne smatra digitalnim       |
| `Product.is_active`                      | `Boolean`      | `False`      | proizvod se podrazumevano ne smatra aktivnim         |
| `StockManagement.quantity`               | `Integer`      | `0`          | početna količina na stanju je nula                   |
| `Product.created_at`, `Order.created_at` | `DateTime`     | `func.now()` | vreme kreiranja obezbeđuje izraz baze u INSERT upitu |

Autor kursa posebno preporučuje da se za booleanske kolone razmotri eksplicitan default. Bez njega, početno stanje zavisi od prosleđene vrednosti ili nullable pravila; sa njim je očekivano stanje vidljivo u modelu.

## Razlika kod `default=func.now()`

`created_at` koristi:

```python
created_at = Column(DateTime, default=func.now(), nullable=False)
```

Ovaj default i dalje zadaje SQLAlchemy, ali njegova vrednost je SQL izraz. SQLAlchemy umeće izraz `now()` u `INSERT`, a samu funkciju izvršava baza. To se razlikuje od `default=False`, gde SQLAlchemy šalje običnu vrednost.

Iako se SQL izraz izvršava u bazi, `default=func.now()` sam po sebi ne dodaje `DEFAULT now()` u DDL definiciju kolone. Dakle, server izvršava funkciju, ali SQLAlchemy kontroliše da se izraz uključi u upit. Ova razlika je važna ako se redovi upisuju i iz drugih programa.

## `server_default`: default definisan u bazi

Ako sama baza treba da primeni vrednost kada `INSERT` izostavi kolonu, koristi se `server_default`. Na primer:

```python
from sqlalchemy import Boolean, Column, text

is_active = Column(
		Boolean,
		nullable=False,
		server_default=text("false"),
)
```

U našem SQLAlchemy 2.x stilu:

```python
from sqlalchemy import Boolean, text
from sqlalchemy.orm import Mapped, mapped_column

aktivna: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    server_default=text("false"),
)
```

Za PostgreSQL i SQLite `false` je uobičajen SQL izraz za boolean default; tačan literal i ponašanje treba proveriti za ciljni dijalekt. Integer primer je `server_default=text("0")`, a vremenski default može se zadati SQLAlchemy izrazom `server_default=func.now()`.

Default baze je deo DDL šeme i može da se primeni i kada upit dolazi iz drugog programa, pod uslovom da taj upit izostavi kolonu. Ako `INSERT` eksplicitno pošalje `NULL`, server default se ne koristi; uz `NOT NULL` baza će odbiti taj red. Default-i ne opravdavaju prosleđivanje `NULL` vrednosti.

### Poređenje

| Pitanje                                  | `default=...`                              | `server_default=...`                           |
| ---------------------------------------- | ------------------------------------------ | ---------------------------------------------- |
| Gde je pravilo definisano?               | U SQLAlchemy modelu/upitu                  | U definiciji kolone u bazi                     |
| Ko ga primenjuje?                        | SQLAlchemy pri pripremi upisa              | Baza kada upis izostavi kolonu                 |
| Važi za direktan SQL iz drugog programa? | Ne, osim ako taj program prosledi vrednost | Da, ako izostavi kolonu i baza ima taj default |
| Tipičan primer                           | `default=False`                            | `server_default=text("false")`                 |

Za aplikaciju koja ima samo jedan put upisa, `default` može biti dovoljan. Ako pravilo treba da važi za sve klijente baze, `server_default` je jača garancija na nivou šeme. Mogu se koristiti i zajedno, ali tada treba namerno uskladiti njihova značenja i vrednosti.

`server_default` je deo DDL metapodataka za kreiranje šeme. Ako tabela već postoji, sama izmena Python modela ne menja automatski postojeću bazu; promena šeme se primenjuje migracijom, na primer Alembic migracijom kada je uvedemo u projekat. `create_all()` takođe nije zamena za upravljanje izmenama postojeće šeme.

## Python callable kao default

Kada vrednost treba da se generiše u Python-u za svaki novi upis, prosleđuje se callable, odnosno funkcija bez pozivanja:

```python
import uuid

token = Column(String(36), default=lambda: str(uuid.uuid4()))
```

Tipizovana SQLAlchemy 2.x varijanta izgleda ovako:

```python
import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

token: Mapped[str] = mapped_column(
	String(36),
	default=lambda: str(uuid.uuid4()),
	nullable=False,
)
```

SQLAlchemy poziva callable kada mu je potreban default. Ne treba unapred pozvati funkciju, kao `default=str(uuid.uuid4())`, jer bi se tada jedna vrednost napravila pri učitavanju modula i koristila za sve redove.

Ovo je dopunski obrazac; priložena skripta lekcije 09 koristi skalarne Python vrednosti i SQL izraz `func.now()`, a ne Python callable.

## Default-i u priloženom source kodu

Skripta `6_default_values.py` postavlja sledeće default-e:

- `Category.is_active`: `False`;
- `Category.level`: `0`;
- `Product.is_digital` i `Product.is_active`: `False`;
- `Product.created_at` i `Order.created_at`: `func.now()`;
- `StockManagement.quantity`: `0`.

U našem praktičnom paketu odgovarajuća polja su `Kategorija.aktivna=False`, `Kategorija.nivo=0`, `Proizvod.digitalni=False`, `Proizvod.aktivan=False`, `StanjeZaliha.kolicina=0` i `kreirano_u=func.now()` kod proizvoda i porudžbine. Imena su prevedena, ali su namena i SQLAlchemy default-i sačuvani.

Ostala polja nemaju default u ovoj verziji. Zato, na primer, aplikacija mora da prosledi `last_checked_at`, `PromotionEvent` datume i `OrderProduct.quantity`.

`nullable=False` i default rešavaju povezana, ali različita pitanja. Default obezbeđuje vrednost ako je upis izostavi; `nullable=False` zabranjuje da u koloni ostane `NULL`. Default nije zamena za ograničenje, a ograničenje ne izračunava vrednost.

## Opažanja u odnosu na prethodni source snapshot

Ovo su razlike vidljive poređenjem fajlova, a ne zaključci iz transkripta:

- `User.username` i `User.email` u `6_default_values.py` više nemaju `unique=True`, iako su ga imali u `5_required.py`. Ako jedinstvenost ostaje poslovno pravilo, treba je vratiti u model/migraciju; ova lekcija ne objašnjava da je namerno uklonjena.
- `Product.updated_at` i `Order.updated_at` i dalje imaju `nullable=False` i `onupdate=func.now()`, ali nemaju početni default. `onupdate` se ne primenjuje na `INSERT`, pa red mora dobiti `updated_at` eksplicitno ili će insert pasti zbog `NOT NULL` ograničenja. To nije rešeno default-ima ove lekcije.
- Source snapshot i dalje nema primarne ključeve, a `ProductPromotionEvent` je prazan. Zbog toga fajl nije samostalno kompletan ORM primer.

## Pitanja za proveru razumevanja

1. Kada se primenjuje `default=False`?
2. Da li `default=False` dodaje serverski default u DDL?
3. Šta se razlikuje kod `default=func.now()` u odnosu na `default=0`?
4. Zašto drugi program koji direktno upisuje u bazu ne dobija nužno SQLAlchemy `default` vrednost?
5. Kada bi izabrao `server_default` umesto `default`?
6. Da li server default zamenjuje eksplicitno prosleđeni `NULL`?
7. Zašto `updated_at` iz skripte i dalje može da spreči insert?

## Sažetak

- Default daje početnu vrednost kada `INSERT` izostavi kolonu; vrednost treba da odgovara poslovnom značenju podatka.
- `default=False` i `default=0` su SQLAlchemy-jem primenjene vrednosti, dok je `default=func.now()` SQL izraz uključen u upit koji izvršava baza.
- `default=...` sam po sebi nije serverski default u DDL-u i ne pokriva upise koji zaobilaze SQLAlchemy model.
- `server_default=...` definiše default na strani baze i može da ga koristi svaki klijent koji izostavi kolonu.
- Eksplicitni `NULL` nije isto što i izostavljena kolona; default nije zamena za `nullable=False`.
- U source kodu `updated_at` i dalje nema početni default, a jedinstvenost `User.username` i `User.email` se razlikuje od prethodnog snapshot-a.
