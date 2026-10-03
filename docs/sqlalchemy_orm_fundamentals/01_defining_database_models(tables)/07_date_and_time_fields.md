# Lekcija 07: Datumska i vremenska polja

## Cilj lekcije

U ovoj lekciji dodajemo datumske i vremenske kolone u modele i učimo kada vrednost nastaje: može se zadati ručno, izračunati u Python-u ili prepustiti bazi. Primeri iz ERD-a i skripte pokazuju sva tri česta slučaja:

- datum početka i završetka promotivnog događaja;
- automatski `created_at` i `updated_at` za proizvode i porudžbine;
- `last_checked_at`, datum i vreme sa uključenom opcijom za vremensku zonu.

Važno je razlikovati tip kolone od pravila koje popunjava tu kolonu. `DateTime` kaže kakva je vrednost; `default` i `onupdate` opisuju kada SQLAlchemy treba da obezbedi vrednost.

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

## Automatsko vreme pri kreiranju: `default`

U skripti je polje `created_at` definisano ovako:

```python
created_at = Column(DateTime, default=func.now())
```

`default` se koristi kada se novom ORM objektu ili redu ne prosledi vrednost za tu kolonu. `func.now()` je SQLAlchemy izraz za SQL funkciju koja vraća trenutno vreme prema podržanom dijalektu. Kada SQLAlchemy izvrši `INSERT`, izraz se prosleđuje bazi, pa baza izračunava vreme u trenutku upisa.

Zbog toga `default=func.now()` nije isto što i Python poziv `datetime.now()`: u ovom primeru vrednost izračunava baza, a ne Python proces.

Default ne sprečava eksplicitnu vrednost. Ako aplikacija prosledi `created_at`, ta vrednost se koristi umesto default izraza. To odgovara transkriptu: sistem može automatski da dodeli vreme, ali može i da upiše vreme koje je aplikacija dobila iz ulaza ili izračunala u Python-u.

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

Izbor između Python-a i baze zavisi od toga gde želimo da bude izvor vremena. Vreme iz baze može biti doslednije kada više aplikacija upisuje u istu bazu. Python vreme može biti korisno kada aplikacija mora da kontroliše ili testira generisanu vrednost. Ne mešati naizmenično naive i timezone-aware `datetime` objekte.

## Vremenske zone: `DateTime(timezone=True)`

Za skladište poslednje provere skripta koristi:

```python
last_checked_at = Column(DateTime(timezone=True))
```

Parametar `timezone=True` traži od SQLAlchemy dijalekta tip `DateTime` koji podržava vremensku zonu. U PostgreSQL-u se to prevodi u `TIMESTAMP WITH TIME ZONE`. Ovo je korisno za vremenske trenutke koji treba da budu uporedivi bez obzira na lokalnu zonu aplikacije ili korisnika.

Ipak, opcija sama po sebi ne pretvara proizvoljnu vrednost u UTC, ne bira vremensku zonu korisnika i ne čuva nužno izvorni naziv zone poput `Europe/Belgrade`. Aplikacija treba dosledno da koristi timezone-aware vrednosti i da dogovori kako ih normalizuje i prikazuje. Podrška i detalji se razlikuju među bazama: SQLAlchemy tipovi su prenosivi, ali konkretno ponašanje zavisi od dijalekta i same baze.

## Pregled polja iz ERD-a i koda

| Model             | Kolona                     | Tip / ponašanje u skripti                                             |
| ----------------- | -------------------------- | --------------------------------------------------------------------- |
| `PromotionEvent`  | `start_date`, `end_date`   | `Date`; poslovni datumi bez vremena                                   |
| `Product`         | `created_at`               | `DateTime`; `default=func.now()` pri unosu                            |
| `Product`         | `updated_at`               | `DateTime`; `onupdate=func.now()` pri izmeni, bez default-a pri unosu |
| `StockManagement` | `last_checked_at`          | `DateTime(timezone=True)`                                             |
| `Order`           | `created_at`, `updated_at` | ista podešavanja kao kod `Product`                                    |

Ovaj pregled opisuje priloženi source kod. Ako ERD prikazuje drugačiju obaveznost, naziv ili ponašanje kolone, razliku treba uskladiti pre migracije, a ne pretpostaviti da je model već sprovodi.

## Bitna razlika: `default` naspram `server_default`

**Dodatak: preciziranje SQLAlchemy ponašanja.** `default=func.now()` je SQL izraz koji SQLAlchemy koristi prilikom generisanja `INSERT` upita. Iako samu funkciju `now()` izvršava baza, ovo podešavanje pripada SQLAlchemy-jevom generisanju upita; ono samo po sebi ne dodaje `DEFAULT now()` u definiciju tabele.

Ako podrazumevana vrednost treba da bude definisana u DDL-u i da važi i kada red upisuje klijent koji ne koristi ovaj SQLAlchemy model, koristi se `server_default`, na primer:

```python
from sqlalchemy import DateTime, func

created_at = Column(DateTime, server_default=func.now())
```

`default`, `onupdate`, `server_default` i trigger nisu međusobno zamenljivi. Izbor zavisi od toga da li vrednost treba da kontroliše SQLAlchemy upit ili sama baza za sve klijente.

## Ograničenja priloženog snapshot-a

Skripta ove lekcije nastavlja modele iz ranijih primera, ali nijedan model još nema primarni ključ. SQLAlchemy ORM zato ne može da mapira te klase kao potpune modele i fajl ne može samostalno da se izvrši do kraja. To je nedovršen snapshot kursa, a ne problem u deklaracijama `Date` ili `DateTime`. Primarne ključeve i ostala ograničenja ne dodajemo prećutno jer nisu deo priloženog izvora ove lekcije.

## Pitanja za proveru razumevanja

1. Kada koristiti `Date`, a kada `DateTime`?
2. Šta se dešava sa `created_at` kada nije prosleđena vrednost pri unosu?
3. Da li `onupdate=func.now()` automatski postavlja početnu vrednost polja pri `INSERT` upitu?
4. Ko izračunava vreme u `default=func.now()`, a ko u Python callable default-u?
5. Da li se `onupdate` iz ORM modela aktivira ako drugi klijent izvrši SQL `UPDATE` direktno nad bazom?
6. Šta `timezone=True` garantuje, a šta ne garantuje?
7. Po čemu se `default=func.now()` razlikuje od `server_default=func.now()`?

## Sažetak

- `Date`, `Time` i `DateTime` opisuju datum, vreme i datum zajedno sa vremenom; ova skripta koristi `Date` i `DateTime`.
- Datumi promocije su poslovni podaci, dok su `created_at` i `updated_at` tipične vremenske oznake za zapise.
- `default` obezbeđuje vrednost pri unosu kada nije eksplicitno prosleđena; `onupdate` obezbeđuje vrednost pri odgovarajućem SQLAlchemy `UPDATE` upitu.
- U skripti `updated_at` nema početni default, pa pri kreiranju može biti `NULL`.
- `func.now()` je SQL izraz čiju funkciju izvršava baza; Python callable default generiše vrednost u Python-u.
- `DateTime(timezone=True)` traži podršku vremenske zone od dijalekta, ali ne konvertuje automatski vrednosti niti garantuje isto ponašanje svake baze.
- `server_default` definiše podrazumevanu vrednost na strani baze; razlikuje se od SQLAlchemy `default`-a.
- Izvorni modeli još nemaju primarne ključeve i zato ovaj snapshot nije samostalno izvršiv kao ORM model.
