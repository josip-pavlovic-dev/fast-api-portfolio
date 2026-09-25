# Oblast 03 - Authentication and Authorization

## Lekcija 07 - Kreiranje prvog korisnika

Ova lekcija uvodi prvi auth endpoint koji prima podatke novog korisnika i pravi SQLAlchemy `Users` objekat.

Tok transkripta je:

```text
GET test ruta
    -> POST ruta za kreiranje korisnika
        -> Pydantic request validacija
            -> Users SQLAlchemy model
                -> privremeni povratak modela
```

U ovoj lekciji se jos ne radi potpuno bezbedno čuvanje korisnika. Password se namerno prikazuje kao privremeni plain-text korak da bi se u sledećoj lekciji zamenio password hash-om.

---

### Pravilo za trenutnu fazu rada

Ovo je teorijski materijal. Ne menjamo još aktivne skripte u `TodoApp` projektu i ne dodajemo stvarnog korisnika u bazu.

---

## 1) Gde se budući kod smešta

U kursnom primeru auth kod se nalazi u `auth.py` fajlu. U tvom projektu njegova lokacija je:

```text
fast-api-course-my-work/TodoApp/api/routes/auth.py
```

Buduće odgovornosti su:

```text
TodoApp/api/routes/auth.py
    POST auth endpointi
    register endpoint
    login endpoint

TodoApp/models.py
    Users SQLAlchemy model

TodoApp/schemas.py
    Pydantic request i response modeli

TodoApp/db/session.py
    db_dependency

TodoApp/main.py
    uključivanje auth routera
```

Transkript privremeno definise `CreateUserRequest` direktno u `auth.py`. To je razumljivo za mali kursni primer. U tvom organizovanijem rasporedu kasnije možemo schema izdvojiti u `schemas.py`, kada budemo radili praktičnu i bezbednu implementaciju.

---

## 2) Promena metode iz GET u POST

Prethodna test ruta je mogla izgledati ovako:

```python
@router.get("/user")
async def get_user():
    return {"message": "user authenticated"}
```

Ona samo vraća poruku i ne kreira korisnika.

Za kreiranje resursa koristi se POST:

```python
@router.post("/auth")
async def create_user():
    ...
```

POST je odgovarajuci HTTP metod kada klijent šalje podatke za kreiranje novog zapisa.

U tvom rasporedu router je u:

```text
TodoApp/api/routes/auth.py
```

a glavna aplikacija ga ukljucuje iz:

```text
TodoApp/main.py
```

### Napomena o URL putanji

U kasnijoj organizaciji možemo koristiti:

```python
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
```

Tada bi lokalna ruta:

```python
@router.post("/register")
```

postala:

```text
POST /auth/register
```

Ako transkript koristi `@router.post("/auth")`, to treba citati kao njegov kursni primer. Stvarni URL zavisi od router prefix-a i lokalne putanje.

---

## 3) Pydantic request model

Endpoint treba da zna kakve podatke ocekuje od klijenta.

Transkript uvodi:

```python
from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
```

Ovaj model opisuje HTTP request body.

Primer JSON zahteva:

```json
{
  "username": "ana",
  "email": "ana@example.com",
  "first_name": "Ana",
  "last_name": "Jovanovic",
  "password": "Test1234",
  "role": "user"
}
```

FastAPI koristi Pydantic model da:

- proveri da li su polja prisutna
- proveri osnovne tipove
- pretvori validan JSON u Python objekat
- prijavi gresku ako zahtev nije odgovarajuc

Ako `password` nedostaje, request nije validan prema ovom modelu.

---

## 4) Zasto request ne sadrzi `id` i `is_active`

`CreateUserRequest` nema:

```python
id: int
is_active: bool
```

To je namerno.

### `id`

ID treba da generise baza kroz primary key i autoincrement. Klijent ne treba da bira ID novog korisnika.

```text
klijent salje podatke korisnika
baza generise id
```

### `is_active`

Novi korisnik moze automatski postati aktivan:

```text
is_active = True
```

Klijent ne treba proizvoljno da kreira neaktivan ili privilegovan nalog ako aplikacija to ne dozvoljava.

### Request naspram modela

Request model predstavlja podatke koje klijent sme da posalje.

SQLAlchemy model predstavlja podatke koje baza cuva.

Zato ova dva modela ne moraju imati ista polja.

---

## 5) Polja CreateUserRequest modela

### `username`

Korisnicko ime. U bazi je buduci `Users.username` najcesce jedinstven.

### `email`

Email korisnika. U bazi moze imati `unique=True`.

### `first_name`

Ime korisnika.

### `last_name`

Prezime korisnika.

### `password`

Password koji korisnik salje pri kreiranju naloga.

U ovoj lekciji jos nije hashovan. To je namerno samo privremeni edukativni korak.

### `role`

Uloga korisnika, na primer:

```text
user
admin
```

U produkcionom sistemu ne bi trebalo dozvoliti da svaki klijent sam sebi posalje:

```json
{ "role": "admin" }
```

Transkript to koristi radi demonstracije mapiranja. Kasnije treba uvesti bezbednu politiku za dodelu role.

---

## 6) Razlika izmedju `password` i `hashed_password`

Pydantic request koristi:

```python
password: str
```

SQLAlchemy `Users` model koristi:

```python
hashed_password = Column(String)
```

Nazivi nisu isti zato sto podaci prolaze kroz transformaciju:

```text
password iz request-a
    -> password hashing
        -> hashed_password za bazu
```

Zbog toga ovaj obrazac nije dovoljan:

```python
user_model = Users(**create_user_request.model_dump())
```

`model_dump()` bi proizveo recnik sa kljucem:

```python
{
    "password": "Test1234"
}
```

A `Users` model ocekuje:

```python
{
    "hashed_password": "..."
}
```

SQLAlchemy ne moze automatski da zakljuci da `password` treba da se preseli u `hashed_password`.

---

## 7) Zasto `**model_dump()` ovde ne radi

Kod poput ovog radi kada se imena i struktura poklapaju:

```python
todo_model = Todos(**todo_request.model_dump())
```

Ako `TodoRequest` ima polja koja odgovaraju kolonama `Todos` modela, Python prosiruje recnik u named arguments.

Kod korisnika postoji razlika:

```text
request: password
model: hashed_password
```

Zato bi sledeci kod bio problem:

```python
user_model = Users(**create_user_request.model_dump())
```

Recnik sadrzi `password`, ali model nema kolonu `password`.

U ovoj lekciji koristi se eksplicitno mapiranje.

---

## 8) Eksplicitno mapiranje request-a na model

Konceptualni kod izgleda ovako:

```python
user_model = Users(
    email=create_user_request.email,
    username=create_user_request.username,
    first_name=create_user_request.first_name,
    last_name=create_user_request.last_name,
    role=create_user_request.role,
    hashed_password=create_user_request.password,
    is_active=True,
)
```

Svaka linija jasno govori gde podatak ide:

```text
request.email       -> Users.email
request.username    -> Users.username
request.first_name  -> Users.first_name
request.last_name   -> Users.last_name
request.role        -> Users.role
request.password    -> Users.hashed_password
```

Aplikacija sama postavlja:

```text
is_active = True
```

### Zasto je eksplicitno mapiranje korisno

- vidi se razlika izmedju request i database modela
- password moze da se transformise pre cuvanja
- sistem ne kopira nezeljena polja
- lakse je dodati validaciju i security pravila
- promene modela su uocljivije

---

## 9) Vazno upozorenje: plain-text password

Transkript u ovoj lekciji privremeno radi:

```python
hashed_password=create_user_request.password
```

Naziv polja je `hashed_password`, ali vrednost jos nije hash. To je edukativno namerno i bezbednosno nije prihvatljivo za stvarnu aplikaciju.

Tako nastaje losa situacija:

```text
hashed_password kolona
    sadrzi plain-text password
```

Ovaj korak sluzi samo da se prvo razume:

- request model
- SQLAlchemy model
- rucno mapiranje
- razlika u nazivima polja

U sledecoj lekciji password treba transformisati pomocu proverenog password hashing mehanizma.

Do tada treba zapamtiti:

> Nikada ne cuvaj stvarni korisnicki password u bazi, cak ni ako se kolona zove `hashed_password`.

---

## 10) Gde se nalazi endpoint u tvom projektu

Kursni konceptualni kod:

```python
# TodoApp/routers/auth.py
from fastapi import APIRouter
from pydantic import BaseModel
from models import Users

router = APIRouter()
```

Tvoj aktivni ciljni oblik:

```python
# TodoApp/api/routes/auth.py
from fastapi import APIRouter
from pydantic import BaseModel

from ...models import Users


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
```

Ako se schema za sada nalazi uz endpoint, moze izgledati ovako:

```python
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
```

U vecoj organizaciji schema moze biti izdvojena:

```text
TodoApp/schemas.py
```

pa auth router koristi:

```python
from ...schemas import CreateUserRequest
```

Za teorijsko pracenje transkripta vazno je razumeti obe stvari:

```text
kursni korak: schema uz auth endpoint
organizovaniji projekat: schema u schemas.py
```

---

## 11) Buduci endpoint primer

Ciljni teorijski primer moze izgledati ovako:

```python
@router.post("/register")
async def create_user(create_user_request: CreateUserRequest):
    user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=create_user_request.password,
        is_active=True,
    )

    return user_model
```

Ovaj endpoint za sada samo vraca napravljen Python/ORM objekat u demonstraciji. Ne treba ga tumaciti kao gotov register sistem.

Nedostaju mu:

- `db_dependency`
- provera da email vec ne postoji
- provera da username vec ne postoji
- password hashing
- `db.add(...)`
- `db.commit()`
- `db.refresh(...)`
- response schema bez password-a
- status `201 Created`
- kontrola role vrednosti

Ove stavke dolaze kroz naredne lekcije.

---

## 12) Zasto se model prvo samo vraca

Transkript na kraju vraca `create_user_model` da bi se videlo kako se podaci mapiraju.

To je demonstracioni korak:

```python
return user_model
```

Ako endpoint vrati ORM objekat bez odgovarajuce response schema, mogu se pojaviti problemi sa:

- serializacijom
- izlaganjem `hashed_password` vrednosti
- formatom odgovora
- status kodom

Zato u ozbiljnijem API-ju ne treba automatski vracati ceo `Users` model.

Bolji buduci pristup je schema koja ne sadrzi password:

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
```

`hashed_password` ne treba vracati klijentu.

---

## 13) Role kao podatak iz request-a

Transkript dozvoljava:

```python
role=create_user_request.role
```

To je jednostavno za demonstraciju, ali predstavlja bezbednosni problem ako javni register endpoint prihvata proizvoljnu role vrednost.

Napadac bi mogao poslati:

```json
{
  "username": "napadac",
  "role": "admin"
}
```

Zato se u realnijem sistemu cesto radi jedno od sledeceg:

```text
javna registracija uvek dobija role = "user"
admin role dodeljuje se posebno
samo administrator moze promeniti role
```

Teorijski kursni korak treba razumeti, ali ga ne treba nekriticki preneti u produkcioni kod.

---

## 14) Pydantic validacija i buduca poboljsanja

Osnovni request model koristi samo tipove:

```python
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
```

Kasnije se mogu dodati ogranicenja:

```python
from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3)
    email: EmailStr
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    password: str = Field(min_length=8)
    role: str = "user"
```

Ovo je modernija dopuna, a nije osnovni deo transkripta.

Za sada je vazno prvo razumeti osnovni tok:

```text
JSON -> Pydantic objekat -> Users ORM objekat
```

---

## 15) Buduci puniji tok kreiranja korisnika

Kada se kasnije dodaju baza i hashing, tok ce izgledati ovako:

```text
1. klijent salje register JSON
2. FastAPI cita CreateUserRequest
3. Pydantic validira polja
4. endpoint proverava jedinstven email i username
5. password se hash-uje
6. pravi se Users ORM objekat
7. owner-related vrednosti jos nisu potrebne za samog korisnika
8. db.add(user_model)
9. db.commit()
10. db.refresh(user_model)
11. vraca se bezbedan UserResponse
```

Konceptualni kod kasnije:

```python
hashed_password = hash_password(create_user_request.password)

user_model = Users(
    email=create_user_request.email,
    username=create_user_request.username,
    first_name=create_user_request.first_name,
    last_name=create_user_request.last_name,
    hashed_password=hashed_password,
    is_active=True,
    role="user",
)
```

Ovaj kod spaja vise lekcija. U ovoj lekciji ucimo samo prvi deo toka.

---

## 16) Status kod za kreiranje korisnika

Transkript dobija `200 OK`, ali kreiranje novog resursa se u API dizajnu cesto oznacava sa:

```text
201 Created
```

Buduci endpoint moze imati:

```python
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
```

Ovo nije glavna tema transkripta, ali je vazna moderna preporuka.

U teorijskoj fazi samo razlikujemo:

```text
200 OK       zahtev uspesan
201 Created  novi resurs kreiran
```

---

## 17) Podela izmedju fajlova u tvom TodoApp projektu

Ciljna podela za buducu implementaciju:

```text
TodoApp/models.py
    class Users(Base)
    class Todos(Base)

TodoApp/schemas.py
    CreateUserRequest
    UserResponse
    TodoRequest
    TodoResponse

TodoApp/api/routes/auth.py
    POST /auth/register
    login endpointi

TodoApp/api/routes/todos.py
    Todo CRUD
    ownership filteri

TodoApp/db/session.py
    db_dependency

TodoApp/core/config.py
    security settings

TodoApp/main.py
    include_router(auth.router)
    include_router(todos.router)
```

U pocetnom kursnom primeru `CreateUserRequest` moze biti u `auth.py`, ali tvoj projekat vec ima centralni `schemas.py`. Zato ce prakticna implementacija kasnije moci da ga smesti tamo bez promene koncepta.

---

## 18) Sta ova lekcija jos ne radi

Ova lekcija ne zavrsava registraciju korisnika.

Ne radi jos:

- cuvanje u bazu
- password hashing
- provere jedinstvenosti
- validaciju email formata
- proveru jacine password-a
- bezbedno dodeljivanje role
- response schema
- login
- JWT
- current user dependency

Takodje, u ovoj teorijskoj fazi ne menjamo:

```text
TodoApp/models.py
TodoApp/schemas.py
TodoApp/api/routes/auth.py
TodoApp/main.py
```

Samo pripremamo razumevanje za naredne korake.

---

## 19) Pitanja za proveru znanja

1. Zasto se test auth ruta menja iz GET u POST?
2. Gde se u tvom projektu nalazi buduci auth endpoint?
3. Sta radi `CreateUserRequest` Pydantic model?
4. Zasto request ne treba da prima `id` korisnika?
5. Zasto request ne mora da prima `is_active`?
6. Koja je razlika izmedju `password` i `hashed_password`?
7. Zasto `Users(**create_user_request.model_dump())` ne radi kada se nazivi ne poklapaju?
8. Zasto se koristi eksplicitno mapiranje polja?
9. Da li je vrednost u `hashed_password=create_user_request.password` zaista hashovana?
10. Zasto javni register endpoint ne bi trebalo da prihvati proizvoljnu `role` vrednost?
11. Zasto ne treba vracati ceo `Users` model klijentu?
12. Koji status kod je prikladniji za uspesno kreiranje korisnika?
13. Gde pripada `Users` SQLAlchemy model?
14. Gde bi u tvom organizovanom projektu mogao da pripada `CreateUserRequest`?
15. Koje faze nedostaju pre stvarnog cuvanja korisnika u bazi?

---

## 20) Prakticni zadaci

### Zadatak 1 - Napravi request JSON

Napisi validan JSON za kreiranje korisnika sa sledecim podacima:

```text
username: ana
email: ana@example.com
first_name: Ana
last_name: Jovanovic
password: Test1234
role: user
```

Zatim oznaci koje polje nije deo request-a:

```text
id
is_active
```

### Zadatak 2 - Mapiraj request na model

Napravi tabelu:

```text
CreateUserRequest polje | Users model polje
```

Popuni je za:

- username
- email
- first_name
- last_name
- password
- role
- is_active

Posebno oznaci transformaciju:

```text
password -> hashed_password
```

### Zadatak 3 - Pronadji gresku u `**model_dump()`

Objasni zasto bi ovaj kod bio problem:

```python
user_model = Users(**create_user_request.model_dump())
```

Napiši kako bi ga zamenio eksplicitnim mapiranjem bez hashovanja, samo kao privremeni kursni korak.

### Zadatak 4 - Prepoznaj security problem

Analiziraj:

```python
hashed_password=create_user_request.password
```

Odgovori:

- sta je problem
- zasto naziv kolone ne menja stvarnu vrednost
- u kojoj sledecoj fazi se problem resava

### Zadatak 5 - Prepoznaj privilege escalation

Analiziraj request:

```json
{
  "username": "student",
  "email": "student@example.com",
  "first_name": "Student",
  "last_name": "Test",
  "password": "Test1234",
  "role": "admin"
}
```

Objasni zasto javni register endpoint ne bi trebalo automatski da prihvati ovakav zahtev.

### Zadatak 6 - Odredi lokaciju koda

Za svaki element izaberi buduci fajl:

```text
CreateUserRequest
Users model
POST /auth/register
password hashing helper
DB dependency
include_router
```

Koristi:

```text
TodoApp/models.py
TodoApp/schemas.py
TodoApp/api/routes/auth.py
TodoApp/core/config.py ili security modul
TodoApp/db/session.py
TodoApp/main.py
```

### Zadatak 7 - Nacrtaj HTTP tok

Nacrtaj tok:

```text
POST /auth/register
    -> JSON body
    -> Pydantic validation
    -> password processing
    -> Users ORM model
    -> database commit
    -> safe response
```

Oznaci koje korake ova lekcija samo objasnjava, a koji dolaze kasnije.

### Zadatak 8 - Response bez password-a

Napisi polja koja bi trebalo da sadrzi `UserResponse`, a zatim navedi polje koje ne treba da se vrati:

```text
id
username
email
first_name
last_name
role
is_active
hashed_password
```

### Zadatak 9 - Status kodovi

Zaokruzi prikladniji status kod:

```text
uspesno kreiranje korisnika: 200 / 201
nevalidan request: 200 / 422
neautorizovan zahtev: 401 / 201
zabranjena admin akcija: 403 / 200
```

Objasni svaki izbor.

### Zadatak 10 - Teorijski plan implementacije

Napisi redosled buducih koraka, bez menjanja aktivnih fajlova:

1. definisati schema
2. definisati model
3. dodati router endpoint
4. validirati podatke
5. hash-ovati password
6. cuvati korisnika
7. vratiti bezbedan response

Dopuni plan svim koracima koje smatras potrebnim.

---

## 21) Zakljucak

Lekcija uvodi prvi oblik kreiranja korisnika kroz POST endpoint.

Glavni konceptualni tok je:

```text
CreateUserRequest
    -> rucno mapiranje
        -> Users model
```

Za tvoj projekat to znaci:

- auth endpoint ce pripadati `TodoApp/api/routes/auth.py`
- `Users` model ce pripadati `TodoApp/models.py`
- schema moze biti izdvojena u `TodoApp/schemas.py`
- DB dependency ostaje u `TodoApp/db/session.py`
- router se registruje u `TodoApp/main.py`

Najvaznije je razumeti zasto se request ne kopira slepo u ORM model:

```text
password != hashed_password
id ne dolazi iz klijenta
is_active kontrolise aplikacija
role zahteva posebnu bezbednosnu politiku
```

Transkript namerno prikazuje plain-text password samo kao privremeni korak. Pre stvarnog cuvanja korisnika u bazi mora se uvesti provereni password hashing, a pre vracanja odgovora mora se spreciti izlaganje password podataka.

Aktivne skripte ostaju nepromenjene dok se ne zavrsi teorija cele oblasti.
