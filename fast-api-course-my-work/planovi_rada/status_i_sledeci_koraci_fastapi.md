# Status učenja i sledeci koraci - FastAPI kurs

## 1) Gde se trenutno nalaziš

Do ovog trenutka završena je osnova rada sa bazama podataka u FastAPI projektu:

- SQLAlchemy `engine`
- `check_same_thread=False` za SQLite
- `SessionLocal`
- SQLAlchemy `Base`
- `models.py` i ORM modeli
- `Users` i `Todos` tabele
- `ForeignKey` veza `Todos.owner_id -> Users.id`
- `Base.metadata.create_all(bind=engine)`
- osnovno razumevanje SQLite baze i kreiranja tabela

Sada počinješ oblast:

```text
docs/stage_2/02_api_request_methods
```

Prva lekcija je:

```text
01_get_all_todos_from_database
```

---

## 2) Važna napomena o stanju repozitorijuma

Klonirani repo već sadrži delove koji pripadaju kasnijim fazama kursa:

- `routers/`
- `auth.py`
- Alembic konfiguraciju i migracije
- testove
- kompletaniji `Project_4/TodoApp`

To ne znači da su te teme već obrađene. Te fajlove treba posmatrati kao unapred pripremljen ili gotov primer projekta. Učenje treba nastaviti redom prema lekcijama u `docs/stage_2`, bez preskakanja na gotovu implementaciju iz Project 4.

Project 4 već pokazuje napredniji oblik aplikacije:

- dependency za bazu kroz `get_db()` i `yield`
- autentifikaciju kroz `get_current_user`
- filtriranje todo zapisa po `owner_id`
- CRUD endpoint-e
- validaciju pomoću Pydantic-a
- Alembic migracije

Ove teme će služiti kao budući cilj i referenca, ali ih ne treba učiti sve odjednom.

## 3) Trenutni cilj: API request methods

Prva etapa treba da poveže bazu sa HTTP zahtevom. Redosled učenja:

1. `get_db()` dependency
2. `yield` i zatvaranje DB sesije u `finally`
3. `Depends(get_db)`
4. prvi GET endpoint
5. SQLAlchemy ORM query
6. vracanje liste todo zapisa
7. sortiranje pomocu `order_by`
8. razlika izmedju javnog prikaza svih zapisa i filtriranja po vlasniku

Mentalni model za ovu etapu:

```text
HTTP GET zahtev
    -> FastAPI ruta
    -> get_db otvara sesiju
    -> endpoint izvrsava ORM query
    -> baza vraca redove
    -> FastAPI pravi JSON odgovor
    -> get_db zatvara sesiju
```

## 4) Predlozeni redosled sledecih lekcija

### Korak 1 - GET svi todos

Fokus:

- `APIRouter`
- `Depends`
- `Session`
- `get_db()` sa `yield`
- `db.query(Todos).all()`
- `order_by(Todos.id)`

Prakticni cilj:

- napraviti endpoint koji vraća sve todo zapise
- proveriti rezultat kroz Swagger UI ili `curl`
- razumeti zašto se sesija zatvara posle request-a

Izlazni kriterijum:

- umeš da objasniš svaki deo `get_db()` funkcije
- umeš da napišeš query za sve todo zapise
- možeš da potvrdiš da se zapisi vraćaju sortirani po `id`

---

### Korak 2 - GET todo po ID-u

Fokus:

- path parameter
- `filter(Todos.id == todo_id)`
- `.first()`
- `404 Not Found` kada zapis ne postoji

Prakticni cilj:

- dobiti jedan todo zapis po ID-u
- obraditi slučaj nepostojećeg ID-a

---

### Korak 3 - POST kreiranje todo zapisa

Fokus:

- request body
- Pydantic schema
- validacija ulaznih podataka
- `db.add()`
- `db.commit()`
- `db.refresh()`
- status `201 Created`

Praktični cilj:

- poslati JSON telo zahteva
- sačuvati novi todo u bazi
- vratiti kreirani zapis

---

### Korak 4 - PUT izmena todo zapisa

Fokus:

- pronalazenje postojećeg zapisa
- provera `404` slučaja
- menjanje ORM atributa
- `commit()` nakon izmene

Prakticni cilj:

- izmeniti sve podatke jednog todo zapisa (PUT)
- proveriti promenu ponovnim GET zahtevom

---

### Korak 5 - DELETE brisanje todo zapisa (DELETE)

Fokus:

- pronalaženje zapisa
- brisanje
- `commit()`
- status `204 No Content`

Prakticni cilj:

- obrisati zapis
- proveriti da kasniji GET vraća `404`

---

### Korak 6 - autentifikacija i vlasnistvo podataka

Ovaj korak dolazi tek nakon razumevanja osnovnog CRUD-a.

Fokus:

- zavisnost za trenutno ulogovanog korisnika
- `user_dependency`
- filtriranje po `Todos.owner_id`
- razlika izmedju `user_id` iz URL-a i stvarno autentifikovanog korisnika
- zaštita od prikazivanja tuđih podataka

Važno:

```python
.filter(Todos.owner_id == user.get('id'))
```

je bezbedniji obrazac od endpointa koji samo prima proizvoljan `user_id` iz URL-a. Sam URL parametar nije autentifikacija.

---

### Korak 7 - Pydantic validacija i napredniji request patterns

Nakon osnovnog CRUD-a:

- `Field`
- ograničenja za stringove i brojeve
- `Path`
- query parametri (npr. `?skip=0&limit=10`)
- parcijalna izmena kroz PATCH (HTTP metoda za delimičnu izmenu resursa)
- response modeli (Pydantic schema koje se koriste za oblikovanje odgovora)
- jasna razlika između SQLAlchemy modela i Pydantic schema

---

### Korak 8 - Alembic i testovi

Ovo je već prisutno u Project 4, ali treba učiti nakon osnovnog CRUD-a:

- zašto `create_all()` nije zamena za migracije
- pravljenje migracije
- upgrade/downgrade
- testiranje ruta
- test baza i dependency override

---

## 5) Kako koristiti Project 4

Project 4 treba koristiti na tri načina:

1. kao mapu gde se vidi krajnji oblik aplikacije
2. kao izvor primera kada neka tema dođe na red
3. kao materijal za poredjenje posle samostalne implementacije

Ne treba trenutno pokušavati da se razume ceo Project 4 odjednom, zato što sadrzi teme koje još nisu obrađene:

- auth tokene (JWT)
- routers
- Alembic
- testove (pytest)
- napredniju validaciju
- odnose izmedju korisnika i todo zapisa

---

## 6) Pravilo rada za svaku lekciju

Za svaku novu lekciju koristiti ovaj redosled:

1. Pročitati cilj lekcije
2. Razumeti jedan novi koncept
3. Pogledati najmanji mogući primer
4. Samostalno napisati ili dopuniti kod
5. Testirati jedan uspešan slučaj
6. Testirati jedan neuspešan slučaj
7. Odgovoriti na kratka pitanja za samoproveru
8. Tek onda preći na sledeći koncept

---

## 7) Trenutni sledeći zadatak

Sada treba završiti lekciju `01_get_all_todos_from_database`.

Minimalni rezultat lekcije je:

- postoji `get_db()` dependency
- DB sesija se zatvara u `finally`
- postoji GET endpoint za čitanje svih todo zapisa
- query koristi `Todos`
- rezultat je sortiran po `id`
- razume se da endpoint bez filtera ne ograničava podatke po korisniku

Tek posle toga prelaziti na GET by ID.

---

## 8) Napomena za dalje konsultacije

Kada zatreba teorija, fokus treba da bude na aktuelnoj lekciji iz `docs/stage_2`, uz kratko povezivanje sa gotovim kodom iz Project 4. Ne treba uvoditi kasnije teme pre vremena osim kada služe da objasne razliku ili budući cilj.
