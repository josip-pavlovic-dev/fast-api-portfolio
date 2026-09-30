# 01 - Sta je novo u SQLAlchemy 2.0

## Zasto 2.0

SQLAlchemy 2.0 uvodi:

1. konzistentniji API,
2. cistiji typing,
3. moderniji ORM obrazac,
4. manje "magije" i predvidljiviji kod.

## Najveca razlika koju ces odmah osetiti

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

## Bitna poruka

SQLAlchemy 2.0 nije "druga biblioteka". To je isti SQLAlchemy sa modernim obrascem rada. Zato prelazak nije reset, nego evolucija onoga sto vec znas.
