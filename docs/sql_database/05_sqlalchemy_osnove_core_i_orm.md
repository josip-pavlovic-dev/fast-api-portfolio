# 05 SQLAlchemy osnove: Core i ORM

## Sta je SQLAlchemy

SQLAlchemy je Python biblioteka za rad sa SQL bazama.
Ima dva glavna sloja:

- Core: eksplicitniji rad sa SQL izrazima
- ORM: mapiranje tabela na Python klase

U FastAPI CRUD app najčešće koristiš ORM.

---

## Klasični pojmovi

- Engine: konekcija ka bazi
- Session: radna jedinica za upite i izmene
- Base: bazna klasa za ORM modele
- Model class: Python klasa koja predstavlja tabelu

---

## Minimalni tok

1. Definišeš engine.
2. Kreiraš SessionLocal factory.
3. Definišeš modele koji nasleđuju Base.
4. Pozivaš create_all (za lokalno i učenje).
5. Kroz session radiš add, query, commit, refresh.

---

## Primer mentalnog mapiranja

- tabela items <-> klasa Item
- red iz items <-> instanca klase Item
- kolona title <-> atribut item.title

---

## Session lifecycle i zatvaranje

Bitno pravilo u web app:

- jedna sesija po zahtevu
- session se zatvara nakon zahteva

Zašto:

- izbegavaš curenje konekcija
- izbegavaš neočekivano deljenje stanja između korisnika

---

## Commit i refresh

- `add`: stavlja objekat u sesiju
- `commit`: trajno upisuje u bazu i završava transakciju
- `refresh`: osvežava objekat vrednostima iz baze (npr. auto id)

---

## Query stil (stariji 1.x stil)

ORM primer ideje:

```python
item = db.query(Item).filter(Item.id == item_id).first()
```

Ako vrati `None`, tipično dižeš `404`.

---

## SQLAlchemy 2.0 stil upita

Primer ideje:

```python
from sqlalchemy import select

stmt = select(Item).where(Item.id == item_id) # gradi SQL izraz iz ORM modela Item
item = db.execute(stmt).scalars().first()
```

`stmt` je skraćeni naziv za `statement`, odnosno SQL izraz koji se gradi i kasnije izvršava.

`db.execute(stmt)` izvršava SQL izraz, a `scalars()` uzima ORM instance iz rezultata. Pod ORM instancama iz rezultata podrazumevamo redove koji su mapirani na ORM modele npr. `Item(id=1, title="Primer")`, ignorišući kolone koje nisu mapirane na ORM modele.

Na kraju, `first()` vraća prvi rezultat ili `None` ako ne postoji. Ovaj pristup omogućava jasnu separaciju između SQL izraza i njegovog izvršavanja, što doprinosi predvidljivijem i tipiziranijem kodu.

---

## Relacije u ORM

Pored `ForeignKey` kolone, definišeš i `relationship`.
To ti daje lak pristup povezanim objektima.

Primer ideje:

- item.owner
- user.items

---

## Lazy vs eager loading

- lazy: povezani podaci se učitavaju kasnije, na pristup
- eager: učitaju se odmah sa glavnim upitom

Ako ne paziš, možeš napraviti `N+1 query` problem.

---

## N+1 problem

Scenarijo:

1. Učitaš 100 items
2. Za svaki item posebno učitaš owner

Rezultat: 101 upit umesto 1–2.

Rešenje: `joinedload`/`selectinload` i dobar dizajn query-ja.

---

## SQLAlchemy i validacija

ORM modeli nisu zamena za API validaciju.

- ORM model: `struktura` i `persistence` (persistence znači trajno čuvanje u bazi)
- Pydantic schema: `ulaz/izlaz` API-a

Oba sloja su potrebna.

---

## Najčešće greške

- Mešanje `Session` objekta i `engine` objekta
- Zaboravljen `rollback` na exception blok (npr. `except: db.rollback()`)
- Vraćanje ORM objekata bez `response schema` kontrole
- Slaba granica između `route` i `data` sloja (npr. direktno korišćenje ORM modela u ruti umesto kroz servisni sloj)

---

## Zadaci

1. Napiši 2 ORM modela sa relacijom 1:N.
2. Napisi flow za create item: add -> commit -> refresh.
3. Simuliraj grešku pri commit i opisi gde ide rollback.
4. Objasni razliku ORM model vs Pydantic schema.

---

## Zaključak

SQLAlchemy je centralni alat za prelaz iz FastAPI osnova u ozbiljniji backend, omogućavajući efikasno upravljanje bazom podataka i ORM pristup podacima.
Sledeće ga uklapamo u konkretnu FastAPI arhitekturu sa `database.py`, `models.py` i `schemas.py`.
