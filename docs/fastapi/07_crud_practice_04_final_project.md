# CRUD praksa 04: Finalni projekat

Ovo je završni file u nizu praktičnih vežbi.

Cilj: da imaš potpuno funkcionalan CRUD API za knjige, bez dodatnih komplikacija.

---

## 1) Finalni projekat

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

## 2) Šta sve ovaj projekat pokazuje?

Ovaj projekat pokriva:

- `BaseModel`
- validaciju podataka
- `response_model`
- `status_code`
- `HTTPException`
- `GET`, `POST`, `PUT`, `DELETE`
- `CRUD` logiku osnovnog API-ja

---

## 3) Primeri zahteva

### GET svih knjiga

```http
GET /books
```

### GET jedne knjige

```http
GET /books/1
```

### POST nove knjige

```http
POST /books
```

Telo:

```json
{
  "title": "Django uvod",
  "author": "Petar",
  "description": "Novi kurs"
}
```

### PUT izmene knjige

```http
PUT /books/1
```

Telo:

```json
{
  "title": "Python za napredne",
  "author": "Marko",
  "description": "Izmenjen opis"
}
```

### DELETE knjige

```http
DELETE /books/1
```

---

## 4) Obavezno proveri sledeće

### 4.1 Da li GET vraća listu?

```http
GET /books
```

### 4.2 Da li GET po ID vraća 404 ako ne postoji?

```http
GET /books/999
```

### 4.3 Da li POST vraća 201?

```http
POST /books
```

### 4.4 Da li PUT menja podatke?

```http
PUT /books/1
```

### 4.5 Da li DELETE uklanja knjigu?

```http
DELETE /books/1
```

---

## 5) Kada je ovaj projekat dovoljno dobar?

Smatra se da si dobro razumeo osnovu ako možeš:

- da objasniš šta je `BookCreate`
- da objasniš šta je `BookResponse`
- da objasniš razliku između `GET` i `POST`
- da dodaješ novi zapis i vidiš 201
- da dobijes 404 kada resurs ne postoji
- da menjaš i brišeš podatke

---

## 6) Šta je sledeći korak?

Nakon ovog CRUD projekta, pravi sledeći korak su:

- `PATCH` i delimično ažuriranje
- `Query` parametri
- `Path` i `Body`
- `FileUpload` i slike
- `SQLAlchemy` i baze podataka

Ali sve to tek posle što solidno ovladaš ovim osnovama.

---

## 7) Finalni zaključak

Ovaj projekat je model koji ćeš koristiti u mnogim aplikacijama:

- API za knjige
- API za korisnike
- API za proizvode
- API za zadatke
- API za blog postove

Osnova je ista: model, endpoint, validacija, status kod, HTTPException, CRUD.

To je i dalje najvažniji “backend mentalni model” za sve što dolazi posle.
