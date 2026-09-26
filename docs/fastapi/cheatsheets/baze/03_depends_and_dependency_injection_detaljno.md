# `Depends` i Dependency Injection u FastAPI-ju

## 1. Osnovna ideja

U FastAPI kodu često vidimo:

```python
@router.post("/token")
async def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
	db: db_dependency,
):
	...
```

Ovde endpoint ne pravi sam `form_data` i `db`. On samo opisuje šta mu je potrebno. FastAPI zatim čita potpis funkcije, pronalazi dependency-je, poziva njihove funkcije ili konstruktore, prosleđuje rezultate endpointu i izvršava cleanup kada je potreban.

To je **Dependency Injection**, odnosno **ubacivanje zavisnosti**.

```text
endpoint kaže tačno šta mu treba kroz parametre
FastAPI dobavlja te vrednosti pre nego što pozove endpoint
Zatim FastAPI ubacuje te vrednosti u odgovarajuće parametre endpoint funkcije
```

---

## 2. Šta je dependency

Dependency je `vrednost`, `objekat`, `resurs` ili `servis` koji je potreban drugom delu aplikacije.

Endpoint za `todo` aplikaciju može zavisiti od:

```text
	database session (db: Session = Depends(get_db))
	trenutno prijavljenog korisnika (current_user: Users = Depends(get_current_user))
	JWT tokena (token: str = Depends(get_jwt_token))
	provere admin role (is_admin: bool = Depends(get_is_admin))
	request parametara (params: dict = Depends(get_request_params))
	application settings objekta (settings: Settings = Depends(get_settings))
	email servisa (email_service: EmailService = Depends(get_email_service))
	payment servisa (payment_service: PaymentService = Depends(get_payment_service))
```

Sa dependency injection-om endpoint samo prima ono što mu treba:

```python
@router.get("/todos")
async def get_todos(
	db: Annotated[Session, Depends(get_db)],
	current_user: Annotated[Users, Depends(get_current_user)],
):
	...
```

Endpoint se tada fokusira na poslovnu logiku, a dependency funkcije na pripremu resursa i provere.

---

## 3. Šta radi `Depends`

`Depends` je FastAPI instrukcija koja opisuje kako treba dobaviti dependency.

```python
Depends(get_db)
```

znači:

```text
FastAPI, kada rešavaš ovaj request, pozovi get_db
```

Ovo nije isto što i:

```python
get_db()
```

Razlika:

```python
Depends(get_db)  # funkcija kao instrukcija
get_db()         # funkcija se odmah poziva
```

U endpoint parametru želimo prvi oblik. FastAPI treba da upravlja trenutkom pozivanja, rezultatom i cleanup-om.

`Depends` nije konkretna database session i nije korisnički objekat. On je opis načina na koji FastAPI može da dobije takvu vrednost.

---

## 4. Dependency Injection u običnom i FastAPI kodu

Obična Python funkcija:

```python
def get_todos(db: Session):
	return db.query(Todo).all()


db = SessionLocal()
get_todos(db)
```

Programer ručno pravi `db` i prosleđuje ga.

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

Ovde je:

1. `Session` tip rezultata koji endpoint očekuje.
2. `get_db` je dependency funkcija koja pravi konkretnu instancu `Session`
3. `Depends(get_db)` govori FastAPI-ju da tu funkciju koristi za dobavljanje vrednosti.
4. `db` je konkretna instanca `Session` koja se prosleđuje endpointu.

Ovo omogućava FastAPI-ju da upravlja životnim ciklusom database session-a. Za programera, endpoint parametar `db` je jednostavno instanca `Session` koju može koristiti u svom kodu.

---

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

Ovde je `OAuth2PasswordRequestForm` klasa koja može da se koristi kao dependency callable. `Depends()` nema eksplicitni argument zato što FastAPI, kada je dependency `None`, koristi tip iz `Annotated` izraza kao dependency (u ovom slučaju `OAuth2PasswordRequestForm`).

Tok `login request`-a:

```text
klijent šalje form data
	-> username=ana
	-> password=Test1234

FastAPI pravi OAuth2PasswordRequestForm objekat
	-> popunjava form_data.username
	-> popunjava form_data.password

FastAPI poziva login_for_access_token(form_data)
```

Endpoint zato ne čita ručno body i ne parsira formu.

Ovaj oblik je sličan starijem obliku:

```python
form_data: OAuth2PasswordRequestForm = Depends()
```

Moderni `Annotated` oblik odvaja Python tip od FastAPI metadata:

```python
Annotated[
	OAuth2PasswordRequestForm,  # tip koji FastAPI treba da instancira i koji sadrzi podatke iz form data
	Depends(), # FastAPI instrukcija kako se dobija instanca tipa iz Annotated
]
```

---

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

1. pravi SQLAlchemy session (`db= SessionLocal()`)
2. predaje session endpointu preko `yield` (FastAPI uzima vrednost iz `yield` i prosleđuje je parametru `db` endpoint funkcije)
3. zatvara session u `finally` bloku (Tada se vrši cleanup tj. oslobađanje resursa koji su korišćeni tokom session-a i osigurava da se session pravilno zatvori bez obzira na to da li je došlo do greške)

Endpoint koristi alias `db_dependency` umesto da direktno koristi `Annotated[Session, Depends(get_db)]`

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

Oba oblika imaju isto ponašanje. Alias samo izbegava ponavljanje.

---

## 7. Razlika između `get_db`, `db_dependency` i `db`

```python
def get_db():
	...
```

`get_db` je funkcija koja zna kako da napravi i zatvori session.

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

`db_dependency` je reusable opis dependency-ja (`typing/dependency alias`). To nije konkretna session instanca.

```python
async def endpoint(db: db_dependency):
	...
```

`db` je parametar endpointa. Tokom konkretnog request-a u njemu se nalazi konkretna SQLAlchemy `Session` instanca.

| Ime             | Sta je                  | Kada se dobija konkretna vrednost |
| --------------- | ----------------------- | --------------------------------- |
| `get_db`        | dependency funkcija     | kada je FastAPI pozove            |
| `db_dependency` | typing/dependency alias | pri učitavanju modula kao opis    |
| `db`            | endpoint parametar      | tokom izvršavanja request-a       |

---

## 8. Zašto `get_db` koristi `yield`

Običan dependency bez posebnog cleanup-a može koristiti `return`:

```python
def get_settings():
	return Settings()
```

Baza je resurs koji treba zatvoriti (`cleanup` je neophodan):

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
pre yield-a    -> priprema resursa za izvršavanje endpoint-a

yield db       -> resurs se ubacuje u endpoint
               -> koristi se tokom izvršavanja request-a

posle yield-a  -> cleanup resursa i zatvaranje session-a (u finally bloku)
```

Ako endpoint podigne exception, `finally` se i dalje izvršava. Zato se session zatvara i u slučaju greške.

---

## 9. Kako se čita `Annotated`

Opšti oblik je:

```python
Annotated[tip, metadata]
```

`Annotated` ima najmanje dva važna dela:

```text
prvi deo  -> tip vrednosti
drugi deo -> metadata, odnosno dodatna informacija za framework
```

Na primer:

```python
Annotated[Session, Depends(get_db)]
```

znači:

```text
Session          -> endpoint očekuje SQLAlchemy Session
Depends(get_db)  -> FastAPI zna kako da dobavi tu Session vrednost
```

### 9.1. Koji objekti mogu biti tip

Prvi deo može biti bilo koji odgovarajući Python tip, na primer:

```text
Session                     -> SQLAlchemy session (instanca klase Session)
str                         -> string, na primer token (instanca klase str)
int                         -> celobrojna vrednost (instanca klase int)
float                       -> decimalna vrednost (instanca klase float)
bool                        -> True ili False (instanca klase bool)
datetime                    -> datum i vreme (instanca klase datetime)
list                        -> lista (instanca klase list)
dict                        -> rečnik (instanca klase dict)
OAuth2PasswordRequestForm   -> objekat OAuth2 login forme (instanca klase OAuth2PasswordRequestForm)
```

`OAuth2PasswordRequestForm` je, dakle, tip odnosno klasa. U `Annotated` se nalazi na mestu prvog argumenta, a ne u metadata delu.

---

### 9.2. Šta može biti metadata

Drugi deo može biti FastAPI informacija kao:

```text
Depends(...)  -> dobavi vrednost preko dependency sistema
Query(...)    -> čitaj i validiraj query parametar
Path(...)     -> čitaj i validiraj path parametar
Header(...)   -> čitaj header vrednost
Cookie(...)   -> čitaj cookie vrednost
Body(...)     -> čitaj body vrednost
Form(...)     -> čitaj form podatke
File(...)     -> čitaj fajl podatke
Security(...) -> sigurnosni dependency, na primer OAuth2 ili API key
```

Važno: `OAuth2PasswordRequestForm` nije metadata objekat. On je klasa koju FastAPI može koristiti kao dependency.

---

## 9.3. Da li su ova dva oblika ekvivalentna?

Za ovaj konkretan slučaj, sledeća dva oblika imaju isto značenje:

```python
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm


form_data: Annotated[
	OAuth2PasswordRequestForm,
	Depends(),
]
```

i:

```python
form_data: Annotated[
	OAuth2PasswordRequestForm,
	Depends(OAuth2PasswordRequestForm),
]
```

Zašto? Zato što `Depends()` bez eksplicitnog argumenta koristi tip iz `Annotated` kao dependency. U prvom primeru taj tip je `OAuth2PasswordRequestForm`, pa FastAPI zna da treba da koristi baš tu klasu.

Drugi oblik to kaže eksplicitno:

```text
tip parametra: OAuth2PasswordRequestForm
dependency:    OAuth2PasswordRequestForm
```

U ovom slučaju su isti objekat i tip i dependency callable, pa su oblici praktično ekvivalentni.

---

### 9.4. Oblik koji nije ispravan

Ovo nije ispravan ekvivalent:

```python
Annotated[Depends(OAuth2PasswordRequestForm)]
```

Razlozi su:

1. `Annotated` očekuje najmanje prvi argument koji predstavlja tip.
2. `Depends(...)` je metadata, a ne tip parametra.
3. Nije navedeno koji tip endpoint treba da dobije.

Ispravno je:

```python
Annotated[
	OAuth2PasswordRequestForm,
	Depends(OAuth2PasswordRequestForm),
]
```

ili kraće:

```python
Annotated[
	OAuth2PasswordRequestForm,
	Depends(),
]
```

Razlika je ista kao razlika između nepotpunog opisa i potpunog opisa:

```text
Annotated[metadata]                  -> nedostaje tip
Annotated[tip, metadata]             -> potpun oblik
```

---

### 9.5. Šta znači `OAuth2PasswordRequestForm(...)`

Važno je razlikovati klasu i instancu:

```python
OAuth2PasswordRequestForm       # klasa, tip i callable dependency
OAuth2PasswordRequestForm(...)  # poziv klase, pokušaj pravljenja instance
```

U `Annotated` ne pišemo:

```python
Annotated[
	OAuth2PasswordRequestForm,
	OAuth2PasswordRequestForm(...),
]
```

jer FastAPI ne treba unapred napravljenu formu. FastAPI treba da dobije instrukciju kako da napravi formu za konkretan request. Zato koristimo:

```python
Depends(OAuth2PasswordRequestForm)
```

ili, u ovom specifičnom slučaju, skraćeno:

```python
Depends()
```

Tok je:

```text
request sa username/password form podacima
    -> FastAPI poziva OAuth2PasswordRequestForm dependency
        -> pravi instancu forme za taj request
            -> ubacuje je u form_data
```

---

### 9.6. Poređenje sa bazom

Kod baze imamo:

```python
db: Annotated[Session, Depends(get_db)]
```

Ovde tip i dependency nisu isti:

```text
Session       -> tip rezultata koji endpoint dobija (class Session)
get_db        -> callable koji zna kako da napavi instancu klase Session
              -> preko dependency injection (Depends(get_db)) koji FastAPI koristi
			  -> na taj način što poziva funkciju get_db a zatim se preko db = LocalSession() i dobija instanca klase Session
```

Kod OAuth2 forme imamo:

```python
form_data: Annotated[
	OAuth2PasswordRequestForm,
	Depends(OAuth2PasswordRequestForm),
]
```

Ovde ista klasa ima dve uloge:

```text
OAuth2PasswordRequestForm kao prvi deo -> tip rezultata koji endpoint dobija (class OAuth2PasswordRequestForm)

OAuth2PasswordRequestForm u Depends -> callable koji pravi rezultat, vraća instancu klase OAuth2PasswordRequestForm
```

Zato je moguće koristiti `Depends()` bez argumenta.

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

znači:

```text
Parametar se zove db
čekuje se Session
FastAPI treba da je dobavi pozivom get_db
```

A ovo:

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

znači da se isti opis čuva pod reusable imenom. Na taj način možemo ga koristiti na više mesta bez ponovnog kucanja koda ili redefinisanja dependency-ja.

---

## 10. Dependency graf

Dependency može zavisiti od drugog dependency-ja.

U JWT delu kursa videćeš nešto slično:

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

Grafikon (dependency graph) je:

```text
get_todos
	-> get_current_user
		-> oauth2_scheme
		-> get_db
```

FastAPI prvo rešava unutrašnje dependency-je, pa spoljašnje:

```text
oauth2_scheme pročita token
	-> get_db obezbedi bazu
		-> get_current_user identifikuje korisnika
			-> get_todos dobija current_user
```

Endpoint ne mora sam da čita header, dekodira JWT i pretrazuje bazu.

---

## 11. Buduci JWT dependency: `OAuth2PasswordBearer`

U sledećoj oblasti pojaviće se:

```python
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl="auth/token",
)
```

Token se izdvaja ovako:

```python
async def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
):
	...
```

Ako request sadrži:

```http
Authorization: Bearer eyJ...
```

dependency izdvaja samo token:

```text
Bearer eyJ...
	   -> token = eyJ...
```

`oauth2_scheme` uglavnom čita token iz header-a. Ne treba ga mešati sa kompletnom proverom korisnika. Dekodiranje JWT-a i pretraga `Users` tabele pripadaće sledećoj funkciji, na primer `get_current_user`.

---

## 12. `get_current_user` kao složenija dependency

Budući oblik može izgledati ovako:

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

Ako dependency podigne `HTTPException`, endpoint se ne izvršava.

---

## 13. Authorization dependency i role

Authentication odgovara na pitanje:

```text
Ko je korisnik?
```

Authorization odgovara na pitanje:

```text
Šta korisnik sme da uradi?
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

---

## 14. Ownership dependency

Dependency može proveriti i da li todo pripada trenutnom korisniku:

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

---

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

---

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

---

### Callable objekat

Objekat može imati `__call__` metod:

```python
class QueryChecker:
	def __init__(self, required_value: str):
		self.required_value = required_value

	def __call__(self, query: str = ""):
		return query == self.required_value


checker = QueryChecker("fastapi")
```

Callable objekat može biti dependency jer se ponaša kao funkcija.

---

## 16. Dependency u parametru ili u dekoratoru

Ako nam treba rezultat dependency-ja, koristimo parametar:

```python
async def endpoint(
	current_user: Annotated[Users, Depends(get_current_user)],
):
	print(current_user.id)
```

Ako nam treba samo provera, možemo koristiti dependency na ruti:

```python
@router.get(
	"/admin-area",
	dependencies=[Depends(require_admin)],
)
async def admin_area():
	return {"message": "allowed"}
```

U drugom obliku `require_admin` se izvršava, ali njegov povratni objekat nije prosleđen endpointu kao parametar.

---

## 17. Dependency override i testiranje

Dependency injection olakšava testiranje jer dependency možemo zameniti.

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

Isti princip može zameniti:

```text
production email service -> fake email service
production payment client -> mock client
real current user -> test user
production settings -> test settings
```

Ovo je jedna od najpraktičnijih prednosti dependency injection-a.

---

## 18. Česte greške

### Pozivanje dependency funkcije ručno

Pogrešno:

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

---

### Korišćenje funkcije bez `Depends`

```python
db: get_db
```

Ovo ne daje FastAPI-ju instrukciju da treba da pozove `get_db` i da rezultat ubaci u `db`.

---

### Vraćanje session-a bez cleanup-a

```python
def get_db():
	db = SessionLocal()
	return db
```

Ovaj kod ne opisuje kada se session zatvara. Za request-scoped bazu bolji je `yield` sa `finally` blokom.

---

### Mešanje authentication i authorization

```text
oauth2_scheme       -> cita bearer token
get_current_user    -> identifikuje korisnika
require_admin       -> proverava dozvolu
```

To su različite odgovornosti, iako mogu biti povezane u jedan dependency lanac.

---

## 19. Kada ne treba koristiti `Depends`

Ne treba svaku pomoćnu funkciju pretvoriti u dependency.

Obična funkcija:

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
izvrši zajednicku proveru
omogući test override
```

---

## 20. Dependency i middleware

`Middleware` obmotava širi `request/response` tok:

```text
request -> middleware -> router -> dependency -> endpoint
```

`Middleware` je pogodan za logging svih request-ova, CORS, globalne headere i merenje vremena.

`Dependency` je pogodniji za database session, trenutnog korisnika, role proveru i specificnu validaciju.

---

## 21. Direktni odgovori

### Da li `Depends` odmah poziva funkciju?

Ne. On opisuje tačno šta FastAPI treba da uradi kada rešava konkretan request.

---

### Da li je `db_dependency` konkretna baza?

Ne. To je alias za dependency opis. Konkretna `Session` nastaje tokom request-a.

---

### Zašto endpoint ne poziva `get_db()`?

Zato što FastAPI preko `Depends(get_db)` upravlja pozivanjem, prosledjivanjem i cleanup-om.

---

### Da li dependency mora da vrati objekat?

Ne. Može vratiti bilo koju vrednost ili samo izvršiti proveru i podići exception.

---

### Da li dependency može zavisiti od druge dependency?

Da. Na primer `get_current_user` može zavisiti od tokena i baze, a endpoint od `get_current_user`.

---

## 22. Najkraci rezime

```text
dependency = ono što endpointu treba za rad sa resursima iz FastAPI-ja (npr. baza, trenutni korisnik, token)

Depends(...) -> sadrži instrukciju kako FastAPI dobavlja/kreira dependency. Najčešće se koristi za resurse koji zahtevaju lifecycle management, kao što su baze podataka ili autentifikacija.

dependency injection -> FastAPI prosleđuje dobijenu vrednost za dependency u endpoint.
```

Tvoja dva primera znače:

```python
form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
```

FastAPI pravi OAuth2 form objekat iz login request-a i ubacuje ga u `form_data`.

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Alias govori FastAPI-ju da za parametar koji koristi `db_dependency` (npr. `db: db_dependency`) pozove `get_db`, dobavi SQLAlchemy session i zatvori je nakon request-a.

Budući obrasci su:

```text
oauth2_scheme       -> čita bearer token (Authorization header)
get_current_user    -> identifikuje korisnika (iz bearer token-a)
require_admin       -> proverava rolu (npr. admin)
get_user_todo       -> proverava ownership (da li trenutni korisnik ima pristup datom todo-u)
```

Endpoint ne treba da zna kako se svaki resurs pravi. Endpoint treba da dobije ono što mu je potrebno i da se bavi svojom glavnom poslovnom logikom (npr. obrada todo item-a, kreiranje novog todo item-a, itd.).

---

## 23. Šta se dešava unutar jednog request-a

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

1. Stigne `GET request /todos/7` preko HTTP protokola.
2. Endpoint je odabran na osnovu `URL`-a i `HTTP` metode (`GET`, `POST`, itd.).
3. FastAPI `analizira potpis endpointa` da bi odredio koje `dependency`-je treba da reši i odakle da dobije vrednosti za parametre koje endpoint funkcija očekuje.
4. Prepozna `todo_id` kao path parametar (`/todos/{todo_id}`).
5. Resi `get_current_user` i njegove dependency-je
6. Resi `get_db` i dobije `Session`
7. Pozove endpoint sa gotovim argumentima (`todo_id`, `current_user`, `db`)
8. Obradi povratnu vrednost (npr. JSON response)
9. Izvrši cleanup dependency-ja koji koriste `yield`
10. Pošalje HTTP response

Jednim potpisom kombinujemo više izvora:

```text
todo_id      -> URL path
current_user -> Authorization header + baza
db           -> SessionLocal
```

---

## 24. Dependency funkcija može imati svoje parametre

Dependency funkcija može imati obične FastAPI parametre:

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

FastAPI čita `skip` i `limit` iz query string-a:

```text
GET /todos?skip=20&limit=10
	-> pagination(skip=20, limit=10)
		-> pagination_data = {"skip": 20, "limit": 10}
```

Dependency tako može obraditi zajedničke request parametre pre endpointa.

---

## 25. Odakle dependency dobavlja podatke

Dependency može koristiti path parametar:

```python
def load_todo(todo_id: int, db: db_dependency):
	return db.query(Todo).filter(Todo.id == todo_id).first()
```

Može koristiti header:

```python
from fastapi import Header


def get_request_id(
	x_request_id: str | None = Header(default=None),
):
	return x_request_id
```

Može koristiti cookie:

```python
from fastapi import Cookie


def get_session_id(
	session_id: str | None = Cookie(default=None),
):
	return session_id
```

Može koristiti i Pydantic body model:

```python
def validate_payload(payload: CreateUserRequest):
	return payload
```

Praktično pravilo:

```text
tip parametra i FastAPI marker određuju odakle se vrednost čita
Depends određuje da se pozove druga funkcija ili dependency klasa
```

---

## 26. `Depends` i drugi FastAPI markeri

Ovi izrazi imaju sličan izgled, ali različite uloge:

```python
page: Annotated[int, Query(ge=1)]
todo_id: Annotated[int, Path(gt=0)]
user_agent: Annotated[str | None, Header()]
session_id: Annotated[str | None, Cookie()]
```

Značenja:

`Query()` -> query string (primer: `?skip=20&limit=10`)
`Path()` -> URL path (primer: `/todos/{todo_id}`)
`Header()` -> HTTP header (primer: `User-Agent`)
`Cookie()` -> cookie (primer: `session_id=abc123`)
`Body()` -> request body (primer: `{"key": "value"}`)
`Depends()` -> dependency funkcija ili klasa (primer: `Depends(get_current_user)`)

Svi ovi izrazi daju FastAPI-ju `metadata`, ali samo `Depends` opisuje `dependency lanac`.

---

## 27. Caching dependency-ja u jednom request-u

FastAPI po defaultu kešira rezultat dependency-ja unutar jednog request-a.

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

Za isti request FastAPI obično poziva `get_current_user` jednom i koristi rezultat na oba mesta.

```text
jedan request
	-> get_current_user() jednom
		-> first_user = rezultat
		-> second_user = isti rezultat
```

Ako namerno želimo ponovno izvršavanje:

```python
Depends(get_value, use_cache=False)
```

Ovo važi samo za jedan request. Nije trajna memorija i ne deli rezultat između različitih request-ova.

---

## 28. Sync i async dependency funkcije

Dependency može biti sinhrona:

```python
def get_settings():
	return Settings()
```

ili asinhrona:

```python
async def get_current_user():
	return user
```

Endpoint može koristiti oba oblika:

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

FastAPI zna da sačeka asinhroni dependency. Sinhroni dependency takođe može da koristi i asinhroni endpoint; FastAPI upravlja načinom izvršavanja.

Praktično pravilo:

```text
ne biraj async samo zato što izgleda modernije
biraj oblik koji odgovara operaciji i biblioteci
```

---

## 29. Redosled izvršavanja

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

Resurs koji je otvoren kasnije obično se zatvara ranije. Za bazu to znači da se `db.close()` izvršava nakon endpointa i dependency-ja koji koriste bazu.

---

## 31. Globalni objekat naspram dependency-ja

Možemo imati globalnu konfiguraciju:

```python
settings = Settings()
```

I dependency koja je vraća:

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

Dependency dodaje kontrolisanu granicu i omogućava override:

```python
def override_settings():
	return TestSettings()


app.dependency_overrides[get_settings] = override_settings
```

Ovo je korisno kada produkcijska konfiguracija koristi environment promenljive ili spoljne servise.

---

## 32. Dependency kao granica odgovornosti

Dobar dependency ima jednu jasnu odgovornost:

```text
get_db             -> dobavi i zatvori bazu
get_current_user   -> identifikuj korisnika
require_admin      -> proveri admin privilegiju
get_pagination     -> obradi paginaciju (lista rezultata podeljena na strane ili delove u kojima se prikazuju rezultati endpointa)
get_request_id     -> pročitaj request ID
```

Prevelik dependency bi radio sve:

```text
pročitaj token
dekodiraj JWT
pronađi korisnika
proveri role
pročitaj todo
pošalji email
```

Bolje je napraviti mali lanac:

```text
oauth2_scheme
	-> get_current_user
		-> require_admin
			-> endpoint
```

Svaki sloj dobija jednu glavnu odgovornost i lakše se testira.

---

## 33. Dependency i servisna funkcija

Servisna funkcija se poziva iz poslovne logike:

```python
def calculate_total(items: list[Item]) -> float:
	return sum(item.price for item in items)
```

Dependency se rešava pre endpointa:

```python
def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
):
	...
```

Razlika je u tome ko upravlja pozivom:

```text
običnu funkciju poziva tvoj kod
dependency poziva FastAPI dependency sistem
```

Servisna funkcija može biti pozvana iz dependency-ja:

```python
def verify_token(token: str) -> str:
	...


def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)],
):
	username = verify_token(token)
	...
```

---

## 34. Security redosled za buduci TodoApp

Praktični security lanac treba čitati ovako:

```text
1. oauth2_scheme čita Authorization header
2. JWT decoder proverava potpis i expiration
3. payload daje identitet kroz sub claim
4. get_current_user čita korisnika iz baze
5. proverava se is_active
6. require_admin ili ownership dependency proverava dozvolu
7. endpoint izvršava poslovnu operaciju
```

Dependency može sakriti korake 1 do 5 od endpointa, ali ih ne uklanja. Oni i dalje moraju biti tačno implementirani.

Samo postojanje `current_user` ne znači automatski da korisnik sme da menja svaki todo. Ownership uslov mora biti primenjen u query-ju ili kroz poseban dependency.

---

## 35. Vežba: ručno simuliraj FastAPI

Za ovaj endpoint:

```python
@router.get("/todos")
async def get_todos(
	db: db_dependency,
	current_user: Annotated[Users, Depends(get_current_user)],
):
	return {"user_id": current_user.id}
```

napiši redosled koji FastAPI mora da izvrši:

```text
1. Pozvati get_db
2. Dobiti Session
3. Pročitaj bearer token
4. Dekodiraj token
5. Pronađi korisnika
6. Pozovi get_todos(db, current_user)
7. Zatvori Session
```

Ako možeš da objasniš ovaj redosled, razumeš osnovu dependency injection-a.

---

## 36. Vežba: prepoznaj dependency

Odredi ulogu svakog izraza:

```python
get_db
db_dependency
db
Depends(get_db)
db.query(Todo).all()
```

Rešenje:

```text
get_db               -> dependency funkcija
db_dependency        -> reusable dependency alias
db                    -> vrednost ubacena u endpoint
Depends(get_db)       -> instrukcija FastAPI-ju
db.query(Todo).all()  -> query/poslovna operacija
```

---

## 37. Završni mentalni model

Kada vidiš:

```python
value: Annotated[SomeType, Depends(some_dependency)]
```

pročitaj ga ovako:

```text
Endpoint ima parametar value.
Očekuje se da value bude SomeType.
FastAPI ne očekuje da endpoint sam napravi value.
FastAPI rešava some_dependency (some_dependency je dependency funkcija koja vraća vrednost koja će biti ubačena u value).
Rezultat dependency-ja ubacuje u value.
```

Kada vidiš:

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

pročitaj ga ovako:

```text
Napravljen je reusable opis.
Parametar koji koristi alias dobija Session.
Session se dobavlja pozivom get_db.
get_db upravlja lifecycle-om kroz yield i finally.
```

Kada vidiš:

```python
current_user: Annotated[Users, Depends(get_current_user)]
```

pročitaj ga ovako:

```text
Endpoint zahteva identifikovanog korisnika.
FastAPI pre endpointa čita i validira token.
Pronađe korisnika u bazi.
Ako provera ne uspe, endpoint se ne poziva.
Ako uspe, endpoint dobija Users objekat.
```

To je suština `FastAPI dependency injection` sistema.
