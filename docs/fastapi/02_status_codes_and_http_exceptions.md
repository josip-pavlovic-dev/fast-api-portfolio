# Status code i HTTPException u FastAPI

Ovo je jedna od najvažnijih tema kad radiš sa API endpointima.

Status code ti govori klijentu da li je zahtev uspešno obrađen, neuspelo, ili je došlo do problema.

---

## 1) Šta je status code?

Status code je broj koji se vraća u HTTP odgovoru.

Najčešći su:

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

FastAPI automatski koristi status kodove, a ti ih možeš eksplicitno postaviti.

---

## 2) Najčešći status kodovi za početnike

### `200 OK`

Kada je zahtev uspešno obrađen i vraćaš normalan rezultat.

```python
@app.get("/books")
async def get_books():
    return {"message": "ok"}
```

### `201 Created`

Kada si napravio novi resurs, npr. novu knjigu.

```python
@app.post("/books", status_code=201)
async def create_book():
    return {"message": "Knjiga je kreirana"}
```

### `404 Not Found`

Kada resurs ne postoji.

```python
@app.get("/books/{book_id}")
async def get_book(book_id: int):
    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

### `422 Unprocessable Entity`

Kada validacija ne prođe.

Ovo FastAPI automatski radi za Pydantic modele ako pošalješ pogrešne podatke.

---

## 3) `status_code` parametar u decoratoru

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/books", status_code=201)
async def create_book():
    return {"message": "Uspešno kreirano"}
```

### Kako to radi?

FastAPI postavlja HTTP status kod kao deo odgovora.

U praksi to znači da klijent zna da je došlo do kreiranja novog resursa.

---

## 4) `HTTPException`

`HTTPException` je osnovni način da vraćaš grešku u API-u.

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/books/{book_id}")
async def get_book(book_id: int):
    if book_id == 999:
        raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
    return {"id": book_id, "title": "Python"}
```

### Šta ovo znači?

- ako je `book_id` 999, vraća se greška 404
- klijent dobija poruku `Knjiga nije pronađena`

---

## 5) `detail` polje

`detail` je najvažniji deo `HTTPException`-a.

```python
raise HTTPException(status_code=400, detail="Neispravan zahtev")
```

To je poruka koju klijent vidi u JSON odgovoru.

### Primer odgovora

```json
{
  "detail": "Neispravan zahtev"
}
```

---

## 6) `status_code` i `response_model` zajedno

Najlakši i najčistiji obrazac je da kombinuješ:

- `response_model` za format odgovora
- `status_code` za HTTP status

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class BookResponse(BaseModel):
    id: int
    title: str
    author: str

@app.post("/books", response_model=BookResponse, status_code=201)
async def create_book():
    return {"id": 1, "title": "Python", "author": "Marko"}
```

### Zašto je ovo dobro?

- API vraća u očekivanom obliku
- klijent zna da je resurs kreiran
- dokumentacija u Swagger-u je jasnija

---

## 7) Primer: GET, POST, 404 i 201

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str

class BookResponse(BaseModel):
    id: int
    title: str
    author: str

books = [
    {"id": 1, "title": "Python", "author": "Marko"}
]

@app.get("/books", response_model=list[BookResponse])
async def get_books():
    return books

@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")

@app.post("/books", response_model=BookResponse, status_code=201)
async def create_book(book: BookCreate):
    new_book = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author,
    }
    books.append(new_book)
    return new_book
```

---

## 8) `HTTPException` sa imenovanim greškama

Najčešće se koristi za:

- `404` — resurs nije pronađen
- `400` — loš zahtev
- `401` — neautorizovan
- `403` — zabranjen
- `409` — konflikt

### Primer

```python
raise HTTPException(status_code=409, detail="Knjiga već postoji")
```

---

## 9) `422` se automatski javlja od Pydantic-a

Ako pošalješ body koji ne odgovara modelu, FastAPI će automatski vratiti:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Field required",
      "type": "value_error.missing"
    }
  ]
}
```

### To znači:

- Pydantic je odbio zahtev
- `status_code` je 422
- klijent vidi poruku o validacijskom problemu

---

## 10) Kada koristiti `status_code` a kada `HTTPException`?

### Koristi `status_code` kada:

- endpoint radi normalno i samo vraća success rezultat
- želiš da eksplicitno definišeš HTTP status za uspešan odgovor

### Koristi `HTTPException` kada:

- postoji neki problem
- zahtev ne može da se obradi pravilno
- treba da vratiš detaljnu grešku

---

## 11) Najvažnije pravilo za pamćenje

- `200` = sve je u redu
- `201` = kreiran novi resurs
- `404` = nema resursa
- `400` = loš zahtev
- `422` = neispravna validacija
- `HTTPException` = način da vraćaš greške sa porukom

---

## 12) Kratka lista “šta treba da znaš”

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str

class BookResponse(BaseModel):
    id: int
    title: str
    author: str

@app.post("/books", response_model=BookResponse, status_code=201)
async def create_book(book: BookCreate):
    return {"id": 1, "title": book.title, "author": book.author}

@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    if book_id == 999:
        raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
    return {"id": book_id, "title": "Python", "author": "Marko"}
```

---

## 13) Prakticna vežba

Napravi endpoint:

- `POST /books` => status 201
- `GET /books/{book_id}` => ako ne postoji, status 404
- `GET /books` => vraća listu knjiga

Obavezno koristi:

- `BookCreate`
- `BookResponse`
- `response_model`
- `status_code`
- `HTTPException`

---

## 14) Zaključak

Status code i `HTTPException` su osnovni mehanizmi komunikacije između servera i klijenta.

Bez njih, API ne zna da li je nešto:

- uspešno izvršeno
- nepostojeće
- invalidno
- ili je došlo do greške

To je jedan od ključnih koraka ka ozbiljnom backend razvoju.

Naredni korak je da naučiš `POST`, `PUT` i `DELETE` i da ih povežeš u jedan CRUD obrazac.
