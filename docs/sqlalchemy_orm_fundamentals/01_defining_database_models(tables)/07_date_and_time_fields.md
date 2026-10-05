# Lekcija 07: Datumska i vremenska polja

## Cilj lekcije

U ovoj lekciji dodajemo datumske i vremenske kolone u modele i učimo kada vrednost nastaje: može se zadati ručno, izračunati u Python-u ili prepustiti bazi. Primeri iz ERD-a i skripte pokazuju sva tri česta slučaja:

- datum početka i završetka promotivnog događaja;
- automatski `created_at` i `updated_at` za proizvode i porudžbine;
- `last_checked_at`, datum i vreme sa uključenom opcijom za vremensku zonu.

Važno je razlikovati tip kolone od pravila koje popunjava tu kolonu. `DateTime` kaže kakva je vrednost; `default` i `onupdate` opisuju kada SQLAlchemy treba da obezbedi vrednost.

---

## Datum, vreme i datum sa vremenom

SQLAlchemy nudi odvojene tipove za različite potrebe:

| SQLAlchemy tip | Šta predstavlja               | Primer upotrebe                      |
| -------------- | ----------------------------- | ------------------------------------ |
| `Date`         | kalendarski datum bez vremena | početak i kraj promocije             |
| `Time`         | vreme u danu bez datuma       | vreme otvaranja                      |
| `DateTime`     | datum zajedno sa vremenom     | trenutak kreiranja ili izmene zapisa |

Skripta ove lekcije koristi `Date` i `DateTime`. `Time` se pominje kao raspoloživi tip, ali nije primenjen ni na jednu kolonu u priloženom modelu.

Primeri prikaza vrednosti u Python-u:

```python
from datetime import date, datetime, time

promotion_start = date(2026, 10, 3)
store_opening = time(9, 30)
product_created = datetime(2026, 10, 3, 9, 30)
```

Datum i vreme koje korisnik bira prema poslovnom pravilu, kao što su datumi promocije, obično se zadaju iz ulaznih podataka. Vreme nastanka ili izmene zapisa često se popunjava automatski.

---

## Polja u modelima iz skripte

Kurs nastavlja da koristi `Column(...)` i deklarativne modele iz prethodnih lekcija:

```python
from sqlalchemy import Column, Date, DateTime, func


class PromotionEvent(Base):
		__tablename__ = "promotion_event"

		start_date = Column(Date)
		end_date = Column(Date)


class Product(Base):
		__tablename__ = "product"

		created_at = Column(DateTime, default=func.now())
		updated_at = Column(DateTime, onupdate=func.now())


class StockManagement(Base):
		__tablename__ = "stock_management"

		last_checked_at = Column(DateTime(timezone=True))
```

U punoj skripti i model `Order` ima kolone `created_at` i `updated_at` sa istim podešavanjima kao `Product`.

### Nazivi u našem praktičnom paketu

Kursni snapshot ostaje na engleskom. U praktičnim modelima koristimo sledeće srpske ASCII nazive, uz ista SQLAlchemy podešavanja:

| Kursni model i polje              | Praktični model i polje              | Tip i ponašanje                   |
| --------------------------------- | ------------------------------------ | --------------------------------- |
| `PromotionEvent.start_date`       | `PromotivniDogadjaj.datum_pocetka`   | `Date`                            |
| `PromotionEvent.end_date`         | `PromotivniDogadjaj.datum_zavrsetka` | `Date`                            |
| `Product.created_at`              | `Proizvod.kreirano_u`                | `DateTime`, `default=func.now()`  |
| `Product.updated_at`              | `Proizvod.izmenjeno_u`               | `DateTime`, `onupdate=func.now()` |
| `StockManagement.last_checked_at` | `StanjeZaliha.poslednja_provera`     | `DateTime(timezone=True)`         |
| `Order.created_at`                | `Porudzbina.kreirano_u`              | `DateTime`, `default=func.now()`  |
| `Order.updated_at`                | `Porudzbina.izmenjeno_u`             | `DateTime`, `onupdate=func.now()` |

Source ne postavlja `nullable=False` za ova polja, pa praktične deklaracije koriste `Mapped[date | None]` ili `Mapped[datetime | None]`. Za `updated_at` je sačuvano i to da nema `default`: pri kreiranju reda polje može ostati `NULL` do prve izmene.

---

### Savremeni zapis u SQLAlchemy 2.0

U našem praktičnom paketu iste kolone pišemo pomoću `Mapped[...]` i `mapped_column()`. Ovo su isečci koji se dodaju unutar već postojećih klasa; nisu samostalne klase bez ostatka modela:

```python
from datetime import date, datetime

from sqlalchemy import Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

# Unutar PromotivniDogadjaj
datum_pocetka: Mapped[date | None] = mapped_column(Date)
datum_zavrsetka: Mapped[date | None] = mapped_column(Date)

# Unutar Proizvod i Porudzbina
kreirano_u: Mapped[datetime | None] = mapped_column(
	DateTime,
	default=func.now(),
)
izmenjeno_u: Mapped[datetime | None] = mapped_column(
	DateTime,
	onupdate=func.now(),
)

# Unutar StanjeZaliha
poslednja_provera: Mapped[datetime | None] = mapped_column(
	DateTime(timezone=True),
)
```

`Mapped[date | None]` i `Mapped[datetime | None]` kažu da Python atribut može biti `None`, pa SQLAlchemy dozvoljava SQL `NULL`, kao u kursnom source-u. Kada naredna lekcija uvede obaveznost, tipovi i `nullable=False` treba da se usklade sa tim pravilom.

---

## Automatsko vreme pri kreiranju: `default`

U skripti je polje `created_at` definisano ovako:

```python
created_at = Column(DateTime, default=func.now())
```

`default` se koristi kada se novom ORM objektu ili redu ne prosledi vrednost za tu kolonu. `func.now()` je SQLAlchemy izraz za SQL funkciju koja vraća trenutno vreme prema podržanom dijalektu. Kada SQLAlchemy izvrši `INSERT`, izraz se prosleđuje bazi, pa baza izračunava vreme u trenutku upisa.

Zbog toga `default=func.now()` nije isto što i Python poziv `datetime.now()`: u ovom primeru vrednost izračunava baza, a ne Python proces.

`func` je SQLAlchemy objekat za pravljenje SQL funkcijskih izraza. Izraz `func.now()` nije poziv Python sata u trenutku učitavanja fajla; to je SQL izraz koji SQLAlchemy umeće u upit. Za PostgreSQL se ovaj izraz tipično ispisuje kao `now()`, a samu funkciju izvršava PostgreSQL kada primi upit.

Pojednostavljen prikaz `INSERT` upita kada aplikacija nije zadala `kreirano_u`:

```sql
INSERT INTO proizvod (kreirano_u) VALUES (now());
```

---

Ovaj `now()` dolazi iz SQLAlchemy `default=func.now()` pri formiranju INSERT-a. Nije time automatski upisan `DEFAULT now()` u definiciju tabele.

Default ne sprečava eksplicitnu vrednost. Ako aplikacija prosledi `created_at`, ta vrednost se koristi umesto default izraza. To odgovara transkriptu: sistem može automatski da dodeli vreme, ali može i da upiše vreme koje je aplikacija dobila iz ulaza ili izračunala u Python-u.

---

## Automatsko vreme pri izmeni: `onupdate`

Skripta definiše `updated_at` ovako:

```python
updated_at = Column(DateTime, onupdate=func.now())
```

`onupdate` je vrednost koju SQLAlchemy dodaje pri `UPDATE` upitu kada se red menja, a aplikacija nije eksplicitno zadala novu vrednost za tu kolonu. Sa `func.now()` vreme izmene izračunava baza dok izvršava taj upit.

Razlika u odnosu na `default`:

- `default` je namenjen početnom unosu reda;
- `onupdate` je namenjen narednim izmenama reda.

U priloženoj skripti `updated_at` nema `default`. Prema tome, pri prvom unosu se ne postavlja automatski na vreme kreiranja; pošto kolona nije označena kao `nullable=False` i nema drugi default, može biti `NULL` dok se red prvi put ne ažurira. Ako je poželjno da polje ima vrednost i odmah po kreiranju, treba definisati i početni default, na primer `default=func.now()`, uz `onupdate=func.now()`.

`onupdate` nije isto što i trigger u bazi. Ono se primenjuje na upite koje SQLAlchemy generiše sa odgovarajućim pravilom; ako red menjaju drugi program ili ručno izvršen SQL, `onupdate` iz ORM modela se ne aktivira. Za pravilo koje mora da važi za sve klijente potrebna je odgovarajuća podrška same baze, kao što je serverski default ili trigger.

---

## Vreme izračunato u Python-u

Kurs pominje i mogućnost da Python napravi vremensku vrednost, pa da se ona prosledi bazi. Python callable može se postaviti kao default bez pozivanja funkcije prilikom definicije modela:

```python
from datetime import datetime, timezone

created_at = Column(
		DateTime(timezone=True),
		default=lambda: datetime.now(timezone.utc),
)
```

SQLAlchemy poziva funkciju kada je potrebna vrednost. Ne treba napisati `default=datetime.now()` jer bi se ta funkcija izvršila jednom, pri učitavanju modula, a ne za svaki novi red. Primer sa `timezone.utc` je savremena preporuka kada aplikacija želi da generiše vremenske oznake u UTC-u; kompatibilnost tipa kolone i ponašanje baze i dalje treba proveriti za izabrani dijalekt.

U tipizovanom SQLAlchemy 2.0 modelu isti Python-side default može se zapisati ovako:

```python
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

created_at: Mapped[datetime | None] = mapped_column(
	DateTime(timezone=True),
	default=lambda: datetime.now(timezone.utc),
)
```

Ovde Python callable vraća vrednost; za razliku od `default=func.now()`, vreme se ne traži od baze.

Izbor između Python-a i baze zavisi od toga gde želimo da bude izvor vremena. Vreme iz baze može biti doslednije kada više aplikacija upisuje u istu bazu. Python vreme može biti korisno kada aplikacija mora da kontroliše ili testira generisanu vrednost. Ne mešati naizmenično naive i timezone-aware `datetime` objekte.

---

## Vremenske zone: `DateTime(timezone=True)`

Za skladište poslednje provere skripta koristi:

```python
last_checked_at = Column(DateTime(timezone=True))
```

Parametar `timezone=True` traži od SQLAlchemy dijalekta tip `DateTime` koji podržava vremensku zonu. U PostgreSQL-u se to prevodi u `TIMESTAMP WITH TIME ZONE`. Ovo je korisno za vremenske trenutke koji treba da budu uporedivi bez obzira na lokalnu zonu aplikacije ili korisnika.

Ipak, opcija sama po sebi ne pretvara proizvoljnu vrednost u UTC, ne bira vremensku zonu korisnika i ne čuva nužno izvorni naziv zone poput `Europe/Belgrade`. Aplikacija treba dosledno da koristi timezone-aware vrednosti i da dogovori kako ih normalizuje i prikazuje. Podrška i detalji se razlikuju među bazama: SQLAlchemy tipovi su prenosivi, ali konkretno ponašanje zavisi od dijalekta i same baze.

---

## Pregled polja iz ERD-a i koda

| Model             | Kolona                     | Tip / ponašanje u skripti                                             |
| ----------------- | -------------------------- | --------------------------------------------------------------------- |
| `PromotionEvent`  | `start_date`, `end_date`   | `Date`; poslovni datumi bez vremena                                   |
| `Product`         | `created_at`               | `DateTime`; `default=func.now()` pri unosu                            |
| `Product`         | `updated_at`               | `DateTime`; `onupdate=func.now()` pri izmeni, bez default-a pri unosu |
| `StockManagement` | `last_checked_at`          | `DateTime(timezone=True)`                                             |
| `Order`           | `created_at`, `updated_at` | ista podešavanja kao kod `Product`                                    |

Ovaj pregled opisuje priloženi source kod. Ako ERD prikazuje drugačiju obaveznost, naziv ili ponašanje kolone, razliku treba uskladiti pre migracije, a ne pretpostaviti da je model već sprovodi.

---

## Bitna razlika: `default` naspram `server_default`

**Dodatak: preciziranje SQLAlchemy ponašanja.** `default=func.now()` je SQL izraz koji SQLAlchemy koristi prilikom generisanja `INSERT` upita. Iako samu funkciju `now()` izvršava baza, ovo podešavanje pripada SQLAlchemy-jevom generisanju upita; ono samo po sebi ne dodaje `DEFAULT now()` u definiciju tabele.

Ako podrazumevana vrednost treba da bude definisana u DDL-u i da važi i kada red upisuje klijent koji ne koristi ovaj SQLAlchemy model, koristi se `server_default`, na primer:

```python
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

kreirano_u: Mapped[datetime | None] = mapped_column(
	DateTime,
	server_default=func.now(),
)
```

`default`, `onupdate`, `server_default` i trigger nisu međusobno zamenljivi. Izbor zavisi od toga da li vrednost treba da kontroliše SQLAlchemy upit ili sama baza za sve klijente.

---

## Osnovni prevod u PostgreSQL

Ovo su orijentacioni primeri najvažnijih prevoda za ovu lekciju. Tačan DDL može sadržati dodatne detalje koje SQLAlchemy generiše za izabranu verziju i konfiguraciju.

| SQLAlchemy deklaracija                   | Tip ili SQL u PostgreSQL-u                  | Osnovno značenje                                                                         |
| ---------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `mapped_column(Date)`                    | `DATE`                                      | Datum bez vremena.                                                                       |
| `mapped_column(DateTime)`                | `TIMESTAMP WITHOUT TIME ZONE`               | Datum i vreme bez informacije o vremenskoj zoni.                                         |
| `mapped_column(DateTime(timezone=True))` | `TIMESTAMP WITH TIME ZONE`                  | Vremenski trenutak sa podrškom vremenske zone.                                           |
| `default=func.now()`                     | `INSERT ... VALUES (now())`                 | SQLAlchemy dodaje izraz u INSERT kada vrednost nije prosleđena.                          |
| `onupdate=func.now()`                    | `UPDATE ... SET kolona = now()`             | SQLAlchemy dodaje izraz u svoj UPDATE kada se red menja i nova vrednost nije prosleđena. |
| `server_default=func.now()`              | `kolona ... DEFAULT now()` u `CREATE TABLE` | Podrazumevana vrednost je definisana na strani baze i važi i za druge klijente.          |

Primer pojednostavljenog DDL-a za tri različita polja:

```sql
CREATE TABLE primer_vremena (
	datum DATE,
	lokalno_vreme TIMESTAMP WITHOUT TIME ZONE,
	vremenski_trenutak TIMESTAMP WITH TIME ZONE
);
```

Primeri INSERT-a i UPDATE-a koji ilustruju SQL izraze:

```sql
INSERT INTO proizvod (kreirano_u) VALUES (now());
UPDATE proizvod SET izmenjeno_u = now() WHERE id = 1;
```

Ove komande su objašnjavajući PostgreSQL prikaz, ne dodatne komande koje sada treba ručno izvršavati. Da vidiš SQL koji SQLAlchemy stvarno šalje, engine može da se napravi sa `echo=True`; tačan ispis zavisi od upita i dijalekta:

```python
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL, echo=True)
```

Ovde je `DATABASE_URL` prethodno podešena adresa baze; `echo=True` uključuje ispis SQLAlchemy SQL naredbi i parametara u log.

---

### Važna orijentacija za vremenske zone

U PostgreSQL-u `TIMESTAMP WITH TIME ZONE` se često naziva i `timestamptz`. On predstavlja vremenski trenutak; PostgreSQL ga normalizuje i prikazuje prema vremenskoj zoni sesije. Ne čuva originalni naziv zone, kao što je `Europe/Belgrade`. `TIMESTAMP WITHOUT TIME ZONE` čuva lokalni datum i vreme bez zone i ne konvertuje ga automatski. Detalje ćemo učiti u PostgreSQL delu kursa; za sada je dovoljno prepoznati prevod i izabrati `timezone=True` kada kolona predstavlja stvarni vremenski trenutak.

U ovom source-u `DateTime` bez `timezone=True` koristi se i uz `func.now()`. U PostgreSQL-u `now()` vraća zonirani vremenski trenutak; pri upisu u kolonu `TIMESTAMP WITHOUT TIME ZONE` PostgreSQL ga pretvara prema vremenskoj zoni sesije, a zona se ne čuva u koloni. Ovo prati kursni primer, ali ne znači da je to uvek najbolji izbor za aplikaciju; konačan dizajn zavisi od toga da li polje predstavlja lokalno vreme ili jedinstven trenutak.

---

## Ograničenja priloženog snapshot-a

Skripta ove lekcije nastavlja modele iz ranijih primera, ali nijedan model još nema primarni ključ. SQLAlchemy ORM zato ne može da mapira te klase kao potpune modele i fajl ne može samostalno da se izvrši do kraja. To je nedovršen snapshot kursa, a ne problem u deklaracijama `Date` ili `DateTime`. Primarne ključeve i ostala ograničenja ne dodajemo prećutno jer nisu deo priloženog izvora ove lekcije.

---

## Pitanja za proveru razumevanja

1. Kada koristiti `Date`, a kada `DateTime`?

ODGOVOR: `Date` koristimo kada je važan samo kalendarski datum, a `DateTime` kada su važni datum i vreme. Za vremenski trenutak koji treba jednoznačno porediti između sistema često se bira `DateTime(timezone=True)` i prosleđuju se timezone-aware Python vrednosti, često u UTC-u. To nije univerzalno pravilo za svako polje koje sadrži vreme: lokalno radno vreme, na primer, može imati drugačije zahteve. `timezone=True` traži od SQLAlchemy dijalekta tip koji podržava vremensku zonu; ne bira korisnikovu zonu, ne formatira vrednost za prikaz i ne garantuje isto ponašanje svake baze. U PostgreSQL-u se prevodi u `TIMESTAMP WITH TIME ZONE`; detaljnije ponašanje obrađivaćemo u PostgreSQL delu. UTC znači `Coordinated Universal Time` i služi kao zajednička vremenska referenca.

2. Šta se dešava sa `created_at` kada nije prosleđena vrednost pri unosu?

ODGOVOR: Ako vrednost nije prosleđena i kolona nije eksplicitno dobila `NULL`, SQLAlchemy ili baza mogu primeniti podrazumevanu vrednost, u zavisnosti od toga kako je ona definisana:

- `default=lambda: datetime.now(timezone.utc)` je Python callable: SQLAlchemy ga poziva i dobija vrednost u Python-u.
- `default=func.now()` je SQLAlchemy column default koji sadrži SQL izraz. SQLAlchemy uključi `now()` u svoj `INSERT`, a bazni server izvrši tu funkciju. To važi za ORM i SQLAlchemy Core upite, ali se time ne dodaje default u DDL šeme.
- `server_default=func.now()` definiše `DEFAULT now()` u DDL-u. Baza ga primenjuje i na upise klijenata koji ne koriste SQLAlchemy, kada izostave kolonu ili navedu `DEFAULT`. Eksplicitno prosleđeni `NULL` nije isto što i izostavljena vrednost.

Za Python vreme danas koristi `datetime.now(timezone.utc)`, a ne `datetime.utcnow()`, jer `utcnow()` vraća naive `datetime` bez podataka o zoni.

3. Da li `onupdate=func.now()` automatski postavlja početnu vrednost polja pri `INSERT` upitu?

ODGOVOR: Ne. `onupdate=func.now()` nije početna vrednost za `INSERT`; SQLAlchemy ga koristi za `UPDATE` iskaze kada se red menja, a nova vrednost za tu kolonu nije posebno prosleđena. Za početnu vrednost pri unosu potreban je `default` ili `server_default`.

4. Ko izračunava vreme u `default=func.now()`, a ko u Python callable default-u?

ODGOVOR: Kod `default=func.now()`, SQLAlchemy u svoj `INSERT` ubacuje SQL izraz `now()` i bazni server izračunava vreme kada izvršava upit. Kod Python callable default-a, SQLAlchemy poziva Python funkciju, na primer `lambda: datetime.now(timezone.utc)`, pre nego što pošalje upit.

5. Da li se `onupdate` iz ORM modela aktivira ako drugi klijent izvrši SQL `UPDATE` direktno nad bazom?

ODGOVOR: Ne, ako taj klijent zaista šalje SQL direktno bazi i zaobilazi SQLAlchemy. `onupdate` je SQLAlchemy-side ponašanje i može se primeniti na SQLAlchemy ORM ili Core `UPDATE` iskaze; ne postaje automatski trigger u bazi. Ako pravilo treba da važi za sve klijente, potrebna je serverska logika, na primer trigger.

6. Šta `timezone=True` garantuje, a šta ne garantuje?

ODGOVOR: `timezone=True` traži od SQLAlchemy dijalekta tip koji podržava vremensku zonu; na PostgreSQL-u to je `TIMESTAMP WITH TIME ZONE`. Samo podešavanje ne dodaje zonu naive Python vrednosti, ne bira korisnikovu lokalnu zonu i ne čuva nužno naziv zone kao `Europe/Belgrade`. Stvarna podrška i ponašanje zavise od baze i drajvera, pa je važno koristiti timezone-aware `datetime` vrednosti i proveriti pravila izabranog dijalekta.

7. Po čemu se `default=func.now()` razlikuje od `server_default=func.now()`?

ODGOVOR: `default=func.now()` je SQLAlchemy column default: pri SQLAlchemy `INSERT` upitu SQLAlchemy ubacuje izraz `now()` u iskaz, a baza ga izvršava. Ne dodaje `DEFAULT now()` u `CREATE TABLE`, pa ga ne koriste klijenti koji zaobilaze SQLAlchemy. `server_default=func.now()` upisuje `DEFAULT now()` u DDL šeme; baza ga primenjuje kada je kolona izostavljena ili je zatražen `DEFAULT`, uključujući upise drugih klijenata. U oba slučaja, eksplicitna vrednost ima prednost; eksplicitni `NULL` nije isto što i izostavljena kolona.

---

## Sažetak

- `Date`, `Time` i `DateTime` opisuju datum, vreme i datum zajedno sa vremenom; ova skripta koristi `Date` i `DateTime`.
- Datumi promocije su poslovni podaci, dok su `created_at` i `updated_at` tipične vremenske oznake za zapise.
- `default` obezbeđuje vrednost pri unosu kada nije eksplicitno prosleđena; `onupdate` obezbeđuje vrednost pri odgovarajućem SQLAlchemy `UPDATE` upitu.
- U skripti `updated_at` nema početni default, pa pri kreiranju može biti `NULL`.
- `func.now()` je SQL izraz čiju funkciju izvršava baza; Python callable default generiše vrednost u Python-u.
- `DateTime(timezone=True)` traži podršku vremenske zone od dijalekta, ali ne konvertuje automatski vrednosti niti garantuje isto ponašanje svake baze.
- `server_default` definiše podrazumevanu vrednost na strani baze; razlikuje se od SQLAlchemy `default`-a.
- Izvorni modeli još nemaju primarne ključeve i zato ovaj snapshot nije samostalno izvršiv kao ORM model.
