# Playground

Mesto za male, samostalne primere iz SQLAlchemy 2.0 kursa. Ovi primeri su odvojeni od aplikacionih projekata i modela u `sqlalchemy_orm_fundamentals/`.

Koristi se postojeći root `.venv`; ovaj folder nema svoj `requirements.txt` niti virtualno okruženje.

---

## Pokretanje

Komande pokreci iz root-a repozitorijuma:

```bash
.venv/bin/python fast-api-course-my-work/playground/sqlalchemy_2/01_prva_tabela.py
```

---

## Dogovor za vežbanje

- Dodaj po jedan numerisani Python fajl za manji primer ili ideju iz kursa.
- Primeri treba da budu samostalni; ne uvoze modele iz aplikacija ili glavnog ORM projekta.
- Pocetne vezbe koriste SQLite bazu u memoriji (`sqlite://`), pa se podaci odbacuju kada se skripta zavrsi.
- `create_all()` pravi tabele koje nedostaju; ne brise niti resetuje postojece tabele.
- U pocetnom primeru je ukljucen SQLAlchemy `echo=True` da bi se video SQL koji se izvrsava.

---

## Početni primer

`sqlalchemy_2/01_prva_tabela.py` prikazuje deklarativni ORM model, primarni ključ, obaveznu tekstualnu kolonu, pravljenje tabele, `Session`, INSERT i SELECT. Kasnije primere dodaj ovde redom dok prolaziš kroz kurs.

## Rešeni primeri po lekcijama

Kada prvo pokušaš vežbu iz odgovarajuće teorijske beleške, koristi [indeks rešenih primera za svih 10 lekcija](sqlalchemy_2/resenja/README.md) za poređenje. Svaki numerisani primer je samostalan i koristi SQLite bazu u memoriji.
