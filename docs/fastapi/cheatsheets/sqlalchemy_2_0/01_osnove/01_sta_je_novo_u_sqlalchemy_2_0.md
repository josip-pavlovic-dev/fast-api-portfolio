# 01 - Šta je novo u SQLAlchemy 2.0

## Zašto 2.0

SQLAlchemy 2.0 uvodi:

1. konzistentniji API,
2. čistiji typing,
3. moderniji ORM obrazac,
4. manje "magije" i predvidljiviji kod.

---

## Najveća razlika koju ćeš odmah osetiti

Stari stil (kod tebe trenutno):

```python
user = db.query(Users).filter(Users.id == user_id).first()
```

Novi 2.0 stil:

```python
from sqlalchemy import select

stmt = select(Users).where(Users.id == user_id)
user = db.execute(stmt).scalars().first()
```

`stmt` (statement) je `SQLAlchemy 2.0` ekvivalent `query` objekta iz starog stila gde je `where` ustvari `filter` u starom stilu koji definiše uslove za upit.

`stmt` predstavlja sam upit koji će biti izvršen nad bazom. Skraćeno, `stmt` definiše šta želiš da dobiješ iz baze, a `db.execute(stmt)` ga zapravo izvršava.

`scalars()` je metoda koja vraća rezultate upita kao listu objekata, slično `all()` u starom stilu.

`first()` vraća prvi rezultat iz liste, slično kao u starom stilu.

---

## Stari i novi stil modela (models.py)

Stari stil:

```python
id = Column(Integer, primary_key=True)
```

Novi stil:

```python
from sqlalchemy.orm import Mapped, mapped_column

id: Mapped[int] = mapped_column(primary_key=True)
```

`Mapped` je generički tip koji se koristi za označavanje tipa kolone u modelu, dok `mapped_column` definiše samu kolonu u bazi.

---

## Bitna poruka

SQLAlchemy 2.0 nije "druga biblioteka". To je isti SQLAlchemy sa modernim obrascem rada. Zato prelazak nije reset, nego evolucija onoga što već znaš.
