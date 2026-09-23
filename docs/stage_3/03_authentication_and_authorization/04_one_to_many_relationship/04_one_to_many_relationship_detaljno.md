# Oblast 03 - Authentication and Authorization

## Lekcija 04 - One-to-many odnos izmedju korisnika i todo zapisa

Ova lekcija uvodi prvi vazan odnos izmedju buduce `Users` tabele i postojece `Todos` tabele.

Ideja je:

> Jedan korisnik moze imati vise todo zapisa, ali jedan todo zapis pripada jednom korisniku.

Ovo je **one-to-many** odnos:

```text
jedan User  ->  mnogo Todos
```

U tvom aktivnom projektu ovaj odnos ce se kasnije odraziti prvenstveno na:

```text
fast-api-course-my-work/TodoApp/models.py
```

Buduci auth i todo routeri ostaju u:

```text
fast-api-course-my-work/TodoApp/api/routes/
```

Ova lekcija jos ne implementira korisnicku tabelu, login ili JWT. Ona priprema mentalni i bazni model za ownership, odnosno vlasnistvo nad todo zapisima.

---

## 1) Sta znaci one-to-many

Zamisli aplikaciju sa dva korisnika:

```text
Korisnik 1: Ana
    - kupiti namirnice
    - zavrsiti izvestaj
    - zakazati pregled

Korisnik 2: Marko
    - procitati knjigu
    - otici na trening
```

Ana ima vise todo zapisa. Marko takodje ima vise todo zapisa.

To ne znaci da u bazi postoji samo jedan korisnik. Znaci da **svaki pojedinacni korisnik moze imati vise todo zapisa**.

Relacija izgleda ovako:

```text
Users
    user 1 --------------+
                          +-- todo 1
                          +-- todo 2
                          +-- todo 3

    user 2 --------------+
                          +-- todo 4
                          +-- todo 5
```

Jedan todo zapis ne pripada istovremeno Ani i Marku. On ima jednog vlasnika.

---

## 2) Dve odvojene tabele

U relacionoj bazi korisnici i todo zapisi treba da budu odvojene tabele.

### Tabela `users`

Buduca tabela korisnika moze imati kolone slicne ovima:

| Kolona            | Uloga                    |
| ----------------- | ------------------------ |
| `id`              | primarni kljuc korisnika |
| `email`           | email korisnika          |
| `username`        | korisnicko ime           |
| `first_name`      | ime                      |
| `last_name`       | prezime                  |
| `hashed_password` | sacuvan hash password-a  |
| `is_active`       | da li je nalog aktivan   |

### Tabela `todos`

Postojeca tabela trenutno ima:

| Kolona        | Uloga                      |
| ------------- | -------------------------- |
| `id`          | primarni kljuc todo zapisa |
| `title`       | naslov zadatka             |
| `description` | opis zadatka               |
| `priority`    | prioritet                  |
| `complete`    | status zavrsenosti         |

Da bi se tabele povezale, `todos` dobija novu kolonu:

```text
owner_id
```

Ta kolona cuva ID korisnika kome todo pripada.

---

## 3) Primarni i strani kljuc

### Primarni kljuc

Primarni kljuc jedinstveno identifikuje red u tabeli.

U `users` tabeli:

```text
users.id
```

U `todos` tabeli:

```text
todos.id
```

Na primer:

```text
users
+----+----------+
| id | username |
+----+----------+
|  1 | ana      |
|  2 | marko    |
+----+----------+
```

### Strani kljuc

Strani kljuc je kolona koja cuva vrednost primarnog kljuca iz druge tabele.

U `todos` tabeli:

```text
todos.owner_id -> users.id
```

Ako `owner_id` ima vrednost `1`, to znaci da todo pripada korisniku ciji je `users.id` jednak `1`.

Vazno je razlikovati:

```text
todos.id
```

od:

```text
todos.owner_id
```

- `id` identifikuje sam todo zapis
- `owner_id` identifikuje korisnika koji je vlasnik tog zapisa

---

## 4) Primer podataka sa owner ID vrednostima

Pretpostavimo da postoje dva korisnika:

```text
users
+----+-------------------+
| id | username          |
+----+-------------------+
|  1 | codingwithrobby   |
|  2 | example_user      |
+----+-------------------+
```

I sest todo zapisa:

```text
todos
+----+----------------------+----------+----------+
| id | title                | complete | owner_id |
+----+----------------------+----------+----------+
|  1 | izneti smece         | false    | 1        |
|  2 | kupiti namirnice    | false    | 1        |
|  3 | zakazati sisanje    | true     | 1        |
|  4 | procitati knjigu    | false    | 2        |
|  5 | otici na trening    | false    | 2        |
|  6 | srediti sto         | true     | 2        |
+----+----------------------+----------+----------+
```

Tumacenje:

```text
owner_id = 1  -> todo pripada korisniku users.id = 1
owner_id = 2  -> todo pripada korisniku users.id = 2
```

Baza ne cuva celo ime korisnika u svakom todo redu. Cuva samo njegov ID, a veza izmedju tabela govori na kog korisnika se taj ID odnosi.

---

## 5) Kako ovo izgleda u SQLAlchemy modelu

Trenutni `TodoApp/models.py` sadrzi samo `Todos` model:

```python
class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
```

Kada bude uveden `Users` model, `Todos` ce dobiti dodatnu kolonu za strani kljuc.

Kursni konceptualni oblik moze izgledati ovako:

```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
```

Najvazniji deo je:

```python
owner_id = Column(Integer, ForeignKey("users.id"))
```

To znaci:

- `owner_id` je celobrojna kolona
- njena vrednost treba da predstavlja ID korisnika
- `ForeignKey("users.id")` opisuje vezu sa `users.id`

U tvom projektu ovaj kod pripada `TodoApp/models.py`, a ne routeru i ne `schemas.py` fajlu.

---

## 6) Gde se smesta `Users` model

U ovoj fazi tvog projekta postoji samo `Todos` model u:

```text
TodoApp/models.py
```

Kurs kasnije uvodi `Users` tabelu. Za trenutnu organizaciju najjednostavniji prelazni oblik je da oba SQLAlchemy modela ostanu u istom fajlu:

```text
TodoApp/models.py
    class Todos(Base)
    class Users(Base)
```

To je u skladu sa postojecim projektom i lakse je za ucenje.

Kasnije, kada broj modela poraste, moguca je organizacija:

```text
TodoApp/
    models/
        __init__.py
        todo.py
        user.py
```

Medjutim, to je posebna refaktorizacija i ne treba je uvoditi samo zato sto je uveden prvi strani kljuc. Za sada je dovoljno razumeti da relacijska veza pripada SQLAlchemy modelima u `models.py`.

---

## 7) Foreign key nije isto sto i Python promenljiva

Ovo:

```python
owner_id = Column(Integer, ForeignKey("users.id"))
```

nije samo obicna Python promenljiva koja cuva broj.

Ona istovremeno opisuje:

1. tip podatka u bazi
2. naziv kolone
3. vezu sa drugom tabelom
4. ogranicenje koje pomaze da se sacuvaju validne reference

Bez foreign key veze, neko bi mogao da upise:

```text
owner_id = 9999
```

cak i kada korisnik sa ID-em `9999` ne postoji.

Sa pravilno definisanom relacijom baza moze da pomogne u ocuvanju referencijalnog integriteta.

Referencijalni integritet znaci da reference iz jedne tabele treba da pokazuju na validne redove druge tabele.

---

## 8) Zasto todo treba da ima jednog vlasnika

U ovoj aplikaciji jedan todo opisuje jedan zadatak koji pripada jednom korisniku.

Zato je prirodan model:

```text
User 1 ---- many Todos
Todo 1 ---- one User
```

Ako bi jedan todo mogao pripadati mnogim korisnicima, to bi bio drugaciji odnos:

```text
many-to-many
```

Tada se obicno uvodi pomocna asocijativna tabela, na primer:

```text
user_todos
    user_id
    todo_id
```

To nije model koji ova lekcija uvodi.

---

## 9) One-to-many naspram one-to-one i many-to-many

### One-to-many

```text
Jedan korisnik -> mnogo todo zapisa
Jedan todo -> jedan korisnik
```

Primer: licni zadaci korisnika.

### One-to-one

```text
Jedan korisnik -> jedan profil
Jedan profil -> jedan korisnik
```

Primer: poseban profilni zapis.

### Many-to-many

```text
Mnogo korisnika -> mnogo projekata
Mnogo projekata -> mnogo korisnika
```

Primer: vise korisnika radi na vise projekata.

Kod one-to-many odnosa strani kljuc se najcesce nalazi na strani `many`, odnosno u tabeli `todos`:

```text
todos.owner_id -> users.id
```

Ovo je korisno pravilo za pamcenje:

> Foreign key se nalazi u tabeli koja sadrzi mnogo povezanih redova.

---

## 10) Kako se veza koristi u upitima

Kada znamo ID korisnika, mozemo pronaci samo njegove todo zapise:

```python
user_todos = (
    db.query(Todos)
    .filter(Todos.owner_id == user_id)
    .all()
)
```

Znacenje upita:

```text
uzmi Todos
gde je Todos.owner_id jednak user_id vrednosti
vrati sve takve zapise
```

Ako je:

```python
user_id = 1
```

dobijamo samo redove ciji je `owner_id` jednak `1`.

Ovo je osnova za buducu authorization logiku:

```text
current user -> njegov ID -> filter Todos.owner_id == current user ID
```

U ovoj lekciji `user_id` je konceptualna vrednost. U stvarnoj aplikaciji ne treba slepo verovati ID-u koji klijent posalje.

---

## 11) Ownership i bezbednost

Sama kolona `owner_id` ne obezbedjuje automatski bezbednost.

Ona samo cuva vezu izmedju reda u `todos` tabeli i reda u `users` tabeli.

Endpoint mora pravilno da koristi tu vezu.

Nesigurna logika bi bila:

```python
@app.get("/todo/user/{user_id}")
async def read_user_todos(user_id: int):
    return db.query(Todos).filter(Todos.owner_id == user_id).all()
```

Ako aplikacija nema dodatnu proveru, klijent bi mogao da promeni `user_id` iz `1` u `2` i pokusa da cita tudje podatke.

Bezbedniji buduci oblik koristi identitet dobijen iz validiranog tokena:

```python
current_user_id = current_user.get("id")

return (
    db.query(Todos)
    .filter(Todos.owner_id == current_user_id)
    .all()
)
```

Ovaj koncept ce se obradjivati detaljnije nakon uvodjenja korisnika, password hash-a i JWT-a.

---

## 12) Gde pripadaju request podaci

Trenutni `TodoRequest` u `TodoApp/schemas.py` opisuje podatke koje klijent salje za todo:

```python
class TodoRequest(BaseModel):
    title: str
    description: str
    priority: int
    complete: bool
```

Kada se uvede ownership, vazno je razmisliti da li klijent treba sam da salje `owner_id`.

Za licnu Todo aplikaciju bezbedniji princip je:

```text
owner_id ne dolazi proizvoljno iz request body-ja
owner_id dolazi iz autentifikovanog current user-a
```

Zato se `owner_id` obicno ne dodaje u javni `TodoRequest` samo da bi klijent mogao da izabere bilo kog vlasnika.

Kasnije mozemo imati odvojene modele:

```text
TodoRequest
    podaci koje klijent sme da posalje

TodoResponse
    podaci koje API vraca klijentu

Todo model
    podaci koji se cuvaju u bazi, ukljucujuci owner_id
```

Ovo je primer razlike izmedju:

- HTTP schema
- SQLAlchemy modela
- sigurnosnog identiteta korisnika

---

## 13) Sta se desava sa postojecim podacima

Dodavanje nove `owner_id` kolone nije samo promena Python koda. To je promena strukture baze.

Postojeca tabela moze vec imati todo zapise koji nemaju vlasnika. Zato se mora razmisliti o migraciji:

```text
stara tabela todos
    nema owner_id

nova tabela todos
    ima owner_id
```

U razvojnom projektu sa SQLite bazom ponekad se tabela ponovo napravi, ali to moze obrisati podatke. U realnom projektu se koristi migracioni alat, kao sto je Alembic.

Vazna napomena:

```python
Base.metadata.create_all(bind=engine)
```

uglavnom kreira tabele koje ne postoje. Ne treba ga posmatrati kao potpun sistem za bezbedno menjanje vec postojecih tabela.

Kada dodjemo do implementacije `Users` modela i `owner_id`, prvo treba odluciti:

- da li je baza samo razvojna
- da li postoje podaci koje treba sacuvati
- da li se koristi Alembic migracija
- da li `owner_id` sme privremeno biti `NULL`
- kako se postojeci podaci dodeljuju korisniku

---

## 14) Buduci raspored fajlova u TodoApp projektu

Posle ove lekcije ciljna struktura moze izgledati ovako:

```text
fast-api-course-my-work/
    TodoApp/
        __init__.py
        main.py
        models.py
        schemas.py
        api/
            __init__.py
            routes/
                __init__.py
                auth.py
                todos.py
                users.py
        core/
            __init__.py
            config.py
        db/
            __init__.py
            base.py
            database.py
            session.py
```

Odgovornosti su:

```text
models.py
    Users i Todos SQLAlchemy modeli

schemas.py
    request i response Pydantic modeli

api/routes/auth.py
    register i login endpointi

api/routes/todos.py
    Todo CRUD endpointi i buduci ownership filteri

api/routes/users.py
    korisnicki endpointi

db/session.py
    get_db dependency

main.py
    jedna FastAPI aplikacija i ukljucivanje routera
```

One-to-many veza pripada modelima, ali se koristi u todo endpointima i security logici.

---

## 15) Korak po korak mentalni model

Kada korisnik napravi novi todo, buduci tok moze izgledati ovako:

```text
1. Klijent salje title, description, priority i complete
2. FastAPI validira TodoRequest
3. security dependency odredjuje current user
4. endpoint uzima ID current user-a
5. endpoint pravi Todos objekat sa owner_id vrednoscu
6. SQLAlchemy cuva todo u todos tabeli
7. owner_id povezuje todo sa users.id
```

Primer konceptualnog SQLAlchemy objekta:

```python
todo_model = Todos(
    title=todo_request.title,
    description=todo_request.description,
    priority=todo_request.priority,
    complete=todo_request.complete,
    owner_id=current_user.id,
)
```

Ovde je vazno da `owner_id` dolazi iz autentifikovanog korisnika, a ne iz proizvoljnog podatka klijenta.

---

## 16) Sta ova lekcija jos ne implementira

Transkript samo objasnjava odnos tabela i dodavanje owner foreign key koncepta.

Ova lekcija jos ne uvodi potpuno:

- `Users` SQLAlchemy model u aktivni kod
- registraciju korisnika
- password hashing
- login
- JWT token
- `current_user` dependency
- admin role
- Alembic migraciju
- filtriranje svih postojecih todo ruta po vlasniku

Te teme dolaze postepeno u narednim lekcijama.

Zato ne treba sada samostalno dodavati `owner_id` u aktivni model ako zelis da pratis kurs korak po korak. Teorijski cilj ove lekcije je da razumes zasto ce ta kolona biti potrebna.

---

## 17) Pitanja za proveru znanja

1. Sta znaci one-to-many odnos?
2. Zasto jedan korisnik moze imati vise todo zapisa?
3. Zasto jedan todo zapis u ovom modelu pripada jednom korisniku?
4. Koje dve tabele ucestvuju u ovom odnosu?
5. Sta je primarni kljuc?
6. Sta je strani kljuc?
7. Na koju kolonu pokazuje `ForeignKey("users.id")`?
8. Zasto se `owner_id` nalazi u `todos` tabeli, a ne u `users` tabeli za svaki todo?
9. Koja je razlika izmedju `todos.id` i `todos.owner_id`?
10. Gde bi u tvom projektu pripadala definicija `owner_id`?
11. Zasto `owner_id` ne treba bez razmisljanja dodati u javni `TodoRequest`?
12. Kako se filtriraju todo zapisi jednog korisnika?
13. Zasto `owner_id` sam po sebi ne predstavlja autentifikaciju?
14. Sta moze biti problem sa postojecim todo podacima kada se doda nova obavezna kolona?
15. Koja je razlika izmedju one-to-many i many-to-many odnosa?
16. Koja je uloga `models.py`, a koja `api/routes/todos.py` u ovoj arhitekturi?

---

## 18) Prakticni zadaci

### Zadatak 1 - Nacrtaj relaciju

Nacrtaj dve tabele `users` i `todos` na papiru ili u Markdown-u.

U `users` dodaj:

```text
id, username, email
```

U `todos` dodaj:

```text
id, title, complete, owner_id
```

Oznaci:

- primarni kljucevi
- strani kljuc
- smer relacije
- primer da jedan user ima tri todo zapisa

### Zadatak 2 - Tumacenje podataka

Za sledece podatke objasni kome pripada svaki todo:

```text
users:
1 - ana
2 - marko

 todos:
101 - owner_id 1
102 - owner_id 1
103 - owner_id 2
```

Napisi koliko todo zapisa ima Ana, a koliko Marko.

### Zadatak 3 - Napisi SQLAlchemy kolonu

U posebnom tekstualnom primeru napisi import i model kolonu potrebnu za foreign key:

```python
from sqlalchemy import ForeignKey

owner_id = Column(Integer, ForeignKey("users.id"))
```

Objasni svaki deo izraza svojim recima.

Ne menjaj jos aktivni `models.py` ako korisnicki model jos nije uveden u prakticnom delu kursa.

### Zadatak 4 - Napisi ownership upit

Napisi SQLAlchemy upit koji vraca samo todo zapise za korisnika sa ID-em `3`.

Ocekuje se oblik slican:

```python
db.query(Todos).filter(Todos.owner_id == 3).all()
```

Zatim objasni zasto ovaj upit sam po sebi jos ne dokazuje da je zahtev poslao korisnik sa ID-em `3`.

### Zadatak 5 - Pronadji bezbednosni problem

Analiziraj ovaj endpoint:

```python
@app.get("/todo/user/{user_id}")
async def read_user_todos(user_id: int):
    return db.query(Todos).filter(Todos.owner_id == user_id).all()
```

Odgovori:

- sta klijent moze da promeni
- cije podatke bi mogao da pokusa da procita
- koji podatak bi u buducnosti trebalo da dolazi iz current user dependency-ja

### Zadatak 6 - Razdvoji model i schemu

Napravi dve liste:

```text
Podaci koje klijent sme da posalje:

Podaci koje aplikacija kontrolise:
```

Razvrstaj:

- `title`
- `description`
- `priority`
- `complete`
- `owner_id`
- `id`

Cilj je da pre uvodjenja JWT-a razumes zasto svi podaci iz baze ne treba automatski da budu pod kontrolom klijenta.

### Zadatak 7 - Predvidi promenu strukture

Napravi plan od najmanje pet koraka za buducu implementaciju one-to-many odnosa u tvom projektu.

Plan treba da sadrzi:

1. dodavanje `Users` modela
2. dodavanje `owner_id` u `Todos`
3. proveru baze i migracije
4. dobijanje current user-a
5. filtriranje todo zapisa po vlasniku

### Zadatak 8 - Razmisli o migraciji

Pretpostavi da tabela `todos` vec ima deset postojecih redova, a uvodis novi `owner_id`.

Odgovori:

- zasto ti podaci predstavljaju problem
- da li svi redovi mogu dobiti isti owner ID
- kada bi koristio migraciju
- zasto `create_all()` nije dovoljan alat za svaku promenu postojece tabele

### Zadatak 9 - Povezi putanje sa odgovornostima

Popuni sledecu mapu:

```text
TodoApp/models.py              ->
TodoApp/schemas.py             ->
TodoApp/api/routes/todos.py    ->
TodoApp/api/routes/auth.py     ->
TodoApp/db/session.py          ->
TodoApp/main.py                ->
```

Za svaki fajl napisi jednu ili dve konkretne odgovornosti u kontekstu korisnika i todo zapisa.

---

## 19) Zakljucak

One-to-many odnos opisuje vezu:

```text
jedan korisnik -> mnogo todo zapisa
```

U bazi se ta veza realizuje tako sto `todos` tabela dobija strani kljuc:

```text
todos.owner_id -> users.id
```

Za tvoj projekat to znaci:

- SQLAlchemy veza pripada `TodoApp/models.py`
- buduci todo endpointi pripadaju `TodoApp/api/routes/todos.py`
- autentifikacioni endpointi pripadaju `TodoApp/api/routes/auth.py`
- DB dependency ostaje u `TodoApp/db/session.py`
- glavna aplikacija ostaje u `TodoApp/main.py`
- `owner_id` ce kasnije omoguciti filtriranje todo zapisa po korisniku
- pravi ownership mora da koristi autentifikovani identitet, a ne proizvoljan ID iz URL-a

Ova lekcija je most izmedju obicnog Todo CRUD-a i bezbedne multi-user aplikacije. Pre nego sto korisnik moze da vidi samo svoje podatke, baza mora znati koji todo pripada kom korisniku.
