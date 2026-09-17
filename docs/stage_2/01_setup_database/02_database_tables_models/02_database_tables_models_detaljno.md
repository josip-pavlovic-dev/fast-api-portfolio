# Stage 2 - Setup Database

## Lekcija 02 - Database Tables and Models (SQLAlchemy ORM)

## 0) Sta je cilj ove lekcije

U prethodnoj lekciji si napravio konekciju sa bazom (`database.py`).
U ovoj lekciji pravis ORM modele u `models.py`, odnosno Python klase koje predstavljaju SQL tabele.

Kratko:

- `database.py` = kako se povezujes na bazu
- `models.py` = koje tabele i kolone postoje

Bez `models.py` SQLAlchemy ne zna sta treba da kreira u bazi.

---

## 1) Sta transkript pokriva (verno lekciji)

Transkript fokusira jednu glavnu ideju:

1. Kreiras `models.py`
2. Uvezes `Base` iz `database.py`
3. Definises klasu (tabelu), npr. `Todos`
4. Dodas `__tablename__`
5. Dodas kolone (`id`, `title`, `description`, `priority`, `complete`)

To je minimalni ORM setup koji omogucava da se tabela kreira kasnije preko:

```python
models.Base.metadata.create_all(bind=engine)
```

---

## 2) Kako SQLAlchemy "razume" tvoju tabelu

SQLAlchemy ORM cita Python klasu i mapira je na SQL tabelu.

Primer mentalnog modela:

- klasa `Todos` -> tabela `todos`
- atribut `id = Column(Integer, primary_key=True)` -> kolona `id INTEGER PRIMARY KEY`
- jedna instanca klase `Todos(...)` -> jedan red u tabeli `todos`

Dakle, ORM je prevodilac izmedju Python objekata i SQL reda/kolona.

---

## 3) Analiza tvog stvarnog models.py (Project 3)

Tvoj trenutni fajl u Project 3:

- ima dve tabele (`Users`, `Todos`)
- koristi i `ForeignKey` (`owner_id` pokazuje na `users.id`)

To znaci da je tvoj kod vec iznad minimalnog nivoa iz transkripta, sto je odlicno.

### 3.1 Imports

```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
```

Ovo su SQL tipovi i gradivni elementi kolona.

```python
try:
    from .database import Base
except ImportError:
    from database import Base  # type: ignore
```

Ovo je kompatibilnost za dva nacina pokretanja:

- package mode
- script mode

Za pocetnika je najbitnije da razumes: `Base` je roditelj svih modela.

### 3.2 Users tabela

```python
class Users(Base):
    __tablename__ = "users"
```

`__tablename__` je stvarno ime tabele u bazi.

Kolone:

- `id`: integer, primarni kljuc
- `email`: string, unique
- `username`: string, unique
- `first_name`, `last_name`: string
- `hashed_password`: string
- `is_active`: boolean, default `True`
- `role`: string

### 3.3 Todos tabela

```python
class Todos(Base):
    __tablename__ = "todos"
```

Kolone:

- `id`: integer, primarni kljuc
- `title`: string
- `description`: string
- `priority`: integer
- `complete`: boolean, default `False`
- `owner_id`: integer, strani kljuc ka `users.id`

`owner_id = Column(Integer, ForeignKey("users.id"))` je prva prava relacija.
Time svaki todo pripada nekom user-u.

---

## 4) Objasnjenje najvaznijih Column opcija

## `primary_key=True`

Kazemo SQL-u: ovo je glavni identifikator reda.
Mora biti jedinstven i stabilan.

## `index=True`

Kreira se indeks nad kolonom (zavisi od baze i migracija/kreiranja).
Pomaze brze pretrage, npr. po `id`.

## `unique=True`

Sprecava duplikate.
Primer: dva user-a ne mogu imati isti `email`.

## `default=...`

Ako ne posaljes vrednost, uzima se default.
Primer: `complete=False` znaci da je novi todo po defaultu ne-zavrsen.

## `ForeignKey("users.id")`

Referencijalni integritet:
`owner_id` u `todos` mora pokazivati na postojeci `users.id`.

---

## 5) Transcript vs tvoj repo: zasto se razlikuju

U transkriptu lekcija 02 objasnjava pre svega `Todos` tabelu.
U tvom kodu vec postoje i `Users` + `owner_id` relacija.

To je normalno jer:

- kurs ide progresivno
- neki fajlovi u repo-u su iz kasnijih koraka

Zato je najbolja praksa da gledas:

1. sta lekcija uvodi kao koncept
2. kako je taj koncept prosiren u finalnijem kodu

---

## 6) Kako tabele stvarno nastaju u SQLite bazi

Model sam po sebi ne kreira tabelu odmah.
Tabela nastaje kada se izvrsi:

```python
models.Base.metadata.create_all(bind=engine)
```

U tvom projektu to je u `main.py`.

Posle toga u sqlite3 mozes proveriti:

```sql
.tables
.schema users
.schema todos
```

Ako tabela ne postoji, najcesce su razlozi:

- nisi pokrenuo app ili skriptu koja zove `create_all`
- otvorio si pogresan `.db` fajl
- modeli nisu importovani pre `create_all`

---

## 7) Mini SQL slika iza modela

Priblizno, ORM definicije bi dale SQL ideju slicnu ovoj:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE,
    username VARCHAR UNIQUE,
    first_name VARCHAR,
    last_name VARCHAR,
    hashed_password VARCHAR,
    is_active BOOLEAN DEFAULT 1,
    role VARCHAR
);

CREATE TABLE todos (
    id INTEGER PRIMARY KEY,
    title VARCHAR,
    description VARCHAR,
    priority INTEGER,
    complete BOOLEAN DEFAULT 0,
    owner_id INTEGER,
    FOREIGN KEY(owner_id) REFERENCES users(id)
);
```

Napomena: tacan SQL moze blago varirati po dijalektu i verziji.

---

## 8) Dobre navike koje su bitne vec sada

1. Razdvajaj odgovornosti

- `database.py`: engine/session/base
- `models.py`: tabele

2. Nemoj overfit-ovati sve u jednoj klasi

- jedna tabela = jedan jasan entitet

3. Razmisljaj o integritetu od starta

- `unique`, `foreign key`, `default`, posle i `nullable=False`

4. Cuvaj semantiku imena

- tabela plural (`users`, `todos`)
- kolona koja referencira user-a: `owner_id`

---

## 9) Ceste pocetnicke greske bas u ovoj lekciji

1. Mesanje Pydantic modela i SQLAlchemy modela

- Pydantic je za API ulaz/izlaz
- SQLAlchemy je za bazu

2. Mislis da je `index=True` isto sto i `unique=True`

- nije isto
- indeks ubrzava, unique ogranicava duplikate

3. Zaboravljen `ForeignKey`

- relacija ostaje samo "dogovor" u kodu, bez zastite baze

4. Pokretanje iz razlicitih foldera

- kreiras drugi `.db` fajl i deluje kao da "nema tabela"

---

## 10) Vezbe (od osnovnog ka srednjem)

## Vezba 1

Objasni svojim recima razliku:

- `primary_key`
- `unique`
- `index`

## Vezba 2

Dodaj u `Todos` novo polje:

- `created_at` (za sada moze `String` da ostane jednostavno)

Pitanje: sta treba da uradis da se ta kolona zaista pojavi u bazi?

## Vezba 3

Napravi mentalni ER odnos:

- jedan `Users`
- vise `Todos`

Nacrtaj strelicu i objasni gde je `ForeignKey`.

## Vezba 4

Nadji 2 mesta u kodu gde `owner_id` treba posebno proveravati zbog bezbednosti (autorizacija).

---

## 11) Brza samoprovera razumevanja

Ako mozes tacno da odgovoris na ova pitanja, lekcija je legla:

1. Zasto `class Todos(Base)` nasledjuje `Base`?
2. Sta radi `__tablename__`?
3. Da li model odmah kreira tabelu sam od sebe?
4. Cemu sluzi `ForeignKey("users.id")`?
5. Zasto su `email` i `username` cesto `unique=True`?

---

## 12) Zakljucak

Lekcija 02 deluje kratko, ali je kljucna.
Ovde prvi put formalno definises strukturu podataka aplikacije.

Kad razumes `models.py`, sledeci koraci (CRUD, auth, filtering, migracije) postaju logicni jer svi zavise od dobrog modela.

U jednoj recenici:
`database.py` otvara vrata baze, a `models.py` crta mapu kako baza izgleda.
