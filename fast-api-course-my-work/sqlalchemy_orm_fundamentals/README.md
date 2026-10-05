# SQLAlchemy ORM Fundamentals: radni projekat

Ovaj paket je praktična implementacija kursa u repozitorijumu, odvojena od transkripata i originalnih source snapshot-ova u `docs/sqlalchemy_orm_fundamentals/`. Kod se dopunjava postepeno, u skladu sa lekcijama.

## Struktura

```text
sqlalchemy_orm_fundamentals/
    db/
        base.py          # zajednička DeclarativeBase klasa
        database.py      # dodaće se kada kurs uvede engine
        session.py       # dodaće se kada kurs uvede ORM sesije
    models/
        __init__.py      # centralno učitavanje/izvoz modela
        catalog.py       # kategorije, proizvodi i stanje zaliha
        promotions.py    # promocije i veza proizvoda sa promocijama
        orders.py        # korisnici i porudžbine
```

Lekcija 05 definiše osam ORM klasa sa minimalnim autogenerisanim `id` ključem, raspoređenih po domenima u `catalog.py`, `promotions.py` i `orders.py`: `Kategorija`, `Proizvod`, `StanjeZaliha`, `PromotivniDogadjaj`, `VezaProizvodaIPromocije`, `Korisnik`, `Porudzbina` i `StavkaPorudzbine`. Lekcija 06 dodaje kolone i SQLAlchemy tipove, lekcija 07 dodaje datumska i vremenska polja, a lekcija 08 usklađuje anotacije `Mapped[...]` i `nullable` pravila. Tabele i polja koriste srpska ASCII imena, uz očuvanje tipova i ograničenja iz kursnog source-a, osim izričito dokumentovanih praktičnih korekcija. Snapshot-i na engleskom ostaju neizmenjeni. U praktičnim modelima `izmenjeno_u` dobija i `default=func.now()` uz `onupdate=func.now()` da bi obavezno polje imalo vrednost već pri `INSERT`-u; kurski source nema taj početni default. Strani ključevi i ORM veze dodavaćemo kada ih obradimo; engine i sesije još nisu implementirani.

`Base` je na jednom mestu da bi svi ORM modeli nasleđivali istu baznu klasu i registrovali svoje tabele u zajedničkom `Base.metadata`. Modeli će biti grupisani po domenu umesto da se pravi poseban fajl za svaku malu klasu.

## Dogovor za rad

- Koristi se postojeći `.venv` iz root-a repozitorijuma. Ovaj paket nema zaseban `.venv` niti poseban `requirements.txt`.
- Ovaj projekat se gradi lekciju po lekciju. Ne dodajemo unapred engine, sesije, sve modele ili PostgreSQL konfiguraciju pre nego što ih kurs uvede.
- U sopstvenom kodu koristićemo SQLAlchemy 2.x tipizovani ORM stil: `Mapped[...]` i `mapped_column()`. Kada se kurski snapshot oslanja na stariji `Column` stil, sačuvaćemo ga neizmenjenog i objasniti razliku.
- Nazive domena u ovom paketu pišemo na srpskom ASCII slovima; nazivi SQLAlchemy API-ja ostaju standardni.
- Ne pokrećemo `drop_all()`/reset skripte nad bazom sa podacima koje treba sačuvati. Povezivanje i schema operacije uvode se tek u narednoj oblasti.

## Uvoz paketa

Iz root-a repozitorijuma paket može da se uveze dodavanjem radnog direktorijuma kursa u `PYTHONPATH`:

```bash
PYTHONPATH=fast-api-course-my-work .venv/bin/python -c "from sqlalchemy_orm_fundamentals.db.base import Base; print(Base.metadata.tables)"
```

Ova komanda samo učitava `Base`; ne povezuje se sa bazom i ne kreira tabele.
