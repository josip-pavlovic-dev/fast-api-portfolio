# Stage 3 Recap - Authentication and Authorization (Lekcije 01-07)

Ovaj recap obuhvata prvih 7 od ukupno 14 lekcija iz oblasti **Authentication and Authorization**.

Ovo je kontrolna tačka na polovini teorijske oblasti. Do sada je projekat presao iz jednostavnog Todo CRUD API-ja u aplikaciju koja ima osnovu za korisnike, ali authentication još nije završen.

Najvažnije je da trenutno ne pomešaš:

```text
Šta je teorijski plan
Šta je stvarno implementirano
Šta je samo pripremljeno u strukturi projekta
Šta tek treba uraditi u lekciji 08
```

Sledeća lekcija je:

```text
08 - Hash users password
```

To je važan trenutak jer trenutni `auth endpoint` još uvek čuva `plain-text password` ( u koloni `hashed_password=create_user_request.password`) u auth.py (`auth router`). Taj problem će biti rešen hashovanjem.

---

## 1) Mapa oblasti 01-07

## Lekcija 01 - Starting Authentication and Authorization

Tema: zasto Todo CRUD aplikaciji treba korisnicki identitet i kontrola pristupa.

Ishod:

- razlikuješ authentication i authorization
- razumeš da authentication odgovara na pitanje `Ko si?`
- razumeš da authorization odgovara na pitanje `Sta smes da uradis?`
- razumeš zašto svi korisnici ne smeju automatski da vide ili menjaju sve Todo zapise
- povezuješ budući `Users` model sa postojećim `Todos` modelom

Osnovna razlika:

```text
Authentication
    potvrda identiteta korisnika

Authorization
    provera dozvole korisnika
```

Primer:

```text
korisnik se uspesno prijavio
    -> authentication je uspela

korisnik pokusava da obrise tud Todo
    -> authorization moze da odbije zahtev
```

Materijal:

- [01_starting_authentication_and_authorization/01_starting_authentication_and_authorization_detaljno.md](01_starting_authentication_and_authorization/01_starting_authentication_and_authorization_detaljno.md)

## Lekcija 02 - Izdvajanje auth routera

Tema: organizovanje authentication endpointa u poseban router.

Ishod:

- razumeš ulogu `APIRouter`
- razumeš zašto auth logika ne treba da bude u `main.py`
- razumeš razliku između definisanja routera i njegovog registrovanja
- razumeš kako se API deli na funkcionalne module

Ciljna lokacija:

```text
TodoApp/api/routes/auth.py
```

Auth router je izdvojen iz centralnog fajla, a `main.py` ga registruje:

```python
from .api.routes import auth

app.include_router(auth.router)
```

Materijal:

- [02_routers_scale_authentication_file/02_routers_scale_authentication_file_detaljno.md](02_routers_scale_authentication_file/02_routers_scale_authentication_file_detaljno.md)

## Lekcija 03 - Izdvajanje Todo routera

Tema: izdvajanje Todo endpointa u `todos.py`.

Ishod:

- razumeš zašto auth i Todo funkcije treba da budu odvojene
- razumeš kako `main.py` postaje mesto za sklapanje aplikacije
- razumeš kako se router registruje preko `include_router`
- pripremaš Todo router za buduće current user i ownership provere

Ciljna lokacija:

```text
TodoApp/api/routes/todos.py
```

U `main.py` se sada registruju oba routera:

```python
app.include_router(auth.router)
app.include_router(todos.router)
```

Materijal:

- [03_router_scale_todos_file/03_router_scale_todos_file_detaljno.md](03_router_scale_todos_file/03_router_scale_todos_file_detaljno.md)

---

## Lekcija 04 - One-to-many relationship

Tema: odnos jednog user-a i više Todo zapisa.

Ishod:

- razumeš da jedan user može posedovati više Todo zapisa
- razumeš da jedan Todo pripada jednom owner-u
- razumeš zašto je potreban `owner_id`
- razumeš buduću potrebu za filtriranjem po current user-u

Koncept:

```text
jedan Users red
    -> vise Todos redova

jedan Todos red
    -> jedan owner
```

Primer:

```text
Users.id = 1
    -> Todos.owner_id = 1
    -> Todos.owner_id = 1
    -> Todos.owner_id = 1
```

Materijal:

- [04_one_to_many_relationship/04_one_to_many_relationship_detaljno.md](04_one_to_many_relationship/04_one_to_many_relationship_detaljno.md)

---

## Lekcija 05 - Foreign keys

Tema: povezivanje `Todos` i `Users` tabela kroz foreign key.

Ishod:

- razlikuješ primary key i foreign key
- razumeš sta znaci `ForeignKey("users.id")`
- razumeš da baza moze da cuva relaciju izmedju tabela
- razumeš da foreign key nije isto sto i authorization provera

Konceptualna kolona:

```python
owner_id = Column(Integer, ForeignKey("users.id"))
```

Znacenje:

```text
Todos.owner_id
    mora pokazivati na users.id
```

Vazna razlika:

```text
foreign key
    cuva vezu u bazi

authorization
    proverava da li current user sme da pristupi tom redu
```

Samo dodavanje `owner_id` ne sprecava korisnika da cita tud Todo. Za to ce kasnije biti potreban current user i query filter.

Materijal:

- [05_foreign_keys/05_foreign_keys_detaljno.md](05_foreign_keys/05_foreign_keys_detaljno.md)

## Lekcija 06 - Kreiranje Users tabele

Tema: dodavanje SQLAlchemy `Users` modela i tabele.

Ishod:

- razumeš zasto aplikacija mora da cuva korisnike
- razumeš polja potrebna za registraciju i login
- povezuješ `Users.id` sa `Todos.owner_id`
- razumeš razliku izmedju modela i Pydantic schema
- razumeš ogranicenje `Base.metadata.create_all()` kod postojecih tabela

Buduci model ima polja:

```text
id
email
username
first_name
last_name
hashed_password
is_active
role
```

Materijal:

- [06_users_table_creation/06_users_table_creation_detaljno.md](06_users_table_creation/06_users_table_creation_detaljno.md)

## Lekcija 07 - Kreiranje prvog user-a

Tema: kreiranje prvog korisnika kroz auth endpoint.

Ishod:

- razumeš `CreateUserRequest`
- razumeš pretvaranje request podataka u `Users` model
- razumeš zasto password ne treba čuvati kao plain text
- razumeš da prvi user predstavlja prelaz ka stvarnom authentication toku
- uočavaš bezbednosni problem koji se rešava u lekciji 08

Materijal:

- [07_create_first_user/07_create_first_user_detaljno.md](07_create_first_user/07_create_first_user_detaljno.md)

---

## 2) Šta se promenilo u odnosu na Stage 2

### Stage 2 stanje

Stage 2 je bio fokusiran na Todo CRUD:

```text
klijent
    -> Todo endpoint
        -> db dependency (SQLAlchemy session)
            -> Todos model
                -> todos tabela
```

Postojale su operacije:

```text
GET all todos
GET todo by id
POST todo
PUT todo
DELETE todo
```

Korisnik nije bio deo poslovnog toka. Aplikacija nije znala ko je napravio Todo i nije imala login.

---

### Stage 3 stanje posle lekcije 07

Sada se tok proširuje:

```text
klijent
    -> auth endpoint (login, register)
        -> User schema (Pydantic)
            -> Users model (SQLAlchemy)
                -> users tabela (SQLAlchemy)
```

I za Todo postoji buduća veza:

```text
Users.id
    <- Todos.owner_id
```

Ali cela authentication funkcionalnost još nije gotova. Trenutno imamo temelje, ne kompletan security sistem.

---

## 3) Realno trenutno stanje projekta

Ovo je najvažnija sekcija za razliku između plana i stvarnosti.

## 3.1 `main.py`

Trenutno `main.py`:

- kreira FastAPI aplikaciju
- importuje `models` da SQLAlchemy zna za modele
- kreira tabele preko `Base.metadata.create_all(bind=engine)`
- registruje `auth.router`
- registruje `todos.router`

Konceptualni kod:

```python
from . import models
from .api.routes import auth, todos
from .db.base import Base
from .db.database import engine

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
```

### Šta je dobro

- endpointi više nisu nagurani u `main.py`
- auth i Todo rute su odvojene
- aplikacija registruje oba routera
- struktura je pripremljena za dalje proširenje

---

### Šta još nije završeno

- nema `login endpointa`
- nema `JWT-a`
- nema `get_current_user()` dependency-ja (trenutno)
- nema `authorization` provere
- nema filtera `Todos.owner_id == current_user.id` (trenutno)
- nema `password hashing-a` (kriptovanje lozinke)

---

## 3.2 `models.py`

Trenutno postoje dva SQLAlchemy modela:

```python
class Todos(Base):
    __tablename__ = "todos"
    ...
    owner_id = Column(Integer, ForeignKey("users.id"))


class Users(Base):
    __tablename__ = "users"
    ...
```

`Users` model postoji u Python kodu i `create_all()` može da kreira tabelu ako tabela još ne postoji.

Važna napomena:

```text
Base.metadata.create_all()
    kreira tabele koje nedostaju

Base.metadata.create_all()
    ne menja pouzdano postojeću tabelu kada se model kasnije promeni
```

Za ozbiljne promene postojećih tabela kasnije će biti potrebne migracije, na primer `Alembic`. Za trenutnu edukativnu fazu važno je samo znati da dodavanje klase ne znači automatski migraciju svih starih struktura.

---

## 3.3 `schemas.py`

Trenutno postoje:

```python
class CreateTodoRequest(BaseModel):
    ...

class TodoResponse(BaseModel):
    ...

class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    is_active: bool
    role: str
```

---

### Request schema

`CreateUserRequest` opisuje šta klijent šalje:

```text
email
username
first_name
last_name
password
role
```

---

### Response schema

`UserResponse` opisuje šta klijent sme da dobije nazad:

```text
id
email
username
first_name
last_name
is_active
role
```

Namerno nema:

```text
password
hashed_password
```

Oni se nalaze samo u bazi (`models.py`) i ne smeju biti izloženi klijentu. To je važna bezbednosna mera u razvoju API-ja. Ovo je razlog zašto `UserResponse` ne sadrži polja `password` i `hashed_password` a `CreateUserRequest` ih koristi samo za unos novih korisnika.

---

## 3.4 `auth.py`

Trenutni auth router je:

```python
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
```

To znači da se lokalna ruta:

```python
@router.post("/")
```

javno poziva kao:

```text
POST /auth/
```

Swagger endpoint je grupisan pod tagom `auth`.

Trenutna funkcija konceptualno radi sledeće:

```python
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_users(
    create_user_request: CreateUserRequest,
) -> UserResponse:
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=create_user_request.password,
        is_active=True,
    )
    return create_user_model
```

### Šta endpoint trenutno radi

- prima `CreateUserRequest`
- pravi SQLAlchemy `Users` objekat
- popunjava njegova polja
- vraća `UserResponse`-kompatibilan rezultat

---

### Šta endpoint trenutno ne radi

- ne hash-uje password
- ne koristi `db_dependency`
- ne čuva user-a u bazu
- nema `db.add()`
- nema `db.commit()`
- nema `db.refresh()`
- ne proverava dupli email
- ne proverava dupli username
- ne vraća autentifikacioni token

Zato je trenutni endpoint samo prvi edukativni korak, a ne kompletna registracija korisnika.

Najveći trenutni problem je ova linija:

```python
hashed_password=create_user_request.password
```

Naziv polja govori da očekujemo `hash`, ali vrednost je još uvek originalni password.

To je upravo problem koji rešava `lekcija 08_hashing_passwords`.

---

## 3.5 `todos.py`

Todo router trenutno ima prefix:

```python
prefix="/todos"
```

i tag:

```python
tags=["todos"]
```

Javne rute su:

```text
GET    /todos/
GET    /todos/{todo_id}
POST   /todos/
PUT    /todos/{todo_id}
DELETE /todos/{todo_id}
```

Todo response koristi Pydantic konverziju:

```python
return [
    TodoResponse.model_validate(todo)
    for todo in todo_models
]
```

To znači da je odvojeno:

```text
Todos
    SQLAlchemy model

TodoResponse
    Pydantic API response
```

---

### Šta je trenutno dobro

- CRUD endpointi rade nad `Todos` modelom
- response tipovi su Pydantic schema klase
- `from_attributes=True` omogućava čitanje ORM atributa
- POST koristi `db.refresh()` pre response-a
- PUT koristi `204 No Content`
- DELETE koristi `204 No Content`
- nepostojeći Todo vraća `404`

---

### Šta jos nije dodato

- `current_user` dependency
- authentication header
- owner filter
- zaštita tuđih Todo zapisa
- automatsko popunjavanje `owner_id`

Trenutno svaki Todo CRUD endpoint može biti pozvan bez login-a, ako aplikacija radi na trenutni način.

---

## 4) Promena auth putanje

Pre dodavanja prefixa auth endpoint je bio efektivno na root putanji:

```text
POST /
```

Browser je slao:

```text
GET /
```

i dobijao:

```text
405 Method Not Allowed
```

Razlog je bio sto postoji `POST /`, ali ne i `GET /`.

Sada je router promenjen na:

```python
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
```

Zato je javna ruta sada:

```text
POST /auth/
```

Ova promena je dobra jer:

- auth endpoint više nije na root putanji
- Swagger grupiše auth endpoint pod `auth`
- buduce login i register rute mogu biti zajedno
- API struktura je jasnija

Primer buducih ruta:

```text
POST /auth/       kreiranje user-a u ovoj kursnoj fazi
POST /auth/token  budući login i token endpoint
```

---

## 5) Razlika između trenutnog i ciljnog stanja

### Trenutno stanje posle lekcije 07

```text
POST /auth/
    -> primi CreateUserRequest
        -> napravi Users ORM objekat
            -> vrati objekat
```

Password tok je trenutno nebezbedan:

```text
plain password
    -> hashed_password kolona
```

Todo tok je trenutno otvoren:

```text
GET /todos/
    -> svi todos
```

---

### Ciljno stanje posle cele oblasti

```text
POST /auth/
    -> validacija user podataka
        -> password hash
            -> db.add
                -> db.commit
                    -> UserResponse
```

Login:

```text
POST /auth/token
    -> username/password provera
        -> JWT access token
```

Protected Todo:

```text
GET /todos/
    -> Bearer token
        -> current user
            -> filter owner_id
                -> samo user-ovi todos
```

---

## 6) Zašto je lekcija 08 sledeći pravi korak

Trenutno imamo polje:

```python
hashed_password = Column(String)
```

Ali auth endpoint jos radi:

```python
hashed_password=create_user_request.password
```

To znači da se u kolonu sa imenom `hashed_password` stavlja plain-text password.

Lekcija 08 uvodi:

```python
from passlib.context import CryptContext
```

i konfiguraciju sličnu:

```python
bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)
```

Zatim se password pretvara u hash:

```python
hashed_password = bcrypt_context.hash(
    create_user_request.password
)
```

U `Users` model se onda čuva:

```python
hashed_password=hashed_password
```

A ne:

```python
hashed_password=create_user_request.password
```

### Tok posle lekcije 08

```text
password iz request-a
    -> bcrypt_context.hash(password)
        -> hash string
            -> Users.hashed_password
```

Hash nije enkripcija. Aplikacija kasnije ne čita originalni password iz baze. Pri login-u će koristiti `verify()`.

---

## 7) Šta je urađeno, sta je delimično, a šta nije urađeno

### Urađeno

- [x] Stage 2 Todo CRUD ostao je osnova projekta
- [x] auth router je izdvojen u `api/routes/auth.py`
- [x] Todo router je izdvojen u `api/routes/todos.py`
- [x] oba routera su registrovana u `main.py`
- [x] `Users` SQLAlchemy model postoji
- [x] `Todos.owner_id` foreign key postoji
- [x] `CreateUserRequest` schema postoji
- [x] `UserResponse` schema postoji
- [x] auth router ima `prefix="/auth"`
- [x] auth router ima `tags=["auth"]`
- [x] Todo router ima `prefix="/todos"`
- [x] Todo response je odvojen od SQLAlchemy modela
- [x] teoretski je objasnjena potreba za hashovanjem

### Delimično urađeno

- [ ] auth endpoint pravi `Users` ORM objekat, ali ga jos ne cuva u bazu
- [ ] Users tabela postoji u modelima, ali nema kompletan user CRUD
- [ ] `owner_id` postoji, ali se ne popunjava pri kreiranju Todo zapisa
- [ ] `UserResponse` postoji, ali nema stvarnog user database endpoint toka
- [ ] router struktura postoji, ali security helper jos nije izdvojen u `core/security.py`
- [ ] database schema moze zahtevati migraciju ako je tabela vec postojala

---

### Nije urađeno

- [ ] password hashing
- [ ] password verification
- [ ] korisnik se ne cuva trajno kroz auth endpoint
- [ ] login endpoint
- [ ] OAuth2 password bearer
- [ ] JWT encoding
- [ ] JWT decoding
- [ ] `get_current_user()`
- [ ] protected Todo endpointi
- [ ] ownership authorization
- [ ] role-based authorization

---

## 8) Plan učenja za sledeći deo

### Današnji sledeći korak - Lekcija 08

Pročitaj lekciju 08 sa fokusom na:

- šta je hashing
- razlika hashing i enkripcija
- uloga salt-a
- uloga bcrypt-a
- uloga `CryptContext`
- razlika `hash()` i `verify()`
- zašto se ne hash-uje ponovo password radi poređenja

Exit kriterijum:

- Možeš objasniti zašto plain password ne ide u bazu

`plain password` ne ide u bazu zbog bezbednosnih razloga (može biti kompromitovan ako baza bude hakovana)

- Možeš objasniti zašto dva hasha istog password-a mogu biti različita

Dva hasha istog password-a mogu biti različita zbog upotrebe `salt`-a koji se dodaje pre hash-ovanja.

`salt` predstavlja nasumičnu vrednost koja se dodaje plain password-u pre hash-ovanja kako bi se povećala bezbednost i sprečilo korišćenje rainbow tabela. Posle hash-ovanja, `salt` se obično čuva zajedno sa hash-om kako bi se mogao koristiti prilikom verifikacije password-a.

- Možeš napisati gde se poziva `bcrypt_context.hash()`

`bcrypt_context.hash()` se poziva prilikom kreiranja novog user-a pre nego što se password sačuva u bazu. Na taj način se osigurava da se u bazi čuva samo hash, a ne plain password. Ovo je ključni deo bezbednosnog mehanizma za zaštitu korisničkih lozinki.

- Možeš objasniti da se za login koristi `verify()`

`bcrypt_context.verify()` se koristi prilikom login-a da bi se proverilo da li plain password koji korisnik unese odgovara hash-ovanom password-u koji je sačuvan u bazi. Ovo omogućava autentifikaciju bez potrebe da se plain password ikada čuva u bazi.

---

## Posle lekcije 08 - Lekcija 09

Sledeći korak je hash-ovanje i čuvanje user-a u bazi:

```text
request
    -> hash
        -> Users model
            -> db.add
                -> db.commit
                    -> db.refresh
```

Exit kriterijum:

- Zašto se `user` ne čuva kao `plain text`?

- `user` se čuva u bazi kao hash-ovan password, a ne kao plain text zbog bezbednosnih razloga. U njih spadaju krađa baze podataka, neovlašćen pristup i potencijalni napadi na lozinke.

- Kada se koristi `db.add()`?

`db.add()` se koristi kada želimo da dodamo novi objekat u sesiju baze podataka. Ovaj korak samo priprema objekat za čuvanje, ali ga još uvek ne upisuje u bazu.

- Kada se koristi `db.commit()`?

`db.commit()` se koristi kada želimo da trajno sačuvamo sve promene koje su dodate u sesiju baze podataka. Ovaj korak upisuje sve pripremljene objekte u bazu.

- Kada je potreban `db.refresh()`?

`db.refresh()` se koristi kada želimo da osvežimo objekat iz baze podataka kako bismo dobili najnovije vrednosti, uključujući one koje su automatski generisane od strane baze (npr. ID). Najčešće se koristi kod metode `put`, `patch` ili nakon kreiranja novog objekta(npr. `POST /auth/`).

---

## 9) Kontrolna pitanja za lekcije 01-07

1. Koja je razlika između autentifikacije i autorizacije?

Odgovor: Autentifikacija je proces provere identiteta korisnika (npr. login), dok je autorizacija proces provere da li korisnik ima prava da pristupi određenim resursima ili izvrši određene akcije.

2. Zašto auth rute ne treba držati u `main.py`?

Odgovor: Auth rute se izdvajaju u posebne fajlove radi bolje organizacije koda, lakšeg održavanja i čitljivosti. Držanje svih ruta u `main.py` bi dovelo do pretrpanog i teže održivog fajla.

3. Šta radi `app.include_router(auth.router)`?

Odgovor: Ova linija koda uključuje ruter definisan u `auth.py` u glavnu aplikaciju, omogućavajući da sve rute iz auth rutera budu dostupne u aplikaciji.

4. Šta znači `prefix="/auth"`?

Odgovor: `prefix="/auth"` znači da će sve rute definisane u auth ruteru imati prefiks `/auth` u URL-u. Na primer, ruta `@router.post("/")` će biti dostupna kao `POST /auth/`.

5. Koja je javna putanja za `@router.post("/")` unutar auth routera?

Odgovor: Javna putanja je `POST /auth/` zbog prefiksa definisanog u `app.include_router(auth.router, prefix="/auth")`.

6. Zašto `GET /` daje 405 kada postoji samo `POST /` ili ranije `POST /auth/`?

Odgovor: HTTP status 405 znači "Method Not Allowed". Ako postoji samo `POST /auth/`, pokušaj `GET /auth/` će rezultirati 405 jer ruta ne podržava GET metodu.

7. Šta predstavlja one-to-many relacija između user-a i todos?

Odgovor: One-to-many relacija znači da jedan korisnik (`user`) može imati više zadataka (`todos`), dok svaki zadatak pripada tačno jednom korisniku.

8. Šta predstavlja `Todos.owner_id`?

Odgovor: `Todos.owner_id` predstavlja ID korisnika kojem pripada zadatak. To je kolona koja povezuje zadatak sa korisnikom u bazi podataka.

9. Na koju tabelu pokazuje `ForeignKey("users.id")`?

Odgovor: `ForeignKey("users.id")` pokazuje na kolonu `id` u tabeli `users`, uspostavljajući vezu između zadataka i korisnika.

10. Da li foreign key sam proverava da li user sme da vidi Todo?

Odgovor: Ne, foreign key samo osigurava referencijalni integritet u bazi podataka. Provera da li korisnik sme da vidi određeni zadatak mora biti implementirana u aplikaciji.

12. Koja je razlika izmedju SQLAlchemy modela i Pydantic schema klase?

Odgovor: SQLAlchemy modeli predstavljaju strukturu i logiku baze podataka, dok Pydantic schema klase služe za validaciju i serijalizaciju podataka koji ulaze i izlaze iz API-ja.

11. Koja je razlika izmedju SQLAlchemy modela i Pydantic schema klase?

Odgovor: SQLAlchemy modeli se koriste za interakciju sa bazom podataka, dok Pydantic schema klase definišu kako podaci treba da izgledaju kada se šalju ili primaju preko API-ja.

12. Zašto `UserResponse` ne sme da sadrži `hashed_password`?

Odgovor: `UserResponse` se koristi za slanje podataka o korisniku klijentu. Uključivanje `hashed_password` bi otkrilo osetljive informacije i predstavljalo bezbednosni rizik.

13. Šta trenutno radi auth endpoint?

Odgovor: Auth endpoint trenutno omogućava kreiranje novog korisnika i vraća podatke o korisniku, ali ne vrši proveru lozinke niti generisanje tokena za autentifikaciju.

14. Šta trenutno ne radi auth endpoint?

Odgovor: Auth endpoint trenutno ne vrši proveru lozinke korisnika niti generisanje tokena za autentifikaciju.

15. Zašto je `hashed_password=create_user_request.password` bezbednosni problem?

Odgovor: `hashed_password=create_user_request.password` je bezbednosni problem jer se lozinka čuva u bazi u nekriptovanom obliku, što može dovesti do kompromitovanja korisničkih naloga u slučaju curenja podataka.

16. Zašto se uvodi password hashing?

Odgovor: Password hashing se uvodi kako bi se lozinke korisnika čuvale u bezbednom, nečitljivom obliku. Čak i ako baza podataka bude kompromitovana, napadači neće moći lako da dobiju stvarne lozinke korisnika.

17. Gde se trenutno nalazi podatak o user password-u?

Odgovor: Trenutno se lozinka korisnika nalazi u `create_user_request.password` i direktno se dodeljuje `hashed_password` koloni u bazi, što znači da se čuva u nekriptovanom obliku.

18. Šta se mora desiti pre nego što user bude sačuvan u bazu?

Odgovor: Pre nego što user bude sačuvan u bazu, lozinka mora biti heširana pomoću odgovarajuće funkcije za password hashing.

19. Zašto Todo endpointi još uvek nisu protected?

Odgovor: Todo endpointi još uvek nisu protected jer autentifikacija i autorizacija korisnika još nisu implementirani. To znači da bilo koji korisnik može pristupiti i menjati tuđe zadatke bez provere identiteta i dozvola.

20. Koji je sledeći korak posle prvog user-a?

Odgovor: Sledeći korak je implementacija autentifikacije i autorizacije, što uključuje proveru lozinke korisnika prilikom prijave i generisanje tokena za autentifikaciju, kao i zaštitu Todo endpointa kako bi samo ovlašćeni korisnici mogli da pristupaju i menjaju svoje zadatke.

---

## 10) Praktični analitički zadaci

### Zadatak 1 - Nacrtaj trenutnu strukturu

Nacrtaj ili zapisi:

```text
TodoApp/
    main.py
    models.py
    schemas.py
    api/routes/auth.py
    api/routes/todos.py
    db/session.py
```

Uz svaki fajl dodaj jednu rečenicu odgovornosti.

---

### Zadatak 2 - Prati registraciju user-a

Napiši stvarni tok trenutnog endpointa:

```text
POST /auth/
    -> CreateUserRequest
        -> Users(...)
            -> return
```

Zatim oznaci gde trenutno nedostaju:

```text
hash
add
commit
refresh
```

### Zadatak 3 - Prati password

Uporedi ova dva toka:

```text
Trenutno:
password -> hashed_password kolona

Posle lekcije 08:
password -> hash(password) -> hashed_password kolona
```

Objasni zasto je drugi tok bezbedniji.

### Zadatak 4 - Razdvoji model i schema

Za svaku klasu odredi sloj:

```text
Todos
Users
CreateTodoRequest
CreateUserRequest
TodoResponse
UserResponse
```

Koristi:

```text
SQLAlchemy database model
Pydantic request schema
Pydantic response schema
```

### Zadatak 5 - Foreign key scenario

Pretpostavi:

```text
Users.id = 4
Todos.id = 10
Todos.owner_id = 4
```

Objasni:

1. kome Todo pripada
2. sta baza zna iz foreign key-a
3. sta baza jos ne zna o dozvoli pristupa
4. sta ce buduci authorization kod morati da proveri

### Zadatak 6 - API putanje

Zapisi javne putanje za:

```python
router = APIRouter(prefix="/auth", tags=["auth"])
@router.post("/")
```

I za:

```python
router = APIRouter(prefix="/todos", tags=["todos"])
@router.get("/")
```

### Zadatak 7 - Bezbedan response

Objasni zasto je ovaj response dobar:

```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    role: str
```

A ovaj los:

```python
class UserResponse(BaseModel):
    username: str
    hashed_password: str
```

### Zadatak 8 - Priprema za lekciju 08

Pre nego što nastaviš, odgovori svojim rečima:

1. Šta je plain-text password?

Odgovori svojim rečima: plain-text password je lozinka koja se čuva ili prenosi u nešifrovanom tekstualnom obliku.

2. Šta je hash?

Odgovori svojim rečima: hash je jednosmerna funkcija koja pretvara plain-text password u fiksnu niz karaktera, tako da originalni password nije lako povratiti.

3. Da li hash može da se dekriptuje?

Odgovori svojim rečima: hash ne može lako da se dekriptuje jer je jednosmerna funkcija. Salt dodatno osigurava da isti plain-text password rezultira različitim hash vrednostima.

4. Zašto salt pravi različite hash vrednosti?

Odgovori svojim rečima: salt dodaje jedinstvenu vrednost svakom plain-text password-u pre nego što se hash-uje, čime se osigurava da isti password rezultira različitim hash vrednostima.

5. Koja biblioteka se uvodi u kursu?

Odgovori svojim rečima: biblioteka koja se uvodi u kursu je `passlib`, koja omogućava bezbedno hash-ovanje i verifikaciju lozinki.

6. Koja je razlika između `hash()` i `verify()`?

Odgovori svojim rečima: `hash()` kreira hash vrednost za dati plain-text password, dok `verify()` proverava da li dati plain-text password odgovara prethodno kreiranom hash-u.

---

## 11) Realna mapa sledećih lekcija

Posle današnje kontrolne tačke sledeći tok je:

```text
08 hash password
    -> bezbedno napravi hash

09 save user to database
    -> sačuvaj user-a i hash u bazu

10 authenticate a user
    -> pronađi user-a i proveri password

11 JSON Web Token
    -> razumi token koji predstavlja identitet (id korisnika)

12 encode JWT
    -> kreiraj access token

13 decode JWT
    -> validiraj Bearer token i dobij current user-a

14 authentication enhancements
    -> dovrši status kodove, prefixe i auth organizaciju
```

Do sada je završena priprema za prva tri security pitanja:

```text
Ko je korisnik?
Gde se korisnik cuva?
Kako se password bezbedno cuva?
```

Lekcija 08 sada direktno odgovara na treće pitanje.

---

## 12) Zaključak prve polovine oblasti

Posle lekcije 07 TodoApp ima osnovu za korisnike, ali još nema završenu autentifikaciju.

Stvarno stanje je:

```text
Users model postoji
Todos.owner_id postoji
auth router postoji
/auth prefix postoji
User request/response schema postoje

password hash još ne postoji
user se još ne čuva kroz auth endpoint
login još ne postoji
JWT još ne postoji
Todo authorization još ne postoji
```

Najvažniji problem koji sada treba rešiti je:

```python
hashed_password=create_user_request.password
```

Ovo mora postati konceptualno:

```python
hashed_password = bcrypt_context.hash(
    create_user_request.password
)
```

Tek posle toga vrednost treba proslediti u `Users.hashed_password`.

Zapamti:

> Kolona `hashed_password` nije bezbedna samo zato što se tako zove. Bezbedna postaje tek kada u nju upisemo stvarno izračunat password hash.

Ovim je završena prva polovina teorijske mape. Sledeći fokus je lekcija 08, bez preskakanja na login ili JWT dok password hashing i njegovo mesto u registracionom toku nisu jasni.
