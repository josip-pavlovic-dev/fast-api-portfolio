from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id: int, title: str, author: str, description: str, rating: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating


class BookRequest(BaseModel):
    id: int | None = Field(
        description="The ID of the book is not needed on creation", default=None
    )
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Nova Knjiga",
                "author": "Marko Vidojkovic",
                "description": "Opis knjige",
                "rating": 5,
            }
        }
    }


# Poredjenja brojeva:
# lt - less than (manje od)
# gt - greater than (veće od)
# le - less than or equal to (manje ili jednako)
# ge - greater than or equal to (veće ili jednako)

BOOKS: list[Book] = [
    Book(
        id=1,
        title="FastAPI for Beginners",
        author="John Doe",
        description="A comprehensive guide to FastAPI.",
        rating=5,
    ),
    Book(
        id=2,
        title="Advanced FastAPI",
        author="Jane Smith",
        description="Deep dive into FastAPI features.",
        rating=4,
    ),
    Book(
        id=3,
        title="Mastering FastAPI",
        author="Alice Johnson",
        description="Expert techniques for building APIs with FastAPI.",
        rating=5,
    ),
    Book(
        id=4,
        title="FastAPI in Action",
        author="Bob Brown",
        description="Practical guide to building APIs with FastAPI.",
        rating=4,
    ),
    Book(
        id=5,
        title="The FastAPI Cookbook",
        author="Charlie Davis",
        description="Recipes for common FastAPI tasks.",
        rating=5,
    ),
    Book(
        id=6,
        title="FastAPI Patterns",
        author="Diana Evans",
        description="Design patterns and best practices for FastAPI.",
        rating=4,
    ),
]


# Čitanje svih knjiga:
@app.get("/books")
async def read_all_books():
    return BOOKS


# Čitanje pojedinačne knjige po ID-u:
@app.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book
    return {"error": "Book not found"}


# Kreiranje nove knjige:
@app.post("/create-book", status_code=201)
async def create_book(book_request: BookRequest):
    new_book = Book(
        **book_request.model_dump()
    )  # konvertuje zahtev u objekat klase Book
    BOOKS.append(find_book_id(new_book))  # type: ignore

    return new_book


# Funkcija koja omogućava da id knjige ide redom kako ih registrujemo u listi BOOKS
def find_book_id(book: Book):

    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    # if len(BOOKS) > 0:
    #     book.id = BOOKS[-1].id + 1
    # else:
    #     book.id = 1

    return book


# Deo po deo `new_book= Book(**book_request.model_dump())`:
# 1. `book_request.model_dump()` konvertuje Pydantic model u rečnik.
# 2. `**book_request.model_dump()` raspakuje rečnik u ključne (keyword arguments naprimer `id=1, title="FastAPI for Beginners", ...`) argumente za konstruktor klase Book.
# 3. `Book(**book_request.model_dump())` kreira novi objekat klase Book sa podacima iz zahteva.

# Šta tačno radi funkcija ‚model_dump()‘:
# `model_dump()` je metoda Pydantic modela koja vraća podatke modela kao rečnik.
# Ovo omogućava jednostavno kreiranje novih objekata koristeći te podatke.
