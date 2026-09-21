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

1. Kreirati Python paket `TodoApp`
2. Dodati `database.py`
3. Definisati URL baze:
   `sqlite:///./todosapp.db`
4. Napraviti engine preko `create_engine(...)`
5. Napraviti `SessionLocal` preko `sessionmaker(...)`
6. Napraviti `Base` preko `declarative_base()`

Ovo je “foundation” pre modela i CRUD logike.

Relevantni fajlovi iz projekta:

- [scratch/fast-api-course/Project 3/TodoApp/database.py](scratch/fast-api-course/Project%203/TodoApp/database.py)
- [scratch/fast-api-course/Project 3/TodoApp/models.py](scratch/fast-api-course/Project%203/TodoApp/models.py)
- [scratch/fast-api-course/Project 3/TodoApp/main.py](scratch/fast-api-course/Project%203/TodoApp/main.py)

---

## 2) Kako se pravi Python paket u VS Code (Linux)

Na Mac-u tutor koristi “new Python package” kroz klik.
U VS Code/Linux suština je jednostavna:

Paket = folder + **init**.py

Primer:

- folder TodoApp
- fajl TodoApp/**init**.py

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

---

### 3.2 SQLALCHEMY_DATABASE_URL

Vrednost:
`sqlite:///./todosapp.db`

Značenje:

- `sqlite:` - koristi SQLite driver za SQLite bazu
- `///`- označava da je baza fajl u trenutnom direktorijumu
- `./todosapp.db` baza je fajl u trenutnom working directory-ju i biće kreirana ako ne postoji pod imenom `todosapp.db`.
- `.` ispred `todosapp.db` označava trenutni direktorijum.

Važna početnička zamka:
Ako menjaš folder iz kog pokrećeš app, možeš nenamerno praviti više različitih `todosapp.db` fajlova.

---

### 3.3 connect_args={"check_same_thread": False}

SQLite po default-u očekuje da se ista (eng. `same`) konekcija koristi u istom `thread`-u (što može biti problem u web aplikacijama sa više thread-ova).

`Thread` je osnovna jedinica izvršavanja u Python-u i drugim programskim jezicima. Pod `thread`-om se podrazumeva tok izvršavanja koda. Jedno izvršavanje koda u okviru `thread`-a se odvija sekvencijalno. To znači da se izvršavanje koda u jednom `thread`-u odvija iz delova a ne u celini odjednom. Zbog toga SQLite po default-u očekuje da se ista konekcija koristi u istom `thread`-u kako bi se izbegli konflikti sa sekvencijalnim izvršavanjem drugih `thread`-ova. Zato je potrebno postaviti `check_same_thread=False` kada koristiš `SQLite` u ovakvim scenarijima. Tako se omogućava da više thread-ova koristi istu konekciju bez konflikta.

ZAKLJUČAK:
FastAPI radi sa više requestova i može uključiti više thread-ova.
Zato u ovoj kombinaciji često postavljaš `check_same_thread=False`.

---

### 3.4 SessionLocal

`SessionLocal` je “fabrika sesija”.

Sama po sebi nije sesija, nego objekat koji pravi sesije kada ga pozoveš (npr. `db = SessionLocal()`). Sesija predstavlja kontekst za rad sa bazom, gde možeš izvršavati upite i menjati podatke. Primer:

```python
db = SessionLocal()
try:
    # ovde ide rad sa bazom, npr. db.query(...)
    pass
finally:
    db.close()
```

Parametri:

- `autocommit=False`: ništa se ne upisuje automatski, ti kontrolišeš commit
- `autoflush=False`: flush (predstavlja upis promena u bazu) se ne radi automatski u svakom koraku
- `bind=engine`: sesije koriste engine ka tvojoj bazi

---

### 3.5 Base = declarative_base()

`Base` je roditeljska klasa za `ORM` modele.
Svaka tabela-model nasleđuje `Base`.
Bez toga `SQLAlchemy` ne zna koje sve tabele treba da mapira.

---

## 4) Kako se ovo povezuje sa models.py i main.py

U [scratch/fast-api-course/Project 3/TodoApp/models.py](scratch/fast-api-course/Project%203/TodoApp/models.py):

- Klase Users i Todos u `models.py` nasleđuju `Base`. Zbog toga radimo `from database import Base` i koristimo ga u `models.py`.

- to znači da `SQLAlchemy` sada zna kako da mapira Python klase u SQL tabele na osnovu `Base` klase.

U [scratch/fast-api-course/Project 3/TodoApp/main.py](scratch/fast-api-course/Project%203/TodoApp/main.py):

- importuje se `models` kako bi `SQLAlchemy` video sve definisane modele
- poziva se `models.Base.metadata.create_all(bind=engine)`
- time se fizički kreiraju tabele u `SQLite` fajlu (ako ne postoje)

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

4. Očekivanje da `SessionLocal` sam upisuje promene
   Ne upisuje. Potreban je commit.

---

## 7) Kako proveravaš da li je sve stvarno povezano

Najpre u bash terminalu pokreni sqlite3 shell sa fajlom `todosapp.db`:

```bash
sqlite3 todosapp.db
```

Zatim u sqlite3 shell-u:

```sql
.tables
.schema users
.schema todos
```

Ako nema tabela:

- Proveri da li je `create_all` zaista izvršen
- Proveri da li si otvorio pravi `todosapp.db`

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

- otvori sesiju (`SessionLocal`)
- uradi posao (`db.add`, `db.commit`, itd.)
- zatvori sesiju (`db.close()`)

Kasnije se ovo elegantno rešava `FastAPI dependency` funkcijom `get_db()`.

---

## 9) Šta je dobro u kurs kodu, a šta bi kasnije unapredio

Dobro za početak:

- jasan i minimalan setup
- ispravna osnova za SQLite + SQLAlchemy

Kasnije unaprediti:

- preći na noviji SQLAlchemy 2.x stil declarative base
- centralizovati get_db dependency
- jasnije organizovati import putanje za paket modele

---

## 10) Kratka mapa pojmova

- `Engine`: konekcioni mehanizam ka bazi
- `Session`: radni kontekst za ORM operacije
- `Base`: roditelj svih modela
- `Model`: Python klasa mapirana na SQL tabelu
- `create_all`: kreira tabele definisane modelima

---

## 11) Vežbe (od lakog ka težem)

1. Objasni svojim rečima razliku `Engine` vs `Session`.

`Engine` je konekcioni mehanizam ka bazi, dok je `Session` radni kontekst za ORM operacije.
2. Napiši šta znači `sqlite:///./todosapp.db` i zašto je bitan working directory.

`sqlite:///./todosapp.db` označava SQLite bazu koja se nalazi u trenutnom radnom direktorijumu (`./`). Bitan je working directory jer SQLite koristi relativnu putanju za fajl baze. To znači da ako pokreneš aplikaciju iz drugog direktorijuma, SQLite možda neće moći da pronađe fajl baze.

3. Uoči gde u projektu nastaju tabele i objasni redosled importa (`database.py` -> `models.py` -> `main.py`).

Odgovor: Tabele nastaju kada se pozove `Base.metadata.create_all(bind=engine)` u `database.py`. Redosled importa je bitan jer `models.py` mora da importuje `Base` iz `database.py`, a `main.py` mora da importuje modele kako bi SQLAlchemy znao za njih pre kreiranja tabela.

4. Dodaj zamišljeno polje `phone` u `Users` i objasni šta je potrebno da bi se pojavilo u bazi.

```python
# U models.py dodaj polje phone u Users
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, index=True)
```
5. Napiši mini dijagnostiku: šta proveravaš ako .tables ne prikazuje users i todos.

Ako `.tables` ne prikazuje `users` i `todos`, proveri sledeće:
- Da li si importovao modele u `main.py` pre kreiranja tabela.
- Da li si pozvao `Base.metadata.create_all(bind=engine)` nakon što su modeli definisani.
- Da li je putanja do SQLite fajla ispravna i da li fajl postoji.
- Da li si restartovao aplikaciju nakon dodavanja novih polja u modele (SQLite ne menja postojeće tabele automatski).
- Da li si proverio da li su migracije potrebne ako koristiš SQLite i menjaš postojeće tabele.

Provera iz bash-a:
```bash
sqlite3 ./todosapp.db
.tables
```


---

## 12) Zaključak

Ova lekcija nije “samo 10 linija koda”.
To je temelj celog `SQL` dela:

- bez dobrog `database.py` nema stabilnih modela
- bez `models.py` nema `tabela` u bazi
- bez tabela nema pravog `CRUD`-a a samim tim ni funkcionalne aplikacije

Kad ovo razumeš, sledeći korak (`CRUD` preko `ORM` sesije) biće mnogo jasniji i manje stresan.
