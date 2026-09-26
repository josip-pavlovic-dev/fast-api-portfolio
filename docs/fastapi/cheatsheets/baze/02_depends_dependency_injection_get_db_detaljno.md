# Depends i Dependency Injection u FastAPI (detaljno)

Ovaj materijal je fokusiran na najvazniji obrazac u FastAPI radu sa bazom:

1. Depends
2. dependency injection
3. get_db sa yield
4. Session
5. Annotated

Cilj je da razumeš tačno šta FastAPI radi "iza scene" kada endpoint dobije `db` parametar.

---

## 1) Brza definicija pojmova

- `Depends`: FastAPI mehanizam kojim deklarišeš da `endpoint` zavisi od neke funkcije. Ovo je ključni deo dependency injection sistema u FastAPI-ju.

- `Dependency function`: funkcija koja priprema resurs (npr. `DB sesiju`, `current user`, `config`). Ovo je funkcija koja se izvršava pre endpoint logike i čiji rezultat se ubrizgava u endpoint parametar. Primer je `get_db` funkcija koja priprema SQLAlchemy sesiju.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- `Dependency injection`: automatsko izvršavanje dependency funkcije i ubacivanje rezultata u endpoint parametar. Ovo omogućava da `endpoint` dobije sve potrebne resurse od FastAPI-ja bez da ih ručno kreira.

- `Session`: SQLAlchemy radni kontekst za `query/add/commit`. Ovo nije globalni objekat i treba ga koristiti unutar request-a. To znači da se nova sesija kreira za svaki request i zatvara nakon što request završi. Zatvaranje se obavlja u `finally` bloku unutar dependency funkcije.

- `Annotated`: tip-safe način da kažeš "ovaj parametar je `Session` i dolazi preko `Depends(get_db)`". U praksi ovo znači da IDE i alati za statičku analizu koda mogu pravilno razumeti tip parametra, dok FastAPI i dalje koristi dependency injection mehanizam. Ne menja runtime ponašanje, već poboljšava statičku proveru tipova.

---

## 2) Najvažnija ideja

Kada napišeš endpoint ovako:

```python
@app.get("/")
async def read_all(db: Annotated[Session, Depends(get_db)]):
    return db.query(Todos).all()
```

TI ne pozivaš `get_db()` ručno.

FastAPI radi sve ovo automatski:

1. Vidi da endpoint traži dependency `Depends(get_db)`
2. Poziva `get_db()` pre endpoint logike
3. Uzima vrednost iz `yield db`
4. Ubacuje tu vrednost u parametar `db` (dependency injection).
5. Izvrši endpoint funkciju.
6. Po završetku request-a vrati se u dependency i izvrši `finally: db.close()`.

To je dependency injection.

---

## 3) get_db sa yield - zašto je standard

Tipican obrazac:

```python
from collections.abc import Generator
from sqlalchemy.orm import Session

from .db.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Zašto `yield`, a ne `return`?

- `yield` dozvoljava FastAPI-ju da "pauzira" funkciju, prosledi `db` endpoint-u, pa da se vrati nazad i uradi cleanup.
- `return` bi samo vratio objekat i zavrsio funkciju, bez pouzdanog `post-request cleanup` toka.

Praktična posledica:

- `Sesija` je otvorena samo tokom request-a sve dok ne se ne završi request
- `Sesija` se zatvara i kad endpoint baci grešku sa exception-om.

---

## 4) Session: šta jeste, a šta nije

`Session` jeste:

- ORM kontekst za rad sa podacima u bazi
- mesto gde radiš `query`, `add`, `commit`, `refresh`, `delete`

`Session` nije:

- globalni singleton za celu aplikaciju širom request-ova. To bi dovelo do problema sa konkurentnim pristupom i potencijalnim curenjem resursa. Ovako se kreira nova sesija za svaki request i zatvara nakon što request završi.

- objekat koji treba deliti kroz više request-ova kao globalni singleton. Pravilo je: svaka sesija treba da bude vezana za jedan request.

Pogrešan obrazac:

```python
# lose: globalna sesija za sve request-ove
DB = SessionLocal()
```

Ispravan obrazac:

- nova sesija po request-u kroz dependency
- zatvaranje u `finally`

---

## 5) Annotated + Depends: zašto je bolji od "golih" default parametara

### Direktno u potpisu (bez Annotated)

```python
@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    ...
```

Radi i ovo je validno.

### Sa Annotated

```python
from typing import Annotated

DbDep = Annotated[Session, Depends(get_db)]

@app.get("/")
async def read_all(db: DbDep):
    ...
```

Prednosti `Annotated` pristupa:

- Jasnije odvojena `tipizacija` od mehanizma ubrizgavanja (`dependency injection`-a)

- Manje ponavljanja u većim `router` fajlovima, posebno kada imaš više `endpoint`-a koji koriste istu zavisnost, jer možeš definisati dependency jednom i koristiti ga svuda.

- Čitljivije kad imaš više dependency-ja u endpoint-ima, jer je jasno koji tip zavisnosti se ubrizgava.

---

## 6) Šta je zapravo dependency injection u ovom kontekstu

U kursu se često kaže: "kod koji ubacujemo iza scene u endpoint je dependency injection".

To je praktično tačno, ali precizna formulacija je:

1. Ti napišeš dependency funkciju (`get_db`).
2. Ti deklarišeš zavisnost (`Depends(get_db)`).
3. FastAPI runtime automatski izvršava dependency i prosleđuje rezultat endpoint-u.

Znači:

- `Dependency injection` nije "bilo koji kod iza scene" uopšteno.

- `Dependency injection` je konkretan mehanizam razrešavanja i ubrizgavanja zavisnosti pre endpoint logike.

---

## 7) Flow request-a sa bazom (korak po korak)

Primer endpoint-a:

```python
@app.get("/todos")
async def read_all(db: Annotated[Session, Depends(get_db)]):
    return db.query(Todos).order_by(Todos.id).all()
```

Izvršavanje:

1. `HTTP GET /todos` stiže u FastAPI.
2. FastAPI vidi da treba `db` dependency.
3. Poziva `get_db()` i otvara sesiju.
4. `yield db` predaje sesiju endpoint-u.
5. Endpoint radi query.
6. FastAPI šalje JSON response. (npr. lista todos)
7. FastAPI se vraća u `get_db()` i zatvara sesiju.

---

## 8) Tri tipična anti-patterna

1. Otvaranje sesije bez zatvaranja

```python
def get_db():
    db = SessionLocal()
    return db
```

Problem: resource leak. Rešenje je koristiti `yield` i `finally` za zatvaranje sesije.

2. Mešanje `auth` i `ownership` bez jasne granice o odgovornosti.

```python
# nije auth samo zato što postoji user_id u URL-u
@app.get("/todos/{user_id}")
```

`auth` se odnosi na autorizaciju (proveru da li korisnik ima pravo da pristupi resursu). Ona se razlikuje od `ownership`-a, koji proverava da li korisnik zaista poseduje resurs koji pokušava da modifikuje.

Problem: Korisnik može menjati `user_id` u URL-u za pristup tuđim resursima. Ovo je moguće zbog nedostatka jasne separacije između `auth` i `ownership` logike. Zato je važno pravilno koristiti dependency injection za `auth` i `ownership` logiku.

3. Kopiranje `SessionLocal()` poziva po svakom `endpoint`-u

```python
def read_all():
    db = SessionLocal()
    try:
        return db.query(Todos).all()
    finally:
        db.close()

def read_one(todo_id: int):
    db = SessionLocal()
    try:
        return db.query(Todos).filter(Todos.id == todo_id).first()
    finally:
        db.close()
```
Problem: dupliranje koda i veća šansa za grešku. Ovo se dešava kada svaki endpoint sam otvara i zatvara sesiju, umesto da se koristi centralizovana dependency funkcija.

---

## 9) Minimalni profesionalni template

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from .db.database import SessionLocal
from .models import Todos

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]

@app.get("/todos")
async def read_all(db: DbDep):
    return db.query(Todos).all()

@app.get("/todos/{todo_id}")
async def read_one(todo_id: int, db: DbDep):
    return db.query(Todos).filter(Todos.id == todo_id).first()
```
`DbDep` se čita kao "database dependency". To znači da svaki put kada se `DbDep` koristi kao tip u endpoint funkciji, FastAPI će automatski pozvati `get_db()` i proslediti otvorenu sesiju kao argument. Ovo je centralizovani način za upravljanje životnim ciklusom sesije čime se izbegava dupliranje koda i smanjuje šansa za greške čak i u većim aplikacijama sa više endpoint-a.

---

## 10) Povezivanje sa tvojim trenutnim projektima

- U referentnom kurs projektu (napredniji) dependency obrazac je već raspakovan kroz router fajlove.
- U tvom aktivnom projektu treba da ga gradiš postepeno, ali po istoj logici.
- Ključna veština nije da "radi kod", nego da tačno razumeš lifecycle: `open session -> use session -> close session`.

---

## 11) Brza samoprovera

Ako umeš da odgovoris na sledeće bez gledanja, tema je legla:

1. Ko poziva `get_db()` - ti ili FastAPI?

`get_db()` poziva FastAPI. Primer:

```python
@app.get("/todos")
async def read_all(db: DbDep):
    return db.query(Todos).all()
```
2. Kada se izvršava `db.close()`?

`db.close()` se izvršava nakon što FastAPI završi obradu request-a i izađe iz `yield` bloka u `get_db()` funkciji.

3. Zašto je `yield` pogodniji od `return` u ovom obrascu?

`yield` omogućava FastAPI-ju da preuzme kontrolu nad životnim ciklusom resursa. Kada bi se koristio `return`, FastAPI ne bi imao priliku da automatski zatvori sesiju nakon što request bude obrađen.

4. Šta tačno predstavlja `dependency injection` ovde?

`dependency injection` ovde znači da FastAPI automatski "ubrizgava" zavisnosti (u ovom slučaju `db` sesiju) u endpoint funkcije. Ti ne moraš ručno da kreiraš i zatvaraš sesiju u svakom endpoint-u; FastAPI to radi umesto tebe koristeći `Depends(get_db)`.

5. Zašto `Session` ne treba da bude globalna promenljiva?

`Session` ne treba da bude globalna promenljiva jer svaka sesija predstavlja konekciju ka bazi podataka. Ako bi bila globalna, više request-a bi delilo istu sesiju, što može dovesti do konflikata, nepredvidivog ponašanja i problema sa konkurentnošću. Korišćenjem `get_db()` i `Depends(get_db)`, svaka funkcija dobija svoju izolovanu sesiju koja se pravilno zatvara nakon upotrebe.

---

## 12) Zaključak

`Depends(get_db)` + `yield` obrazac je osnova skoro svake ozbiljne FastAPI aplikacije sa `SQLAlchemy`.

Kad ovo savladaš:

- CRUD endpoint-i postaju rutinski
- auth i ownership filteri se lakše uvode
- testiranje i refactoring su čistiji

Bez ovog obrasca, aplikacija brzo postaje nestabilna i teška za održavanje.
