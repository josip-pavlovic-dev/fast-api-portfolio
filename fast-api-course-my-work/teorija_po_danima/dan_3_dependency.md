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
- Funkcionalno je ispravno, ali su odgovornosti pomešane u jednom fajlu.

---

## 2) Prva promena: uklanjanje pitanja-komentara i direktan Base

Ranije (u prethodnom koraku, van ovog fajla) postojao je komentar-pitanje pored importa:

```python
from .db.base import Base # Zašto nije iskorišćen direktno i sta koristi models.Base? Koju Base klasu SQLAlchemy koristi?
```

Poziv `create_all` je ranije išao preko `models.Base.metadata.create_all(bind=engine)`, a sada je direktno preko `Base.metadata.create_all(bind=engine)`. Klasa `Base` je sada uzeta direktno iz `db/base.py`, što je izvor istine za definiciju svih tabela. Ranije je `Base` dolazila indirektno kroz `models`, što je bilo manje jasno, i važilo je pravilo:

```python
models.Base.metadata.create_all(bind=engine)
```

Sada je promenjeno u:

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

Napomena: `from . import models` je i dalje ostao u fajlu, jer je taj import nužan da SQLAlchemy registruje `Todos` tabelu u `Base.metadata` pre poziva `create_all()`. Nužno je da se importuje `models`, čak i ako se direktno ne koristi u kodu, zbog `"side effect" registracije tabela`.

`side effect` registracija tabela znači da se importovanjem `models` fajla automatski registruju sve tabele definisane u njemu u `Base.metadata`, što je neophodno pre poziva `create_all()`. Ovo je česta praksa u SQLAlchemy projektima kako bi se osiguralo da su sve tabele registrovane pre nego što se pokuša njihovo kreiranje u bazi.

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

Zato što želimo da `Base` bude jedinstvena roditeljska klasa za sve ORM modele i da se tabele kreiraju na osnovu te klase, a ne direktno iz `models.py`. Ovo omogućava centralizovano upravljanje metapodacima i olakšava migracije i kreiranje tabela.

2. Šta tačno radi `from . import models` ako se `models` nigde direktno ne koristi u telu funkcija?

Ovo osigurava da su svi ORM modeli registrovani pri pokretanju aplikacije. Bez ovog importa, `Base` možda ne bi znao za sve modele, što bi moglo dovesti do toga da tabele ne budu kreirane. Zato je važno da se import `models` izvrši čak i ako se direktno ne koristi u kodu.

3. Zašto je `get_db()` premešten iz `main.py` u `db/session.py`?

Zato što želimo da logika za dobijanje sesije baze bude centralizovana i ponovo upotrebljiva. Na taj način `main.py` ostaje tanak i fokusiran samo na orkestraciju aplikacije, dok detalji o sesiji baze ostaju u `db/session.py`. Ovo takođe olakšava testiranje i održavanje koda.

4. Zašto `main.py` više ne uvozi `SessionLocal`, ali i dalje uvozi `engine`?

Zato što `SessionLocal` više nije potreban u `main.py` jer se sesija baze sada dobija preko `db_dependency`. `engine` je i dalje potreban za kreiranje tabela (`Base.metadata.create_all(bind=engine)`) i eventualno za druge operacije koje zahtevaju direktan pristup engine-u.

5. Šta bi se pokvarilo kada bi neki budući router fajl pokušao da uveze `db_dependency` direktno iz `main.py`?

Ako bi neki budući router fajl pokušao da uveze `db_dependency` direktno iz `main.py`, došlo bi do kružnog importa i potencijalno greške pri pokretanju aplikacije. `main.py` treba da ostane centralno mesto za orkestraciju aplikacije, dok se specifične zavisnosti, kao što je `db_dependency`, uvoze iz svojih odgovarajućih modula (`db/session.py`).

Ako na sva pitanja možeš da odgovoriš svojim rečima, ova lekcija je usvojena i možeš nastaviti na sledeću temu (routers u tvom aktivnom projektu).

---

## 8) Pitanja i odgovori

### Pitanje 1

PITANJE: Da li treba u `fast-api-course-my-work/TodoApp/main.py` da kreiram:

```python
class TodoRequest(BaseModel):
    title: str = Field(min_length=3, description="Naslov todo zadatka mora imati najmanje 3 karaktera")
    description: str = Field(min_length=3, max_length=100, description="Opis todo zadatka mora imati najmanje 3 karaktera i najviše 100 karaktera")
    priority: int = Field(gt=0, lt=6, description="Prioritet todo zadatka mora biti veći od 0 i manji od 6")
    completed: bool = Field(description="Status završenosti todo zadatka") # Nema dodatnih ograničenja zato što je boolean i može biti samo True ili False (0 ili 1)
```

ili u nekom drugom folderu?

Problem je što je u kursu drugačiji raspored foldera (working tree) tj. sve je smešteno u `scratch/fast-api-course/Project_3` a u rasporedu foldera kod mene odvojeno imam foldere `db`, `core`, `api`. Poslao sam ti moj `TodoApp` da vidiš raspored foldera u projektu.

---

### Odgovor 1

ODGOVOR: Ne treba da stavljaš `TodoRequest` direktno u `main.py`. U tvojoj strukturi najbolje je da napraviš:

```text
fast-api-course-my-work/
└── TodoApp/
    ├── main.py
    ├── models.py
    ├── schemas.py       <- ovde
    ├── db/
    ├── core/
    └── api/
```

Razlog:

- `models.py` sadrži SQLAlchemy modele i opis tabela baze.
- `schemas.py` sadrži Pydantic modele za `request/response` podatke API-ja.
- `main.py` povezuje aplikaciju i endpoint-e.

U `TodoApp/schemas.py`:

```python
from pydantic import BaseModel, Field


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool = False
```

Obrati pažnju na pravilno pisanje:

```python
Field(min_length=3, max_length=100)
```

Ne:

```python
Field(min_lenght=3, max_lenght=100)
```

U `main.py` bi kasnije koristio:

```python
from .schemas import TodoRequest
```

Na primer za `POST`:

```python
@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_request: TodoRequest,
    db: db_dependency,
):
    todo_model = Todos(**todo_request.model_dump())

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    return todo_model
```

Za sada, dok radiš samo `GET`, `TodoRequest` ti još nije potreban. Biće ti potreban u sledećem koraku kada počneš da primaš JSON body kroz `POST`i kroz `PUT` a kasnije i kroz `PATCH`.

Najvažnije pravilo:

```text
models.py  -> struktura baze
schemas.py -> struktura HTTP podataka
main.py    -> aplikacija i endpoint registracija
```

U tvom slučaju preporučujem `TodoApp/schemas.py`, jer se to najviše poklapa sa rasporedom glavnog projekta u root-u repozitorijuma.

---

### Pitanje 2

PITANJE: Da li na kraju posle `db.commit()` treba da koristim i `db.refresh(todo_model)` i u `main.py` za `POST` i `PUT` zahteve?

---

### Odgovor 2

ODGOVOR: Da, preporučuje se koristiti `db.refresh(todo_model)` nakon `db.commit()` i za `POST` i za `PUT` zahteve. Razlog je što `db.commit()` upisuje promene u bazu, ali ne osvežava instancu modela sa generisanim vrednostima iz baze (npr. automatski generisani `id`). `db.refresh(todo_model)` osigurava da instanca modela sadrži najnovije podatke iz baze.

ZAKLJUČAK: Da, u ovom `POST` endpointu je preporučljivo da posle `db.commit()` pozoveš `db.refresh(todo_model)`, naročito zato što baza tada generiše `id`. Dodaću ga odmah na pravo mesto i proveriti fajl.

Preporučljivo je:

```python
db.add(todo_model)
db.commit()
db.refresh(todo_model)

return todo_model
```

Razlika:

- `db.commit()` trajno upisuje podatke u bazu.

- `db.refresh(todo_model)` ponovo učitava objekat iz baze, uključujući automatski generisan `id`.

Bez `refresh(todo_model)` zapis može biti sačuvan, ali objekat koji vraćaš klijentu ne mora pouzdano sadržati sve vrednosti koje je baza generisala ili izmenila.

---

### Pitanje 3

PITANJE: Šta znači u anotaciji `Generator(Session, None, None)`?

---

### Odgovor 3

ODGOVOR: U Python-u, `Generator` je tip koji opisuje generator funkciju. Anotacija `Generator(Session, None, None)` znači da generator:

- `yield`-uje vrednosti tipa `Session`
- ne očekuje nikakve vrednosti koje se šalju nazad u generator (`None`)
- ne vraća nikakvu vrednost kada se završi (`None`)

U kontekstu `FastAPI`-ja i `SQLAlchemy`-ja, ovo se obično koristi za `dependency` koji pruža SQLAlchemy sesiju.

`Generator` yield-uje sesiju, a nakon što se završi, sesija se zatvara.

---

### Pitanje 4

PITANJE: Zbog čega tačno u `main.py` fajlu koji sam ti poslao `update_todo` funkcija zahteva da parametar `todo_request: TodoRequest` mora biti iznad `Path` parametra u definiciji funkcije. Da li je to zato što posle default (podrazumevanih) parametara ne možemo imati pozicioni parametar `todo_request` pa on mora ići na početak?

---

### Odgovor 4

ODGOVOR:

U tvojoj funkciji u `fast-api-course-my-work/TodoApp/main.py` fajlu:

```python
@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
```

`todo_request` nema podrazumevanu vrednost, pa mora doći pre:

```python
todo_id: int = Path(...)
```

`Path(...)` se u Python sintaksi ponaša kao podrazumevana vrednost. Zato bi ovo bilo neispravno:

```python
def update_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0),
    todo_request: TodoRequest,
):
    ...
```

Python bi prijavio:

```text
SyntaxError: non-default argument follows default argument
```

FastAPI zatim na osnovu `tipova` i `anotacija` zaključuje:

- `db: db_dependency` je dependency
- `todo_request: TodoRequest` je request body
- `todo_id: int = Path(...)` je path parameter

Redosled u URL-u određuje ruta:

```python
@app.put("/todo/{todo_id}")
```

a ne redosled parametara u funkciji.

Dakle, komentar u tvom kodu treba preciznije da glasi:

```python
# todo_request mora biti pre todo_id jer todo_id ima podrazumevanu vrednost Path(...).
# Python zahteva da parametri bez podrazumevane vrednosti budu pre parametara sa podrazumevanom vrednošću.
```

---

### Pitanje 5

PITANJE: Koji način za `delete` je bolji?

```python
db.query(Todos).filter(Todos.id == todo_id).delete()
```

ili

```python
db.delete(todo_model)
```

---

### Odgovor 5

U tvom konkretnom kodu (`fast-api-course-my-work/TodoApp/main.py`)bolji je ovaj način:

```python
db.delete(todo_model)
db.commit()
```

Zato što si već prethodno pronašao objekat:

```python
todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
```

Kompletan endpoint:

```python
@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0),
) -> None:
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo nije pronađen.")

    db.delete(todo_model)
    db.commit()
```

#### Razlika

```python
db.delete(todo_model)
```

- briše već učitan `ORM` objekat
- čitljivije je za početnika
- `SQLAlchemy` prati stanje tog objekta
- pogodnije je kada kasnije dodaš `odnose`, `validacije` ili `dodatnu logiku`

```python
db.query(Todos).filter(Todos.id == todo_id).delete()
```

- izvršava direktno SQL `DELETE` upit
- ne mora prethodno da učita objekat
- može biti efikasnije za brisanje velikog broja zapisa
- spada u `bulk` operacije i zahteva više pažnje oko sinhronizacije `ORM` sesije i povezanih objekata

U tvom trenutnom kodu druga varijanta je nepotrebno ponavljanje `query`-ja (upita `SELECT`), jer si zapis već pronašao. Zato koristi:

```python
db.delete(todo_model)
db.commit()
```

Za početak i učenje ORM načina rada, ovo je jasniji i bolji izbor.

---

### Pitanje 6

PITANJE: Da li je potreban `first()` kod `todo_model = db.query(Todos).filter(Todos.id == todo_id).first()`. Upitanju je pretraga po `id`-u a on je jedinstven zar ne? Zato mi `first()` nema logike.

ODGOVOR: `first()` je tehnički nepotreban kada pretražuješ po `id`-u jer je `id` jedinstven. Možeš koristiti `one()` ili `one_or_none()` umesto `first()`. Međutim, `first()` je često korišćen jer je jednostavan i ne baca izuzetak ako zapis ne postoji, već vraća `None`.

Tako da si delimično upravu: `id` je jedinstven, ali `first()` je ipak potreban zato što:

```python
db.query(Todos).filter(Todos.id == todo_id)
```

još uvek samo pravi SQLAlchemy `Query` objekat. Upit nije izvršen i nemaš konkretan `Todo` objekat.

`first()`:

- izvršava upit
- vraća jedan `ORM objekat` ili `None`
- dodaje ograničenje da se vrati najviše jedan rezultat

```python
todo_model = (
    db.query(Todos)
    .filter(Todos.id == todo_id)
    .first()
)
```

Zato ovaj kod ima smisla čak i kada je `id` jedinstven.

Još bolji način za pretragu po primarnom ključu je:

```python
todo_model = db.get(Todos, todo_id)
```

To direktno znači: pronađi objekat `Todos` čiji je primarni ključ `todo_id`.

Tvoj endpoint može biti:

```python
todo_model = db.get(Todos, todo_id)

if todo_model is None:
    raise HTTPException(status_code=404, detail="Todo nije pronađen.")
```

Razlike:

```python
.first()
```

Vraća objekat ili `None`.

```python
.one()
```

Očekuje tačno jedan rezultat, ali baca grešku ako rezultat ne postoji.

```python
db.get(Todos, todo_id)
```

Najjasniji je izbor kada tražiš baš po primarnom ključu.

Za tvoj slučaj preporučujem:

```python
todo_model = db.get(Todos, todo_id)
```

---
