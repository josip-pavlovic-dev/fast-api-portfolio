from fastapi import FastAPI, status
from pydantic import BaseModel, Field

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
    title: str = Field(min_length=3)
    author: str = Field(min_length=2)
    description: str = Field(min_length=5, max_length=200)
    rating: int = Field(ge=1, le=5)
    published_date: int = Field(ge=2000, le=2100)


BOOKS: list[Book] = [
    Book(1, "Python Basics", "Marko", "Uvod u Python", 5, 2024),
    Book(2, "FastAPI Intro", "Ana", "Uvod u FastAPI", 4, 2025),
]


def find_book_id(book: Book) -> Book:
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    data = book_request.model_dump()

    new_book = Book(
        id=0,
        title=data["title"],
        author=data["author"],
        description=data["description"],
        rating=data["rating"],
        published_date=data["published_date"],
    )

    new_book = find_book_id(new_book)
    BOOKS.append(new_book)
    return new_book
