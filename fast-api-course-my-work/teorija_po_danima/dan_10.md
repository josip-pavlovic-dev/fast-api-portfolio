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
