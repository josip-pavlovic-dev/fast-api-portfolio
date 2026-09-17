# Stage 2 - Database Connection with ORM (SQLAlchemy)

## Lekcija 01 - Povezivanje FastAPI aplikacije sa SQLite bazom

## 0) Kontekst: gde si sada
Do sada si radio FastAPI CRUD bez prave baze (ili sa osnovnim pristupom).
U ovoj lekciji praviš prvi ozbiljan korak:
- uvodiš SQLAlchemy
- povezuješ aplikaciju sa SQLite bazom
- pripremaš osnovu za modele i tabele

Kurs ovo prolazi brzo, pa ovde ide detaljno objašnjenje za početnika.

---

## 1) Šta lekcija iz transkripta zapravo radi

Na osnovu transkripta i koda, cilj je:

1. Kreirati Python paket TodoApp
2. Dodati database.py
3. Definisati URL baze:
   sqlite:///./todosapp.db
4. Napraviti engine preko create_engine(...)
5. Napraviti SessionLocal preko sessionmaker(...)
6. Napraviti Base preko declarative_base()

Ovo je “foundation” pre modela i CRUD logike.

Relevantni fajlovi iz projekta:
- [scratch/fast-api-course/Project 3/TodoApp/database.py](scratch/fast-api-course/Project%203/TodoApp/database.py)
- [scratch/fast-api-course/Project 3/TodoApp/models.py](scratch/fast-api-course/Project%203/TodoApp/models.py)
- [scratch/fast-api-course/Project 3/TodoApp/main.py](scratch/fast-api-course/Project%203/TodoApp/main.py)

---

## 2) Kako se pravi Python paket u VS Code (Linux)

Na Mac-u tutor koristi “new Python package” kroz klik.
U VS Code/Linux suština je jednostavna:

Paket = folder + __init__.py

Primer:
- folder TodoApp
- fajl TodoApp/__init__.py

To je dovoljno da Python prepozna import putanje kao paket.

---

## 3) Detaljna analiza database.py (liniju po liniju)

Kod:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### 3.1 create_engine
Engine je glavni “ulaz” u bazu.
Ne izvršava odmah sve upite, nego predstavlja konfigurisan kanal ka DB-u.

### 3.2 SQLALCHEMY_DATABASE_URL
Vrednost:
sqlite:///./todosapp.db

Značenje:
- sqlite: koristi SQLite driver
- ///: file-based baza
- ./todosapp.db: baza je fajl u trenutnom working directory-ju

Važna početnička zamka:
Ako menjaš folder iz kog pokrećeš app, možeš nenamerno praviti više različitih todosapp.db fajlova.

### 3.3 connect_args={"check_same_thread": False}
SQLite po default-u očekuje da se ista konekcija koristi u istom thread-u.
FastAPI radi sa više requestova i može uključiti više thread-ova.
Zato u ovoj kombinaciji često postavljaš check_same_thread=False.

### 3.4 SessionLocal
SessionLocal je “fabrika sesija”.
Nije sama sesija, nego objekat koji pravi sesije kad pozoveš SessionLocal().

Parametri:
- autocommit=False: ništa se ne upisuje automatski, ti kontrolišeš commit
- autoflush=False: flush se ne radi automatski u svakom koraku
- bind=engine: sesije koriste engine ka tvojoj bazi

### 3.5 Base = declarative_base()
Base je roditeljska klasa za ORM modele.
Svaka tabela-model nasleđuje Base.
Bez toga SQLAlchemy ne zna koje sve tabele treba da mapira.

---

## 4) Kako se ovo povezuje sa models.py i main.py

U [scratch/fast-api-course/Project 3/TodoApp/models.py](scratch/fast-api-course/Project%203/TodoApp/models.py):
- klase Users i Todos nasleđuju Base
- to znači da SQLAlchemy zna kako da mapira Python klase u SQL tabele

U [scratch/fast-api-course/Project 3/TodoApp/main.py](scratch/fast-api-course/Project%203/TodoApp/main.py):
- poziva se models.Base.metadata.create_all(bind=engine)
- time se fizički kreiraju tabele u SQLite fajlu (ako ne postoje)

Dakle redosled:
1. import database (engine, Base)
2. import models (koji koriste Base)
3. create_all -> kreiranje tabela

---

## 5) Mentalni model: ORM za apsolutnog početnika

ORM znači:
- umesto da odmah pišeš ručni SQL za sve,
- radiš sa Python klasama i objektima,
- SQLAlchemy prevodi to u SQL upite.

Primer ideje:
- class Users -> tabela users
- objekat Users(...) -> jedan red u tabeli users

Ali važno:
ORM ne znači da SQL nije bitan.
SQL i dalje postoji ispod haube.

---

## 6) Najčešće greške u ovoj lekciji

1. Pogrešan working directory
Simptom:
- tabela “ne postoji”
- a zapravo gledaš drugi DB fajl

2. Modeli nisu importovani pre create_all
Ako SQLAlchemy ne vidi modele, nema šta da kreira.

3. Loša import struktura u paketu
Ako koristiš paket pristup, import putanje moraju biti dosledne.

4. Očekivanje da SessionLocal sam upisuje promene
Ne upisuje. Potreban je commit.

---

## 7) Kako proveravaš da li je sve stvarno povezano

U sqlite3 shell-u:

```sql
.tables
.schema users
.schema todos
```

Ako nema tabela:
- proveri da li je create_all zaista izvršen
- proveri da li si otvorio pravi todosapp.db

---

## 8) Minimalni primer korišćenja sesije (koncept)

```python
db = SessionLocal()
try:
    # db.add(obj)
    # db.commit()
    pass
finally:
    db.close()
```

Poenta:
- otvori sesiju
- uradi posao
- zatvori sesiju

Kasnije se ovo elegantno rešava FastAPI dependency funkcijom get_db().

---

## 9) Šta je dobro u kurs kodu, a šta bi kasnije unapredio

Dobro za početak:
- jasan i minimalan setup
- ispravna osnova za SQLite + SQLAlchemy

Kasnije unaprediti:
- preći na noviji SQLAlchemy 2.x stil declarative base
- centralizovati get_db dependency
- jasnije organizovati import putanje za paket mode

---

## 10) Kratka mapa pojmova

- Engine: konekcioni mehanizam ka bazi
- Session: radni kontekst za ORM operacije
- Base: roditelj svih modela
- Model: Python klasa mapirana na SQL tabelu
- create_all: kreira tabele definisane modelima

---

## 11) Vežbe (od lakog ka težem)

1. Objasni svojim rečima razliku Engine vs Session.
2. Napiši šta znači sqlite:///./todosapp.db i zašto je bitan working directory.
3. Uoči gde u projektu nastaju tabele i objasni redosled importa.
4. Dodaj zamišljeno polje phone u Users i objasni šta je potrebno da bi se pojavilo u bazi.
5. Napiši mini dijagnostiku: šta proveravaš ako .tables ne prikazuje users i todos.

---

## 12) Zaključak

Ova lekcija nije “samo 10 linija koda”.
To je temelj celog SQL dela:

- bez dobrog database.py nema stabilnih modela
- bez modela nema tabela
- bez tabela nema pravog CRUD-a

Kad ovo razumeš, sledeći korak (CRUD preko ORM sesije) biće mnogo jasniji i manje stresan.
