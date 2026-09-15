from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(
        self,
        id: int,
        title: str,
        author: str,
        description: str,
        rating: int,
        published_date: int,
    ):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    # TODO 1: Dodaj Field validacije prema zadatku.
    # title: min_length=3
    # author: min_length=2
    # description: min_length=5, max_length=200
    # rating: ge=1, le=5
    # published_date: ge=2000, le=2100
    title: str
    author: str
    description: str
    rating: int
    published_date: int


BOOKS: list[Book] = [
    Book(1, "Python Basics", "Marko", "Uvod u Python", 5, 2024),
    Book(2, "FastAPI Intro", "Ana", "Uvod u FastAPI", 4, 2025),
]


def find_book_id(book: Book) -> Book:
    # Ako lista nije prazna, uzmi poslednji ID + 1.
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    # TODO 2: Koristi model_dump() da kreiras Book objekat.
    # TODO 3: Dodeli ID kroz find_book_id(...).
    # TODO 4: Dodaj knjigu u BOOKS i vrati je.
    pass
