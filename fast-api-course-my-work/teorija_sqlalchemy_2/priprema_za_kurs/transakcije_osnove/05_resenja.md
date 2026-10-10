# 05: Rešenja — transakcije

Pokušaj najpre zadatke iz [vežbi](04_vezbe.md). Kod je ilustrativan i koristi memorijski SQLite ili SQLAlchemy engine napravljen za tu vežbu.

## Rešenje 1: prepoznaj granicu

- `INSERT INTO account ...` je jedan SQL iskaz.
- `connection` je SQLAlchemy konekcija kojom se iskazi šalju bazi.
- blok sa skidanjem i dodavanjem novca, ograničen početkom i `COMMIT`-om, jeste transakcija koja sadrži više iskaza.

## Rešenje 2: potvrđen i poništen red

```python
import sqlite3

connection = sqlite3.connect(":memory:")
connection.execute(
    "CREATE TABLE note (id INTEGER PRIMARY KEY, text TEXT NOT NULL)"
)
connection.commit()

connection.execute("BEGIN")
connection.execute("INSERT INTO note (text) VALUES (?)", ("sačuvan",))
connection.commit()

connection.execute("BEGIN")
connection.execute("INSERT INTO note (text) VALUES (?)", ("poništen",))
connection.rollback()

rows = connection.execute("SELECT text FROM note ORDER BY id").fetchall()
assert rows == [("sačuvan",)]
connection.close()
```

Samo red iz potvrđene transakcije ostaje.

## Rešenje 3: greška i rollback

```python
import sqlite3

connection = sqlite3.connect(":memory:")
connection.execute("CREATE TABLE note (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")
connection.commit()

try:
    connection.execute("BEGIN")
    connection.execute("INSERT INTO note (id, text) VALUES (?, ?)", (1, "prvi"))
    connection.execute("INSERT INTO note (id, text) VALUES (?, ?)", (1, "duplikat"))
    connection.commit()
except sqlite3.IntegrityError:
    connection.rollback()

assert connection.execute("SELECT COUNT(*) FROM note").fetchone()[0] == 0
connection.close()
```

Drugi INSERT krši primarni ključ. Po rollback-u ni prvi INSERT iz iste nepotvrđene transakcije ne ostaje.

## Rešenje 4: `engine.connect()`

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite://")
with engine.begin() as connection:
    connection.execute(
        text("CREATE TABLE note (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")
    )

with engine.connect() as connection:
    connection.execute(
        text("INSERT INTO note (text) VALUES (:text)"),
        {"text": "bez commit-a"},
    )

with engine.connect() as connection:
    assert connection.execute(text("SELECT COUNT(*) FROM note")).scalar_one() == 0

with engine.connect() as connection:
    connection.execute(
        text("INSERT INTO note (text) VALUES (:text)"),
        {"text": "potvrđen"},
    )
    connection.commit()

with engine.connect() as connection:
    assert connection.execute(text("SELECT text FROM note")).scalar_one() == "potvrđen"

engine.dispose()
```

Prvi INSERT nije commit-ovan, pa se pri zatvaranju konekcije nepotvrđena transakcija poništava. Drugi je eksplicitno potvrđen i ostaje.

## Rešenje 5: `engine.begin()`

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite://")
with engine.begin() as connection:
    connection.execute(
        text("CREATE TABLE note (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")
    )

with engine.begin() as connection:
    connection.execute(text("INSERT INTO note (text) VALUES (:text)"), {"text": "jedan"})
    connection.execute(text("INSERT INTO note (text) VALUES (:text)"), {"text": "dva"})

try:
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO note (text) VALUES (:text)"), {"text": "ne ostaje"})
        raise RuntimeError("simulirana greška")
except RuntimeError:
    pass

with engine.connect() as connection:
    rows = connection.execute(text("SELECT text FROM note ORDER BY id")).scalars().all()
    assert rows == ["jedan", "dva"]

engine.dispose()
```

Normalan izlazak iz prvog bloka potvrđuje oba reda. Izuzetak koji izađe iz drugog transakcijskog bloka pokreće rollback.

Ako bismo grešku uhvatili i potisnuli unutar `with engine.begin()` bloka, kontekstni menadžer bi video normalan izlazak. Ako želimo rollback, greška mora izaći iz bloka ili moramo eksplicitno upravljati rollback-om.

## Rešenje 6: `SessionFactory.begin()`

```python
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)
SessionFactory = sessionmaker(engine)

with SessionFactory.begin() as session:
    session.add(User(name="sandy"))

with SessionFactory() as session:
    names = session.scalars(select(User.name)).all()
    assert names == ["sandy"]

engine.dispose()
```

Normalan izlazak iz `SessionFactory.begin()` bloka potvrđuje transakciju, a druga sesija vidi sačuvani red.

## Rešenje 7: `add`, `flush`, `commit`

```python
with SessionFactory() as session:
    user = User(name="patrick")
    session.add(user)

    assert user in session.new
    assert user.id is None

    session.flush()
    assert user.id is not None

    session.rollback()

with SessionFactory() as session:
    assert session.scalars(
        select(User).where(User.name == "patrick")
    ).first() is None
```

`add()` registruje objekat. `flush()` šalje INSERT i može da dobije ID, ali transakcija se još može rollback-ovati. Da bi red ostao sačuvan, koristi `session.commit()` ili normalno izađi iz `SessionFactory.begin()` bloka.
