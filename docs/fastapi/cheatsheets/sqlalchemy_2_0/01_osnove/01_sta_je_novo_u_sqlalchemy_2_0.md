# 01 - Sta je novo u SQLAlchemy 2.0

## Zašto 2.0

`SQLAlchemy 2.0` uvodi:

1. konzistentniji `API`, što znači da je lakše predvideti ponašanje i koristiti ga u kodu
2. čistiji `typing` (bolja integracija sa Python type hintovima),
3. moderniji ORM obrazac (`Mapped` i `mapped_column` u SQLAlchemy 2.0)
4. manje "magije" i predvidljiviji kod. (`explicit is better than implicit`)

`Objektno-relacioni maper` sloj ili `ORM` sloj predstavlja sloj koji povezuje `Python objekte` i `objekte/tabele` u bazi podataka. Time on spaja objektno-orijentisani svet Pythona i relacioni svet baze podataka. `orm` je skraćeni naziv za `Object Relational Mapper` i deo je SQLAlchemy biblioteke. On omogućava rad sa bazom podataka koristeći Python objekte umesto direktnog pisanja SQL upita.

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

---

## Stari i novi stil modela

Stari stil:

```python
id = Column(Integer, primary_key=True)
```

Novi stil:

```python
from sqlalchemy.orm import Mapped, mapped_column

id: Mapped[int] = mapped_column(primary_key=True)
```

---

## Bitna poruka

SQLAlchemy 2.0 nije "druga biblioteka". To je isti `SQLAlchemy` sa modernim obrascem rada. Zato prelazak nije reset, nego evolucija onoga što već znaš.
