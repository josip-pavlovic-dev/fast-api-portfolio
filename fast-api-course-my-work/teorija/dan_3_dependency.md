# Dan 3 - Dependency injection: refaktorisanje main.py u TodoApp

Ovaj dokument prati tačno šta se promenilo u `fast-api-course-my-work/TodoApp/main.py` tokom rada na temi Depends/dependency injection, i zašto je svaka promena napravljena. Cilj je da svaki korak razumeš pre nego što nastaviš dalje.

---

## 1) Polazno stanje main.py

Pre bilo kakvih izmena, `main.py` je izgledao ovako:

```python
from typing import Annotated
from collections.abc import Generator
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import models  # noqa: F401 - potrebno da Base zna za Todos tabelu
from .db.base import Base
from .db.database import SessionLocal, engine
from .models import Todos

app = FastAPI(
    title="TodoApp API",
    description="API za upravljanje zadacima",
    version="1.0.0",
    contact={"name": "TodoApp Support", "email": "support@todoapp.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()
```

Šta je ovde bilo tačno:

- `main.py` je radio sve odjednom: kreiranje FastAPI aplikacije, `create_all`, definisanje `get_db` dependency-ja, definisanje `db_dependency` tipa, i sam endpoint.
- Funkcionalno je ispravno, ali je odgovornosti pomešalo u jednom fajlu.

---

## 2) Prva promena: uklanjanje pitanja-komentara i direktan Base

Ranije (u prethodnom koraku, van ovog fajla) postojao je komentar-pitanje pored importa:

```python
from .db.base import Base # Zašto nije iskorišćen direktno i sta koristi models.Base? Koju Base klasu SQLAlchemy koristi?
```

i poziv:

```python
models.Base.metadata.create_all(bind=engine)
```

Promenjeno u:

```python
from .db.base import Base
```

```python
Base.metadata.create_all(bind=engine)
```

Zašto:

- `Base` se sada uzima direktno iz `db/base.py`, gde je i definisan (izvor istine).
- `models.Base.metadata.create_all(...)` bi funkcionisalo isto (jer `models.py` importuje isti `Base`), ali direktan import je jasniji: odmah se vidi odakle `Base` dolazi, bez zaobilaznog puta preko `models` modula.
- Komentar-pitanje je uklonjen jer je bio radna beleška, ne trajna dokumentacija koda.

Napomena: `from . import models` je i dalje ostao u fajlu, jer je taj import nužan da SQLAlchemy registruje `Todos` tabelu u `Base.metadata` pre poziva `create_all()`. To je "side effect" import - ne koristi se direktno `models.nesto`, ali mora postojati.

---

## 3) Druga promena: premeštanje get_db i db_dependency u db/session.py

Ovo je glavna promena za temu "Dan 3 - dependency injection".

### Pre premeštanja

`get_db()` i `db_dependency` su živeli direktno u `main.py`:

```python
from .db.database import SessionLocal, engine

...

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
```

### Posle premeštanja

Sadržaj je preseljen u novi fajl `db/session.py`:

```python
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
```

A `main.py` sada samo uvozi gotov `db_dependency`:

```python
from .db.session import db_dependency
```

### Zašto je ovo bolja praksa

1. Razdvajanje odgovornosti (separation of concerns)
   - `db/database.py`: kako se pravi konekcija (`engine`, `SessionLocal`)
   - `db/session.py`: kako se ta konekcija koristi po jednom HTTP zahtevu (`get_db`, `db_dependency`)
   - `main.py`: sastavljanje aplikacije (FastAPI instanca, `create_all`, endpoint-i)

2. Priprema za routere
   - Kada uvedeš `routers/todos.py`, `routers/users.py` i slično, svaki od tih fajlova će trebati `db_dependency`.
   - Mnogo je čistije da svi importuju:

     ```python
     from ..db.session import db_dependency
     ```

     nego da svaki router ponovo definiše `get_db()`, ili (još gore) da importuje nešto iz `main.py`, što bi lako napravilo kružni import (`main.py` uvozi routere, routeri uvoze iz `main.py`).

3. Jedna tačka istine
   - Ako ikada promeniš logiku otvaranja/zatvaranja sesije (npr. dodaš logovanje grešaka u `finally`), menjaš je na jednom mestu, a ne u više fajlova.

---

## 4) Treća promena: zašto je SessionLocal uklonjen iz main.py

Ovo je pitanje na koje želiš najjasniji odgovor.

### Pre

```python
from .db.database import SessionLocal, engine
```

`main.py` je direktno uvozio `SessionLocal` zato što je sam `main.py` sadržao `get_db()` funkciju, a ta funkcija poziva `SessionLocal()` da otvori sesiju:

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()  # <- ovde je SessionLocal bio potreban
    ...
```

### Posle

```python
from .db.database import engine
from .db.session import db_dependency
```

`SessionLocal` više nije potreban u `main.py` zato što:

1. Funkcija `get_db()`, koja jedina poziva `SessionLocal()`, više ne živi u `main.py` - preseljena je u `db/session.py`.
2. `main.py` sada ne otvara nijednu sesiju direktno. On samo:
   - koristi `engine` da pozove `Base.metadata.create_all(bind=engine)` (ovo je jednokratna operacija pri startu aplikacije, ne po-request logika),
   - koristi gotov `db_dependency` (koji je već "spakovan" `Annotated[Session, Depends(get_db)]`) za endpoint parametre.

Ključna razlika za pamćenje:

- `engine` je i dalje potreban u `main.py` jer se koristi za `create_all()`.
- `SessionLocal` nije potreban u `main.py` jer se koristi isključivo unutar `get_db()`, a ta funkcija se sada nalazi u `db/session.py`.

Pravilo: uvozi u fajl samo ono što taj fajl stvarno koristi. Pošto `main.py` više ne sadrži kod koji direktno poziva `SessionLocal()`, taj import postaje mrtav (nekorišćen) i uklanja se.

Da je import ostao, dobio bi upozorenje tipa "imported but unused" - isti princip kao ranije sa `Todos` importom u `Project_3/main1.py`.

---

## 5) Finalno stanje main.py (trenutno)

```python
from fastapi import FastAPI

from . import models  # noqa: F401 - potrebno da Base zna za Todos tabelu
from .db.base import Base
from .db.database import engine
from .db.session import db_dependency
from .models import Todos

app = FastAPI(
    title="TodoApp API",
    description="API za upravljanje zadacima",
    version="1.0.0",
    contact={"name": "TodoApp Support", "email": "support@todoapp.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

Base.metadata.create_all(bind=engine)


@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()
```

Šta `main.py` sada radi, i ništa više od toga:

1. Kreira `FastAPI` aplikaciju (metadata: title, description, version, contact, license).
2. Osigurava da su modeli registrovani (`from . import models`).
3. Kreira tabele pri startu (`Base.metadata.create_all(bind=engine)`).
4. Definiše endpoint(e) koristeći gotov `db_dependency` iz `db/session.py`.

`main.py` se time pretvorio u tanak "orchestration" sloj, dok su detalji baze i dependency-ja premešteni u `db/` paket.

---

## 6) Mapa odgovornosti po fajlovima (posle svih promena)

```text
db/
  database.py   -> engine, SessionLocal (kako se konektujemo na bazu)
  base.py       -> Base (roditeljska klasa za ORM modele)
  session.py    -> get_db(), db_dependency (kako dobijamo sesiju po request-u)

models.py       -> Todos (ORM model / tabela)

main.py         -> FastAPI app, create_all, endpoint-i (sastavljanje aplikacije)
```

---

## 7) Samoprovera pre nastavka

Pre nego što predjes na sledeću temu, proveri da li umeš da odgovoriš:

1. Zašto je `Base` uvezen direktno iz `db/base.py`, umesto preko `models.Base`?
2. Šta tačno radi `from . import models` ako se `models` nigde direktno ne koristi u telu funkcija?
3. Zašto je `get_db()` premešten iz `main.py` u `db/session.py`?
4. Zašto `main.py` više ne uvozi `SessionLocal`, ali i dalje uvozi `engine`?
5. Šta bi se pokvarilo kada bi neki budući router fajl pokušao da uveze `db_dependency` direktno iz `main.py`?

Ako na sva pitanja možeš da odgovoriš svojim rečima, ova lekcija je usvojena i možeš nastaviti na sledeću temu (routers u tvom aktivnom projektu).
