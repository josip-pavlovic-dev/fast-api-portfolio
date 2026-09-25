# Dan 6 - Ispravka registracije korisnika i password hashovanja

## 1) Problem koji je prijavljen

Registracioni endpoint u `TodoApp/api/routes/auth.py` koristio je `Passlib`:

```python
hashed_password=bcrypt_context.hash(
	create_user_request.password
)
```

Ali endpoint je samo napravio SQLAlchemy objekat i vratio ga:

```python
create_user_model = Users(...)
return create_user_model
```

Objekat tada jos nije bio sacuvan u bazi. Zbog toga SQLAlchemy nije popunio njegov `id`.

Istovremeno, response schema zahteva:

```python
class UserResponse(BaseModel):
	id: int
	email: str
	username: str
	first_name: str
	last_name: str
	is_active: bool
	role: str
```

Novi ORM objekat pre `commit()` poziva ima priblizno ovo stanje:

```text
id = None
email = "ana@example.com"
username = "ana"
hashed_password = "...hash..."
```

`UserResponse` ne moze da pretvori `None` u obavezni `int`, pa FastAPI moze prijaviti response validation `422`.

---

## 2) Zasto se hash ponekad nije izvrsavao

HTTP `422` moze nastati na dve razlicite tacke.

### 2.1 Request validation `422`

Pre nego sto FastAPI pozove funkciju `create_users()`, Pydantic proverava request body prema modelu `CreateUserRequest`.

Model zahteva sva polja:

```python
class CreateUserRequest(BaseModel):
	email: str
	username: str
	first_name: str
	last_name: str
	password: str
	role: str
```

Validan JSON primer je:

```json
{
  "email": "ana@example.com",
  "username": "ana",
  "first_name": "Ana",
  "last_name": "Jovanovic",
  "password": "Test1234",
  "role": "user"
}
```

Ako nedostaje na primer `role`, FastAPI vraca `422` pre ulaska u endpoint. Tada se ovaj kod uopste ne izvrsava:

```python
bcrypt_context.hash(create_user_request.password)
```

U response JSON-u takva greska obicno ima lokaciju slicnu:

```json
{
  "detail": [
    {
      "loc": ["body", "role"],
      "msg": "Field required"
    }
  ]
}
```

`loc: ["body", ...]` znaci da je problem u request body-ju.

### 2.2 Response validation `422`

Ako je lokacija slicna:

```json
{
  "detail": [
    {
      "loc": ["response", "id"],
      "msg": "Input should be a valid integer"
    }
  ]
}
```

onda je endpoint vec radio, ali vraceni `Users` objekat nema generisan `id`. U tom slucaju password hash je mogao vec biti napravljen, ali korisnik nije pravilno sacuvan i osvezen iz baze.

Pravilo za dijagnozu:

```text
body    -> greska pre endpoint funkcije
response -> greska nakon endpoint funkcije
```

---

## 3) Sta je promenjeno u `auth.py`

Postojeci projekat vec ima centralizovanu DB dependency logiku u:

```text
TodoApp/db/session.py
```

Tamo postoji:

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

Zato `auth.py` ne treba da pravi novu sesiju, vec koristi postojeci dependency:

```python
from ...db.session import db_dependency
```

Endpoint sada prima i DB sesiju:

```python
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_users(
	create_user_request: CreateUserRequest,
	db: db_dependency,
) -> UserResponse:
```

Posle kreiranja ORM objekta dodata su tri vazna koraka:

```python
db.add(create_user_model)
db.commit()
db.refresh(create_user_model)
```

Kompletan relevantni tok sada izgleda ovako:

```python
create_user_model = Users(
	email=create_user_request.email,
	username=create_user_request.username,
	first_name=create_user_request.first_name,
	last_name=create_user_request.last_name,
	role=create_user_request.role,
	hashed_password=bcrypt_context.hash(
		create_user_request.password
	),
	is_active=True,
)

db.add(create_user_model)
db.commit()
db.refresh(create_user_model)

return create_user_model
```

---

## 4) Znacenje `db.add`, `db.commit` i `db.refresh`

### `db.add()`

```python
db.add(create_user_model)
```

Dodaje ORM objekat u SQLAlchemy session. Objekat je sada poznat session-u i spreman za insert, ali transakcija jos nije potvrdena.

Mentalni model:

```text
Python objekat
	-> db.add()
		-> SQLAlchemy session prati objekat
```

### `db.commit()`

```python
db.commit()
```

Potvrdjuje transakciju i salje INSERT bazi.

Pojednostavljeno:

```text
db.add(user)
	priprema objekat

db.commit()
	trajno potvrdjuje promenu
```

Posle uspehnog commit-a SQLite moze generisati primarni kljuc `id`.

### `db.refresh()`

```python
db.refresh(create_user_model)
```

Ponovo cita objekat iz baze i osvezava njegove vrednosti u Python memoriji. To je vazno zato sto se nakon insert-a mogu popuniti:

- `id` koji generise baza
- database default vrednosti
- druge vrednosti koje dolaze iz baze

Posle refresh-a objekat je spreman za `UserResponse`:

```text
id = 1
email = "ana@example.com"
username = "ana"
is_active = True
role = "user"
```

---

## 5) Zasto `UserResponse` sada moze da radi

Schema koristi:

```python
model_config = ConfigDict(from_attributes=True)
```

To dozvoljava Pydantic-u da cita atribute iz SQLAlchemy objekta, umesto da ocekuje obican dictionary.

Ali `from_attributes=True` ne moze da resi problem nedostajuceg `id`. Ono samo govori Pydantic-u gde da cita vrednosti.

Potrebna su oba uslova:

```text
from_attributes=True
	omogucava citanje ORM atributa

db.add + db.commit + db.refresh
	obezbedjuju da ORM objekat ima generisan id
```

Takodje, `UserResponse` namerno nema:

```python
password
hashed_password
```

Hash se cuva interno radi kasnijeg login-a, ali se ne vraca javnom API klijentu.

---

## 6) Zasto kurs prikazuje hash, a tvoj response ne

U kursnom prikazu mozes videti vrednost slicnu:

```text
$2b$12$...dugacak_hash...
```

To ne znaci da se hash kod tebe nije napravio. U tvom trenutnom kodu hash se pravi ovde:

```python
hashed_password=bcrypt_context.hash(
	create_user_request.password
)
```

Razlika je u `UserResponse` schemi. Tvoja schema namerno sadrzi:

```python
class UserResponse(BaseModel):
	id: int
	email: str
	username: str
	first_name: str
	last_name: str
	is_active: bool
	role: str
```

Ona ne sadrzi:

```python
hashed_password: str
```

Zato FastAPI response validacija izbacuje `hashed_password` iz javnog response body-ja. Hash se i dalje nalazi u SQLAlchemy objektu i cuva se u koloni `users.hashed_password`, ali nije poslat klijentu.

### Dva razlicita prikaza

Kursni demo moze prikazati hash ako:

- vraca ceo ORM objekat bez ogranicene response schema-e
- koristi response schemu koja sadrzi `hashed_password`
- stampa ORM objekat ili cita bazu direktno

Tvoj API koristi bezbedniji oblik:

```text
Users ORM objekat
	-> sadrzi hashed_password interno

UserResponse
	-> namerno ne sadrzi hashed_password

HTTP response
	-> ne prikazuje hash
```

Zato je normalno da u Swagger response body-ju ne vidis hash, ali da ga vidis ako proveris SQLite bazu ili interno ispisivanje objekta tokom ucenja.

### Zasto ne treba dodati hash u `UserResponse`

Tehnicki bi moglo:

```python
class UserResponse(BaseModel):
	...
	hashed_password: str
```

Ali to nije dobro za stvarni API. Hash nije plaintext password, ali je i dalje osetljiv interni autentifikacioni podatak. Ako napadac dobije hash, moze pokusavati offline napade na password.

Zato je ispravno da hash:

- postoji u bazi
- postoji u internom ORM objektu
- koristi se kasnije za `verify()`
- ne postoji u javnom response body-ju

U `auth.py` je sada konverzija dodatno eksplicitna:

```python
return UserResponse.model_validate(create_user_model)
```

Ovaj kod potvrduje da se javni response pravi kroz bezbednu `UserResponse` schemu, a ne direktno kroz ceo `Users` model.

---

### Kako da proveriš da li je hash zaista sačuvan

Najprakticnije je da proveris bazu direktno kroz `sqlite3`. Ne moras da
kreiras posebnu Python skriptu.

```bash
cd /home/jole-pavlovic-dev/code/python-automation-lab/fast-api-portfolio/fast-api-course-my-work
sqlite3 todosapp.db
```

U SQLite promptu unesi:

```sql
.headers on
.mode column

SELECT id, email, username, hashed_password
FROM users;
```

Videces hash u koloni `hashed_password`, u formatu slicnom:

```text
$2b$12$...
```

Iz SQLite prompta izadji sa:

```sql
.quit
```

Za jednokratno generisanje novog hash-a, bez upisa korisnika u bazu, mozes
alternativno pokrenuti Python iz aktivnog terminala:

```bash
cd /home/jole-pavlovic-dev/code/python-automation-lab/fast-api-portfolio
source .venv/bin/activate
python
```

Zatim u Python promptu unesi:

```python
from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")
saved_hash = context.hash("TestPassword123")
print(saved_hash)
```

Iz Python prompta izadji sa:

```python
exit()
```

Za proveru postojeceg korisnika koristi SQLite upit, a ne API response. Hash
ne treba vracati klijentu kroz `UserResponse`.

Očekivana vrednost u `users.hashed_password` treba da izgleda slično:

```text
$2b$12$...
```

Ne treba da izgleda ovako:

```text
TestPassword123
```

Zaključak:

```text
hash nije vidljiv u response-u
	!=
hash nije kreiran
```

U tvom projektu hash se kreira, čuva i namerno skriva iz response-a.

---

## 7) Instalacija `Passlib` i `bcrypt`

Za ovaj kursni projekat koristi se dependency fajl:

```text
/home/jole-pavlovic-dev/code/python-automation-lab/fast-api-portfolio/fast-api-course-my-work/requirements.txt
```

dodate su runtime dependency stavke:

```text
passlib==1.7.4
bcrypt==4.0.1
```

One pripadaju `requirements.txt`, a ne `requirements-dev.txt`, zato što ih aplikacija koristi dok radi.

### Zašto baš ove verzije u ovoj lekciji

Ovo je kursna implementacija. `bcrypt==4.0.1` je dodat zbog kompatibilnosti sa kursnim `Passlib` primerom.

To nije tvrdnja da je ova kombinacija najbolji izbor za svaki novi projekat. Za novi projekat kasnije možemo razmotriti `pwdlib` i moderni backend, kao što je objašnjeno u:

```text
docs/fastapi/cheatsheets/passlib_vs_pwdlib_detaljno.md
```

### Važno: isti Python interpreter

Komanda treba da koristi isti interpreter kojim se pokrece Uvicorn:

```bash
python -m pip install -r requirements.txt
```

Bolje je koristiti:

```bash
python -m pip
```

nego samo:

```bash
pip
```

jer `python -m pip` jasnije pokazuje kom interpreteru instaliramo paket.

### PEP 668 problem

Na jednom sistemskom Python interpreteru instalacija je odbijena porukom:

```text
externally-managed-environment
```

To znači da distribucija štiti sistemski Python i ne dozvoljava direktan `pip install` u globalno okruženje.

Preporučeno rešenje je virtuelno okruženje:

```bash
cd /home/jole-pavlovic-dev/code/python-automation-lab/fast-api-portfolio
source .venv/bin/activate
python -m pip install -r fast-api-course-my-work/requirements.txt
```

Zatim iz tog aktiviranog okruženja pokretati aplikaciju:

```bash
cd fast-api-course-my-work
uvicorn TodoApp.main:app --reload --host 0.0.0.0 --port 8000
```

Provera interpretera:

```bash
which python
python -c "import sys; print(sys.executable)"
```

Provera paketa:

```bash
python -m pip show passlib bcrypt
```

Ne treba koristiti `--break-system-packages` kao prvo rešenje za ovaj projekat. Virtuelno okruženje je čistije i bezbednije.

---

## 7) Direktan test hashovanja

Pre testiranja endpointa možemo proveriti samo password sloj:

```python
from passlib.context import CryptContext

context = CryptContext(
	schemes=["bcrypt"],
	deprecated="auto",
)

plain_password = "TestPassword123"
saved_hash = context.hash(plain_password)

print(saved_hash)
print(context.verify(plain_password, saved_hash))
print(context.verify("WrongPassword123", saved_hash))
```

### Očekivani rezultat

Očekivani rezultat je sličan:

```text
$2b$12$...
True
False
```

Ovaj test proverava samo `Passlib` i `bcrypt`. Ne proverava FastAPI, Pydantic ni SQLAlchemy.

---

## 8) Test registracionog endpointa

Javna ruta se sastoji od:

```text
router prefix: /auth
endpoint path: /
public path:   /auth/
```

Primer `curl` poziva:

```bash
curl -X POST http://localhost:8000/auth/ \
  -H "Content-Type: application/json" \
  -d '{
	"email": "ana@example.com",
	"username": "ana",
	"first_name": "Ana",
	"last_name": "Jovanovic",
	"password": "TestPassword123",
	"role": "user"
  }'
```

Očekivani status je:

```text
201 Created
```

Očekivani response sadrži javna polja:

```json
{
  "id": 1,
  "email": "ana@example.com",
  "username": "ana",
  "first_name": "Ana",
  "last_name": "Jovanovic",
  "is_active": true,
  "role": "user"
}
```

Response ne treba da sadrži:

```text
password
hashed_password
```

### Rezultat izvršene provere

Nakon izmene endpoint je testiran sa jedinstvenim korisnikom i vratio je:

```text
HTTP 201 Created
```

To potvrđuje da su zajedno prošli:

1. Pydantic request validacija
2. `bcrypt_context.hash(...)`
3. Kreiranje `Users` ORM objekta
4. `db.add(...)`
5. `db.commit()`
6. `db.refresh(...)`
7. Pydantic response validacija

---

## 9) Kako čitati greške ubuduće

### `422 Unprocessable Entity`

Ova greška znači da request nije validan.

Prvo pogledati `detail` i `loc` u odgovoru sa servera. Taj odgovor vidite u JSON formatu u Swagger-u i on pokazuje gde je problem u requestu.

```text
body     -> request JSON/form data nije validan
query    -> query parametar nije validan
path     -> path parametar nije validan
response -> endpoint je vratio objekat koji ne odgovara response schema-i
```

---

### `500 Internal Server Error`

To obično znači da je izuzetak nastao u Python kodu ili dependency-ju. U ovom slučaju mogući uzroci su:

- `passlib` nije instaliran u interpreteru koji pokreće server
- nekompatibilna verzija `bcrypt`
- Database konekcija ili transakcija je pala
- Model ili schema nisu usklađeni

Kod `500` treba pročitati traceback iz terminala u kom radi Uvicorn. Swagger prikazuje samo opštu poruku `Internal Server Error`, dok terminal prikazuje stvarni uzrok.

---

### `201 Created`, ali korisnik nije u bazi

Ako endpoint vrati `201`, a podaci se kasnije ne vide, treba proveriti:

- da li je `db.commit()` pozvan
- da li aplikacija koristi očekivanu SQLite putanju
- da li se gleda ista baza iz drugog direktorijuma
- da li endpoint zaista koristi istu `SessionLocal` konfiguraciju

U ovom kodu `db.commit()` sada postoji, pa bi novi korisnik trebalo da ostane u `todosapp.db` bazi.

---

## 10) Zašto nije dovoljno samo vratiti ORM objekat

Ovaj kod:

```python
user_model = Users(...)
return user_model
```

radi samo u memoriji procesa. On ne znači automatski:

```text
INSERT u bazu
```

SQLAlchemy session mora da zna za objekat:

```python
db.add(user_model)
```

Transakcija mora biti potvrdjena:

```python
db.commit()
```

Vrednosti koje je baza generisala treba procitati nazad:

```python
db.refresh(user_model)
```

Zato je pun tok:

```text
request
	-> Pydantic validacija
		-> hash password-a
			-> Users ORM objekat
				-> db.add
					-> db.commit
						-> db.refresh
							-> UserResponse
```

---

## 11) Bezbednosna napomena o plain password-u

Plain password postoji samo privremeno:

```python
create_user_request.password
```

Koristi se kao ulaz u hash funkciju:

```python
bcrypt_context.hash(create_user_request.password)
```

U bazu se upisuje samo rezultat:

```python
hashed_password=...
```

Ne treba:

- Štampati plain password u terminal
- Čuvati ga u logovima
- Vraćati ga kroz response
- Čuvati ga u posebnoj koloni
- Stavljati ga u JWT payload

Hash takođe ne treba vraćati kroz javni response, iako nije isto što i plain password.

---

## 12) Šta je sada popravljeno, a šta još nije deo ove lekcije

### Popravljeno

- `auth.py` koristi postojeci `db_dependency`
- korisnik se dodaje u SQLAlchemy session
- transakcija se commit-uje
- generisani `id` se osvezava kroz `db.refresh`
- `passlib` i `bcrypt` su navedeni kao runtime dependency-ji
- registracioni endpoint je provereno vratio `201 Created`
- password se hash-uje pre upisa u bazu
- `hashed_password` nije deo `UserResponse` response-a

### Još nije implementirano

- Provera jedinstvenosti email-a i username-a pre insert-a
- Obrada `IntegrityError` iz baze
- Login endpoint
- `verify()` pri login-u
- JWT access token
- `get_current_user` dependency
- Authorization po `role`
- Filtriranje todo zapisa po `owner_id`
- Migracija sa `Passlib` na `pwdlib`

Ovi koraci pripadaju narednim lekcijama authentication oblasti.

---

## 13) Sledeći preporučeni koraci

1. Proveriti da li se novi korisnik vidi u SQLite bazi.
2. Dodati proveru duplikata pre `db.commit()` ili obraditi `IntegrityError`.
3. Implementirati login i `bcrypt_context.verify(...)`.
4. Dodati JWT tek kada autentifikacija korisnika radi.
5. Napisati fokusirane testove za hash, registraciju i pogresan request.
6. Tek posle kursne implementacije razmotriti `pwdlib` migraciju.

Kursni redosled sada ima smisla:

```text
hash pri registraciji
	-> čuvanje korisnika
		-> verify pri login-u
			-> JWT
				-> current user
					-> authorization
```

---

## Zaključak

Problem nije bio u tome što `bcrypt_context.hash()` ima pogrešan oblik. Glavni problem je bio što je endpoint pravio ORM objekat bez čuvanja u bazi, a zatim ga vraćao kao `UserResponse` koji zahteva generisani `id`.

Drugi problem je bio environment-specific: jedan sistemski Python nije imao instaliran `passlib` i odbio je instalaciju zbog PEP 668, dok je Uvicorn okruženje uspešno obradilo zahtev. Zbog toga pakete treba instalirati u istom virtuelnom okruženju iz kog se pokreće server.

Koncizni ispravan tok je:

```text
validan JSON request
	-> bcrypt_context.hash(password)
		-> Users objekat
			-> db.add
				-> db.commit
					-> db.refresh
						-> UserResponse sa id-em
```
