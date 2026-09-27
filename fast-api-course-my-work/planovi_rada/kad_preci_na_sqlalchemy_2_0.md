# Kad preći na SQLAlchemy 2.0

Na osnovu trenutnog napretka, **još ne bih sada refaktorisao kod u SQLAlchemy 2.0**.

Trenutno si u delu autentifikacije, a najkorisniji trenutak za prelazak je:

**posle završetka Section 11: Authenticate Requests, a pre Section 12/13**, odnosno pre ozbiljnog production database setup-a i Alembic migracija.

Tada ćeš već razumeti:

- modele i kolone
- `Session` i dependency
- `query()`, `filter()`, `first()`
- ORM instance
- autentifikaciju i rad sa korisničkim modelom
- osnovni CRUD

Pre Alembic-a je dobro imati konačniju verziju modela, na primer:

```python
from sqlalchemy.orm import Mapped, mapped_column

hashed_password: Mapped[str] = mapped_column(nullable=False)
is_active: Mapped[bool] = mapped_column(default=True)
```

Moj predlog redosleda:

1. Završi autentifikaciju i JWT deo.
2. Nauči osnovnu Alembic teoriju, ali još ne radi migracije.
3. Pređi na SQLAlchemy 2.0 stil i refaktoriši modele/query-je.
4. Tek onda radi Section 12 i Section 13 sa production bazom i Alembic migracijama.
5. Nakon toga nastavi na testing, deployment i full-stack delove.

Dakle, **checkpoint za SQLAlchemy 2.0: kraj Section 11, pre Section 12/13**.
