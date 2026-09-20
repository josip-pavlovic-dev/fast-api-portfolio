# Nadogradnja `main1.py` sa Pydantic validacijama i SQLAlchemy bazom

Na osnovu tvoje teorije (`Field`, `Path`, validacije, `model_dump()`) i naprednog dela iz `stage_2` (SQLAlchemy + SQLite do lekcije 05), evo dva odvojena zadatka: prvo nadograđivanje `main1.py` sa Pydantic validacijama, pa zatim uvođenje baze — po uzoru na obrazac koji već postoji u `database.py` i `models.py`.

## Deo 1: Nadogradnja `main1.py` sa `Field`, `Path`, validacijama

Radi ovo u `main1.py`, korak po korak.

### Korak 1 — `Field(...)` u `UserCreate`

Zameni gole tipove sa `Field(...)` validacijama:

- `name: str = Field(min_length=2, max_length=50)`
- `email: str = Field(min_length=5, max_length=100)` (za pravu validaciju emaila kasnije se koristi `EmailStr`, ali to nisi još učio — preskoči za sad)
- `role: str = Field(default="user", description="Uloga korisnika (npr. admin, user)")`
- `is_active: bool = Field(default=True, description="Da li je korisnik aktivan")`

**Zadatak:** dodaj i pravilo da `role` mora biti jedan od dozvoljenih stringova — probaj sa `Literal["admin", "user"]` umesto `str` (ovo je sledeći korak posle `Field`, korisno je da ga isprobaš).

PITANJE: Da li je `Literal["admin", "user"]` zastareo?
ODGOVOR: `Literal["admin", "user"]` nije zastareo; i dalje je preporučeni način da se ograniči skup dozvoljenih string vrednosti u Pydantic modelima. Nema novih preporuka koje bi ga zamenile. Importuje se iz `typing` modula:

```python
from typing import Literal
```

### Korak 1.1 — detaljnije o Literal tipovima

`Literal` tipovi omogućavaju da Pydantic modeli ograniče vrednosti polja na unapred definisani skup. Na primer:

```python
from typing import Literal
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    role: Literal["admin", "user"] = Field(default="user", description="Uloga korisnika (npr. admin ili user)")
```

U ovom primeru, `role` može biti samo `"admin"` ili `"user"`. Pokušaj da dodeliš neku drugu vrednost će izazvati grešku validacije.

---

### Korak 2 — `Path(...)` za `user_id`

Svuda gde imaš `user_id: int` u path parametru (`get_user`, `update_user`, `user_del`), zameni sa:

```python
user_id: int = Path(gt=0, description="ID korisnika mora biti veći od 0")
```

Ovo sprečava besmislene zahteve tipa `/users/-5`.

---

### Korak 3 — `UserResponse` bez default vrednosti

Primeti grešku koju si napravio: u `UserResponse` si stavio `role: str = "user"` i `is_active: bool = True` kao default.

Response model **ne treba** default vrednosti — on samo opisuje šta server vraća, a server uvek treba da vrati stvarnu vrednost. Ukloni te defaulte, ostavi samo tipove (`role: Literal["admin", "user"]`, `is_active: bool`).

---

### Korak 4 — `model_dump()` umesto ručnog rečnika

Trenutno ručno praviš `dict` u `create_user` i `update_user`. Zameni sa obrascem koji si već video u teoriji:

```python
new_user = {"id": len(users) + 1, **user.model_dump()}
```

Ovo je kraće i manje podložno greškama (ne moraš ručno navoditi svako polje).

---

### Korak 5 — najbolje prakse koje treba primeniti

- Nemoj mešati `str` i validaciju uloge ručno u kodu (`if role not in [...]`) — pusti Pydantic/`Literal` da to uradi za tebe.

- `Field(..., description=...)` koristi svuda gde želiš da se polje vidi u `docs`.

- Nemoj koristiti `raise HTTPException` unutar `else` grane petlje (u tvom `update_user` trenutno je `raise` uvučen unutar `for`, pa se izvršava posle prve neuspešne iteracije — ovo je bug, treba da bude van petlje, isto kao u `main.py`).

---

## Deo 2: Zadatak za bazu (SQLAlchemy + SQLite)

Pošto si stigao do lekcije 05 (`sqlite3_setting_up_Todos`), spreman si da napraviš isti sloj za korisnike, po uzoru na `app` folder.

---

### Korak 1 — `database.py`

Napravi fajl analogan `database.py`:

- `engine = create_engine("sqlite:///./users.db", connect_args={"check_same_thread": False})`
- `SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)`
- `get_db()` generator dependency koji otvara i zatvara sesiju (identično kao u referentnom fajlu).

**Pitanje za proveru razumevanja:** zašto je `check_same_thread=False` potrebno samo za SQLite, a ne za PostgreSQL?

---

### Korak 2 — ORM model `User`

Napravi `models.py` sa klasom `User(Base)`, po uzoru na `models.py`:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(20), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

**Zadatak:** dodaj `unique=True` na `email` i objasni sebi zašto je to dobra praksa (sprečava duplirane naloge na nivou baze, ne samo u kodu).

---

### Korak 3 — razdvoji `schemas.py` od `models.py`

Tvoji trenutni `UserCreate`/`UserResponse` (Pydantic) presele se u `schemas.py`, nepromenjeni po strukturi. Ovo je razlika koju treba da utvrdiš: `models.py` opisuje **tabelu u bazi**, `schemas.py` opisuje **oblik podataka u API-ju** — mogu izgledati slično, ali služe potpuno različitim slojevima.

Dodaj i konfiguraciju da Pydantic ume da čita ORM objekte direktno:

```python
class UserResponse(BaseModel):
    ...
    model_config = ConfigDict(from_attributes=True)
```

---

### Korak 4 — prebaci endpointe na sesiju

Za svaki endpoint dodaj `db: Session = Depends(get_db)` kao parametar i zameni logiku nad `users` listom sa upitima:

- `GET /users` → `db.query(User)` + `.filter(User.role == role)` ako je `role` prosleđen, isto za `is_active`

- `GET /users/{id}` → `db.query(User).filter(User.id == user_id).first()`, ako je `None` → `404`

- `POST /users` → `new_user = User(**user.model_dump())`, pa `db.add(new_user)`, `db.commit()`, `db.refresh(new_user)`

- `PUT /users/{id}` → pronađi objekat, izmeni atribute (`existing.name = user.name`, itd.), `db.commit()`, `db.refresh(existing)`

- `DELETE /users/{id}` → pronađi objekat, `db.delete(existing)`, `db.commit()`

---

### Korak 5 — inicijalizacija tabela

U `main1.py`, pri startu aplikacije, pozovi `Base.metadata.create_all(bind=engine)` (kao što piše u lekciji 03 `03_main_detaljno.md`) da se tabela `users` napravi ako ne postoji.

---

### Najbolje prakse za bazu

- Nikad ne drži globalnu listu paralelno sa bazom — jednom kad pređeš na DB, `users: list[...]` se briše potpuno.

- Uvek radi `commit()` posle `add`/`delete`, i `refresh()` kad ti treba auto-generisani `id` nazad.

- `get_db` dependency mora zatvarati sesiju u `finally`, bez obzira na uspeh/grešku (ovo već imaš kao obrazac u referentnom fajlu).

- Filtriranje po query parametrima radi kroz `.filter()` lanac, ne kroz Python list comprehension — bazu pusti da filtrira, ne aplikaciju.
