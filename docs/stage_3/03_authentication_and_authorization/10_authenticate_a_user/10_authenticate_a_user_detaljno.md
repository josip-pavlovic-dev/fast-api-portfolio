# Oblast 03 - Authentication and Authorization

## Lekcija 10 - Autentifikacija korisnika

Do sada je tok izgledao ovako:

```text
korisnik posalje username i password
    -> password se hash-uje
        -> Users zapis se cuva u bazi
```

Sada aplikacija treba da proveri da li korisnik koji pokusava login zaista postoji i da li je uneo ispravan password.

Prvi cilj ove lekcije nije jos izdavanje JWT-a. Prvi cilj je da aplikacija ume da:

1. primi username i password
2. pronadje korisnika po username-u
3. proveri password pomocu sacuvanog hash-a
4. vrati rezultat autentifikacije

Kasnije ce se rezultat `True` koristiti za izdavanje access tokena.

### Vazna napomena za trenutni plan

Ovo je teorijski materijal. Ne menjamo aktivne Python fajlove, ne instaliramo `python-multipart`, ne pravimo stvarni `/token` endpoint i ne dodajemo login korisnika u bazu.

---

## 1) Authentication naspram authorization

### Authentication

Autentifikacija proverava identitet:

```text
Ko si ti?
```

U ovoj lekciji aplikacija proverava:

```text
Da li username postoji?
Da li password odgovara sacuvanom hash-u?
```

### Authorization

Autorizacija proverava dozvole:

```text
Sta smes da uradis?
```

Authorization dolazi nakon uspesne autentifikacije. Kasnije ce proveravati:

- da li je korisnik aktivan
- da li je korisnik admin
- da li todo pripada tom korisniku

Ova lekcija je prvenstveno o authentication delu.

---

## 2) Novi endpoint: `/token`

Transkript uvodi POST endpoint:

```python
@router.post("/token")
async def login_for_access_token():
    return "token"
```

Buduca lokacija u tvom projektu je:

```text
fast-api-course-my-work/TodoApp/api/routes/auth.py
```

Zasto se endpoint zove `/token`?

OAuth2 password flow tradicionalno koristi token endpoint na koji klijent salje kredencijale i ocekuje access token.

U ovoj lekciji endpoint jos ne vraca pravi JWT. On samo priprema prijem username-a i password-a.

Kasniji tok ce biti:

```text
POST /auth/token
    -> username + password
        -> provera korisnika
            -> JWT access token
```

Ako router ima:

```python
router = APIRouter(prefix="/auth")
```

onda lokalna ruta:

```python
@router.post("/token")
```

postaje:

```text
POST /auth/token
```

---

## 3) Zasto se koristi POST

Login kredencijali ne treba da budu deo URL-a.

Ne treba koristiti:

```text
GET /login?username=ana&password=Test1234
```

URL moze da se pojavi u:

- browser history-ju
- proxy logovima
- server logovima
- analytics alatima
- bookmark-ovima

Zato se kredencijali salju kroz POST request body, odnosno form data u OAuth2 password flow-u.

POST takodje bolje opisuje operaciju koja pokrece autentifikacioni proces i potencijalno izdaje token.

---

## 4) `OAuth2PasswordRequestForm`

Transkript koristi FastAPI security dependency:

```python
from fastapi.security import OAuth2PasswordRequestForm
```

Ovaj objekat ocekuje form podatke, posebno:

```text
username
password
```

Pored njih forma moze imati i standardna OAuth2 polja:

```text
grant_type
scope
client_id
client_secret
```

Za ovaj kursni korak koriste se prvenstveno:

```python
form_data.username
form_data.password
```

Primer dependency oblika:

```python
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm


form_data: Annotated[
    OAuth2PasswordRequestForm,
    Depends(),
]
```

U novijem FastAPI kodu moze se koristiti i:

```python
form_data: OAuth2PasswordRequestForm = Depends()
```

Oba primera izrazavaju istu ideju: FastAPI treba da napravi form objekat iz incoming request-a.

---

## 5) Zasto je potreban `python-multipart`

`OAuth2PasswordRequestForm` koristi form data, a ne obican JSON body.

FastAPI za parsiranje form podataka koristi multipart podrsku. Zato transkript instalira:

```bash
pip install python-multipart
```

U tvom projektu je to runtime dependency jer je potrebna dok aplikacija obradjuje form request.

Konceptualno mesto za dependency je:

```text
fast-api-portfolio/requirements.txt
```

Ne pripada `requirements-dev.txt` samo zato sto se koristi tokom razvoja. Ako aplikacija bez nje ne moze da obradjuje production request, onda je runtime dependency.

### Vazna napomena za ovaj kurs

Ne instaliramo paket sada. Kada dodje prakticna faza, proverice se postojeci dependency fajl i instalacija ce se uraditi uskladjeno sa celim projektom.

---

## 6) Kako Swagger prikazuje formu

Kada endpoint koristi `OAuth2PasswordRequestForm`, Swagger UI moze prikazati polja:

```text
username
password
grant_type
scope
client_id
client_secret
```

To je drugacije od JSON request-a kao:

```json
{
  "username": "ana",
  "password": "Test1234"
}
```

OAuth2 password flow koristi form format, pa browser/Swagger salje podatke kao form fields.

U ovoj fazi endpoint moze vratiti samo:

```text
"token"
```

To ne znaci da je autentifikacija uspesna. Endpoint jos nije proverio podatke.

---

## 7) Dodavanje DB dependency-ja u token endpoint

Da bi endpoint pronasao korisnika u bazi, treba mu SQLAlchemy session.

U tvom projektu se koristi centralni dependency:

```python
from ...db.session import db_dependency
```

Buduci potpis moze konceptualno izgledati ovako:

```python
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: db_dependency = None,
):
    ...
```

Napomena: stvarni Python potpis treba formatirati prema pravilima tipova i postojecem stilu projekta. Poenta je da endpoint dobija:

```text
form_data -> username i password
db        -> database session
```

U ranijim lekcijama koristili smo `db_dependency` kao `Annotated` alias. Prakticni potpis ce se prilagoditi tacnoj verziji FastAPI/Python typing stila koju budemo koristili.

---

## 8) Pomocna funkcija `authenticate_user`

Umesto da endpoint direktno sadrzi svu query i password logiku, transkript uvodi pomocnu funkciju:

```python
def authenticate_user(
    username: str,
    password: str,
    db: Session,
):
    ...
```

Ova funkcija ima jednu glavnu odgovornost:

```text
proveri da li username i password pripadaju validnom korisniku
```

Ne treba je mesati sa:

- kreiranjem JWT-a
- proverom admin role
- citanjem todo zapisa
- registracijom novog korisnika

Podela funkcija olaksava testiranje i citanje koda.

---

## 9) Pronalaženje korisnika po username-u

Pomocna funkcija prvo pretrazuje `Users` tabelu:

```python
user = (
    db.query(Users)
    .filter(Users.username == username)
    .first()
)
```

Znacenje:

```text
uzmi Users tabelu
pronadji red gde je username jednak vrednosti iz login forme
uzmi prvi rezultat
```

SQLAlchemy upit odgovara otprilike ovom SQL-u:

```sql
SELECT *
FROM users
WHERE username = 'ana'
LIMIT 1;
```

Ako korisnik ne postoji:

```python
if user is None:
    return False
```

Ne treba nastaviti na `user.hashed_password` ako je `user` `None`.

---

## 10) Provera password-a pomocu `verify()`

Ako korisnik postoji, proverava se password:

```python
if not bcrypt_context.verify(
    password,
    user.hashed_password,
):
    return False
```

Ovde su argumenti:

```text
password
    plain password koji je korisnik upravo poslao

user.hashed_password
    hash sacuvan u bazi
```

`verify()` internally koristi algoritam i salt podatke iz hash vrednosti da proveri da li plain password odgovara.

Ne radimo:

```python
bcrypt_context.hash(password) == user.hashed_password
```

jer isti password moze dobiti drugaciji hash zbog salt-a.

Ako password odgovara:

```python
return True
```

Ako username ne postoji ili password nije ispravan:

```python
return False
```

---

## 11) Kompletna teorijska pomocna funkcija

Prilagodjeni ciljni oblik moze izgledati ovako:

```python
from sqlalchemy.orm import Session

from ...models import Users


def authenticate_user(
    username: str,
    password: str,
    db: Session,
):
    user = (
        db.query(Users)
        .filter(Users.username == username)
        .first()
    )

    if user is None:
        return False

    if not bcrypt_context.verify(
        password,
        user.hashed_password,
    ):
        return False

    return user
```

Transkript vraca `True` za uspesnu proveru. Prakticniji oblik vraca sam `user` objekat, jer sledeci korak treba korisnicki ID za JWT payload.

Oba pristupa mogu biti edukativno validna:

```text
True/False
    dovoljno za prostu proveru

user/False
    korisnije za nastavak autentifikacionog toka
```

Ako funkcija vraca `user`, endpoint moze koristiti:

```python
user.id
user.username
user.role
user.is_active
```

---

## 12) Pozivanje funkcije iz token endpointa

Endpoint uzima podatke iz forme:

```python
user = authenticate_user(
    form_data.username,
    form_data.password,
    db,
)
```

Ako autentifikacija nije uspesna:

```python
if not user:
    return "Failed authentication"
```

Ako jeste:

```python
return "Successful authentication"
```

Ovo je demonstracioni oblik iz transkripta.

### Bolji FastAPI oblik

Pravilniji API odgovor koristi `HTTPException`:

```python
from fastapi import HTTPException, status


if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
```

Uspesna autentifikacija jos ne mora da vrati JWT u ovoj lekciji. Moze privremeno vratiti potvrdu, ali sledeca lekcija ce dodati pravi token.

---

## 13) Zasto ne treba otkrivati da li username postoji

Bezbednosno je bolje koristiti isti neuspesan odgovor za:

```text
username ne postoji
password nije ispravan
```

Ne treba vracati:

```text
"Username ne postoji"
```

u jednom slucaju i:

```text
"Password je pogresan"
```

u drugom, jer napadac moze da proverava koji username-i postoje u sistemu.

Bolji genericki odgovor je:

```text
Incorrect username or password
```

Ovo ne sprecava sve napade, ali smanjuje nepotrebno otkrivanje informacija.

---

## 14) Provera `is_active`

Pronadjen korisnik moze biti deaktiviran:

```python
if not user.is_active:
    return False
```

Buduci redosled moze biti:

```text
1. pronadji korisnika
2. proveri password
3. proveri is_active
4. dozvoli dalji autentifikacioni tok
```

Neke aplikacije prvo proveravaju active status, neke ga proveravaju zajedno sa login pravilima. Vazno je da neaktivni korisnik ne dobije pristup samo zato sto zna ispravan password.

---

## 15) `form_data.username` i `form_data.password`

`OAuth2PasswordRequestForm` objekat sadrzi vrednosti koje je FastAPI izvukao iz forme:

```python
form_data.username
form_data.password
```

To nisu isto sto i:

```python
CreateUserRequest
```

`CreateUserRequest` sluzi za registraciju i moze imati:

```text
email
first_name
last_name
role
```

Login forma uglavnom koristi:

```text
username
password
```

Razlog je sto registracija i login imaju razlicite potrebe.

---

## 16) Buduci raspored security logike

U pocetnoj verziji kursa pomocna funkcija i `bcrypt_context` mogu biti u `auth.py`:

```text
TodoApp/api/routes/auth.py
    bcrypt_context
    authenticate_user
    /register
    /token
```

Kada kod poraste, logicnija podela moze biti:

```text
TodoApp/core/security.py
    password_context
    hash_password()
    verify_password()

TodoApp/api/routes/auth.py
    register endpoint
    token endpoint
    pozivi security helpera
```

Tada auth router ostaje usmeren na HTTP tok, a security modul na kriptografske operacije.

Ovo je preporucena buduca organizacija, ali se ne uvodi pre zavrsetka teorije.

---

## 17) Sta ova lekcija jos ne radi

Ova lekcija jos ne pravi JWT, iako endpoint ima naziv `/token`.

Ne radi jos:

- encoding JWT-a
- decoding JWT-a
- access token payload
- `sub` claim
- `exp` claim
- current user dependency
- zastitu Todo ruta
- role authorization

Radi samo:

```text
prijem login podataka
pronalaženje user-a
verify password-a
osnovni rezultat autentifikacije
```

Zato je `/token` u ovoj lekciji priprema za kasniji endpoint, a ne kompletan token sistem.

---

## 18) Pitanja za proveru znanja

1. Koja je razlika izmedju authentication i authorization?
2. Zasto se za login koristi POST?
3. Sta je uloga `/token` endpointa?
4. Zasto se koristi `OAuth2PasswordRequestForm`?
5. Koji paket je potreban za form data podrsku?
6. Koja polja iz forme koristi ova lekcija?
7. Gde se u tvom projektu nalazi `db_dependency`?
8. Sta radi funkcija `authenticate_user`?
9. Kako se korisnik pronalazi u `Users` tabeli?
10. Sta se vraca ako username ne postoji?
11. Kako se proverava password?
12. Zasto se ne porede dva nova bcrypt hash stringa?
13. Zasto je bolje koristiti genericki neuspesan login odgovor?
14. Sta radi provera `is_active`?
15. Zasto transkriptni stringovi `successful/failed authentication` nisu idealan production API odgovor?
16. Koja je razlika izmedju registracionog `CreateUserRequest` i login forme?
17. Sta `/token` endpoint jos ne radi u ovoj lekciji?

---

## 19) Prakticni zadaci

### Zadatak 1 - Razvrstaj podatke

Razvrstaj gde se nalaze podaci:

```text
CreateUserRequest
OAuth2PasswordRequestForm
Users ORM model
```

Za svaku navedenu strukturu napisi koja polja ocekuje.

### Zadatak 2 - Nacrtaj login tok

Nacrtaj:

```text
username + password forma
    -> authenticate_user()
        -> query Users
            -> verify password
                -> user ili False
```

Uz svaku strelicu napisi sta se desava.

### Zadatak 3 - Napisi SQL ekvivalent

Prevedi ovaj SQLAlchemy query u SQL:

```python
user = (
    db.query(Users)
    .filter(Users.username == username)
    .first()
)
```

Koristi oblik:

```sql
SELECT ...
FROM ...
WHERE ...
LIMIT ...;
```

### Zadatak 4 - Pronadji redosled provere

Poredjaj korake:

```text
verify password
pronadji user
proveri is_active
izdaj token
```

Objasni zasto token ne treba izdati pre uspesne provere.

### Zadatak 5 - Ispravi nesiguran rezultat

Analiziraj:

```python
if user is None:
    return "Username does not exist"

if not password_matches:
    return "Wrong password"
```

Napisi jedan genericki odgovor koji ne otkriva koja je od dve situacije nastala.

### Zadatak 6 - Uporedi `True` i user objekat

Objasni razliku izmedju:

```python
return True
```

i:

```python
return user
```

Koji oblik je prakticniji za sledecu lekciju o JWT-u i zasto?

### Zadatak 7 - Odredi fajlove

Za svaki deo upisi buducu lokaciju:

```text
OAuth2PasswordRequestForm import
authenticate_user()
Users model
get_db()
password verify helper
/token endpoint
```

Koristi:

```text
TodoApp/api/routes/auth.py
TodoApp/models.py
TodoApp/db/session.py
TodoApp/core/security.py
```

### Zadatak 8 - Form dependency

Objasni razliku izmedju JSON tela:

```json
{
  "username": "ana",
  "password": "Test1234"
}
```

i OAuth2 form podataka sa istim vrednostima.

Navedi zasto Swagger prikazuje drugaciji oblik.

### Zadatak 9 - HTTP statusi

Odredi odgovarajuci rezultat:

```text
ispravan username i password
nepostojeci username
pogresan password
neaktivan korisnik
```

Za svaki navedi da li bi koristio:

```text
200
401
403
```

i objasni izbor.

### Zadatak 10 - Priprema za JWT

Napravi plan sta treba dodati nakon sto `authenticate_user()` vrati validnog korisnika.

U plan ukljuci:

- korisnicki ID
- payload
- potpisivanje tokena
- expiration
- response model
- zastitu buducih ruta

---

## 20) Zakljucak

Ova lekcija uvodi prvi stvarni korak autentifikacije:

```text
username + password
    -> pronadji user-a
        -> verify sacuvanog hash-a
            -> validan ili nevalidan korisnik
```

Za tvoj projekat:

- `/token` endpoint pripada `TodoApp/api/routes/auth.py`
- `OAuth2PasswordRequestForm` prima login formu
- `python-multipart` je runtime dependency za form podatke
- `db_dependency` se koristi iz `TodoApp/db/session.py`
- `Users` model pripada `TodoApp/models.py`
- password provera moze kasnije biti izdvojena u `TodoApp/core/security.py`
- JWT jos nije implementiran

Najvaznije je zapamtiti da autentifikacija prvo mora pouzdano da utvrdi ko je korisnik. Tek nakon toga aplikacija moze izdati token i proveravati authorization pravila.

Aktivne skripte, dependency fajlovi i baza ostaju nepromenjeni dok se ne zavrsi teorija cele oblasti.
