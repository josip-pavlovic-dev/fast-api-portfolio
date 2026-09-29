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

Znači:

1. `form_data` je objekat tipa `OAuth2PasswordRequestForm`
2. `Depends()` govori FastAPI-ju da taj objekat dobavi kao dependency,a FastAPI će automatski proslediti odgovarajući objekat prilikom poziva funkcije.

### Detaljnije o Depends i dependency injection

`Depends` je `FastAPI funkcija` koja označava da određeni parametar funkcije treba da bude popunjen od strane `FastAPI dependency injection sistema`. Kada koristimo `Annotated` sa `Depends()`, mi zapravo govorimo FastAPI-ju: "Ovaj parametar zavisi od određenog dependency-ja, pa ga automatski popuni."

---

## 3) Šta je `Annotated[T, metadata]`

Opšti oblik je:

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

Drugim rečima, `Annotated` omogućava da jednom parametru pridružimo i tip i dodatne informacije koje framework treba da pročita.

Za login parametar:

```python
form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
```

Python deo razume osnovni tip `OAuth2PasswordRequestForm`, a FastAPI deo razume `Depends()`.

---

## 4) Zašto se nekada koristi `=`

Pogledajmo ovaj kod:

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Ovde `db_dependency` nije ime parametra funkcije. To je ime promenljive.

Znak `=` u ovom slučaju znači dodeljivanje:

```text
vrednost_prom_enljive = vrednost
```

Dakle, Python prvo napravi ovaj `Annotated` izraz:

```python
Annotated[Session, Depends(get_db)]
```

i zatim ga sačuva pod imenom:

```python
db_dependency
```

Možemo to zamisliti ovako:

```python
db_dependency = "Session + Depends(get_db)"
```

Samo što je stvarna vrednost strukturisana typing/FastAPI informacija, a ne tekst.

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

Prednost aliasa je što se isti dependency ne ponavlja u svakom endpointu.

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

---

### Sačuvano u aliasu

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

Zato ne postoji pravilo da se `Annotated` "nekada piše sa dvotackom, a nekada sa jednako". Isti `Annotated[...]` može biti direktna anotacija ili vrednost dodeljena promenljivoj.

---

## 6) Poređenje sa običnim tipovima

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

## 7) Zašto se `UserResponse` koristi kao `response_model=UserResponse`

Kod:

```python
@router.post(
	"/",
	status_code=status.HTTP_201_CREATED,
	response_model=UserResponse,
)
```

nije anotacija funkcijskog parametra. Ovo je poziv metode `router.post()` sa imenovanim argumentima.

Približno možemo zamisliti dekorator ovako:

```python
router.post(
	path="/",
	status_code=status.HTTP_201_CREATED,
	response_model=UserResponse,
)
```

Ovde `response_model` prima vrednost `UserResponse`.

Značenje je:

```text
Kada ovaj endpoint vrati odgovor,
koristi UserResponse kao pravilo za validaciju i serializaciju odgovora.
```

`UserResponse` je Pydantic schema, odnosno klasa koja opisuje javni oblik odgovora.

Ako ORM objekat korisnika sadrži:

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

a `UserResponse` sadrži samo:

```text
id
email
username
first_name
last_name
is_active
role
```

onda FastAPI vraća samo polja definisana u `UserResponse`. `hashed_password` se ne šalje klijentu.

Zato je bezbedno da endpoint vrati ORM objekat:

```python
return create_user_model
```

FastAPI ga zatim obradi kroz:

```python
response_model=UserResponse
```

---

## 8) Razlika između `response_model=UserResponse` i `-> UserResponse`

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

Značenje je:

```text
Očekuje se da funkcija vraća vrednost kompatibilnu sa UserResponse.
```

Return type hint pomaže editoru, type checker-u i čitaocu koda. `response_model` je FastAPI instrukcija za stvarno ponašanje HTTP endpointa.

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

imaju isto značenje, zato što su to imenovani argumenti funkcije/dekoratora.

Napomena o default parametrima koju si naveo odnosi se na drugi Python slučaj: definiciju funkcije.

Na primer, ovo nije dozvoljeno:

```python
def example(value: int = 10, name: str):
	...
```

Parametar bez default vrednosti ne može ići posle parametra sa default vrednošću. Ispravno je:

```python
def example(name: str, value: int = 10):
	...
```

Ali kod poziva funkcije sa imenovanim argumentima redosled nije takav problem:

```python
example(value=10, name="Ana")
```

Isto važi za `status_code=` i `response_model=` u `@router.post(...)`: oba su imenovani argumenti dekoratora, a nisu parametri tvoje endpoint funkcije.

---

## 10) Tri slična zapisa, tri razlicita značenja

```python
db: db_dependency
```

Znači: `db` je parametar sa anotacijom `db_dependency`.

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Znači: napravi promenljivu/alias koji čuva `Annotated` izraz.

```python
response_model=UserResponse
```

Znači: prosledi `UserResponse` kao imenovani argument FastAPI dekoratoru.

Vizuelno slični znakovi pripadaju različitim Python konstrukcijama:

| Zapis                                   | Uloga znaka | Značenje                             |
| --------------------------------------- | ----------- | ------------------------------------ |
| `db: db_dependency`                     | `:`         | anotacija parametra                  |
| `db_dependency = Annotated[...]`        | `=`         | dodela aliasa promenljivoj           |
| `response_model=UserResponse`           | `=`         | imenovani argument pozivu dekoratora |
| `def create_users(...) -> UserResponse` | `->`        | tip povratne vrednosti funkcije      |

---

## 11) Ponovljen tok lekcije 10

Pre nego što pređemo na `JWT`, trenutni login tok treba razumeti ovako:

```text
POST /auth/token
	-> OAuth2PasswordRequestForm čita username i password
		-> db_dependency obezbedjuje SQLAlchemy Session
			-> authenticate_user() traži korisnika po username-u
				-> bcrypt_context.verify() proverava password
					-> proverava se is_active
						-> validan user ili 401 greška
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

Ako je autentifikacija uspesna, trenutna aplikacija vraća `placeholder`:

```python
{
	"access_token": "token",
	"token_type": "bearer",
}
```

To još nije pravi `JWT`. Sledeća lekcija će zameniti `placeholder` stvarno potpisanim JSON Web Tokenom.

---

## 12) Najkraći odgovor

```python
form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
```

Koristi `:` zato što je `form_data` parametar funkcije, a `Annotated[...]` je njegova anotacija.

```python
db_dependency = Annotated[Session, Depends(get_db)]
```

Koristi `=` zato što se `Annotated[...]` čuva u promenljivoj kao reusable alias. Kasnije se alias koristi kao anotacija:

```python
db: db_dependency
```

```python
response_model=UserResponse
```

Koristi `=` zato što je `response_model` imenovani argument `router.post()` dekoratora. To nije anotacija parametra, već FastAPI konfiguracija HTTP odgovora.

```python
-> UserResponse
```

je Python-ova anotacija povratne vrednosti funkcije.

Najvažnija formula za pamćenje:

```text
parametar: anotacija
alias = vrednost/anotacija
dekorator(opcija=vrednost/anotacija)
funkcija(...) -> tip_povratne_vrednosti
```

Ovo razdvajanje će biti korisno u JWT lekciji, jer ćemo kombinovati dependency za čitanje tokena, pomoćnu funkciju za dekodiranje i response modele za bezbedan API odgovor.

---

## 13) SQLAlchemy `filter()` i kombinovanje uslova

U lekciji 10 koristi se provera da li već postoji korisnik sa istim email-om **ili** username-om:

```python
existing_user = (
	db.query(Users)
	.filter(
		(Users.email == create_user_request.email)
		| (Users.username == create_user_request.username)
	)
	.first()
)
```

Ovaj kod možemo čitati ovako:

```text
pretraži Users tabelu
	-> email je jednak poslatom email-u
	ILI
	-> username je jednak poslatom username-u
uzmi prvi pronađeni rezultat
```

Približan SQL oblik je:

```sql
SELECT *
FROM users
WHERE email = :email
   OR username = :username
LIMIT 1;
```

`:` u SQL primeru označava parametrizovanu vrednost. SQLAlchemy bezbedno prosleđuje stvarne vrednosti kroz parametre, umesto da ih ručno spaja u SQL string.

### 13.1. Šta radi `filter()`

`filter()` dodaje uslov pretrage u SQLAlchemy query:

```python
users = (
	db.query(Users)
	.filter(Users.is_active == True)
	.all()
)
```

Približan SQL:

```sql
SELECT *
FROM users
WHERE is_active = true;
```

`filter()` ne vraća odmah listu korisnika. On gradi query objekat. Query se izvršava kada pozovemo terminalnu metodu kao što su:

```python
.first() # Prvi rezultat
.all() # Svi rezultati
.one() # Tačno jedan rezultat, inače greška
.one_or_none() # Tačno jedan rezultat ili None
.count() # Broj rezultata
```

Primer:

```python
query = db.query(Users).filter(Users.username == "ana")
user = query.first()
```

Tok je:

```text
db.query(Users)          -> napravi početni query
filter(...)              -> dodaj WHERE uslov
first()                  -> izvrši query i uzmi prvi rezultat
```

---

### 13.2. SQLAlchemy izraz nije običan Python `bool`

Kada napišemo:

```python
Users.email == email
```

to nije obična Python provera koja odmah vraća `True` ili `False`. SQLAlchemy ORM kolona `Users.email` pravi `SQLAlchemy izraz` koji predstavlja `budući SQL uslov`:

```text
Users.email == email
	-> SQLAlchemy expression
		-> email = :email
```

Zato možemo taj izraz proslediti SQLAlchemy metodama kao što su `filter()` i `where()`.

Za razliku od običnog Python `bool` izraza, ovaj izraz se koristi za generisanje SQL uslova koji će se izvršiti kada se query izvrši.

---

## 14) `OR`: operator `|` i funkcija `or_()`

Za SQL `OR` možemo koristiti SQLAlchemy operator `|`:

```python
query = db.query(Users).filter(
	(Users.email == email)
	| (Users.username == username)
)
```

To znači:

```sql
WHERE email = :email -- PREVOD: Gde je email jednak parametru email u tabeli users
OR username = :username -- :username predstavlja parametar username u tabeli users. SQLAlchemy će zameniti :username stvarnom vrednošću kada se query izvrši
```

Možemo koristiti i eksplicitnu SQLAlchemy funkciju `or_()`:

```python
from sqlalchemy import or_


query = db.query(Users).filter(
	or_(
		Users.email == email,
		Users.username == username,
	)
)
```

Oba oblika izražavaju SQL `OR`:

```python
(condition_a) | (condition_b)
```

i:

```python
or_(condition_a, condition_b)
```

Funkcija `or_()` često je preglednija kada imamo više ili dinamički izgrađenih uslova.

---

## 15) `AND`: operator `&`, više argumenata i `and_()`

Za SQL `AND` možemo koristiti operator `&`:

```python
query = db.query(Users).filter(
	(Users.role == "admin")
	& (Users.is_active == True)
)
```

Približan SQL:

```sql
WHERE role = 'admin'
AND is_active = true
```

Možemo koristiti i `and_()`:

```python
from sqlalchemy import and_


query = db.query(Users).filter(
	and_(
		Users.role == "admin",
		Users.is_active == True,
	)
)
```

Najčešći i najjednostavniji oblik je da više uslova prosledimo direktno u `filter()`:

```python
query = db.query(Users).filter(
	Users.role == "admin",
	Users.is_active == True,
)
```

Više argumenata u jednom `filter()` pozivu spaja se po defaultu kao SQL `AND`, tako da je korišćenje `and_()` često nepotrebno!

```sql
WHERE role = 'admin'
AND is_active = true
```

Zato su sledeća dva oblika uglavnom ekvivalentna:

```python
db.query(Users).filter(
	(Users.role == "admin")
	& (Users.is_active == True)
)
```

i:

```python
db.query(Users).filter(
	Users.role == "admin",
	Users.is_active == True,
)
```

---

## 16) Važno: ne koristiti Python `and` i `or`

Za SQLAlchemy uslove ne treba pisati:

```python
# Pogrešno za SQLAlchemy izraze
Users.email == email or Users.username == username
```

ni:

```python
# Pogrešno za SQLAlchemy izraze
Users.role == "admin" and Users.is_active == True
```

Python `or` i `and` pokušavaju odmah da procene truthiness svojih operanada.

`SQLAlchemy` izraz `nije obična Python boolean vrednost` koju treba tako procenjivati.

Za SQL uslove koristi:

```python
# SQL OR
(Users.email == email) | (Users.username == username)
```

```python
# SQL AND
(Users.role == "admin") & (Users.is_active == True)
```

ili eksplicitne funkcije:

```python
or_(Users.email == email, Users.username == username)
and_(Users.role == "admin", Users.is_active == True) # ne mora moze i samo sa filter() sa više argumenata
```

Praktična tabela:

| Python zapis                   | SQLAlchemy značenje              | SQL značenje                 |
| ------------------------------ | -------------------------------- | ---------------------------- |
| `a == b`                       | SQLAlchemy comparison expression | `a = b`                      |
| `condition_a` \| `condition_b` | SQLAlchemy OR                    | `A OR B`                     |
| `condition_a & condition_b`    | SQLAlchemy AND                   | `A AND B`                    |
| `or_(a, b)`                    | eksplicitni SQLAlchemy OR        | `A OR B`                     |
| `and_(a, b)`                   | eksplicitni SQLAlchemy AND       | `A AND B`                    |
| `a or b`                       | Python logički operator          | ne koristiti za query uslove |
| `a and b`                      | Python logički operator          | ne koristiti za query uslove |

---

## 17) Zašto su zagrade važne

Kod operatora `|` i `&` treba staviti zagrade oko pojedinačnih uslova:

```python
query = db.query(Users).filter(
	(Users.email == email)
	| (Users.username == username)
)
```

Zagrade jasno odvajaju svaki SQLAlchemy comparison expression i sprečavaju probleme sa Python prioritetom operatora.

Za složeniji izraz:

```python
query = db.query(Users).filter(
	(Users.role == "admin")
	& (
		(Users.email == email)
		| (Users.username == username)
	)
)
```

Značenje je:

```text
role je admin
I
(email odgovara ILI username odgovara)
```

SQL oblik:

```sql
WHERE role = 'admin'
AND (email = :email OR username = :username)
```

Bez unutrašnjih zagrada lako se izgubi nameravano grupisanje uslova.

NAPOMENA: Nemoj mešati Python `or` sa SQLAlchemy operatorom `|`.

Kod običnog Python izraza:

```python
result = condition_a or condition_b
```

Python koristi `short-circuiting`: ako je `condition_a` istinit, `condition_b` se ne procenjuje.

Kod SQLAlchemy izraza:

```python
(Users.email == email) | (Users.username == username)
```

operator `|` ne odlučuje odmah da li je rezultat `True` ili `False`. On konstruiše SQLAlchemy izraz koji će kasnije postati SQL `OR`, na primer:

```sql
WHERE email = :email OR username = :username
```

Kada baza izvršava SQL, ne treba se oslanjati na to da će drugi uslov uvek biti preskočen čim prvi bude tačan. Baza može optimizovati query i drugačije proceniti predikate; SQL ne garantuje redosled procene uslova u `WHERE` klauzuli.

Zagrade su i dalje obavezne kada kombinujemo SQLAlchemy uslove pomoću `|` i `&`, ali one služe za pravilno grupisanje izraza, a ne za short-circuiting:

```python
query = db.query(Users).filter(
	(Users.email == email)
	| (Users.username == username)
)
```

### Kako SQL `AND` i `OR` grade uslov za bazu

SQL ne dobija gotovu Python vrednost `True` ili `False` pre nego što pošalje query. Umesto toga, SQL dobija predikate, odnosno uslove koje treba primeniti na svaki red:

```sql
WHERE email = :email
	OR username = :username
```

Za svaki red u tabeli baza logički posmatra rezultat svakog pojedinačnog uslova. Na primer, za jedan red može da dobije:

```text
email = :email       -> True
username = :username -> False
```

Zatim primeni SQL operator `OR`:

```text
True OR False -> True
```

Pošto je ukupan `WHERE` uslov `True`, taj red može biti deo rezultata.

Kod `AND` oba pojedinačna uslova moraju biti tačna:

```text
role = 'admin'       -> True
is_active = true     -> False

True AND False -> False
```

Pošto je ukupan `WHERE` uslov `False`, taj red neće biti vraćen.

Logičke tabele izgledaju ovako:

| Uslov A | Uslov B | `A AND B` | `A OR B` |
| ------- | ------- | --------- | -------- |
| `False` | `False` | `False`   | `False`  |
| `False` | `True`  | `False`   | `True`   |
| `True`  | `False` | `False`   | `True`   |
| `True`  | `True`  | `True`    | `True`   |

Zato možemo zapamtiti:

```text
AND -> svi uslovi moraju biti True
OR  -> najmanje jedan uslov mora biti True
```

Za query:

```sql
WHERE role = 'admin'
  AND is_active = true -- mozemo i odvojiti AND u drugom redu, SQL će i dalje pravilno proceniti uslove, ne reaguje na whitespace i nove redove
```

baza zadržava samo redove kod kojih su oba uslova tačna:

```text
role je admin AND korisnik je aktivan
```

Za query:

```sql
WHERE role = 'admin'
OR role = 'manager' -- ovde nismo odvojili OR u drugom redu, nema whitespace-a, a SQL će i dalje pravilno proceniti uslove!
```

baza zadržava red ako je makar jedan uslov tačan:

```text
role je admin OR role je manager
```

---

### Da li SQL kod `OR` proverava drugi uslov?

Ne treba razmišljati potpuno isto kao kod Python-a:

```python
result = condition_a or condition_b
```

Python koristi `short-circuiting`. Ako je `condition_a` istinit, `condition_b` se ne procenjuje.

Kod SQL-a je važno razlikovati dve stvari:

1. **Logičko značenje:** rezultat mora biti isti kao da su uslovi kombinovani po tabeli `AND`/`OR` iznad. Za `True OR False`, rezultat je `True`; za `True AND False`, rezultat je `False`.

2. **Fizičko izvršavanje:** baza sama bira kako će najefikasnije izvršiti query. Može proceniti oba predikata, može koristiti indeks, ili može preskočiti procenu nekog predikata kao optimizaciju.

Zato SQL ne garantuje da će kod:

```sql
WHERE condition_a OR condition_b
```

uvek prvo proveriti `condition_a`, pa zatim proveriti ili preskočiti `condition_b`. Redosled uslova u `WHERE` klauzuli nije način da kontrolišemo redosled izvršavanja.

Ali rezultat mora biti logički ispravan. Ako je za neki red:

```text
condition_a -> True
condition_b -> False
```

onda je rezultat:

```text
True OR False -> True
```

Ako je:

```text
condition_a -> True
condition_b -> False
```

kod `AND` rezultat je:

```text
True AND False -> False
```

Drugim rečima, SQL optimizator može promeniti način i redosled procene, ali ne sme promeniti konačno značenje query-ja.

---

### SQL ima i `UNKNOWN` zbog `NULL` vrednosti

SQL nije ograničen samo na `True` i `False`. Ako je neka vrednost `NULL`, poređenje često daje `UNKNOWN`:

```sql
NULL = 'admin'
```

nije `True`, već `UNKNOWN`.

U `WHERE` klauzuli se vraćaju samo redovi čiji je konačni rezultat `True`; redovi sa rezultatom `False` ili `UNKNOWN` se izostavljaju.

Za `UNKNOWN` važe ova korisna pravila:

| A         | B         | `A AND B` | `A OR B`  |
| --------- | --------- | --------- | --------- |
| `True`    | `UNKNOWN` | `UNKNOWN` | `True`    |
| `False`   | `UNKNOWN` | `False`   | `UNKNOWN` |
| `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` |

Zato se `NULL` ne proverava operatorom `=`. Koristi se:

```sql
WHERE deleted_at IS NULL
```

ili u SQLAlchemy-ju:

```python
Users.deleted_at.is_(None)
```

---

### Veza sa SQLAlchemy kodom

U ovom kodu:

```python
query = db.query(Users).filter(
	 (Users.email == email)
	 | (Users.username == username)
)
```

SQLAlchemy ne izvršava Python proveru:

```python
Users.email == email or Users.username == username
```

Umesto toga, operator `|` konstruiše SQLAlchemy expression koji se prevodi u SQL:

```sql
WHERE email = :email OR username = :username
```

Zatim baza, za svaki red, odlučuje da li je konačni uslov `True`. Samo takvi redovi ulaze u rezultat query-ja.

---

## 18) Zašto je `/` pogrešan operator

U primeru pitanja pojavio se ovaj zapis:

```python
(Users.email == create_user_request.email)
/ (Users.username == create_user_request.username)
```

Operator `/` znači deljenje. On ne znači ni SQL `OR` ni SQL `AND`.

Ispravan kod za proveru duplog email-a ili username-a je:

```python
existing_user = (
	db.query(Users)
	.filter(
		(Users.email == create_user_request.email)
		| (Users.username == create_user_request.username)
	)
	.first()
)
```

Ili eksplicitno:

```python
from sqlalchemy import or_


existing_user = (
	db.query(Users)
	.filter(
		or_(
			Users.email == create_user_request.email,
			Users.username == create_user_request.username,
		)
	)
	.first()
)
```

---

## 19) Negacija uslova: `~` i `not_()`

Za SQL `NOT` može se koristiti operator `~`:

```python
query = db.query(Users).filter(
	~(Users.role == "admin")
)
```

Približan SQL:

```sql
WHERE NOT (role = 'admin')
```

Može se koristiti i `not_()`:

```python
from sqlalchemy import not_


query = db.query(Users).filter(
	not_(Users.role == "admin")
)
```

## 20) Česti SQLAlchemy uslovi

### Jednakost i nejednakost

```python
Users.username == username
Users.role != "guest"
Users.id > 10
Users.id >= 10
Users.id < 100
Users.id <= 100
```

---

### Provera `NULL` vrednosti

Ne treba pisati:

```python
Users.deleted_at == None
```

Iako može izgledati logično, preporučeni SQLAlchemy oblik je:

```python
Users.deleted_at.is_(None)
Users.deleted_at.is_not(None)
```

SQL:

```sql
WHERE deleted_at IS NULL
WHERE deleted_at IS NOT NULL
```

---

### Provera da je vrednost u listi

```python
Users.role.in_(["admin", "manager"])
```

SQL:

```sql
WHERE role IN ('admin', 'manager')
```

Negacija je:

```python
Users.role.not_in(["guest", "blocked"])
```

---

### Pretraga teksta

```python
Users.username.like("ana%")
Users.username.ilike("ana%")
```

`like()` je obično case-sensitive u zavisnosti od baze i collation podešavanja, dok `ilike()` predstavlja case-insensitive pretragu na bazama koje je podržavaju.

Znakovi:

```text
% -> nula ili više proizvoljnih karaktera
_ -> tačno jedan proizvoljan karakter
```

Primer:

```python
Users.email.ilike("%@example.com")
```

---

## 21) `filter()` naspram `filter_by()`

`filter()` prima SQLAlchemy izraze i pogodan je za složene uslove:

```python
db.query(Users).filter(
	(Users.email == email)
	| (Users.username == username)
)
```

`filter_by()` koristi jednostavniji oblik sa imenima atributa i jednakostima:

```python
db.query(Users).filter_by(username="ana")
```

Više keyword argumenata u `filter_by()` znači `AND`:

```python
db.query(Users).filter_by(
	role="admin",
	is_active=True,
)
```

`filter_by()` nije dobar izbor za `OR`, složeno grupisanje ili operatore kao što su `in_()` i `ilike()`. Za takve slučajeve koristi `filter()`.

---

## 22) `.filter()` i `.where()`

Kod ORM query-ja često se koristi:

```python
db.query(Users).filter(Users.username == username)
```

U SQLAlchemy 2.x stilu češće se koristi `select()` sa `.where()`:

```python
from sqlalchemy import select


statement = select(Users).where(Users.username == username)
user = db.execute(statement).scalar_one_or_none()
```

Za postojeći projekat i lekcije koristićemo stil koji već postoji u kodu, odnosno `db.query(...).filter(...)`. Važno je razumeti da oba oblika grade SQL uslove; razlikuje se API stil.

---

## 23) Čitanje konkretnog koda iz registracije

Kod:

```python
existing_user = (
	db.query(Users)
	.filter(
		(Users.email == create_user_request.email)
		| (Users.username == create_user_request.username)
	)
	.first()
)
```

možemo prevesti na običan jezik:

```text
1. Kreni od Users tabele.
2. Pronađi red čiji email odgovara email-u iz request-a.
3. Ili pronađi red čiji username odgovara username-u iz request-a.
4. Vrati prvi pronađeni red.
5. Ako nema reda, rezultat je None.
```

Zašto se koristi `OR`, a ne `AND`?

Zato što registracija treba da bude odbijena ako je zauzet makar jedan unique podatak:

```text
email zauzet       -> odbij registraciju
username zauzet    -> odbij registraciju
oba zauzeta        -> odbij registraciju
```

Da bismo proverili da li su **oba** podataka istovremeno jednaka nekom kriterijumu, koristili bismo `AND`:

```python
db.query(Users).filter(
	Users.email == email,
	Users.username == username,
)
```

To bi značilo:

```text
email odgovara I username odgovara
```

To nije ista poslovna provera kao provera zauzetosti pojedinačnih unique polja.

---

## 24) Brza tabela za pamćenje

| Potreba                          | Python/SQLAlchemy oblik                         |
| -------------------------------- | ----------------------------------------------- |
| Jedan uslov                      | `.filter(Users.username == username)`           |
| Svi uslovi moraju važiti         | `.filter(condition_a, condition_b)`             |
| SQL `AND` eksplicitno            | `(condition_a) & (condition_b)` ili `and_(...)` |
| Bar jedan uslov mora važiti      | `(condition_a) \| (condition_b)` ili `or_(...)` |
| Negacija                         | `~condition` ili `not_(condition)`              |
| `NULL`                           | `.is_(None)` ili `.is_not(None)`                |
| Vrednost iz liste                | `.in_([...])`                                   |
| Tekstualni obrazac               | `.like(...)` ili `.ilike(...)`                  |
| Jednostavna jednakost po imenima | `.filter_by(username="ana")`                    |

---

## 25) Pitanja za proveru

1. Da li `Users.email == email` odmah vraća Python `True` ili SQLAlchemy expression?

ODGOVOR: SQLAlchemy expression, ne Python `True` ili `False`. Ovo znači da se uslov koristi za generisanje SQL upita, a ne za direktno evaluiranje u Python-u. Dakle, `Users.email == email` samo gradi deo SQL upita:

SQLAlchemy expression se koristi za generisanje SQL upita:

```python
query = db.query(Users).filter(Users.email == email)
```

SQL upit koji se generiše:

```sql
SELECT * FROM users WHERE email = :email
```

2. Koji SQL operator predstavlja `|`?

ODGOVOR: Predstavlja SQL `OR` operator. On se koristi za kombinovanje više uslova gde je dovoljno da bar jedan uslov bude zadovoljen. Primer:

```python
query = db.query(Users).filter((Users.email == email) | (Users.username == username))
```

```sql
SELECT * FROM users WHERE email = :email OR username = :username
```

3. Koji SQL operator predstavlja `&`?

ODGOVOR: Predstavlja SQL `AND` operator. On se koristi za kombinovanje više uslova gde svi uslovi moraju biti zadovoljeni. Primer:

```python
query = db.query(Users).filter((Users.email == email) & (Users.username == username))
```

```sql
SELECT * FROM users WHERE email = :email AND username = :username
```

4. Zašto se ne koriste Python `and` i `or` u SQLAlchemy filter uslovima?

ODGOVOR: Python `and` i `or` odmah evaluiraju izraze kao `True` ili `False` u Python-u, što nije ono što želimo kada gradimo SQL upit. Umesto toga, koristimo `&` i `|` koji generišu SQL `AND` i `OR` uslove.

5. Šta radi više argumenata u `.filter(condition_a, condition_b)`?

ODGOVOR: Više argumenata u `.filter()` se tretira kao da su povezani sa SQL `AND` operatorom. Na primer:

```python
query = db.query(Users).filter(Users.email == email, Users.username == username)
```

```sql
SELECT * FROM users WHERE email = :email AND username = :username
```

6. Zašto su zagrade važne kada koristimo `|` i `&`?

ODGOVOR: Zagrade su važne zbog prioriteta operatora. U Python-u, `&` ima viši prioritet od `|`, pa bez zagrada može doći do neočekivanih rezultata. Uvek koristi zagrade da jasno definišeš redosled evaluacije uslova.

7. Zašto je `/` pogrešan u primeru za proveru duplikata?

ODGOVOR: U SQLAlchemy filter uslovima, `/` nema nikakvo značenje i neće generisati validan SQL upit. Za logičke operacije koristimo `&` za `AND` i `|` za `OR`.

8. Koja je razlika između `filter()` i `filter_by()`?

ODGOVOR: `filter()` omogućava korišćenje složenih SQL uslova sa operatorima `&`, `|`, `~` i funkcijama `and_()`, `or_()`. `filter_by()` je jednostavniji i koristi se za direktno poređenje kolona sa vrednostima, bez potrebe za operatorima. Na primer:

```python
query = db.query(Users).filter_by(email=email, username=username)
```

```sql
SELECT * FROM users WHERE email = :email AND username = :username
```

9. Kako se proverava `NULL` vrednost?

ODGOVOR: U SQLAlchemy, `NULL` vrednosti se proveravaju koristeći `is_()` i `isnot_()` metode. Na primer:

```python
query = db.query(Users).filter(Users.email.is_(None))
```

```sql
SELECT * FROM users WHERE email IS NULL
```

10. Zašto registracija koristi `OR` između email-a i username-a?

ODGOVOR: Registracija koristi `OR` jer želimo da proverimo da li je **bilo koji** od ovih podataka već zauzet. Ako je ili email ili username već u bazi, registracija se odbija.

---

## 26) Kratak zaključak

Za `SQLAlchemy query uslove` zapamti:

```text
|       -> SQL OR
&       -> SQL AND
~       -> SQL NOT
and_()  -> eksplicitni SQL AND
or_()   -> eksplicitni SQL OR
```

Ne mešaj ih sa Python operatorima:

```python
# SQLAlchemy uslovi
(Users.email == email) | (Users.username == username)
(Users.role == "admin") & (Users.is_active == True)
```

Za tvoj konkretan kod najvažnije je:

```python
.filter(
	(Users.email == create_user_request.email)
	| (Users.username == create_user_request.username)
)
```

Znači: pronađi korisnika ako je zauzet **email ili username**. Ako `first()` vrati korisnika, registracija se odbija; ako vrati `None`, možemo pokušati da kreiramo novog korisnika.

---
