from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# FastAPI aplikacija se pravi sa objektom FastAPI.
# Ovaj objekat "zna" koje rute postoje i kako da obradi HTTP zahteve.
app = FastAPI(
    title="Books API", version="1.0.0", description="Jednostavan CRUD API za knjige."
)


# Request model: šta klijent šalje serveru.
# Ovaj model definise strukturu JSON body-a za POST i PUT metode.
class BookCreate(BaseModel):
    title: str
    author: str
    description: str | None = None


# Response model: šta server vraća klijentu.
# Koristi se u response_model parametru i daje uniforman format odgovora.
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str | None = None


# In-memory baza podataka.
# U realnom projektu ovo bi bila baza podataka (SQLite, PostgreSQL...),
# ali za učenje je dovoljno da koristimo Python listu.
books: list[dict[str, str | int | None]] = [
    {
        "id": 1,
        "title": "Python za početnike",
        "author": "Marko",
        "description": "Osnovni uvod u Python.",
    },
    {
        "id": 2,
        "title": "FastAPI uvod",
        "author": "Ana",
        "description": "Praktična uvodna lekcija.",
    },
]


# GET /books
# Ova ruta vraća listu svih knjiga.
# response_model=list[BookResponse] znači da svaki element liste mora da odgovara BookResponse modelu.
@app.get("/books", response_model=list[BookResponse])
def get_books():
    return books


# GET /books/{book_id}
# Ovaj endpoint vraća jednu knjigu po ID-u.
# book_id je path parameter, pa se u URL-u pojavljuje kao /books/1.
@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    # HTTPException se koristi za vraćanje HTTP greške.
    # 404 znači da traženi resurs ne postoji.
    raise HTTPException(status_code=404, detail="Book not found")


# POST /books
# Ova ruta kreira novu knjigu.
# book: BookCreate prihvata JSON telo i validira ga prema modelu.
@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    new_book: dict[str, str | int | None] = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author,
        "description": book.description,
    }
    books.append(new_book)
    return new_book


# PUT /books/{book_id}
# Ova ruta menja podatke već postojeće knjige.
@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book: BookCreate):
    for index, existing_book in enumerate(books):
        if existing_book["id"] == book_id:
            updated_book: dict[str, int | str | None] = {
                "id": book_id,
                "title": book.title,
                "author": book.author,
                "description": book.description,
            }
            books[index] = updated_book
            return updated_book

    raise HTTPException(status_code=404, detail="Book not found")


# DELETE /books/{book_id}
# Ova ruta briše knjigu na osnovu ID-a.
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
