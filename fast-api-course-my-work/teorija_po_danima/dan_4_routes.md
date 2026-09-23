# Dan 4 - Routes (auth, todos, router)

## Pitanje 1

PITANJE: Prilikom kreiranja POST funkcije, da li treba da vratim `todos_model` koji sam postovao ili ne treba da vrati ništa, već samo obaveštenje da je uspešno kreiran `todos`?

---

## Odgovor 1

ODGOVOR: `Treba` da vratiš `todos_model` koji si postovao. Na taj način klijent dobija potvrdu o uspešnom kreiranju i može odmah da koristi podatke novokreiranog `todo` zapisa kao što su ID i ostali atributi.

---

### Objašnjenje

U tvom slučaju je dobro da `POST` funkcija vrati kreirani `Todo` objekat:

```python
db.add(todo_model)
db.commit()
db.refresh(todo_model)

return todo_model
```

Tako klijent odmah dobija:

- generisani `id`
- `title`
- `complete`
- eventualno druge vrednosti iz baze

To je uobičajen REST pristup:

```text
POST uspešan -> 201 Created + kreirani resurs
```

Ako želiš da ne vraćaš sadržaj, možeš koristiti:

```python
@router.post("/todo", status_code=status.HTTP_204_NO_CONTENT)
```

i funkcija ne bi vraćala objekat. Tada klijent dobija samo informaciju da je operacija uspešna, ali ne dobija generisani `id`.

Za trenutni projekat preporučujem da zadržiš:

```python
return todo_model
```

Samo je u većem projektu bolje da response bude `TodoResponse` schema umesto direktnog SQLAlchemy modela.

---

## Pitanje 2

PITANJE: Da li kod `put` ide na kraju `db.refresh(todo_model)` i `return` izmenjenog `todo_model` ili je dovoljno samo `db.commit()`?

---

## Odgovor 2

ODGOVOR: Za `PUT` operaciju nije obavezno koristiti `db.refresh(todo_model)` i `return` izmenjenog modela ako ne vraćaš podatke klijentu. Dovoljno je samo `db.commit()`. Ovo je u skladu sa REST pristupom kada koristiš status kod `204 No Content`, što znači da operacija uspešno izvršena, ali ne vraća telo odgovora.

---

### Objašnjenje

Da, kod trenutnog endpointa je ispravno da **nema `return`**, zato što koristiš:

```python
status_code=status.HTTP_204_NO_CONTENT
```

Status `204` znači: uspešno izmenjeno, ali response nema body.

`db.refresh(todo_model)` ti ovde nije potreban jer izmenjeni objekat ne vraćaš klijentu. Možeš završiti ovako:

```python
for key, value in todo_request.model_dump().items():
    setattr(todo_model, key, value)

db.commit()
```

`db.add(todo_model)` takođe nije neophodan, jer je `todo_model` već učitan iz te SQLAlchemy sesije i session ga već prati.

Ako želiš da vratiš izmenjeni Todo, onda koristiš `200 OK`, `db.refresh()` i `return`:

```python
@router.put("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(...) -> Todos:
    ...

    db.commit()
    db.refresh(todo_model)

    return todo_model
```

Dakle:

```text
204 No Content -> commit(), bez refresh() i bez return-a
200 OK         -> commit(), refresh(), return todo_model
```

Za stil koji trenutno učiš, tvoj postojeći izbor `204` i `-> None` je sasvim odgovarajući.

---

## Pitanje 3

PITANJE: Da li je bolje koristiti `db.get(Todos, todo_id)` ili `db.query(Todos).filter(Todos.id == todo_id).first()` za dobijanje pojedinačnog `Todo` zapisa?

---

## Odgovor 3

ODGOVOR: Preporučuje se koristiti `db.get(Todos, todo_id)` kada želiš da dobiješ pojedinačni zapis po primarnom ključu. `db.get` je jednostavniji, čitljiviji i direktno koristi primarni ključ, dok `db.query(...).filter(...).first()` može biti korisno kada želiš da filtriraš po drugim kolonama ili koristiš složenije upite.

Takođe, `db.get` je optimizovan za primarni ključ i može koristiti keširanje unutar SQLAlchemy sesije, što može poboljšati performanse u poređenju sa `query().filter().first()`.

Međutim, `db.query(...).filter(...).first()` je fleksibilniji i omogućava složenije upite koji ne zavise samo od primarnog ključa.

U praksi, za jednostavne CRUD operacije nad primarnim ključem, `db.get` je obično bolji izbor zbog jednostavnosti i performansi. Za složenije upite ili filtriranje po drugim kolonama, koristi `query().filter().first()`.

---

## Pitanje 4

PITANJE: Da li je uredu deo za `brisanje` koji sam obeležio u skripti?

---

## Odgovor 4

ODGOVOR: Deo za `brisanje` koji si obeležio u skripti je uredu. Korišćenje `db.get(Todos, todo_id)` za dobijanje modela i zatim `db.delete(todo_model)` je ispravan način za brisanje zapisa. Takođe, provera da li model postoji pre brisanja i podizanje `HTTPException` sa statusom `404` ako nije pronađen je dobra praksa.

---

### Objašnjenje

Da, deo za brisanje je funkcionalno ispravan:

```python
todo_model = db.get(Todos, todo_id)

if todo_model is None:
    raise HTTPException(status_code=404, detail="Todo nije pronađen.")

db.delete(todo_model)
db.commit()
```

`db.get(Todos, todo_id)` pronalazi zapis po primarnom ključu, `db.delete()` ga označava za brisanje, a `db.commit()` trajno izvršava brisanje.

Preporučujem samo da eksplicitno dodaš status `204`:

```python
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
```

Pošto funkcija vraća `None`, `204 No Content` jasno govori da je brisanje uspešno i da nema response body-ja. `db.refresh()` i `return` ovde nisu potrebni.

---

## Pitanje 5

PITANJA:

1. Da li je `main.py` koji sam ti poslao sada dobar u smislu da sam obrisao endpointe i stavio ih u `todos.py`?
2. Da li se status importuje iz `starlette` ili iz `fastapi` modula?
3. Predložio si mi da kasnije pređem na `SQLAlchemy 2.0` ako se ne varam. Kada je taj momenat i koliko se razlikuje od `SQLAlchemy`-ja u kojem sada radim?

---

## Odgovor 5

ODGOVOR:

1. Da, `main.py` je sada dobar u smislu da si obrisao endpointe i stavio ih u `todos.py`. Ovo je dobra praksa jer omogućava bolju organizaciju koda i razdvajanje odgovornosti.

2. `status` se može importovati iz oba modula, ali u FastAPI projektima je uobičajeno koristiti `from fastapi import status`.

3. Prelazak na `SQLAlchemy 2.0` je preporučen kada želiš da koristiš najnovije funkcionalnosti i poboljšanja performansi. Razlike uključuju promene u API-ju za sesije i upite, kao i bolje tipiziranje i podršku za moderne Python funkcionalnosti. Prelazak nije hitan, ali je dobro planirati migraciju kada se projekt razvija dalje.

---

### Zaključak

1. Da li je `main.py` sada dobar?

Delimično. Endpointi jesu izdvojeni u `todos.py`, ali `main.py` trenutno **ne uključuje Todo router**:

```python
app.include_router(auth.router)
```

Potrebno je dodati:

```python
from .api.routes import auth, todos
```

i:

```python
app.include_router(auth.router)
app.include_router(todos.router)
```

Bez `app.include_router(todos.router)`, FastAPI neće registrovati Todo endpoint-e.

Takođe, preporučujem da kasnije dodaš prefix i tag direktno u `todos.py`:

```python
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)
```

Tada bi lokalne putanje mogle biti:

```python
@router.get("/")
@router.get("/{todo_id}")
@router.post("/")
@router.put("/{todo_id}")
@router.delete("/{todo_id}")
```

Trenutno imaš malo nedosledne putanje:

```text
/todo/{todo_id}
/todos/{todo_id}
/todo
```

To nije greška koja sprečava rad, ali je bolje koristiti jedan oblik, na primer `/todos`.

Kod delete endpointa možeš eksplicitno dodati:

```python
@router.delete(
    "/todo/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
```

---

2. Odakle se importuje `status`?

Preporučeno je:

```python
from fastapi import status
```

To koristiš upravo ovako:

```python
status.HTTP_200_OK
status.HTTP_201_CREATED
status.HTTP_204_NO_CONTENT
status.HTTP_404_NOT_FOUND
```

`status` zapravo dolazi iz Starlette ekosistema i može se importovati i ovako:

```python
from starlette import status
```

Oba pristupa rade, ali u FastAPI projektu koristi:

```python
from fastapi import status
```

To je jasnije i uobičajenije za FastAPI kod.

---

3. Kada preći na SQLAlchemy 2.0?

Ne moraš odmah da prelaziš. Tvoj trenutni kod koristi SQLAlchemy stil koji i dalje radi u SQLAlchemy 2.x verzijama:

```python
db.query(Todos).filter(Todos.id == todo_id).first()
```

To je stariji, ali još podržan ORM način.

Preporučeni trenutak za prelazak je:

1. završiš trenutni CRUD kod,
2. završiš teoriju i osnovnu implementaciju autentifikacije,
3. testiraš da postojeći kod radi,
4. zatim napraviš posebnu refaktorsku fazu za SQLAlchemy 2.0 stil.

Nemoj istovremeno učiti JWT, korisnike, authorization i novu SQLAlchemy sintaksu. To bi nepotrebno pomešalo više tema.

---

#### Trenutni stil

```python
todo_model = (
    db.query(Todos)
    .filter(Todos.id == todo_id)
    .first()
)
```

---

#### SQLAlchemy 2.0 stil

```python
from sqlalchemy import select

statement = select(Todos).where(Todos.id == todo_id)
todo_model = db.execute(statement).scalar_one_or_none()
```

Za listu:

```python
statement = select(Todos)
todos = db.execute(statement).scalars().all()
```

Za pronalaženje po primarnom ključu već koristiš moderniji oblik:

```python
todo_model = db.get(Todos, todo_id)
```

---

#### Glavne razlike

| Trenutni stil     | SQLAlchemy 2.0 stil            |
| ----------------- | ------------------------------ |
| `db.query(Todos)` | `select(Todos)`                |
| `.filter(...)`    | `.where(...)`                  |
| `.first()`        | `.scalar_one_or_none()`        |
| `query.all()`     | `execute(...).scalars().all()` |
| klasični modeli   | `Mapped` i `mapped_column`     |

SQLAlchemy 2.0 model može izgledati ovako:

```python
from sqlalchemy.orm import Mapped, mapped_column


class Todos(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    complete: Mapped[bool]
```

Za sada nastavi sa postojećim stilom dok završavaš trenutnu oblast. Nakon toga možemo uraditi odvojenu, kontrolisanu migraciju na SQLAlchemy 2.0 i testirati svaki endpoint posle promene.

---

## Pitanje 6

PITANJE: Da li je su sada ispravno povezani `todos.py` i `main.py`?

---

## Odgovor 6

ODGOVOR: Da, sada su oba fajla funkcionalno dobro organizovana za trenutnu fazu projekta.

`main.py` je ispravan jer:

```python
from .api.routes import auth, todos
```

i registruje oba routera:

```python
app.include_router(auth.router)
app.include_router(todos.router)
```

`todos.py` je takođe dobro organizovan:

```python
prefix="/todos"
tags=["todos"]
```

Konačne putanje su:

```text
GET    /todos/
GET    /todos/{todo_id}
POST   /todos/
PUT    /todos/{todo_id}
DELETE /todos/{todo_id}
```

Statusi su odgovarajući:

- `200 OK` za čitanje
- `201 Created` za kreiranje
- `204 No Content` za update i delete
- `404 Not Found` ako Todo ne postoji
- `422 Unprocessable Entity` za nevalidan `todo_id` ili payload

Provera fajlova je uspešna: **No errors found**.

Sitnice koje možeš kasnije urediti, ali trenutno nisu greške:

1. Dodaj prazan red između `db.commit()` i sledećeg dekoratora radi čitljivosti.
2. Možeš koristiti `status.HTTP_404_NOT_FOUND` i u `update_todo` i `delete_todo`, umesto direktnog `404`.
3. Dugačak komentar kod `update_todo` možeš kasnije skratiti ili ukloniti.
4. `auth.py` je još uvek samo privremeni placeholder, što je očekivano dok ne implementiraš stvarnu autentifikaciju.
