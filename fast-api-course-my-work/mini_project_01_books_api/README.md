# Mini projekat 1: Books API

Ovaj projekat predstavlja prvi osnovni CRUD API u FastAPI-ju.

## Šta ovaj projekat uči?

- šta je ruta
- šta je path parameter
- šta je request body
- šta je response model
- šta su HTTP status codes
- kako radi CRUD (Create, Read, Update, Delete)

---

## 1) Struktura projekta

U ovom folderu imamo:

- `main.py` — glavni kod aplikacije
- `requirements.txt` — zavisnosti

---

## 2) Kratak opis glavnog koda

### 2.1 Uvoz biblioteka

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
```

- `FastAPI` je glavna klasa za aplikaciju.
- `HTTPException` se koristi kada želimo da vratimo HTTP grešku, npr. 404.
- `status` sadrži standardne HTTP status kodove (201, 404, 200, itd.).
- `BaseModel` iz Pydantic-a omogućava definisanje strukture podataka.

---

### 2.2 Kreiranje aplikacije

```python
app = FastAPI(
    title="Books API",
    version="1.0.0",
    description="Jednostavan CRUD API za knjige."
)
```

- `app` predstavlja FastAPI aplikaciju.
- `title` i `description` ne utiču na logiku, ali poboljšavaju Swagger dokumentaciju.
- Ovo je centralni objekat preko koga se registruju rute.

---

### 2.3 Request model

```python
class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None
```

- Ovaj model opisuje podatke koje klijent šalje serveru.
- `title` i `author` su obavezni.
- `description` je opciono (`None` ako nije poslato).
- Pydantic automatski proverava da li su tipovi ispravni.

---

### 2.4 Response model

```python
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str | None = None
```

- Ovaj model opisuje odgovor servera.
- `response_model` koristi ovaj model kako bi bio sigurno definisan format JSON-a.
- Na primer, svi odgovori vraćaju `id`, `title`, `author` i `description`.

---

### 2.5 In-memory baza

```python
books = [
    {"id": 1, "title": "Python za početnike", "author": "Marko", "description": "Osnovni uvod u Python."},
    {"id": 2, "title": "FastAPI uvod", "author": "Ana", "description": "Praktična uvodna lekcija."},
]
```

- Ovaj `list` simulira bazu podataka.
- U realnom projektu bi koristio SQLite, PostgreSQL ili neku drugu bazu.
- Za početak je dovoljno da imamo jednostavnu Python listu.

---

### 2.6 GET /books

```python
@app.get("/books", response_model=list[BookResponse])
def get_books():
    return books
```

- `@app.get` registruje GET endpoint.
- `/books` je ruta.
- `response_model=list[BookResponse]` znači da će odgovor biti lista objekata tipa `BookResponse`.
- Funkcija vraća listu knjiga.

---

### 2.7 GET /books/{book_id}

```python
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")
```

- `book_id` je path parametar.
- URL primer: `/books/1`
- Petlja prolazi kroz listu i traži knjigu sa odgovarajućim ID-jem.
- Ako ne postoji, vraća se HTTP 404.

---

### 2.8 POST /books

```python
@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    new_book = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author,
        "description": book.description,
    }
    books.append(new_book)
    return new_book
```

- `POST` se koristi za kreiranje novog resursa.
- `book: BookCreate` znači da FastAPI očekuje JSON body koji odgovara modelu.
- `new_book` se dodaje u listu.
- `status.HTTP_201_CREATED` vraća status 201, što znači da je novi resurs uspešno kreiran.

---

### 2.9 PUT /books/{book_id}

```python
@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookCreate):
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

    raise HTTPException(status_code=404, detail="Book not found")
```

- `PUT` se koristi za izmenu postojećeg resursa.
- `book_id` identifikuje koji resurs menjamo.
- `book` sadrži nove podatke.
- Ako ID ne postoji, vraća se 404.

---

### 2.10 DELETE /books/{book_id}

```python
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            deleted_book = books.pop(index)
            return {
                "message": "Book deleted successfully",
                "deleted_book": deleted_book,
            }

    raise HTTPException(status_code=404, detail="Book not found")
```

- `DELETE` briše knjigu.
- Pronalazi se knjiga po ID-u.
- Ako postoji, briše se iz liste i vraća se poruka o uspehu.
- Ako ne postoji, vraća se 404.

---

## 3) Šta je ovo u praksi?

Ovaj projekat pokriva osnovni CRUD obrazac:

- CREATE → POST
- READ → GET
- UPDATE → PUT
- DELETE → DELETE

U stvari, to je najosnovniji API obrazac koji se koristi u web aplikacijama.

---

## 4) Kako pokrenuti projekat

U terminalu u ovom folderu izvrši:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Zatim otvori:

- http://127.0.0.1:8000/docs

Tamo ćeš videti Swagger dokumentaciju i moći da testiraš endpoint-e.

---

## 5) Šta treba da zapamtiš

- Route = putanja / URL
- Path parameter = deo URL-a koji treba da se promijeni
- Request model = oblik podataka koje klijent šalje
- Response model = oblik podataka koje server vraća
- Status code = informacija o uspehu ili grešci
- CRUD = osnovni API obrazac

---

Ako želiš, sledeći korak je da napraviš malo komplikovaniji projekat sa korisnicima, filtriranjem i query parametrima.
