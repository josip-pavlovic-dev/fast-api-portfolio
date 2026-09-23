# Oblast 03 - Authentication and Authorization

## Lekcija 06 - Kreiranje Users tabele

Ova lekcija uvodi novu baznu tabelu za korisnike i prosiruje `Todos` model tako da svaki todo moze biti povezan sa svojim vlasnikom.

Prethodne lekcije su objasnile:

```text
one-to-many odnos
foreign key
owner_id
filtriranje todo zapisa po korisniku
```

Sada se prvi put spajaju u konkretnu strukturu baze:

```text
users tabela
    users.id

 todos tabela
    todos.owner_id -> users.id
```

### Vazna napomena za tvoj trenutni plan

Ovaj dokument je teorija i plan buduce implementacije. Dok ne zavrsimo celu teorijsku oblast, ne menjamo:

- `TodoApp/models.py`
- `TodoApp/db/database.py`
- `TodoApp/main.py`
- `TodoApp/schemas.py`
- routere
- bazu podataka

Kod u ovom dokumentu je primer ciljnog stanja, a ne zahtev da se sada kopira u projekat.

---

## 1) Zasto nam treba Users tabela

Do sada aplikacija ima samo `Todos` model. To je dovoljno za single-user CRUD vezbu, ali nije dovoljno za multi-user aplikaciju.

Ako vise korisnika koristi aplikaciju, moramo znati:

- ko je korisnik
- kako se korisnik identifikuje
- koji email i username pripadaju korisniku
- gde se cuva password hash
- da li je nalog aktivan
- koja je uloga korisnika
- koji todo zapisi pripadaju tom korisniku

Zato se uvodi posebna tabela:

```text
users
```

Jedna baza moze imati vise tabela:

```text
TodoApp baza
    +-- todos
    +-- users
```

To nije nova baza za korisnike. To je nova tabela unutar iste aplikacione baze.

---

## 2) Naziv baze naspram naziva tabele

Transkript pravi korisnu razliku izmedju naziva baze i naziva tabela.

Primer:

```text
SQLite baza: todoapp.db

Tabele:
    todos
    users
```

Naziv `todoapp.db` oznacava celu bazu podataka.

Naziv `todos` oznacava jednu tabelu unutar baze.

Naziv `users` oznacava drugu tabelu unutar iste baze.

Mozemo to zamisliti ovako:

```text
todoapp.db
    ├── todos
    └── users
```

Promena naziva SQLite fajla nije isto sto i preimenovanje tabele. To su dva razlicita nivoa:

```text
baza podataka -> sadrzi tabele
tabela        -> sadrzi redove i kolone
```

---

## 3) Zasto se u kursu menja naziv baze

Kursni projekat je u pocetku koristio naziv koji je mogao zbunjivati, na primer baza nazvana prema samo jednoj tabeli:

```text
todos.db
```

Kada baza kasnije sadrzi i `users` tabelu, razumljiviji naziv je:

```text
todoapp.db
```

To bolje opisuje celu aplikaciju, a ne samo Todo deo.

U tvom projektu buduci naziv treba da bude uskladjen sa konfiguracijom u:

```text
fast-api-course-my-work/TodoApp/db/database.py
```

Trenutno ne menjamo taj fajl. Kada dodje vreme za implementaciju, proverice se gde je definisan SQLite URL i zatim ce se svesno promeniti naziv.

---

## 4) Vazno upozorenje: promena ili brisanje SQLite baze

U kursnom primeru stara SQLite baza se brise da bi SQLAlchemy napravio novu bazu sa novom strukturom.

Ako se obrise fajl baze:

```text
stara baza.db
```

brisu se i podaci koji su bili u njoj:

```text
todos redovi
users redovi
```

Posle pokretanja aplikacije SQLAlchemy moze napraviti novu praznu bazu i nove tabele, ali ne moze vratiti prethodne podatke.

Zato je razlika izmedju razvojne i produkcione baze vazna:

### Razvojna baza

Ako su podaci samo vezba, moguce je obrisati bazu i poceti ponovo.

### Produkciona baza

Ne brise se rucno. Struktura se menja migracijama, a podaci se cuvaju.

Za migracije se koristi alat kao sto je Alembic.

### Pravilo za tvoj projekat

Pre bilo kakvog brisanja baze:

1. proveri koji je tacan fajl baze
2. napravi kopiju ako podaci imaju vrednost
3. potvrdi da je baza samo razvojna
4. proveri da nije pracena kao vazan git fajl
5. tek onda odluci da li je reset prihvatljiv

U ovoj fazi ne radimo nijedan od tih koraka, jer je trenutni cilj teorija.

---

## 5) Ogranicenje `Base.metadata.create_all`

U aplikaciji se koristi obrazac slican:

```python
Base.metadata.create_all(bind=engine)
```

Ovaj poziv moze da napravi tabele koje ne postoje.

Na primer, ako `Users` model postoji i tabela `users` ne postoji, SQLAlchemy moze da je kreira pri pokretanju aplikacije.

Ali `create_all()` nije pun sistem za promenu postojecih tabela.

Ako tabela `todos` vec postoji, a mi naknadno dodamo:

```python
owner_id = Column(Integer, ForeignKey("users.id"))
```

ne treba automatski pretpostaviti da ce `create_all()` bezbedno izmeniti postojecu tabelu.

Za ozbiljne promene koristi se migracioni alat:

```text
Alembic
```

Kurs ga uvodi kasnije, zato se u ovoj lekciji koristi jednostavniji razvojni pristup: nova ili resetovana baza.

---

## 6) Kreiranje `Users` SQLAlchemy modela

Buduci `Users` model pripada:

```text
fast-api-course-my-work/TodoApp/models.py
```

Konceptualni oblik izgleda ovako:

```python
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
```

Ovaj model nasledjuje `Base`, isto kao i postojeci `Todos` model.

### `__tablename__`

```python
__tablename__ = "users"
```

Odredjuje ime tabele u bazi.

### `id`

```python
id = Column(Integer, primary_key=True, index=True)
```

Svaki korisnik dobija jedinstveni ID.

### `email`

```python
email = Column(String, unique=True)
```

Email je tekstualna vrednost i ne sme se ponoviti ako je `unique=True`.

### `username`

```python
username = Column(String, unique=True)
```

I korisnicko ime treba da bude jedinstveno ako se koristi za prijavljivanje ili identifikaciju.

### `first_name` i `last_name`

Oni cuvaju osnovne podatke o korisniku.

### `hashed_password`

Cuva hash password-a, a ne originalni password.

### `is_active`

Odredjuje da li je nalog aktivan.

### `role`

Cuva ulogu, na primer:

```text
user
admin
```

Kasnije se koristi za autorizaciju.

---

## 7) Zasto se cuva `hashed_password`

Aplikacija ne treba da cuva password koji je korisnik uneo:

```text
password = "Test1234"
```

Umesto toga, password se provlaci kroz password hashing algoritam i cuva se rezultat:

```text
hashed_password = "$2b$..."
```

Pojednostavljen tok:

```text
password koji korisnik unese
    -> password hashing funkcija
        -> hashed_password u bazi
```

Pri login-u:

```text
password iz login zahteva
    -> ista biblioteka za proveru
        -> poredjenje sa sacuvanim hash-om
```

Aplikacija ne treba da radi:

```python
if entered_password == saved_plain_text_password:
    login_successful()
```

Niti treba sama da izmisli algoritam za hashing.

Koristi se proverena biblioteka i odgovarajuci password hashing algoritam. Konkretna biblioteka i implementacija dolaze u kasnijoj lekciji.

### Vazna preciznost

Hashing nije isto sto i enkripcija:

- enkripcija je namenjena da se podatak kasnije dekriptuje kljucem
- password hashing je jednosmerni proces za proveru password-a

Zato se originalni password ne dobija iz hash-a. Pri proveri se porede rezultat provere i sacuvani hash.

---

## 8) `is_active` i deaktiviran nalog

Korisnik moze postojati u bazi, ali nalog ne mora biti aktivan.

Primer:

```text
is_active = True
```

znaci da korisnik moze da koristi aplikaciju, u skladu sa ostalim proverama.

```text
is_active = False
```

moze znaciti da je nalog deaktiviran.

Buduca security logika moze odbiti zahtev neaktivnog korisnika:

```text
ako current_user.is_active nije True
    odbij zahtev
```

Transkript posebno povezuje neaktivan nalog sa nemogucnoscu pristupa njegovim todo zapisima.

To je authorization odluka, a ne samo podatak u bazi.

Kolona `is_active` sama ne blokira endpoint. Endpoint ili security dependency mora da je proveri.

---

## 9) `role` i buduca autorizacija

Kolona `role` moze da sadrzi vrednosti kao sto su:

```text
user
admin
```

Primer:

```text
username: ana
role: user
```

```text
username: marko
role: admin
```

Kasnije se mogu napraviti posebni endpointi za administratore.

Autentifikacija odgovara na pitanje:

```text
Ko je korisnik?
```

Autorizacija odgovara na pitanje:

```text
Sta taj korisnik sme da uradi?
```

`role` se koristi u drugom pitanju.

Na primer:

```python
if current_user.role != "admin":
    raise HTTPException(status_code=403, detail="Nedovoljna prava.")
```

Ovo je samo konceptualni primer. U aktivni projekat se jos ne dodaje.

---

## 10) Dodavanje `owner_id` u `Todos` model

Kada `Users` model postoji, `Todos` model se konceptualno prosiruje:

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

Veza znaci:

```text
todos.owner_id cuva users.id vrednost
```

Kada se korisnik prijavi i aplikacija zna njegov ID, novi todo moze dobiti taj ID kao vlasnika:

```python
todo_model = Todos(
    title=todo_request.title,
    description=todo_request.description,
    priority=todo_request.priority,
    complete=todo_request.complete,
    owner_id=current_user.id,
)
```

Ponovo, ovaj primer je buduci cilj. `current_user` jos nije dostupan u trenutnom projektu.

---

## 11) Kompletna buduca slika modela

Kada se spoje `Users` i `Todos`, konceptualna struktura je:

```python
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
```

Tabele su i dalje odvojene:

```text
users
    id, email, username, ..., role

todos
    id, title, description, ..., owner_id
```

Povezane su foreign key kolonom:

```text
todos.owner_id -> users.id
```

---

## 12) Zasto model pripada `models.py`

SQLAlchemy modeli opisuju strukturu baze.

Zato `Users` i `Todos` pripadaju:

```text
TodoApp/models.py
```

Ne pripadaju:

```text
TodoApp/api/routes/auth.py
TodoApp/api/routes/todos.py
TodoApp/main.py
```

Router zna kako da obradi HTTP zahtev i pozove model. Model zna kako izgleda tabela.

Podela odgovornosti:

```text
models.py
    tabela, kolone i foreign key veze

schemas.py
    validacija request i response podataka

api/routes/auth.py
    register i login HTTP endpointi

api/routes/todos.py
    Todo HTTP endpointi

main.py
    sklapanje FastAPI aplikacije
```

---

## 13) Buduci raspored fajlova

Kada se ova oblast kasnije implementira, tvoj raspored moze ostati:

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

Ova lekcija menja prvenstveno buduci sadrzaj:

```text
models.py
    Users model
    owner_id u Todos modelu

db/database.py
    smisleniji naziv SQLite baze
```

Ali dok traje teorijska faza, fajlovi ostaju nepromenjeni.

---

## 14) Sta se desava kada se aplikacija pokrene

Kada su modeli pravilno importovani pre:

```python
Base.metadata.create_all(bind=engine)
```

SQLAlchemy moze videti modele i napraviti tabele koje ne postoje.

Buduci tok za novu praznu razvojnu bazu:

```text
1. aplikacija ucita Base
2. aplikacija ucita Users i Todos modele
3. metadata zna za users i todos tabele
4. create_all proverava tabele
5. baza dobija users i todos
```

Vazno je da Python ucita model module. Ako model nije importovan, metadata mozda ne zna da taj model postoji.

U trenutnom projektu `main.py` vec importuje modele radi registracije tabela. Kada se doda `Users`, treba obratiti paznju da i novi model bude ucitan pre poziva `create_all()`.

Ovo je teorijsko objasnjenje, ne trenutna implementacija.

---

## 15) Gubitak starih Todo zapisa u kursnom primeru

Kurs brise staru bazu pre kreiranja nove strukture.

To znaci:

```text
stara todos tabela
    stari todo zapisi

brisanje database fajla
    svi stari podaci nestaju

novo pokretanje aplikacije
    nova prazna baza
    nova todos tabela
    nova users tabela
```

To je prihvatljivo samo zato sto je kursni primer u razvojnoj fazi i podaci mogu da se naprave ponovo.

Za tvoj projekat treba jasno razlikovati:

```text
reset razvojne baze
```

od:

```text
migracija baze sa ocuvanjem podataka
```

Reset je jednostavan, ali destruktivan. Migracija je zahtevnija, ali cuva postojece podatke.

---

## 16) Pitanja za proveru znanja

1. Zasto je potrebna posebna `Users` tabela?
2. Koja je razlika izmedju baze `todoapp.db` i tabele `todos`?
3. Gde se u tvom projektu definisu SQLAlchemy modeli?
4. Sta radi `__tablename__ = "users"`?
5. Zasto `email` i `username` mogu imati `unique=True`?
6. Zasto se cuva `hashed_password`, a ne plain-text password?
7. Koja je razlika izmedju hashing-a i enkripcije?
8. Sta znaci `is_active`?
9. Kako se `role` moze koristiti u autorizaciji?
10. Kako se `Todos.owner_id` povezuje sa `Users.id`?
11. Zasto `Base.metadata.create_all()` nije dovoljan za sve promene postojecih tabela?
12. Sta se gubi kada se obrise SQLite database fajl?
13. Zasto je brisanje baze prihvatljivije u razvojnom nego u produkcionom okruzenju?
14. Zasto `Users` model mora biti ucitan pre `create_all()`?
15. Koja je razlika izmedju resetovanja baze i Alembic migracije?
16. Zasto ova lekcija jos ne zahteva promenu tvog aktivnog koda?

---

## 17) Prakticni zadaci

### Zadatak 1 - Dizajniraj Users tabelu

Napravi tabelu u Markdown-u sa kolonama:

```text
id | email | username | first_name | last_name | hashed_password | is_active | role
```

Za svaku kolonu napisi:

- tip podatka
- da li treba da bude jedinstvena
- cemu sluzi

### Zadatak 2 - Prepoznaj opasne podatke

Razvrstaj sledece vrednosti u dve grupe:

```text
obicni korisnicki podaci
osetljivi/security podaci
```

Vrednosti:

- email
- username
- first_name
- last_name
- hashed_password
- is_active
- role

Objasni zasto se `hashed_password` ne vraca proizvoljno kroz javni API response.

### Zadatak 3 - Nacrtaj kompletnu bazu

Nacrtaj:

```text
TodoApp baza
    users tabela
    todos tabela
```

Oznaci:

- primary key u obe tabele
- foreign key u `todos`
- one-to-many smer
- primer dva korisnika i pet todo zapisa

### Zadatak 4 - Napisi ciljni model na papiru

Bez menjanja aktivnog fajla, napisi konceptualni SQLAlchemy kod za:

```python
class Users(Base):
    ...

class Todos(Base):
    ...
```

U `Users` ukljuci sve kolone iz lekcije, a u `Todos` dodaj `owner_id`.

### Zadatak 5 - Analiziraj brisanje baze

Odgovori na pitanja:

- sta se desava kada se obrise SQLite fajl
- sta se kreira pri sledecem pokretanju
- zasto se gube prethodni todos
- sta bi uradio pre brisanja baze

### Zadatak 6 - Reset ili migracija

Za svaki scenario izaberi da li je prihvatljiv reset ili je potrebna migracija:

1. prazna razvojna baza sa testnim podacima
2. produkciona baza sa registrovanim korisnicima
3. licni projekat bez vaznih podataka
4. baza koju koristi vise klijenata
5. vezba iz kursa gde se podaci mogu ponovo napraviti

Obrazlozi svaki izbor.

### Zadatak 7 - Objasni `create_all`

Napisi svojim recima:

```text
create_all moze da...
create_all ne treba posmatrati kao...
Alembic sluzi za...
```

Cilj je da razdvojis kreiranje nepostojecih tabela od migriranja postojecih tabela.

### Zadatak 8 - Povezi budući endpoint sa modelom

Napravi mapu odgovornosti:

```text
POST /auth/register
POST /auth/token
POST /todo
GET /todo
```

Za svaki endpoint navedi:

- koji router ce ga sadrzati
- koji model koristi
- da li koristi `Users`
- da li koristi `Todos`
- da li ce u buducnosti koristiti `current_user`

### Zadatak 9 - Proveri security tok

Objasni sledeci tok:

```text
plain password
    -> hash
        -> hashed_password u users tabeli

login password
    -> provera sa sacuvanim hash-om
        -> uspesna autentifikacija
```

Navedi zasto aplikacija ne mora da zna originalni password iz baze.

### Zadatak 10 - Napravi plan kasnije implementacije

Napisi plan kojim bi, tek posle zavrsetka teorije, implementirao ovu lekciju u svom projektu.

Plan mora da obuhvati:

1. backup razvojne baze
2. promenu naziva baze ako je potrebna
3. `Users` model
4. `owner_id` u `Todos`
5. proveru metadata i tabela
6. odluku reset ili migracija
7. proveru da se aplikacija pokrece

Za sada plan ostaje samo na papiru.

---

## 18) Zakljucak

Ova lekcija uvodi `Users` tabelu kao osnovu za autentifikaciju i autorizaciju.

Ciljna struktura je:

```text
users
    id, email, username, first_name, last_name,
    hashed_password, is_active, role

todos
    id, title, description, priority, complete, owner_id
```

Veza je:

```text
todos.owner_id -> users.id
```

Za tvoj projekat to znaci:

- `Users` i `Todos` pripadaju `TodoApp/models.py`
- buduća auth logika pripada `TodoApp/api/routes/auth.py`
- buduća Todo ownership logika pripada `TodoApp/api/routes/todos.py`
- database konfiguracija ostaje u `TodoApp/db/database.py`
- DB dependency ostaje u `TodoApp/db/session.py`
- glavna aplikacija ostaje u `TodoApp/main.py`

Najvaznije bezbednosne poruke su:

- password se ne cuva kao plain text
- `hashed_password` nije isto sto i enkripcija
- `is_active` mora da se proverava u security logici
- `role` se koristi za authorization odluke
- `owner_id` povezuje todo sa korisnikom
- brisanje baze brise podatke
- `create_all()` nije zamena za migracije

Dok traje teorijska faza, aktivne skripte ostaju nepromenjene. Implementacija `Users` tabele, foreign key-a, routera i security logike dolazi tek kada zavrsimo celu oblast i predjemo na praktican rad.
