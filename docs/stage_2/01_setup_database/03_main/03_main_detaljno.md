# Stage 2 - Setup Database

## Lekcija 03 - main.py i automatsko kreiranje baze/tabela

## 0) Sta je poenta ove lekcije

U prethodne dve lekcije si uradio:

- `database.py` (konekcija, engine, session, Base)
- `models.py` (struktura tabela kroz ORM klase)

Sada pravis `main.py` koji povezuje sve delove.

Bez `main.py` aplikacija nema ulaznu tacku.
Bez poziva `create_all` tabele se ne kreiraju.

---

## 1) Sta transcript objasnjava (core ideja)

Transcript uvodi vrlo vazan tok:

1. Kreiras FastAPI app (`app = FastAPI()`)
2. Importujes `models`
3. Importujes `engine` iz `database.py`
4. Pozoves `models.Base.metadata.create_all(bind=engine)`
5. Pokrenes aplikaciju (`uvicorn main:app --reload`)
6. SQLAlchemy napravi SQLite fajl i tabele (ako ne postoje)

Klasicna poruka ove lekcije:
"Nema rucnog SQL CREATE TABLE, ORM radi to iza scene."

---

## 2) Analiza tvog trenutnog main.py

Tvoj `main.py` (Project 3) je:

```python
from fastapi import FastAPI

try:
    from . import models
    from .database import engine
    from .routers import admin, auth, todos, users
except ImportError:
    import models # type: ignore
    from database import engine # type: ignore
    from routers import admin, auth, todos, users # type: ignore

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
```

Sta je bitno da razumes:

## `app = FastAPI()`

Pravi ASGI aplikaciju.
`uvicorn` trazi bas taj objekat (`module:app`).

## `import models`

Ovo nije "visak" import.
Ovim SQLAlchemy "vidi" klase `Users` i `Todos`.
Ako modeli nisu importovani, `Base.metadata` ne zna koje tabele postoje.

## `from database import engine`

`engine` je kanal ka konkretnoj bazi (kod tebe SQLite).
`create_all` bez engine-a ne zna gde da kreira tabele.

## `models.Base.metadata.create_all(bind=engine)`

Najvaznija linija lekcije.
Radi sledece:

- cita sve modele registrovane pod tim `Base`
- proverava da li tabele postoje
- kreira nedostajuce tabele

Napomena:

- ne brise postojece tabele
- ne radi kompleksne migracije
- za ozbiljne izmene schema koristi se Alembic

## `app.include_router(...)`

Povezuje endpointe sa aplikacijom.
Ovo nije direktno deo kreiranja baze, ali je deo "startup slike" aplikacije.

---

## 3) Kako tacno nastaje fajl baze

U `database.py` imas URL:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
```

`./todosapp.db` zavisi od foldera iz kog pokreces komandu.
Zato mogu nastati 2 razlicita fajla ako menjas lokaciju pokretanja.

Primer:

- pokretanje iz `Project 3` -> baza u `Project 3/todosapp.db`
- pokretanje iz `Project 3/TodoApp` -> baza u `Project 3/TodoApp/todosapp.db`

Ovo je najcesci razlog "skripta se izvrsi, ali ne vidim tabelu".

---

## 4) Zasto lekcija kaze da je "magija"

Iza scene se desava sledece:

1. Python ucita `main.py`
2. Uveze `models` i `engine`
3. SQLAlchemy metadata registruje modele
4. `create_all` poredi metadata sa realnom bazom
5. Emituje SQL `CREATE TABLE` samo za ono sto ne postoji

Dakle, SQL se i dalje izvrsava, samo ga ti ne pises rucno.

---

## 5) Dva stabilna nacina pokretanja (u tvom setup-u)

Posto imas fallback import logiku, mogu oba:

## A) Package mode (preporuka)

Pokreni iz parent foldera `Project 3`:

```bash
cd "scratch/fast-api-course/Project 3"
uvicorn TodoApp.main:app --reload
```

## B) Script mode

Pokreni iz `TodoApp` foldera:

```bash
cd "scratch/fast-api-course/Project 3/TodoApp"
uvicorn main:app --reload
```

Najbitnije:

- izaberi jedan nacin i drzi se njega
- inace menjas lokaciju SQLite fajla

---

## 6) Kako proveravas da je baza stvarno kreirana

Nakon pokretanja app:

1. proveri da se pojavio `todosapp.db`
2. otvori sqlite3 nad tim fajlom
3. proveri tabele

```bash
sqlite3 "putanja/do/todosapp.db"
```

U sqlite shell-u:

```sql
.tables
.schema users
.schema todos
```

Ako `users` i `todos` postoje, sve radi kako treba.

---

## 7) Sta create_all moze, a sta ne moze

## Moze

- kreirati bazu (SQLite fajl) ako ne postoji
- kreirati nove tabele koje ne postoje

## Ne moze dobro da resava

- kompleksne izmene postojecih tabela
- rename kolona/tabela na siguran nacin
- data migracije

Za to kasnije uvodis Alembic migracije.

---

## 8) Ceste greske bas u ovoj lekciji

1. Zaboravljen import `models`
   Simptom: baza postoji, ali tabela nema.

2. Pogresan working directory
   Simptom: otvoris jedan `todosapp.db`, a app pise u drugi.

3. Pokusaj importa sa pogresnom putanjom
   Simptom: `ModuleNotFoundError`.

4. Ocekivanje da create_all menja staru tabelu
   Simptom: promenio si model, ali kolona se nije pojavila kako ocekujes.

5. Mislis da je `main.py` samo za rute
   U ovoj fazi je i bootstrap za DB lifecycle.

---

## 9) Veza sa prethodne dve lekcije

- Lekcija 01: napravio si vezu ka bazi (engine/session/base)
- Lekcija 02: definisao si sta su tabele i kolone
- Lekcija 03: aktiviras to u runtime-u preko `main.py`

Ovo je kompletan mini ciklus:

1. Definicija veze
2. Definicija strukture
3. Materijalizacija strukture u stvarnoj bazi

---

## 10) Practical mini test (5 minuta)

1. Obrisi oba `todosapp.db` fajla ako ih imas vise.
2. Pokreni app samo iz jednog foldera.
3. Proveri da se kreirao jedan DB fajl.
4. U sqlite3 proveri `.tables`.
5. Potvrdi da vidis `users` i `todos`.

Ako je svih 5 koraka ok, lekcija je usvojena.

---

## 11) Pitanja za samoproveru

1. Zasto je import `models` potreban pre `create_all`?
2. Sta tacno znaci `bind=engine`?
3. Zasto mogu nastati dva `todosapp.db` fajla?
4. Sta je granica `create_all`, a gde pocinje potreba za migracijama?
5. Kako bi objasnio ovu lekciju nekome u 3 recenice?

---

## 12) Zakljucak

Lekcija 03 je "prekidac" koji pali ceo DB setup.

`database.py` i `models.py` su plan,
`main.py` je izvrsenje tog plana.

Kad razumes ovu tacku, spreman si za sledeci korak:
rad sa sqlite3 komandama i unos prvih realnih zapisa u tabelu.
