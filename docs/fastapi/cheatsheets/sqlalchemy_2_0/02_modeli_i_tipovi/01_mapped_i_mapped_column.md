# 03 - Modeli u 2.0: Mapped i mapped_column

## Stari model (trenutno kod tebe)

```python
id = Column(Integer, primary_key=True)
email = Column(String, unique=True)
```

## Novi model (2.0)

```python
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

id: Mapped[int] = mapped_column(primary_key=True, index=True)
email: Mapped[str] = mapped_column(String, unique=True)
is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

## Zasto je ovo bolje

1. Tipovi su jasni i Pylance/Mypy bolje pomazu.
2. Model je citljiviji.
3. Lakse je odrzavati vece projekte.

## Kako mapirati tvoj `Users` model

Prva refaktor meta:

- `id`, `email`, `username`, `first_name`, `last_name`, `hashed_password`, `is_active`, `role`

Uradi model po model, ne sve odjednom.
