# CRUD projekat sa validacijama i realnijim pravilima

Ovo je verzija koja uvodi dodatna pravila i pokazuje kako Pydantic pomaže da kontrolišeš kvalitet ulaza.

---

## 1) Šta dodajemo?

Sada ćemo dodati validacije:

- `price > 0`
- `year > 1900`
- `rating` mora biti između 0 i 5
- `genre` mora biti string
- `available` je bool

Ovo je važna razlika između jednostavnog API primera i realnog API-ja.

---

## 2) Primer sa validacijama

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()


class BookCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    author: str = Field(..., min_length=2, max_length=100)
    description: str | None = None
    price: float = Field(..., gt=0)
    year: int = Field(..., gt=1900)
    genre: str = Field(..., min_length=2)
    available: bool = True
    rating: float | None = Field(default=None, ge=0, le=5)


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str | None = None
    price: float
    year: int
    genre: str
    available: bool
    rating: float | None = None


books: list[dict] = [
    {
        "id": 1,
        "title": "Python za početnike",
        "author": "Marko",
        "description": "Dobar uvod u Python",
        "price": 19.99,
        "year": 2024,
        "genre": "programming",
        "available": True,
        "rating": 4.8,
    },
    {
        "id": 2,
        "title": "FastAPI uvod",
        "author": "Ana",
        "description": "API tutorial",
        "price": 24.50,
        "year": 2025,
        "genre": "backend",
        "available": True,
        "rating": 4.9,
    },
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


@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate):
    new_book = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "price": book.price,
        "year": book.year,
        "genre": book.genre,
        "available": book.available,
        "rating": book.rating,
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
                "price": book.price,
                "year": book.year,
                "genre": book.genre,
                "available": book.available,
                "rating": book.rating,
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

## 3) Šta donose validacije?

Već u ovoj verziji vidiš da Pydantic radi ozbiljno:

- `title` mora da ima najmanje 2 slova
- `price` mora biti veći od 0
- `year` mora biti veći od 1900
- `rating` mora biti između 0 i 5

Ako pošalješ loš zahtev, dobiješ 422 grešku i jasnu poruku.

---

## 4) Primer lošeg zahteva

```json
{
  "title": "A",
  "author": "P",
  "price": 0,
  "year": 1800,
  "rating": 9
}
```

Pydantic će vratiti grešku, jer:

- `title` je prekratak
- `author` je prekratak
- `price` nije > 0
- `year` nije > 1900
- `rating` nije u opsegu [0, 5]

---

## 5) Zašto je ovo važno?

Jer bez validacije API može da prihvati potpuno besmislen podatak.

Na primer:

- knjiga bez imena
- cena 0
- godina 50
- ocena 100

To su sve stvari koje u aplikaciji treba da se spreče.

---

## 6) Šta dalje mogu da dodam?

Ako želiš nastaviti sa ovom vrstom razvoja, sledeći koraci su:

- `PATCH` endpoint
- `Query` parametri
- `status_code` razne vrednosti
- `Enum` polja
- `@validator` custom validacija

Ali za sada je dovoljno da znaš: validacija je jedan od najvažnijih delova realnog API-ja.

---

## 7) Zaključak

Ovo je već veoma ozbiljan CRUD projekat, a i dalje nema baze.

To je dobar kvalitetni prelaz između jednostavnog učenja i realnog backend razvoja.

Sa ovim stepenom razumevanja, nije daleko do:

- SQLAlchemy
- SQLite/PostgreSQL
- modela sa bazom
- više slojeva aplikacije

---

## 8) Stop tačka

Po ovom delu stajemo sa materijalom.

Nastavak ide tek kada počneš sa bazama i SQLAlchemy-jem.

Zato je ovo dobra tačka za pauzu i usvajanje svih prethodnih tema.
