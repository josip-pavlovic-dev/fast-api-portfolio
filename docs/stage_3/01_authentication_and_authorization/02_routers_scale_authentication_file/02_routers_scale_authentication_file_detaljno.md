# Oblast 01 - Authentication and Authorization

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

Ne treba praviti novi `TodoApp/routers/` paket ako pratimo strukturu koju već imaš.

---

## 1) Problem koji rešavamo

U prethodnoj lekciji napravljen je poseban `auth.py` fajl. U njemu je mogla da postoji nova FastAPI aplikacija:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/user")
async def get_user():
    return {"message": "user authenticated"}
```

Međutim, ta aplikacija je odvojena od aplikacije u `main.py`.

Ako pokrenemo:

```bash
uvicorn TodoApp.main:app --reload
```

Uvicorn pokreće samo `app` iz `TodoApp/main.py`. Ruta iz `auth.py` se neće pojaviti ako nije registrovana u glavnoj aplikaciji.

Ako pokrenemo posebnu aplikaciju iz `auth.py`, dobićemo auth rutu, ali nećemo dobiti todo rute iz `main.py`.

---

### Glavni problem

Želimo istovremeno:

- jednu glavnu FastAPI aplikaciju (npr. `app` iz `main.py`)
- jedan port (npr. 8000)
- odvojene module za različite funkcionalne oblasti (npr. `auth`, `todos`)
- mogućnost da se aplikacija proširuje bez ogromnog `main.py` fajla (koristeći routere)

Rešenje je `APIRouter`.

---

## 2) Šta je router

Router je objekat koji grupiše povezane API rute.

Na primer, auth router može da sadrži:

```text
GET  /auth/user
POST /auth/register
POST /auth/login
```

Todo router može da sadrži:

```text
GET    /todo
GET    /todo/{todo_id}
POST   /todo
PUT    /todo/{todo_id}
DELETE /todo/{todo_id}
```

Router sam po sebi nije cela aplikacija. On je zbir ruta koji glavna FastAPI aplikacija treba da uključi.

Možemo ga zamisliti ovako:

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

Značenje je isto. Razlika je samo u organizaciji paketa.

| Kursni primer                     | Tvoj aktivni projekat             |
| --------------------------------- | --------------------------------- |
| `TodoApp/routers/auth.py`         | `TodoApp/api/routes/auth.py`      |
| `TodoApp/routers/todos.py`        | `TodoApp/api/routes/todos.py`     |
| `from routers import auth`        | `from .api.routes import auth`    |
| `app.include_router(auth.router)` | `app.include_router(auth.router)` |

Kod tebe `api` predstavlja API sloj, a `routes` grupiše module koji definišu `HTTP rute`.

---

## 4) Pravljenje `auth.py` router modula

U tvom projektu buduća lokacija auth skripte je:

```text
fast-api-course-my-work/TodoApp/api/routes/auth.py
```

Sadržaj može da izgleda ovako:

```python
from fastapi import APIRouter


router = APIRouter()


@router.get("/user")
async def get_user():
    return {"message": "user authenticated"}
```

Obrati pažnju na tri promene u odnosu na prethodni primer:

1. Uvozi se `APIRouter`, a ne `FastAPI`.
2. Pravi se objekat `router`, a ne nova aplikacija `app`.
3. Dekorator koristi `@router.get(...)`, a ne `@app.get(...)`.

Ovaj endpoint jos uvek ne vrši pravu autentifikaciju. On samo služi da proverimo da li router radi.

---

## 5) `APIRouter` naspram `FastAPI`

Razlika između `FastAPI` i `APIRouter` je u tome što `FastAPI` predstavlja glavnu aplikaciju, dok `APIRouter` predstavlja izdvojenu grupu ruta i nije samostalan server. On se koristi za organizaciju i modularizaciju ruta unutar glavne aplikacije. Povezuje se sa glavnom aplikacijom pomoću `app.include_router(...)`.

### `FastAPI`

```python
app = FastAPI()
```

`FastAPI()` predstavlja `glavnu aplikaciju`. Ona sadrži kompletnu konfiguraciju aplikacije i sve routere koji su u nju uključeni.

U tvom projektu glavna instanca ostaje u:

```text
TodoApp/main.py
```

---

### `APIRouter`

```python
router = APIRouter()
```

`APIRouter()` predstavlja izdvojenu grupu ruta. On `nije` samostalan server i ne pokreće se posebnim Uvicorn procesom.

U tvom projektu routeri pripadaju folderu:

```text
TodoApp/api/routes/
```

Jedna aplikacija može imati više routera:

```python
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
```

---

## 6) Uključivanje routera u `main.py`

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

Najvažniji red je:

```python
app.include_router(auth.router)
```

On govori glavnoj aplikaciji:

> Registruj sve rute koje se nalaze u objektu `auth.router`.

Posle toga `FastAPI` zna i za rute definisane u `main.py` i za rute definisane u `auth.py`.

---

## 7) Kako se ovo uklapa sa trenutnim `main.py`

Tvoj trenutni `main.py` već ima glavnu aplikaciju i todo CRUD rute:

```python
app = FastAPI(
    title="TodoApp API",
    description="API za upravljanje zadacima",
    version="1.0.0",
)
```

Trenutno todo endpointi još mogu ostati u `main.py`, jer se izdvajanje radi postepeno. Kada dođemo do praktične refaktorizacije, budući raspored može biti:

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

- napravi `FastAPI()` instancu (npr. `app = FastAPI(title="TodoApp API", description="API za upravljanje zadacima", version="1.0.0")`)
- uključi router module (npr. `auth.router`, `todos.router`, `users.router`)
- zadrži globalnu konfiguraciju aplikacije (npr. `title`, `description`, `version`)
- eventualno registruje `startup/lifespan` logiku. (`@app.on_event("startup")` i `@app.on_event("shutdown")`)

Ne treba unapred premeštati trenutne CRUD funkcije ako lekcija još samo objašnjava koncept. Praktična refaktorizacija dolazi kao poseban korak.

---

## 8) Prefix za funkcionalnu oblast

`Router` može imati zajednički prefix:

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

Konačna putanja je:

```text
GET /auth/user
```

`prefix="/auth"` dodaje `/auth` na početak svake rute u tom routeru.

`tags=["auth"]` grupiše rutu u Swagger dokumentaciji. `tags` ne menja URL.

Za buduće module može se koristiti:

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

## 9) Kako se aplikacija pokreće

Iako je `auth.py` poseban fajl, ne pokrećemo ga kao posebnu FastAPI aplikaciju.

Iz foldera:

```text
fast-api-course-my-work/
```

pokreće se glavna aplikacija:

```bash
uvicorn TodoApp.main:app --reload
```

Tok ucitavanja izgleda ovako:

```text
Uvicorn
    -> TodoApp.main:app
        -> main.py importuje api.routes.auth
            -> main.py uključuje auth.router
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

---

### `main.py`

ULOGA: Glavna FastAPI aplikacija i uključivanje routera. Ona služi kao centralno mesto gde se sve rute povezuju i gde se aplikacija pokreće. Važno je da `main.py` ostane jednostavan i da ne sadrži previše logike, već da samo povezuje različite delove aplikacije.

---

### `api/routes/`

ULOGA: Mesto gde se definišu `HTTP endpointi` grupisani po funkcionalnoj oblasti. Svaki fajl u ovom folderu predstavlja zaseban router koji se kasnije uključuje u glavnu aplikaciju (`main.py`).

HTTP endpointi grupisani po funkcionalnoj oblasti. Svaki `router` može imati svoje `dependencies`, `middlewares` i `logiku` koja je specifična za tu funkcionalnu oblast.

---

### `models.py`

ULOGA: Definisanje `SQLAlchemy modela` i `strukture tabela`. Ovaj fajl sadrži definicije klasa koje predstavljaju tabele u bazi podataka. Ostali delovi aplikacije koriste ove modele za interakciju sa bazom. Bez ovih modela, rad sa bazom bi bio znatno komplikovaniji. Osnovno pravilo je da svaki model odgovara jednoj tabeli u bazi a svaka instanca modela odgovara jednom redu u toj tabeli. Primer:

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

```python
@router.post("/user")
def create_user(db, username: str, email: str, hashed_password: str):
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
```

Ovaj primer pokazuje kako se kreira korisnik kroz FastAPI router koristeći SQLAlchemy model i DB sesiju. U stvarnoj aplikaciji, trebalo bi dodati validaciju podataka, rukovanje greškama i eventualno hashiranje lozinke pre nego što se sačuva u bazi. Ova funkcija je pojednostavljen prikaz i služi samo za ilustraciju osnovnog principa.

ZAKLJUČAK:

`models.py` definiše strukturu tabela u bazi podataka kroz SQLAlchemy modele. Ovi modeli se koriste u routerima i servisima za interakciju sa bazom, čime se olakšava rad sa podacima i održava konzistentnost između aplikacije i baze.

Instanciranje modela dovodi do kreiranja objekta koji predstavlja jedan red u odgovarajućoj tabeli u bazi podataka!

---

### `schemas.py`

ULOGA: Definisanje Pydantic request i response modela. Pydantic modeli služe za validaciju i serijalizaciju podataka koji ulaze i izlaze iz API endpointa u FastAPI aplikaciji. Oni omogućavaju da se podaci automatski proveravaju i konvertuju u odgovarajuće tipove pre nego što stignu do poslovne logike aplikacije. Ostali delovi aplikacije koriste ove modele za rad sa podacima na siguran i konzistentan način.

Imamo na primer `UserCreate` i `UserResponse` modele koji definišu kako podaci o korisniku treba da izgledaju prilikom kreiranja i vraćanja iz API-ja. Zbog njihove uloge u validaciji i serijalizaciji, ovi modeli pomažu u održavanju konzistentnosti i sigurnosti podataka kroz celu aplikaciju.

`UserCreate` se koristi prilikom kreiranja novog korisnika i definiše koja polja su obavezna za unos i stavlja se kao anotacija za parametre funkcije (npr. `def create_user(user: UserCreate)`), dok `UserResponse` model definiše koja polja će biti vraćena u odgovoru API-ja i koristi se za serijalizaciju podataka pre nego što se pošalju klijentu. Ona se kao anotacija koristi u response_model parametru u router funkciji.(`@router.post("/user", response_model=UserResponse)`)

---

### `db/database.py`

ULOGA: Definisanje SQLAlchemy `Engine`, `URL baze` i `SessionLocal` konfiguracija. Ove konfiguracije omogućavaju aplikaciji da se poveže sa bazom podataka i da kreira sesije za interakciju sa bazom. `Engine` predstavlja konekciju ka bazi, `URL baze` sadrži informacije o lokaciji i pristupu bazi, dok `SessionLocal` omogućava kreiranje sesija za izvršavanje upita i transakcija. Ove konfiguracije su ključne za pravilno funkcionisanje aplikacije i interakciju sa bazom podataka. Pravilo koje treba zapamtiti, jedna sesija odgovara jednoj transakciji (transakcija je jedinica rada sa bazom podataka. Prosto rečeno, svaka sesija treba da se koristi za jednu logičku operaciju sa bazom i zatim zatvori. Pod logičkom operacijom podrazumevamo niz upita i promena koje čine jednu celinu rada sa bazom. (npr. kreiranje korisnika može uključivati unos podataka u više tabela, ali sve to treba da se desi unutar jedne sesije i transakcije). Zato je važno pravilno upravljati životnim ciklusom sesija i osigurati da se svaka sesija zatvori nakon završetka operacije.

Prikaz jedne sesije u praksi može izgledati ovako:

```python
from db.session import SessionLocal

db = SessionLocal()
try:
    db.add(new_user)
    db.commit()
finally:
    db.close()
```

---

### `db/session.py`

ULOGA: Definisanje `get_db()` dependency-ja i tipa koji routeri koriste za DB sesiju. Ovaj dependency omogućava router funkcijama da dobiju instancu DB sesije koja se pravilno otvara i zatvara, čime se osigurava ispravno upravljanje životnim ciklusom sesija i transakcija u aplikaciji FastAPI. `get_db()` preko dependency injekcije omogućava da se svaka sesija koristi unutar jedne logičke operacije i zatim zatvori, čime se održava konzistentnost i integritet podataka u bazi.

Primer implementacije `get_db()` dependency-ja može izgledati ovako:

```python
from db.session import SessionLocal
from fastapi import Depends
from typing import Annotated

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[SessionLocal, Depends(get_db)]
```

Ovaj kod definiše `get_db()` funkciju koja se koristi kao dependency u FastAPI routerima. Funkcija kreira novu DB sesiju, yield-uje je za korišćenje u endpoint funkcijama, i zatim osigurava da se sesija zatvori nakon završetka operacije.

`db_dependency` je naziv koji koristimo za dependency u routerima (npr., `db: db_dependency` u endpoint funkcijama), a zapravo se odnosi na `get_db()` funkciju iz `db/session.py` u smislu dependency injekcije.

---

### `db/base.py`

ULOGA: Definisanje SQLAlchemy `Base` klase koju modeli nasleđuju. Ova klasa služi kao osnovna klasa za sve ORM modele u aplikaciji, omogućavajući SQLAlchemy-u da prati i mapira tabele u bazi podataka. Svi `modeli` u aplikaciji treba da nasleđuju ovu `Base` klasu kako bi SQLAlchemy mogao pravilno da upravlja njima. To omogućava centralizovano definisanje metapodataka i olakšava kreiranje i migraciju tabela u bazi podataka.

Ovde dolazimo do glavne razlike između `models.py` i `schemas.py` fajlova. `models.py` definiše strukturu podataka u `bazi` (ORM modele) i nasleđuje `Base` klasu iz `db/base.py`, dok `schemas.py` definiše `Pydantic` modele koji se koriste za validaciju i serijalizaciju podataka u `API` sloju. `schemas.py` ne zna ništa o bazi podataka i služi isključivo za rad sa podacima koji ulaze i izlaze iz API-ja. Nasleđuje `pydantic.BaseModel` klasu.

---

### `core/config.py`

ULOGA: Definisanje centralizovane konfiguracije aplikacije, uključujući settings vrednosti za tajne, okruženje i druge globalne parametre. Ovaj fajl omogućava da se konfiguracija lako menja i pristupa iz različitih delova aplikacije, bez potrebe za dupliciranjem konfiguracionih vrednosti.

Vrednosti u ovom fajlu se obično čitaju iz okruženja ili `.env` fajla, omogućavajući fleksibilnu konfiguraciju aplikacije u različitim okruženjima.

---

## 12) Primer budućeg auth routera sa dependency importom

Kada `auth` endpoint bude radio sa bazom, importi ce se prilagoditi potrebama endpointa:

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

Ovde tri tačke u relativnom importu znače:

```text
auth.py
    .. -> routes
    ... -> api
    ...db.session -> TodoApp/db/session.py
```

Ovaj primer samo pokazuje gde bi se dependency importovao. Ne predstavlja još potpun login sistem.

Kada se uvedu korisnički modeli i autentifikacija, auth router će moći da koristi:

- `db_dependency` iz `db/session.py`
- `Users` model iz odgovarajućeg model modula
- Pydantic schemas iz `schemas.py` ili kasnije izdvojenih schema modula
- settings iz `core/config.py`

---

## 13) Važna granica: router nije autentifikacija

Naziv `auth.py` i URL prefix `/auth` ne znači da je korisnik autentifikovan.

Router samo organizuje endpoint-e.

Prava autentifikacija kasnije zahteva, na primer:

1. Korisnik pošalje kredencijale
2. Aplikacija pronađe korisnika u bazi
3. Aplikacija proveri password hash-a
4. Aplikacija izda session ili token
5. Sledeći zahtev pošalje token
6. Dependency proveri token i odredi current user

Autorizacija zatim proverava tačno šta taj korisnik sme da uradi.

Dakle:

```text
APIRouter = organizacija endpointa
Authentication = provera identiteta
Authorization = provera dozvola
```

---

## 14) Kursni primer i prilagođeni primer

### Kursni primer

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

### Tvoj prilagođeni primer

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

Kod je skoro isti. Menja se putanja importa zato što je tvoj router smešten dublje u `api/routes/` paketu.

---

## 15) Samoprovera

1. Zašto `auth.py` sa `app = FastAPI()` predstavlja posebnu aplikaciju?

Zato što `auth.py` sa `app = FastAPI()` predstavlja potpuno nezavisnu FastAPI aplikaciju, odvojenu od glavne aplikacije u `main.py`. Posledica toga je da bi se pokretala kao zaseban proces, što nije cilj kada koristimo routere.

2. Koja je razlika između `FastAPI()` i `APIRouter()`?

Zato što `FastAPI()` kreira novu aplikaciju koja može da se pokreće samostalno, dok `APIRouter()` služi za organizaciju ruta unutar postojeće aplikacije. Router sam po sebi ne pokreće server, već se registruje u glavnoj aplikaciji. `APIRouter()` se registruje u glavnoj aplikaciji pomoću `app.include_router()`. Nije samostalna aplikacija.

3. Gde se u tvom projektu smešta `auth.py`?

U mom projektu, `auth.py` se nalazi u `TodoApp/api/routes/auth.py`.

4. Koji import iz `main.py` odgovara tvojoj strukturi?

Odgovarajući import iz `main.py` je:

```python
from .api.routes import auth
```

5. Šta radi `app.include_router(auth.router)`?

Registruje auth router u glavnoj aplikaciji, tako da rute definisane u `auth.py` postaju dostupne kroz glavnu aplikaciju. Ovo omogućava modularnu organizaciju koda i olakšava održavanje.

6. Zašto se auth router ne pokreće posebnim Uvicorn procesom?

Zato što `APIRouter` nije samostalna aplikacija. On je samo skup ruta koje se registruju u glavnoj aplikaciji. Samo `FastAPI()` objekat može da se pokrene posebnim Uvicorn procesom.

7. Šta menja `prefix="/auth"`?

`prefix="/auth"` dodaje prefiks svim rutama unutar auth routera. Na primer, ruta definisana kao `@router.get("/user")` će biti dostupna kao `/auth/user` u glavnoj aplikaciji.

8. Šta menja `tags=["auth"]`?

`tags=["auth"]` dodaje oznaku svim rutama unutar auth routera. Ove oznake se koriste u dokumentaciji (Swagger UI) da grupišu rute po funkcionalnim oblastima. Na primer, sve rute sa `tags=["auth"]` biće prikazane zajedno u sekciji "auth" u Swagger UI.

Gde bi se nalazila DB dependency koju koristi auth endpoint?

Odgovor: DB dependency, kao što je `get_db()`, bi se nalazila u `db/session.py` i koristila u auth endpointima kroz `Depends(get_db)`.

10. Da li `APIRouter` sam po sebi proverava username i password?

Ne, `APIRouter` sam po sebi ne proverava username i password. Provera autentifikacije se implementira unutar endpoint funkcija koristeći odgovarajuće dependency-je i sigurnosne mehanizme, kao što su JWT tokeni ili OAuth2.

11. Zašto trenutni todo CRUD može privremeno da ostane u `main.py`?

Trenutni todo CRUD može privremeno da ostane u `main.py` jer još uvek nismo izdvojili todo rute u poseban router. Ovo omogućava da aplikacija funkcioniše dok se modularizacija ne završi.

12. Koja je uloga `main.py` nakon izdvajanja routera?

Nakon izdvajanja routera, `main.py` postaje centralno mesto za kreiranje FastAPI aplikacije i registraciju svih routera. Svi specifični endpointi se nalaze u svojim odgovarajućim router fajlovima, dok `main.py` služi za povezivanje i pokretanje cele aplikacije.

---

## 16) Zaključak

Glavna poruka transkripta je:

> Jedna FastAPI aplikacija može da uključi više routera, tako da različite funkcionalne oblasti rade preko istog porta.

Za tvoj projekat to konkretno znači:

- glavna aplikacija ostaje u `TodoApp/main.py`
- auth router će biti u `TodoApp/api/routes/auth.py`
- budući todo router će biti u `TodoApp/api/routes/todos.py`
- `app.include_router(...)` povezuje router sa glavnom aplikacijom
- `db/session.py` ostaje mesto za `get_db()` dependency
- `core/config.py` je mesto za centralnu konfiguraciju
- ne pravi se novi kursni `TodoApp/routers/` paket

Ova lekcija uvodi organizaciju aplikacije. Prava autentifikacija, JWT, password hashing i autorizacija dolaze tek kada se uvedu odgovarajući korisnički `modeli`, `schemas` i `security dependency-ji`.

---

### Prakticna napomena

Za ovu teorijsku lekciju nije potrebno menjati aktivni kod. Kada budeš spreman za implementaciju, prvo ćemo dodati `auth.py` u `TodoApp/api/routes/`, zatim ga registrovati u `TodoApp/main.py`, a tek nakon toga postepeno prebacivati todo rute iz `main.py` u `todos.py`.
