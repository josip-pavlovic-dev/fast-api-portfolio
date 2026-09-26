# Dan 7 - `Annotated`, dependency alias i `response_model`

## 1) Pitanje iz `auth.py`

U aktivnom kodu imamo dva oblika:

```python
@router.post("/token")
async def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
	db: db_dependency,
):
	...
```

U `db/session.py` imamo:

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

A kod registracionog endpointa imamo:

```python
@router.post(
	"/",
	status_code=status.HTTP_201_CREATED,
	response_model=UserResponse,
)
```

Na prvi pogled deluje kao da se `Annotated` nekada piše sa `:`, a nekada sa `=`. U stvari, ovde se preklapaju tri različite stvari:

1. Python anotacija parametra (korišćenje `:` u definiciji funkcije)
2. Python promenljiva koja čuva `reusable alias` -> pointer na `Annotated` tip koji se može koristiti više puta (korišćenje `=` za dodeljivanje)
3. Imenovani argument FastAPI dekoratora (korišćenje `=` u pozivu dekoratora)

Najvažnije je prvo razumeti značenje `:` i `=` u Pythonu.

---

## 2) Šta znači `:` kod parametra funkcije

U ovom primeru:

```python
def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
	...
```

dvotačka (`:`) uvodi anotaciju parametra (tip ili dodatne informacije):

```text
ime_parametra: anotacija
```

Jednostavan Python primer (anotacije tipa):

```python
name: str
age: int
```

To znači:

```text
name bi trebalo da bude str
age bi trebalo da bude int
```

Anotacija sama po sebi uglavnom ne pretvara vrednost i ne izvršava funkciju. Ona opisuje tip ili dodatne informacije o parametru. FastAPI čita tu informaciju i koristi je da konstruiše `request` podatke (primarno iz HTTP zahteva) i `dependency objekte` (npr. baze podataka, servise, itd.).

U našem primeru:

```python
form_data: Annotated[
	OAuth2PasswordRequestForm,
	Depends(),
]
```

znači:

```text
form_data je objekat tipa OAuth2PasswordRequestForm
Depends() govori FastAPI-ju da taj objekat dobavi kao dependency,
a FastAPI će automatski proslediti odgovarajući objekat prilikom poziva funkcije.
```

### Detaljnije o Depends i dependency injection
---

## 3) Sta je `Annotated[T, metadata]`

Opsti oblik je:

```python
Annotated[tip, dodatne_informacije]
```

Na primer:

```python
Annotated[Session, Depends(get_db)]
```

ima dva dela:

```text
Session             -> Python tip vrednosti
Depends(get_db)     -> FastAPI metadata i instrukcija za dependency injection
```

Drugim recima, `Annotated` omogucava da jednom parametru pridruzimo i tip i dodatne informacije koje framework treba da procita.

Za login parametar:

```python
form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
```

Python deo razume osnovni tip `OAuth2PasswordRequestForm`, a FastAPI deo razume `Depends()`.

---

## 4) Zasto se nekada koristi `=`

Pogledajmo ovaj kod:

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Ovde `db_dependency` nije ime parametra funkcije. To je ime promenljive.

Znak `=` u ovom slucaju znaci dodeljivanje:

```text
vrednost_prom_enljive = vrednost
```

Dakle, Python prvo napravi ovaj `Annotated` izraz:

```python
Annotated[Session, Depends(get_db)]
```

i zatim ga sacuva pod imenom:

```python
db_dependency
```

Mozemo to zamisliti ovako:

```python
db_dependency = "Session + Depends(get_db)"
```

Samo sto je stvarna vrednost strukturisana typing/FastAPI informacija, a ne tekst.

Kasnije se alias koristi kao anotacija parametra:

```python
async def create_users(
	create_user_request: CreateUserRequest,
	db: db_dependency,
):
	...
```

Ovo je priblizno isto kao da smo napisali pun izraz direktno:

```python
async def create_users(
	create_user_request: CreateUserRequest,
	db: Annotated[Session, Depends(get_db)],
):
	...
```

Prednost aliasa je sto se isti dependency ne ponavlja u svakom endpointu.

---

## 5) Direktni oblik i reusable oblik

### Direktno u parametru

```python
async def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
	...
```

Ovde je `Annotated[...]` napisan direktno na mestu anotacije parametra.

Struktura je:

```text
parametar: anotacija
form_data: Annotated[...]
```

### Sacuvano u aliasu

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Ovde se prvo pravi reusable promenljiva, a zatim se koristi:

```python
db: db_dependency
```

Struktura je:

```text
alias = anotacija
parametar: alias
```

Zato ne postoji pravilo da se `Annotated` "nekada pise sa dvotackom, a nekada sa jednako". Isti `Annotated[...]` moze biti direktna anotacija ili vrednost dodeljena promenljivoj.

---

## 6) Poredjenje sa obicnim tipovima

Ovo:

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

ima istu Python ideju kao:

```python
text_type = str
number_type = int
```

A ovo:

```python
db: db_dependency
```

ima istu ideju kao:

```python
name: text_type
age: number_type
```

U prvom primeru `=` pravi alias. U drugom primeru `:` govori koji alias se koristi kao anotacija.

---

## 7) Zasto se `UserResponse` koristi kao `response_model=UserResponse`

Kod:

```python
@router.post(
	"/",
	status_code=status.HTTP_201_CREATED,
	response_model=UserResponse,
)
```

nije anotacija funkcijskog parametra. Ovo je poziv metode `router.post()` sa imenovanim argumentima.

Priblizno mozemo zamisliti dekorator ovako:

```python
router.post(
	path="/",
	status_code=status.HTTP_201_CREATED,
	response_model=UserResponse,
)
```

Ovde `response_model` prima vrednost `UserResponse`.

Znacenje je:

```text
Kada ovaj endpoint vrati odgovor,
koristi UserResponse kao pravilo za validaciju i serializaciju odgovora.
```

`UserResponse` je Pydantic schema, odnosno klasa koja opisuje javni oblik odgovora.

Ako ORM objekat korisnika sadrzi:

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

a `UserResponse` sadrzi samo:

```text
id
email
username
first_name
last_name
is_active
role
```

onda FastAPI vraca samo polja definisana u `UserResponse`. `hashed_password` se ne salje klijentu.

Zato je bezbedno da endpoint vrati ORM objekat:

```python
return create_user_model
```

FastAPI ga zatim obradi kroz:

```python
response_model=UserResponse
```

---

## 8) Razlika izmedju `response_model=UserResponse` i `-> UserResponse`

Ova dva zapisa su povezana, ali nisu potpuno ista:

```python
@router.post("/", response_model=UserResponse)
async def create_users(...) -> UserResponse:
	...
```

### `response_model=UserResponse`

Ovo je FastAPI konfiguracija dekoratora. Ona govori frameworku kako da:

- validira response
- serializuje response
- filtrira polja koja ne treba javno vratiti
- napravi OpenAPI/Swagger dokumentaciju

### `-> UserResponse`

Ovo je Python return type hint:

```python
def function(...) -> UserResponse:
	...
```

Znacenje je:

```text
Ocekuje se da funkcija vraca vrednost kompatibilnu sa UserResponse.
```

Return type hint pomaze editoru, type checker-u i citaocu koda. `response_model` je FastAPI instrukcija za stvarno ponasanje HTTP endpointa.

U ovom projektu koristimo oba:

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
	...
```

Prvi zapis konfigurise FastAPI, a drugi opisuje povratnu vrednost funkcije.

---

## 9) Da li `response_model` mora biti pre `status_code`

Ne mora.

Ovo:

```python
@router.post(
	"/",
	status_code=status.HTTP_201_CREATED,
	response_model=UserResponse,
)
```

i ovo:

```python
@router.post(
	"/",
	response_model=UserResponse,
	status_code=status.HTTP_201_CREATED,
)
```

imaju isto znacenje, zato sto su to imenovani argumenti funkcije/dekoratora.

Napomena o default parametrima koju si naveo odnosi se na drugi Python slucaj: definiciju funkcije.

Na primer, ovo nije dozvoljeno:

```python
def example(value: int = 10, name: str):
	...
```

Parametar bez default vrednosti ne moze ici posle parametra sa default vrednoscu. Ispravno je:

```python
def example(name: str, value: int = 10):
	...
```

Ali kod poziva funkcije sa imenovanim argumentima redosled nije takav problem:

```python
example(value=10, name="Ana")
```

Isto vazi za `status_code=` i `response_model=` u `@router.post(...)`: oba su imenovani argumenti dekoratora, a nisu parametri tvoje endpoint funkcije.

---

## 10) Tri slicna zapisa, tri razlicita znacenja

```python
db: db_dependency
```

Znaci: `db` je parametar sa anotacijom `db_dependency`.

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Znaci: napravi promenljivu/alias koji cuva `Annotated` izraz.

```python
response_model=UserResponse
```

Znaci: prosledi `UserResponse` kao imenovani argument FastAPI dekoratoru.

Vizuelno slicni znakovi pripadaju razlicitim Python konstrukcijama:

| Zapis                                   | Uloga znaka | Znacenje                             |
| --------------------------------------- | ----------- | ------------------------------------ |
| `db: db_dependency`                     | `:`         | anotacija parametra                  |
| `db_dependency = Annotated[...]`        | `=`         | dodela aliasa promenljivoj           |
| `response_model=UserResponse`           | `=`         | imenovani argument pozivu dekoratora |
| `def create_users(...) -> UserResponse` | `->`        | tip povratne vrednosti funkcije      |

---

## 11) Ponovljen tok lekcije 10

Pre nego sto predjemo na JWT, trenutni login tok treba razumeti ovako:

```text
POST /auth/token
	-> OAuth2PasswordRequestForm cita username i password
		-> db_dependency obezbedjuje SQLAlchemy Session
			-> authenticate_user() trazi korisnika po username-u
				-> bcrypt_context.verify() proverava password
					-> proverava se is_active
						-> validan user ili 401 greska
```

U kodu:

```python
authenticated_user = authenticate_user(
	form_data.username,
	form_data.password,
	db,
)
```

Ako korisnik ne postoji, password nije ispravan ili korisnik nije aktivan:

```python
raise HTTPException(
	status_code=status.HTTP_401_UNAUTHORIZED,
	detail="Could not validate user",
	headers={"WWW-Authenticate": "Bearer"},
)
```

Ako je autentifikacija uspesna, trenutna aplikacija vraca placeholder:

```python
{
	"access_token": "token",
	"token_type": "bearer",
}
```

To jos nije pravi JWT. Sledeca lekcija ce zameniti placeholder stvarno potpisanim JSON Web Tokenom.

---

## 12) Najkraci odgovor

```python
form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
```

Koristi `:` zato sto je `form_data` parametar funkcije, a `Annotated[...]` je njegova anotacija.

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Koristi `=` zato sto se `Annotated[...]` cuva u promenljivoj kao reusable alias. Kasnije se alias koristi kao anotacija:

```python
db: db_dependency
```

```python
response_model=UserResponse
```

Koristi `=` zato sto je `response_model` imenovani argument `router.post()` dekoratora. To nije anotacija parametra, vec FastAPI konfiguracija HTTP odgovora.

```python
-> UserResponse
```

je Python anotacija povratne vrednosti funkcije.

Najvaznija formula za pamcenje:

```text
parametar: anotacija
alias = vrednost/anotacija
dekorator(opcija=vrednost)
funkcija(...) -> tip_povratne_vrednosti
```

Ovo razdvajanje ce biti korisno u JWT lekciji, jer cemo kombinovati dependency za citanje tokena, pomocnu funkciju za dekodiranje i response modele za bezbedan API odgovor.
