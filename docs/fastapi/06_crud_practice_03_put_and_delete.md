# CRUD praksa 03: PUT i DELETE

Sada kada znaš kako da radiš `GET` i `GET by ID`, sledeći korak je da uradiš ažuriranje i brisanje knjiga.

---

## 1) Setup

```python
from fastapi import FastAPI, HTTPException
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
    {"id": 2, "title": "FastAPI uvod", "author": "Ana", "description": "Osnovni uvod"},
]
```

---

## 2) `PUT /books/{book_id}`

```python
@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookCreate):
    for index, existing_book in enumerate(books):
        if existing_book["id"] == book_id:
            updated_book = {
                "id": book_id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
            }
            books[index] = updated_book
            return updated_book

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

### Šta to znači?

- klijent šalje novi sadržaj u JSON body-u
- endpoint menja knjigu sa datim `book_id`
- ako knjiga ne postoji, vraća se 404

---

## 3) `DELETE /books/{book_id}`

```python
@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            deleted_book = books.pop(index)
            return {
                "message": "Knjiga je obrisana",
                "deleted_book": deleted_book,
            }

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

### Šta je važno?

- `DELETE` uzima `book_id`
- ako postoji, briše se
- vraća poruku i obrisani objekat

---

## 4) Kompletan primer

```python
from fastapi import FastAPI, HTTPException
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
    {"id": 2, "title": "FastAPI uvod", "author": "Ana", "description": "Osnovni uvod"},
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
        "description": book.description,
    }
    books.append(new_book)
    return new_book

@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookCreate):
    for index, existing_book in enumerate(books):
        if existing_book["id"] == book_id:
            updated_book = {
                "id": book_id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
            }
            books[index] = updated_book
            return updated_book

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")

@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            deleted_book = books.pop(index)
            return {
                "message": "Knjiga je obrisana",
                "deleted_book": deleted_book,
            }

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

---

## 5) Testiranje

### PUT /books/1

Telo zahteva:

```json
{
  "title": "Python za napredne",
  "author": "Marko",
  "description": "Ažuriran opis"
}
```

Očekivani odgovor:

```json
{
  "id": 1,
  "title": "Python za napredne",
  "author": "Marko",
  "description": "Ažuriran opis"
}
```

### DELETE /books/2

Poziv:

```http
DELETE /books/2
```

Očekivani odgovor:

```json
{
  "message": "Knjiga je obrisana",
  "deleted_book": {
    "id": 2,
    "title": "FastAPI uvod",
    "author": "Ana",
    "description": "Osnovni uvod"
  }
}
```

---

## 6) Najčešće greške

### Greška 1: zaboravljeni `book_id`

```python
@app.put("/books/{book_id}")
async def update_book(book_id: int, book: BookCreate):
```

Obavezno mora da postoji u ruti i funkciji.

### Greška 2: pogrešna provera u listi

```python
if book.get("id") == book_id
```

ovo je ok, ali uvek mora da bude ispravan ključ.

### Greška 3: brisanje nepostojećeg resursa

Treba da vratiš 404, ne da “silently” prođe.

---

## 7) Šta treba da uradiš

Napravi mala testiranja:

- promeni prvu knjigu
- izbriši drugu knjigu
- pokušaj da izbrišeš nepostojeću knjigu
- proveri odgovore sa status kodovima

---

## 8) Sledeći korak

U finalnom fajlu spajaš sve zajedno u jedan kompletan CRUD projekat i proveravaš ceo tok.
