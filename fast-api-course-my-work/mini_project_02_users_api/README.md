# Mini projekat 2: Users API

Ovaj projekat uvodi query parametre i malo napredniju strukturu API-ja.

## Šta ovaj projekat uči?

- query parametre
- filtriranje podataka
- Response model
- Request model
- CRUD operacije za korisnike

---

## 1) Početna ideja

Ovaj API radi sa korisnicima i podržava:

- `GET /users` — lista svih korisnika
- `GET /users/{user_id}` — jedan korisnik po ID-u
- `POST /users` — kreiranje korisnika
- `PUT /users/{user_id}` — izmena korisnika
- `DELETE /users/{user_id}` — brisanje korisnika

Dodatno, `GET /users` podržava query parametre:

- `/users?role=admin`
- `/users?is_active=true`
- `/users?role=user&is_active=true`

---

## 2) Request model

```python
class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "user"
    is_active: bool = True
```

- `name` je obavezno
- `email` je obavezno
- `role` ima default vrednost `"user"`
- `is_active` ima default vrednost `True`

Ovo pokazuje kako se definišu opcionalna i default polja u Pydantic modelima.

---

## 3) Response model

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
```

- Ovaj model opisuje šta klijent dobija kao odgovor.
- Svi odgovori imaju konsistentan format.

---

## 4) Query parametri

```python
@app.get("/users", response_model=list[UserResponse])
def get_users(
    role: str | None = Query(default=None, description="Filter korisnika po roli."),
    is_active: bool | None = Query(default=None, description="Filter po aktivnom statusu."),
):
```

- `role` je opcioni query parametar.
- `is_active` je opcioni query parametar.
- Query parametri se pojavljuju nakon `?` u URL-u.

Primer:

```http
GET /users?role=admin
GET /users?is_active=true
GET /users?role=user&is_active=true
```

---

## 5) Filtriranje korisnika

```python
filtered_users = users

if role is not None:
    filtered_users = [user for user in filtered_users if user["role"] == role]

if is_active is not None:
    filtered_users = [user for user in filtered_users if user["is_active"] == is_active]
```

- Ovaj deo koda primenjuje filtere na listu.
- Ako je `role` dat, filtrira po roli.
- Ako je `is_active` dat, filtrira po statusu aktivnosti.

Ovo je najjednostavniji model za pretragu i filtriranje u API-ju.

---

## 6) GET /users/{user_id}

```python
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found")
```

- `user_id` je path parametar.
- URL primer: `/users/2`
- Ako korisnik ne postoji, vraća se 404.

---

## 7) POST /users

```python
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    new_user = {
        "id": len(users) + 1,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }
    users.append(new_user)
    return new_user
```

- `POST` se koristi za kreiranje novog korisnika.
- `user: UserCreate` prihvata JSON body.
- `status.HTTP_201_CREATED` znači da je novi korisnik napravljen.

---

## 8) PUT /users/{user_id}

```python
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate):
    for index, existing_user in enumerate(users):
        if existing_user["id"] == user_id:
            updated_user = {
                "id": user_id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
            }
            users[index] = updated_user
            return updated_user

    raise HTTPException(status_code=404, detail="User not found")
```

- `PUT` menja postojeće korisnike.
- `user_id` identifikuje kog korisnika menjamo.
- `user` sadrži novi sadržaj.

---

## 9) DELETE /users/{user_id}

```python
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for index, user in enumerate(users):
        if user["id"] == user_id:
            deleted_user = users.pop(index)
            return {
                "message": "User deleted successfully",
                "deleted_user": deleted_user,
            }

    raise HTTPException(status_code=404, detail="User not found")
```

- `DELETE` briše korisnika po ID-u.
- Ako korisnik ne postoji, vraća se 404.

---

## 10) Zašto je ovaj projekat važan?

Jer pokazuje realnu upotrebu:

- query parametara
- path parametara
- request modela
- response modela
- CRUD operacija

To je zapravo sledeći nivo razvoja API-ja posle osnovnih primerasa.

---

## 11) Kako pokrenuti projekat

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Zatim otvori:

- http://127.0.0.1:8000/docs

---

## 12) Šta treba da zapamtiš

- Query parametrima se dodatno filtriraju podaci.
- Path parametri se koriste za konkretan resurs.
- Request model definiše ulaz.
- Response model definiše izlaz.
- CRUD je osnovni obrazac API-ja.

---

Ovaj projekat je odličan prelaz ka složenijim API aplikacijama i SQLite bazama.
