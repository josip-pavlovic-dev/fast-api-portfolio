# Stage 2 - API Request Methods

## Lekcija 03 - POST request: create todo u bazi

## 0) Gde se ova lekcija uklapa

Posle:

- GET all todos
- GET todo by id

sada dodajes CREATE deo CRUD-a.
To znaci da API vise nije samo read-only, vec pocinje da upisuje podatke u bazu.

---

## 1) Sta transcript pokriva (verno lekciji)

U lekciji se radi:

1. Kreiranje request modela (`TodoRequest`) preko Pydantic `BaseModel`
2. Dodavanje validacija kroz `Field`
3. POST endpoint sa status kodom 201
4. Pretvaranje request podataka u ORM model (`Todos(**todo_request.model_dump())`)
5. `db.add(...)` i `db.commit()`
6. Provera kroz docs da se novi todo stvarno pojavio

Kljucna poruka transkripta:

- `id` se ne salje iz request-a
- baza sama dodeljuje auto-increment primarni kljuc

---

## 2) Pydantic request model: zasto je potreban

`TodoRequest` je ugovor ulaza za POST.

Konceptualno:

```python
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
```

Sta ovo donosi:

- schema je jasna
- validacija je automatska
- los input ne stize do DB sloja

Ako klijent posalje pogresan payload, FastAPI vraca 422 pre ulaska u business logiku.

---

## 3) Zasto ne saljemo id u POST payload

U tabeli `todos` kolona `id` je primarni kljuc.

To znaci:

- jedinstven je
- baza ga generise
- klijent ne treba i ne sme da pogadja sledeci id

Zbog toga request schema namerno nema `id` polje.

---

## 4) POST endpoint logika (korak po korak)

U tvom Project 4 obrascu endpoint izgleda ovako (koncept):

```python
@router.post("/todo", status_code=201)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()
```

Tok:

1. Auth proveri korisnika
2. Input se validira kroz `TodoRequest`
3. Pravi se ORM objekat `Todos`
4. Dodaje se `owner_id` iz autentifikacije
5. `db.add` registruje promenu u session-u
6. `db.commit` upisuje transakciju u bazu

---

## 5) Razlika izmedju db.add i db.commit

`db.add(obj)`:

- stavlja objekat u ORM session
- jos nije trajno upisan u bazu

`db.commit()`:

- zatvara transakciju
- promene postaju trajne

Jednostavno pravilo:

- add = priprema
- commit = upis

---

## 6) model_dump i zasto je koristan

`todo_request.model_dump()` vraca dict iz Pydantic modela.

Primer ideje:

```python
todo_request.model_dump()
# {
#   "title": "Learn FastAPI",
#   "description": "...",
#   "priority": 5,
#   "complete": False
# }
```

Onda se taj dict prosledi u ORM konstruktor kroz `**`.

To je cist i standardan obrazac za Pydantic v2.

---

## 7) Validacije koje transcript uvodi

- `title` minimum 3 karaktera
- `description` izmedju 3 i 100
- `priority` > 0 i < 6
- `complete` bool

Efekat:

- losi podaci se odbijaju ranije
- manje gresaka i cistija baza

---

## 8) Status kod 201 i zasto je bitan

Za uspesan CREATE koristi se:

- 201 Created

To je semanticki tacan signal klijentu da je resurs kreiran.

Ako je validacija losa:

- 422

Ako korisnik nije autentifikovan:

- 401

---

## 9) Transcript varijanta vs Project 4 varijanta

Transcript pocetna ideja:

- kreira todo iz request-a
- bez vlasnistva korisnika

Project 4:

- dodaje `owner_id` iz auth-a
- svaki todo je vezan za korisnika

Ovo je ogroman korak ka realnoj aplikaciji.
Bez `owner_id` lako nastane curenje podataka i haos oko ownership pravila.

---

## 10) Kako da proveris da POST radi

Minimalni test scenario:

1. Pozovi GET all i zapamti broj redova
2. Pozovi POST /todo sa validnim payload-om
3. Ocekuj 201
4. Ponovo GET all i potvrdi da je broj redova veci za 1
5. Proveri da novi red ima owner_id trenutnog korisnika

Ako payload nije validan, ocekuj 422 i bez promene broja redova.

---

## 11) Ceste greske pocetnika

1. Zaboravljen commit

- endpoint vrati success, ali red nije sacuvan

2. Pokusaj unosa id iz klijenta

- nepotrebno i rizicno

3. Bez owner_id pri kreiranju

- kasnije read/update/delete pravila pucaju

4. Pogresan tip za complete ili priority

- dobija se 422

5. Mesanje request modela i ORM modela

- Pydantic i SQLAlchemy imaju razlicite uloge

---

## 12) Mala napredna napomena

U ozbiljnijem API dizajnu cesto se radi:

- `db.commit()`
- `db.refresh(todo_model)`
- vracanje kreiranog objekta kao response model

To omogucava da odmah vratis i DB generisana polja (npr. `id`).
U ovoj kurs fazi nije obavezno, ali je dobro da znas unapred.

---

## 13) Samoprovera razumevanja

Ako mozes da odgovoris na ova pitanja, lekcija je usvojena:

1. Zasto `TodoRequest` nema id polje?
2. Koja je razlika izmedju `db.add` i `db.commit`?
3. Kada dobijas 201, a kada 422?
4. Zasto je `owner_id` bitan u Project 4?
5. Sta radi `model_dump()` pre kreiranja ORM objekta?

---

## 14) Zakljucak

POST lekcija je prvi pravi write korak kroz API.

Savladavanjem ovog obrasca dobijas:

- cist ulaz kroz Pydantic
- kontrolisano mapiranje ka ORM modelu
- transakcioni upis u bazu
- spremnost za sledece korake: PUT i DELETE

Jedna recenica:
GET cita ono sto postoji, POST stvara ono sto ce tek postojati.
