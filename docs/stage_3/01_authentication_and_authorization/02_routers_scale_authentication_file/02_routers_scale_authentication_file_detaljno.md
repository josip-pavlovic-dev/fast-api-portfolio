# Oblast 03 - Authentication and Authorization

## Lekcija 02 - Skaliranje aplikacije pomocu routera

Ova lekcija pokazuje kako da se rute izdvoje iz `main.py`, a da i dalje pripadaju istoj FastAPI aplikaciji i rade na istom portu.

Transkript koristi naziv paketa `routers/`. Tvoj aktivni projekat koristi organizovaniji raspored:

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

Zato se u ovoj teoriji kursni `routers/` prevodi na:

```text
TodoApp/api/routes/
```

Ne treba praviti novi `TodoApp/routers/` paket ako pratimo strukturu koju vec imas.

---

## 1) Problem koji resavamo

U prethodnoj lekciji napravljen je poseban `auth.py` fajl. U njemu je mogla da postoji nova FastAPI aplikacija:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/user")
async def get_user():
    return {"message": "user authenticated"}
```

Medjutim, ta aplikacija je odvojena od aplikacije u `main.py`.

Ako pokrenemo:

```bash
uvicorn TodoApp.main:app --reload
```

Uvicorn pokrece samo `app` iz `TodoApp/main.py`. Ruta iz `auth.py` se nece pojaviti ako nije registrovana u glavnoj aplikaciji.

Ako pokrenemo posebnu aplikaciju iz `auth.py`, dobicemo auth rutu, ali necemo dobiti todo rute iz `main.py`.

### Glavni problem

Zelimo istovremeno:

- jednu glavnu FastAPI aplikaciju
- jedan port
- odvojene module za razlicite funkcionalne oblasti
- mogucnost da se aplikacija prosiruje bez ogromnog `main.py` fajla

Resenje je `APIRouter`.

---

## 2) Sta je router

Router je objekat koji grupise povezane API rute.

Na primer, auth router moze da sadrzi:

```text
GET  /auth/user
POST /auth/register
POST /auth/login
```

Todo router moze da sadrzi:

```text
GET    /todo
GET    /todo/{todo_id}
POST   /todo
PUT    /todo/{todo_id}
DELETE /todo/{todo_id}
```

Router sam po sebi nije cela aplikacija. On je zbir ruta koji glavna FastAPI aplikacija treba da ukljuci.

Mozemo ga zamisliti ovako:

```text
TodoApp/main.py
    glavna FastAPI aplikacija
          |
          +-- api/routes/auth.py
          |      auth router
          |
          +-- api/routes/todos.py
                 todo router
```

---

## 3) Kursni raspored naspram tvog rasporeda

Kurs koristi ovaj oblik:

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

Znacenje je isto. Razlika je samo u organizaciji paketa.

| Kursni primer                     | Tvoj aktivni projekat             |
| --------------------------------- | --------------------------------- |
| `TodoApp/routers/auth.py`         | `TodoApp/api/routes/auth.py`      |
| `TodoApp/routers/todos.py`        | `TodoApp/api/routes/todos.py`     |
| `from routers import auth`        | `from .api.routes import auth`    |
| `app.include_router(auth.router)` | `app.include_router(auth.router)` |

Kod tebe `api` predstavlja API sloj, a `routes` grupise module koji definisu HTTP rute.

---

## 4) Pravljenje `auth.py` router modula

U tvom projektu buduca lokacija auth skripte je:

```text
fast-api-course-my-work/TodoApp/api/routes/auth.py
```

Sadrzaj moze da izgleda ovako:

```python
from fastapi import APIRouter


router = APIRouter()


@router.get("/user")
async def get_user():
    return {"message": "user authenticated"}
```

Obrati paznju na tri promene u odnosu na prethodni primer:

1. Uvozi se `APIRouter`, a ne `FastAPI`.
2. Pravi se objekat `router`, a ne nova aplikacija `app`.
3. Dekorator koristi `@router.get(...)`, a ne `@app.get(...)`.

Ovaj endpoint jos uvek ne vrsi pravu autentifikaciju. On samo sluzi da proverimo da li router radi.

---

## 5) `APIRouter` naspram `FastAPI`

### `FastAPI`

```python
app = FastAPI()
```

`FastAPI()` predstavlja glavnu aplikaciju. Ona sadrzi kompletnu konfiguraciju aplikacije i sve routere koji su u nju ukljuceni.

U tvom projektu glavna instanca ostaje u:

```text
TodoApp/main.py
```

### `APIRouter`

```python
router = APIRouter()
```

`APIRouter()` predstavlja izdvojenu grupu ruta. On nije samostalan server i ne pokrece se posebnim Uvicorn procesom.

U tvom projektu routeri pripadaju folderu:

```text
TodoApp/api/routes/
```

Jedna aplikacija moze imati vise routera:

```python
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
```

---

## 6) Ukljucivanje routera u `main.py`

Glavna aplikacija se nalazi u:

```text
fast-api-course-my-work/TodoApp/main.py
```

U njoj se importuje modul `auth` iz tvog `api/routes` paketa:

```python
from fastapi import FastAPI

from .api.routes import auth


app = FastAPI()

app.include_router(auth.router)
```

Najvazniji red je:

```python
app.include_router(auth.router)
```

On govori glavnoj aplikaciji:

> Registruj sve rute koje se nalaze u objektu `auth.router`.

Posle toga FastAPI zna i za rute definisane u `main.py` i za rute definisane u `auth.py`.

---

## 7) Kako se ovo uklapa sa trenutnim `main.py`

Tvoj trenutni `main.py` vec ima glavnu aplikaciju i todo CRUD rute:

```python
app = FastAPI(
    title="TodoApp API",
    description="API za upravljanje zadacima",
    version="1.0.0",
)
```

Trenutno todo endpointi jos mogu ostati u `main.py`, jer se izdvajanje radi postepeno. Kada dodjemo do prakticne refaktorizacije, buduci raspored moze biti:

```text
TodoApp/
    main.py                  # sklapa aplikaciju
    models.py                # SQLAlchemy modeli
    schemas.py               # Pydantic modeli
    api/
        routes/
            auth.py          # registracija, login i auth rute
            todos.py         # todo HTTP rute
            users.py         # korisnicke rute
            admin.py         # administratorske rute
```

Tada `main.py` treba prvenstveno da:

- napravi `FastAPI()` instancu
- ukljuci router module
- zadrzi globalnu konfiguraciju aplikacije
- eventualno registruje startup/lifespan logiku

Ne treba unapred premestati trenutne CRUD funkcije ako lekcija jos samo objasnjava koncept. Prakticna refaktorizacija dolazi kao poseban korak.

---

## 8) Prefix za funkcionalnu oblast

Router moze imati zajednicki prefix:

```python
from fastapi import APIRouter


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/user")
async def get_user():
    return {"message": "user authenticated"}
```

Ako je router ukljucen ovako:

```python
app.include_router(auth.router)
```

konacna putanja je:

```text
GET /auth/user
```

`prefix="/auth"` dodaje `/auth` na pocetak svake rute u tom routeru.

`tags=["auth"]` grupise rutu u Swagger dokumentaciji. `tags` ne menja URL.

Za buduce module moze se koristiti:

```python
# api/routes/todos.py
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)
```

Tada endpoint:

```python
@router.get("")
async def read_all_todos():
    ...
```

postaje:

```text
GET /todos
```

---

## 9) Kako se aplikacija pokrece

Iako je `auth.py` poseban fajl, ne pokrecemo ga kao posebnu FastAPI aplikaciju.

Iz foldera:

```text
fast-api-course-my-work/
```

pokrece se glavna aplikacija:

```bash
uvicorn TodoApp.main:app --reload
```

Tok ucitavanja izgleda ovako:

```text
Uvicorn
    -> TodoApp.main:app
        -> main.py importuje api.routes.auth
            -> main.py ukljucuje auth.router
                -> auth ruta postaje deo glavne aplikacije
```

Zato su auth i todo endpointi dostupni preko istog servera i istog porta.

Ne treba pokretati:

```bash
uvicorn TodoApp.api.routes.auth:app --reload
```

jer `auth.py` ne treba da ima posebnu `FastAPI()` aplikaciju niti promenljivu `app`.

---

## 10) Zasto je ova struktura skalabilnija

Kada se aplikacija prosiruje, svaka funkcionalna oblast dobija svoj modul:

```text
api/routes/
    auth.py
    todos.py
    users.py
    admin.py
```

Prednosti su:

- `auth.py` sadrzi auth endpoint-e
- `todos.py` sadrzi todo endpoint-e
- `users.py` sadrzi korisnicke endpoint-e
- `admin.py` sadrzi administratorske endpoint-e
- `main.py` ostaje mesto gde se aplikacija sklapa
- sve rute rade preko jedne FastAPI aplikacije

Ovo ne znaci da svaka datoteka mora odmah imati mnogo koda. Modularnost se uvodi da bi se odgovornosti jasno odvojile kada projekat raste.

---

## 11) Gde pripadaju ostali fajlovi

Router modul nije mesto za sve vrste koda. U tvom rasporedu odgovornosti su podeljene ovako:

```text
TodoApp/
    main.py
    models.py
    schemas.py
    api/routes/
        auth.py
        todos.py
    core/
        config.py
    db/
        base.py
        database.py
        session.py
```

### `main.py`

Glavna FastAPI aplikacija i ukljucivanje routera.

### `api/routes/`

HTTP endpointi grupisani po funkcionalnoj oblasti.

### `models.py`

SQLAlchemy modeli i struktura tabela.

### `schemas.py`

Pydantic request i response modeli.

### `db/database.py`

Engine, URL baze i `SessionLocal` konfiguracija.

### `db/session.py`

`get_db()` dependency i tip koji routeri koriste za DB sesiju.

### `db/base.py`

SQLAlchemy `Base` klasa koju modeli nasledjuju.

### `core/config.py`

Centralna konfiguracija aplikacije, a kasnije i settings vrednosti za tajne i okruzenje.

Ova podela sprecava da se DB konfiguracija, HTTP rute i modeli pomesaju u jednom fajlu.

---

## 12) Primer buduceg auth routera sa dependency importom

Kada auth endpoint bude radio sa bazom, importi ce se prilagoditi potrebama endpointa:

```python
from fastapi import APIRouter

from ...db.session import db_dependency


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.get("/user")
async def get_user(db: db_dependency):
    return {"message": "user authenticated"}
```

Ovde tri tacke u relativnom importu znace:

```text
auth.py
    .. -> routes
    ... -> api
    ...db.session -> TodoApp/db/session.py
```

Ovaj primer samo pokazuje gde bi se dependency importovao. Ne predstavlja jos potpun login sistem.

Kada se uvedu korisnicki modeli i autentifikacija, auth router ce moci da koristi:

- `db_dependency` iz `db/session.py`
- `Users` model iz odgovarajuceg model modula
- Pydantic schemas iz `schemas.py` ili kasnije izdvojenih schema modula
- settings iz `core/config.py`

---

## 13) Vazna granica: router nije autentifikacija

Naziv `auth.py` i URL prefix `/auth` ne znace da je korisnik autentifikovan.

Router samo organizuje endpoint-e.

Prava autentifikacija kasnije zahteva, na primer:

1. korisnik posalje kredencijale
2. aplikacija pronadje korisnika u bazi
3. aplikacija proveri password hash
4. aplikacija izda session ili token
5. sledeci zahtev posalje token
6. dependency proveri token i odredi current user

Autorizacija zatim proverava sta taj korisnik sme da uradi.

Dakle:

```text
APIRouter = organizacija endpointa
Authentication = provera identiteta
Authorization = provera dozvola
```

---

## 14) Kursni primer i prilagodjeni primer

### Kursni oblik

```python
# TodoApp/routers/auth.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/user")
async def get_user():
    return {"message": "user authenticated"}
```

```python
# TodoApp/main.py
from routers import auth

app.include_router(auth.router)
```

### Tvoj aktivni oblik

```python
# TodoApp/api/routes/auth.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/user")
async def get_user():
    return {"message": "user authenticated"}
```

```python
# TodoApp/main.py
from .api.routes import auth

app.include_router(auth.router)
```

Kod je skoro isti. Menja se putanja importa zato sto je tvoj router smesten dublje u `api/routes/` paketu.

---

## 15) Samoprovera

1. Zasto `auth.py` sa `app = FastAPI()` predstavlja posebnu aplikaciju?
2. Koja je razlika izmedju `FastAPI()` i `APIRouter()`?
3. Gde se u tvom projektu smesta `auth.py`?
4. Koji import iz `main.py` odgovara tvojoj strukturi?
5. Sta radi `app.include_router(auth.router)`?
6. Zasto se auth router ne pokrece posebnim Uvicorn procesom?
7. Sta menja `prefix="/auth"`?
8. Sta menja `tags=["auth"]`?
9. Gde bi se nalazila DB dependency koju koristi auth endpoint?
10. Da li `APIRouter` sam po sebi proverava username i password?
11. Zasto trenutni todo CRUD moze privremeno da ostane u `main.py`?
12. Koja je uloga `main.py` nakon izdvajanja routera?

---

## 16) Zakljucak

Glavna poruka transkripta je:

> Jedna FastAPI aplikacija moze da ukljuci vise routera, tako da razlicite funkcionalne oblasti rade preko istog porta.

Za tvoj projekat to konkretno znaci:

- glavna aplikacija ostaje u `TodoApp/main.py`
- auth router ce biti u `TodoApp/api/routes/auth.py`
- buduci todo router ce biti u `TodoApp/api/routes/todos.py`
- `app.include_router(...)` povezuje router sa glavnom aplikacijom
- `db/session.py` ostaje mesto za `get_db()` dependency
- `core/config.py` je mesto za centralnu konfiguraciju
- ne pravi se novi kursni `TodoApp/routers/` paket

Ova lekcija uvodi organizaciju aplikacije. Prava autentifikacija, JWT, password hashing i autorizacija dolaze tek kada se uvedu odgovarajuci korisnicki modeli, schemas i security dependency-ji.

### Prakticna napomena

Za ovu teorijsku lekciju nije potrebno menjati aktivni kod. Kada budes spreman za implementaciju, prvo cemo dodati `auth.py` u `TodoApp/api/routes/`, zatim ga registrovati u `TodoApp/main.py`, a tek nakon toga postepeno prebacivati todo rute iz `main.py` u `todos.py`.
