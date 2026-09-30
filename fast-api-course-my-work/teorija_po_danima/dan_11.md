# Dan 11 - Lekcija 13 (Decode JWT) praktično, korak po korak

Ovaj materijal je vodič za ručno kucanje koda dok vežbaš dekodiranje i validaciju JWT tokena.

Cilj dana:

1. Da znaš od koje skripte krećeš.
2. Da uvedeš `get_current_user` dependency.
3. Da razumeš svaku dodatu liniju.
4. Da zaštitiš Todo rute current user logikom.

Napomena o konfiguraciji:

`JWT_SECRET_KEY`, `JWT_ALGORITHM` i `ACCESS_TOKEN_EXPIRE_MINUTES` su u `.env`, a `core/config.py` ih čita i validira. To ostaje isto kao juče.

---

## Pitanje 1

PITANJE: Od koje skripte počinjem za decode JWT?

---

## Odgovor 1

ODGOVOR: Redosled rada za ovu lekciju je sledeći:

1. `TodoApp/core/security.py`
   Tu dodaješ `oauth2_bearer` i `get_current_user` (srce decode logike).
2. `TodoApp/api/routes/todos.py`
   Tu koristiš `get_current_user` dependency i uvodiš owner filter.
3. `TodoApp/api/routes/auth.py`
   U ovoj fazi uglavnom ne menjaš logiku; `/auth/token` već radi i daje JWT.

Zašto ovim redom:

Prvo praviš security alat (`get_current_user`), pa ga tek onda ubacuješ u rute koje treba štititi.

---

## Pitanje 2

PITANJE: Šta tačno dodajem u `core/security.py` i zašto?

---

## Odgovor 2

Ispod je praktičan primer koda koji kucaš u `TodoApp/core/security.py` (zadržava postojeći `create_access_token`).

```python
from datetime import datetime, timedelta, timezone
from typing import Any, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from ..db.session import db_dependency
from ..models import Users
from .config import settings


oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(
	*,
	username: str,
	user_id: int,
	expires_delta: timedelta | None = None,
) -> str:
	expire_delta = expires_delta or timedelta(
		minutes=settings.access_token_expire_minutes
	)
	expire = datetime.now(timezone.utc) + expire_delta

	payload: dict[str, Any] = {
		"sub": str(user_id),
		"username": username,
		"exp": expire,
	}

	return jwt.encode(
		payload,
		settings.jwt_secret_key,
		algorithm=settings.jwt_algorithm,
	)


async def get_current_user(
	token: Annotated[str, Depends(oauth2_bearer)],
	db: db_dependency,
) -> Users:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	try:
		payload = jwt.decode(
			token,
			settings.jwt_secret_key,
			algorithms=[settings.jwt_algorithm],
		)
	except JWTError as error:
		raise credentials_exception from error

	subject = payload.get("sub")
	if not isinstance(subject, str) or not subject:
		raise credentials_exception

	try:
		user_id = int(subject)
	except ValueError as error:
		raise credentials_exception from error

	user = db.query(Users).filter(Users.id == user_id).first()
	if user is None:
		raise credentials_exception

	is_active = getattr(user, "is_active", None)
	if not isinstance(is_active, bool) or not is_active:
		raise credentials_exception

	return user
```

### Linija po linija objašnjenje dodatog decode dela

#### `from typing import Any, Annotated`

1. `Any` već koristiš za payload tip.
2. `Annotated` je potreban da dependency jasno bude tipizovan.

---

#### `from fastapi import Depends, HTTPException, status`

1. `Depends` rešava token iz header-a.
2. `HTTPException` daje kontrolisan 401 odgovor.
3. `status` čini kod čitljivijim (`status.HTTP_401_UNAUTHORIZED`).

---

#### `from fastapi.security import OAuth2PasswordBearer`

Ovo nije "skripta koja sama sebe importuje".

Šta se zapravo dešava:

1. `fastapi` je instaliran paket.
2. `security` je modul unutar tog paketa (`fastapi/security/...`).
3. `OAuth2PasswordBearer` je klasa definisana u tom modulu.
4. Linija `from fastapi.security import OAuth2PasswordBearer` samo "uzima" tu klasu i pravi je dostupnom u tvom fajlu.

Drugim rečima:

1. Ništa se ne importuje "samo od sebe".
2. Ti eksplicitno tražiš objekat iz spoljnog modula.
3. Posle toga možeš da napišeš:

```python
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
```

Kratka paralela:

```python
from datetime import timedelta
```

Radi po istoj ideji: uzimaš `timedelta` iz `datetime` modula i koristiš je u svom fajlu.

Praktično značenje u ovom projektu:

`OAuth2PasswordBearer` dodaje mehanizam koji iz `Authorization: Bearer <token>` izvlači samo token string.

---

#### `from jose import JWTError, jwt`

1. `jwt.decode(...)` radi verifikaciju i čitanje payload-a.
2. `JWTError` hvata nevalidan token/signature/format/exp slučajeve.

---

#### `from ..db.session import db_dependency` i `from ..models import Users`

Treba ti DB i `Users` model da od token identiteta dobiješ stvarnog korisnika.

---

#### `oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")`

1. `tokenUrl` mora da odgovara javnoj token ruti (`/auth/token`).
2. Ovo koristi `OpenAPI/Swagger` i dependency sistem tako što automatski čita token iz `Authorization` header-a, tačnije iz njegove vrednosti formata `Bearer <token>`), i prosleđuje token u dependency funkciju (`get_current_user`).

Jednostavno rečeno, token se vadi iz `bearer` dela `Authorization header`-a (sve što dolazi posle `Bearer` a to je `string vrednost tokena`).

---

#### `async def get_current_user(...)`

Potpis funkcije znači:

1. `token` dolazi iz `Authorization` header-a (Bearer šema: `Authorization: Bearer <token>`).
2. `db` dolazi iz DB dependency-ja.
3. Funkcija vraća `Users` instancu (verified current user).

#### `credentials_exception = HTTPException(...)`

Jedno mesto za standardni 401 odgovor, da ne dupliraš isti blok više puta.

#### `payload = jwt.decode(...)`

Ovde se dešava prava validacija:

1. provera potpisa (`settings.jwt_secret_key`),
2. provera algoritma (`algorithms=[settings.jwt_algorithm]`),
3. provera vremena (`exp`) kroz biblioteku.

#### `except JWTError as error: raise credentials_exception from error`

Ako decode padne iz bilo kog JWT razloga, vraćaš uniforman 401.

#### `subject = payload.get("sub")`

Čitaš identitet iz claim-a koji encode već upisuje (`sub` = `str(user_id)`).

#### `if not isinstance(subject, str) or not subject:`

Aplikaciona validacija: claim mora postojati i biti ne-prazan string.

#### `user_id = int(subject)`

Konvertuješ `sub` nazad u integer ID korisnika.

#### `user = db.query(Users).filter(Users.id == user_id).first()`

Od token identiteta dobijaš stvarni DB user objekat.

#### `if user is None: raise credentials_exception`

Token može biti kriptografski validan, ali korisnik više ne postoji.

#### `is_active` provera

Zadržavaš bezbednosno pravilo da neaktivan user ne sme proći autentifikaciju.

#### `return user`

Rute sada dobijaju server-verifikovan current user kontekst.

---

## Pitanje 3

PITANJE: Šta tačno dodajem u `todos.py` da koristi decode?

---

## Odgovor 3

Ispod je praktičan primer izmena koje kucaš u `TodoApp/api/routes/todos.py`.

```python
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from ...core.security import get_current_user
from ...db.session import db_dependency
from ...models import Todos, Users
from ...schemas import CreateTodoRequest, TodoResponse

router = APIRouter(
	prefix="/todos",
	tags=["todos"],
)

current_user_dependency = Annotated[Users, Depends(get_current_user)]


@router.get(
	"/",
	status_code=status.HTTP_200_OK,
)
async def get_all(
	db: db_dependency,
	current_user: current_user_dependency,
) -> list[TodoResponse]:
	todo_models = db.query(Todos).filter(Todos.owner_id == current_user.id).all()
	return [TodoResponse.model_validate(todo) for todo in todo_models]


@router.get(
	"/{todo_id}",
	status_code=status.HTTP_200_OK,
)
async def read_todo(
	db: db_dependency,
	current_user: current_user_dependency,
	todo_id: int = Path(gt=0, description="ID todo zadatka mora biti veći od nule."),
) -> TodoResponse:
	todo_model = (
		db.query(Todos)
		.filter(Todos.id == todo_id, Todos.owner_id == current_user.id)
		.first()
	)

	if todo_model is not None:
		return TodoResponse.model_validate(todo_model)

	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail="Todo nije pronađen.",
	)


@router.post(
	"/",
	status_code=status.HTTP_201_CREATED,
)
async def create_todo(
	db: db_dependency,
	current_user: current_user_dependency,
	todo_request: CreateTodoRequest,
) -> TodoResponse:
	todo_model = Todos(**todo_request.model_dump(), owner_id=current_user.id)
	db.add(todo_model)
	db.commit()
	db.refresh(todo_model)
	return TodoResponse.model_validate(todo_model)


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
	db: db_dependency,
	current_user: current_user_dependency,
	todo_request: CreateTodoRequest,
	todo_id: int = Path(gt=0, description="ID todo zadatka mora biti veći od nule"),
) -> None:
	todo_model = (
		db.query(Todos)
		.filter(Todos.id == todo_id, Todos.owner_id == current_user.id)
		.first()
	)
	if todo_model is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Todo nije pronađen.",
		)
	for key, value in todo_request.model_dump().items():
		setattr(todo_model, key, value)

	db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
	db: db_dependency,
	current_user: current_user_dependency,
	todo_id: int = Path(
		gt=0,
		description="ID todo zadatka mora biti veći od nule",
	),
) -> None:
	todo_model = (
		db.query(Todos)
		.filter(Todos.id == todo_id, Todos.owner_id == current_user.id)
		.first()
	)
	if todo_model is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Todo nije pronađen.",
		)

	db.delete(todo_model)
	db.commit()
```

### Linija po linija objašnjenje ključnih dodataka

#### `from typing import Annotated`

Potrebno za typed dependency alias.

#### `from fastapi import ... Depends ...`

`Depends` je obavezan jer sada rute zahtevaju current user dependency.

#### `from ...core.security import get_current_user`

Uvozi decode helper koji verifikuje token i vraća user-a.

#### `from ...models import Todos, Users`

Dodaješ `Users` tip da `current_user_dependency` bude tipizovan.

#### `current_user_dependency = Annotated[Users, Depends(get_current_user)]`

Jedna linija za DRY pristup: ne ponavljaš `Annotated[...]` u svakoj ruti.

#### `current_user: current_user_dependency` u potpisima ruta

Svaka ruta postaje protected. Bez validnog Bearer tokena nema pristupa.

#### `filter(Todos.owner_id == current_user.id)`

To je ownership filter. User vidi samo svoje podatke.

#### `Todos(**todo_request.model_dump(), owner_id=current_user.id)`

Na kreiranju novog todo-a ownership dolazi iz tokena, ne iz klijentskog input-a.

#### `filter(Todos.id == todo_id, Todos.owner_id == current_user.id)`

Kod `read/update/delete` istovremeno proveravaš i ID todo-a i vlasništvo.

---

## Pitanje 4

PITANJE: Da li menjam `auth.py` u lekciji decode?

---

## Odgovor 4

ODGOVOR: U tvom trenutnom stanju projekta, minimalno.

1. `/auth/token` već vraća validan JWT.
2. `create_access_token(...)` već upisuje `sub`, `username`, `exp`.
3. Decode lekcija fokus je na `security.py` i potrošače (npr. `todos.py`).

Dakle, `auth.py` trenutno može ostati kako jeste.

---

## Pitanje 5

PITANJE: Kako da testiram decode korak kada sve ručno ukucam?

---

## Odgovor 5

Predlog redosleda testiranja:

1. Registruj user-a (`POST /auth/`).
2. Login (`POST /auth/token`) i preuzmi `access_token`.
3. U Swagger `Authorize` nalepi token kao `Bearer <token>`.
4. Pozovi `GET /todos/`:
   - sa tokenom očekuješ 200,
   - bez tokena očekuješ 401.
5. Kreiraj todo sa user A, pa pokušaj čitanje/izmenu sa user B:
   - treba da ne vidi/menja tuđi zapis.

Minimalni očekivani rezultat lekcije 13:

1. `get_current_user` uspešno dekodira token.
2. Protected ruta zahteva validan Bearer token.
3. Todo rezultat je filtriran po `owner_id`.

---

## Pitanje 6

PITANJE: Odakle dolazi naziv `user_id` kada je u `models.py` i `schemas.py` polje `id`?

---

## Odgovor 6

ODGOVOR: Naziv `user_id` ne dolazi automatski iz SQLAlchemy modela ili Pydantic sheme, nego iz imena parametra koje si ti izabrao u funkciji.

Ključna ideja:

1. U modelu korisnika imaš atribut `id` (na primer `user.id`).
2. Kada tu vrednost prosleđuješ u funkciju za kreiranje tokena, parametar može da se zove kako želiš.
3. U ovom kodu je izabrano ime `user_id` jer je čitljivije i preciznije od samog `id`.

Primer mapiranja u praksi:

```python
authenticated_user = ...

token = create_access_token(
	username=authenticated_user.username,
	user_id=authenticated_user.id,
)
```

Šta ovo znači:

1. Levo (`user_id=...`) je naziv funkcijskog parametra.
2. Desno (`authenticated_user.id`) je realna vrednost iz modela (`id` kolona iz baze).
3. Dakle, `id` iz modela se samo prosledi u parametar koji je nazvan `user_id`.

Zašto je to dobro:

1. U većim fajlovima imaš više različitih ID vrednosti (`todo_id`, `user_id`, `project_id`).
2. Ime `user_id` odmah govori da je to ID korisnika, pa je kod čitljiviji i manje sklon greškama.

Napomena:

Mogao bi tehnički da nazoveš parametar i `id`, i kod bi radio, ali je to slabije čitljivo i može da napravi zabunu kada imaš više tipova identifikatora.

---

## Pitanje 7

PITANJE: Zašto se za ključ `sub` radi `str(user_id)` umesto da ostane broj?

---

## Odgovor 7

ODGOVOR: Radi se prvenstveno zbog standardizacije i interoperabilnosti JWT claim-ova.

Suština:

1. `sub` (subject) predstavlja identitet subjekta tokena.
2. U praksi JWT/OAuth2/OIDC ekosistema `sub` se najčešće tretira kao string identifikator.
3. Zato je bezbednije i kompatibilnije da u token upišeš `sub` kao tekst, tj. `str(user_id)`.

Šta time dobijaš:

1. Bolju kompatibilnost između biblioteka, jezika i servisa (manje zavisiš od toga kako ko tretira JSON brojeve).
2. Stabilniji format identiteta kroz ceo auth tok.
3. Jasnu i eksplicitnu validaciju u decode fazi, jer ti kontrolišeš kada i kako se string pretvara nazad u `int`.

Kako to izgleda u tvom toku:

1. Encode faza: u payload ide `"sub": str(user_id)`.
2. Decode faza: čitaš `subject = payload.get("sub")`.
3. Proveravaš da je `subject` neprazan string.
4. Tek onda radiš `user_id = int(subject)`.

Zašto je ovo dobro za validaciju:

1. Ako je `sub` neispravan (npr. prazan, pogrešnog tipa, ili ne može da se konvertuje), odmah vraćaš 401.
2. Time sprečavaš da nevalidan identitet stigne do DB upita.

Zaključak:

`str(user_id)` u `sub` nije slučajno, nego namerna odluka da identitet u JWT bude u standardnom, prenosivom obliku, a da se stroga tipizacija (`int`) vrati tek u kontrolisanoj decode logici.

---

## Mini rezime za dan 11

1. Počinješ od `core/security.py` (decode logika).
2. Nastavljaš na `todos.py` (primena dependency-ja + ownership).
3. `auth.py` uglavnom ostaje stabilan.
4. Najvažnije: ne veruješ klijentu za user identitet; uzimaš ga iz verifikovanog JWT-a.
