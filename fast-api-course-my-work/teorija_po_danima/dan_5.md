# Dan 5 - Users model, Pydantic schemas i response tipovi

Ovaj dokument predstavlja beleške za početak današnjeg rada.

Danas smo postavili prvi korak ka authentication delu aplikacije: u SQLAlchemy modele je dodat `Users` model. Nakon toga se pojavila greška prilikom pokretanja FastAPI aplikacije, a zatim i statička type-checking greška u `todos.py`.

Današnji rad je važan zato što povezuje tri različita sloja:

```text
SQLAlchemy model
	-> predstavlja tabelu i red iz baze

Pydantic schema
	-> definiše podatke koje API prima ili vraća

FastAPI endpoint
	-> povezuje HTTP zahtev, bazu i response
```

Glavna lekcija dana je:

> SQLAlchemy model i Pydantic response schema nisu ista stvar, čak i kada imaju slična polja.

---

## Pitanje 1

PITANJE: Ubacio sam tabelu `Users`, odnosno klasu `Users`, u `models.py`, ali se pri pokretanju servera javlja greška:

```text
FastAPIError: Invalid args for response field!
Hint: check that list[TodoApp.models.Todos] is a valid Pydantic field type.
```

Da li treba da dodam nove klase `UserRequest` i `UserResponse` u `schemas.py`?

---

## Odgovor 1

ODGOVOR: Da, `UserRequest` i `UserResponse` treba dodati u `schemas.py` kada počnemo da pravimo user endpoint-e. Međutim, same Users klase nisu direktan uzrok ove konkretne greške.

Direktan uzrok je bio u tome što su Todo endpoint-i imali povratne tipove SQLAlchemy modela:

```python
async def get_all(db: db_dependency) -> list[Todos]:
	...

async def read_todo(...) -> Todos:
	...

async def create_todo(...) -> Todos:
	...
```

FastAPI koristi return type anotaciju da napravi response model. `Todos` je SQLAlchemy model, a FastAPI response model treba da bude Pydantic model koji može da opiše i validira API response.

Zato je za response potrebno koristiti `TodoResponse`, a za buduće user endpoint-e `UserRequest` i `UserResponse`.

---

### Objašnjenje 1: SQLAlchemy model naspram Pydantic schema

U `models.py` trenutno imamo `SQLAlchemy` modele:

```python
class Todos(Base):
	__tablename__ = "todos"

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String)
	description = Column(String)
	priority = Column(Integer)
	complete = Column(Boolean, default=False)
	owner_id = Column(Integer, ForeignKey("users.id"))


class Users(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String, unique=True)
	username = Column(String, unique=True)
	first_name = Column(String)
	last_name = Column(String)
	hashed_password = Column(String)
	is_active = Column(Boolean, default=True)
	role = Column(String)
```

Ove klase opisuju bazu:

- `__tablename__` određuje ime tabele
- `Column` određuje kolonu
- `primary_key=True` određuje primarni ključ
- `ForeignKey("users.id")` povezuje Todo sa user tabelom
- `unique=True` sprečava duplikate u bazi
- `default=True` određuje podrazumevanu vrednost u bazi

`SQLAlchemy model` prvenstveno služi za `rad sa bazom`.

`Pydantic schema` opisuje `API podatke`:

```python
class TodoRequest(BaseModel):
	title: str
	description: str
	priority: int
	complete: bool
```

Ona služi za `validaciju` request body-ja koji dolazi od klijenta.

`Response schema` služi za podatke koji se vraćaju klijentu:

```python
class TodoResponse(BaseModel):
	id: int
	title: str
	description: str
	priority: int
	complete: bool

	model_config = ConfigDict(from_attributes=True)
```

`model_config` omogućava Pydantic-u da pročita atribute iz SQLAlchemy modela.
`ConfigDict` je klasa koja omogućava konfiguraciju Pydantic modela. Nju importujemo iz `pydantic`. Njeni argumenti definišu kako će Pydantic model interpretirati podatke. Na primer, `from_attributes=True` govori Pydantic-u da čita podatke iz atributa objekta (SQLAlchemy instance naprimer iz `Todos` modela), a ne samo iz dictionary-like struktura (naprimer `class TodoRequest(BaseModel): {"title": "My Todo", "description": "Description"}`).

Primer:

```python
todo_model = Todos(
	id=1,
	title="My Todo",
	description="Description",
	priority=1,
	complete=False,
	owner_id=1
)

todo_response = TodoResponse.from_orm(todo_model)
print(todo_response.dict())

# Output:
# {'id': 1, 'title': 'My Todo', 'description': 'Description', 'priority': 1, 'complete': False}
```

Zato imamo tri različita `koncepta`:

```text
Todos
	SQLAlchemy model za bazu

TodoRequest
	Pydantic schema za ulazni request

TodoResponse
	Pydantic schema za izlazni response
```

---

### Objašnjenje 2: Zašto FastAPI ne prihvata `list[Todos]` kao response model

Kada FastAPI vidi:

```python
async def get_all(db: db_dependency) -> list[Todos]:
	return db.query(Todos).all()
```

ono pokušava da od `list[Todos]` napravi response field.

Problem je što `Todos` nasleđuje SQLAlchemy `Base`, a ne Pydantic `BaseModel`.

Drugim rečima:

```python
class Todos(Base):
	...
```

nije isto što i:

```python
class TodoResponse(BaseModel):
	...
```

FastAPI/Pydantic response sloj ne treba direktno da koristi SQLAlchemy klasu kao javni API ugovor.

Greška zato kaže da `list[TodoApp.models.Todos]` nije validno Pydantic polje.

To ne znači da SQLAlchemy query ne radi. Query radi i vraća SQLAlchemy objekte. Problem nastaje kada FastAPI treba da razume kako te objekte da predstavi kao API response.

---

### Objašnjenje 3: Uloga `TodoResponse`

U `schemas.py` već postoji:

```python
class TodoResponse(BaseModel):
	id: int
	title: str
	description: str
	priority: int
	complete: bool

	model_config = ConfigDict(from_attributes=True)
```

Podešavanje:

```python
model_config = ConfigDict(from_attributes=True)
```

omogućava Pydantic-u da podatke pročita iz atributa SQLAlchemy objekta.

Bez toga Pydantic očekuje uglavnom dictionary-like podatke. Sa `from_attributes=True`, može da pročita:

```python
todo_model.title
todo_model.description
todo_model.priority
```

iz SQLAlchemy instance.

---

### Objašnjenje 4: User schema klase

Dodate su i pripremne klase za budući authentication kod:

```python
class UserRequest(BaseModel):
	email: str
	username: str
	first_name: str
	last_name: str
	password: str
```

`UserRequest` predstavlja podatke koje klijent može poslati prilikom kreiranja user-a.

Password je ovde plain tekst samo na ulazu u aplikaciju. On ne sme biti direktno sačuvan u bazi. Kasnije će se pre upisa izvršiti hashing:

```text
request password
	-> password hashing
		-> Users.hashed_password
```

Response schema ne treba da vrati ni plaintext password ni hash:

```python
class UserResponse(BaseModel):
	id: int
	email: str
	username: str
	first_name: str
	last_name: str
	is_active: bool
	role: str

	model_config = ConfigDict(from_attributes=True)
```

Namerno nema:

```python
password: str
hashed_password: str
```

To sprečava da password podaci slučajno postanu deo javnog API response-a.

Važno je razlikovati:

```text
UserRequest
	podaci koje klijent šalje

UserResponse
	bezbedni podaci koje server vraća

Users
	kompletan database model, uključujući hashed_password
```

---

### Objašnjenje 5: Modeli i schema klase imaju različite granice

SQLAlchemy model može sadržati podatke koji nikada ne smeju otići klijentu:

```python
hashed_password
```

Pydantic response schema može namerno sakriti ta polja.

To je jedna od glavnih prednosti odvajanja modela i schema:

```text
database model
	ne mora biti
API response model
```

Ovo odvajanje omogućava:

- bezbednije response-e
- jasnu validaciju ulaza
- stabilniji javni API
- promenu baze bez automatske promene API ugovora
- sprečavanje curenja internih kolona

---

### Izmena u `todos.py`

Pre problema endpoint je imao:

```python
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency) -> list[Todos]:
	return db.query(Todos).all()
```

Prvi pokušaj da se samo promeni anotacija u:

```python
async def get_all(db: db_dependency) -> list[TodoResponse]:
```

nije dovoljan, jer query i dalje vraća:

```python
list[Todos]
```

Funkcija je tada obećala `list[TodoResponse]`, ali je stvarno vraćala `list[Todos]`.

To su različiti Python tipovi.

---

## Pitanje 2

PITANJE: Nakon izmene pojavila se greška:

```text
Type "List[Todos]" is not assignable to return type "list[TodoResponse]"
```

Poruka objašnjava da nije moguće vratiti listu klase `TodoResponse`. Kako treba rešiti problem?

---

## Odgovor 2

ODGOVOR: Query vraća listu SQLAlchemy objekata `Todos`, a funkcija je označena da vraća listu Pydantic objekata `TodoResponse`. Zato treba eksplicitno konvertovati svaki `Todos` objekat u `TodoResponse` pomoću:

```python
TodoResponse.model_validate(todo)
```

Za listu se koristi list comprehension:

```python
todo_models = db.query(Todos).all()

return [
	TodoResponse.model_validate(todo)
	for todo in todo_models
]
```

Sada funkcija zaista vraća `list[TodoResponse]`, a ne samo tvrdi kroz anotaciju da to radi.

---

## Pitanje 3

PITANJE: Da li se `model_validate` koristi u modernom programiranju ili postoji drugi način da se poveže SQLAlchemy model sa Pydantic schemom?

Ako ne stavim liniju:

```python
    model_config = ConfigDict(from_attributes=True)
```

Već False, da li šta menjam time tačno osim što Pydantic ne može da čita atribute iz class Todos i Class Users?

---

## Odgovor 3

ODGOVOR: Ako ne stavite liniju `model_config = ConfigDict(from_attributes=True)`, Pydantic neće moći da čita atribute iz SQLAlchemy modela `Todos` i `Users`. To znači da `model_validate` neće moći da konvertuje SQLAlchemy objekte u Pydantic objekte, i dobićete greške prilikom pokušaja validacije ili kreiranja Pydantic instanci iz SQLAlchemy objekata.

### Detaljno objašnjenje

Da, `model_validate()` je moderan i preporučen način u **Pydantic v2**.

```python
TodoResponse.model_validate(todo_model)
```

On validira SQLAlchemy objekat i pravi Pydantic objekat `TodoResponse`.

U Pydantic v1 koristio se stariji način:

```python
TodoResponse.from_orm(todo_model)
```

Dakle:

```text
Pydantic v1 -> from_orm()
Pydantic v2 -> model_validate() + from_attributes=True
```

---

#### Šta radi `from_attributes=True`?

```python
model_config = ConfigDict(from_attributes=True)
```

Dozvoljava Pydantic-u da čita atribute iz SQLAlchemy instance:

```python
todo_model.id
todo_model.title
todo_model.complete
```

Bez toga, Pydantic očekuje dictionary:

```python
{
    "id": 1,
    "title": "Learn FastAPI",
    "description": "Practice",
    "priority": 1,
    "complete": False,
}
```

Ako napišeš:

```python
model_config = ConfigDict(from_attributes=False)
```

ili potpuno ukloniš tu liniju, ovo najverovatnije neće raditi:

```python
TodoResponse.model_validate(todo_model)
```

jer je `todo_model` SQLAlchemy objekat, a ne dictionary.

Ali ovo će raditi:

```python
TodoResponse.model_validate({
    "id": todo_model.id,
    "title": todo_model.title,
    "description": todo_model.description,
    "priority": todo_model.priority,
    "complete": todo_model.complete,
})
```

Zaključak:

```python
model_config = ConfigDict(from_attributes=True)
```

Koristimo kada Pydantic treba direktno da čita SQLAlchemy objekte. Isto važi za `TodoResponse` i `UserResponse`.

Ne menjaš SQLAlchemy model niti podatke u bazi. Menjaš samo način na koji Pydantic dobavlja podatke iz ORM objekta.

---

## SQLAlchemy query i Pydantic model_validation (objašnjeno)

### Objašnjenje 1: Šta vraća SQLAlchemy query

Ovaj kod:

```python
todo_models = db.query(Todos).all()
```

vraća:

```text
list[Todos]
```

Svaki element liste je SQLAlchemy objekat. To znači da je svaki element instance klase `Todos` SQLAlchemy model (instancom klase `Todos` dobijamo jedan pojedinačni zapis iz tabele `todos`, jedan red u bazi, jedan `Todo` objekat sa svim atributima definisanim u SQLAlchemy modelu (`models.py`), a ne Pydantic objekat (schema.`TodoResponse`)).

Primer jednog SQLAlchemy objekta iz liste Todos:

```python
Todos(
	id=1,
	title="Learn FastAPI",
	description="Practice schemas",
	priority=1,
	complete=False,
)
```

To nije Pydantic objekat.

Pydantic objekat nastaje tek kada pozovemo:

```python
TodoResponse.model_validate(todo_model)
```

---

### Objašnjenje 2: `model_validate()`

`model_validate()` pravi i validira Pydantic instancu iz ulaznog objekta.

Kod našeg response modela:

```python
TodoResponse.model_validate(todo_model)
```

Pydantic čita atribute iz `todo_model` zato što `TodoResponse` ima:

```python
model_config = ConfigDict(from_attributes=True)
```

Rezultat je objekat tipa:

```text
TodoResponse
```

Za listu se transformacija radi element po element:

```python
todo_models = db.query(Todos).all()
todo_responses = [
	TodoResponse.model_validate(todo_model)
	for todo_model in todo_models
]

return todo_responses
```

Tipovi su sada dosledni:

```text
todo_models     -> list[Todos]
todo_responses  -> list[TodoResponse]
return          -> list[TodoResponse]
```

---

### Objašnjenje 3: Konačna `get_all` funkcija

Konačna verzija je:

```python
@router.get(
	"/",
	status_code=status.HTTP_200_OK,
)
async def get_all(db: db_dependency) -> list[TodoResponse]:
	todo_models = db.query(Todos).all()
	return [TodoResponse.model_validate(todo) for todo in todo_models]
```

Ona radi u sledećim koracima:

```text
1. FastAPI dobavlja database session kroz db_dependency
2. SQLAlchemy izvršava query nad tabelom todos
3. query vraća list[Todos]
4. list comprehension prolazi kroz svaki Todos objekat
5. model_validate pravi TodoResponse objekat
6. funkcija vraća list[TodoResponse]
```

Ovaj kod je statički dosledan i runtime ispravan.

---

### Objašnjenje 4: Konačni `read_todo` endpoint

Za jedan zapis koristi se ista ideja:

```python
@router.get(
	"/{todo_id}",
	status_code=status.HTTP_200_OK,
)
async def read_todo(
	db: db_dependency,
	todo_id: int = Path(
		gt=0,
		description="ID todo zadatka mora biti veći od nule.",
	),
) -> TodoResponse:
	todo_model = (
		db.query(Todos)
		.filter(Todos.id == todo_id)
		.first()
	)

	if todo_model is not None:
		return TodoResponse.model_validate(todo_model)

	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail="Todo nije pronađen.",
	)
```

Ovde query vraća:

```text
Todos ili None
```

Posle provere `is not None`, objekat se konvertuje u:

```text
TodoResponse
```

Ako objekat ne postoji, endpoint ne pokušava da ga konvertuje, već vraća `404 Not Found`.

---

### Objašnjenje 5: Konačni `create_todo` endpoint

Kod kreiranja, SQLAlchemy model nastaje ovako:

```python
todo_model = Todos(**todo_request.model_dump())
```

Nakon commit-a i refresh-a, model se konvertuje pre vraćanja:

```python
@router.post(
	"/",
	status_code=status.HTTP_201_CREATED,
)
async def create_todo(
	db: db_dependency,
	todo_request: TodoRequest,
) -> TodoResponse:
	todo_model = Todos(**todo_request.model_dump())

	db.add(todo_model)
	db.commit()
	db.refresh(todo_model)

	return TodoResponse.model_validate(todo_model)
```

`db.refresh(todo_model)` je važan kod POST-a jer baza može popuniti vrednosti kao što su:

- generisani `id`
- podrazumevane vrednosti
- vrednosti koje baza izračunava

Tek posle refresh-a response predstavlja sveže stanje zapisa u bazi.

---

### Objašnjenje 6: Zašto nije dovoljno samo promeniti anotaciju

Ovo nije dovoljno:

```python
async def get_all(db: db_dependency) -> list[TodoResponse]:
	return db.query(Todos).all()
```

Razlog:

```text
obećani tip: list[TodoResponse]
stvarni tip: list[Todos]
```

Return annotation nije konverzija. Ona samo opisuje šta funkcija treba da vrati.

Da bi se objekat zaista promenio, potrebna je operacija:

```python
TodoResponse.model_validate(todo)
```

Ovo je važna opšta lekcija iz tipiziranja:

> Anotacija tipa ne menja vrednost. Ona opisuje vrednost i omogućava proveru grešaka.

---

### Objašnjenje 7: Zašto je `list` invariant

Pylance prijavljuje i deo:

```text
Type parameter "_T@list" is invariant
```

To znači da Python type checker ne smatra da je:

```text
list[Todos]
```

automatski isto što i:

```text
list[TodoResponse]
```

Čak i kada bi klase imale neku vezu, mutable liste su invariantne jer ih možemo menjati.

Ali ovde problem nije samo teorija o varijanci. `Todos` i `TodoResponse` su zaista različite klase i treba ih eksplicitno konvertovati.

Zato nije dobro samo menjati `list` u `Sequence` kao masku za problem. Pravi korak je konverzija modela u schema objekte.

---

### Objašnjenje 8: Uloga FastAPI response modela

FastAPI može da koristi return anotaciju kao response model:

```python
async def get_all(...) -> list[TodoResponse]:
```

Može se koristiti i eksplicitno:

```python
@router.get("/", response_model=list[TodoResponse])
```

Ali `response_model` sam po sebi ne rešava problem statičkog tipa u funkciji. On opisuje kako FastAPI treba da validira i dokumentuje response.

Ako funkcija vraća SQLAlchemy objekte direktno, FastAPI može da ih serijalizuje kada schema ima `from_attributes=True`. Međutim, Pylance može i dalje prijaviti da funkcija vraća `list[Todos]`, a anotirana je kao `list[TodoResponse]`.

Zato je u našem trenutnom kodu urađena eksplicitna konverzija:

```python
return [TodoResponse.model_validate(todo) for todo in todo_models]
```

Time su istovremeno zadovoljeni:

- Python type checker
- Pydantic
- FastAPI response dokumentacija
- odvajanje baze od javnog API-ja

---

## Pregled današnjih izmena

### Izmena 1 - dodat `Users` model

U `models.py` dodat je:

```python
class Users(Base):
	__tablename__ = "users"
	...
```

To priprema bazu za:

- registraciju korisnika
- login
- password hash
- JWT
- ownership Todo zapisa

---

### Izmena 2 - `Todos.owner_id`

Todo model sadrži:

```python
owner_id = Column(Integer, ForeignKey("users.id"))
```

To znači da Todo može biti povezan sa user-om preko `users.id`.

Trenutno još nema authorization filtera. Sama foreign key kolona ne sprečava korisnika da vidi ili menja tuđi Todo. To će doći kasnije kroz current user i ownership proveru.

---

### Izmena 3 - dodat `UserRequest`

```python
class UserRequest(BaseModel):
	email: str
	username: str
	first_name: str
	last_name: str
	password: str
```

Ovo je ulazna schema za buduće kreiranje user-a.

---

### Izmena 4 - dodat `UserResponse`

```python
class UserResponse(BaseModel):
	id: int
	email: str
	username: str
	first_name: str
	last_name: str
	is_active: bool
	role: str

	model_config = ConfigDict(from_attributes=True)
```

Ovo je bezbedna response schema bez password polja.

---

### Izmena 5 - Todo endpointi koriste Pydantic response

Za listu:

```python
todo_models = db.query(Todos).all()
return [TodoResponse.model_validate(todo) for todo in todo_models]
```

Za jedan zapis:

```python
return TodoResponse.model_validate(todo_model)
```

Za kreiranje:

```python
db.refresh(todo_model)
return TodoResponse.model_validate(todo_model)
```

---

## Konačna struktura razmene podataka

### GET lista

```text
GET /todos/
	-> db.query(Todos).all()
		-> list[Todos]
			-> model_validate svaki element
				-> list[TodoResponse]
					-> JSON response
```

---

### GET jedan Todo

```text
GET /todos/{todo_id}
	-> query
		-> Todos ili None
			-> 404 ili TodoResponse
				-> JSON response
```

---

### POST Todo

```text
POST /todos/
	-> TodoRequest
		-> model_dump()
			-> Todos SQLAlchemy model
				-> db.add
					-> db.commit
						-> db.refresh
							-> TodoResponse
```

---

### User registracija u budućnosti

```text
POST /auth/create_user
	-> UserRequest
		-> password hashing
			-> Users model
				-> db.commit
					-> UserResponse
```

---

## Najvažnije greške koje treba zapamtiti

### Greška 1 - SQLAlchemy model kao response annotation

Problematično:

```python
async def get_all(...) -> list[Todos]:
```

Bolje:

```python
async def get_all(...) -> list[TodoResponse]:
```

uz stvarnu konverziju:

```python
return [TodoResponse.model_validate(todo) for todo in todo_models]
```

---

### Greška 2 - samo promenjena anotacija

Problematično:

```python
async def get_all(...) -> list[TodoResponse]:
	return db.query(Todos).all()
```

Anotacija i stvarna vrednost se ne slažu.

---

### Greška 3 - password u response schemi

Ne treba:

```python
class UserResponse(BaseModel):
	hashed_password: str
```

Response treba da sadrži samo podatke koje klijent sme da vidi.

---

### Greška 4 - mešanje database i API odgovornosti

`models.py` ne treba koristiti kao zamenu za `schemas.py`.

```text
models.py  -> baza
schemas.py -> API ulaz/izlaz
```

---

### Greška 5 - verovanje da `from_attributes` vrši konverziju sam od sebe

`from_attributes=True` omogućava Pydantic-u da čita atribute iz ORM objekta, ali je i dalje potrebno pozvati:

```python
TodoResponse.model_validate(todo_model)
```

---

## Pitanja za ponavljanje

1. Koja je razlika između SQLAlchemy modela i Pydantic schema klase?

Odgovor: Razlika je u tome što SQLAlchemy modeli predstavljaju strukturu baze podataka i koriste se za interakciju sa bazom, dok Pydantic schema klase definišu kako podaci ulaze i izlaze iz API-ja, uključujući validaciju i serijalizaciju.

2. Zašto `Todos` nije dobar FastAPI response model?

Odgovor: Zato što predstavlja SQLAlchemy model, a ne Pydantic schema. FastAPI očekuje Pydantic modele za response kako bi mogao da vrši validaciju i serijalizaciju.

3. Šta vraća `db.query(Todos).all()`?

Odgovor: Vraća listu SQLAlchemy model objekata tipa `Todos`.

4. Šta radi `TodoResponse.model_validate(todo)`?

Odgovor: Konvertuje SQLAlchemy model objekat `todo` u Pydantic model `TodoResponse`, omogućavajući validaciju i serijalizaciju podataka za API response.

5. Zašto je za listu potreban list comprehension?

Odgovor: Zato što `db.query(Todos).all()` vraća listu SQLAlchemy model objekata, a potrebno je konvertovati svaki objekat u Pydantic model koristeći `TodoResponse.model_validate(todo)`. List comprehension omogućava da se konverzija primeni na sve elemente liste.

6. Šta omogućava `ConfigDict(from_attributes=True)`?

Odgovor: Omogućava Pydantic modelu da čita atribute iz ORM objekta, što olakšava konverziju SQLAlchemy modela u Pydantic modele bez potrebe za ručnim mapiranjem polja.

7. Zašto `UserRequest` može imati `password`, a `UserResponse` ne treba?

Odgovor: `UserRequest` može imati `password` jer je to podatak koji korisnik unosi prilikom registracije ili promene lozinke, dok `UserResponse` ne treba da sadrži `password` iz bezbednosnih razloga, kako se lozinka ne bi slala nazad klijentu.

8. Zašto se `hashed_password` čuva u modelu, ali ne vraća u response-u?

Odgovor: `hashed_password` se čuva u modelu kako bi se mogla vršiti autentifikacija korisnika, ali se ne vraća u response-u iz bezbednosnih razloga, kako se lozinka ne bi izlagala klijentu.

9. Zašto samo promena return anotacije ne konvertuje objekat?

Odgovor: Promena return anotacije ne konvertuje objekat jer FastAPI ne vrši automatsku konverziju SQLAlchemy modela u Pydantic modele. Potrebno je eksplicitno pozvati `TodoResponse.model_validate(todo)` ili koristiti list comprehension za liste.

10. Koja je razlika između `list[Todos]` i `list[TodoResponse]`?

Odgovor: `list[Todos]` je lista SQLAlchemy model objekata, dok je `list[TodoResponse]` lista Pydantic model objekata. FastAPI očekuje Pydantic modele za response kako bi mogao da vrši validaciju i serijalizaciju.

11. Šta se dešava ako Todo ne postoji u `read_todo` endpointu?

Odgovor: Ako Todo ne postoji, obično se vraća `None` iz baze, što može izazvati grešku pri konverziji u Pydantic model. Potrebno je rukovati ovim slučajem, npr. vraćanjem HTTP 404 odgovora.

12. Zašto se kod POST-a koristi `db.refresh()` pre pravljenja response-a?

Odgovor: `db.refresh()` osvežava SQLAlchemy model objekat sa podacima iz baze, uključujući automatski generisana polja kao što je `id`, pre nego što se konvertuje u Pydantic model za response.

13. Da li samo dodavanje `Users` modela automatski završava authentication funkcionalnost?

Odgovor: Ne, dodavanje `Users` modela samo definiše strukturu korisnika u bazi. Autentifikacija zahteva dodatnu logiku za registraciju, login, hashovanje lozinke i verifikaciju tokena.

14. Šta još nedostaje za stvarni login?

Odgovor: Potrebno je implementirati endpoint za login koji proverava korisničke kredencijale, generiše i vraća JWT token, i eventualno middleware za zaštitu ruta koristeći taj token.

---

## Kratki praktični zadaci

### Zadatak 1 - Prepoznaj sloj

Razvrstaj sledeće stavke:

```text
Column(Integer, primary_key=True)
Field(min_length=3)
model_validate()
ForeignKey("users.id")
hashed_password
HTTP response
```

Koristi kategorije:

```text
SQLAlchemy model
Pydantic schema
API response
```

---

### Zadatak 2 - Napiši tipove kroz tok

Popuni tipove:

```text
db.query(Todos).all()       ->
TodoResponse.model_validate ->
lista posle konverzije      ->
```

---

### Zadatak 3 - Pronađi grešku

Objasni zašto je ovo problem:

```python
async def get_all(db: db_dependency) -> list[TodoResponse]:
	return db.query(Todos).all()
```

Prepravi funkciju tako da tipovi budu usklađeni.

### Zadatak 4 - User response bez tajnih podataka

---

Napiši `UserResponse` koji sadrži:

- `id`
- `username`
- `email`
- `is_active`
- `role`

Proveri da nema `password` ni `hashed_password` polje.

---

### Zadatak 5 - Objasni `from_attributes`

Svojim rečima objasni šta se dešava u:

```python
TodoResponse.model_validate(todo_model)
```

ako je uključeno:

```python
model_config = ConfigDict(from_attributes=True)
```

---

### Zadatak 6 - Nacrtaj POST tok

Nacrtaj sledeći tok bez gledanja u materijal:

```text
TodoRequest
	-> model_dump
		-> Todos
			-> db.add
				-> db.commit
					-> db.refresh
						-> TodoResponse
```

---

### Zadatak 7 - Razmisli o Users tabeli

Odgovori:

1. Zašto `Users` model ima `hashed_password`, a ne `password`?

Odgovor: Zato što želimo da korisnici unose lozinku u čistom obliku prilikom registracije ili prijave, a ne njen hash. Hash se generiše na serveru i čuva u bazi. Ostavljanje polja `password` u modelu koji se čuva u bazi bi predstavljalo sigurnosni rizik.

2. Zašto `UserRequest` ipak prima `password`?

Odgovor: Zato što `UserRequest` predstavlja podatke koje korisnik šalje prilikom registracije ili prijave, i u tom kontekstu je potrebno primiti lozinku u čistom obliku kako bi se mogla hashovati i sačuvati u bazi. Ostavljanje polja `hashed_password` u `UserRequest` ne bi imalo smisla jer korisnik ne treba da šalje hash, već samo čistu lozinku.

3. Gde će se password hashovati?

Odgovor: Password će se hashovati na serveru, obično u funkciji koja obrađuje registraciju korisnika pre nego što se podaci sačuvaju u bazi.

4. Zašto `Todos.owner_id` sam po sebi još ne štiti endpoint?

Odgovor: `Todos.owner_id` samo čuva informaciju o vlasniku zapisa, ali ne implementira nikakvu logiku za proveru da li trenutni korisnik ima pravo da pristupi ili modifikuje taj zapis. Za pravu zaštitu endpoint-a potrebno je dodati autorizaciju koja proverava da li je korisnik vlasnik zapisa pre nego što mu se dozvoli pristup ili izmena.

---

## Današnji zaključak

Danas smo napravili prelaz sa Todo-only aplikacije ka aplikaciji koja ima osnovu za korisnike i authentication.

Najvažnije je da sada razumeš sledeću razliku:

```text
Todos
	objekat koji SQLAlchemy dobija iz baze

TodoResponse
	Pydantic objekat koji API vraća klijentu
```

Kada query vrati listu:

```python
list[Todos]
```

ne treba samo napisati anotaciju:

```python
list[TodoResponse]
```

već treba izvršiti konverziju:

```python
[
	TodoResponse.model_validate(todo)
	for todo in todo_models
]
```

Tako su usklađeni:

- SQLAlchemy rezultat (model instance)
- Pydantic schema (model_validate result)
- FastAPI response (JSON serialized Pydantic model)
- statička provera tipova (mypy ili slični alati)

Dodavanje `Users` modela je prvi korak, ali authentication još nije završen. Sledeći koraci biće:

```text
1. schema za kreiranje user-a
2. password hashing
3. čuvanje user-a u bazi
4. login provera
5. JWT token
6. current user dependency
7. authorization i ownership Todo zapisa
```

Za današnje ponavljanje zapamti jednu rečenicu:

> SQLAlchemy model služi bazi, Pydantic schema služi API-ju, a `model_validate()` ih povezuje.
