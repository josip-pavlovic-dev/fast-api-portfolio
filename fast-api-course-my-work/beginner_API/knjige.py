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


books: list[dict] = [
    {
        "id": 1,
        "title": "Python za početnike",
        "author": "Marko",
        "description": None,
    },
    {
        "id": 2,
        "title": "FastAPI uvod",
        "author": "Ana",
        "description": "Osnovni uvod",
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
