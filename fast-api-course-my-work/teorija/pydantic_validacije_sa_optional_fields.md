# Pydantic validacije sa optional fields

## Pydantic validacije i optional fields

Pydantic model ti govori:

- koje podatke očekuješ
- koji su obavezni
- koji su opcioni
- koji tipovi su dozvoljeni

### Osnovni primer

```python
from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None
```

Ovo znači:

- `title` je obavezno
- `author` je obavezno
- `description` je opciono
- ako ne pošalješ `description`, vrednost će biti `None`

---

### Primer validacije

```python
from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
    year: int | None = None
```

Ako pošalješ:

```json
{
  "title": "Python",
  "author": "Marko"
}
```

to će proći.

Ako pošalješ:

```json
{
  "title": 123,
  "author": "Marko"
}
```

to će vratiti 422, jer `title` mora biti string.

---

### Zašto je ovo važno?

Jer bez validacije:

- API prima bilo šta
- dolaze neispravni podaci
- backend postaje nepouzdan

FastAPI + Pydantic ti to rešava automatski.

---

### Najčešći slučajevi

```python
class Book(BaseModel):
    id: int
    title: str
    author: str
    description: str | None = None
```

Ovo je tipičan model:

- neki podaci su obavezni
- neki su opcioni

---

## 2) Mini CRUD primer sa response_model na svim endpointima

Ovo je najbolji način da sve spojiš u jedno.

### Ideja

Imamo listu knjiga u memoriji i pravimo API:

- GET /books
- GET /books/{book_id}
- POST /books
- PUT /books/{book_id}
- DELETE /books/{book_id}

### Primer koda

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str | None = None

books = [
    {"id": 1, "title": "Python za početnike", "author": "Marko", "description": None},
    {"id": 2, "title": "FastAPI uvod", "author": "Ana", "description": "Osnovni uvod"}
]

@app.get("/books", response_model=list[BookResponse])
def get_books():
    return books

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    new_book = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author,
        "description": book.description
    }
    books.append(new_book)
    return new_book

@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookCreate):
    for index, existing_book in enumerate(books):
        if existing_book["id"] == book_id:
            updated_book = {
                "id": book_id,
                "title": book.title,
                "author": book.author,
                "description": book.description
            }
            books[index] = updated_book
            return updated_book

    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            deleted_book = books.pop(index)
            return {
                "message": "Book deleted successfully",
                "deleted_book": deleted_book
            }

    raise HTTPException(status_code=404, detail="Book not found")
```

---

## 3) Šta ovo pokazuje?

Ovo je ključna stvar:

- `BookCreate` = šta klijent šalje
- `BookResponse` = šta server vraća
- `response_model` = ali se forma outputa uvek definiše
- `status_code` = govori klijentu da li je sve uspešno
- `HTTPException` = vraća 404 ako nema resursa

To je već pravi “početni beginner API” koji ima smisla.

---

## 4) Najvažnije za pamćenje

### Request model

- koristi se za POST i PUT
- definiše šta klijent šalje

### Response model

- koristi se za GET, POST, PUT, DELETE response
- definiše šta klijent dobija

### Optional field

- ne mora da postoji
- koristi se sa `= None`

### Status codes

- 200 = OK
- 201 = Created
- 404 = Not Found
- 422 = invalid input

---
