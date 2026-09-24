# Oblast 01 - Authentication and Authorization

## Lekcija 03 - Izdvajanje Todo ruta u router

Prethodna lekcija je pokazala kako se auth rute izdvajaju u poseban router. Ova lekcija pravi sledeći korak: postojeće todo endpoint-e premešta iz `main.py` u poseban `todos.py` router modul.

Kurs koristi folder `routers/`, dok tvoj aktivni projekat koristi:

```text
fast-api-course-my-work/
    TodoApp/
        main.py
        models.py
        schemas.py
        api/
            __init__.py
            routes/
                __init__.py
        core/
        db/
```

Zato ce kursni `routers/todos.py` kod tebe biti smešten u:

```text
fast-api-course-my-work/TodoApp/api/routes/todos.py
```

Cilj nije da se napravi druga FastAPI aplikacija. Cilj je da jedna glavna aplikacija uključi više routera:

```text
TodoApp/main.py
    +-- api/routes/auth.py
    +-- api/routes/todos.py
```

---

## 1) Šta je stanje pre ove refaktorizacije

Trenutno se u tvom projektu glavna aplikacija i Todo CRUD nalaze u istom fajlu:

```text
TodoApp/main.py
```

U njemu se nalaze:

- `app = FastAPI(...)`
- kreiranje tabela pomocu `Base.metadata.create_all(...)`
- GET svih todo zapisa
- GET jednog todo zapisa
- POST novog todo zapisa
- PUT izmena todo zapisa
- DELETE todo zapisa
- importi modela, schema, engine-a i DB dependency-ja

Ovakav raspored je prihvatljiv dok ucis osnovni CRUD. Kada se dodaju auth, users i admin rute, `main.py` postaje previse veliki.

Ova lekcija uvodi sledeću podelu:

```text
main.py
    konfiguriše glavnu FastAPI aplikaciju

auth.py
    sadrži auth endpoint-e

todos.py
    sadrži todo endpoint-e
```

---

## 2) Kursni raspored i tvoj aktivni raspored

Kursni primer koristi:

```text
TodoApp/
    main.py
    routers/
        auth.py
        todos.py
```

Tvoj aktivni projekat koristi:

```text
TodoApp/
    main.py
    api/
        routes/
            __init__.py
            auth.py
            todos.py
```

Ovo su ekvivalentne lokacije:

| Kursni fajl                 | Tvoj fajl                       |
| --------------------------- | ------------------------------- |
| `TodoApp/routers/auth.py`   | `TodoApp/api/routes/auth.py`    |
| `TodoApp/routers/todos.py`  | `TodoApp/api/routes/todos.py`   |
| `from routers import auth`  | `from .api.routes import auth`  |
| `from routers import todos` | `from .api.routes import todos` |

Kod se ne menja zbog funkcionalnosti, vec zbog dubine paketa i nacina importa.

---

## 3) Zasto je vazno iz kog foldera radimo

Transkript skrece paznju na organizaciju projekta u razvojnom alatu. U kursnom primeru nadfolder moze izgledati ovako:

```text
fast-api-course/
    .venv/
    TodoApp/
        main.py
        routers/
```

Ako se razvojno okruzenje otvori na `fast-api-course/`, a Python paket se nalazi u podfolderu `TodoApp/`, relativni importi i pokretanje mogu biti zbunjujuci za pocetnika.

Tvoj projekat je organizovan ovako:

```text
fast-api-portfolio/
    fast-api-course-my-work/
        TodoApp/
            main.py
```

Preporucena radna lokacija za pokretanje aktivne aplikacije je:

```text
fast-api-course-my-work/
```

Tada se aplikacija pokrece komandom:

```bash
uvicorn TodoApp.main:app --reload
```

Objasnjenje komande:

```text
TodoApp.main
    paket TodoApp, modul main.py

:app
    promenljiva app u main.py

--reload
    razvojni server se ponovo ucitava nakon izmene koda
```

Ako se otvori sam `TodoApp` kao projekat u IDE-u, relativni importi unutar paketa mogu biti pregledniji, ali se komanda za pokretanje mora uskladiti sa radnim direktorijumom. Najvaznije je da se ne mesaju nasumicno:

- trenutni working directory
- Python import path
- putanja do Uvicorn aplikacije

---

## 4) Pravljenje `todos.py` router modula

U tvom aktivnom rasporedu novi fajl treba da bude:

```text
fast-api-course-my-work/TodoApp/api/routes/todos.py
```

Najmanja pocetna struktura je:

```python
from fastapi import APIRouter


router = APIRouter()
```

Za razliku od `main.py`, ovaj fajl ne pravi novu aplikaciju:

```python
# Ne radimo ovo u todos.py:
app = FastAPI()
```

Umesto toga koristi se:

```python
router = APIRouter()
```

Sve todo dekoratore kasnije menjamo iz:

```python
@app.get("/")
```

u:

```python
@router.get("/")
```

Router preuzima ulogu objekta na koji se registruju endpointi, ali sama glavna aplikacija ostaje u `main.py`.

---

## 5) Koje importе treba prebaciti u `todos.py`

Kada se Todo endpointi izdvoje iz `main.py`, `todos.py` mora da dobije samo importе koji su potrebni tim endpointima.

Za trenutni projekat to su:

```python
from fastapi import APIRouter, HTTPException, Path, status

from ...db.session import db_dependency
from ...models import Todos
from ...schemas import TodoRequest
```

Kompletan pocetni modul moze izgledati ovako:

```python
from fastapi import APIRouter, HTTPException, Path, status

from ...db.session import db_dependency
from ...models import Todos
from ...schemas import TodoRequest


router = APIRouter(
    prefix="/todo",
    tags=["todo"],
)
```

### Zasto tri tacke u importu

Fajl se nalazi ovde:

```text
TodoApp/api/routes/todos.py
```

Relativni import:

```python
from ...models import Todos
```

znaci:

```text
... -> iz routes nazad kroz api do TodoApp
models -> TodoApp/models.py
```

Slicno:

```python
from ...db.session import db_dependency
```

ucitava:

```text
TodoApp/db/session.py
```

Ovo je razlog zbog kog je korisno da se `TodoApp` tretira kao Python paket i da se aplikacija pokrece kao `TodoApp.main:app`.

---

## 6) Premestanje GET svih todo zapisa

Trenutna ruta u `main.py` je slicna ovoj:

```python
@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()
```

Kada se nalazi u `todos.py`, dekorator treba da koristi router:

```python
@router.get("")
async def read_all(db: db_dependency):
    return db.query(Todos).all()
```

Ako je router definisan sa:

```python
router = APIRouter(
    prefix="/todo",
    tags=["todo"],
)
```

konacna putanja postaje:

```text
GET /todo
```

Ako ne koristimo prefix, mozemo ostaviti originalne putanje:

```python
router = APIRouter()


@router.get("/")
async def read_all(db: db_dependency):
    ...
```

Tada je konacna putanja:

```text
GET /
```

### Vazna odluka o putanjama

Kurs uglavnom zadrzava postojece putanje i samo menja `app` u `router`. U prakticnoj refaktorizaciji ne treba istovremeno menjati i organizaciju fajlova i javne URL putanje bez jasnog razloga.

Za pocetak je sigurnije zadrzati postojece URL-ove, a router koristiti bez novog prefixa:

```python
router = APIRouter(tags=["todo"])
```

Tako se organizacija koda menja, ali API ugovor ostaje isti.

---

## 7) Premestanje GET rute po ID-u

Originalni endpoint koristi `Path` i DB dependency:

```python
@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0),
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is not None:
        return todo_model

    raise HTTPException(status_code=404, detail="Todo nije pronađen.")
```

U router modulu menja se samo dekorator:

```python
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0),
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is not None:
        return todo_model

    raise HTTPException(status_code=404, detail="Todo nije pronađen.")
```

Logika baze ostaje ista. Premestanje u router ne menja nacin na koji se pretrazuje tabela.

Ako se koristi `prefix="/todo"`, onda se putanja moze skraceno napisati ovako:

```python
@router.get("/{todo_id}")
```

Konacna putanja je i dalje:

```text
GET /todo/{todo_id}
```

Ali se prefix i lokalna putanja sabiraju:

```text
prefix `/todo` + route `/{todo_id}` = `/todo/{todo_id}`
```

---

## 8) Premestanje POST, PUT i DELETE ruta

Isti princip vazi za sve ostale endpoint-e.

### POST

```python
@router.post("/todo", status_code=status.HTTP_201_CREATED)
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

### PUT

```python
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
) -> None:
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo nije pronađen.")

    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)

    db.add(todo_model)
    db.commit()
```

### DELETE

```python
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0),
) -> None:
    todo_model = db.get(Todos, todo_id)

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo nije pronađen.")

    db.delete(todo_model)
    db.commit()
```

Ovde se ne menja CRUD logika. Menja se samo objekat koji registruje rutu:

```python
@app.get(...)       # ranije u main.py
@router.get(...)    # sada u todos.py
```

---

## 9) Kako izgleda kompletan `todos.py`

Za ocuvanje postojecih URL putanja, router moze izgledati ovako:

```python
from fastapi import APIRouter, HTTPException, Path, status

from ...db.session import db_dependency
from ...models import Todos
from ...schemas import TodoRequest


router = APIRouter(tags=["todo"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0),
):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo nije pronađen.")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo_request: TodoRequest,
    db: db_dependency,
):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
) -> None:
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo nije pronađen.")

    for key, value in todo_request.model_dump().items():
        setattr(todo_model, key, value)

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0),
) -> None:
    todo_model = db.get(Todos, todo_id)

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo nije pronađen.")

    db.delete(todo_model)
    db.commit()
```

Ovaj primer prati logiku koju vec imas, ali u stvarnom refaktorisanjу treba pazljivo sacuvati sve postojece komentare, validacije i formatiranje koje zelis da zadrzis.

---

## 10) Ciscenje `main.py`

Kada se svi todo endpointi premeste u `todos.py`, `main.py` vise ne treba da sadrzi njihove funkcije niti njihove direktne CRUD importe.

Tada se u `main.py` zadrzava slicna struktura:

```python
from fastapi import FastAPI

from . import models  # registruje SQLAlchemy modele za metadata
from .api.routes import auth, todos
from .db.base import Base
from .db.database import engine


app = FastAPI(
    title="TodoApp API",
    description="API za upravljanje zadacima",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
```

### Sta je uklonjeno iz `main.py`

Posle refaktorizacije se iz glavnog fajla uklanjaju importi koji vise nisu potrebni za endpoint funkcije:

```python
from fastapi import HTTPException, Path, status
from .db.session import db_dependency
from .models import Todos
from .schemas import TodoRequest
```

Oni sada pripadaju `todos.py`.

### Sta ostaje u `main.py`

- `FastAPI` import
- import routera
- `Base` i `engine` za trenutni nacin kreiranja tabela
- glavna `app` instanca
- `Base.metadata.create_all(bind=engine)`
- `app.include_router(...)` pozivi

Ovim `main.py` postaje composition root: mesto gde se svi delovi aplikacije sastavljaju u jednu aplikaciju.

---

## 11) Registracija auth i todos routera

Ako postoje oba modula:

```text
TodoApp/api/routes/auth.py
TodoApp/api/routes/todos.py
```

u `main.py` se mogu importovati zajedno:

```python
from .api.routes import auth, todos
```

A zatim registrovati:

```python
app.include_router(auth.router)
app.include_router(todos.router)
```

Redosled registracije je vazan samo kada se rute preklapaju ili kada postoje posebna pravila za redosled obrade. U ovom jednostavnom primeru auth i todo rute imaju razlicite putanje, pa je redosled lako citljiv.

Rezultat je jedna aplikacija:

```text
jedan Uvicorn proces
    jedna FastAPI app instanca
        auth router
        todos router
```

---

## 12) Provera da refaktorizacija nije promenila API

Posle prebacivanja endpointa treba proveriti da li su URL putanje ostale iste.

Pre refaktorizacije, na primer:

```text
GET    /
GET    /todo/{todo_id}
POST   /todo
PUT    /todo/{todo_id}
DELETE /todo/{todo_id}
```

Posle refaktorizacije moraju ostati iste ako nismo namerno uvodili prefix.

Provera se moze izvrsiti preko:

- Swagger UI na `/docs`
- GET zahteva za sve todos
- GET zahteva za postojeci i nepostojeci ID
- POST zahteva sa validnim telom
- PUT zahteva
- DELETE zahteva

Najcesca greska je da se prefix doda, a da se stara putanja ne prilagodi:

```python
router = APIRouter(prefix="/todo")

@router.get("/todo/{todo_id}")
```

Ovo pravi:

```text
/todo/todo/{todo_id}
```

Ispravna kombinacija je ili:

```python
router = APIRouter(prefix="/todo")

@router.get("/{todo_id}")
```

ili:

```python
router = APIRouter()

@router.get("/todo/{todo_id}")
```

Ne treba koristiti obe putanje odjednom.

---

## 13) Vazna granica: teorija naspram trenutne implementacije

Transkript pokazuje kompletno prebacivanje endpointa iz `main.py` u `todos.py`. Tvoj aktivni projekat trenutno jos nije refaktorisan na taj nacin.

Zato ovaj dokument objasnjava ciljnu strukturu, ali ne podrazumeva da je treba odmah primeniti bez posebnog zahteva.

Do prakticne implementacije:

```text
TodoApp/main.py
    trenutno sadrzi Todo CRUD

TodoApp/api/routes/
    trenutno je pripremljen paket za buduce router module
```

Kada budes radio implementaciju, sigurni redosled je:

1. napravi `api/routes/todos.py`
2. prebaci potrebne importe
3. promeni `@app` u `@router`
4. proveri da nema duplih ruta u `main.py`
5. importuj `todos` u `main.py`
6. dodaj `app.include_router(todos.router)`
7. pokreni aplikaciju
8. proveri `/docs` i CRUD ponasanje

---

## 14) Najcesce greske

### 1. Nova `FastAPI()` instanca u `todos.py`

Pogresno:

```python
app = FastAPI()
```

Time se pravi nova aplikacija umesto router modula.

Ispravno:

```python
router = APIRouter()
```

### 2. Zaboravljen `include_router`

Ako `main.py` ne sadrzi:

```python
app.include_router(todos.router)
```

todo rute nisu registrovane u glavnoj aplikaciji.

### 3. Pogresan relativni import

Za `TodoApp/api/routes/todos.py` import modela je:

```python
from ...models import Todos
```

a ne kursni import koji pretpostavlja drugu strukturu.

### 4. Dupliranje endpointa

Ako se funkcija ostavi u `main.py`, a ista funkcija se doda u `todos.py`, aplikacija moze imati duple ili zbunjujuce rute.

### 5. Promenjen URL bez namere

Dodavanje prefixa menja javni API. Prefix treba uvesti svesno i proveriti sve klijente i testove.

### 6. Pokretanje pogresnog modula

Za trenutni raspored ne pokrece se `todos.py`. Pokrece se glavna aplikacija:

```bash
uvicorn TodoApp.main:app --reload
```

---

## 15) Pitanja za proveru znanja

1. Zasto se Todo endpointi izdvajaju iz `main.py`?
2. Gde se u tvom projektu nalazi buduci `todos.py`?
3. Koja je razlika izmedju `app = FastAPI()` i `router = APIRouter()`?
4. Zasto se u `todos.py` dekoratori menjaju iz `@app.get` u `@router.get`?
5. Koji import koristi `todos.py` za `db_dependency`?
6. Sta znace tri tacke u `from ...models import Todos`?
7. Koji red u `main.py` ukljucuje Todo router?
8. Zasto `main.py` i dalje mora da zadrzi `app = FastAPI()`?
9. Sta se desava ako zaboravimo `app.include_router(todos.router)`?
10. Zasto nije dobro istovremeno koristiti `prefix="/todo"` i rutu `"/todo/{todo_id}"`?
11. Koja je preporucena Uvicorn komanda za tvoj aktivni raspored?
12. Koji delovi Todo CRUD logike ostaju isti nakon prebacivanja u router?
13. Zasto ne treba pokretati `todos.py` kao posebnu FastAPI aplikaciju?
14. Koja je uloga `main.py` nakon izdvajanja routera?

---

## 16) Prakticni zadaci

### Zadatak 1 - Prepoznaj odgovornosti

Napravi tabelu sa tri kolone:

```text
Kod ili odgovornost | Trenutna lokacija | Ciljna lokacija
```

Popuni je za sledece elemente:

- `FastAPI()` aplikacija
- `db_dependency`
- `Todos` SQLAlchemy model
- `TodoRequest` schema
- GET svih todo zapisa
- DELETE todo zapisa
- `engine`

Cilj zadatka je da razlikujes aplikaciju, router, model, schema i DB dependency.

### Zadatak 2 - Nacrtaj plan prebacivanja

Bez menjanja koda napisi redosled od najmanje sedam koraka kojim bi prebacio Todo CRUD iz `TodoApp/main.py` u `TodoApp/api/routes/todos.py`.

Za svaki korak navedi sta proveravas pre nego sto nastavis.

### Zadatak 3 - Napravi minimalni router

U razvojnoj kopiji projekta napravi:

```text
TodoApp/api/routes/todos.py
```

Dodaj `APIRouter` i jednu testnu rutu:

```python
@router.get("/router-check")
async def router_check():
    return {"message": "todos router works"}
```

Registruj router u `main.py` i proveri rutu preko Swagger UI.

Ne prebacuj jos CRUD endpoint-e ako zelis da prvo vezbas samo registraciju routera.

### Zadatak 4 - Prebaci samo GET svih todos

Prebaci samo endpoint za citanje svih todo zapisa u `todos.py`.

Obavezno proveri:

- import `db_dependency`
- import `Todos`
- `@router` dekorator
- registraciju routera u `main.py`
- da se endpoint pojavljuje u `/docs`
- da stara ruta vise nije duplirana u `main.py`

### Zadatak 5 - Prebaci ceo CRUD

Kada Zadatak 4 radi, prebaci i:

- GET po ID-u
- POST
- PUT
- DELETE

Pokreni aplikaciju komandom:

```bash
uvicorn TodoApp.main:app --reload
```

Zatim rucno proveri sve operacije kroz Swagger UI.

### Zadatak 6 - Eksperiment sa prefixom

Privremeno koristi:

```python
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)
```

Prilagodi lokalne putanje tako da konacne URL putanje budu:

```text
GET    /todos
GET    /todos/{todo_id}
POST   /todos
PUT    /todos/{todo_id}
DELETE /todos/{todo_id}
```

Zabelezi razliku izmedju lokalne putanje u routeru i konacne URL putanje u aplikaciji.

### Zadatak 7 - Dijagnostikuj gresku importa

Namerno uporedi ova dva importa u `TodoApp/api/routes/todos.py`:

```python
from ...models import Todos
```

```python
from .models import Todos
```

Objasni zasto drugi import ne odgovara rasporedu foldera. Posle eksperimenta ostavi ispravan import.

### Zadatak 8 - Provera da API ugovor nije promenjen

Pre i posle refaktorizacije zapisi listu URL putanja Todo API-ja. Uporedi ih i potvrdi da su ostale iste ako nisi uvodio prefix.

Dodatno proveri:

- status za nepostojeci ID
- validaciju `todo_id > 0`
- POST status `201`
- PUT i DELETE status `204`

---

## 17) Zakljucak

Ova lekcija zavrsava osnovno izdvajanje API modula:

- `auth.py` i `todos.py` su odvojeni router moduli
- `main.py` ostaje glavna FastAPI aplikacija
- `app.include_router(...)` povezuje routere sa aplikacijom
- `TodoApp/api/routes/` je aktivna lokacija u tvom projektu
- DB dependency ostaje u `TodoApp/db/session.py`
- modeli i schemas ostaju u svojim modulima
- svi endpointi i dalje rade preko jednog Uvicorn servera i jednog porta

Najvaznija prakticna poruka je:

> Kada izdvojis endpoint u router, menjas mesto i objekat registracije rute, ali ne moras menjati samu CRUD logiku.

Prava autentifikacija i autorizacija sada imaju cist prostor za razvoj, jer todo i auth funkcionalnosti vise ne moraju da rastu u istom `main.py` fajlu.
