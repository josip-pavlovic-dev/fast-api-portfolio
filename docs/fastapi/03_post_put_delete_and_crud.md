# POST, PUT, DELETE i CRUD model u FastAPI

Ovo je sledeći korak nakon `GET` i `response_model`.

U praksi, većina API-ja radi CRUD operacije:

- `Create` => POST
- `Read` => GET
- `Update` => PUT
- `Delete` => DELETE

---

## 1) Šta je CRUD?

CRUD je akronim:

- C = Create
- R = Read
- U = Update
- D = Delete

To je osnovni obrazac za rad sa podacima u aplikacijama.

Primer sa knjigama:

- POST /books -> dodaj knjigu
- GET /books -> vidi sve knjige
- GET /books/{book_id} -> vidi jednu knjigu
- PUT /books/{book_id} -> izmeni knjigu
- DELETE /books/{book_id} -> obriši knjigu

---

## 2) `POST` metoda

`POST` se koristi kada klijent želi da kreira novi resurs.

### Primer

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None

books = []

@app.post("/books")
async def create_book(book: BookCreate):
    new_book = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author,
        "description": book.description,
    }
    books.append(new_book)
    return new_book
```

### Šta se dešava?

- klijent šalje JSON telo
- FastAPI prihvata podatke u skladu sa `BookCreate`
- kreira se novi objekat
- vraća se rezultat

### Dobra praksa

Dodaj `response_model` i `status_code`:

```python
@app.post("/books", response_model=BookResponse, status_code=201)
async def create_book(book: BookCreate):
    ...
```

---

## 3) `GET` metoda

`GET` se koristi za čitanje podataka.

```python
@app.get("/books", response_model=list[BookResponse])
async def get_books():
    return books
```

### Značenje

- vraćaš listu svih knjiga
- `response_model` garantuje format odgovora

---

## 4) `PUT` metoda

`PUT` se koristi za izmenu postojećeg resursa.

### Primer

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
    {"id": 1, "title": "Python", "author": "Marko", "description": None}
]

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

### Šta je bitno?

- `PUT` menja postojeći zapis
- mora da zna koji resurs se menja (`book_id`)
- ako ne postoji, vraća se 404

---

## 5) `DELETE` metoda

`DELETE` se koristi za brisanje resursa.

### Primer

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

books = [
    {"id": 1, "title": "Python", "author": "Marko"},
    {"id": 2, "title": "FastAPI", "author": "Ana"},
]

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

### Napomena

`DELETE` često vraća:

- poruku o uspehu
- obrisani objekat
- jednostavan JSON odgovor

---

## 6) Kompletn CRUD primer sa knjigama

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

## 7) Zašto je `PUT` drukčiji od `PATCH`?

`PUT` se koristi za potpuno ažuriranje resursa, tj. svih polja.

```python
book = {
    "title": "Nova knjiga",
    "author": "Ana",
    "description": "Opis"
}
```

`PATCH` se koristi za delimično ažuriranje.

Na primer, ako želiš da promeniš samo `author`, a ostala polja ostaju ista.

U ovoj fazi je dovoljno da znaš:

- `PUT` = nadogradi ili zameni ceo zapis
- `PATCH` = menja samo deo

---

## 8) Šta najbolje radiš u praksi?

Za početak, koristi ovaj obrazac:

- `GET` za čitanje
- `POST` za kreiranje
- `PUT` za izmenu
- `DELETE` za brisanje

I svaki endpoint sa:

- `response_model`
- `status_code`
- `HTTPException`

---

## 9) Najčešće greške u CRUD-u

### Greška 1: zaboraviš da proslediš `book_id`

```python
@app.put("/books/{book_id}")
```

Nakon toga, u funkciji moraš da imaš:

```python
async def update_book(book_id: int, book: BookCreate):
```

---

### Greška 2: zaboraviš `response_model`

Bez njega endpoint možda vraća raw dict, i FastAPI ne validira format odgovora.

---

### Greška 3: ne vraćaš 404 kada resurs ne postoji

Ako ne postoji knjiga, to je uvek validan slučaj za `HTTPException`.

---

### Greška 4: `book.get(id)` umesto `book["id"]`

To je vrlo česta greška i u CRUD-u i u GET po ID.

---

## 10) Praktična vežba

Napravi aplikaciju sa sledećim endpointima:

- `GET /books`
- `GET /books/{book_id}`
- `POST /books`
- `PUT /books/{book_id}`
- `DELETE /books/{book_id}`

Koristi:

- `BookCreate`
- `BookResponse`
- `HTTPException`
- `status_code`
- `response_model`

---

## 11) Zaključak

CRUD je osnovni obrazac svih backend aplikacija.

FastAPI ga radi veoma jednostavno, ali je važno da pravilno kombinuješ:

- model za ulaz
- model za izlaz
- `status_code`
- `HTTPException`
- `response_model`

Ako ovo razumeš, već si spreman za ozbiljniji rad sa API-jem.

---

Sledeći korak je da pređeš na malo realniju praksu:

- više endpointa
- više modela
- validacija za svaki zahtev
- razlika između `POST`, `PUT` i `PATCH`
- i kasnije: baze podataka.
