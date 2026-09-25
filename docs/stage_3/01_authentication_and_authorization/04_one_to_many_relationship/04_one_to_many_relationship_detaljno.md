# Oblast 03 - Authentication and Authorization

## Lekcija 04 - One-to-many odnos između korisnika i todo zapisa

Ova lekcija uvodi prvi važan odnos između buduće `users` tabele (class `Users`) i postojeće `todos` (class `Todos`) tabele.

Ideja je:

> Jedan korisnik može imati više todo zapisa, ali jedan todo zapis pripada jednom korisniku.

Ovo je **one-to-many** odnos:

```text
jedan User  ->  mnogo Todos
```

U tvom aktivnom projektu ovaj odnos će se kasnije odraziti prvenstveno na:

```text
fast-api-course-my-work/TodoApp/models.py
```

Budući `auth` i `todo` routeri ostaju u:

```text
fast-api-course-my-work/TodoApp/api/routes/
```

Ova lekcija još ne implementira korisničku `users` (class `Users`) tabelu, `login` ili `JWT`. Ona priprema mentalni i bazni model za `ownership`, odnosno vlasništvo nad `todo` zapisima.

---

## 1) Šta znači one-to-many

Zamisli aplikaciju sa dva korisnika:

```text
Korisnik 1: Ana
    - kupiti namirnice
    - završiti izveštaj
    - zakazati pregled

Korisnik 2: Marko
    - pročitati knjigu
    - otići na trening
```

Ana ima više od jednog `todo` zapisa. Marko takođe ima više od jednog `todo` zapisa.

To ne znači da u bazi postoji samo jedan korisnik. Znači da **svaki pojedinačni korisnik može imati više todo zapisa**.

Relacija izgleda ovako:

```text
Users
    user 1 --------------+
                          +-- todo 1 (owner_id = 1)
                          +-- todo 2 (owner_id = 1)
                          +-- todo 3 (owner_id = 1)

    user 2 --------------+
                          +-- todo 4 (owner_id = 2)
                          +-- todo 5 (owner_id = 2)
```

Ni jedan `todo` zapis ne pripada istovremeno Ani i Marku. Jedan `todo` zapis može imati samo jednog vlasnika.

---

## 2) Dve odvojene tabele

U relacionoj bazi podataka korisnici (`users`) i todo zapisi (`todos`) treba da budu odvojene tabele.

### Tabela `users`

Buduća tabela korisnika može imati kolone slične ovima:

| Kolona            | Uloga                              |
| ----------------- | ---------------------------------- |
| `id`              | primarni ključ korisnika           |
| `email`           | email korisnika                    |
| `username`        | korisnicko ime                     |
| `first_name`      | ime                                |
| `last_name`       | prezime                            |
| `hashed_password` | sačuvan `hash` password-a          |
| `is_active`       | da li je nalog aktivan             |
| `role`            | uloga korisnika (npr. admin, user) |

---

### Tabela `todos`

Postojeća tabela trenutno ima:

| Kolona        | Uloga                            |
| ------------- | -------------------------------- |
| `id`          | primarni ključ `todo` zapisa     |
| `title`       | naslov zadatka                   |
| `description` | opis zadatka                     |
| `priority`    | prioritet                        |
| `complete`    | status kompletiranosti           |
| `owner_id`    | ID korisnika kome `todo` pripada |

Da bi se tabele povezale, `todos` dobija novu kolonu:

```text
owner_id (foreign key koji referencira (pokazuje) na users.id)
```

`owner_id` kolona čuva ID korisnika kome `todo` pripada. Kada se pogledaju vrednosti u toj koloni (npr. `1` ili `2`), može se odrediti kojem korisniku svaki `todo` zapis pripada na osnovu `id` kolone u `users` tabeli.

Na primer, ako `owner_id` u `todos` tabeli ima vrednost `1`, to znači da taj `todo` zapis pripada korisniku čiji je `id` u `users` tabeli `1`. Uvođenje stranog ključa omogućava ovu vezu između tabela. Strani ključ osigurava referencijalni integritet, što znači da `owner_id` uvek mora odgovarati nekom `id` u `users` tabeli.

Jednostavno rečeno, sada svaki `todo` zapis (jedan red u `todos` tabeli) ima i svog vlasnika, koji mora biti jedinstveni korisnik (zbog stranog ključa `owner_id`) iz `users` tabele.

---

## 3) Primarni i strani ključ

### Primarni ključ

Primarni ključ jedinstveno identifikuje red u tabeli.

U `users` tabeli:

```text
users.id = 1
```

Dobijamo korisnika čiji je primarni ključ `id` jednak `1`. U našem primeru jednog korisnika
čine `email`, `username`, `first_name`,`last_name`, `hashed_password` i `is_active` vrednosti kako su definisane u `users` tabeli.

U `todos` tabeli:

```text
todos.id = 1
```

Dobijamo `todo` zapis čiji je primarni ključ `id` jednak `1`. U našem primeru jedan `todo` zapis čine `title`, `description`, `priority`, `complete` i `owner_id` vrednosti kako su definisane u `todos` tabeli.

Na primer za korisnika sa `id` jednakim `1` za `users` tabelu dobijamo:

```text
users
-----+----------+------------------ +------------+-----------+------------+----------------+
| id | username |         email     | first_name | last_name | hashed_password | is_active |
-----+----------+------------------ +------------+-----------+-----------------+-----------+
|  1 | ana      | ana@example.com   | Ana        | Petrović  | hashed_pw       | true      |
|  2 | marko    | marko@example.com | Marko      | Perović   | hashed_pw       | true      |
-----+----------+------------------ +------------+-----------+-----------------+-----------+
```

---

### Strani ključ (foreign key)

Strani ključ je kolona koja čuva vrednost primarnog ključa iz druge tabele.

U `todos` tabeli:

```text
todos.owner_id -> users.id
```

Ako `owner_id` ima vrednost `1`, to znači da `todo` pripada korisniku čiji je `users.id` jednak `1`.

Važno je razlikovati:

```text
todos.id (primarni ključ)
```

od:

```text
todos.owner_id (strani ključ)
```

- `id` identifikuje sam `todo` zapis
- `owner_id` identifikuje korisnika koji je vlasnik tog zapisa

---

## 4) Primer podataka sa owner ID vrednostima

Pretpostavimo da postoje dva korisnika:

```text
users
+----+-------------------+
| id | username          |
+----+-------------------+
|  1 | ana_petrović      |
|  2 | marko_marković    |
+----+-------------------+
```

I šest `todo` zapisa:

```text
todos
+----+----------------------+----------+----------+
| id | title                | complete | owner_id |
+----+----------------------+----------+----------+
|  1 | izneti smeće         | false    | 1        |
|  2 | kupiti namirnice     | false    | 1        |
|  3 | zakazati šišanje     | true     | 1        |
|  4 | pročitati knjigu     | false    | 2        |
|  5 | otići na trening     | false    | 2        |
|  6 | srediti sto          | true     | 2        |
+----+----------------------+----------+----------+
```

Tumačenje:

```text
owner_id = 1  -> todo pripada korisniku users.id = 1
owner_id = 2  -> todo pripada korisniku users.id = 2
```

`Baza` ne čuva celo ime korisnika u svakom `todo redu`. Čuva samo njegov `ID`, a veza između tabela govori na kog korisnika se taj `ID` odnosi.

---

## 5) Kako ovo izgleda u SQLAlchemy modelu

Trenutni `TodoApp/models.py` sadrži samo `Todos` model:

```python
class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
```

Kada bude uveden `Users` model, `Todos` će dobiti dodatnu kolonu za strani ključ.

Kursni konceptualni oblik može izgledati ovako:

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

Najvažniji deo je:

```python
owner_id = Column(Integer, ForeignKey("users.id"))
```

To znači:

- `owner_id` je celobrojna kolona
- njena vrednost treba da predstavlja ID korisnika iz tabele `users`
- `ForeignKey("users.id")` opisuje vezu sa `users.id`, tj. da vrednost u koloni `owner_id` mora odgovarati nekom `id` iz tabele `users`.

U tvom projektu ovaj kod pripada `TodoApp/models.py`, a ne routeru i ne `schemas.py` fajlu.

---

## 6) Gde se smešta `Users` model

U ovoj fazi tvog projekta postoji samo `Todos` model u:

```text
TodoApp/models.py
```

Kurs kasnije uvodi `Users` tabelu. Za trenutnu organizaciju najjednostavniji prelazni oblik je da oba `SQLAlchemy` modela ostanu u istom fajlu:

```text
TodoApp/models.py
    class Todos(Base)
    class Users(Base)
```

To je u skladu sa postojećim projektom i lakše je za učenje.

Kasnije, kada broj modela poraste, moguća je organizacija:

```text
TodoApp/
    models/
        __init__.py
        todo.py
        user.py
```

Međutim, to je posebna refaktorizacija i ne treba je uvoditi samo zato što je uveden prvi strani ključ. Za sada je dovoljno razumeti da relacijska veza pripada SQLAlchemy modelima u `models.py`.

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

Sama kolona `owner_id` ne obezbeđuje automatski bezbednost.

Ona samo cuva vezu izmedju reda u `todos` tabeli i reda u `users` tabeli.

Endpoint mora pravilno da koristi tu vezu.

Nesigurna logika bi bila:

```python
@app.get("/todo/user/{user_id}")
async def read_user_todos(user_id: int):
    return db.query(Todos).filter(Todos.owner_id == user_id).all()
```

Ako aplikacija nema dodatnu proveru, klijent bi mogao da promeni `user_id` iz `1` u `2` i pokušа da čita tuđe podatke.

Bezbedniji budući oblik koristi identitet dobijen iz validiranog tokena:

```python
current_user_id = current_user.get("id")

return (
    db.query(Todos)
    .filter(Todos.owner_id == current_user_id)
    .all()
)
```

Ovaj koncept će se obrađivati detaljnije nakon uvodjenja korisnika, password hash-a i JWT-a.

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

## 13) Šta se dešava sa postojecim podacima

Dodavanje nove `owner_id` kolone nije samo promena Python koda. To je promena strukture baze podataka.

Postojeća tabela može već imati todo zapise koji nemaju vlasnika. Zato se mora razmisliti o migraciji:

```text
stara tabela todos
    nema owner_id

nova tabela todos
    ima owner_id
```

U razvojnom projektu sa SQLite bazom ponekad se tabela ponovo napravi, ali to može obrisati podatke. U realnom projektu se koristi migracioni alat, kao što je Alembic.

Vazna napomena:

```python
Base.metadata.create_all(bind=engine)
```

uglavnom kreira tabele koje ne postoje. Ne treba ga posmatrati kao potpun sistem za bezbedno menjanje već postojecih tabela.

Kada dodjemo do implementacije `Users` modela i `owner_id`, prvo treba odlučiti:

- da li je baza samo razvojna
- da li postoje podaci koje treba sačuvati
- da li se koristi Alembic migracija
- da li `owner_id` sme privremeno biti `NULL`
- kako se postojeći podaci dodeljuju korisniku

---

## 14) Budući raspored fajlova u TodoApp projektu

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

`One-to-many` veza pripada modelima, ali se koristi u todo endpointima i security logici.

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

Ovde je važno da `owner_id` dolazi iz autentifikovanog korisnika, a ne iz proizvoljnog podatka klijenta.

---

## 16) Šta ova lekcija još ne implementira

Transkript samo objašnjava odnos tabela i dodavanje `owner foreign key koncepta`.

Ova lekcija još ne uvodi potpuno:

- `Users` SQLAlchemy model u aktivni kod
- registraciju korisnika
- password hashing
- login
- JWT token
- `current_user` dependency
- admin role
- Alembic migraciju
- filtriranje svih postojećih todo ruta po vlasniku

Te teme dolaze postepeno u narednim lekcijama.

Zato ne treba sada samostalno dodavati `owner_id` u aktivni model ako želiš da pratiš kurs korak po korak. Teorijski cilj ove lekcije je da razumeš zašto će ta kolona biti potrebna.

---

## 17) Pitanja za proveru znanja

1. Šta znači `one-to-many` odnos?

Odgovor: `one-to-many` znači da jedan zapis u jednoj tabeli može biti povezan sa više zapisa u drugoj tabeli. Ovo je tipično za odnos korisnika i njihovih todo zapisa, gde jedan korisnik može imati više todo zapisa, ali svaki todo zapis pripada samo jednom korisniku.

2. Zašto jedan korisnik može imati više `todo` zapisa?

Odgovor: Jedan korisnik može imati više `todo` zapisa jer je definisan `one-to-many` odnos između `users` i `todos` tabela. To znači da jedan korisnik (jedan zapis u `users` tabeli) može biti povezan sa više zapisa u `todos` tabeli.

3. Zašto jedan `todo` zapis u ovom modelu pripada jednom korisniku?

Odgovor: Odnos `many-to-one` znači da svaki `todo` zapis pripada jednom korisniku jer je definisan `many-to-one` odnos sa `users` tabelom. To znači da svaki `todo` zapis ima referencu (`owner_id`) na jednog korisnika, čime se osigurava da svaki `todo` zapis pripada tačno jednom korisniku.

4. Koje dve tabele učestvuju u ovom odnosu?

Odgovor: Dve tabele koje učestvuju u ovom odnosu su `users` i `todos`.

5. Šta je primarni ključ (`primary key`)?

Odgovor: Primarni ključ je kolona ili skup kolona koje jedinstveno identifikuju svaki zapis u tabeli. U `users` tabeli, `id` je primarni ključ, a u `todos` tabeli, `id` je primarni ključ.

6. Šta je strani ključ (`foreign key`)?

Odgovor: Strani ključ je kolona ili skup kolona u jednoj tabeli koja referencira primarni ključ u drugoj tabeli. U ovom slučaju, `owner_id` u `todos` tabeli je strani ključ koji referencira `id` kolonu u `users` tabeli.

7. Na koju kolonu pokazuje `ForeignKey("users.id")`?

Odgovor: `ForeignKey("users.id")` pokazuje na `id` kolonu u `users` tabeli, što znači da `owner_id` u `todos` tabeli referencira `id` kolonu u `users` tabeli.

8. Zašto se `owner_id` nalazi u `todos` tabeli, a ne u `users` tabeli za svaki todo?

Odgovor: `owner_id` se nalazi u `todos` tabeli jer svaki todo zapis pripada jednom korisniku. Ako bismo stavili `owner_id` u `users` tabelu, morali bismo imati kolonu za svaki todo zapis, što nije praktično i ne odražava pravilno `one-to-many` odnos. U `one-to-many` odnosu, strani ključ se nalazi u tabeli koja predstavlja "many" stranu, u ovom slučaju `todos` tabeli.

9. Koja je razlika između `todos.id` i `todos.owner_id`?

Odgovor: `todos.id` je primarni ključ koji jedinstveno identifikuje svaki todo zapis, dok je `todos.owner_id` strani ključ koji pokazuje na korisnika kojem todo zapis pripada.

10. Gde bi u tvom projektu pripadala definicija `owner_id`?

Odgovor: Definicija `owner_id` bi pripadala u `models.py` fajl, unutar `Todos` modela, jer predstavlja kolonu u `todos` tabeli koja je strani ključ ka `users` tabeli.

11. Zašto `owner_id` ne treba bez razmišljanja dodati u javni `TodoRequest`?

Odgovor: `owner_id` ne treba bez razmišljanja dodati u javni `TodoRequest` jer bi to omogućilo korisnicima da sami postavljaju ili menjaju vlasnika todo zapisa, što može dovesti do sigurnosnih problema i kršenja integriteta podataka. Umesto toga, vlasnik todo zapisa treba da se određuje na osnovu autentifikovanog korisnika.

12. Kako se filtriraju todo zapisi jednog korisnika?

Odgovor: Todo zapisi jednog korisnika se filtriraju pomoću `owner_id` kolone. Na primer, za korisnika sa ID-em `3`, upit bi izgledao ovako:

```python
db.query(Todos).filter(Todos.owner_id == 3).all()
```

13. Zašto `owner_id` sam po sebi ne predstavlja autentifikaciju?

Odgovor: `owner_id` sam po sebi ne predstavlja autentifikaciju jer samo pokazuje na korisnika kojem todo zapis pripada, ali ne potvrđuje identitet korisnika koji pravi zahtev. Autentifikacija zahteva proveru identiteta korisnika, na primer putem tokena ili sesije, kako bi se osiguralo da korisnik zaista ima pravo da pristupi ili menja određene podatke.

14. Šta može biti problem sa postojećim todo podacima kada se doda nova obavezna kolona?

Odgovor: Problem može nastati ako postojeći todo zapisi nemaju vrednost za novu obaveznu kolonu. U tom slučaju, baza podataka neće dozvoliti unos ili ažuriranje zapisa bez te vrednosti, što može dovesti do grešaka ili potrebe za migracijom podataka kako bi se popunile vrednosti za novu kolonu.

15. Koja je razlika između `one-to-many` i `many-to-many` odnosa?

Odgovor: `one-to-many` odnos znači da jedan zapis u jednoj tabeli može biti povezan sa više zapisa u drugoj tabeli, dok `many-to-many` odnos znači da više zapisa u jednoj tabeli može biti povezano sa više zapisa u drugoj tabeli. U kontekstu korisnika i todo zapisa, jedan korisnik može imati više todo zapisa (`one-to-many`), ali jedan todo zapis pripada samo jednom korisniku. Ovo je tipičan scenario za `one-to-many` odnos.

`many-to-many` bi bio slučaj kada, na primer, todo zapis može biti dodeljen više korisnika i korisnik može imati više todo zapisa. Ovo se obično implementira pomoću dodatne tabele koja povezuje korisnike i todo zapise.

16. Koja je uloga `models.py`, a koja `api/routes/todos.py` u ovoj arhitekturi?

## Odgovor: `models.py` sadrži definiciju strukture podataka i odnosa između tabela, uključujući kolone i strane ključeve. `api/routes/todos.py` sadrži rute i logiku za rukovanje HTTP zahtevima vezanim za todo zapise, kao što su kreiranje, čitanje, ažuriranje i brisanje todo zapisa. Ukratko, `models.py` definiše kako podaci izgledaju, dok `api/routes/todos.py` definiše kako se ti podaci koriste i izlažu kroz API.

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

Označi:

- primarne ključeve (npr. `id` u obe tabele)
- strani ključ (npr. `owner_id` u tabeli `todos`)
- smer relacije (npr. jedan korisnik ima više todo zapisa)
- primer da jedan user ima tri todo zapisa (npr. korisnik sa `id` 1 ima todo zapise sa `id` 101, 102 i 103)

---

### Zadatak 2 - Tumačenje podataka

Za sledeće podatke objasni kome pripada svaki todo:

```text
users:
1 - ana
2 - marko

 todos:
101 - owner_id 1
102 - owner_id 1
103 - owner_id 2
```

Napiši koliko todo zapisa ima Ana, a koliko Marko.

---

### Zadatak 3 - Napiši SQLAlchemy kolonu

U posebnom tekstualnom primeru napiši import i model kolonu potrebnu za foreign key:

```python
from sqlalchemy import ForeignKey

owner_id = Column(Integer, ForeignKey("users.id"))
```

Objasni svaki deo izraza svojim rečima.

Ne menjaj još aktivni `models.py` ako korisnički model još nije uveden u praktičnom delu kursa.

---

### Zadatak 4 - Napiši ownership upit

Napiši SQLAlchemy upit koji vraća samo todo zapise za korisnika sa ID-em `3`.

Očekuje se oblik sličan:

```python
db.query(Todos).filter(Todos.owner_id == 3).all()
```

Zatim objasni zašto ovaj upit sam po sebi još ne dokazuje da je zahtev poslao korisnik sa ID-em `3`.

---

### Zadatak 5 - Pronađi bezbednosni problem

Analiziraj ovaj endpoint:

```python
@app.get("/todo/user/{user_id}")
async def read_user_todos(user_id: int):
    return db.query(Todos).filter(Todos.owner_id == user_id).all()
```

Odgovori:

- Šta klijent može da promeni?
- Čije podatke bi mogao da pokuša da pročita?
- Koji podatak bi u budućnosti trebalo da dolazi iz current user dependency-ja?

---

### Zadatak 6 - Razdvoji model i schemu

Napravi dve liste:

```text
Podaci koje klijent sme da pošalje:

Podaci koje aplikacija kontroliše:
```

Razvrstaj:

- `title`
- `description`
- `priority`
- `complete`
- `owner_id`
- `id`

Cilj je da pre uvođenja JWT-a razumeš zašto svi podaci iz baze ne treba automatski da budu pod kontrolom klijenta.

---

### Zadatak 7 - Predvidi promenu strukture

Napravi plan od najmanje pet koraka za buduću implementaciju `one-to-many` odnosa u tvom projektu.

Plan treba da sadrži:

1. dodavanje `Users` modela
2. dodavanje `owner_id` u `Todos`
3. proveru baze i migracije
4. dobijanje current user-a
5. filtriranje todo zapisa po vlasniku

---

### Zadatak 8 - Razmisli o migraciji

Pretpostavi da tabela `todos` već ima deset postojećih redova, a uvodiš novi `owner_id`.

Odgovori:

- Zašto ti podaci predstavljaju problem?

- ODGOVOR: Ti podaci predstavljaju problem jer novi `owner_id` ne može biti automatski dodeljen postojećim redovima bez dodatne logike ili migracije. Zbog toga je potrebno pažljivo planirati kako će se postojeći podaci ažurirati prilikom uvođenja novog kolone.

- Da li svi redovi mogu dobiti isti owner ID?

- ODGOVOR: Ne, jer svaki todo zapis treba da pripada određenom korisniku. Dodeljivanje istog owner ID-a svim redovima bi narušilo integritet podataka i ownership logiku.

- Kada bi koristio migraciju?

- ODGOVOR: Migraciju bi koristio kada želiš da dodaš novi `owner_id` u postojeću tabelu `todos` bez gubitka podataka i da bi se osiguralo da svi postojeći redovi dobiju validne vrednosti za novi kolonu.

- Zašto `create_all()` nije dovoljan alat za svaku promenu postojeće tabele?

- ODGOVOR: `create_all()` nije dovoljan alat za svaku promenu postojeće tabele jer on samo kreira tabele koje ne postoje. Ne može da menja postojeće tabele, dodaje nove kolone ili vrši migracije podataka. Za takve promene je potrebno koristiti migracione alate kao što je Alembic.

---

### Zadatak 9 - Poveži putanje sa odgovornostima

Popuni sledeću mapu:

```text
TodoApp/models.py              ->
TodoApp/schemas.py             ->
TodoApp/api/routes/todos.py    ->
TodoApp/api/routes/auth.py     ->
TodoApp/db/session.py          ->
TodoApp/main.py                ->
```

Za svaki fajl napiši jednu ili dve konkretne odgovornosti u kontekstu korisnika i todo zapisa.

---

## 19) Zaključak

One-to-many odnos opisuje vezu:

```text
jedan korisnik -> mnogo todo zapisa
```

U bazi se ta veza realizuje tako što `todos` tabela dobija strani ključ:

```text
todos.owner_id -> users.id
```

Za tvoj projekat to znači:

- SQLAlchemy veza pripada `TodoApp/models.py`
- budući todo endpointi pripadaju `TodoApp/api/routes/todos.py`
- autentifikacioni endpointi pripadaju `TodoApp/api/routes/auth.py`
- DB dependency ostaje u `TodoApp/db/session.py`
- glavna aplikacija ostaje u `TodoApp/main.py`
- `owner_id` će kasnije omogućiti filtriranje todo zapisa po korisniku
- pravi ownership mora da koristi autentifikovani identitet, a ne proizvoljan ID iz URL-a

Ova lekcija je most između običnog Todo CRUD-a i bezbedne multi-user aplikacije. Pre nego što korisnik može da vidi samo svoje podatke, baza mora znati koji todo pripada kom korisniku.
