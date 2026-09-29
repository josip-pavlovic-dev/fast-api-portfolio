# Dan 10 - Detaljna analiza `schemas.py` (liniju po liniju)

Ovaj dokument je fokusiran na `TodoApp/schemas.py` i služi kao nastavak analize koju smo radili za `config.py` i `security.py`.

Cilj:

1. Da razumeš svaku liniju u `schemas.py`.
2. Da razlikuješ request i response šeme.
3. Da razumeš kako `Token` schema učestvuje u JWT flow-u.
4. Da teorijski razjasnimo obeleženi deo iz `dan_9.md` koji je povezan sa `schemas.py`.

---

## Pitanje 1

PITANJE: Potrebna mi je detaljna analiza liniju po liniju za `schemas.py`, isto kao za `config.py` i `security.py`.

---

## Odgovor 1

ODGOVOR: U nastavku je potpuna analiza `TodoApp/schemas.py`.

### Ceo kod (referenca)

```python
from pydantic import BaseModel, ConfigDict, Field

class CreateTodoRequest(BaseModel):
	title: str = Field(
		min_length=3, description="Naslov todo zadatka mora imati najmanje 3 karaktera"
	)
	description: str = Field(
		min_length=3, description="Opis todo zadatka mora imati najmanje 3 karaktera"
	)
	priority: int = Field(
		gt=0,
		lt=6,
		description="Prioritet todo zadatka mora biti veći od 0 i manji od 6",
	)
	complete: bool = Field(description="Status završenosti todo zadatka")

class TodoResponse(BaseModel):
	id: int
	title: str
	description: str
	priority: int
	complete: bool

	model_config = ConfigDict(from_attributes=True)

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

	model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
	access_token: str
	token_type: str
```

---

### Linija po linija objašnjenje

#### Linija 1: `from pydantic import BaseModel, ConfigDict, Field`

Uvozi tri ključna elementa iz Pydantic-a:

1. `BaseModel`:
   Osnova za sve šeme. Svaka klasa koja nasleđuje `BaseModel` dobija validaciju, parsing i serializaciju.
2. `ConfigDict`:
   Pydantic v2 način da podesiš ponašanje modela (`model_config`).
3. `Field`:
   Omogućava dodatna pravila i metapodatke za polja (npr. `min_length`, `gt`, `lt`, `description`).

---

#### Linije 4-16: `class CreateTodoRequest(BaseModel):`

Ovo je request schema za kreiranje todo stavke. Koristi se kao ulazni model u endpoint-u (body).

#### Linija 5-7: `title: str = Field(min_length=3, ...)`

`title` mora biti string dužine najmanje 3 karaktera.

Ako klijent pošalje kraći naslov, FastAPI/Pydantic vraća 422 Validation Error pre ulaska u endpoint logiku.

#### Linija 8-10: `description: str = Field(min_length=3, ...)`

Isto pravilo kao za `title`: minimum 3 karaktera.

#### Linije 11-15: `priority: int = Field(gt=0, lt=6, ...)`

`priority` mora biti ceo broj strogo između 0 i 6, praktično 1 do 5.

1. `gt=0` znači greater than 0.
2. `lt=6` znači less than 6.

#### Linija 16: `complete: bool = Field(...)`

Polje statusa završetka zadatka (`True/False`).

---

#### Linije 19-27: `class TodoResponse(BaseModel):`

Response schema za vraćanje todo objekta klijentu.

Razlika u odnosu na request:

1. Ovde postoji `id`, jer ga uglavnom dodeljuje baza.
2. Ovo je izlazni ugovor (response contract), ne ulazni.

#### Linija 26: `model_config = ConfigDict(from_attributes=True)`

Ključna postavka za ORM rad:

1. Omogućava da Pydantic model čita podatke iz objekata sa atributima (npr. SQLAlchemy ORM instanca), ne samo iz dict-a.
2. Praktično znači da možeš vratiti ORM objekat, a FastAPI/Pydantic ga mapira u `TodoResponse`.

---

#### Linije 30-36: `class CreateUserRequest(BaseModel):`

Request schema za kreiranje korisnika.

Polja:

1. `email: str`
2. `username: str`
3. `first_name: str`
4. `last_name: str`
5. `password: str`
6. `role: str`

Napomena:

Trenutno su to osnovni tipovi bez dodatnih validacija (`min_length`, regex, `EmailStr`). To je funkcionalno, ali možeš kasnije pojačati pravila kada budeš radio hardening.

---

#### Linije 39-48: `class UserResponse(BaseModel):`

Response schema za korisnika.

Polja su slična korisničkom modelu, ali bez `password` (što je ispravno i bezbedno).

#### Linija 47: `model_config = ConfigDict(from_attributes=True)`

Ista svrha kao kod `TodoResponse`: olakšava mapiranje iz ORM objekata.

---

#### Linije 51-53: `class Token(BaseModel):`

Schema za odgovor login endpoint-a:

1. `access_token: str` -> stvarni JWT string.
2. `token_type: str` -> najčešće `bearer`.

Ovo je API ugovor između backend-a i klijenta za auth odgovor.

---

## Pitanje 2 (vezano za obeleženi deo iz `dan_9.md`)

PITANJE: Kako teorijski pravilno razumeti `payload` deo i vezu sa `schemas.py`?

---

## Odgovor 2

ODGOVOR:

1. `schemas.py` ne definiše JWT payload direktno.
2. JWT payload se formira u `security.py` (u funkciji za token `encode`).
3. `Token` schema u `schemas.py` definiše samo izlazni format odgovora (`access_token`, `token_type`).

Drugim rečima:

1. `security.py` određuje sadržaj claim-ova (`sub`, `username`, `exp`).
2. `schemas.py` određuje kako taj rezultat izgleda prema klijentu tj. u response-u.

Važno bezbednosno pravilo:

JWT payload nije enkriptovan, već potpisan. Zato u claim-ove ne ide osetljiv sadržaj (lozinke, tajni ključevi i slično).

---

## Mini rezime (najvažnije za pamćenje)

1. Request i response šeme odvoji logički.
2. Validacija u request modelima štedi kod u endpoint-ima.
3. `from_attributes=True` je ključan za lep ORM -> schema tok.
4. `Token` schema je response contract, a ne mesto gde se pravi payload.

---

## Pitanje 3

PITANJE: Potrebno je detaljno objašnjenje liniju po liniju za `auth.py`.

---

## Odgovor 3

ODGOVOR: U nastavku je detaljna analiza fajla `TodoApp/api/routes/auth.py`.

### Ceo kod (referenca)

```python
from datetime import timedelta
from typing import Annotated

# from typing import cast  # Stari workaround je ostavljen zakomentarisan ispod.
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from ...core.config import settings
from ...core.security import create_access_token
from ...db.session import db_dependency
from ...models import Users
from ...schemas import CreateUserRequest, Token, UserResponse

router = APIRouter(
	prefix="/auth",
	tags=["auth"],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(username: str, password: str, db: db_dependency):
	"""Vraća korisnika ako username postoji i password odgovara hash-u."""
	user = db.query(Users).filter(Users.username == username).first()
	if user is None:
		return False

	hashed_password = getattr(user, "hashed_password", None)
	if not isinstance(hashed_password, str):
		return False

	if not bcrypt_context.verify(password, hashed_password):
		return False

	is_active = getattr(user, "is_active", None)
	if not isinstance(is_active, bool):
		return False
	if not is_active:
		return False

	return user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_users(
	create_user_request: CreateUserRequest,
	db: db_dependency,
) -> UserResponse:
	existing_user = (
		db.query(Users)
		.filter(
			(Users.email == create_user_request.email)
			| (Users.username == create_user_request.username)
		)
		.first()
	)
	if existing_user:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="User with this email or username already exists",
		)

	create_user_model = Users(
		email=create_user_request.email,
		username=create_user_request.username,
		first_name=create_user_request.first_name,
		last_name=create_user_request.last_name,
		role=create_user_request.role,
		hashed_password=bcrypt_context.hash(create_user_request.password),
		is_active=True,
	)

	db.add(create_user_model)
	try:
		db.commit()
	except IntegrityError:
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="User with this email or username already exists",
		)
	db.refresh(create_user_model)

	return create_user_model


@router.post("/token", response_model=Token)
async def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
	db: db_dependency,
):
	authenticated_user = authenticate_user(
		form_data.username,
		form_data.password,
		db,
	)
	if not authenticated_user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate user",
			headers={"WWW-Authenticate": "Bearer"},
		)

	username = getattr(authenticated_user, "username", None)
	user_id = getattr(authenticated_user, "id", None)
	if not isinstance(username, str) or not isinstance(user_id, int):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate user",
			headers={"WWW-Authenticate": "Bearer"},
		)

	access_token = create_access_token(
		username=username,
		user_id=user_id,
		expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
	)

	return Token(access_token=access_token, token_type="bearer")
```

---

### Linija po linija objašnjenje

#### Linija 1: `from datetime import timedelta`

Uvozi `timedelta` da bi se definisalo trajanje tokena u minutima pre slanja u `create_access_token(...)`.

#### Linija 2: `from typing import Annotated`

`Annotated` se koristi sa FastAPI dependency sistemom da jasno veže tip i `Depends()` deklaraciju.

#### Linija 5: `from fastapi import APIRouter, Depends, HTTPException, status`

Uvozi:

1. `APIRouter` za grupisanje auth ruta.
2. `Depends` za dependency injection.
3. `HTTPException` za kontrolisane HTTP greške.
4. `status` za čitljive HTTP status kodove.

#### Linija 6: `from fastapi.security import OAuth2PasswordRequestForm`

Model forme za login (`username`, `password`, `grant_type`). Koristi se kod OAuth2 password flow-a.

#### Linija 7: `from passlib.context import CryptContext`

Alat za hash/verify lozinki (ovde sa `bcrypt`).

#### Linija 8: `from sqlalchemy.exc import IntegrityError`

Hvata DB greške integriteta (npr. unique constraint). Korisno kao druga zaštitna mreža.

#### Linije 10-14: lokalni importi iz projekta

1. `settings` iz config sloja.
2. `create_access_token` iz security sloja.
3. `db_dependency` za bazu.
4. `Users` ORM model.
5. Pydantic šeme: `CreateUserRequest`, `Token`, `UserResponse`.

#### Linije 16-19: `router = APIRouter(...)`

Postavlja auth router:

1. `prefix="/auth"` znači da sve rute počinju sa `/auth`.
2. `tags=["auth"]` grupiše rute u Swagger/OpenAPI dokumentaciji.

#### Linija 21: `bcrypt_context = CryptContext(...)`

Konfiguriše hash kontekst:

1. `schemes=["bcrypt"]` -> bcrypt za lozinke.
2. `deprecated="auto"` -> olakšava prelazak sa starijih hash formata.

---

### Funkcija `authenticate_user`

#### Linija 27: `def authenticate_user(...)`

Pomoćna funkcija koja vraća korisnika ili `False` ako autentifikacija ne prođe.

#### Linija 29: query korisnika

Traži korisnika po `username`.

#### Linije 30-31: ako korisnik ne postoji

Odmah vraća `False`.

#### Linije 37-39: runtime provera `hashed_password`

`getattr(..., None)` + `isinstance(..., str)` sprečavaju pad aplikacije ako je podatak neočekivan.

#### Linije 41-42: provera lozinke

`bcrypt_context.verify(password, hashed_password)` poredi plain tekst i hash.

#### Linije 44-48: provera `is_active`

1. Potvrđuje da je tip ispravan (`bool`).
2. Odbija neaktivnog korisnika.

#### Linija 50: `return user`

Vraća ORM korisnika kada su sve provere uspešne.

---

### Endpoint `create_users`

#### Linija 71: dekorator `@router.post(...)`

Kreira endpoint `POST /auth/`:

1. `201 CREATED` kada je uspešno.
2. `response_model=UserResponse` filtrira izlaz.

#### Linije 72-75: potpis funkcije

1. Ulaz je `CreateUserRequest`.
2. DB dolazi kroz dependency.
3. Povratni tip je `UserResponse`.

#### Linije 77-84: pre-check za duplikate

Traži da li već postoji korisnik sa istim email-om ili username-om.

#### Linije 85-89: ako postoji duplikat

Vraća `400 BAD REQUEST` sa jasnim detaljem.

#### Linije 91-99: pravljenje ORM instance

1. Popunjava polja.
2. Lozinku hashuje pre čuvanja (`bcrypt_context.hash(...)`).
3. Postavlja `is_active=True`.

#### Linije 102-110: commit + fallback na `IntegrityError`

1. `db.commit()` pokušava upis.
2. Ako baza prijavi konflikt, radi `db.rollback()`.
3. Vraća kontrolisanu `400` grešku.

#### Linija 111: `db.refresh(create_user_model)`

Učitava osveženo stanje objekta (npr. novi `id`).

#### Linija 114: `return create_user_model`

FastAPI kroz `response_model=UserResponse` vraća samo dozvoljena polja (bez lozinke).

---

### Endpoint `login_for_access_token`

#### Linija 117: dekorator `@router.post("/token", response_model=Token)`

Kreira login endpoint `POST /auth/token` koji vraća `Token` šemu.

#### Linije 118-121: parametri

1. `form_data` dolazi iz OAuth2 forme.
2. `db` dependency za pristup bazi.

#### Linije 122-126: autentifikacija

Poziva `authenticate_user(...)` sa username/password podacima.

#### Linije 127-133: neuspešna autentifikacija

Vraća `401 UNAUTHORIZED` i `WWW-Authenticate: Bearer` header.

#### Linije 135-143: provera runtime tipova za `username` i `id`

Defanzivna provera da su podaci validni pre kreiranja tokena.

#### Linije 145-149: kreiranje access tokena

1. Prosleđuje `username` i `user_id`.
2. `expires_delta` pravi iz `settings.access_token_expire_minutes`.

#### Linija 151: `return Token(...)`

Vraća JSON oblik:

1. `access_token` -> JWT string.
2. `token_type="bearer"` -> očekivani OAuth2 tip.

---

## Kratak praktični zaključak

1. `auth.py` je dobar primer tankih ruta + izdvojene security logike.
2. Hash lozinke i JWT su pravilno odvojeni po odgovornostima.
3. `response_model` i runtime provere smanjuju rizik od curenja ili nekonzistentnih podataka.
4. Ceo tok je spreman za sledeći korak: `get_current_user` i protected rute.

---

## Pitanje 4

PITANJE: Kako da koristim sajt jwt.io kada ubacim encoded token i dobijem decoded sadržaj?

---

## Odgovor 4

ODGOVOR: jwt.io je odličan alat za učenje i proveru JWT strukture, ali ga treba koristiti pažljivo.

### Šta tačno vidiš kada nalepiš token

JWT ima 3 dela odvojena tačkom:

1. Header
2. Payload
3. Signature

Kada nalepiš encoded token u jwt.io, alat automatski prikaže decoded Header i Payload u čitljivom JSON formatu.

Važno:

1. To nije dekripcija tajnih podataka.
2. JWT payload je samo Base64URL dekodiran, pa je čitljiv svakome ko ima token.

---

### Kako da čitaš decoded deo (korak po korak)

1. Header:
   Proveri `alg` (npr. HS256) i `typ` (obično JWT).
2. Payload:
   Proveri claim-ove kao što su `sub`, `username`, `exp`.
3. Signature:
   Potpis potvrđuje integritet tokena, ali samo ako backend radi verifikaciju odgovarajućim secret-om/ključem.

---

### Najvažniji claim-ovi koje treba da proveriš

1. `sub`:
   Stabilan identitet korisnika (kod tebe user_id kao string).
2. `exp`:
   Vreme isteka tokena. Ako je isteklo, token mora biti odbijen.
3. `username`:
   Pomoćni claim za prikaz i debug, ne glavni identitet.

---

### Bezbednosne napomene (obavezno)

1. Ne lepi produkcijske tokene u javne alate.
2. Ne deli token u četu, screenshot-u ili Git repozitorijumu.
3. U payload nikad ne stavljaj lozinke, API ključeve ili druge tajne podatke.
4. Za stvarnu validnost tokena uvek je odgovoran backend decode i verify proces, a ne samo vizuelni prikaz na jwt.io.

---

### Kratka veza sa tvojim kodom

U tvom projektu:

1. Token nastaje u `create_access_token(...)` u `security.py`.
2. jwt.io ti pomaže da proveriš da li su claim-ovi stvarno upisani kako očekuješ (`sub`, `username`, `exp`).
3. Prava kontrola pristupa se dešava tek kada backend validira token (potpis + istek + očekivani claim-ovi).
