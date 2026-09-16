# 05 SQLAlchemy osnove: Core i ORM

## Sta je SQLAlchemy

SQLAlchemy je Python biblioteka za rad sa SQL bazama.
Ima dva glavna sloja:

- Core: eksplicitniji rad sa SQL izrazima
- ORM: mapiranje tabela na Python klase

U FastAPI CRUD app najcesce koristis ORM.

## Klasicni pojmovi

- Engine: konekcija ka bazi
- Session: radna jedinica za upite i izmene
- Base: bazna klasa za ORM modele
- Model class: Python klasa koja predstavlja tabelu

## Minimalni tok

1. Definises engine.
2. Kreiras SessionLocal factory.
3. Definises modele koji nasledjuju Base.
4. Pozivas create_all (za lokalno i ucenje).
5. Kroz session radis add, query, commit, refresh.

## Primer mentalnog mapiranja

- tabela items <-> klasa Item
- red iz items <-> instanca klase Item
- kolona title <-> atribut item.title

## Session lifecycle

Bitno pravilo u web app:

- jedna sesija po zahtevu
- session se zatvara nakon zahteva

Zasto:

- izbegavas curenje konekcija
- izbegavas neocekivano deljenje stanja izmedju korisnika

## Commit i refresh

- add: stavlja objekat u sesiju
- commit: trajno upisuje u bazu
- refresh: osvezava objekat vrednostima iz baze (npr. auto id)

## Query stil

ORM primer ideje:

```python
item = db.query(Item).filter(Item.id == item_id).first()
```

Ako vrati None, tipicno dizes 404.

## Relacije u ORM

Pored ForeignKey kolone, definises i relationship.
To ti daje lak pristup povezanim objektima.

Primer ideje:

- item.owner
- user.items

## Lazy vs eager loading

- lazy: povezani podaci se ucitaju kasnije, na pristup
- eager: ucitaju se odmah sa glavnim upitom

Ako ne pazis, mozes napraviti N+1 query problem.

## N+1 problem

Scenarijo:

1. ucitas 100 items
2. za svaki item posebno ucitas owner

Rezultat: 101 upit umesto 1-2.

Resenje: joinedload/selectinload i dobar dizajn query-ja.

## SQLAlchemy i validacija

ORM modeli nisu zamena za API validaciju.

- ORM model: struktura i persistence
- Pydantic schema: ulaz/izlaz API-a

Oba sloja su potrebna.

## Najcesce greske

- mesanje Session objekta i engine
- zaboravljen rollback na exception
- vracanje ORM objekata bez response schema kontrole
- slaba granica izmedju route i data sloja

## Zadaci

1. Napisi 2 ORM modela sa relacijom 1:N.
2. Napisi flow za create item: add -> commit -> refresh.
3. Simuliraj gresku pri commit i opisi gde ide rollback.
4. Objasni razliku ORM model vs Pydantic schema.

## Zakljucak

SQLAlchemy je centralni alat za prelaz iz FastAPI osnova u ozbiljniji backend.
Sledece ga uklapamo u konkretnu FastAPI arhitekturu sa database.py, models.py i schemas.py.
