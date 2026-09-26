# Response Models u FastAPI-ju

Response model je model koji kaže FastAPI-ju:
“Ovo je oblik odgovora koji vraćam klijentu.”

To je veoma korisno, jer API treba da vrati dosledan format podataka.

---

## 1) Šta je Response Model?

To je Pydantic klasa koja opisuje strukturu odgovora.

Primer:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    title: str
    author: str

@app.get("/books/1", response_model=Book)
def get_book():
    return {
        "title": "Python za početnike",
        "author": "Marko"
    }
```

Ovo znači:

- endpoint vraća podatke u obliku `Book`
- `title` mora biti string
- `author` mora biti string

---

## 2) Zašto je to korisno?

Zato što Response Model pomaže sa:

- validacijom odgovora
- konzistentnim JSON oblikom
- boljom dokumentacijom u Swagger-u
- manjim rizikom od “nepravilnog” odgovora

Na primer, ako funkcija vrati nešto što ne odgovara modelu, FastAPI može da to prijavi ili filtrira.

---

## 3) Najvažnija ideja

Request model:

- šta klijent šalje serveru

Response model:

- šta server vraća klijentu

To je vrlo jednostavna distinkcija.

---

## 4) Jednostavan primer

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    id: int
    title: str
    author: str

@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int):
    return {
        "id": book_id,
        "title": "Django za početnike",
        "author": "Ana"
    }
```

Ako pozoveš:

```http
GET /books/10
```

dobijaš:

```json
{
  "id": 10,
  "title": "Django za početnike",
  "author": "Ana"
}
```

---

## 5) Šta ako vratiš više polja nego model?

Na primer:

```python
return {
    "id": 1,
    "title": "Python",
    "author": "Marko",
    "created_at": "2026-09-13"
}
```

a model je:

```python
class Book(BaseModel):
    id: int
    title: str
    author: str
```

U praksi, response model će obično filtrirati dodatna polja i vratiti samo ona koja model definiše.

To je korisno jer klijent ne treba da vidi sve interne atribute.

---

## 6) Response model sa stub vrednostima

Možeš da dodaš default vrednosti:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Book(BaseModel):
    id: int
    title: str
    author: str
    description: str = "Nema opis"

@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int):
    return {
        "id": book_id,
        "title": "Python",
        "author": "Marko"
    }
```

Odgovor će biti:

```json
{
  "id": 1,
  "title": "Python",
  "author": "Marko",
  "description": "Nema opis"
}
```

---

## 7) Request model i Response model zajedno

Najčešći obrazac je:

- model za ulaz
- model za izlaz

Primer:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str

class BookResponse(BaseModel):
    id: int
    title: str
    author: str

books = []

@app.post("/books", response_model=BookResponse)
def create_book(book: BookCreate):
    new_book = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author
    }
    books.append(new_book)
    return new_book
```

Ovo je veoma čest i profesionalan obrazac.

---

## 8) Zašto je to čest obrazac?

Jer se često želi:

- klijent šalje samo pola informacija
- server vraća kompletan objekat

Na primer:

- `BookCreate` može imati samo `title` i `author`
- `BookResponse` može imati i `id`, `created_at`, itd.

---

## 9) Jednostavno pravilo za pamćenje

Response model je kao “plan odgovora”.

To je:

- šta će API vratiti
- koji su tipovi podataka
- koji polja su očekivana

---

## 10) Najčešća greška početnika

Pokušavaju da vrate dict koji ne odgovara modelu.

Primer:

```python
@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int):
    return {"title": "Python"}   # nedostaje author i id
```

Ovo može biti problem, jer model očekuje više polja.

---

## 11) Kratka lista za pamćenje

- Response model definiše oblik odgovora
- koristi se sa `response_model=...`
- pomaže validaciji i dokumentaciji
- čest je kod POST/GET endpointa
- pravi API odgovor doslednim i predvidivim

---

## 12) Mini vežba

Napiši ovaj kod:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/items/1", response_model=Item)
def get_item():
    return {
        "name": "Laptop",
        "price": 999.99
    }
```

Koji je odgovor?

```json
{
  "name": "Laptop",
  "price": 999.99
}
```

Ako razumeš ovo, razumeš i Response Models.

---

## 13) Dobar mentalni model

Response model = “šablon odgovora”.

Request model = “šablon zahteva”.

To je najjednostavniji način da to zapamtiš.

---

## Response status + response model zajedno

### 1) Pydantic model = šablon podataka

Pydantic model definiše šta podatak treba da izgleda.

```python
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str
```

Ovo znači:

- `title` mora biti string
- `author` mora biti string

Ako pošalješ:

```json
{
  "title": "Python",
  "author": "Marko"
}
```

to je validno.

Ako pošalješ:

```json
{
  "title": 123,
  "author": "Marko"
}
```

FastAPI će vratiti grešku, jer `title` nije string.

---

### 2) Request model i Response model

To je najvažnija distinkcija u API-ju.

- Request model = šta klijent šalje
- Response model = šta server vraća

Primer:

```python
class BookCreate(BaseModel):
    title: str
    author: str

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
```

Dakle:

- `BookCreate` koristi se za POST
- `BookResponse` koristi se za odgovor

---

### 3) Optional field

Ako neko polje nije obavezno, staviš `= None` ili tip `str | None`.

Primer:

```python
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str
    description: str | None = None
```

Ovo znači:

- `title` je obavezno
- `author` je obavezno
- `description` nije obavezno

To je veoma često u API-ju.

---

### 4) Status codes su kao poruka servera

Najbitniji za početak:

- `200 OK` → sve je uspelo
- `201 Created` → novi resurs je napravljen
- `404 Not Found` → resurs ne postoji
- `422 Unprocessable Entity` → podaci nisu validni

FastAPI to podržava jednostavno:

```python
from fastapi import FastAPI, status

app = FastAPI()

@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book():
    return {"message": "Kreirano"}
```

---

### 5) CRUD je osnovni mentalni model

Najvažniji set za jednu API aplikaciju je:

- GET → čitanje
- POST → kreiranje
- PUT → izmena
- DELETE → brisanje

To je osnova za skoro svaki API.

---

### 6) Najvažniji obrazac u FastAPI

Ovo je obrazac koji ćeš koristiti u mini projektu:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class BookCreate(BaseModel):
    title: str
    author: str

class BookResponse(BaseModel):
    id: int
    title: str
    author: str

books = []

@app.get("/books", response_model=list[BookResponse])
def get_books():
    return books

@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(book: BookCreate):
    new_book = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author
    }
    books.append(new_book)
    return new_book
```

To je već pravi API obrazac.

---

## Mini projekat: Simple Books API

Napravimo mali projekat koji pokriva celu oblast koju si do sada prošao.

### Cilj

Napraviti API za knjige:

- GET /books → sve knjige
- GET /books/{book_id} → jedna knjiga
- POST /books → dodavanje knjige
- PUT /books/{book_id} → izmena knjige
- DELETE /books/{book_id} → brisanje knjige

### Kod

```python
from fastapi import FastAPI, HTTPException, status
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
    {"id": 1, "title": "Python za početnike", "author": "Marko"},
    {"id": 2, "title": "FastAPI uvod", "author": "Ana"},
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
        "author": book.author
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
                "author": book.author
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

## Šta je ovde najvažnije?

Ovo pokriva sve što si radio do sada:

- ruta
- path parameters
- request body
- response model
- status codes
- HTTPException za 404
- CRUD operacije

To je zapravo sredina za pravi FastAPI projekat.

---

## Kako da radiš sa ovim projekatima

Preporuka je:

1. Napiši kod u mentalnom modelu
2. Sklopi ga u jedan fajl
3. Pokreni uvicorn
4. Testiraj kroz Swagger UI
5. Probaj svaki endpoint
6. Nakon toga dodaš sledeći mali feature

---
