from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(
    title="Books API", version="1.0.0", description="Jednostavan CRUD API za knjige."
)

# Definisanje Pydantic modela za zahteve i odgovore vezane za knjige
class BookRequest(BaseModel):
    title: str
    author: str
    description: str | None = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: str | None = None

# In-memory lista knjiga (simulacija baze podataka)
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


# Dohvatanje svih knjiga (GET request)
@app.get("/books", response_model=list[BookResponse])
async def get_books():
    return books


# Pojedinačna knjiga (Path parametar) po id-u
@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena.")


# Pravljenje nove knjige (POST request)
@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookRequest):
    new_book: dict[str, int |str | None] = {
        "id": len(books) + 1,
        "title": book.title,
        "author": book.author,
        "description": book.description,
    }

    books.append(new_book)
    return new_book

# Promena podataka već postojeće knjige (PUT request)
@app.put("/books/{book_id}", response_model= BookResponse)
async def update_book(book_id: int, book: BookRequest):
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

    raise HTTPException(status_code=404, detail="Knjiga nije pronađena.")

# Brisanje knjige po id-u (DELETE request)
@app.delete("/books/{books_id}")
async def book_delete(books_id: int):
    for index, book_to_delete in enumerate(books):
        if book_to_delete["id"] == books_id:
            deleted_book = books.pop(index)
            return{
                "message": "Knjiga je obrisana",
                "deleted_book": deleted_book
            }

    raise HTTPException(status_code=404, detail="Pogrešan ID, knjiga nije pronađena!")
