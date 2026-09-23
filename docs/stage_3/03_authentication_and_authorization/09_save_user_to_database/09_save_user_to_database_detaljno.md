# Oblast 03 - Authentication and Authorization

## Lekcija 09 - Cuvanje korisnika u bazu

Prethodna lekcija je napravila `Users` ORM objekat i hashovala password, ali ga je samo vratila iz endpointa.

Sada se dodaje sledeci korak:

```text
request
    -> Pydantic validacija
        -> password hash
            -> Users ORM objekat
                -> db.add()
                    -> db.commit()
                        -> korisnik sacuvan u bazi
```

U transkriptu se auth modul dodatno povezuje sa DB sesijom. U tvom projektu vec postoji centralizovana DB dependency logika u:

```text
fast-api-course-my-work/TodoApp/db/session.py
```

Zato u buducoj implementaciji `auth.py` treba da koristi postojece:

```python
from ...db.session import db_dependency
```

a ne da ponovo kopira `get_db()` u router.

### Vazna napomena

Ovo je teorijski materijal. Ne menjamo aktivne Python fajlove, ne instaliramo pakete i ne dodajemo korisnika u bazu.

---

## 1) Sta se menja u odnosu na prethodnu lekciju

Prethodni demonstracioni endpoint mogao je da radi ovako:

```python
@router.post("/register")
async def create_user(create_user_request: CreateUserRequest):
    user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=hash_password(create_user_request.password),
        is_active=True,
    )

    return user_model
```

Problem je sto objekat nije sacuvan u bazi.

Vraca se Python/ORM objekat koji postoji samo tokom obrade request-a. Ako se proces zavrsi, taj objekat sam po sebi ne znaci da postoji trajni red u tabeli `users`.

Nova ideja je:

```python
db.add(user_model)
db.commit()
```

---

## 2) Gde se buduci kod smesta

U tvom rasporedu buduca podela je:

```text
TodoApp/api/routes/auth.py
    POST /auth/register
    kreiranje Users objekta
    db.add i db.commit

TodoApp/db/session.py
    get_db()
    db_dependency

TodoApp/models.py
    Users SQLAlchemy model

TodoApp/schemas.py
    CreateUserRequest
    UserResponse

TodoApp/main.py
    glavna FastAPI aplikacija
    include_router(auth.router)
```

Kursni primer mozda importuje dependency iz lokalnog `database.py` ili ga definise u auth fajlu. Tvoj projekat je vec organizovan drugacije, pa ne treba praviti drugu verziju DB dependency-ja.

---

## 3) DB dependency iz tvog projekta

Tvoj postojeći koncept je:

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

Auth router ne treba da zna detalje o tome kako se `SessionLocal` pravi. On samo koristi tip dependency-ja:

```python
async def create_user(
    db: db_dependency,
    create_user_request: CreateUserRequest,
):
    ...
```

FastAPI ce pri svakom request-u:

1. pozvati `get_db()`
2. dobiti SQLAlchemy `Session`
3. proslediti je endpointu kroz `db`
4. zatvoriti sesiju u `finally` bloku

---

## 4) Sta radi `db.add()`

Kada napravimo ORM objekat:

```python
user_model = Users(
    email="ana@example.com",
    username="ana",
    first_name="Ana",
    last_name="Jovanovic",
    hashed_password="hash-vrednost",
    is_active=True,
    role="user",
)
```

on jos nije trajno upisan u bazu.

Poziv:

```python
db.add(user_model)
```

dodaje objekat u SQLAlchemy session.

To znaci da session zna da objekat treba da bude insertovan u bazu pri flush/commit fazi.

Mozemo zamisliti stanje:

```text
user_model napravljen u Python memoriji
    -> db.add(user_model)
        -> session prati objekat
```

`db.add()` sam po sebi nije isto sto i konacno potvrđivanje transakcije.

---

## 5) Sta radi `db.commit()`

Poziv:

```python
db.commit()
```

potvrđuje trenutnu transakciju.

SQLAlchemy tada salje promenu bazi, pa novi korisnik postaje trajno sacuvan ako nema greske.

Pojednostavljen tok:

```text
db.add(user_model)
    objekat je pripremljen u session-u

db.commit()
    transakcija se potvrđuje
    INSERT se trajno cuva u bazi
```

Ako se `commit()` ne pozove, promena mozda nece biti trajno sacuvana nakon zatvaranja sesije.

### Transakcija

Transakcija je grupa promena koja treba da se potvrdi kao celina.

Ako nastane greska pre commit-a, aplikacija moze prekinuti obradu i uraditi rollback:

```python
try:
    db.add(user_model)
    db.commit()
except Exception:
    db.rollback()
    raise
```

Ovaj obrazac je vazan kada se uvedu provere jedinstvenosti i moguce DB greske.

---

## 6) Zasto transkript dobija `201` i `null`

Transkript postavlja status:

```python
status_code=status.HTTP_201_CREATED
```

To znaci da je novi resurs kreiran.

Zatim endpoint ne vraca model, vec samo radi:

```python
db.add(create_user_model)
db.commit()
```

Ako Python funkcija ne sadrzi eksplicitni `return`, njena povratna vrednost je:

```python
None
```

FastAPI `None` serijalizuje kao:

```json
null
```

Zato response moze biti:

```text
status: 201 Created
body: null
```

To nije nuzno greska. Znaci da je zahtev uspesno zavrsen, ali endpoint nije definisao response body.

U zrelijem API-ju cesto zelimo da vratimo bezbedan `UserResponse`, ali ne i password podatke.

---

## 7) Zasto ne treba samo vratiti sacuvani ORM model

Naivni oblik je:

```python
db.add(user_model)
db.commit()
return user_model
```

Problem je sto `user_model` moze sadrzati:

```text
hashed_password
```

Ni plain password ni hash ne treba nepotrebno izlagati klijentu.

Bolji princip je odvojiti:

```text
Users model
    podaci za bazu

UserResponse schema
    samo podaci koji smeju u response
```

Primer:

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

U response-u nema:

```text
password
hashed_password
```

---

## 8) Zasto je `db.refresh()` ponekad potreban

Posle commit-a baza moze generisati vrednosti koje objekat nije imao pre upisa, na primer:

```text
id
created_at
```

Ako zelimo da objekat osvezi vrednosti iz baze:

```python
db.refresh(user_model)
```

Tok moze biti:

```python
db.add(user_model)
db.commit()
db.refresh(user_model)
return user_model
```

Za korisnicki endpoint koji vraca response sa novim `id`-em, `refresh()` je cesto koristan.

Ako endpoint vraca `201` i `null`, kao u transkriptu, `refresh()` nije neophodan za sam response. Ipak, u punoj implementaciji treba svesno odluciti sta se vraca.

---

## 9) Konceptualni kompletan endpoint

Prilagodjeni ciljnom rasporedu, teorijski endpoint moze izgledati ovako:

```python
from fastapi import APIRouter, status

from ...db.session import db_dependency
from ...models import Users
from ...schemas import CreateUserRequest


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    db: db_dependency,
    create_user_request: CreateUserRequest,
):
    hashed_password = bcrypt_context.hash(
        create_user_request.password
    )

    user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=hashed_password,
        is_active=True,
        role="user",
    )

    db.add(user_model)
    db.commit()
    db.refresh(user_model)
```

Ako nema `return`, response body je `null`.

Ovo je edukativni primer, ne gotova produkciona implementacija. Nedostaju:

- provera postojecih email i username vrednosti
- rollback pri DB gresci
- response schema
- kontrola input role vrednosti
- centralizovan security helper
- testovi

---

## 10) Zasto `role` ne treba slepo uzeti iz request-a

U prethodnoj lekciji request je imao:

```python
role: str
```

Ako sada direktno radimo:

```python
role=create_user_request.role
```

klijent moze da pokusa da napravi admin nalog.

Za javnu registraciju bezbedniji koncept je:

```python
role="user"
```

A admin role se dodeljuje kontrolisanim procesom.

Ovo je vazno jer cuvanje korisnika u bazi nije samo tehnicki insert. To je i bezbednosna odluka o tome koje vrednosti aplikacija prihvata.

---

## 11) Provera da korisnik vec ne postoji

Ako su `email` i `username` jedinstveni, aplikacija treba pre insert-a da proveri da li vec postoje.

Konceptualno:

```python
existing_user = (
    db.query(Users)
    .filter(Users.username == create_user_request.username)
    .first()
)

if existing_user is not None:
    raise HTTPException(
        status_code=400,
        detail="Username vec postoji.",
    )
```

Slicna provera moze da postoji za email.

Samo provera u Python kodu nije dovoljna kao jedina zastita. Database `unique=True` constraint treba da bude krajnja zastita od duplikata, posebno kada dva request-a stignu istovremeno.

---

## 12) Provera baze pomocu SQLite alata

Transkript proverava sacuvani red direktno SQLite komandnim alatom.

Konceptualni SQL je:

```sql
SELECT * FROM users;
```

Ovaj upit vraca sve kolone i redove iz `users` tabele.

Ocekivane kolone mogu biti:

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

U SQLite prikazu boolean vrednosti se cesto vide kao:

```text
1 -> True
0 -> False
```

To je nacin predstavljanja vrednosti u SQLite-u, a ne promena Python znacenja.

### Vazna napomena za tvoj projekat

Ne pretpostavljamo naziv fajla baze i ne pokrecemo komandu dok ne dodjemo do prakticne implementacije. Tacan database URL treba procitati iz `TodoApp/db/database.py`.

---

## 13) Sta se desava ako commit ne uspe

Commit moze da ne uspe zbog:

- duplog unique email-a
- duplog username-a
- pogresne strukture tabele
- pogresnog tipa podatka
- prekinute baze
- problema sa foreign key pravilima

Ako commit ne uspe, session moze ostati u stanju greske. Zato se koristi rollback:

```python
try:
    db.add(user_model)
    db.commit()
except Exception:
    db.rollback()
    raise
```

U naprednijoj implementaciji greska se moze pretvoriti u jasan HTTP response, ali se ne sme sakriti bez rollback-a.

---

## 14) Odnos transakcije i dependency lifecycle-a

`get_db()` otvara session pre endpointa i zatvara je posle endpointa.

Unutar endpointa:

```python
db.add(user_model)
db.commit()
```

commit odlucuje da li je promena potvrdjena.

Na kraju request-a:

```python
db.close()
```

zatvara sesiju.

Ova tri pojma nisu ista:

```text
Session lifecycle
    otvori i zatvori DB sesiju

add
    dodaj objekat u session

commit
    potvrdi transakciju u bazi
```

Razumevanje ove razlike pomaze kod buducih problema sa rollback-om i vise DB operacija u jednom request-u.

---

## 15) Gde se koriste paketi i skripte

Buduci raspored:

```text
TodoApp/
    api/routes/auth.py
        endpoint za registraciju

    db/session.py
        db_dependency

    db/database.py
        engine i SessionLocal

    models.py
        Users model

    schemas.py
        CreateUserRequest i UserResponse

    core/security.py
        password hashing helper, kasnije

    main.py
        include_router(auth.router)
```

Paketi:

```text
requirements.txt
    runtime biblioteke za FastAPI, SQLAlchemy i security

requirements-dev.txt
    testovi, lint i razvojni alati
```

U teorijskoj fazi ne menjamo ni jedan od ovih fajlova.

---

## 16) Sta ova lekcija jos ne resava

Ova lekcija ne predstavlja zavrsen register sistem.

Jos uvek nedostaju:

- stvarna implementacija u `auth.py`
- `Users` model u aktivnom `models.py`
- migration ili reset baze
- jedinstvene provere
- rollback obrada
- response schema
- login endpoint
- password verification
- JWT
- current user dependency
- authorization

Lekcija uci samo granicu izmedju:

```text
napraviti ORM objekat
```

i:

```text
sacuvati ORM objekat u bazu
```

---

## 17) Pitanja za proveru znanja

1. Koja je razlika izmedju pravljenja ORM objekta i njegovog cuvanja u bazi?
2. Sta radi `db.add(user_model)`?
3. Sta radi `db.commit()`?
4. Zasto `db.add()` sam po sebi nije dovoljan?
5. Zasto transkript dobija `201` i `null` response body?
6. Kada moze biti koristan `db.refresh()`?
7. Zasto ne treba vratiti ceo `Users` ORM model klijentu?
8. Gde se u tvom projektu nalazi `db_dependency`?
9. Zasto ne treba kopirati `get_db()` u `auth.py`?
10. Zasto javna registracija ne treba slepo da prihvati `role="admin"`?
11. Zasto su database unique constraint-i i Python provere oba korisna?
12. Sta treba uraditi ako `commit()` baci gresku?
13. Koji SQL upit proverava korisnike u tabeli?
14. Zasto SQLite prikazuje boolean kao `1` ili `0`?
15. Koje funkcionalnosti nedostaju pre pravog login sistema?

---

## 18) Prakticni zadaci

### Zadatak 1 - Nacrtaj session tok

Nacrtaj sledeci tok i uz svaki korak napisi objasnjenje:

```text
get_db()
    -> db_dependency
        -> db.add(user_model)
            -> db.commit()
                -> db.close()
```

Razdvoji lifecycle sesije od operacija transakcije.

### Zadatak 2 - Razlika add i commit

Objasni svojim recima sta bi moglo da se desi ako kod sadrzi:

```python
db.add(user_model)
```

ali nema:

```python
db.commit()
```

### Zadatak 3 - Analiziraj `201 null`

Objasni rezultat:

```text
HTTP 201
response body: null
```

Napisi kakav bi rezultat bio kada endpoint ima:

```python
return user_response
```

### Zadatak 4 - Napisi bezbedan response spisak

Odredi koja polja smeju da se vrate iz `Users` modela:

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

Objasni zasto `hashed_password` izostaje.

### Zadatak 5 - Planiraj rollback

Dopuni konceptualni obrazac:

```python
try:
    db.add(user_model)
    db.commit()
except Exception:
    ______________________
    ______________________
```

Objasni zasto se rollback radi pre ponovnog bacanja greske.

### Zadatak 6 - Dupli username

Pretpostavi da `username="ana"` vec postoji.

Napisi plan:

1. kako proveravas postojanje
2. koji HTTP status vracas
3. zasto unique constraint i dalje treba da postoji

### Zadatak 7 - Prepoznaj losu arhitekturu

Analiziraj ideju da svaki router ima sopstvenu kopiju `get_db()` funkcije.

Navedi najmanje tri problema i objasni zasto je `TodoApp/db/session.py` bolje centralno mesto.

### Zadatak 8 - Razdvoji odgovornosti fajlova

Popuni:

```text
auth.py       ->
session.py    ->
database.py   ->
models.py     ->
schemas.py    ->
main.py       ->
```

Koristi konkretne odgovornosti iz ove lekcije.

### Zadatak 9 - Provera SQL rezultata

Napisi SQL upit koji prikazuje sve korisnike:

```sql
SELECT * FROM users;
```

Zatim navedi koje kolone ocekujes da vidis i kako bi prepoznao da je `is_active` ukljucen u SQLite prikazu.

### Zadatak 10 - Celokupan teorijski plan

Napisi redosled buduce implementacije od request-a do baze:

```text
request
Pydantic validacija
hash password-a
Users ORM objekat
DB dependency
db.add
db.commit
db.refresh
bezbedan response
```

Za svaki korak navedi fajl u kom bi se nalazio kod.

---

## 19) Zakljucak

Kreiranje ORM objekta i cuvanje u bazi su dva razlicita koraka.

Glavni tok je:

```text
Users(...)
    -> db.add(user_model)
        -> db.commit()
            -> zapis u users tabeli
```

Za tvoj projekat najvaznije je:

- auth endpoint pripada `TodoApp/api/routes/auth.py`
- `db_dependency` se koristi iz `TodoApp/db/session.py`
- `Users` model pripada `TodoApp/models.py`
- request i response schemata pripadaju `TodoApp/schemas.py`
- engine i `SessionLocal` ostaju u `TodoApp/db/database.py`
- `main.py` sklapa aplikaciju i ukljucuje auth router

Transkript prikazuje `201` sa `null` body-em zato sto endpoint ne vraca objekat nakon commit-a. To je korisno za razumevanje transakcije, ali kasnije treba dodati bezbedan response bez password vrednosti.

Aktivne skripte, dependency fajlovi i baza ostaju nepromenjeni dok se ne zavrsi teorija cele oblasti.
