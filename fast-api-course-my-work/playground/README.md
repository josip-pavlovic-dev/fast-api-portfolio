# Playground

Mesto za male, samostalne primere iz SQLAlchemy 2.0 kursa. Ovi primeri su odvojeni od aplikacionih projekata i modela u `sqlalchemy_orm_fundamentals/`.

Koristi se postojeci root `.venv`; ovaj folder nema svoj `requirements.txt` niti virtualno okruzenje.

## Pokretanje

Komande pokreci iz root-a repozitorijuma:

```bash
.venv/bin/python fast-api-course-my-work/playground/sqlalchemy_2/01_prva_tabela.py
```

## Dogovor za vezbanje

- Dodaj po jedan numerisani Python fajl za manji primer ili ideju iz kursa.
- Primeri treba da budu samostalni; ne uvoze modele iz aplikacija ili glavnog ORM projekta.
- Pocetne vezbe koriste SQLite bazu u memoriji (`sqlite://`), pa se podaci odbacuju kada se skripta zavrsi.
- `create_all()` pravi tabele koje nedostaju; ne brise niti resetuje postojece tabele.
- U pocetnom primeru je ukljucen SQLAlchemy `echo=True` da bi se video SQL koji se izvrsava.

## Pocetni primer

`sqlalchemy_2/01_prva_tabela.py` prikazuje deklarativni ORM model, primarni kljuc, obaveznu tekstualnu kolonu, pravljenje tabele, `Session`, INSERT i SELECT. Kasnije primere dodaj ovde redom dok prolazis kroz kurs.
