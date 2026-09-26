# `Depends` i Dependency Injection u FastAPI-ju

## 1. Osnovna ideja

U FastAPI kodu cesto vidimo:

```python
@router.post("/token")
async def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
	db: db_dependency,
):
	...
```

Ovde endpoint ne pravi sam `form_data` i `db`. On samo opisuje sta mu je potrebno. FastAPI zatim cita potpis funkcije, pronalazi dependency-je, poziva njihove funkcije ili konstruktore, prosledjuje rezultate endpointu i izvrsava cleanup kada je potreban.

To je **Dependency Injection**, odnosno **ubacivanje zavisnosti**.

```text
endpoint kaze sta mu treba
FastAPI dobavlja tu vrednost
FastAPI je ubacuje u endpoint
```

## 2. Sta je dependency

Dependency je vrednost, objekat, resurs ili servis koji je potreban drugom delu aplikacije.

Endpoint za todo aplikaciju moze zavisiti od:

```text
database session
trenutno prijavljenog korisnika
JWT tokena
provere admin role
request parametara
application settings objekta
email servisa
payment servisa
```

Bez dependency injection-a endpoint bi morao sam da pravi sve:

```python
@router.get("/todos")
async def get_todos():
	db = SessionLocal()
	settings = Settings()
	current_user = ...
	...
```

Sa dependency injection-om endpoint samo prima ono sto mu treba:

```python
@router.get("/todos")
async def get_todos(
	db: Annotated[Session, Depends(get_db)],
	current_user: Annotated[Users, Depends(get_current_user)],
):
	...
```

Endpoint se tada fokusira na poslovnu logiku, a dependency funkcije na pripremu resursa i provere.

## 3. Sta radi `Depends`

`Depends` je FastAPI instrukcija koja opisuje kako treba dobaviti dependency.

```python
Depends(get_db)
```

znaci:

```text
FastAPI, kada resavas ovaj request, pozovi get_db
```

Ovo nije isto sto i:

```python
get_db()
```

Razlika:

```python
Depends(get_db)  # funkcija kao instrukcija
get_db()         # funkcija se odmah poziva
```

U endpoint parametru zelimo prvi oblik. FastAPI treba da upravlja trenutkom pozivanja, rezultatom i cleanup-om.

`Depends` nije konkretna database session i nije korisnicki objekat. On je opis nacina na koji FastAPI moze da dobije takvu vrednost.

## 4. Dependency Injection u obicnom i FastAPI kodu

Obicna Python funkcija:

```python
def get_todos(db: Session):
	return db.query(Todo).all()


db = SessionLocal()
get_todos(db)
```

Programer rucno pravi `db` i prosledjuje ga.

U FastAPI-ju to radi framework:

```python
@router.get("/todos")
async def get_todos(
	db: Annotated[Session, Depends(get_db)],
):
	return db.query(Todo).all()
```

Tok je:

```text
HTTP request
	-> FastAPI vidi Depends(get_db)
		-> FastAPI poziva get_db()
			-> rezultat ubacuje u db
				-> poziva get_todos(db)
```

## 5. Prvi obrazac: `OAuth2PasswordRequestForm`

Do sada si koristio:

```python
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm


@router.post("/token")
async def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
	username = form_data.username
	password = form_data.password
	...
```

Ovde je `OAuth2PasswordRequestForm` dependency klasa. `Depends()` nema eksplicitni argument zato sto FastAPI koristi tip iz `Annotated` izraza.

Tok login request-a:

```text
klijent salje form data
	-> username=ana
	-> password=Test1234

FastAPI pravi OAuth2PasswordRequestForm objekat
	-> popunjava form_data.username
	-> popunjava form_data.password

FastAPI poziva login_for_access_token(form_data)
```

Endpoint zato ne cita rucno body i ne parsira formu.

Ovaj oblik je slican starijem obliku:

```python
form_data: OAuth2PasswordRequestForm = Depends()
```

Moderni `Annotated` oblik odvaja Python tip od FastAPI metadata:

```python
Annotated[
	OAuth2PasswordRequestForm,  # tip
	Depends(),                  # FastAPI instrukcija
]
```

## 6. Drugi obrazac: database session

U tvom `TodoApp/db/session.py` postoji:

```python
def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


db_dependency = Annotated[Session, Depends(get_db)]
```

`get_db` je dependency funkcija. Ona:

1. pravi SQLAlchemy session
2. predaje session endpointu preko `yield`
3. zatvara session u `finally` bloku

Endpoint koristi alias:

```python
@router.get("/todos")
async def get_todos(db: db_dependency):
	return db.query(Todo).all()
```

Isti kod bez aliasa:

```python
@router.get("/todos")
async def get_todos(
	db: Annotated[Session, Depends(get_db)],
):
	return db.query(Todo).all()
```

Oba oblika imaju isto ponasanje. Alias samo izbegava ponavljanje.

## 7. Razlika izmedju `get_db`, `db_dependency` i `db`

```python
def get_db():
	...
```

`get_db` je funkcija koja zna kako da napravi i zatvori session.

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

`db_dependency` je reusable opis dependency-ja. To nije konkretna session.

```python
async def endpoint(db: db_dependency):
	...
```

`db` je parametar endpointa. Tokom konkretnog request-a u njemu se nalazi konkretna SQLAlchemy `Session` instanca.

| Ime             | Sta je                  | Kada se dobija konkretna vrednost |
| --------------- | ----------------------- | --------------------------------- |
| `get_db`        | dependency funkcija     | kada je FastAPI pozove            |
| `db_dependency` | typing/dependency alias | pri ucitavanju modula kao opis    |
| `db`            | endpoint parametar      | tokom izvrsavanja request-a       |

## 8. Zasto `get_db` koristi `yield`

Obican dependency bez posebnog cleanup-a moze koristiti `return`:

```python
def get_settings():
	return Settings()
```

Baza je resurs koji treba zatvoriti:

```python
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
```

`yield` deli funkciju na tri konceptualne faze:

```text
pre yield-a    -> priprema resursa
yield db       -> resurs se ubacuje u endpoint
posle yield-a  -> cleanup
```

Ako endpoint podigne exception, `finally` se i dalje izvrsava. Zato se session zatvara i u slucaju greske.

## 9. Kako se cita `Annotated`

Opsti oblik je:

```python
Annotated[tip, metadata]
```

Za bazu:

```python
Annotated[Session, Depends(get_db)]
```

Delovi su:

```text
Session          -> vrednost koju endpoint ocekuje
Depends(get_db)  -> instrukcija kako FastAPI dobavlja vrednost
```

Zato:

```python
db: Annotated[Session, Depends(get_db)]
```

znaci:

```text
parametar se zove db
ocekuje se Session
FastAPI treba da je dobavi pozivom get_db
```

A ovo:

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

znaci da se isti opis cuva pod reusable imenom.

## 10. Dependency graf

Dependency moze zavisiti od druge dependency.

U JWT delu kursa videces nesto slicno:

```python
async def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
	db: db_dependency,
):
	...
```

Endpoint zatim zavisi od `get_current_user`:

```python
@router.get("/todos")
async def get_todos(
	current_user: Annotated[Users, Depends(get_current_user)],
):
	...
```

Graf je:

```text
get_todos
	-> get_current_user
		-> oauth2_scheme
		-> get_db
```

FastAPI prvo resava unutrasnje dependency-je, pa spoljasnje:

```text
oauth2_scheme procita token
	-> get_db obezbedi bazu
		-> get_current_user identifikuje korisnika
			-> get_todos dobija current_user
```

Endpoint ne mora sam da cita header, dekodira JWT i pretrazuje bazu.

## 11. Buduci JWT dependency: `OAuth2PasswordBearer`

U sledecoj oblasti pojavice se:

```python
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl="auth/token",
)
```

Token se cita ovako:

```python
async def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
):
	...
```

Ako request sadrzi:

```http
Authorization: Bearer eyJ...
```

dependency izdvaja samo token:

```text
Bearer eyJ...
	   -> token = eyJ...
```

`oauth2_scheme` uglavnom cita token iz header-a. Ne treba ga mesati sa kompletnom proverom korisnika. Dekodiranje JWT-a i pretraga `Users` tabele pripadace sledecoj funkciji, na primer `get_current_user`.

## 12. `get_current_user` kao slozenija dependency

Buduci oblik moze izgledati ovako:

```python
async def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
	db: db_dependency,
):
	payload = decode_access_token(token)
	username = payload.get("sub")

	if username is None:
		raise HTTPException(
			status_code=401,
			detail="Could not validate credentials",
		)

	user = db.query(Users).filter(Users.username == username).first()

	if user is None:
		raise HTTPException(
			status_code=401,
			detail="Could not validate credentials",
		)

	return user
```

Endpoint ga koristi ovako:

```python
@router.get("/todos")
async def get_todos(
	current_user: Annotated[Users, Depends(get_current_user)],
):
	...
```

Tok:

```text
Authorization header
	-> oauth2_scheme procita token
		-> get_current_user dekodira JWT
			-> db_dependency dobavi Session
				-> Users query pronadje korisnika
					-> endpoint dobija current_user
```

Ako dependency podigne `HTTPException`, endpoint se ne izvrsava.

## 13. Authorization dependency i role

Authentication odgovara na pitanje:

```text
Ko je korisnik?
```

Authorization odgovara na pitanje:

```text
Sta korisnik sme da uradi?
```

Za admin-only rutu moze se napraviti:

```python
def require_admin(
	current_user: Annotated[Users, Depends(get_current_user)],
):
	if current_user.role != "admin":
		raise HTTPException(
			status_code=403,
			detail="Admin privileges required",
		)

	return current_user
```

Endpoint:

```python
@router.delete("/users/{user_id}")
async def delete_user(
	user_id: int,
	admin_user: Annotated[Users, Depends(require_admin)],
):
	...
```

Lanac je:

```text
endpoint
	-> require_admin
		-> get_current_user
			-> oauth2_scheme + db_dependency
		-> provera role
```

Provere se tako ne ponavljaju u svakom endpointu.

## 14. Ownership dependency

Dependency moze proveriti i da li todo pripada trenutnom korisniku:

```python
def get_todo_for_current_user(
	todo_id: int,
	current_user: Annotated[Users, Depends(get_current_user)],
	db: db_dependency,
):
	todo = (
		db.query(Todo)
		.filter(
			Todo.id == todo_id,
			Todo.owner_id == current_user.id,
		)
		.first()
	)

	if todo is None:
		raise HTTPException(status_code=404, detail="Todo not found")

	return todo
```

Endpoint postaje mali:

```python
@router.get("/todos/{todo_id}")
async def read_todo(
	todo: Annotated[Todo, Depends(get_todo_for_current_user)],
):
	return todo
```

Ovaj dependency kombinuje path parametar, trenutnog korisnika, bazu i ownership pravilo.

## 15. Dependency kao funkcija, klasa ili callable objekat

### Funkcija

```python
def common_parameters(skip: int = 0, limit: int = 100):
	return {"skip": skip, "limit": limit}


@router.get("/items")
async def read_items(
	params: Annotated[dict, Depends(common_parameters)],
):
	...
```

FastAPI cita parametre `common_parameters` i dobavlja ih iz request-a.

### Klasa

```python
class CommonQueryParams:
	def __init__(self, skip: int = 0, limit: int = 100):
		self.skip = skip
		self.limit = limit


@router.get("/items")
async def read_items(
	params: Annotated[CommonQueryParams, Depends(CommonQueryParams)],
):
	...
```

FastAPI instancira klasu.

### Callable objekat

Objekat moze imati `__call__` metod:

```python
class QueryChecker:
	def __init__(self, required_value: str):
		self.required_value = required_value

	def __call__(self, query: str = ""):
		return query == self.required_value


checker = QueryChecker("fastapi")
```

Callable objekat moze biti dependency jer se ponasa kao funkcija.

## 16. Dependency u parametru ili u dekoratoru

Ako nam treba rezultat dependency-ja, koristimo parametar:

```python
async def endpoint(
	current_user: Annotated[Users, Depends(get_current_user)],
):
	print(current_user.id)
```

Ako nam treba samo provera, mozemo koristiti dependency na ruti:

```python
@router.get(
	"/admin-area",
	dependencies=[Depends(require_admin)],
)
async def admin_area():
	return {"message": "allowed"}
```

U drugom obliku `require_admin` se izvrsava, ali njegov povratni objekat nije prosledjen endpointu kao parametar.

## 17. Dependency override i testiranje

Dependency injection olaksava testiranje jer dependency mozemo zameniti.

Produkcija:

```python
db: Annotated[Session, Depends(get_db)]
```

Test:

```python
def override_get_db():
	yield test_session


app.dependency_overrides[get_db] = override_get_db
```

Endpoint kod ostaje isti, ali dobija testnu bazu.

Isti princip moze zameniti:

```text
production email service -> fake email service
production payment client -> mock client
real current user -> test user
production settings -> test settings
```

Ovo je jedna od najprakticnijih prednosti dependency injection-a.

## 18. Ceste greske

### Pozivanje dependency funkcije rucno

Pogresno:

```python
async def endpoint(db: get_db()):
	...
```

Ispravno:

```python
async def endpoint(
	db: Annotated[Session, Depends(get_db)],
):
	...
```

### Koriscenje funkcije bez `Depends`

```python
db: get_db
```

Ovo ne daje FastAPI-ju instrukciju da treba da pozove `get_db` i da rezultat ubaci u `db`.

### Vracanje session-a bez cleanup-a

```python
def get_db():
	db = SessionLocal()
	return db
```

Ovaj kod ne opisuje kada se session zatvara. Za request-scoped bazu bolji je `yield` sa `finally` blokom.

### Mesanje authentication i authorization

```text
oauth2_scheme       -> cita bearer token
get_current_user    -> identifikuje korisnika
require_admin       -> proverava dozvolu
```

To su razlicite odgovornosti, iako mogu biti povezane u jedan dependency lanac.

## 19. Kada ne treba koristiti `Depends`

Ne treba svaku pomocnu funkciju pretvoriti u dependency.

Obicna funkcija:

```python
def hash_password(password: str) -> str:
	return bcrypt_context.hash(password)


hashed_password = hash_password(password)
```

`Depends` ima smisla kada FastAPI treba da:

```text
dobavi vrednost iz request-a
upravlja lifecycle-om resursa
prosledi rezultat endpointu
gradi dependency graf
izvrsi zajednicku proveru
omoguci test override
```

## 20. Dependency i middleware

Middleware obmotava siri request/response tok:

```text
request -> middleware -> router -> dependency -> endpoint
```

Middleware je pogodan za logging svih request-ova, CORS, globalne headere i merenje vremena.

Dependency je pogodniji za database session, trenutnog korisnika, role proveru i specificnu validaciju.

## 21. Direktni odgovori

### Da li `Depends` odmah poziva funkciju?

Ne. On opisuje sta FastAPI treba da uradi kada resava konkretan request.

### Da li je `db_dependency` konkretna baza?

Ne. To je alias za dependency opis. Konkretna `Session` nastaje tokom request-a.

### Zasto endpoint ne poziva `get_db()`?

Zato sto FastAPI preko `Depends(get_db)` upravlja pozivanjem, prosledjivanjem i cleanup-om.

### Da li dependency mora da vrati objekat?

Ne. Moze vratiti bilo koju vrednost ili samo izvrsiti proveru i podici exception.

### Da li dependency moze zavisiti od druge dependency?

Da. Na primer `get_current_user` moze zavisiti od tokena i baze, a endpoint od `get_current_user`.

## 22. Najkraci rezime

```text
dependency = ono sto endpointu treba
Depends(...) = instrukcija kako FastAPI dobavlja dependency
dependency injection = FastAPI prosledjuje dobijenu vrednost endpointu
```

Tvoja dva primera znace:

```python
form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
```

FastAPI pravi OAuth2 form objekat iz login request-a i ubacuje ga u `form_data`.

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Alias govori FastAPI-ju da za parametar koji koristi `db_dependency` pozove `get_db`, dobavi SQLAlchemy session i zatvori je nakon request-a.

Buduci obrasci su:

```text
oauth2_scheme       -> cita bearer token
get_current_user    -> identifikuje korisnika
require_admin       -> proverava rolu
get_user_todo       -> proverava ownership
```

Endpoint ne treba da zna kako se svaki resurs pravi. Endpoint treba da dobije ono sto mu je potrebno i da se bavi svojom glavnom poslovnom logikom.

## 23. Sta se desava unutar jednog request-a

Pretpostavimo endpoint:

```python
@router.get("/todos/{todo_id}")
async def read_todo(
	todo_id: int,
	current_user: Annotated[Users, Depends(get_current_user)],
	db: db_dependency,
):
	...
```

FastAPI konceptualno izvodi ovaj postupak:

```text
1. Stigne GET request /todos/7
2. FastAPI analizira potpis endpointa
3. Prepozna todo_id kao path parametar
4. Resi get_current_user i njegove dependency-je
5. Resi get_db i dobije Session
6. Pozove endpoint sa gotovim argumentima
7. Obradi povratnu vrednost
8. Izvrsi cleanup dependency-ja koji koriste yield
9. Posalje HTTP response
```

Jednim potpisom kombinujemo vise izvora:

```text
todo_id      -> URL path
current_user -> Authorization header + baza
db           -> SessionLocal
```

## 24. Dependency funkcija moze imati svoje parametre

Dependency funkcija moze imati obicne FastAPI parametre:

```python
def pagination(
	skip: int = 0,
	limit: int = 100,
):
	return {"skip": skip, "limit": limit}
```

Endpoint:

```python
@router.get("/todos")
async def get_todos(
	pagination_data: Annotated[dict, Depends(pagination)],
):
	...
```

FastAPI cita `skip` i `limit` iz query string-a:

```text
GET /todos?skip=20&limit=10
	-> pagination(skip=20, limit=10)
		-> pagination_data = {"skip": 20, "limit": 10}
```

Dependency tako moze obraditi zajednicke request parametre pre endpointa.

## 25. Odakle dependency dobavlja podatke

Dependency moze koristiti path parametar:

```python
def load_todo(todo_id: int, db: db_dependency):
	return db.query(Todo).filter(Todo.id == todo_id).first()
```

Moze koristiti header:

```python
from fastapi import Header


def get_request_id(
	x_request_id: str | None = Header(default=None),
):
	return x_request_id
```

Moze koristiti cookie:

```python
from fastapi import Cookie


def get_session_id(
	session_id: str | None = Cookie(default=None),
):
	return session_id
```

Moze koristiti i Pydantic body model:

```python
def validate_payload(payload: CreateUserRequest):
	return payload
```

Prakticno pravilo:

```text
tip parametra i FastAPI marker odredjuju odakle se vrednost cita
Depends odredjuje da se pozove druga funkcija ili dependency klasa
```

## 26. `Depends` i drugi FastAPI markeri

Ovi izrazi imaju slican izgled, ali razlicite uloge:

```python
page: Annotated[int, Query(ge=1)]
todo_id: Annotated[int, Path(gt=0)]
user_agent: Annotated[str | None, Header()]
session_id: Annotated[str | None, Cookie()]
```

Znacenja:

```text
Query()  -> query string
Path()   -> URL path
Header() -> HTTP header
Cookie() -> cookie
Body()   -> request body
Depends() -> dependency funkcija ili klasa
```

Svi ovi izrazi daju FastAPI-ju metadata, ali samo `Depends` opisuje dependency lanac.

## 27. Caching dependency-ja u jednom request-u

FastAPI po defaultu kesira rezultat dependency-ja unutar jednog request-a.

```python
def get_current_user():
	print("get_current_user se izvrsava")
	return user


async def endpoint(
	first_user: Annotated[Users, Depends(get_current_user)],
	second_user: Annotated[Users, Depends(get_current_user)],
):
	...
```

Za isti request FastAPI obicno poziva `get_current_user` jednom i koristi rezultat na oba mesta.

```text
jedan request
	-> get_current_user() jednom
		-> first_user = rezultat
		-> second_user = isti rezultat
```

Ako namerno zelimo ponovno izvrsavanje:

```python
Depends(get_value, use_cache=False)
```

Ovo vazi samo za jedan request. Nije trajna memorija i ne deli rezultat izmedju razlicitih request-ova.

## 28. Sync i async dependency funkcije

Dependency moze biti sinhrona:

```python
def get_settings():
	return Settings()
```

ili asinhrona:

```python
async def get_current_user():
	return user
```

Endpoint moze koristiti oba oblika:

```python
async def endpoint(
	value: Annotated[str, Depends(get_value)],
):
	...
```

Ne treba dodavati `await` oko `Depends` izraza:

```python
# Pogresno
value: Annotated[str, Depends(await get_value())]
```

Ispravno:

```python
value: Annotated[str, Depends(get_value)]
```

FastAPI zna da saceka asinhroni dependency. Sinhroni dependency takodje moze da koristi i asinhroni endpoint; FastAPI upravlja nacinom izvrsavanja.

Prakticno pravilo:

```text
ne biraj async samo zato sto izgleda modernije
biraj oblik koji odgovara operaciji i biblioteci
```

## 29. Redosled izvrsavanja

Ako imamo:

```python
def dependency_a():
	print("A")
	return "a"


def dependency_b(
	value: Annotated[str, Depends(dependency_a)],
):
	print("B")
	return "b"


@router.get("/example")
async def example(
	value: Annotated[str, Depends(dependency_b)],
):
	print("endpoint")
	return value
```

Konceptualni redosled je:

```text
A
	-> B
		-> endpoint
```

FastAPI prvo mora da dobije rezultat za `dependency_b`, pa tek onda moze da izvrsi endpoint. Ako `dependency_a` podigne exception, ni `dependency_b` ni endpoint se ne izvrsavaju.

## 30. Cleanup redosled sa vise `yield` dependency-ja

Moguce je imati vise dependency funkcija koje koriste `yield`:

```python
def resource_a():
	resource = create_a()
	try:
		yield resource
	finally:
		close_a(resource)


def resource_b(
	value: Annotated[object, Depends(resource_a)],
):
	resource = create_b(value)
	try:
		yield resource
	finally:
		close_b(resource)
```

Konceptualno:

```text
otvori A
	-> otvori B
		-> endpoint
	-> zatvori B
-> zatvori A
```

Resurs koji je otvoren kasnije obicno se zatvara ranije. Za bazu to znaci da se `db.close()` izvrsava nakon endpointa i dependency-ja koji koriste bazu.

## 31. Globalni objekat naspram dependency-ja

Mozemo imati globalnu konfiguraciju:

```python
settings = Settings()
```

I dependency koja je vraca:

```python
def get_settings():
	return settings
```

Endpoint:

```python
async def endpoint(
	settings: Annotated[Settings, Depends(get_settings)],
):
	...
```

Dependency dodaje kontrolisanu granicu i omogucava override:

```python
def override_settings():
	return TestSettings()


app.dependency_overrides[get_settings] = override_settings
```

Ovo je korisno kada produkcijska konfiguracija koristi environment promenljive ili spoljne servise.

## 32. Dependency kao granica odgovornosti

Dobar dependency ima jednu jasnu odgovornost:

```text
get_db             -> dobavi i zatvori bazu
get_current_user   -> identifikuj korisnika
require_admin      -> proveri admin privilegiju
get_pagination     -> obradi paginaciju
get_request_id     -> procitaj request ID
```

Prevelik dependency bi radio sve:

```text
procitaj token
dekodiraj JWT
pronadji korisnika
proveri role
procitaj todo
posalji email
```

Bolje je napraviti mali lanac:

```text
oauth2_scheme
	-> get_current_user
		-> require_admin
			-> endpoint
```

Svaki sloj dobija jednu glavnu odgovornost i lakse se testira.

## 33. Dependency i servisna funkcija

Servisna funkcija se poziva iz poslovne logike:

```python
def calculate_total(items: list[Item]) -> float:
	return sum(item.price for item in items)
```

Dependency se resava pre endpointa:

```python
def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
):
	...
```

Razlika je u tome ko upravlja pozivom:

```text
obicnu funkciju poziva tvoj kod
dependency poziva FastAPI dependency sistem
```

Servisna funkcija moze biti pozvana iz dependency-ja:

```python
def verify_token(token: str) -> str:
	...


def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
):
	username = verify_token(token)
	...
```

## 34. Security redosled za buduci TodoApp

Prakticni security lanac treba citati ovako:

```text
1. oauth2_scheme cita Authorization header
2. JWT decoder proverava potpis i expiration
3. payload daje identitet kroz sub claim
4. get_current_user cita korisnika iz baze
5. proverava se is_active
6. require_admin ili ownership dependency proverava dozvolu
7. endpoint izvrsava poslovnu operaciju
```

Dependency moze sakriti korake 1 do 5 od endpointa, ali ih ne uklanja. Oni i dalje moraju biti tacno implementirani.

Samo postojanje `current_user` ne znaci automatski da korisnik sme da menja svaki todo. Ownership uslov mora biti primenjen u query-ju ili kroz poseban dependency.

## 35. Vezba: rucno simuliraj FastAPI

Za ovaj endpoint:

```python
@router.get("/todos")
async def get_todos(
	db: db_dependency,
	current_user: Annotated[Users, Depends(get_current_user)],
):
	return {"user_id": current_user.id}
```

napisi redosled koji FastAPI mora da izvrsi:

```text
1. Pozvati get_db
2. Dobiti Session
3. Procitati bearer token
4. Dekodirati token
5. Pronaci korisnika
6. Pozvati get_todos(db, current_user)
7. Zatvoriti Session
```

Ako mozes da objasnis ovaj redosled, razumes osnovu dependency injection-a.

## 36. Vezba: prepoznaj dependency

Odredi ulogu svakog izraza:

```python
get_db
db_dependency
db
Depends(get_db)
db.query(Todo).all()
```

Resenje:

```text
get_db               -> dependency funkcija
db_dependency        -> reusable dependency alias
db                    -> vrednost ubacena u endpoint
Depends(get_db)       -> instrukcija FastAPI-ju
db.query(Todo).all()  -> query/poslovna operacija
```

## 37. Zavrsni mentalni model

Kada vidis:

```python
value: Annotated[SomeType, Depends(some_dependency)]
```

procitaj ga ovako:

```text
Endpoint ima parametar value.
Ocekuje se da value bude SomeType.
FastAPI ne ceka da endpoint sam napravi value.
FastAPI resava some_dependency.
Rezultat dependency-ja ubacuje u value.
```

Kada vidis:

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

procitaj ga ovako:

```text
Napravljen je reusable opis.
Parametar koji koristi alias dobija Session.
Session se dobavlja pozivom get_db.
get_db upravlja lifecycle-om kroz yield i finally.
```

Kada vidis:

```python
current_user: Annotated[Users, Depends(get_current_user)]
```

procitaj ga ovako:

```text
Endpoint zahteva identifikovanog korisnika.
FastAPI pre endpointa cita i validira token.
Pronadje korisnika u bazi.
Ako provera ne uspe, endpoint se ne poziva.
Ako uspe, endpoint dobija Users objekat.
```

To je sustina FastAPI dependency injection sistema.
