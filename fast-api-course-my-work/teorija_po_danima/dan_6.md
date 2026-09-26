# Dan 6 - Ispravka registracije korisnika i password hashovanja

## 1) Problem koji je prijavljen

Registracioni endpoint u `TodoApp/api/routes/auth.py` koristio je `Passlib`:

```python
hashed_password=bcrypt_context.hash(
	create_user_request.password
)
```

Ali `endpoint` je samo napravio `SQLAlchemy objekat` i vratio ga:

```python
create_user_model = Users(...)
return create_user_model
```

Objekat tada jos nije bio sačuvan u bazi. Zbog toga SQLAlchemy nije popunio njegov `id`.

Istovremeno, response `schema` zahteva:

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

Novi ORM objekat pre `commit()` poziva ima približno ovo stanje:

```text
id = None
email = "ana@example.com"
username = "ana"
hashed_password = "...hash..."
```

`UserResponse` ne može da pretvori `None` u obavezni `int`, pa FastAPI može prijaviti response validation `422`.

---

## 2) Zašto se hash ponekad nije izvršavao

HTTP `422` može nastati na dve različite tačke.

### 2.1 Request validation `422`

Pre nego što FastAPI pozove funkciju `create_users()`, Pydantic proverava `request body` prema modelu `CreateUserRequest`.

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

Ako nedostaje na primer `role`, FastAPI vraća `422` pre ulaska u endpoint. Tada se ovaj kod uopšte ne izvršava:

```python
bcrypt_context.hash(create_user_request.password)
```

U response JSON-u takva greška obično ima lokaciju sličnu:

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

`loc: ["body", ...]` znači da je problem u `request body`-ju.

---

### 2.2 Response validation `422`

Ako je lokacija slična:

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

Onda je endpoint već radio, ali vraćeni `Users` objekat nema generisan `id`. U tom slučaju password hash je mogao već biti napravljen, ali korisnik nije pravilno sačuvan i osvežen iz baze.

Pravilo za dijagnozu:

```text
body    -> greška pre endpoint funkcije
response -> greška nakon endpoint funkcije
```

---

## 3) Šta je promenjeno u `auth.py`

Postojeći projekat već ima centralizovanu DB dependency logiku u:

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

Zato `auth.py` ne treba da pravi novu sesiju, već koristi postojeći dependency:

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

Posle kreiranja ORM objekta dodata su tri važna koraka:

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

## 4) Značenje `db.add`, `db.commit` i `db.refresh`

### `db.add()`

```python
db.add(create_user_model)
```

Dodaje ORM objekat u SQLAlchemy session. Objekat je sada poznat session-u i spreman za insert, ali transakcija još nije potvrdena.

Mentalni model:

```text
Python objekat
	-> db.add()
		-> SQLAlchemy session sadaprati objekat,
		-> ali transakcija još nije potvrđena
```

---

### `db.commit()`

```python
db.commit()
```

Potvrđuje transakciju (pod `transakcijom` se podrazumevaju `sve promene u bazi`) i šalje INSERT bazi. Pod tim uslovima, promene postaju trajne.

`INSERT` je SQL komanda koja se koristi za dodavanje novih redova u tabelu. U kontekstu SQLAlchemy-ja, `db.add()` priprema objekat za insert, a `db.commit()` izvršava stvarni `INSERT` u bazu.

Pojednostavljeno:

```text
db.add(user)
	priprema objekat za insert

db.commit()
	trajno potvrđuje promenu u bazi
```

Posle uspešnog commit-a SQLite može generisati primarni ključ `id`.

---

### `db.refresh()`

```python
db.refresh(create_user_model)
```

Ponovo čita objekat iz baze i osvežava njegove vrednosti u Python memoriji. To je važno zato što se nakon `insert`-a (`db.commit()`) mogu popuniti:

- `id` koji generiše baza za primarni ključ tabele iz SQLite-a (ili druge baze). U tom trenutku, Python objekat dobija ažuriranu vrednost `id`.

- database `default` vrednosti iz baze (npr. timestamp kolone sa `DEFAULT CURRENT_TIMESTAMP`). U tom trenutku, Python objekat dobija ažurirane vrednosti za te kolone.

- Druge vrednosti koje dolaze iz baze kao rezultat `trigera` ili `izračunatih kolona`. U njih spadaju kolone čije vrednosti se izračunavaju ili postavljaju automatski od strane baze (npr. kolone sa `GENERATED ALWAYS AS` ili trigera (pod `trigger`-om se podrazumeva SQL kod koji postavlja vrednosti u kolone)).

Posle `db.refresh()`-a objekat je spreman za `UserResponse`:

```text
id = 1
email = "ana@example.com"
username = "ana"
is_active = True
role = "user"
```

---

## 5) Zašto `UserResponse` sada može da radi

Schema koristi:

```python
model_config = ConfigDict(from_attributes=True)
```

To dozvoljava Pydantic-u da čita atribute iz SQLAlchemy objekta, umesto da očekuje običan dictionary. Primer:

```python
user = db.query(User).first() # Uzimamo prvi User objekat iz baze (ako postoji)
user_response = UserResponse.from_orm(user) # Kreiramo UserResponse objekat iz ORM objekta, koji sadrži samo javno vidljive atribute

print(user_response) # Ispisujemo UserResponse objekat da vidimo kako izgleda

# SQL ekvivalent koji bi vratio iste podatke kao ORM objekat
SELECT id, email, username, first_name, last_name, is_active, role
FROM users
LIMIT 1;

# LIMIT 1; je SQL ekvivalent za uzimanje prvog reda iz tabele
```

Ali `from_attributes=True` ne može da reši problem nedostajućeg `id`. Ono samo govori Pydantic-u gde da čita vrednosti.

Potrebna su oba uslova:

```text
from_attributes=True
	omogućava čitanje ORM atributa

db.add + db.commit + db.refresh
	obezbeđuju da ORM objekat ima generisan id
```

Takodje, `UserResponse` namerno nema:

```python
password
hashed_password
```

Hash se čuva interno radi kasnijeg login-a, ali se ne vraća javnom API klijentu.

---

## 6) Zašto kurs prikazuje hash, a tvoj response ne

U kursnom prikazu možeš videti vrednost sličnu:

```text
$2b$12$...dugacak_hash...
```

To ne znači da se hash kod tebe nije napravio. U tvom trenutnom kodu hash se pravi ovde:

```python
hashed_password=bcrypt_context.hash(
	create_user_request.password
)
```

Razlika je u `UserResponse` schemi. Tvoja schema namerno sadrži:

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

Ona ne sadrži:

```python
hashed_password: str
```

Zato FastAPI response validacija izbacuje `hashed_password` iz javnog response body-ja. Hash se i dalje nalazi u SQLAlchemy objektu i čuva se u koloni `users.hashed_password`, ali nije poslat klijentu.

### Dva razlicita prikaza

Kursni demo može prikazati hash ako:

- vraća ceo ORM objekat bez ograničene response schema-e
- koristi response schemu koja sadrži `hashed_password`
- štampa ORM objekat ili čita bazu direktno

Tvoj API koristi bezbedniji oblik:

```text
Users ORM objekat
	-> sadrži hashed_password interno u ORM objektu
	-> ORM objekat se nalazi u models.py fajlu (npr. model/klasa `Users`)

UserResponse
	-> namerno ne sadrži hashed_password

HTTP response
	-> ne prikazuje hash
```

Zato je normalno da u Swagger response body-ju ne vidiš hash, ali da ga vidiš ako proveris SQLite bazu ili interno ispisivanje objekta tokom učenja.

---

### Zašto ne treba dodati hash u `UserResponse`

Tehnički bi moglo:

```python
class UserResponse(BaseModel):
	...
	hashed_password: str
```

Ali to nije dobro za stvarni API. Hash nije plaintext password, ali je i dalje osetljiv interni autentifikacioni podatak. Ako napadač dobije hash, može pokušavati offline napade na password.

Zato je ispravno da `hash`:

- postoji u bazi (`users.hashed_password`)
- postoji u internom ORM objektu (`Users.hashed_password` u models.py, klasa `Users`)
- koristi se kasnije za `verify()`
- ne postoji u javnom response body-ju

U `auth.py` je sada konverzija dodatno eksplicitna:

```python
return UserResponse.model_validate(create_user_model)
```

Ovaj kod potvrđuje da se javni response pravi kroz bezbednu `UserResponse` schemu, a ne direktno kroz ceo `Users` model.

---

### Kako da proveriš da li je hash zaista sačuvan

Najprakticnije je da proveriš bazu direktno kroz `sqlite3`. Ne moraš da
kreiraš posebnu Python skriptu.

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

Videćeš hash u koloni `hashed_password`, u formatu sličnom:

```text
$2b$12$...
```

Iz SQLite prompta izađi sa:

```sql
.quit
```

Za jednokratno generisanje novog hash-a, bez upisa korisnika u bazu, možeš
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

Iz Python prompta izađi sa:

```python
exit()
```

Za proveru postojećeg korisnika koristi SQLite upit, a ne API response. Hash
ne treba vraćati klijentu kroz `UserResponse`.

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

---

## Pitanje 1

PITANJE: Kada kažemo `ORM objekat` tu mislimo na instancu `klase/modela` npr. class Users

Buni me razlika između `tabele users` i `modela Users`. Shvatio sam da kada koristim `db.query` koristim `model`. (npr. Users ili Todos). Kada koristim ime same liste npr. users ili todos?

---

## Pitanje 4

PITANJE: Kada pokrenem login endpoint, zašto dobijam grešku sa `grant_type` poljem i kako treba da izgleda trenutni `auth.py` login tok?

### Odgovor

Greška sa porukom:

```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["body", "grant_type"],
      "msg": "String should match pattern 'password'"
    }
  ]
}
```

znači da je login forma poslata sa praznim ili pogrešnim `grant_type` poljem. To nije greška u bcrypt hash-u. Greška nastaje pre ulaska u funkciju `login_for_access_token()`.

`OAuth2PasswordRequestForm` očekuje podatke kao formu, a ne kao JSON objekat. Za OAuth2 password flow potrebno je poslati:

```text
grant_type=password
username=ana
password=TestPassword123
```

Pošto router ima prefiks:

```python
router = APIRouter(
	prefix="/auth",
	tags=["auth"],
)
```

a login endpoint ima putanju:

```python
@router.post("/token")
```

konačna javna ruta je:

```text
POST /auth/token
```

`/auth` dolazi iz prefiksa routera, a `/token` iz dekoratora endpointa. FastAPI ih spaja u `/auth/token`.

### Zašto koristimo `OAuth2PasswordRequestForm`

Ovaj dependency čita standardna OAuth2 form-data polja:

```python
form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
```

Posle toga vrednosti čitamo preko atributa:

```python
form_data.username
form_data.password
form_data.grant_type
```

U ovoj fazi `username` znači vrednost iz kolone `Users.username`. To je odvojeno od email-a, iako bi aplikacija kasnije mogla biti dizajnirana da korisnike prijavljuje email adresom.

### Zašto se koristi `bcrypt_context.verify()`

Pri registraciji se plain password pretvara u hash:

```python
hashed_password=bcrypt_context.hash(
	create_user_request.password
)
```

Pri login-u ne hashujemo ponovo lozinku i ne poredimo dva hash-a tekstualno. Bcrypt koristi salt, pa bi dva hashovanja iste lozinke mogla proizvesti različite rezultate.

Umesto toga koristimo:

```python
bcrypt_context.verify(plain_password, saved_hash)
```

U našem endpointu to znači:

```python
bcrypt_context.verify(
	form_data.password,
	user.hashed_password,
)
```

`verify()` uzima plain password koji je korisnik upravo poslao, čita algoritam i salt iz sačuvanog hash-a i proverava da li se vrednosti poklapaju.

### Pomoćna funkcija `authenticate_user`

Login logiku izdvajamo u posebnu funkciju:

```python
def authenticate_user(username: str, password: str, db: db_dependency):
	user = db.query(Users).filter(Users.username == username).first()

	if user is None:
		return False

	hashed_password = cast(str, getattr(user, "hashed_password"))
	is_active = cast(bool, getattr(user, "is_active"))

	if not bcrypt_context.verify(password, hashed_password):
		return False

	if not is_active:
		return False

	return user
```

Tok funkcije je:

```text
username
	-> pretraga Users modela
		-> tabela users
			-> pronalaženje jednog ORM objekta
				-> provera password-a prema hashed_password
					-> provera is_active
```

Ako je sve uspešno, funkcija vraća jedan `Users` ORM objekat. Ako nešto nije uspešno, vraća `False`.

### Zašto se za pogrešne podatke vraća `401`

Login endpoint proverava rezultat autentifikacije:

```python
if not authenticated_user:
	raise HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate user",
		headers={"WWW-Authenticate": "Bearer"},
	)
```

Status `401 Unauthorized` znači da korisnik nije uspešno autentifikovan. Ista poruka se koristi za nepostojeći username i pogrešan password kako API ne bi otkrivao da li određeni username postoji.

### Trenutni privremeni odgovor

Dok JWT još nije implementiran, endpoint vraća samo oblik odgovora koji liči na OAuth2 token odgovor:

```python
return {
	"access_token": "token",
	"token_type": "bearer",
}
```

Vrednost `"token"` je privremeni placeholder. Ona još nije pravi JWT i ne treba je koristiti za zaštitu todo ruta. Pravi sled rada je:

```text
registracija
	-> hash password-a
		-> login
			-> verify password-a
				-> JWT access token
					-> current user
						-> zaštita ruta
```

### Testiranje kroz `curl`

Login zahtev se šalje kao `application/x-www-form-urlencoded`:

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=ana&password=TestPassword123"
```

Uspešan privremeni odgovor je:

```json
{
  "access_token": "token",
  "token_type": "bearer"
}
```

Pogrešan password ili username daju:

```json
{
  "detail": "Could not validate user"
}
```

sa HTTP statusom:

```text
401 Unauthorized
```

### Važna dopuna ranijeg dela dokumenta

Raniji deo ovog dokumenta navodi da login i `verify()` još nisu implementirani. Nakon dodavanja login toka to više nije potpuno tačno. Trenutno su implementirani:

- čitanje OAuth2 login forme
- pretraga korisnika po `username`
- provera password-a pomoću `bcrypt_context.verify()`
- provera `is_active`
- vraćanje `401` za neuspešnu autentifikaciju
- privremeni odgovor sa `access_token` i `token_type`

Još nisu implementirani:

- stvarno kreiranje JWT tokena
- `get_current_user` dependency
- proveravanje Bearer tokena
- zaštita todo ruta
- autorizacija po `role`

Zato je trenutni login edukativno funkcionalan za proveru identiteta, ali još nije kompletan sistem token-based autentifikacije.

---

## Odgovor 1

ODGOVOR: Kada govorimo o `ORM objektu`, mislimo na instancu klase/modela, npr. `Users`. Tabela `users` je fizička struktura u bazi podataka, dok je model `Users` Python klasa koja mapira tu tabelu. Kada koristimo `db.query`, koristimo model (klasu), a kada koristimo ime same liste, npr. `users`, to je obično rezultat SQL upita ili lista instanci modela.

### Detaljno objašnjenje

Da, tačno: **ORM objekat** je instanca ORM modela, odnosno objekat kreiran iz klase kao što su `Users` ili `Todos`.

Najlakše je razlikovati četiri pojma:

```text
Users       -> ORM model, Python klasa
users       -> tabela u SQLite bazi
user        -> jedan ORM objekat, instanca klase Users
users       -> Python lista ORM objekata
```

---

#### 1. ORM model: `Users`

U `models.py` imaš približno:

```python
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String)
    username = Column(String)
```

`Users` je Python klasa/ORM model koja opisuje tabelu `users`.

Model `Users` mapira (`ORM` - Object Relational Mapping) SQL tabelu `users` u Python objekat tako da svaka instanca klase `Users` predstavlja jedan red u tabeli `users`. Na taj način ORM omogućava rad sa bazom podataka koristeći Python objekte umesto direktnog pisanja SQL upita.

Tabela `users` u bazi i model/klasa `Users` u Pythonu su povezani preko ORM-a (mapiranja). Zbog toga u `models.py` definišemo model i ime tabele. To omogućava SQLAlchemy-ju da automatski prevodi operacije nad modelom `Users` u SQL upite nad tabelom `users`.

```text
Python model:  Users
SQL tabela:    users
```

Slično:

```text
Python model:  Todos
SQL tabela:    todos
```

---

#### 2. `db.query(Users)`

Kada napišeš:

```python
user = db.query(Users).first()
```

`Users` je ORM model, a `user` je instanca tog modela.

`db` je SQLAlchemy sesija koja se koristi za interakciju sa bazom.

`db.query` je metoda SQLAlchemy sesije koja se koristi za kreiranje upita prema bazi koristeći ORM modele. Sinonim za SQL `SELECT` upit.

`db.query(Users)` kreira upit prema tabeli `users` koristeći ORM model `Users`.

Rezultat `db.query(Users)` je lista instanci ORM modela `Users`, tj. lista objekata `users` (Python lista ORM objekata).

> Pretraži tabelu `users` koristeći ORM model `Users`.

```python
users = db.query(Users).all()
for user in users:
    print(user.email)
    print(user.username)
    print(user.id)
```

Rezultat je jedan ORM objekat (instanca klase `Users`):

```python
user.email
user.username
user.id
```

Promenljiva `user` predstavlja jedan red iz baze, ali kao Python objekat.

```text
jedan red iz users tabele
        |
        v
jedna instanca klase Users
```

---

#### 3. `db.query(Users).all()`

Kada napišeš:

```python
users = db.query(Users).all()
```

`users` je obična Python lista koja sadrži više ORM objekata:

```python
[
    Users(...),
    Users(...),
    Users(...),
]
```

Možeš je koristiti ovako:

```python
for user in users:
    print(user.email)
```

Dakle:

```text
Users       -> model/klasa
users       -> lista rezultata
user        -> jedan rezultat, jedna instanca
```

---

#### 4. Važna razlika kod kolona

Ovo:

```python
Users.email
```

koristiš u query uslovu:

```python
user = (
    db.query(Users)
    .filter(Users.email == "ana@example.com")
    .first()
)
```

`Users.email` ovde predstavlja ORM kolonu/model atribut koji SQLAlchemy prevodi u SQL.

Ali ovo:

```python
user.email
```

čita stvarnu vrednost iz pronađenog objekta:

```python
print(user.email)
```

Poređenje:

```text
Users.email       -> model/kolona, koristi se za query
user.email        -> konkretna vrednost jednog korisnika
```

---

#### Kompletan primer

```python
users = db.query(Users).all()

for user in users:
    print(user.id)
    print(user.email)
```

Ovde:

- `Users` je ORM model
- `users` je Python lista
- `user` je jedna instanca klase `Users`
- `user.email` je konkretan email iz jednog reda baze
- tabela u SQLite-u se zove `users`

Isto važi za Todo model:

```python
todos = db.query(Todos).all()

for todo in todos:
    print(todo.title)
```

`todos` nije tabela. To je samo naziv Python promenljive koja sadrži listu ORM objekata vraćenih iz tabele `todos`.

Slično kao kod `Users` modela:

```text
Todos       -> model/klasa
todos       -> lista rezultata
todo        -> jedan rezultat, jedna instanca
```

---

## Pitanje 2

PITANJE: Da li je u delu koda koji definiše endpoint ->

```python
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_users(
    create_user_request: CreateUserRequest,
    db: db_dependency,
) -> UserResponse:
```

dovoljno samo da funkcija vraća `UserResponse` bez `response_model=UserResponse` i da li je greška ako stavim oba kao što sam do sada stavljao?

---

## Odgovor 2

ODGOVOR: U FastAPI-ju, `response_model` u dekoratoru endpoint-a definiše kako će izlaz biti serijalizovan i validiran. Povratna vrednost funkcije može biti tipa `UserResponse`, ali `response_model` je ono što FastAPI koristi za generisanje OpenAPI specifikacije i validaciju izlaza. Dakle, nije greška imati oba, i često je preporučljivo imati oba radi jasnoće i sigurnosti.

### Detaljno objašnjenje

Updated todo list

Nije greška da koristiš oba. Ovo je validan FastAPI kod:

```python
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_users(
    create_user_request: CreateUserRequest,
    db: db_dependency,
) -> UserResponse:
```

Ali oba dela imaju različitu ulogu.

#### `-> UserResponse`

Ovo je Python type hint:

```python
async def create_users(...) -> UserResponse:
```

Govori:

> Očekujemo da funkcija vrati `UserResponse`.

Koristan je za:

- čitanje koda
- Pylance/type checker
- autocomplete
- dokumentovanje namere

---

#### `response_model=UserResponse`

Ovo je FastAPI konfiguracija:

```python
@router.post(..., response_model=UserResponse)
```

Govori FastAPI-ju:

> Validiraj i serijalizuj rezultat endpointa kroz `UserResponse`.

To utiče na:

- validaciju response-a
- automatsko uklanjanje polja kao što je `hashed_password`
- OpenAPI/Swagger dokumentaciju
- prikaz response schema-e

---

#### Da li možeš ukloniti `response_model`?

Da, možeš:

```python
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_users(
    create_user_request: CreateUserRequest,
    db: db_dependency,
) -> UserResponse:
```

FastAPI će uglavnom koristiti `UserResponse` iz return annotation-a kao response model.

---

#### Da li možeš ukloniti `-> UserResponse`?

Takođe možeš:

```python
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_users(
    create_user_request: CreateUserRequest,
    db: db_dependency,
):
```

I ovo će raditi, jer `response_model` govori FastAPI-ju koji model treba koristiti.

---

#### Šta je najbolje u tvom slučaju?

Pošto si početnik i učiš FastAPI, slobodno ostavi oba:

```python
response_model=UserResponse
```

jasno pokazuje FastAPI ponašanje, a:

```python
-> UserResponse
```

jasno pokazuje očekivani Python tip.

Nisu konfliktni jer oba koriste isti model. Samo bi predstavljalo problem kada bi bili različiti, na primer:

```python
@router.post("/", response_model=UserResponse)
async def create_users(...) -> SomeOtherModel:
```

Tada bi FastAPI response obrađivao kao `UserResponse`, dok bi type hint tvrdio da funkcija vraća drugi model.

---

## Pitanje 3

PITANJE: Da li će činjenica da u `auth.py imam:

```python
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
```

Bitno menja situaciju da sada ne mogu imati putanju `"/token"` kao u kursu? Meni se automatski pojavljuje `"/auth/token/` zbog definisanja prefiksa rutera zar ne?

---

## Odgovor 3

ODGOVOR: Da, činjenica da u `auth.py` imaš definisan `prefix="/auth"` znači da će sve rute unutar tog rutera automatski imati prefiks `/auth`. Dakle, ruta `"/token"` će zapravo biti dostupna kao `"/auth/token"`. To ne menja funkcionalnost, ali menja URL na kojem je endpoint dostupan.

### Detaljno objašnjenje

Da, tačno si razumeo.

Pošto imaš:

```python
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
```

i endpoint:

```python
@router.post("/token")
```

FastAPI spaja putanje:

```text
prefix       /auth
endpoint     /token
--------------------
konačna ruta /auth/token
```

Zato koristiš:

```text
POST /auth/token
```

a ne:

```text
POST /token
```

To nije greška. `prefix="/auth"` samo grupiše authentication rute:

```text
POST /auth/          -> registracija
POST /auth/token     -> login
```

Kurs verovatno nema definisan prefiks, pa njegov:

```python
@router.post("/token")
```

daje direktno:

```text
POST /token
```

Ako želiš baš putanju `/token`, imaš dve mogućnosti.

**Opcija 1: ukloniš prefiks sa tog routera**

```python
router = APIRouter(tags=["auth"])
```

Tada bi i registracija i login bili:

```text
POST /
POST /token
```

**Opcija 2: koristiš poseban router za token**

```python
auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

token_router = APIRouter(
    tags=["auth"],
)

@token_router.post("/token")
async def login_for_access_token(...):
    return "token"
```

Ali za tvoj projekat je urednije da ostane:

```text
POST /auth/
POST /auth/token
```

Prefiks jasno pokazuje da obe rute pripadaju authentication delu aplikacije. U Swagger-u ćeš zato videti `/auth/token`.

---

## Pitanje 4

PITANJE:

---

## Pitanje 4 - Login forma, `grant_type` i provera password-a

PITANJE: Zašto login endpoint prijavljuje grešku `422` da `grant_type` mora da odgovara paternu `password` i kako funkcioniše trenutni login kod?

---

## Odgovor 4

ODGOVOR: Trenutni kod je vraćen na preporučeni kursni pristup:
`OAuth2PasswordRequestForm`. To je standardni OAuth2 password login tok u
FastAPI-ju. U ovom režimu Swagger može prikazati dodatna polja kao što su
`scope`, `client_id` i `client_secret`.

### Kako sada radi `login_for_access_token` (preporučeno rešenje)

```python
@router.post("/token")
async def login_for_access_token(
		form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
		db: db_dependency,
):
```

Bitna polja za lekciju 10 su:

- `form_data.username`
- `form_data.password`

`/auth` prefiks ostaje isti, pa je javna ruta:

```text
POST /auth/token
```

### Zašto se dešava `422` za `grant_type`

Ako Swagger pošalje prazan `grant_type`, možeš dobiti:

```text
String should match pattern 'password'
```

To je greška formata forme, ne greška u hash proveri.

Za standardni OAuth2 password flow koristi:

```text
grant_type=password
```

### Bitna razlika: `422` vs `401`

- `422` znači da forma nije validna (npr. prazan/pogrešan `grant_type`).
- `401` znači da je forma validna, ali `username/password` nisu ispravni.

Ako dobiješ `401`, endpoint radi i stigao je do autentifikacije.

### Obavezni praktični korak

Pre login testa moraš prvo napraviti korisnika i koristiti isti par
`username/password`:

1. `POST /auth/` registracija
2. `POST /auth/token` login sa istim vrednostima

Ako promeniš jedno slovo u username ili password, dobićeš `401`.

### Primer testova

Registracija:

```bash
curl -X POST http://localhost:8000/auth/ \
	-H "Content-Type: application/json" \
	-d '{
		"email": "jovana@example.com",
		"username": "jovana",
		"first_name": "Jovana",
		"last_name": "Test",
		"password": "Test123",
		"role": "user"
	}'
```

Login (preporučeno, standardno):

```bash
curl -X POST http://localhost:8000/auth/token \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-d "grant_type=password&username=jovana&password=Test123"
```

Uspešan odgovor je trenutno privremen:

```json
{
  "access_token": "token",
  "token_type": "bearer"
}
```

### Workaround varijanta (samo ako Swagger i dalje šalje prazan `grant_type`)

Ovo nije glavno rešenje, već privremeni workaround:

```python
@router.post("/token")
async def login_for_access_token(
		username: Annotated[str, Form()],
		password: Annotated[str, Form()],
		db: db_dependency,
		grant_type: Annotated[str | None, Form()] = None,
):
```

U toj varijanti možeš tretirati prazan `grant_type` kao validan password flow.
Prednost je praktičnost u Swagger-u; mana je što odstupa od kursnog i
standardnog OAuth2 pristupa.

Zaključak za tvoj projekat:

- preporučeno: `OAuth2PasswordRequestForm`
- workaround: eksplicitna `Form` polja samo kada je potrebno

JWT i `get_current_user` ostaju sledeći korak.

---

## Dopuna - Zašto je bio `500` na registraciji i kako je rešeno

Ako pokušamo da registrujemo korisnika sa već postojećim `email` ili
`username`, baza baca `IntegrityError` zbog `unique` ograničenja na tabeli
`users`.

Pre izmene, taj exception nije bio obrađen, pa je API vraćao:

```text
500 Internal Server Error
```

To nije idealno, jer je duplikat korisnika očekivana poslovna greška,
ne neočekivani pad servera.

### Rešenje u `auth.py`

Dodate su dve zaštite u registracionom toku:

1. pre-provera da li već postoji korisnik sa istim `email` ili `username`
2. `try/except IntegrityError` oko `db.commit()` uz `db.rollback()`

Ako je korisnik duplikat, endpoint sada vraća:

```text
400 Bad Request
```

sa porukom:

```json
{
  "detail": "User with this email or username already exists"
}
```

### Zašto su potrebna oba koraka

- Pre-provera daje lepšu i bržu poruku za najčešći slučaj.
- `IntegrityError` obrada je zaštita od race-condition situacije
  (npr. dva zahteva stignu skoro istovremeno).

---

### Praktično tumačenje status kodova kod registracije

- `201 Created` -> korisnik je uspešno kreiran
- `400 Bad Request` -> duplikat `email` ili `username`
- `422 Unprocessable Entity` -> request format/validacija nije ispravna
- `500 Internal Server Error` -> neočekivana greška (ne bi trebalo da bude
  rezultat normalnog duplikata)

---

## Swagger login checklist (brzi podsetnik)

Kada testiraš login na `POST /auth/token` u Swagger-u, koristi sledeći redosled:

1. Prvo kreiraj korisnika na `POST /auth/`.
2. Na `POST /auth/token` unesi isti `username` i isti `password`.
3. U polje `grant_type` upiši tačno: `password`.
4. Polja `scope`, `client_id` i `client_secret` možeš ostaviti prazna u ovoj fazi.

Kako čitati odgovor:

- `422` -> forma nije validna (najčešće `grant_type` nije `password`).
- `401` -> forma je validna, ali username/password ne odgovaraju.
- `200` + `access_token` -> login je uspešan.

---
