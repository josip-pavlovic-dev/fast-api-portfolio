# 02 - Engine, sessionmaker i Session u 2.0

## Engine ostaje centralan

I u 2.0 i dalje kreiraš engine:

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///./todosapp.db", connect_args={"check_same_thread": False})
```

---

## sessionmaker u 2.0

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
```

Za tvoj trenutni projekat ova forma je i dalje validna. Kasnije možeš uvesti i eksplicitnije tipove za `session factory`.

---

## Session životni ciklus u FastAPI

Već radiš ispravno:

1. Otvori sesiju po request-u
2. `yield` prema endpointu
3. Zatvori u `finally`

To ne menjaš zbog prelaska na 2.0. Menja se pre svega model i query stil.

---

## Ključna stvar za stabilnost

Ne uvodi 2.0 i Alembic istog dana u jednoj mega izmeni. Prvo stabilizuj 2.0 query/model stil, pa tek onda migracije.
