# APIRouter (routers) u FastAPI - detaljan teorijski materijal

Ova lekcija objasnjava zasto se endpoint-i dele u vise fajlova pomocu `APIRouter`, kako se to povezuje sa glavnom aplikacijom, i koje su najcesce greske pri organizaciji rutera.

---

## 1) Problem koji routers resavaju

Na pocetku, sve endpoint-e pises direktno u `main.py`:

```python
app = FastAPI()

@app.get("/todos")
async def read_all(db: db_dependency):
    ...

@app.post("/todos")
async def create_todo(...):
    ...

@app.get("/users")
async def read_all_users(...):
    ...
```

Kad aplikacija raste, ovo postaje:

- tesko za citanje
- tesko za odrzavanje
- tesko za timski rad (svi menjaju isti fajl)

`APIRouter` resava ovo tako sto ti dozvoljava da endpoint-e podelis po domenima:

- `todos`
- `auth`
- `users`
- `admin`

---

## 2) Sta je APIRouter zapravo

`APIRouter` je "mini FastAPI aplikacija" koja moze da sadrzi svoje rute, ali se ne pokrece samostalno.

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_all():
    ...
```

Kasnije se taj `router` prikljucuje na glavnu `FastAPI` instancu.

Mentalni model:

- `FastAPI()` = ceo grad
- `APIRouter()` = jedna cetvrt sa svojim ulicama (rutama)
- `include_router()` = spajanje cetvrti sa gradom

---

## 3) Osnovni primer: main.py + router fajl

### routers/todos.py

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/todos")
async def read_all():
    return {"message": "todos endpoint"}
```

### main.py

```python
from fastapi import FastAPI
from .routers import todos

app = FastAPI()

app.include_router(todos.router)
```

Kada pokrenes aplikaciju, `GET /todos` radi identicno kao da si ga napisao direktno u `main.py`.

---

## 4) prefix i tags - zasto ih koristis

Primer iz kursa (Project 4):

```python
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.get("/todo")
async def read_all(...):
    ...
```

Efekat:

- stvarna ruta postaje `/admin/todo`, ne samo `/todo`
- `tags` grupise endpoint-e u Swagger UI (`/docs`) pod istim naslovom

Prednosti:

1. `prefix` sprecava da svaki endpoint mora rucno da pise pun put
2. `tags` cini API dokumentaciju citljivijom
3. lakse je vizuelno razdvojiti domene u `/docs`

---

## 5) include_router - kako main.py sastavlja aplikaciju

Primer iz Project 4:

```python
from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
```

Sta se ovde dogadja:

1. `main.py` uvozi module iz `routers` paketa
2. svaki modul ima svoj `router = APIRouter(...)`
3. `include_router(...)` dodaje sve rute iz tog routera u glavnu FastAPI aplikaciju

Redosled `include_router` poziva obicno nije bitan za rad rute, ali:

- utice na redosled prikaza u `/docs`
- moze biti bitan ako koristis globalne middleware/prefix konflikte

---

## 6) Zasto se get_db ponavlja u svakom router fajlu (i da li je to problem)

U Project 4 primerima, gotovo svaki router fajl ima:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
```

Ovo je funkcionalno, ali u vecim projektima cesto se centralizuje u jedan zajednicki modul (npr. `database.py` ili `db/session.py`), pa se samo importuje:

```python
from ..database import get_db

db_dependency = Annotated[Session, Depends(get_db)]
```

Prednost centralizacije:

- jedna tacka istine za DB sesiju
- lakse testiranje (mockovanje/override jedne funkcije)
- manje sanse da neki router zaboravi `finally: db.close()`

Ovo je vazna razlika izmedju "kursa koji uci korak po korak" i "produkcione arhitekture".

---

## 7) Relativni importi u routers/ fajlovima

Tipican uzorak:

```python
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user
```

Objasnjenje tacaka:

- `..models` znaci "idi jedan paket gore, pa uzmi models"
- `.auth` znaci "isti paket (routers), uzmi auth modul"

Ovo direktno zavisi od teme koju smo ranije obradili (importi i pokretanje skripti). Router fajlovi su deo paketa, pa relativni importi rade samo ako se aplikacija pokrece kao paket (`uvicorn TodoApp.main:app`).

---

## 8) Kako se povezuju auth i drugi routeri

Primer iz `admin.py` i `users.py`:

```python
from .auth import get_current_user

user_dependency = Annotated[dict, Depends(get_current_user)]
```

Ovo pokazuje da:

- routeri mogu koristiti dependency-je definisane u drugim router fajlovima
- `get_current_user` postaje deljena zavisnost za autentifikaciju kroz vise domena (todos, admin, users)

Ovo je prakticna demonstracija da dependency injection nije vezan samo za DB sesiju, vec i za autentifikaciju, autorizaciju, i druge "pripremne korake" pre endpoint logike.

---

## 9) Provera autorizacije unutar routera (rola korisnika)

Primer iz `admin.py`:

```python
@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).all()
```

Ovo pokazuje sledeci nivo posle osnovnog CRUD-a:

- `user_dependency` dobija podatke o ulogovanom korisniku
- rucna provera role (`user_role == 'admin'`) je autorizacija, ne samo autentifikacija

Razlika:

- autentifikacija = da li znamo ko si
- autorizacija = da li imas pravo da uradis ovu akciju

---

## 10) Struktura foldera za routere (preporuceni obrazac)

```text
TodoApp/
  __init__.py
  main.py
  models.py
  database.py
  routers/
    __init__.py
    auth.py
    todos.py
    users.py
    admin.py
```

Napomena za tvoj trenutni projekat (`fast-api-course-my-work/TodoApp`):

- vec postoji `api/routes/__init__.py` kao placeholder
- kad dodjes do ove teme u kursu, prirodno je da tu dodas fajlove poput `todos.py`, `users.py` po istom prefix/tags obrascu

---

## 11) Najcesce greske pri radu sa routerima

1. Zaboravljen `include_router()`

- ruta postoji u router fajlu, ali se nikad ne "prikljuci" na app, pa vraca 404.

2. Dupli prefix

- prefix definisan i u `APIRouter(prefix=...)` i ponovo rucno u putanji endpoint-a, sto pravi neocekivane URL-ove.

3. Kruzni importi izmedju router fajlova

- npr. `todos.py` importuje nesto iz `admin.py`, a `admin.py` iz `todos.py`.

4. Nedosledni relativni importi

- mesanje `.database` i `database` unutar istog paketa.

5. Ponovno pisanje get_db bez razloga u svakom fajlu

- funkcionalno radi, ali otvara vrata za nekonzistentnost.

---

## 12) Mentalna mapa toka jednog zahteva kroz router

```text
Klijent -> HTTP zahtev (npr. GET /admin/todo)
        -> FastAPI prepoznaje prefix "/admin"
        -> Pronalazi odgovarajucu rutu unutar admin.router
        -> Izvrsava dependency-je (get_db, get_current_user)
        -> Izvrsava telo endpoint funkcije
        -> Vraca JSON odgovor
        -> Zatvara DB sesiju (finally u get_db)
```

---

## 13) Samoprovera razumevanja

1. Koja je razlika izmedju `FastAPI()` i `APIRouter()`?
2. Sta tacno radi `app.include_router(router)`?
3. Cemu sluzi `prefix` u `APIRouter(prefix=...)`?
4. Zasto `tags` ne uticu na funkcionalnost rute, samo na dokumentaciju?
5. Zasto relativni importi u `routers/` fajlovima zahtevaju paketno pokretanje aplikacije?
6. Koja je razlika izmedju autentifikacije i autorizacije u kontekstu admin rute?

---

## 14) Zakljucak

`APIRouter` nije nova tehnologija, vec organizacioni alat.

Kada projekat preraste par endpoint-a:

- deljenje po domenima (`todos`, `users`, `admin`, `auth`) postaje neophodno
- `prefix` i `tags` cine API citljivijim i lakse navigabilnim kroz `/docs`
- deljeni dependency-ji (`get_db`, `get_current_user`) povezuju routere u koherentnu aplikaciju

Ovo je prirodan sledeci korak posle osnovnog CRUD-a i dependency injection obrasca.
