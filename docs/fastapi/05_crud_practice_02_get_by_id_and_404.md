# CRUD praksa 02: GET po ID i 404

Sada kada znaš kako da vraćaš listu i dodaš novu knjigu, sledeći korak je da naučiš kako da vraćaš jednu knjigu po ID-u.

---

## 1) Početni setup

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

## 2) `GET /books/{book_id}`

```python
@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena")
```

### Zašto je ovo bitno?

- `book_id` je path parametar
- endpoint očekuje broj
- ako knjiga postoji, vraća je
- ako ne postoji, vraća 404

---

## 3) Zašto je `book["id"]` važno?

Ovo je česta greška:

```python
if book.get(id) == book_id:
```

To je pogrešno, jer `id` nije ključ u rečniku, nego built-in funkcija.

Pravilno je:

```python
if book["id"] == book_id:
```

ili:

```python
if book.get("id") == book_id:
```

---

## 4) Kompletan primer sa GET po ID

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
```

---

## 5) Testiranje

### GET /books/1

```http
GET /books/1
```

Očekivani odgovor:

```json
{
  "id": 1,
  "title": "Python za početnike",
  "author": "Marko",
  "description": null
}
```

### GET /books/999

```http
GET /books/999
```

Očekivani odgovor:

```json
{
  "detail": "Knjiga nije pronađena"
}
```

I HTTP status:

```http
404 Not Found
```

---

## 6) `HTTPException` je važan

Bez `HTTPException`, endpoint bi mogao da vrati `None` ili da ne radi ništa.

To je problem jer klijent ne zna da je nešto pogrešno.

`HTTPException` ti daje:

- jasno značenje problema
- konkretan HTTP status
- detaljnu poruku

---

## 7) Najčešće greške u ovoj fazi

### Greška 1: `response_model` za listu je pogrešno postavljen

```python
response_model=[BookResponse]
```

Treba da bude:

```python
response_model=BookResponse
```

za jedan objekat, i:

```python
response_model=list[BookResponse]
```

za listu.

### Greška 2: ne vraćaš `404`

Ako knjiga ne postoji, treba da se vrati greška.

### Greška 3: `book.get(id)`

To je pogrešno. Koristi:

```python
book["id"]
```

---

## 8) Šta treba da zapišeš

Napiši odgovor na ova pitanja:

- Šta je `path parameter`?
- ODGOVOR: `path parameter` je deo URL-a koji se koristi za prosleđivanje vrednosti endpoint-u. U ovom slučaju, `book_id` je `path parameter` koji označava ID knjige koju želimo da dohvatimo.
- Kako FastAPI zna da je `book_id` broj?
- ODGOVOR: FastAPI koristi tip podatka definisan u funkciji endpoint-a (`book_id: int`) da automatski validira i konvertuje vrednost path parametra u odgovarajući tip. Ako vrednost nije validan broj, FastAPI vraća grešku.
- Šta radi `HTTPException`?
- ODGOVOR: `HTTPException` omogućava da se vrati HTTP greška sa odgovarajućim status kodom i detaljnom porukom. U ovom slučaju, koristi se za vraćanje 404 greške kada knjiga nije pronađena.
- Zašto se vraća 404 ako nema knjige?
- ODGOVOR: 404 status kod označava da traženi resurs nije pronađen. Ako knjiga sa datim ID-jem ne postoji, vraćamo 404 da bi klijent znao da resurs ne postoji.
- Zašto je `book["id"]` ispravno, a `id` nije?
- ODGOVOR: `book` je rečnik (dict) i da bismo pristupili njegovim vrednostima, moramo koristiti ključ u obliku stringa (`book["id"]`). Samo `id` ne postoji u kontekstu funkcije i izazvalo bi grešku.

---

## 9) Sledeći korak

U sledećem fajlu dodajemo:

- `PUT /books/{book_id}`
- `DELETE /books/{book_id}`
- kompletan CRUD obrazac

Na taj način završavamo ceo API lifecycle.
