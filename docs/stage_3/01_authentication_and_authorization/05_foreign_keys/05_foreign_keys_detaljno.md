# Oblast 03 - Authentication and Authorization

## Lekcija 05 - Foreign key i povezivanje korisnika sa todo zapisima

Ova lekcija detaljnije objasnjava foreign key, odnosno strani kljuc, i pokazuje kako se koristi za povezivanje `users` i `todos` tabela.

U prethodnoj lekciji uveden je one-to-many odnos:

```text
jedan korisnik -> mnogo todo zapisa
```

Sada se fokus pomera na konkretan mehanizam kojim se ta veza cuva u bazi:

```text
todos.owner_id -> users.id
```

Tvoj aktivni projekat trenutno jos nema `Users` model niti `owner_id` u `Todos` modelu. Ovaj dokument prvo gradi razumevanje, a implementacija dolazi kada kurs uvede korisnike i migraciju baze.

---

## 1) Sta je foreign key

Foreign key, ili strani kljuc, jeste kolona u jednoj relacionoj tabeli koja pravi vezu sa drugom tabelom.

On najcesce pokazuje na primary key druge tabele.

U nasem primeru:

```text
users.id       = primary key
 todos.owner_id = foreign key koji pokazuje na users.id
```

Mozemo zapisati relaciju ovako:

```text
todos.owner_id REFERENCES users.id
```

To znaci da vrednost u `todos.owner_id` predstavlja ID korisnika iz `users` tabele.

### Jednostavan primer

Ako u `users` tabeli postoji:

```text
id = 1
username = ana
```

onda red u `todos` tabeli sa:

```text
owner_id = 1
```

pripada Ani.

Foreign key ne cuva celo ime korisnika u todo redu. Cuva ID koji omogucava bazi da pronađe povezani korisnicki zapis.

---

## 2) Gde se foreign key nalazi u one-to-many odnosu

U one-to-many odnosu strani kljuc se nalazi na strani koja ima mnogo redova.

```text
users 1 -------- many todos
```

Zato se strani kljuc nalazi u `todos` tabeli:

```text
todos.owner_id
```

Ne dodajemo po jednu posebnu kolonu u `users` tabelu za svaki todo zapis. Takav pristup bi bio nefleksibilan i narusio bi normalan relacioni dizajn.

Ispravan raspored je:

```text
users
+----+----------+
| id | username |
+----+----------+
|  1 | ana      |
|  2 | marko    |
+----+----------+

 todos
+-----+----------------------+----------+
| id  | title                | owner_id |
+-----+----------------------+----------+
| 101 | kupiti namirnice    | 1        |
| 102 | zavrsiti izvestaj   | 1        |
| 103 | otici na trening    | 2        |
+-----+----------------------+----------+
```

---

## 3) Trenutno stanje tvog projekta

Trenutni `TodoApp/models.py` sadrzi:

```python
from sqlalchemy import Boolean, Column, Integer, String

from .db.base import Base


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
```

U ovom trenutku model nema:

```python
from sqlalchemy import ForeignKey

owner_id = Column(Integer, ForeignKey("users.id"))
```

Zato trenutno ne postoji baza za filtriranje todo zapisa po korisniku.

Buduci ciljni oblik modela je konceptualno:

```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .db.base import Base


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
```

Ovaj kod se jos ne dodaje automatski u aktivni projekat, jer `users` tabela i `Users` model jos nisu uvedeni.

---

## 4) Sta znaci `ForeignKey("users.id")`

Razlozimo izraz:

```python
owner_id = Column(Integer, ForeignKey("users.id"))
```

### `owner_id`

Naziv kolone u `todos` tabeli.

### `Column(...)`

SQLAlchemy-u govori da definisemo kolonu baze.

### `Integer`

Vrednost je celobrojna. To odgovara tipu kolone `users.id`.

### `ForeignKey(...)`

Opisuje vezu sa drugom tabelom.

### `"users.id"`

Znaci:

```text
tabela users, kolona id
```

Cela definicija zato znaci:

> Napravi celobrojnu kolonu `owner_id` u `todos` tabeli, cija vrednost predstavlja referencu na `users.id`.

---

## 5) Foreign key cuva vezu, ali ne vraca podatke sam

Foreign key opisuje odnos izmedju tabela. On sam po sebi nije rezultat upita i ne prikazuje automatski username.

Na primer, ovaj red:

```text
todos.owner_id = 1
```

govori da todo pripada korisniku sa ID-em `1`.

Da bismo dobili sve podatke iz `users` reda, mogli bismo koristiti SQL `JOIN`, ali za filtriranje korisnikovih todo zapisa dovoljan je `WHERE` uslov:

```sql
SELECT *
FROM todos
WHERE owner_id = 1;
```

Ovaj upit vraca sve kolone i redove iz `todos` tabele ciji je `owner_id` jednak `1`.

---

## 6) Citanje svih tabela pomocu SQL-a

Transkript koristi ideju:

```sql
SELECT * FROM todos;
```

Zvezdica znaci da trazimo sve kolone.

Ovaj upit vraca sve redove i sve kolone iz `todos` tabele, na primer:

```text
id | title              | description | priority | complete | owner_id
---+--------------------+-------------+----------+----------+---------
1  | kupiti namirnice  | ...         | 2        | 0        | 1
2  | procitati knjigu  | ...         | 3        | 1        | 2
```

Za korisnike:

```sql
SELECT * FROM users;
```

mozemo dobiti:

```text
id | username | email
---+----------+--------------------
1  | ana      | ana@example.com
2  | marko    | marko@example.com
```

Primecujemo da `users` tabela ne mora imati foreign key kolonu za todo zapise. Veza je predstavljena na strani `todos`, zato sto jedan korisnik moze biti vlasnik vise todo redova.

---

## 7) Filtriranje po owner vrednosti

Ako je korisnikov ID `1`, SQL upit je:

```sql
SELECT * FROM todos WHERE owner_id = 1;
```

Rezultat sadrzi samo todo zapise korisnika sa primarnim kljucem `1`.

Za korisnika sa ID-em `2`:

```sql
SELECT * FROM todos WHERE owner_id = 2;
```

Dobijamo samo njegove zapise.

U SQLAlchemy ORM obliku:

```python
user_todos = (
    db.query(Todos)
    .filter(Todos.owner_id == user_id)
    .all()
)
```

Ako je:

```python
user_id = 1
```

SQLAlchemy konceptualno izvrsava upit slican:

```sql
SELECT * FROM todos WHERE owner_id = 1;
```

Ovde je `Todos.owner_id` atribut SQLAlchemy modela, a ne vrednost jednog konkretnog todo objekta.

---

## 8) Zasto ne moramo prvo da pretrazimo `users` tabelu

Ako zahtev vec sadrzi validan korisnicki ID, mogli bismo direktno filtrirati `todos` tabelu:

```sql
SELECT * FROM todos WHERE owner_id = 1;
```

Time preskacemo poseban upit tipa:

```sql
SELECT * FROM users WHERE id = 1;
```

To je ideja transkripta: kada aplikacija vec zna ID korisnika, moze ga koristiti za filtriranje todo zapisa.

Medjutim, recenica da zahtev ima user ID zahteva vaznu bezbednosnu dopunu:

```text
ID mora biti pouzdano dobijen iz autentifikovanog identiteta.
```

Nije dovoljno da klijent samo posalje broj `1` i da mu aplikacija poveruje.

Kasnije ce se taj ID izvuci iz JWT-a preko current user dependency-ja.

---

## 9) Buduci tok od JWT-a do foreign key filtera

Kada se uvede JWT, buduci tok ce izgledati ovako:

```text
1. korisnik se prijavi
2. aplikacija proveri kredencijale
3. aplikacija izda JWT
4. klijent salje JWT uz sledeci zahtev
5. FastAPI dependency proveri i dekodira JWT
6. dependency pronadje ili odredi current user
7. endpoint uzme current_user.id
8. query filtrira Todos.owner_id == current_user.id
```

Konceptualni kod:

```python
current_user_id = current_user.get("id")

user_todos = (
    db.query(Todos)
    .filter(Todos.owner_id == current_user_id)
    .all()
)
```

Veza kroz bazu je:

```text
JWT
    -> current user ID
        -> Todos.owner_id
            -> samo korisnikovi todo zapisi
```

Ova lekcija jos ne implementira JWT. Ona objasnjava zasto ce JWT korisnicki ID kasnije biti potreban za filtriranje.

---

## 10) Vazna razlika: user ID u URL-u i user ID iz JWT-a

Ova dva primera nisu jednako bezbedna.

### ID direktno iz URL-a

```python
@app.get("/todo/user/{user_id}")
async def read_user_todos(user_id: int):
    return db.query(Todos).filter(Todos.owner_id == user_id).all()
```

Klijent moze da promeni URL:

```text
/todo/user/1
/todo/user/2
/todo/user/3
```

Ako nema authorization provere, moze pokusati da cita tudje podatke.

### ID iz current user dependency-ja

Buduci bezbedniji obrazac je:

```python
@app.get("/todo")
async def read_my_todos(
    db: db_dependency,
    current_user: user_dependency,
):
    user_id = current_user.get("id")
    return db.query(Todos).filter(Todos.owner_id == user_id).all()
```

Ovaj primer je ilustracija buduce strukture. `user_dependency` jos ne postoji u aktivnom projektu.

Glavna razlika je izvor identiteta:

```text
URL vrednost        -> kontrolise klijent
validiran JWT       -> proverava server
```

---

## 11) Query filtriranje nije isto sto i JOIN

Za dobijanje korisnikovih todo zapisa dovoljan je filter:

```python
db.query(Todos).filter(Todos.owner_id == user_id).all()
```

Ako zelimo istovremeno podatke iz `users` i `todos`, mozemo koristiti JOIN:

```sql
SELECT todos.*, users.username
FROM todos
JOIN users ON todos.owner_id = users.id
WHERE users.id = 1;
```

Filter bez JOIN-a koristi samo vrednost `owner_id`:

```sql
SELECT *
FROM todos
WHERE owner_id = 1;
```

Oba pristupa mogu biti korisna, ali resavaju razlicite potrebe:

- `WHERE owner_id = ...` filtrira todo zapise
- `JOIN` kombinuje kolone iz povezanih tabela

Za trenutni cilj, odnosno dobijanje samo korisnikovih todo zapisa, dovoljan je `WHERE` filter.

---

## 12) Gde se ovaj kod smesta u tvom rasporedu

Kada se implementira autentifikovani Todo query, raspodela ce biti:

```text
TodoApp/models.py
    Todos.owner_id foreign key
    Users model

TodoApp/api/routes/todos.py
    endpoint koji filtrira Todos.owner_id

TodoApp/api/routes/auth.py
    register i login endpointi

TodoApp/db/session.py
    db_dependency

TodoApp/core/config.py
    buduci settings i security konfiguracija

TodoApp/main.py
    ukljucivanje routera
```

Nije preporuceno da SQL upit za korisnikove todo zapise bude u `main.py` ako je Todo router vec izdvojen.

Takodje, `models.py` ne treba da sadrzi HTTP endpoint funkcije, a `auth.py` ne treba da bude mesto za definiciju foreign key kolone.

---

## 13) Sta ova lekcija jos ne menja

Iako transkript govori o owner foreign key-ju, aktivni projekat jos nije spreman za kompletnu implementaciju bez dodatnih koraka.

Trenutno nema:

- `Users` modela
- `users` tabele
- `owner_id` kolone u bazi
- JWT tokena
- `user_dependency`
- autentifikovanog current user-a
- migracije koja dodaje novu kolonu postojecim podacima

Zato ovaj dokument ne menja aktivni `models.py` i ne dodaje rutu.

Kada implementacija dodje na red, promene treba uvoditi redom:

1. napraviti `Users` model
2. dodati `owner_id` foreign key u `Todos`
3. proveriti ili napraviti migraciju baze
4. napraviti korisnika
5. uvesti password hashing
6. napraviti login
7. izdati i dekodirati JWT
8. dobiti current user ID
9. filtrirati todo zapise po `owner_id`

---

## 14) Pitanja za proveru znanja

1. Sta je foreign key?
2. Na koji primary key pokazuje `todos.owner_id`?
3. Zasto se foreign key nalazi u `todos` tabeli?
4. Koja je razlika izmedju `todos.id` i `todos.owner_id`?
5. Sta znaci `ForeignKey("users.id")`?
6. Sta radi SQL upit `SELECT * FROM todos WHERE owner_id = 1`?
7. Kako isti filter izgleda u SQLAlchemy ORM obliku?
8. Zasto `users` tabela ne mora imati jednu kolonu za svaki todo zapis?
9. Koja je razlika izmedju filtriranja preko `WHERE` i povezivanja preko `JOIN`?
10. Zasto user ID iz URL-a nije dovoljan za bezbedan ownership?
11. Odakle bi u buducnosti trebalo dobiti pouzdan current user ID?
12. Gde u tvom projektu pripada foreign key definicija?
13. Gde pripada query koji vraca todo zapise current user-a?
14. Zasto se ova lekcija ne moze potpuno implementirati pre `Users` modela?
15. Koja je uloga JWT-a u buducem toku filtriranja?

---

## 15) Prakticni zadaci

### Zadatak 1 - Prevedi SQL u obican jezik

Objasni sledece upite svojim recima:

```sql
SELECT * FROM todos;
SELECT * FROM users;
SELECT * FROM todos WHERE owner_id = 1;
SELECT * FROM todos WHERE owner_id = 2;
```

Za svaki upit navedi:

- iz koje tabele cita
- koje kolone vraca
- koji redovi ulaze u rezultat

### Zadatak 2 - Procitaj tabelu

Za sledece podatke odredi rezultate upita:

```text
users:
1 - ana
2 - marko

 todos:
101 - kupiti namirnice - owner_id 1
102 - procitati knjigu  - owner_id 1
103 - otici na trening  - owner_id 2
104 - oprati auto       - owner_id 2
105 - zavrsiti izvestaj - owner_id 1
```

Odgovori:

- koji todo zapisi pripadaju Ani
- koji todo zapisi pripadaju Marku
- sta bi vratio `WHERE owner_id = 3`

### Zadatak 3 - Napisi SQLAlchemy filter

Napisi SQLAlchemy kod koji vraca todo zapise korisnika sa ID-em `5`:

```python
user_todos = (
    db.query(Todos)
    .filter(Todos.owner_id == 5)
    .all()
)
```

Zatim zameni broj `5` promenljivom `user_id`.

### Zadatak 4 - Povezi kolonu sa tabelom

Dopuni konceptualni model:

```python
class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    owner_id = Column(
        Integer,
        ______________________________,
    )
```

Napisi i objasni zasto je ciljna vrednost `users.id`.

### Zadatak 5 - Uporedi izvore user ID-a

Uporedi sledece izvore:

```python
user_id = path_user_id
```

```python
user_id = current_user.get("id")
```

Napisi koji je bezbedniji za ownership i zasto.

### Zadatak 6 - Napravi dijagram toka

Nacrtaj tok:

```text
JWT -> current user -> user ID -> owner_id filter -> todo results
```

Uz svaku strelicu napisi sta se desava.

### Zadatak 7 - Razdvoji odgovornosti fajlova

Za svaki deo odredi odgovarajuci fajl:

```text
ForeignKey("users.id")
SELECT/filter Todos po owner_id
get_db()
JWT decode logika
app.include_router(...)
```

Koristi sledece lokacije:

```text
TodoApp/models.py
TodoApp/api/routes/todos.py
TodoApp/db/session.py
TodoApp/core/config.py ili security modul
TodoApp/main.py
```

### Zadatak 8 - Pronadji problem u kodu

Analiziraj:

```python
@app.get("/todo/user/{user_id}")
async def read_user_todos(user_id: int, db: db_dependency):
    return db.query(Todos).filter(Todos.owner_id == user_id).all()
```

Odgovori:

- da li query tehnicki filtrira podatke
- koji security problem postoji
- sta bi promenio kada bude postojao current user dependency

### Zadatak 9 - Planiraj migraciju

Pretpostavi da tabela `todos` vec ima postojece podatke.

Napisi plan kako bi uveo `owner_id`, a da ne izgubis podatke. U plan ukljuci:

- backup ili kopiju razvojne baze
- `Users` model
- izbor pocetnog korisnika za stare redove
- migraciju kolone
- proveru rezultata upita

### Zadatak 10 - Proveri API dokumentaciju

Kada kasnije bude implementiran ownership filter u `TodoApp/api/routes/todos.py`, pokreni:

```bash
uvicorn TodoApp.main:app --reload
```

Otvori `/docs` i proveri:

- da li se Todo router pojavljuje
- da li endpoint koristi current user dependency
- da li ruta ne prima proizvoljan `user_id` ako to nije potrebno

---

## 16) Zakljucak

Foreign key povezuje red u jednoj tabeli sa primarnim kljucem druge tabele.

U Todo aplikaciji veza je:

```text
todos.owner_id -> users.id
```

SQL filtriranje izgleda ovako:

```sql
SELECT * FROM todos WHERE owner_id = 1;
```

SQLAlchemy oblik izgleda ovako:

```python
db.query(Todos).filter(Todos.owner_id == user_id).all()
```

Za tvoj projekat najvaznije je zapamtiti raspodelu:

- foreign key se definise u `TodoApp/models.py`
- query za todo zapise pripada `TodoApp/api/routes/todos.py`
- DB sesija i `db_dependency` ostaju u `TodoApp/db/session.py`
- JWT i current user kasnije obezbedjuju pouzdan korisnicki ID
- `TodoApp/main.py` sklapa aplikaciju i ukljucuje routere

Foreign key je mehanizam veze. JWT i authorization logika tek kasnije odlucuju da li trenutni korisnik sme da pristupi povezanim podacima.
