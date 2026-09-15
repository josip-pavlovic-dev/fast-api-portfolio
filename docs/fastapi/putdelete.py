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


@app.put("/books/{book_id}", response_model= BookResponse)
async def change_book(book_id: int, book: BookCreate):
    for i, existing_book in enumerate(books):
        if existing_book.get("id") == book_id:
            updated_book= {"id": book_id,
                           "title": book.title,
                           "author": book.author,
                           "description":book.description
                           }
            books[i] = updated_book
            return updated_book
    raise HTTPException(status_code=404, detail="Book not found")
