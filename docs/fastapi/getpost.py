from fastapi import FastAPI
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

@app.get("/books",response_model = list[BookResponse])
async def get_books():
    return books

@app.post("/books/", response_model = BookResponse, status_code=201)
async def create_book(book: BookCreate):
    new_book= {
        "id": len(books)+1,
        "title": book.title,
        "author": book.author,
        "description": book.description
    }

    books.append(new_book)

    return new_book
